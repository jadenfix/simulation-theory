"""Exact coupled source-law drift and precommitted code-sequence optimization.

Static ambiguity and a time-indexed source law are different objects.  This
module considers a finite path

    q_0 = p,
    TV(q_t, q_{t-1}) <= eta_t,   t=1,...,T,

and permits the state-cost vector to change with time.  The path constraints are
encoded exactly by event halfspaces after eliminating one simplex coordinate
per period.  Every bounded rational path vertex is enumerated from active bases,
and a separate exact rational LP dual supplies a zero-gap optimality receipt.

The second layer chooses a precommitted sequence of deterministic zero-error
binary prefix codebooks.  The entire code sequence is fixed before the source
path is chosen.  A rational switching penalty may be charged whenever the
state-length vector changes.  The outer code-sequence search is exhaustive below
explicit caps, while each inner adversarial path is solved by the same exact
coupled polytope.

The module keeps several distinctions explicit:

* a coupled path optimum versus the looser sum of independent marginal balls;
* a fixed codebook versus a precommitted changing codebook sequence;
* source-independent precommitment versus adaptation to realized source states;
* communication length versus codebook reconfiguration cost;
* exact finite rational certificates versus scalability claims.

These are finite internal source-coding and robust-control results.  They are
not evidence for simulation and do not identify code lengths, switching costs,
or probability-path geometry with parent-universe hardware, energy, mass, or
spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb
from typing import Mapping, Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import (
    TVExpectationCertificate,
    exact_expectation,
    maximize_expectation_tv_ball,
    total_variation_distance,
)
from .polyhedral_priors import _solve_square
from .prior_weighted_codes import RationalInput, validate_rational_prior
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)


ExactInput = int | str | Fraction


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be supplied as exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _validate_probability_vector(
    probabilities: Sequence[ExactInput],
    *,
    name: str,
) -> tuple[Fraction, ...]:
    supplied = tuple(_fraction(value, name=name) for value in probabilities)
    if not supplied:
        raise ValueError(f"{name} cannot be empty")
    if any(value < 0 for value in supplied):
        raise ValueError(f"{name} must be nonnegative")
    if sum(supplied, Fraction(0)) != 1:
        raise ValueError(f"{name} must sum exactly to one")
    return supplied


def _validate_drift_budgets(
    drift_budgets: ExactInput | Sequence[ExactInput],
    horizon: int,
) -> tuple[Fraction, ...]:
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    if isinstance(drift_budgets, (int, str, Fraction)):
        supplied = (_fraction(drift_budgets, name="drift budget"),) * periods
    else:
        supplied = tuple(
            _fraction(value, name="drift budget") for value in drift_budgets
        )
        if len(supplied) != periods:
            raise ValueError("one drift budget is required per period")
    if any(not 0 <= value <= 1 for value in supplied):
        raise ValueError("every drift budget must lie in [0,1]")
    return supplied


def _validate_cost_vectors(
    cost_vectors: Sequence[Sequence[ExactInput]],
    state_count: int,
    horizon: int,
) -> tuple[tuple[Fraction, ...], ...]:
    supplied = tuple(
        tuple(_fraction(value, name="state cost") for value in vector)
        for vector in cost_vectors
    )
    if len(supplied) != horizon:
        raise ValueError("one state-cost vector is required per period")
    if any(len(vector) != state_count for vector in supplied):
        raise ValueError("every state-cost vector must match the source alphabet")
    return supplied


def _canonical_events(state_count: int) -> tuple[tuple[int, ...], ...]:
    """One nonempty representative from every event/complement pair.

    Every representative excludes the final state.  Since signed probability
    differences sum to zero, an event and its complement have equal absolute
    discrepancy.  Thus these ``2^(n-1)-1`` events are sufficient for exact TV.
    """

    n = int(state_count)
    if n < 1:
        raise ValueError("state_count must be positive")
    free = n - 1
    return tuple(
        tuple(index for index in range(free) if (mask >> index) & 1)
        for mask in range(1, 1 << free)
    )


def _event_mass(
    distribution: Sequence[Fraction],
    event: Sequence[int],
) -> Fraction:
    return sum((distribution[index] for index in event), Fraction(0))


def _simplex_vertices(state_count: int) -> tuple[tuple[Fraction, ...], ...]:
    n = int(state_count)
    if n < 1:
        raise ValueError("state_count must be positive")
    return tuple(
        tuple(Fraction(1) if index == state else Fraction(0) for index in range(n))
        for state in range(n)
    )


@dataclass(frozen=True)
class CoupledPathHalfspace:
    """One exact rational path halfspace ``a.x <= b``."""

    coefficients: tuple[Fraction, ...]
    bound: Fraction
    label: str

    def value(self, point: Sequence[Fraction]) -> Fraction:
        if len(point) != len(self.coefficients):
            raise ValueError("point and path halfspace dimensions differ")
        return sum(
            (coefficient * coordinate for coefficient, coordinate in zip(self.coefficients, point)),
            Fraction(0),
        )

    def satisfied(self, point: Sequence[Fraction]) -> bool:
        return self.value(point) <= self.bound


@dataclass(frozen=True)
class CoupledPathVertex:
    free_coordinates: tuple[Fraction, ...]
    path: tuple[tuple[Fraction, ...], ...]
    active_constraints: tuple[str, ...]


@dataclass(frozen=True)
class CoupledDriftPathPolytope:
    """Exact bounded polytope of finite source-law paths."""

    initial_prior: tuple[Fraction, ...]
    drift_budgets: tuple[Fraction, ...]
    constraints: tuple[CoupledPathHalfspace, ...]
    vertices: tuple[CoupledPathVertex, ...]
    candidate_bases: int
    bases_examined: int
    nonsingular_bases: int
    max_bases: int

    @property
    def state_count(self) -> int:
        return len(self.initial_prior)

    @property
    def horizon(self) -> int:
        return len(self.drift_budgets)

    @property
    def dimension(self) -> int:
        return self.horizon * (self.state_count - 1)

    @property
    def paths(self) -> tuple[tuple[tuple[Fraction, ...], ...], ...]:
        return tuple(vertex.path for vertex in self.vertices)

    @property
    def valid(self) -> bool:
        n = self.state_count
        t_count = self.horizon
        d = self.dimension
        if (
            n < 1
            or t_count < 1
            or any(value < 0 for value in self.initial_prior)
            or sum(self.initial_prior, Fraction(0)) != 1
            or any(not 0 <= eta <= 1 for eta in self.drift_budgets)
            or any(len(row.coefficients) != d for row in self.constraints)
            or self.bases_examined != self.candidate_bases
            or not self.vertices
            or len(set(self.paths)) != len(self.vertices)
            or not 0 <= self.nonsingular_bases <= self.bases_examined <= self.max_bases
        ):
            return False
        for vertex in self.vertices:
            if len(vertex.free_coordinates) != d or len(vertex.path) != t_count:
                return False
            if any(not row.satisfied(vertex.free_coordinates) for row in self.constraints):
                return False
            previous = self.initial_prior
            for eta, distribution in zip(self.drift_budgets, vertex.path):
                if (
                    len(distribution) != n
                    or any(value < 0 for value in distribution)
                    or sum(distribution, Fraction(0)) != 1
                    or total_variation_distance(previous, distribution) > eta
                ):
                    return False
                previous = distribution
            active = tuple(
                row.label
                for row in self.constraints
                if row.value(vertex.free_coordinates) == row.bound
            )
            if vertex.active_constraints != active:
                return False
        return True


def _path_constraints(
    initial_prior: tuple[Fraction, ...],
    drift_budgets: tuple[Fraction, ...],
) -> tuple[CoupledPathHalfspace, ...]:
    n = len(initial_prior)
    free = n - 1
    horizon = len(drift_budgets)
    dimension = free * horizon
    rows: list[CoupledPathHalfspace] = []

    def position(period: int, state: int) -> int:
        return period * free + state

    for period in range(horizon):
        for state in range(free):
            coefficients = [Fraction(0)] * dimension
            coefficients[position(period, state)] = Fraction(-1)
            rows.append(
                CoupledPathHalfspace(
                    tuple(coefficients),
                    Fraction(0),
                    f"simplex:t={period + 1}:q[{state}]>=0",
                )
            )
        coefficients = [Fraction(0)] * dimension
        for state in range(free):
            coefficients[position(period, state)] = Fraction(1)
        rows.append(
            CoupledPathHalfspace(
                tuple(coefficients),
                Fraction(1),
                f"simplex:t={period + 1}:q[{n - 1}]>=0",
            )
        )

    events = _canonical_events(n)
    for period, eta in enumerate(drift_budgets):
        for event in events:
            forward = [Fraction(0)] * dimension
            reverse = [Fraction(0)] * dimension
            for state in event:
                forward[position(period, state)] += 1
                reverse[position(period, state)] -= 1
                if period:
                    forward[position(period - 1, state)] -= 1
                    reverse[position(period - 1, state)] += 1
            event_label = "{" + ",".join(map(str, event)) + "}"
            if period == 0:
                previous_mass = _event_mass(initial_prior, event)
                forward_bound = eta + previous_mass
                reverse_bound = eta - previous_mass
            else:
                forward_bound = eta
                reverse_bound = eta
            rows.append(
                CoupledPathHalfspace(
                    tuple(forward),
                    forward_bound,
                    f"tv:t={period + 1}:event={event_label}:forward",
                )
            )
            rows.append(
                CoupledPathHalfspace(
                    tuple(reverse),
                    reverse_bound,
                    f"tv:t={period + 1}:event={event_label}:reverse",
                )
            )
    return tuple(rows)


def _path_from_free_coordinates(
    coordinates: Sequence[Fraction],
    state_count: int,
    horizon: int,
) -> tuple[tuple[Fraction, ...], ...]:
    n = int(state_count)
    free = n - 1
    supplied = tuple(Fraction(value) for value in coordinates)
    if len(supplied) != free * horizon:
        raise ValueError("free-coordinate vector has the wrong path dimension")
    path: list[tuple[Fraction, ...]] = []
    for period in range(horizon):
        block = supplied[period * free : (period + 1) * free]
        path.append(block + (Fraction(1) - sum(block, Fraction(0)),))
    return tuple(path)


def enumerate_coupled_drift_path_polytope(
    initial_prior: Sequence[ExactInput],
    drift_budgets: ExactInput | Sequence[ExactInput],
    horizon: int,
    *,
    max_bases: int = 4_000_000,
) -> CoupledDriftPathPolytope:
    """Enumerate every vertex of the bounded rational drift-path polytope."""

    prior = _validate_probability_vector(initial_prior, name="initial prior")
    budgets = _validate_drift_budgets(drift_budgets, horizon)
    rows = _path_constraints(prior, budgets)
    dimension = len(budgets) * (len(prior) - 1)
    cap = int(max_bases)
    if cap < 1:
        raise ValueError("max_bases must be positive")

    if dimension == 0:
        path = tuple((Fraction(1),) for _ in budgets)
        active = tuple(row.label for row in rows if row.value(tuple()) == row.bound)
        vertex = CoupledPathVertex(tuple(), path, active)
        certificate = CoupledDriftPathPolytope(
            prior,
            budgets,
            rows,
            (vertex,),
            1,
            1,
            1,
            cap,
        )
        if not certificate.valid:
            raise AssertionError("one-state drift-path polytope failed validation")
        return certificate

    basis_count = comb(len(rows), dimension)
    if basis_count > cap:
        raise ValueError(
            "coupled drift active-basis space exceeds the configured cap"
        )

    by_path: dict[
        tuple[tuple[Fraction, ...], ...],
        CoupledPathVertex,
    ] = {}
    examined = 0
    nonsingular = 0
    for basis in combinations(range(len(rows)), dimension):
        examined += 1
        solution = _solve_square(
            tuple(rows[index].coefficients for index in basis),
            tuple(rows[index].bound for index in basis),
        )
        if solution is None:
            continue
        nonsingular += 1
        if any(not row.satisfied(solution) for row in rows):
            continue
        path = _path_from_free_coordinates(solution, len(prior), len(budgets))
        active = tuple(row.label for row in rows if row.value(solution) == row.bound)
        vertex = CoupledPathVertex(tuple(solution), path, active)
        incumbent = by_path.get(path)
        if incumbent is None or vertex.free_coordinates < incumbent.free_coordinates:
            by_path[path] = vertex

    vertices = tuple(
        sorted(
            by_path.values(),
            key=lambda vertex: (vertex.path, vertex.free_coordinates),
        )
    )
    certificate = CoupledDriftPathPolytope(
        prior,
        budgets,
        rows,
        vertices,
        basis_count,
        examined,
        nonsingular,
        cap,
    )
    if not certificate.valid:
        raise AssertionError("coupled drift-path polytope failed validation")
    return certificate


def _objective_from_costs(
    cost_vectors: tuple[tuple[Fraction, ...], ...],
) -> tuple[Fraction, tuple[Fraction, ...]]:
    if not cost_vectors:
        raise ValueError("at least one cost vector is required")
    n = len(cost_vectors[0])
    free = n - 1
    constant = sum((vector[-1] for vector in cost_vectors), Fraction(0))
    coefficients = tuple(
        vector[state] - vector[-1]
        for vector in cost_vectors
        for state in range(free)
    )
    return constant, coefficients


def _point_objective(
    constant: Fraction,
    coefficients: Sequence[Fraction],
    point: Sequence[Fraction],
) -> Fraction:
    return constant + sum(
        (coefficient * coordinate for coefficient, coordinate in zip(coefficients, point)),
        Fraction(0),
    )


def _cumulative_radii(
    budgets: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    total = Fraction(0)
    radii: list[Fraction] = []
    for budget in budgets:
        total = min(Fraction(1), total + budget)
        radii.append(total)
    return tuple(radii)


@dataclass(frozen=True)
class CoupledDriftOptimizationCertificate:
    """Exact primal/dual receipt for one time-varying cost sequence."""

    polytope: CoupledDriftPathPolytope
    cost_vectors: tuple[tuple[Fraction, ...], ...]
    objective_constant: Fraction
    objective_coefficients: tuple[Fraction, ...]
    maximizing_vertex_index: int
    primal_value: Fraction
    dual_multipliers: tuple[Fraction, ...]
    dual_transpose: tuple[Fraction, ...]
    dual_value: Fraction
    dual_support: tuple[int, ...]
    dual_candidate_bases: int
    dual_bases_examined: int
    max_dual_bases: int
    marginal_certificates: tuple[TVExpectationCertificate, ...]
    marginal_upper_bound: Fraction

    @property
    def maximizing_vertex(self) -> CoupledPathVertex:
        return self.polytope.vertices[self.maximizing_vertex_index]

    @property
    def optimal_path(self) -> tuple[tuple[Fraction, ...], ...]:
        return self.maximizing_vertex.path

    @property
    def marginal_relaxation_gap(self) -> Fraction:
        return self.marginal_upper_bound - self.primal_value

    @property
    def valid(self) -> bool:
        rows = self.polytope.constraints
        d = self.polytope.dimension
        if (
            not self.polytope.valid
            or len(self.cost_vectors) != self.polytope.horizon
            or any(len(vector) != self.polytope.state_count for vector in self.cost_vectors)
            or len(self.objective_coefficients) != d
            or not 0 <= self.maximizing_vertex_index < len(self.polytope.vertices)
            or len(self.dual_multipliers) != len(rows)
            or any(weight < 0 for weight in self.dual_multipliers)
            or self.dual_transpose != self.objective_coefficients
            or self.dual_value != self.primal_value
            or self.dual_bases_examined > self.dual_candidate_bases
            or self.dual_candidate_bases > self.max_dual_bases
            or len(self.marginal_certificates) != self.polytope.horizon
            or self.marginal_upper_bound < self.primal_value
        ):
            return False
        expected_constant, expected_coefficients = _objective_from_costs(self.cost_vectors)
        if (
            expected_constant != self.objective_constant
            or expected_coefficients != self.objective_coefficients
        ):
            return False
        vertex_values = tuple(
            _point_objective(
                self.objective_constant,
                self.objective_coefficients,
                vertex.free_coordinates,
            )
            for vertex in self.polytope.vertices
        )
        if (
            self.primal_value != max(vertex_values)
            or vertex_values[self.maximizing_vertex_index] != self.primal_value
        ):
            return False
        transpose = tuple(
            sum(
                (
                    self.dual_multipliers[index]
                    * rows[index].coefficients[coordinate]
                    for index in range(len(rows))
                ),
                Fraction(0),
            )
            for coordinate in range(d)
        )
        dual = self.objective_constant + sum(
            (
                self.dual_multipliers[index] * rows[index].bound
                for index in range(len(rows))
            ),
            Fraction(0),
        )
        if transpose != self.dual_transpose or dual != self.dual_value:
            return False
        if self.dual_support != tuple(
            index for index, weight in enumerate(self.dual_multipliers) if weight > 0
        ):
            return False
        point = self.maximizing_vertex.free_coordinates
        if any(
            weight * (row.bound - row.value(point)) != 0
            for weight, row in zip(self.dual_multipliers, rows)
        ):
            return False
        radii = _cumulative_radii(self.polytope.drift_budgets)
        if any(
            not certificate.valid
            or not certificate.maximize
            or certificate.nominal_distribution != self.polytope.initial_prior
            or certificate.state_values != vector
            or certificate.radius != radius
            for certificate, vector, radius in zip(
                self.marginal_certificates,
                self.cost_vectors,
                radii,
            )
        ):
            return False
        return self.marginal_upper_bound == sum(
            (certificate.extremal_expectation for certificate in self.marginal_certificates),
            Fraction(0),
        )


def optimize_coupled_drift_costs(
    polytope: CoupledDriftPathPolytope,
    cost_vectors: Sequence[Sequence[ExactInput]],
    *,
    max_dual_bases: int = 4_000_000,
) -> CoupledDriftOptimizationCertificate:
    """Maximize a time-varying linear cost over one exact drift-path polytope."""

    if not polytope.valid:
        raise ValueError("drift-path polytope must be valid")
    costs = _validate_cost_vectors(
        cost_vectors,
        polytope.state_count,
        polytope.horizon,
    )
    constant, coefficients = _objective_from_costs(costs)
    vertex_values = tuple(
        _point_objective(constant, coefficients, vertex.free_coordinates)
        for vertex in polytope.vertices
    )
    primal_value = max(vertex_values)
    maximizing_index = min(
        index for index, value in enumerate(vertex_values) if value == primal_value
    )

    rows = polytope.constraints
    dimension = polytope.dimension
    cap = int(max_dual_bases)
    if cap < 1:
        raise ValueError("max_dual_bases must be positive")

    if dimension == 0 or all(value == 0 for value in coefficients):
        multipliers = (Fraction(0),) * len(rows)
        transpose = coefficients
        dual_value = constant
        candidate_bases = 1
        bases_examined = 1
    else:
        candidate_bases = comb(len(rows), dimension)
        if candidate_bases > cap:
            raise ValueError("coupled-drift dual basis space exceeds configured cap")
        best: tuple[Fraction, tuple[Fraction, ...]] | None = None
        bases_examined = 0
        for basis in combinations(range(len(rows)), dimension):
            bases_examined += 1
            matrix = tuple(
                tuple(rows[index].coefficients[coordinate] for index in basis)
                for coordinate in range(dimension)
            )
            solution = _solve_square(matrix, coefficients)
            if solution is None or any(weight < 0 for weight in solution):
                continue
            full = [Fraction(0)] * len(rows)
            for index, weight in zip(basis, solution):
                full[index] = weight
            value = constant + sum(
                (full[index] * rows[index].bound for index in range(len(rows))),
                Fraction(0),
            )
            candidate = (value, tuple(full))
            if best is None or candidate[0] < best[0] or (
                candidate[0] == best[0] and candidate[1] < best[1]
            ):
                best = candidate
        if best is None:
            raise AssertionError("bounded coupled primal did not yield an exact dual")
        dual_value, multipliers = best
        transpose = tuple(
            sum(
                (
                    multipliers[index]
                    * rows[index].coefficients[coordinate]
                    for index in range(len(rows))
                ),
                Fraction(0),
            )
            for coordinate in range(dimension)
        )

    radii = _cumulative_radii(polytope.drift_budgets)
    marginal = tuple(
        maximize_expectation_tv_ball(
            polytope.initial_prior,
            vector,
            radius,
        )
        for vector, radius in zip(costs, radii)
    )
    certificate = CoupledDriftOptimizationCertificate(
        polytope,
        costs,
        constant,
        coefficients,
        maximizing_index,
        primal_value,
        multipliers,
        transpose,
        dual_value,
        tuple(index for index, weight in enumerate(multipliers) if weight > 0),
        candidate_bases,
        bases_examined,
        cap,
        marginal,
        sum((item.extremal_expectation for item in marginal), Fraction(0)),
    )
    if not certificate.valid:
        raise AssertionError(
            "coupled drift optimization has a nonzero dual gap or invalid receipt"
        )
    return certificate


def coupled_path_value(
    polytope: CoupledDriftPathPolytope,
    cost_vectors: Sequence[Sequence[ExactInput]],
) -> tuple[Fraction, int]:
    """Return the exact primal value and first maximizing vertex without a dual search."""

    costs = _validate_cost_vectors(
        cost_vectors,
        polytope.state_count,
        polytope.horizon,
    )
    constant, coefficients = _objective_from_costs(costs)
    values = tuple(
        _point_objective(constant, coefficients, vertex.free_coordinates)
        for vertex in polytope.vertices
    )
    optimum = max(values)
    return optimum, min(index for index, value in enumerate(values) if value == optimum)


def common_cost_ordering(
    cost_vectors: Sequence[Sequence[ExactInput]],
) -> bool:
    """Whether all periods induce the same weak ordering of source states."""

    supplied = tuple(tuple(_fraction(value, name="state cost") for value in vector) for vector in cost_vectors)
    if not supplied:
        raise ValueError("at least one cost vector is required")
    n = len(supplied[0])
    if any(len(vector) != n for vector in supplied):
        raise ValueError("all cost vectors must have equal length")
    signs = tuple(
        tuple(
            (vector[left] > vector[right]) - (vector[left] < vector[right])
            for left in range(n)
            for right in range(left + 1, n)
        )
        for vector in supplied
    )
    return all(signature == signs[0] for signature in signs[1:])


@dataclass(frozen=True)
class CodeSequenceEvaluation:
    code_indices: tuple[int, ...]
    cost_vectors: tuple[tuple[Fraction, ...], ...]
    adversarial_path_value: Fraction
    maximizing_vertex_index: int
    switch_count: int
    switching_penalty: Fraction
    total_value: Fraction

    @property
    def switching_cost(self) -> Fraction:
        return self.switch_count * self.switching_penalty

    @property
    def valid(self) -> bool:
        return (
            bool(self.code_indices)
            and len(self.cost_vectors) == len(self.code_indices)
            and self.switch_count
            == sum(
                left != right
                for left, right in zip(self.code_indices, self.code_indices[1:])
            )
            and self.switch_count >= 0
            and self.switching_penalty >= 0
            and self.total_value
            == self.adversarial_path_value + self.switching_cost
        )


@dataclass(frozen=True)
class PrecommittedCodeSequenceCertificate:
    """Exact finite optimum over precommitted deterministic codebook sequences."""

    graph: ConfusionGraph
    nominal_prior: tuple[Fraction, ...]
    drift_budgets: tuple[Fraction, ...]
    switching_penalty: Fraction
    code_enumeration: RobustCandidateEnumeration
    path_polytope: CoupledDriftPathPolytope
    evaluations: tuple[CodeSequenceEvaluation, ...]
    selected_evaluation_index: int
    selected_path_certificate: CoupledDriftOptimizationCertificate
    best_static_evaluation: CodeSequenceEvaluation
    candidate_sequence_count: int
    max_sequences: int
    max_switches: int | None

    @property
    def horizon(self) -> int:
        return len(self.drift_budgets)

    @property
    def selected_evaluation(self) -> CodeSequenceEvaluation:
        return self.evaluations[self.selected_evaluation_index]

    @property
    def selected_codebooks(self) -> tuple[RobustCodeCandidate, ...]:
        candidates = self.code_enumeration.candidates
        return tuple(candidates[index] for index in self.selected_evaluation.code_indices)

    @property
    def selected_total_value(self) -> Fraction:
        return self.selected_evaluation.total_value

    @property
    def static_total_value(self) -> Fraction:
        return self.best_static_evaluation.total_value

    @property
    def reconfiguration_gain(self) -> Fraction:
        return self.static_total_value - self.selected_total_value

    @property
    def coupled_relaxation_gap(self) -> Fraction:
        return self.selected_path_certificate.marginal_relaxation_gap

    @property
    def valid(self) -> bool:
        candidates = self.code_enumeration.candidates
        if (
            not self.code_enumeration.valid
            or self.code_enumeration.graph != self.graph
            or not self.path_polytope.valid
            or self.path_polytope.initial_prior != self.nominal_prior
            or self.path_polytope.drift_budgets != self.drift_budgets
            or self.switching_penalty < 0
            or not self.evaluations
            or len(self.evaluations) != self.candidate_sequence_count
            or self.candidate_sequence_count > self.max_sequences
            or not 0 <= self.selected_evaluation_index < len(self.evaluations)
            or any(not evaluation.valid for evaluation in self.evaluations)
            or not self.selected_path_certificate.valid
            or self.selected_path_certificate.polytope != self.path_polytope
        ):
            return False
        if any(
            len(evaluation.code_indices) != self.horizon
            or any(not 0 <= index < len(candidates) for index in evaluation.code_indices)
            or evaluation.cost_vectors
            != tuple(candidates[index].scenario_costs for index in evaluation.code_indices)
            or evaluation.switching_penalty != self.switching_penalty
            or (self.max_switches is not None and evaluation.switch_count > self.max_switches)
            for evaluation in self.evaluations
        ):
            return False
        selected = self.selected_evaluation
        if selected.total_value != min(evaluation.total_value for evaluation in self.evaluations):
            return False
        if (
            self.selected_path_certificate.cost_vectors != selected.cost_vectors
            or self.selected_path_certificate.primal_value != selected.adversarial_path_value
            or self.selected_path_certificate.maximizing_vertex_index
            != selected.maximizing_vertex_index
        ):
            return False
        static = tuple(
            evaluation
            for evaluation in self.evaluations
            if len(set(evaluation.code_indices)) == 1
        )
        if not static or self.best_static_evaluation not in static:
            return False
        if self.best_static_evaluation.total_value != min(
            evaluation.total_value for evaluation in static
        ):
            return False
        return self.reconfiguration_gain >= 0


def exact_precommitted_code_sequence(
    graph: ConfusionGraph,
    nominal_prior: Sequence[RationalInput] | Mapping[object, RationalInput],
    drift_budgets: ExactInput | Sequence[ExactInput],
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_switches: int | None = None,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_code_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_path_bases: int = 4_000_000,
    max_dual_bases: int = 4_000_000,
    max_sequences: int = 250_000,
) -> PrecommittedCodeSequenceCertificate:
    """Minimize worst coupled path cost over all bounded codebook sequences."""

    prior = validate_rational_prior(graph, nominal_prior)
    budgets = _validate_drift_budgets(drift_budgets, horizon)
    penalty = _fraction(switching_penalty, name="switching penalty")
    if penalty < 0:
        raise ValueError("switching penalty must be nonnegative")
    switch_cap = None if max_switches is None else int(max_switches)
    if switch_cap is not None and (switch_cap != max_switches or switch_cap < 0):
        raise ValueError("max_switches must be a nonnegative integer or None")

    enumeration = enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_code_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    raw_sequence_count = len(candidates) ** int(horizon)
    sequence_cap = int(max_sequences)
    if sequence_cap < 1:
        raise ValueError("max_sequences must be positive")
    if raw_sequence_count > sequence_cap:
        raise ValueError(
            "precommitted code-sequence search exceeds the configured cap"
        )

    path_polytope = enumerate_coupled_drift_path_polytope(
        prior,
        budgets,
        horizon,
        max_bases=max_path_bases,
    )
    evaluations: list[CodeSequenceEvaluation] = []
    for indices in product(range(len(candidates)), repeat=int(horizon)):
        switch_count = sum(left != right for left, right in zip(indices, indices[1:]))
        if switch_cap is not None and switch_count > switch_cap:
            continue
        costs = tuple(candidates[index].scenario_costs for index in indices)
        value, maximizing_index = coupled_path_value(path_polytope, costs)
        evaluation = CodeSequenceEvaluation(
            tuple(indices),
            costs,
            value,
            maximizing_index,
            switch_count,
            penalty,
            value + switch_count * penalty,
        )
        if not evaluation.valid:
            raise AssertionError("code-sequence evaluation failed validation")
        evaluations.append(evaluation)

    if not evaluations:
        raise ValueError("switch cap leaves no admissible codebook sequence")
    ordered = tuple(
        sorted(
            evaluations,
            key=lambda item: (
                item.total_value,
                item.switch_count,
                item.code_indices,
            ),
        )
    )
    selected = ordered[0]
    selected_path = optimize_coupled_drift_costs(
        path_polytope,
        selected.cost_vectors,
        max_dual_bases=max_dual_bases,
    )
    static = tuple(item for item in ordered if len(set(item.code_indices)) == 1)
    if not static:
        raise AssertionError("every nonempty code universe has a static sequence")
    best_static = min(
        static,
        key=lambda item: (item.total_value, item.code_indices),
    )
    certificate = PrecommittedCodeSequenceCertificate(
        graph,
        prior,
        budgets,
        penalty,
        enumeration,
        path_polytope,
        ordered,
        ordered.index(selected),
        selected_path,
        best_static,
        len(ordered),
        sequence_cap,
        switch_cap,
    )
    if not certificate.valid:
        raise AssertionError("precommitted code-sequence certificate failed validation")
    return certificate
