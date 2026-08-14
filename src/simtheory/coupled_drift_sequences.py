"""Exact coupled source-law drift with time-varying predictive costs.

The static-drift lane is exact because one fixed cost vector admits nested
total-variation transport maximizers. That argument does not extend to a
time-varying sequence of costs: the periodwise extremizers can require
incompatible source-law movements.

This module solves the genuinely coupled finite-horizon problem

    maximize  sum_t q_t . g_t
    subject to q_0 = p and TV(q_t, q_{t-1}) <= eta.

For a finite alphabet, total variation has the event representation

    TV(u,v) = max_S |u(S)-v(S)|.

After eliminating the last simplex coordinate in every period, all simplex and
drift constraints are rational halfspaces. The bounded checker exhausts every
active basis, reconstructs all path-polytope vertices, and independently
certifies the optimum through the exact LP dual.

A second layer evaluates precommitted sequences of deterministic zero-error
prefix codebooks, including an exact rational penalty for each codebook switch.
The source-law path sees the full precommitted sequence. No feedback-adaptive
code selection is claimed here.

All results are finite, rational, bounded, and internal to the declared source
and coding model. They are not evidence for simulation and do not translate
message lengths into parent-substrate hardware, energy, mass, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import (
    TVExpectationCertificate,
    maximize_expectation_tv_ball,
    total_variation_distance,
)
from .polyhedral_priors import _solve_square
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)

ExactInput = RationalInput | Fraction | int
Distribution = tuple[Fraction, ...]
CostVector = tuple[Fraction, ...]
Path = tuple[Distribution, ...]


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _validate_prior(values: Sequence[ExactInput]) -> Distribution:
    prior = tuple(_fraction(value, name="prior probability") for value in values)
    if not prior:
        raise ValueError("prior cannot be empty")
    if any(value < 0 for value in prior):
        raise ValueError("prior probabilities must be nonnegative")
    if sum(prior, Fraction(0)) != 1:
        raise ValueError("prior probabilities must sum exactly to one")
    return prior


def _validate_costs(
    period_costs: Sequence[Sequence[ExactInput]],
    state_count: int,
) -> tuple[CostVector, ...]:
    costs = tuple(
        tuple(_fraction(value, name="period state cost") for value in period)
        for period in period_costs
    )
    if not costs:
        raise ValueError("at least one period cost vector is required")
    if any(len(period) != state_count for period in costs):
        raise ValueError("every period cost vector must match the source alphabet")
    return costs


def _validate_eta(value: ExactInput) -> Fraction:
    eta = _fraction(value, name="drift_per_step")
    if not 0 <= eta <= 1:
        raise ValueError("drift_per_step must lie in [0,1]")
    return eta


def _canonical_event_masks(state_count: int) -> tuple[int, ...]:
    """One representative from each nontrivial event/complement pair."""

    n = int(state_count)
    if n < 1:
        raise ValueError("state_count must be positive")
    if n == 1:
        return tuple()
    full = (1 << n) - 1
    return tuple(mask for mask in range(1, full) if mask < (full ^ mask))


def _event_probability(distribution: Sequence[Fraction], mask: int) -> Fraction:
    return sum(
        (
            probability
            for index, probability in enumerate(distribution)
            if (mask >> index) & 1
        ),
        Fraction(0),
    )


def _event_affine(
    state_count: int,
    period_index: int,
    event_mask: int,
    horizon: int,
) -> tuple[tuple[Fraction, ...], Fraction]:
    """Return coefficients and constant for q_period(event).

    The free variables are q_t[0],...,q_t[n-2] for each t. The final
    coordinate is 1 minus their sum.
    """

    n = state_count
    d_per = n - 1
    dimension = horizon * d_per
    coefficients = [Fraction(0)] * dimension
    includes_last = bool((event_mask >> (n - 1)) & 1)
    constant = Fraction(1) if includes_last else Fraction(0)
    offset = period_index * d_per
    for state in range(d_per):
        coefficients[offset + state] = (
            Fraction(1 if (event_mask >> state) & 1 else 0)
            - Fraction(1 if includes_last else 0)
        )
    return tuple(coefficients), constant


@dataclass(frozen=True)
class PathHalfspace:
    coefficients: tuple[Fraction, ...]
    bound: Fraction
    label: str

    def value(self, point: Sequence[Fraction]) -> Fraction:
        if len(point) != len(self.coefficients):
            raise ValueError("point and halfspace dimensions differ")
        return sum(
            (
                coefficient * coordinate
                for coefficient, coordinate in zip(self.coefficients, point)
            ),
            Fraction(0),
        )

    def satisfied(self, point: Sequence[Fraction]) -> bool:
        return self.value(point) <= self.bound


@dataclass(frozen=True)
class DriftPathVertex:
    free_point: tuple[Fraction, ...]
    path: Path
    active_constraints: tuple[int, ...]


@dataclass(frozen=True)
class DriftPathPolytope:
    nominal_prior: Distribution
    drift_per_step: Fraction
    horizon: int
    constraints: tuple[PathHalfspace, ...]
    vertices: tuple[DriftPathVertex, ...]
    candidate_bases: int
    bases_examined: int
    nonsingular_bases: int
    max_bases: int

    @property
    def state_count(self) -> int:
        return len(self.nominal_prior)

    @property
    def dimension(self) -> int:
        return self.horizon * (self.state_count - 1)

    @property
    def paths(self) -> tuple[Path, ...]:
        return tuple(vertex.path for vertex in self.vertices)

    @property
    def empty(self) -> bool:
        return not self.vertices

    @property
    def valid(self) -> bool:
        if (
            self.horizon < 1
            or not 0 <= self.drift_per_step <= 1
            or self.bases_examined != self.candidate_bases
            or not self.vertices
            or len({vertex.free_point for vertex in self.vertices})
            != len(self.vertices)
            or not (
                0
                <= self.nonsingular_bases
                <= self.bases_examined
                <= self.max_bases
            )
        ):
            return False
        for vertex in self.vertices:
            if (
                len(vertex.free_point) != self.dimension
                or len(vertex.path) != self.horizon
                or any(
                    not constraint.satisfied(vertex.free_point)
                    for constraint in self.constraints
                )
            ):
                return False
            previous = self.nominal_prior
            for distribution in vertex.path:
                if (
                    len(distribution) != self.state_count
                    or any(value < 0 for value in distribution)
                    or sum(distribution, Fraction(0)) != 1
                    or total_variation_distance(previous, distribution)
                    > self.drift_per_step
                ):
                    return False
                previous = distribution
        return True


def _path_from_free(
    free_point: Sequence[Fraction],
    state_count: int,
    horizon: int,
) -> Path:
    d_per = state_count - 1
    distributions: list[Distribution] = []
    for period in range(horizon):
        free = tuple(
            free_point[period * d_per + state] for state in range(d_per)
        )
        distributions.append(free + (Fraction(1) - sum(free, Fraction(0)),))
    return tuple(distributions)


def _path_halfspaces(
    prior: Distribution,
    eta: Fraction,
    horizon: int,
) -> tuple[PathHalfspace, ...]:
    n = len(prior)
    d_per = n - 1
    dimension = horizon * d_per
    rows: list[PathHalfspace] = []

    for period in range(horizon):
        offset = period * d_per
        for state in range(d_per):
            coefficients = [Fraction(0)] * dimension
            coefficients[offset + state] = Fraction(-1)
            rows.append(
                PathHalfspace(
                    tuple(coefficients),
                    Fraction(0),
                    f"period[{period + 1}]:q[{state}]>=0",
                )
            )
        coefficients = [Fraction(0)] * dimension
        for state in range(d_per):
            coefficients[offset + state] = Fraction(1)
        rows.append(
            PathHalfspace(
                tuple(coefficients),
                Fraction(1),
                f"period[{period + 1}]:q[{n - 1}]>=0",
            )
        )

    for period in range(horizon):
        for mask in _canonical_event_masks(n):
            current_coefficients, current_constant = _event_affine(
                n, period, mask, horizon
            )
            if period == 0:
                previous_coefficients = (Fraction(0),) * dimension
                previous_constant = _event_probability(prior, mask)
            else:
                previous_coefficients, previous_constant = _event_affine(
                    n, period - 1, mask, horizon
                )
            difference = tuple(
                current - previous
                for current, previous in zip(
                    current_coefficients,
                    previous_coefficients,
                )
            )
            constant_difference = current_constant - previous_constant
            rows.append(
                PathHalfspace(
                    difference,
                    eta - constant_difference,
                    f"step[{period + 1}]:event[{mask}]:forward",
                )
            )
            rows.append(
                PathHalfspace(
                    tuple(-value for value in difference),
                    eta + constant_difference,
                    f"step[{period + 1}]:event[{mask}]:reverse",
                )
            )
    return tuple(rows)


def enumerate_drift_path_polytope(
    nominal_prior: Sequence[ExactInput],
    drift_per_step: ExactInput,
    horizon: int,
    *,
    max_bases: int = 2_000_000,
) -> DriftPathPolytope:
    """Enumerate every vertex of the exact bounded-TV path polytope."""

    prior = _validate_prior(nominal_prior)
    eta = _validate_eta(drift_per_step)
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    cap = int(max_bases)
    if cap < 1:
        raise ValueError("max_bases must be positive")

    rows = _path_halfspaces(prior, eta, periods)
    dimension = periods * (len(prior) - 1)
    if dimension == 0:
        path = tuple(prior for _ in range(periods))
        vertex = DriftPathVertex(tuple(), path, tuple())
        result = DriftPathPolytope(
            prior, eta, periods, rows, (vertex,), 1, 1, 1, cap
        )
        if not result.valid:
            raise AssertionError("one-state drift-path polytope failed")
        return result

    candidate_bases = comb(len(rows), dimension)
    if candidate_bases > cap:
        raise ValueError("drift-path active-basis space exceeds configured cap")

    by_point: dict[tuple[Fraction, ...], set[int]] = {}
    examined = 0
    nonsingular = 0
    for basis in combinations(range(len(rows)), dimension):
        examined += 1
        solution = _solve_square(
            [rows[index].coefficients for index in basis],
            [rows[index].bound for index in basis],
        )
        if solution is None:
            continue
        nonsingular += 1
        if any(not row.satisfied(solution) for row in rows):
            continue
        active = {
            index
            for index, row in enumerate(rows)
            if row.value(solution) == row.bound
        }
        by_point.setdefault(tuple(solution), set()).update(active)

    vertices = tuple(
        DriftPathVertex(
            point,
            _path_from_free(point, len(prior), periods),
            tuple(sorted(active)),
        )
        for point, active in sorted(by_point.items())
    )
    result = DriftPathPolytope(
        prior,
        eta,
        periods,
        rows,
        vertices,
        candidate_bases,
        examined,
        nonsingular,
        cap,
    )
    if not result.valid:
        raise AssertionError("drift-path polytope certificate failed")
    return result


def _objective_affine(
    period_costs: tuple[CostVector, ...],
) -> tuple[Fraction, tuple[Fraction, ...]]:
    horizon = len(period_costs)
    state_count = len(period_costs[0])
    constant = sum((cost[-1] for cost in period_costs), Fraction(0))
    coefficients: list[Fraction] = []
    for period in range(horizon):
        tail = period_costs[period][-1]
        coefficients.extend(
            period_costs[period][state] - tail
            for state in range(state_count - 1)
        )
    return constant, tuple(coefficients)


def _path_cost(path: Path, costs: tuple[CostVector, ...]) -> Fraction:
    return sum(
        (
            sum(
                (
                    probability * value
                    for probability, value in zip(distribution, cost)
                ),
                Fraction(0),
            )
            for distribution, cost in zip(path, costs)
        ),
        Fraction(0),
    )


@dataclass(frozen=True)
class CoupledDriftCostCertificate:
    polytope: DriftPathPolytope
    period_costs: tuple[CostVector, ...]
    optimum: Fraction
    maximizing_path: Path
    maximizing_vertex_index: int
    vertex_values: tuple[Fraction, ...]
    marginal_relaxation_value: Fraction
    marginal_certificates: tuple[TVExpectationCertificate, ...]
    dual_multipliers: tuple[Fraction, ...]
    dual_value: Fraction
    dual_support: tuple[int, ...]
    dual_candidate_bases: int
    dual_bases_examined: int
    max_dual_bases: int

    @property
    def coupling_gap(self) -> Fraction:
        return self.marginal_relaxation_value - self.optimum

    @property
    def valid(self) -> bool:
        rows = self.polytope.constraints
        dimension = self.polytope.dimension
        if (
            not self.polytope.valid
            or len(self.period_costs) != self.polytope.horizon
            or any(
                len(cost) != self.polytope.state_count for cost in self.period_costs
            )
            or not 0
            <= self.maximizing_vertex_index
            < len(self.polytope.vertices)
            or self.maximizing_path
            != self.polytope.vertices[self.maximizing_vertex_index].path
            or len(self.vertex_values) != len(self.polytope.vertices)
            or len(self.dual_multipliers) != len(rows)
            or any(weight < 0 for weight in self.dual_multipliers)
            or self.dual_support
            != tuple(
                index
                for index, weight in enumerate(self.dual_multipliers)
                if weight > 0
            )
            or self.dual_bases_examined > self.dual_candidate_bases
            or self.dual_candidate_bases > self.max_dual_bases
        ):
            return False

        expected_values = tuple(
            _path_cost(vertex.path, self.period_costs)
            for vertex in self.polytope.vertices
        )
        constant, objective = _objective_affine(self.period_costs)
        transpose = tuple(
            sum(
                (
                    self.dual_multipliers[index]
                    * rows[index].coefficients[coordinate]
                    for index in range(len(rows))
                ),
                Fraction(0),
            )
            for coordinate in range(dimension)
        )
        dual = constant + sum(
            (
                self.dual_multipliers[index] * rows[index].bound
                for index in range(len(rows))
            ),
            Fraction(0),
        )
        expected_radii = tuple(
            min(Fraction(1), self.polytope.drift_per_step * t)
            for t in range(1, self.polytope.horizon + 1)
        )
        return (
            expected_values == self.vertex_values
            and self.optimum == max(expected_values)
            and expected_values[self.maximizing_vertex_index] == self.optimum
            and _path_cost(self.maximizing_path, self.period_costs) == self.optimum
            and transpose == objective
            and dual == self.dual_value == self.optimum
            and len(self.marginal_certificates) == self.polytope.horizon
            and all(
                certificate.valid
                and certificate.maximize
                and certificate.nominal_distribution == self.polytope.nominal_prior
                and certificate.state_values == cost
                and certificate.radius == radius
                for certificate, cost, radius in zip(
                    self.marginal_certificates,
                    self.period_costs,
                    expected_radii,
                )
            )
            and self.marginal_relaxation_value
            == sum(
                (
                    certificate.extremal_expectation
                    for certificate in self.marginal_certificates
                ),
                Fraction(0),
            )
            and self.coupling_gap >= 0
        )


def _dual_for_path_objective(
    polytope: DriftPathPolytope,
    costs: tuple[CostVector, ...],
    *,
    max_dual_bases: int,
) -> tuple[
    tuple[Fraction, ...],
    Fraction,
    tuple[int, ...],
    int,
    int,
]:
    rows = polytope.constraints
    dimension = polytope.dimension
    cap = int(max_dual_bases)
    if cap < 1:
        raise ValueError("max_dual_bases must be positive")
    constant, objective = _objective_affine(costs)

    if dimension == 0 or all(value == 0 for value in objective):
        multipliers = (Fraction(0),) * len(rows)
        return multipliers, constant, tuple(), 1, 1

    candidate_bases = comb(len(rows), dimension)
    if candidate_bases > cap:
        raise ValueError("drift-path dual basis space exceeds configured cap")

    best: tuple[Fraction, tuple[Fraction, ...]] | None = None
    examined = 0
    for basis in combinations(range(len(rows)), dimension):
        examined += 1
        matrix = tuple(
            tuple(rows[index].coefficients[coordinate] for index in basis)
            for coordinate in range(dimension)
        )
        solution = _solve_square(matrix, objective)
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
        if best is None or candidate[0] < best[0]:
            best = candidate

    if best is None:
        raise AssertionError("bounded path primal did not yield an LP dual")
    value, multipliers = best
    return (
        multipliers,
        value,
        tuple(
            index for index, weight in enumerate(multipliers) if weight > 0
        ),
        candidate_bases,
        examined,
    )


def exact_coupled_drift_cost(
    nominal_prior: Sequence[ExactInput],
    period_costs: Sequence[Sequence[ExactInput]],
    drift_per_step: ExactInput,
    *,
    max_path_bases: int = 2_000_000,
    max_dual_bases: int = 2_000_000,
) -> CoupledDriftCostCertificate:
    """Solve and certify the exact coupled finite-horizon path problem."""

    prior = _validate_prior(nominal_prior)
    costs = _validate_costs(period_costs, len(prior))
    polytope = enumerate_drift_path_polytope(
        prior,
        drift_per_step,
        len(costs),
        max_bases=max_path_bases,
    )
    values = tuple(_path_cost(vertex.path, costs) for vertex in polytope.vertices)
    optimum = max(values)
    index = values.index(optimum)
    radii = tuple(
        min(Fraction(1), polytope.drift_per_step * t)
        for t in range(1, polytope.horizon + 1)
    )
    marginal = tuple(
        maximize_expectation_tv_ball(prior, cost, radius)
        for cost, radius in zip(costs, radii)
    )
    (
        multipliers,
        dual_value,
        support,
        dual_candidate_bases,
        dual_examined,
    ) = _dual_for_path_objective(
        polytope,
        costs,
        max_dual_bases=max_dual_bases,
    )
    result = CoupledDriftCostCertificate(
        polytope,
        costs,
        optimum,
        polytope.vertices[index].path,
        index,
        values,
        sum(
            (
                certificate.extremal_expectation
                for certificate in marginal
            ),
            Fraction(0),
        ),
        marginal,
        multipliers,
        dual_value,
        support,
        dual_candidate_bases,
        dual_examined,
        int(max_dual_bases),
    )
    if not result.valid:
        raise AssertionError("coupled drift primal/dual certificate failed")
    return result


def _simplex_vertices(state_count: int) -> tuple[Distribution, ...]:
    return tuple(
        tuple(
            Fraction(1) if state == vertex else Fraction(0)
            for state in range(state_count)
        )
        for vertex in range(state_count)
    )


def _sequence_switch_count(sequence: Sequence[int]) -> int:
    return sum(left != right for left, right in zip(sequence, sequence[1:]))


def _candidate_cost(candidate: RobustCodeCandidate) -> CostVector:
    return tuple(candidate.scenario_costs)


@dataclass(frozen=True)
class PrecommittedCodeSequenceCertificate:
    graph: ConfusionGraph
    nominal_prior: Distribution
    drift_per_step: Fraction
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    sequences: tuple[tuple[int, ...], ...]
    sequence_path_costs: tuple[Fraction, ...]
    sequence_switch_counts: tuple[int, ...]
    sequence_total_costs: tuple[Fraction, ...]
    selected_sequence: tuple[int, ...]
    selected_candidates: tuple[RobustCodeCandidate, ...]
    selected_path_certificate: CoupledDriftCostCertificate
    robust_value: Fraction
    best_static_value: Fraction
    best_static_candidate: RobustCodeCandidate

    @property
    def selected_switches(self) -> int:
        return _sequence_switch_count(self.selected_sequence)

    @property
    def sequence_gain_over_static(self) -> Fraction:
        return self.best_static_value - self.robust_value

    @property
    def valid(self) -> bool:
        candidates = self.enumeration.candidates
        if (
            self.horizon < 1
            or not candidates
            or len(self.sequences) != len(self.sequence_path_costs)
            or len(self.sequences) != len(self.sequence_switch_counts)
            or len(self.sequences) != len(self.sequence_total_costs)
            or self.selected_sequence not in self.sequences
            or len(self.selected_sequence) != self.horizon
            or self.selected_candidates
            != tuple(candidates[index] for index in self.selected_sequence)
            or not self.selected_path_certificate.valid
            or self.selected_path_certificate.period_costs
            != tuple(
                _candidate_cost(candidate) for candidate in self.selected_candidates
            )
            or self.switching_penalty < 0
        ):
            return False
        expected_switches = tuple(
            _sequence_switch_count(sequence) for sequence in self.sequences
        )
        expected_totals = tuple(
            path_cost + self.switching_penalty * switches
            for path_cost, switches in zip(
                self.sequence_path_costs,
                expected_switches,
            )
        )
        selected_index = self.sequences.index(self.selected_sequence)
        static_indices = tuple(
            self.sequences.index((index,) * self.horizon)
            for index in range(len(candidates))
        )
        static_values = tuple(
            self.sequence_total_costs[index] for index in static_indices
        )
        best_static = min(static_values)
        best_static_index = static_values.index(best_static)
        return (
            expected_switches == self.sequence_switch_counts
            and expected_totals == self.sequence_total_costs
            and self.robust_value == min(self.sequence_total_costs)
            and self.sequence_total_costs[selected_index] == self.robust_value
            and self.selected_path_certificate.optimum
            == self.sequence_path_costs[selected_index]
            and self.best_static_value == best_static
            and self.best_static_candidate == candidates[best_static_index]
            and self.sequence_gain_over_static >= 0
        )


def exact_precommitted_code_sequence(
    graph: ConfusionGraph,
    nominal_prior: Sequence[ExactInput],
    drift_per_step: ExactInput,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_sequences: int = 250_000,
    max_path_bases: int = 2_000_000,
    max_dual_bases: int = 2_000_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> PrecommittedCodeSequenceCertificate:
    """Optimize an open-loop deterministic codebook sequence under TV drift.

    The complete sequence is chosen before the source path. A nonnegative
    penalty is charged whenever adjacent deterministic codebooks differ.
    """

    prior = _validate_prior(nominal_prior)
    if len(prior) != graph.vertex_count:
        raise ValueError("graph and prior dimensions differ")
    eta = _validate_eta(drift_per_step)
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    enumeration = enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    sequence_count = len(candidates) ** periods
    if sequence_count > int(max_sequences):
        raise ValueError("code-sequence space exceeds configured cap")

    path_polytope = enumerate_drift_path_polytope(
        prior,
        eta,
        periods,
        max_bases=max_path_bases,
    )
    sequences = tuple(product(range(len(candidates)), repeat=periods))
    path_costs: list[Fraction] = []
    switch_counts: list[int] = []
    total_costs: list[Fraction] = []
    for sequence in sequences:
        costs = tuple(_candidate_cost(candidates[index]) for index in sequence)
        path_cost = max(
            _path_cost(vertex.path, costs) for vertex in path_polytope.vertices
        )
        switches = _sequence_switch_count(sequence)
        path_costs.append(path_cost)
        switch_counts.append(switches)
        total_costs.append(path_cost + penalty * switches)

    selected_index = min(
        range(len(sequences)),
        key=lambda index: (
            total_costs[index],
            switch_counts[index],
            sequences[index],
        ),
    )
    selected_sequence = sequences[selected_index]
    selected_candidates = tuple(candidates[index] for index in selected_sequence)
    selected_path = exact_coupled_drift_cost(
        prior,
        tuple(_candidate_cost(candidate) for candidate in selected_candidates),
        eta,
        max_path_bases=max_path_bases,
        max_dual_bases=max_dual_bases,
    )

    static_values = tuple(
        total_costs[sequences.index((index,) * periods)]
        for index in range(len(candidates))
    )
    best_static_value = min(static_values)
    best_static_index = static_values.index(best_static_value)

    result = PrecommittedCodeSequenceCertificate(
        graph,
        prior,
        eta,
        periods,
        penalty,
        enumeration,
        sequences,
        tuple(path_costs),
        tuple(switch_counts),
        tuple(total_costs),
        selected_sequence,
        selected_candidates,
        selected_path,
        total_costs[selected_index],
        best_static_value,
        candidates[best_static_index],
    )
    if not result.valid:
        raise AssertionError("precommitted code-sequence certificate failed")
    return result
