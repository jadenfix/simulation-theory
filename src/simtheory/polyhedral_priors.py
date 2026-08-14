"""Exact rational polyhedral ambiguity sets for finite source laws.

This module generalizes prior uncertainty from named shapes such as a finite
scenario set or a total-variation ball to an arbitrary bounded rational
polytope

    U = {q in Delta_{n-1}: A q <= b}.

The simplex equality is eliminated exactly, every vertex is enumerated from
active rational bases, and linear expectation extrema are certified by direct
vertex comparison.  Zero-error robust prefix coding then reduces to the
existing complete deterministic code universe evaluated on those vertices.

Two decision criteria are kept separate:

* worst-case expected length;
* worst-case regret relative to the source-law-specific coding oracle.

For regret, q -> L_c(q) - L*(q) is convex piecewise linear, so its maximum over
a compact polytope is attained at a vertex.  The same fact makes the shared-
randomness regret game finite once the ambiguity vertices are known.

All arithmetic in the geometric and coding layers is exact rational arithmetic.
This is a finite one-shot binary-prefix common-message zero-error model, not a
claim about physical simulator costs or evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Iterable, Mapping, Sequence

from .confusion_graphs import ConfusionGraph
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    ExactZeroSumGameCertificate,
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
    solve_exact_zero_sum_game,
)


def _fraction(value: RationalInput | Fraction | int) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _solve_square(
    matrix: Sequence[Sequence[Fraction]],
    rhs: Sequence[Fraction],
) -> tuple[Fraction, ...] | None:
    rows = [list(map(Fraction, row)) + [Fraction(value)] for row, value in zip(matrix, rhs)]
    n = len(rows)
    if n == 0:
        return ()
    if len(rhs) != n or any(len(row) != n + 1 for row in rows):
        raise ValueError("square rational system required")
    for column in range(n):
        pivot = next((row for row in range(column, n) if rows[row][column] != 0), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for row in range(n):
            if row == column:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(rows[row], rows[column])
                ]
    return tuple(rows[row][-1] for row in range(n))


@dataclass(frozen=True)
class LinearPriorConstraint:
    """One rational halfspace a.q <= b on a probability simplex."""

    coefficients: tuple[Fraction, ...]
    bound: Fraction
    label: str = ""

    @classmethod
    def from_values(
        cls,
        coefficients: Sequence[RationalInput],
        bound: RationalInput,
        label: str = "",
    ) -> "LinearPriorConstraint":
        return cls(tuple(_fraction(value) for value in coefficients), _fraction(bound), str(label))

    def value(self, distribution: Sequence[Fraction]) -> Fraction:
        if len(distribution) != len(self.coefficients):
            raise ValueError("distribution and constraint dimensions differ")
        return sum(
            (coefficient * probability for coefficient, probability in zip(self.coefficients, distribution)),
            Fraction(0),
        )

    def satisfied(self, distribution: Sequence[Fraction]) -> bool:
        return self.value(distribution) <= self.bound


@dataclass(frozen=True)
class PolyhedralPriorVertex:
    distribution: tuple[Fraction, ...]
    active_constraints: tuple[str, ...]


@dataclass(frozen=True)
class RationalPriorPolytope:
    state_count: int
    constraints: tuple[LinearPriorConstraint, ...]
    vertices: tuple[PolyhedralPriorVertex, ...]
    transformed_constraints: tuple[tuple[tuple[Fraction, ...], Fraction, str], ...]
    candidate_bases: int
    bases_examined: int
    nonsingular_bases: int
    max_bases: int

    @property
    def distributions(self) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(vertex.distribution for vertex in self.vertices)

    @property
    def empty(self) -> bool:
        return not self.vertices

    @property
    def dimension(self) -> int:
        return self.state_count - 1

    @property
    def valid(self) -> bool:
        if self.state_count < 1 or self.bases_examined != self.candidate_bases:
            return False
        if len(set(self.distributions)) != len(self.vertices):
            return False
        for vertex in self.vertices:
            q = vertex.distribution
            if (
                len(q) != self.state_count
                or any(value < 0 for value in q)
                or sum(q, Fraction(0)) != 1
                or any(not constraint.satisfied(q) for constraint in self.constraints)
            ):
                return False
        return 0 <= self.nonsingular_bases <= self.bases_examined <= self.max_bases


def _canonical_constraints(
    state_count: int,
    constraints: Sequence[LinearPriorConstraint],
) -> tuple[LinearPriorConstraint, ...]:
    n = int(state_count)
    if n < 1:
        raise ValueError("state_count must be positive")
    supplied = tuple(constraints)
    for constraint in supplied:
        if len(constraint.coefficients) != n:
            raise ValueError("every prior constraint must match state_count")
    return supplied


def _transformed_halfspaces(
    state_count: int,
    constraints: Sequence[LinearPriorConstraint],
) -> tuple[tuple[tuple[Fraction, ...], Fraction, str], ...]:
    """Eliminate q_n = 1 - sum_{j<n} q_j and append simplex inequalities."""

    n = int(state_count)
    d = n - 1
    rows: list[tuple[tuple[Fraction, ...], Fraction, str]] = []
    for index, constraint in enumerate(constraints):
        tail = constraint.coefficients[-1]
        coefficients = tuple(constraint.coefficients[j] - tail for j in range(d))
        bound = constraint.bound - tail
        rows.append((coefficients, bound, constraint.label or f"constraint[{index}]"))
    for j in range(d):
        coefficients = tuple(Fraction(-1) if k == j else Fraction(0) for k in range(d))
        rows.append((coefficients, Fraction(0), f"simplex:q[{j}]>=0"))
    rows.append((tuple(Fraction(1) for _ in range(d)), Fraction(1), f"simplex:q[{n-1}]>=0"))
    return tuple(rows)


def enumerate_prior_polytope(
    state_count: int,
    constraints: Sequence[LinearPriorConstraint],
    *,
    max_bases: int = 2_000_000,
) -> RationalPriorPolytope:
    """Enumerate every vertex of a rational simplex polytope exactly.

    A point in d dimensions is a polyhedral vertex iff the active constraint
    normals span R^d.  We therefore solve every d-row active basis and retain
    exactly the feasible solutions, deduplicating degeneracies.
    """

    n = int(state_count)
    canonical = _canonical_constraints(n, constraints)
    rows = _transformed_halfspaces(n, canonical)
    d = n - 1
    cap = int(max_bases)
    if cap < 1:
        raise ValueError("max_bases must be positive")

    if d == 0:
        q = (Fraction(1),)
        feasible = all(constraint.satisfied(q) for constraint in canonical)
        vertices = (PolyhedralPriorVertex(q, tuple()),) if feasible else tuple()
        certificate = RationalPriorPolytope(n, canonical, vertices, rows, 1, 1, 1, cap)
        if not certificate.valid:
            raise AssertionError("one-state polytope certificate failed")
        return certificate

    basis_count = comb(len(rows), d)
    if basis_count > cap:
        raise ValueError("polytope active-basis space exceeds configured cap")
    by_distribution: dict[tuple[Fraction, ...], set[str]] = {}
    nonsingular = 0
    examined = 0
    for basis in combinations(range(len(rows)), d):
        examined += 1
        solution = _solve_square(
            [rows[index][0] for index in basis],
            [rows[index][1] for index in basis],
        )
        if solution is None:
            continue
        nonsingular += 1
        if any(
            sum((coefficient * value for coefficient, value in zip(row, solution)), Fraction(0)) > bound
            for row, bound, _ in rows
        ):
            continue
        last = Fraction(1) - sum(solution, Fraction(0))
        q = tuple(solution) + (last,)
        if any(value < 0 for value in q):
            continue
        active = {
            label
            for row, bound, label in rows
            if sum((coefficient * value for coefficient, value in zip(row, solution)), Fraction(0)) == bound
        }
        by_distribution.setdefault(q, set()).update(active)

    vertices = tuple(
        PolyhedralPriorVertex(distribution, tuple(sorted(labels)))
        for distribution, labels in sorted(by_distribution.items())
    )
    certificate = RationalPriorPolytope(
        n,
        canonical,
        vertices,
        rows,
        basis_count,
        examined,
        nonsingular,
        cap,
    )
    if not certificate.valid:
        raise AssertionError("polyhedral prior certificate failed validation")
    return certificate


@dataclass(frozen=True)
class PolyhedralExpectationCertificate:
    polytope: RationalPriorPolytope
    values: tuple[Fraction, ...]
    maximize: bool
    optimum: Fraction
    optimizer: tuple[Fraction, ...]
    vertex_values: tuple[Fraction, ...]

    @property
    def valid(self) -> bool:
        if self.polytope.empty or len(self.values) != self.polytope.state_count:
            return False
        expected = tuple(
            sum((q * value for q, value in zip(vertex.distribution, self.values)), Fraction(0))
            for vertex in self.polytope.vertices
        )
        extremum = max(expected) if self.maximize else min(expected)
        return (
            expected == self.vertex_values
            and self.optimum == extremum
            and self.optimizer in self.polytope.distributions
            and sum((q * value for q, value in zip(self.optimizer, self.values)), Fraction(0)) == extremum
        )


def extremal_expectation(
    polytope: RationalPriorPolytope,
    values: Sequence[RationalInput],
    *,
    maximize: bool = True,
) -> PolyhedralExpectationCertificate:
    if polytope.empty:
        raise ValueError("cannot optimize over an empty prior polytope")
    vector = tuple(_fraction(value) for value in values)
    if len(vector) != polytope.state_count:
        raise ValueError("value vector must match state_count")
    vertex_values = tuple(
        sum((probability * value for probability, value in zip(vertex.distribution, vector)), Fraction(0))
        for vertex in polytope.vertices
    )
    optimum = (max if maximize else min)(vertex_values)
    index = vertex_values.index(optimum)
    certificate = PolyhedralExpectationCertificate(
        polytope,
        vector,
        bool(maximize),
        optimum,
        polytope.vertices[index].distribution,
        vertex_values,
    )
    if not certificate.valid:
        raise AssertionError("polyhedral expectation certificate failed")
    return certificate


def interval_prior_polytope(
    lower: Sequence[RationalInput],
    upper: Sequence[RationalInput],
    *,
    max_bases: int = 2_000_000,
) -> RationalPriorPolytope:
    lo = tuple(_fraction(value) for value in lower)
    hi = tuple(_fraction(value) for value in upper)
    if not lo or len(lo) != len(hi):
        raise ValueError("aligned nonempty lower and upper vectors required")
    if any(a < 0 or b > 1 or a > b for a, b in zip(lo, hi)):
        raise ValueError("invalid probability interval")
    n = len(lo)
    constraints: list[LinearPriorConstraint] = []
    for i in range(n):
        upper_row = tuple(Fraction(1) if j == i else Fraction(0) for j in range(n))
        lower_row = tuple(Fraction(-1) if j == i else Fraction(0) for j in range(n))
        constraints.append(LinearPriorConstraint(upper_row, hi[i], f"q[{i}]<=upper"))
        constraints.append(LinearPriorConstraint(lower_row, -lo[i], f"q[{i}]>=lower"))
    return enumerate_prior_polytope(n, constraints, max_bases=max_bases)


def huber_contamination_polytope(
    nominal: Sequence[RationalInput],
    epsilon: RationalInput,
    *,
    max_bases: int = 2_000_000,
) -> RationalPriorPolytope:
    p = tuple(_fraction(value) for value in nominal)
    e = _fraction(epsilon)
    if not p or any(value < 0 for value in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("nominal must be a probability vector")
    if not 0 <= e <= 1:
        raise ValueError("epsilon must lie in [0,1]")
    lower = tuple((1 - e) * value for value in p)
    upper = tuple((1 - e) * value + e for value in p)
    return interval_prior_polytope(lower, upper, max_bases=max_bases)


@dataclass(frozen=True)
class PolyhedralRobustCodeCertificate:
    polytope: RationalPriorPolytope
    enumeration: RobustCandidateEnumeration
    criterion: str
    deterministic_candidate: RobustCodeCandidate
    deterministic_value: Fraction
    oracle_costs: tuple[Fraction, ...]
    game: ExactZeroSumGameCertificate
    shared_value: Fraction

    @property
    def randomization_gain(self) -> Fraction:
        return self.deterministic_value - self.shared_value

    @property
    def valid(self) -> bool:
        if self.polytope.empty or self.criterion not in {"length", "regret"}:
            return False
        if self.enumeration.priors != self.polytope.distributions:
            return False
        if len(self.oracle_costs) != len(self.polytope.vertices) or not self.game.valid:
            return False
        candidates = self.enumeration.candidates
        expected_oracles = tuple(
            min(candidate.scenario_costs[r] for candidate in candidates)
            for r in range(len(self.polytope.vertices))
        )
        if expected_oracles != self.oracle_costs:
            return False
        matrix = tuple(
            tuple(
                candidate.scenario_costs[r]
                - (self.oracle_costs[r] if self.criterion == "regret" else Fraction(0))
                for candidate in candidates
            )
            for r in range(len(self.polytope.vertices))
        )
        deterministic_scores = tuple(max(matrix[r][c] for r in range(len(matrix))) for c in range(len(candidates)))
        best = min(deterministic_scores)
        chosen_index = candidates.index(self.deterministic_candidate)
        return (
            self.game.cost_matrix == matrix
            and self.deterministic_value == best
            and deterministic_scores[chosen_index] == best
            and self.shared_value == self.game.value
            and self.shared_value <= self.deterministic_value
        )


def exact_polyhedral_robust_prefix_code(
    graph: ConfusionGraph,
    polytope: RationalPriorPolytope,
    *,
    criterion: str = "length",
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_game_bases: int = 2_000_000,
) -> PolyhedralRobustCodeCertificate:
    """Solve deterministic and shared-randomness robustness over a polytope.

    For ``criterion='regret'`` each vertex payoff subtracts the nominal
    source-law-specific oracle L*(G,q).  Since regret is convex in q, checking
    all ambiguity vertices is exact for the entire polytope.
    """

    mode = str(criterion)
    if mode not in {"length", "regret"}:
        raise ValueError("criterion must be 'length' or 'regret'")
    if polytope.empty:
        raise ValueError("prior ambiguity set is empty")
    if graph.vertex_count != polytope.state_count:
        raise ValueError("graph and prior polytope dimensions differ")

    enumeration = enumerate_robust_code_candidates(
        graph,
        polytope.distributions,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    scenario_count = len(polytope.vertices)
    oracle_costs = tuple(
        min(candidate.scenario_costs[r] for candidate in candidates)
        for r in range(scenario_count)
    )
    matrix = tuple(
        tuple(
            candidate.scenario_costs[r]
            - (oracle_costs[r] if mode == "regret" else Fraction(0))
            for candidate in candidates
        )
        for r in range(scenario_count)
    )
    deterministic_scores = tuple(
        max(matrix[r][c] for r in range(scenario_count))
        for c in range(len(candidates))
    )
    deterministic_value = min(deterministic_scores)
    deterministic_index = deterministic_scores.index(deterministic_value)
    game = solve_exact_zero_sum_game(matrix, max_bases=max_game_bases)
    certificate = PolyhedralRobustCodeCertificate(
        polytope,
        enumeration,
        mode,
        candidates[deterministic_index],
        deterministic_value,
        oracle_costs,
        game,
        game.value,
    )
    if not certificate.valid:
        raise AssertionError("polyhedral robust-code certificate failed")
    return certificate
