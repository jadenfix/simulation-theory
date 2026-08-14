"""Exact finite-horizon coding under coupled total-variation source drift.

The fixed-code drift theorem in :mod:`simtheory.drifting_priors` has a special
separability property: one linear state-cost vector is reused at every period,
so the same monotone mass-transport path simultaneously attains all expanding
TV-ball extrema.  That argument does *not* extend to a time-varying sequence of
cost vectors or codebooks.

This module solves the genuinely coupled problem

    maximize    sum_t q_t . g_t
    subject to  q_0 = p,
                q_t in the finite probability simplex,
                TV(q_t, q_{t-1}) <= eta.

The complete path is represented as one bounded rational polytope.  Every
nontrivial event S supplies the exact linear inequality

    q_t(S) - q_{t-1}(S) <= eta;

its complement supplies the reverse inequality.  One simplex coordinate per
period is eliminated exactly.  Bounded active-set enumeration finds an exact
rational primal vertex.  A separate sparse dual search returns nonnegative
multipliers with exact stationarity, complementary slackness, and zero rational
primal-dual gap.

The module also solves a precommitted sequence of deterministic zero-error
binary prefix codebooks.  The code sequence is chosen first, the source-law
path then moves adversarially within the declared TV speed limit, and an exact
rational penalty may be charged whenever the codebook changes.  This is not an
adaptive or feedback policy: no code choice may depend on realized states or
on an unobserved current source law.

All results are finite-horizon, finite-alphabet, exact-rational, and bounded by
explicit combinatorial caps.  They are internal source-coding and predictive
consistency statements, not evidence for simulation and not parent-substrate
hardware, energy, mass, or spacetime bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb
from typing import Iterable, Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import (
    TVExpectationCertificate,
    maximize_expectation_tv_ball,
    total_variation_distance,
)
from .prior_weighted_codes import RationalInput
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


def _validate_prior(values: Sequence[ExactInput]) -> tuple[Fraction, ...]:
    prior = tuple(_fraction(value, name="prior probability") for value in values)
    if len(prior) < 2:
        raise ValueError("at least two source states are required")
    if any(value < 0 for value in prior):
        raise ValueError("prior probabilities must be nonnegative")
    if sum(prior, Fraction(0)) != 1:
        raise ValueError("prior probabilities must sum exactly to one")
    return prior


def _validate_cost_vectors(
    cost_vectors: Sequence[Sequence[ExactInput]],
    state_count: int,
) -> tuple[tuple[Fraction, ...], ...]:
    vectors = tuple(
        tuple(_fraction(value, name="state cost") for value in vector)
        for vector in cost_vectors
    )
    if not vectors:
        raise ValueError("at least one period cost vector is required")
    if any(len(vector) != state_count for vector in vectors):
        raise ValueError("every period requires one cost per source state")
    return vectors


def _validate_eta(value: ExactInput) -> Fraction:
    eta = _fraction(value, name="drift_per_step")
    if not 0 <= eta <= 1:
        raise ValueError("drift_per_step must lie in [0,1]")
    return eta


def _event_probability(distribution: Sequence[Fraction], mask: int) -> Fraction:
    return sum(
        (value for index, value in enumerate(distribution) if mask & (1 << index)),
        Fraction(0),
    )


def _event_affine(
    *,
    period: int,
    mask: int,
    state_count: int,
    horizon: int,
) -> tuple[Fraction, tuple[Fraction, ...]]:
    """Return constant and global free-coordinate coefficients for q_period(S)."""

    free_per_period = state_count - 1
    dimension = horizon * free_per_period
    coefficients = [Fraction(0)] * dimension
    last = state_count - 1
    offset = period * free_per_period
    if mask & (1 << last):
        constant = Fraction(1)
        for state in range(free_per_period):
            if not (mask & (1 << state)):
                coefficients[offset + state] = Fraction(-1)
    else:
        constant = Fraction(0)
        for state in range(free_per_period):
            if mask & (1 << state):
                coefficients[offset + state] = Fraction(1)
    return constant, tuple(coefficients)


def _subtract_vectors(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    return tuple(a - b for a, b in zip(left, right))


def _dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


@dataclass(frozen=True)
class PathInequality:
    coefficients: tuple[Fraction, ...]
    bound: Fraction
    label: str

    def slack(self, point: Sequence[Fraction]) -> Fraction:
        return self.bound - _dot(self.coefficients, point)


@dataclass(frozen=True)
class CoupledPathPolytope:
    nominal_prior: tuple[Fraction, ...]
    cost_vectors: tuple[tuple[Fraction, ...], ...]
    drift_per_step: Fraction
    inequalities: tuple[PathInequality, ...]
    objective_constant: Fraction
    objective_coefficients: tuple[Fraction, ...]

    @property
    def state_count(self) -> int:
        return len(self.nominal_prior)

    @property
    def horizon(self) -> int:
        return len(self.cost_vectors)

    @property
    def dimension(self) -> int:
        return self.horizon * (self.state_count - 1)

    @property
    def valid(self) -> bool:
        return (
            self.state_count >= 2
            and self.horizon >= 1
            and sum(self.nominal_prior, Fraction(0)) == 1
            and all(value >= 0 for value in self.nominal_prior)
            and all(len(vector) == self.state_count for vector in self.cost_vectors)
            and 0 <= self.drift_per_step <= 1
            and len(self.objective_coefficients) == self.dimension
            and bool(self.inequalities)
            and all(len(row.coefficients) == self.dimension for row in self.inequalities)
        )


def build_coupled_path_polytope(
    nominal_prior: Sequence[ExactInput],
    cost_vectors: Sequence[Sequence[ExactInput]],
    drift_per_step: ExactInput,
) -> CoupledPathPolytope:
    prior = _validate_prior(nominal_prior)
    costs = _validate_cost_vectors(cost_vectors, len(prior))
    eta = _validate_eta(drift_per_step)
    n = len(prior)
    horizon = len(costs)
    free = n - 1
    dimension = horizon * free
    rows: list[PathInequality] = []

    # Per-period simplex constraints after eliminating the final coordinate.
    for period in range(horizon):
        offset = period * free
        for state in range(free):
            coefficients = [Fraction(0)] * dimension
            coefficients[offset + state] = Fraction(-1)
            rows.append(
                PathInequality(
                    tuple(coefficients),
                    Fraction(0),
                    f"simplex[t={period + 1},q[{state}]>=0]",
                )
            )
        coefficients = [Fraction(0)] * dimension
        for state in range(free):
            coefficients[offset + state] = Fraction(1)
        rows.append(
            PathInequality(
                tuple(coefficients),
                Fraction(1),
                f"simplex[t={period + 1},q[{n - 1}]>=0]",
            )
        )

    # Every nontrivial event is included.  Complementary events supply the
    # opposite TV direction, so one-sided inequalities are sufficient.
    for period in range(horizon):
        for mask in range(1, (1 << n) - 1):
            current_constant, current_coefficients = _event_affine(
                period=period,
                mask=mask,
                state_count=n,
                horizon=horizon,
            )
            if period == 0:
                previous_constant = _event_probability(prior, mask)
                coefficients = current_coefficients
            else:
                previous_constant, previous_coefficients = _event_affine(
                    period=period - 1,
                    mask=mask,
                    state_count=n,
                    horizon=horizon,
                )
                coefficients = _subtract_vectors(
                    current_coefficients,
                    previous_coefficients,
                )
            bound = eta - current_constant + previous_constant
            rows.append(
                PathInequality(
                    coefficients,
                    bound,
                    f"tv[t={period + 1},event={mask:#0{n + 2}b}]",
                )
            )

    objective_constant = sum((vector[-1] for vector in costs), Fraction(0))
    objective = [Fraction(0)] * dimension
    for period, vector in enumerate(costs):
        offset = period * free
        for state in range(free):
            objective[offset + state] = vector[state] - vector[-1]

    result = CoupledPathPolytope(
        prior,
        costs,
        eta,
        tuple(rows),
        objective_constant,
        tuple(objective),
    )
    if not result.valid:
        raise AssertionError("coupled drift path polytope failed validation")
    return result


def _solve_square(
    matrix: Sequence[Sequence[Fraction]],
    right_hand_side: Sequence[Fraction],
) -> tuple[Fraction, ...] | None:
    n = len(matrix)
    if n == 0 or len(right_hand_side) != n or any(len(row) != n for row in matrix):
        raise ValueError("square solve requires one n by n matrix and n-vector")
    augmented = [list(row) + [right_hand_side[index]] for index, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if augmented[row][column]), None)
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(augmented[row], augmented[column])
                ]
    return tuple(augmented[row][-1] for row in range(n))


def _solve_unique_rectangular(
    matrix: Sequence[Sequence[Fraction]],
    right_hand_side: Sequence[Fraction],
) -> tuple[Fraction, ...] | None:
    """Solve A x=b when the rectangular system has one unique solution."""

    row_count = len(matrix)
    if row_count != len(right_hand_side):
        raise ValueError("rectangular system row count mismatch")
    column_count = len(matrix[0]) if matrix else 0
    if any(len(row) != column_count for row in matrix):
        raise ValueError("rectangular matrix rows have inconsistent lengths")
    if column_count == 0:
        return () if all(value == 0 for value in right_hand_side) else None

    augmented = [list(row) + [right_hand_side[index]] for index, row in enumerate(matrix)]
    pivot_rows: list[int] = []
    pivot_columns: list[int] = []
    next_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(next_row, row_count) if augmented[row][column]),
            None,
        )
        if pivot is None:
            continue
        augmented[next_row], augmented[pivot] = augmented[pivot], augmented[next_row]
        scale = augmented[next_row][column]
        augmented[next_row] = [value / scale for value in augmented[next_row]]
        for row in range(row_count):
            if row == next_row:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(augmented[row], augmented[next_row])
                ]
        pivot_rows.append(next_row)
        pivot_columns.append(column)
        next_row += 1
        if next_row == row_count:
            break

    for row in range(row_count):
        if all(augmented[row][column] == 0 for column in range(column_count)):
            if augmented[row][-1] != 0:
                return None
    if len(pivot_columns) != column_count:
        return None
    solution = [Fraction(0)] * column_count
    for row, column in zip(pivot_rows, pivot_columns):
        solution[column] = augmented[row][-1]
    return tuple(solution)


def _free_point_to_path(
    point: Sequence[Fraction],
    *,
    state_count: int,
    horizon: int,
) -> tuple[tuple[Fraction, ...], ...]:
    free = state_count - 1
    if len(point) != horizon * free:
        raise ValueError("free point dimension does not match path shape")
    path: list[tuple[Fraction, ...]] = []
    for period in range(horizon):
        prefix = tuple(point[period * free : (period + 1) * free])
        path.append((*prefix, Fraction(1) - sum(prefix, Fraction(0))))
    return tuple(path)


def _objective_from_path(
    path: Sequence[Sequence[Fraction]],
    costs: Sequence[Sequence[Fraction]],
) -> Fraction:
    return sum(
        (_dot(distribution, vector) for distribution, vector in zip(path, costs)),
        Fraction(0),
    )


@dataclass(frozen=True)
class CoupledDriftPathCertificate:
    polytope: CoupledPathPolytope
    free_point: tuple[Fraction, ...]
    extremal_path: tuple[tuple[Fraction, ...], ...]
    objective_value: Fraction
    active_basis: tuple[int, ...]
    dual_multipliers: tuple[Fraction, ...]
    dual_support: tuple[int, ...]
    dual_value: Fraction
    candidate_bases: int
    bases_examined: int
    dual_supports_examined: int
    max_bases: int
    max_dual_supports: int
    marginal_certificates: tuple[TVExpectationCertificate, ...]
    marginal_envelope: Fraction
    marginal_extrema_path_feasible: bool

    @property
    def coupling_gap(self) -> Fraction:
        return self.marginal_envelope - self.objective_value

    @property
    def valid(self) -> bool:
        problem = self.polytope
        if (
            not problem.valid
            or len(self.free_point) != problem.dimension
            or len(self.extremal_path) != problem.horizon
            or len(self.dual_multipliers) != len(problem.inequalities)
            or any(weight < 0 for weight in self.dual_multipliers)
            or self.objective_value != self.dual_value
            or self.coupling_gap < 0
            or self.bases_examined > self.max_bases
            or self.dual_supports_examined > self.max_dual_supports
        ):
            return False
        if self.extremal_path != _free_point_to_path(
            self.free_point,
            state_count=problem.state_count,
            horizon=problem.horizon,
        ):
            return False
        if any(
            any(value < 0 for value in distribution)
            or sum(distribution, Fraction(0)) != 1
            for distribution in self.extremal_path
        ):
            return False
        previous = problem.nominal_prior
        for distribution in self.extremal_path:
            if total_variation_distance(previous, distribution) > problem.drift_per_step:
                return False
            previous = distribution
        if self.objective_value != _objective_from_path(
            self.extremal_path,
            problem.cost_vectors,
        ):
            return False
        slacks = tuple(row.slack(self.free_point) for row in problem.inequalities)
        if any(slack < 0 for slack in slacks):
            return False
        if any(
            weight * slack != 0
            for weight, slack in zip(self.dual_multipliers, slacks)
        ):
            return False
        stationarity = tuple(
            sum(
                (
                    self.dual_multipliers[row] * problem.inequalities[row].coefficients[column]
                    for row in range(len(problem.inequalities))
                ),
                Fraction(0),
            )
            for column in range(problem.dimension)
        )
        if stationarity != problem.objective_coefficients:
            return False
        dual = problem.objective_constant + sum(
            (
                weight * row.bound
                for weight, row in zip(self.dual_multipliers, problem.inequalities)
            ),
            Fraction(0),
        )
        if dual != self.dual_value:
            return False
        if tuple(index for index, weight in enumerate(self.dual_multipliers) if weight) != self.dual_support:
            return False
        if len(self.dual_support) > problem.dimension:
            return False
        expected_marginal = sum(
            (certificate.extremal_expectation for certificate in self.marginal_certificates),
            Fraction(0),
        )
        if expected_marginal != self.marginal_envelope:
            return False
        marginal_path = tuple(
            certificate.extremal_distribution for certificate in self.marginal_certificates
        )
        previous = problem.nominal_prior
        feasible = True
        for distribution in marginal_path:
            if total_variation_distance(previous, distribution) > problem.drift_per_step:
                feasible = False
                break
            previous = distribution
        return feasible == self.marginal_extrema_path_feasible


def exact_coupled_drift_path(
    nominal_prior: Sequence[ExactInput],
    cost_vectors: Sequence[Sequence[ExactInput]],
    drift_per_step: ExactInput,
    *,
    max_bases: int = 2_000_000,
    max_dual_supports: int = 2_000_000,
) -> CoupledDriftPathCertificate:
    problem = build_coupled_path_polytope(
        nominal_prior,
        cost_vectors,
        drift_per_step,
    )
    dimension = problem.dimension
    row_count = len(problem.inequalities)
    candidate_bases = comb(row_count, dimension)
    if candidate_bases > max_bases:
        raise ValueError("coupled path active-basis search exceeds configured cap")

    best_point: tuple[Fraction, ...] | None = None
    best_value: Fraction | None = None
    best_basis: tuple[int, ...] | None = None
    bases_examined = 0
    for basis in combinations(range(row_count), dimension):
        bases_examined += 1
        point = _solve_square(
            tuple(problem.inequalities[index].coefficients for index in basis),
            tuple(problem.inequalities[index].bound for index in basis),
        )
        if point is None:
            continue
        if any(row.slack(point) < 0 for row in problem.inequalities):
            continue
        value = problem.objective_constant + _dot(
            problem.objective_coefficients,
            point,
        )
        if (
            best_value is None
            or value > best_value
            or (value == best_value and point < best_point)
        ):
            best_point = point
            best_value = value
            best_basis = tuple(basis)
    if best_point is None or best_value is None or best_basis is None:
        raise AssertionError("bounded coupled path polytope has no enumerated vertex")

    active = tuple(
        index
        for index, row in enumerate(problem.inequalities)
        if row.slack(best_point) == 0
    )
    dual_support_budget = sum(
        comb(len(active), size)
        for size in range(1, min(dimension, len(active)) + 1)
    )
    if all(value == 0 for value in problem.objective_coefficients):
        dual = tuple(Fraction(0) for _ in problem.inequalities)
        dual_support: tuple[int, ...] = ()
        dual_value = problem.objective_constant
        dual_examined = 0
    else:
        if dual_support_budget > max_dual_supports:
            raise ValueError("coupled path dual-support search exceeds configured cap")
        best_dual: tuple[Fraction, ...] | None = None
        best_dual_value: Fraction | None = None
        best_support: tuple[int, ...] | None = None
        dual_examined = 0
        for size in range(1, min(dimension, len(active)) + 1):
            for support in combinations(active, size):
                dual_examined += 1
                matrix = tuple(
                    tuple(
                        problem.inequalities[index].coefficients[column]
                        for index in support
                    )
                    for column in range(dimension)
                )
                weights = _solve_unique_rectangular(
                    matrix,
                    problem.objective_coefficients,
                )
                if weights is None or any(weight < 0 for weight in weights):
                    continue
                full = [Fraction(0)] * row_count
                for index, weight in zip(support, weights):
                    full[index] = weight
                candidate_value = problem.objective_constant + sum(
                    (
                        weight * problem.inequalities[index].bound
                        for index, weight in zip(support, weights)
                    ),
                    Fraction(0),
                )
                if (
                    best_dual_value is None
                    or candidate_value < best_dual_value
                    or (
                        candidate_value == best_dual_value
                        and tuple(support) < best_support
                    )
                ):
                    best_dual = tuple(full)
                    best_dual_value = candidate_value
                    best_support = tuple(
                        index for index, weight in enumerate(full) if weight
                    )
        if (
            best_dual is None
            or best_dual_value is None
            or best_support is None
            or best_dual_value != best_value
        ):
            raise AssertionError("no exact zero-gap sparse dual certificate was found")
        dual = best_dual
        dual_support = best_support
        dual_value = best_dual_value

    eta = problem.drift_per_step
    marginal_certificates = tuple(
        maximize_expectation_tv_ball(
            problem.nominal_prior,
            vector,
            min(Fraction(1), eta * period),
        )
        for period, vector in enumerate(problem.cost_vectors, start=1)
    )
    marginal_path = tuple(
        certificate.extremal_distribution for certificate in marginal_certificates
    )
    previous = problem.nominal_prior
    marginal_feasible = True
    for distribution in marginal_path:
        if total_variation_distance(previous, distribution) > eta:
            marginal_feasible = False
            break
        previous = distribution

    path = _free_point_to_path(
        best_point,
        state_count=problem.state_count,
        horizon=problem.horizon,
    )
    result = CoupledDriftPathCertificate(
        problem,
        best_point,
        path,
        best_value,
        best_basis,
        dual,
        dual_support,
        dual_value,
        candidate_bases,
        bases_examined,
        dual_examined,
        max_bases,
        max_dual_supports,
        marginal_certificates,
        sum(
            (certificate.extremal_expectation for certificate in marginal_certificates),
            Fraction(0),
        ),
        marginal_feasible,
    )
    if not result.valid:
        raise AssertionError("coupled drift path certificate failed validation")
    return result


def _simplex_vertices(state_count: int) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(Fraction(1) if row == column else Fraction(0) for column in range(state_count))
        for row in range(state_count)
    )


@dataclass(frozen=True)
class PrecommittedCodeSequenceCertificate:
    graph: ConfusionGraph
    nominal_prior: tuple[Fraction, ...]
    drift_per_step: Fraction
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    selected_indices: tuple[int, ...]
    selected_candidates: tuple[RobustCodeCandidate, ...]
    selected_path: CoupledDriftPathCertificate
    switching_count: int
    total_value: Fraction
    static_best_value: Fraction
    static_best_index: int
    sequences_examined: int
    max_sequences: int

    @property
    def sequence_gain_over_static(self) -> Fraction:
        return self.static_best_value - self.total_value

    @property
    def valid(self) -> bool:
        candidates = self.enumeration.candidates
        if (
            self.horizon < 1
            or not candidates
            or len(self.selected_indices) != self.horizon
            or len(self.selected_candidates) != self.horizon
            or any(not 0 <= index < len(candidates) for index in self.selected_indices)
            or self.selected_candidates
            != tuple(candidates[index] for index in self.selected_indices)
            or not self.selected_path.valid
            or self.selected_path.polytope.cost_vectors
            != tuple(candidate.scenario_costs for candidate in self.selected_candidates)
            or self.selected_path.polytope.nominal_prior != self.nominal_prior
            or self.selected_path.polytope.drift_per_step != self.drift_per_step
            or self.switching_count
            != sum(
                left != right
                for left, right in zip(self.selected_indices, self.selected_indices[1:])
            )
            or self.total_value
            != self.selected_path.objective_value
            + self.switching_penalty * self.switching_count
            or self.sequence_gain_over_static < 0
            or not 0 <= self.static_best_index < len(candidates)
        ):
            return False
        return True


def exact_precommitted_code_sequence(
    graph: ConfusionGraph,
    nominal_prior: Sequence[RationalInput],
    drift_per_step: RationalInput,
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_sequences: int = 100_000,
    max_bases: int = 2_000_000,
    max_dual_supports: int = 2_000_000,
) -> PrecommittedCodeSequenceCertificate:
    prior = _validate_prior(nominal_prior)
    if graph.vertex_count != len(prior):
        raise ValueError("graph and nominal prior dimensions differ")
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
    if sequence_count > max_sequences:
        raise ValueError("precommitted code-sequence space exceeds configured cap")

    best_value: Fraction | None = None
    best_indices: tuple[int, ...] | None = None
    best_path: CoupledDriftPathCertificate | None = None
    examined = 0
    for indices in product(range(len(candidates)), repeat=periods):
        examined += 1
        costs = tuple(candidates[index].scenario_costs for index in indices)
        path = exact_coupled_drift_path(
            prior,
            costs,
            eta,
            max_bases=max_bases,
            max_dual_supports=max_dual_supports,
        )
        switches = sum(left != right for left, right in zip(indices, indices[1:]))
        value = path.objective_value + penalty * switches
        tie_key = (
            switches,
            tuple(candidates[index].scenario_costs for index in indices),
            indices,
        )
        current_key = None if best_indices is None else (
            sum(left != right for left, right in zip(best_indices, best_indices[1:])),
            tuple(candidates[index].scenario_costs for index in best_indices),
            best_indices,
        )
        if (
            best_value is None
            or value < best_value
            or (value == best_value and tie_key < current_key)
        ):
            best_value = value
            best_indices = tuple(indices)
            best_path = path
    if best_value is None or best_indices is None or best_path is None:
        raise AssertionError("no bounded precommitted code sequence was examined")

    static_values: list[Fraction] = []
    for index, candidate in enumerate(candidates):
        path = exact_coupled_drift_path(
            prior,
            tuple(candidate.scenario_costs for _ in range(periods)),
            eta,
            max_bases=max_bases,
            max_dual_supports=max_dual_supports,
        )
        static_values.append(path.objective_value)
    static_best = min(static_values)
    static_index = static_values.index(static_best)
    selected = tuple(candidates[index] for index in best_indices)
    switches = sum(left != right for left, right in zip(best_indices, best_indices[1:]))
    result = PrecommittedCodeSequenceCertificate(
        graph,
        prior,
        eta,
        periods,
        penalty,
        enumeration,
        best_indices,
        selected,
        best_path,
        switches,
        best_value,
        static_best,
        static_index,
        examined,
        max_sequences,
    )
    if not result.valid:
        raise AssertionError("precommitted code-sequence certificate failed validation")
    return result


def brute_force_two_state_path_grid(
    nominal_probability_state_one: ExactInput,
    cost_vectors: Sequence[Sequence[ExactInput]],
    drift_per_step: ExactInput,
    denominator: int,
) -> Fraction:
    """Independent exact grid audit for two-state path instances.

    The grid is only complete when the true optimizer lies on the declared
    rational grid.  It is a finite checker, not the primary theorem route.
    """

    p = _fraction(nominal_probability_state_one, name="nominal probability")
    eta = _validate_eta(drift_per_step)
    costs = _validate_cost_vectors(cost_vectors, 2)
    grid_denominator = int(denominator)
    if grid_denominator != denominator or grid_denominator < 1:
        raise ValueError("denominator must be a positive integer")
    grid = tuple(Fraction(index, grid_denominator) for index in range(grid_denominator + 1))
    best: Fraction | None = None
    for path in product(grid, repeat=len(costs)):
        previous = p
        feasible = True
        for value in path:
            if abs(value - previous) > eta:
                feasible = False
                break
            previous = value
        if not feasible:
            continue
        objective = sum(
            (
                probability * vector[1]
                + (Fraction(1) - probability) * vector[0]
                for probability, vector in zip(path, costs)
            ),
            Fraction(0),
        )
        if best is None or objective > best:
            best = objective
    if best is None:
        raise AssertionError("nominal grid point was unexpectedly absent")
    return best
