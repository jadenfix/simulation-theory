"""Exact finite-prior robust zero-error prefix coding.

A code that is Huffman-optimal for one source prior can be fragile when several
priors remain plausible.  This module separates three finite one-shot design
objectives:

* deterministic minimax expected length;
* deterministic minimax regret relative to a prior-specific oracle;
* minimax mixtures of complete deterministic codebooks selected by shared
  randomness independent of the source state.

The deterministic robust optimum need not be Huffman-optimal under any one
scenario.  The checker therefore enumerates every bounded proper independent-
set partition and every bounded complete binary prefix-length assignment.  It
deduplicates equal scenario-cost vectors, removes Pareto-dominated candidates,
and then solves the remaining finite decisions exactly over rational numbers.

Shared codebook randomness produces a finite zero-sum game.  Exact support
enumeration solves both the encoder's primal mixture problem and the
adversary's dual least-favorable-scenario problem, returning a zero rational
duality gap.  The seed is an explicit assistance resource known to every
receiver; private encoder randomness is not silently substituted for it.

All results are finite, one-shot, exact-rational, common-message, binary-prefix,
and zero-error.  They are not evidence for simulation and do not translate
message lengths or shared random seeds into parent-universe hardware, energy,
mass, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import comb
from typing import Mapping, Sequence

from .confusion_graphs import (
    ChromaticCertificate,
    ConfusionGraph,
    exact_chromatic_certificate,
)
from .prior_weighted_codes import (
    Partition,
    RationalInput,
    canonicalize_partition,
    coloring_from_partition,
    iter_proper_partitions,
    partition_is_proper,
    prefix_free,
    validate_rational_prior,
)


@dataclass(frozen=True)
class CompletePrefixShape:
    """One labeled complete binary prefix tree represented by leaf depths."""

    lengths: tuple[int, ...]
    codewords: tuple[str, ...]
    kraft_sum: Fraction

    @property
    def message_count(self) -> int:
        return len(self.lengths)

    @property
    def maximum_length(self) -> int:
        return max(self.lengths)

    @property
    def valid(self) -> bool:
        if not self.lengths or len(self.codewords) != len(self.lengths):
            return False
        if self.message_count == 1:
            return (
                self.lengths == (0,)
                and self.codewords == ("",)
                and self.kraft_sum == 1
            )
        return (
            all(1 <= length <= self.message_count - 1 for length in self.lengths)
            and self.lengths
            == tuple(len(codeword) for codeword in self.codewords)
            and prefix_free(self.codewords)
            and self.kraft_sum
            == sum(
                (Fraction(1, 1 << length) for length in self.lengths),
                Fraction(0),
            )
            and self.kraft_sum == 1
        )


def canonical_codewords_from_lengths(
    lengths: Sequence[int],
) -> tuple[str, ...]:
    """Construct one canonical binary prefix code for a Kraft-feasible vector."""

    supplied = tuple(int(length) for length in lengths)
    if not supplied:
        raise ValueError("at least one codeword length is required")
    if len(supplied) == 1:
        if supplied != (0,):
            raise ValueError("a one-message complete prefix code has length zero")
        return ("",)
    if any(length < 1 for length in supplied):
        raise ValueError("multi-message prefix lengths must be positive")
    if sum(
        (Fraction(1, 1 << length) for length in supplied),
        Fraction(0),
    ) > 1:
        raise ValueError("prefix lengths violate Kraft's inequality")

    order = tuple(
        sorted(
            range(len(supplied)),
            key=lambda index: (supplied[index], index),
        )
    )
    words = [""] * len(supplied)
    code = 0
    previous_length = supplied[order[0]]
    for position, symbol in enumerate(order):
        length = supplied[symbol]
        if position:
            code = (code + 1) << (length - previous_length)
        if code >= 1 << length:
            raise ValueError("prefix lengths have no canonical binary realization")
        words[symbol] = format(code, f"0{length}b")
        previous_length = length
    result = tuple(words)
    if not prefix_free(result):
        raise AssertionError("canonical prefix construction is not prefix-free")
    return result


@lru_cache(maxsize=None)
def _complete_prefix_shapes_cached(
    message_count: int,
    max_prefix_assignments: int,
    max_shapes: int,
) -> tuple[CompletePrefixShape, ...]:
    count = int(message_count)
    assignment_cap = int(max_prefix_assignments)
    shape_cap = int(max_shapes)
    if count < 1 or assignment_cap < 1 or shape_cap < 1:
        raise ValueError("message count and prefix-search caps must be positive")
    if count == 1:
        return (CompletePrefixShape((0,), ("",), Fraction(1)),)

    assignment_space = (count - 1) ** count
    if assignment_space > assignment_cap:
        raise ValueError(
            "complete prefix-length assignment space exceeds the configured cap"
        )

    shapes: list[CompletePrefixShape] = []
    for lengths in product(range(1, count), repeat=count):
        kraft = sum(
            (Fraction(1, 1 << length) for length in lengths),
            Fraction(0),
        )
        if kraft != 1:
            continue
        shape = CompletePrefixShape(
            tuple(lengths),
            canonical_codewords_from_lengths(lengths),
            kraft,
        )
        if not shape.valid:
            raise AssertionError("complete prefix shape failed validation")
        shapes.append(shape)
        if len(shapes) > shape_cap:
            raise ValueError(
                "complete prefix-shape enumeration exceeded the configured cap"
            )
    if not shapes:
        raise AssertionError("every positive message count has a complete tree")
    return tuple(shapes)


def complete_prefix_shapes(
    message_count: int,
    *,
    max_prefix_assignments: int = 10_000_000,
    max_shapes: int = 100_000,
) -> tuple[CompletePrefixShape, ...]:
    """Enumerate every labeled complete binary prefix-length vector.

    Every robust objective implemented here is coordinatewise nondecreasing in
    the state lengths.  Contracting a unary internal node weakly shortens all
    leaves below it, so some optimum is a full binary tree.  A full tree with
    ``k`` leaves has maximum leaf depth at most ``k-1``; enumerating lengths
    ``1..k-1`` with Kraft equality is therefore complete.
    """

    return _complete_prefix_shapes_cached(
        int(message_count),
        int(max_prefix_assignments),
        int(max_shapes),
    )


@dataclass(frozen=True)
class RobustCodeCandidate:
    graph: ConfusionGraph
    partition: Partition
    coloring: tuple[int, ...]
    prefix_shape: CompletePrefixShape
    state_lengths: tuple[int, ...]
    scenario_costs: tuple[Fraction, ...]

    @property
    def message_count(self) -> int:
        return len(self.partition)

    @property
    def maximum_length(self) -> int:
        return self.prefix_shape.maximum_length

    @property
    def valid(self) -> bool:
        return (
            partition_is_proper(self.graph, self.partition)
            and self.coloring
            == coloring_from_partition(self.graph, self.partition)
            and self.prefix_shape.valid
            and self.prefix_shape.message_count == self.message_count
            and self.state_lengths
            == tuple(
                self.prefix_shape.lengths[self.coloring[index]]
                for index in range(self.graph.vertex_count)
            )
            and bool(self.scenario_costs)
        )


def _candidate_tie_key(
    candidate: RobustCodeCandidate,
) -> tuple[object, ...]:
    return (
        candidate.maximum_length,
        candidate.message_count,
        candidate.state_lengths,
        candidate.partition,
        candidate.prefix_shape.lengths,
    )


def _dominates(
    left: RobustCodeCandidate,
    right: RobustCodeCandidate,
) -> bool:
    no_worse = all(
        left_cost <= right_cost
        for left_cost, right_cost in zip(
            left.scenario_costs,
            right.scenario_costs,
        )
    )
    strictly_better = any(
        left_cost < right_cost
        for left_cost, right_cost in zip(
            left.scenario_costs,
            right.scenario_costs,
        )
    )
    return no_worse and strictly_better


def _scenario_costs(
    priors: Sequence[Sequence[Fraction]],
    state_lengths: Sequence[int],
) -> tuple[Fraction, ...]:
    return tuple(
        sum(
            (
                probability * length
                for probability, length in zip(prior, state_lengths)
            ),
            Fraction(0),
        )
        for prior in priors
    )


@dataclass(frozen=True)
class RobustCandidateEnumeration:
    graph: ConfusionGraph
    chromatic_certificate: ChromaticCertificate
    priors: tuple[tuple[Fraction, ...], ...]
    candidates: tuple[RobustCodeCandidate, ...]
    raw_candidate_count: int
    distinct_cost_count: int
    dominated_count: int
    partitions_examined: int
    max_vertices: int
    max_partitions: int
    max_candidates: int
    max_dominance_pairs: int

    @property
    def scenario_count(self) -> int:
        return len(self.priors)

    @property
    def fixed_length_upper_bound(self) -> int:
        return self.chromatic_certificate.fixed_length_bits

    @property
    def valid(self) -> bool:
        return (
            self.chromatic_certificate.valid
            and self.chromatic_certificate.graph == self.graph
            and bool(self.priors)
            and bool(self.candidates)
            and all(
                len(prior) == self.graph.vertex_count
                and all(probability >= 0 for probability in prior)
                and sum(prior, Fraction(0)) == 1
                for prior in self.priors
            )
            and all(
                candidate.graph == self.graph
                and candidate.valid
                and len(candidate.scenario_costs) == self.scenario_count
                and candidate.scenario_costs
                == _scenario_costs(self.priors, candidate.state_lengths)
                for candidate in self.candidates
            )
            and len({candidate.scenario_costs for candidate in self.candidates})
            == len(self.candidates)
            and self.raw_candidate_count >= self.distinct_cost_count
            and self.distinct_cost_count
            == len(self.candidates) + self.dominated_count
            and not any(
                _dominates(left, right)
                for left_index, left in enumerate(self.candidates)
                for right_index, right in enumerate(self.candidates)
                if left_index != right_index
            )
        )


def enumerate_robust_code_candidates(
    graph: ConfusionGraph,
    prior_scenarios: Sequence[
        Sequence[RationalInput] | Mapping[object, RationalInput]
    ],
    *,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> RobustCandidateEnumeration:
    """Enumerate the complete bounded deterministic robust code universe."""

    supplied_scenarios = tuple(prior_scenarios)
    if not supplied_scenarios:
        raise ValueError("at least one prior scenario is required")
    priors = tuple(
        validate_rational_prior(graph, scenario)
        for scenario in supplied_scenarios
    )
    candidate_cap = int(max_candidates)
    pair_cap = int(max_dominance_pairs)
    if candidate_cap < 1 or pair_cap < 1:
        raise ValueError("candidate and dominance caps must be positive")

    chromatic = exact_chromatic_certificate(
        graph,
        max_vertices=max_vertices,
    )
    by_cost: dict[tuple[Fraction, ...], RobustCodeCandidate] = {}
    raw_count = 0
    partitions_examined = 0
    for partition in iter_proper_partitions(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    ):
        partitions_examined += 1
        canonical = canonicalize_partition(partition)
        coloring = coloring_from_partition(graph, canonical)
        for shape in complete_prefix_shapes(
            len(canonical),
            max_prefix_assignments=max_prefix_assignments,
            max_shapes=max_prefix_shapes,
        ):
            raw_count += 1
            if raw_count > candidate_cap:
                raise ValueError(
                    "robust code enumeration exceeded the configured candidate "
                    "cap; no exact optimum was certified"
                )
            state_lengths = tuple(
                shape.lengths[coloring[index]]
                for index in range(graph.vertex_count)
            )
            costs = _scenario_costs(priors, state_lengths)
            candidate = RobustCodeCandidate(
                graph,
                canonical,
                coloring,
                shape,
                state_lengths,
                costs,
            )
            if not candidate.valid:
                raise AssertionError("robust code candidate failed validation")
            incumbent = by_cost.get(costs)
            if (
                incumbent is None
                or _candidate_tie_key(candidate) < _candidate_tie_key(incumbent)
            ):
                by_cost[costs] = candidate

    distinct = tuple(by_cost.values())
    if len(distinct) * max(0, len(distinct) - 1) > pair_cap:
        raise ValueError(
            "dominance comparison space exceeds the configured cap; "
            "no exact robust frontier was certified"
        )
    nondominated = tuple(
        sorted(
            (
                candidate
                for index, candidate in enumerate(distinct)
                if not any(
                    _dominates(other, candidate)
                    for other_index, other in enumerate(distinct)
                    if other_index != index
                )
            ),
            key=lambda candidate: (
                candidate.scenario_costs,
                _candidate_tie_key(candidate),
            ),
        )
    )
    certificate = RobustCandidateEnumeration(
        graph,
        chromatic,
        priors,
        nondominated,
        raw_count,
        len(distinct),
        len(distinct) - len(nondominated),
        partitions_examined,
        int(max_vertices),
        int(max_partitions),
        candidate_cap,
        pair_cap,
    )
    if not certificate.valid:
        raise AssertionError("robust candidate enumeration failed validation")
    return certificate


def _solve_square_rational_system(
    matrix: Sequence[Sequence[Fraction]],
    target: Sequence[Fraction],
) -> tuple[Fraction, ...] | None:
    rows = tuple(tuple(Fraction(value) for value in row) for row in matrix)
    right = tuple(Fraction(value) for value in target)
    if len(rows) != len(right):
        raise ValueError("linear-system target has the wrong length")
    if not rows:
        return ()
    width = len(rows[0])
    if width != len(rows) or any(len(row) != width for row in rows):
        raise ValueError("exact support solver requires a square matrix")
    augmented = [list(row) + [value] for row, value in zip(rows, right)]
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(column, width)
                if augmented[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        pivot_value = augmented[column][column]
        augmented[column] = [
            value / pivot_value for value in augmented[column]
        ]
        for row in range(width):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(
                        augmented[row],
                        augmented[column],
                    )
                ]
    return tuple(augmented[row][-1] for row in range(width))


@dataclass(frozen=True)
class ExactZeroSumGameCertificate:
    """Matching primal and dual certificates for a finite rational cost game."""

    cost_matrix: tuple[tuple[Fraction, ...], ...]
    code_mixture: tuple[Fraction, ...]
    scenario_mixture: tuple[Fraction, ...]
    scenario_costs: tuple[Fraction, ...]
    code_costs: tuple[Fraction, ...]
    value: Fraction
    primal_bases_examined: int
    dual_bases_examined: int
    configured_basis_cap: int

    @property
    def scenario_count(self) -> int:
        return len(self.cost_matrix)

    @property
    def code_count(self) -> int:
        return len(self.cost_matrix[0])

    @property
    def code_support(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, weight in enumerate(self.code_mixture)
            if weight > 0
        )

    @property
    def scenario_support(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, weight in enumerate(self.scenario_mixture)
            if weight > 0
        )

    @property
    def primal_value(self) -> Fraction:
        return max(self.scenario_costs)

    @property
    def dual_value(self) -> Fraction:
        return min(self.code_costs)

    @property
    def gap(self) -> Fraction:
        return self.primal_value - self.dual_value

    @property
    def valid(self) -> bool:
        return (
            bool(self.cost_matrix)
            and bool(self.cost_matrix[0])
            and all(len(row) == self.code_count for row in self.cost_matrix)
            and len(self.code_mixture) == self.code_count
            and len(self.scenario_mixture) == self.scenario_count
            and all(weight >= 0 for weight in self.code_mixture)
            and all(weight >= 0 for weight in self.scenario_mixture)
            and sum(self.code_mixture, Fraction(0)) == 1
            and sum(self.scenario_mixture, Fraction(0)) == 1
            and len(self.code_support) <= self.scenario_count
            and len(self.scenario_support) <= self.code_count
            and self.scenario_costs
            == tuple(
                sum(
                    (
                        weight * self.cost_matrix[scenario][code]
                        for code, weight in enumerate(self.code_mixture)
                    ),
                    Fraction(0),
                )
                for scenario in range(self.scenario_count)
            )
            and self.code_costs
            == tuple(
                sum(
                    (
                        weight * self.cost_matrix[scenario][code]
                        for scenario, weight in enumerate(
                            self.scenario_mixture
                        )
                    ),
                    Fraction(0),
                )
                for code in range(self.code_count)
            )
            and self.primal_value == self.value
            and self.dual_value == self.value
            and self.gap == 0
        )


def _support_basis_count(row_count: int, column_count: int) -> int:
    return sum(
        comb(row_count, size) * comb(column_count, size)
        for size in range(1, min(row_count, column_count) + 1)
    )


def solve_exact_zero_sum_game(
    cost_matrix: Sequence[Sequence[Fraction]],
    *,
    max_bases: int = 2_000_000,
) -> ExactZeroSumGameCertificate:
    """Solve ``min_q max_r E_q[cost(r, code)]`` exactly.

    The primal LP mixes code columns; the dual LP mixes scenario rows.  At a
    vertex with ``s`` positive mixture weights, normalization plus ``s`` active
    opponent constraints determines the support values and game value.  The
    bounded checker enumerates every such square support system on both sides
    and verifies all omitted inequalities exactly.
    """

    matrix = tuple(
        tuple(Fraction(value) for value in row)
        for row in cost_matrix
    )
    if not matrix or not matrix[0]:
        raise ValueError("zero-sum game matrix must be nonempty")
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("zero-sum game matrix must be rectangular")
    row_count = len(matrix)
    basis_cap = int(max_bases)
    if basis_cap < 1:
        raise ValueError("game basis cap must be positive")
    possible = _support_basis_count(row_count, column_count)
    if 2 * possible > basis_cap:
        raise ValueError(
            "exact primal-dual support space exceeds the configured basis cap"
        )

    primal_best: tuple[
        Fraction,
        tuple[Fraction, ...],
        tuple[Fraction, ...],
        tuple[object, ...],
    ] | None = None
    primal_examined = 0
    for support_size in range(1, min(row_count, column_count) + 1):
        for code_support in combinations(range(column_count), support_size):
            for active_rows in combinations(range(row_count), support_size):
                primal_examined += 1
                equations: list[list[Fraction]] = [
                    [Fraction(1)] * support_size + [Fraction(0)]
                ]
                target = [Fraction(1)]
                for row in active_rows:
                    equations.append(
                        [matrix[row][code] for code in code_support]
                        + [Fraction(-1)]
                    )
                    target.append(Fraction(0))
                solution = _solve_square_rational_system(equations, target)
                if solution is None:
                    continue
                support_weights = solution[:-1]
                value = solution[-1]
                if any(weight < 0 for weight in support_weights):
                    continue
                mixture = [Fraction(0)] * column_count
                for code, weight in zip(code_support, support_weights):
                    mixture[code] = weight
                scenario_costs = tuple(
                    sum(
                        (
                            mixture[code] * matrix[row][code]
                            for code in range(column_count)
                        ),
                        Fraction(0),
                    )
                    for row in range(row_count)
                )
                if any(cost > value for cost in scenario_costs):
                    continue
                if max(scenario_costs) != value:
                    continue
                tie_key: tuple[object, ...] = (
                    sum(weight > 0 for weight in mixture),
                    tuple(code_support),
                    tuple(mixture),
                )
                candidate = (
                    value,
                    tuple(mixture),
                    scenario_costs,
                    tie_key,
                )
                if (
                    primal_best is None
                    or candidate[0] < primal_best[0]
                    or (
                        candidate[0] == primal_best[0]
                        and candidate[3] < primal_best[3]
                    )
                ):
                    primal_best = candidate

    dual_best: tuple[
        Fraction,
        tuple[Fraction, ...],
        tuple[Fraction, ...],
        tuple[object, ...],
    ] | None = None
    dual_examined = 0
    for support_size in range(1, min(row_count, column_count) + 1):
        for scenario_support in combinations(
            range(row_count), support_size
        ):
            for active_codes in combinations(
                range(column_count), support_size
            ):
                dual_examined += 1
                equations = [
                    [Fraction(1)] * support_size + [Fraction(0)]
                ]
                target = [Fraction(1)]
                for code in active_codes:
                    equations.append(
                        [matrix[row][code] for row in scenario_support]
                        + [Fraction(-1)]
                    )
                    target.append(Fraction(0))
                solution = _solve_square_rational_system(equations, target)
                if solution is None:
                    continue
                support_weights = solution[:-1]
                value = solution[-1]
                if any(weight < 0 for weight in support_weights):
                    continue
                mixture = [Fraction(0)] * row_count
                for row, weight in zip(scenario_support, support_weights):
                    mixture[row] = weight
                code_costs = tuple(
                    sum(
                        (
                            mixture[row] * matrix[row][code]
                            for row in range(row_count)
                        ),
                        Fraction(0),
                    )
                    for code in range(column_count)
                )
                if any(cost < value for cost in code_costs):
                    continue
                if min(code_costs) != value:
                    continue
                tie_key = (
                    sum(weight > 0 for weight in mixture),
                    tuple(scenario_support),
                    tuple(mixture),
                )
                candidate = (
                    value,
                    tuple(mixture),
                    code_costs,
                    tie_key,
                )
                if (
                    dual_best is None
                    or candidate[0] > dual_best[0]
                    or (
                        candidate[0] == dual_best[0]
                        and candidate[3] < dual_best[3]
                    )
                ):
                    dual_best = candidate

    if primal_best is None or dual_best is None:
        raise AssertionError(
            "finite zero-sum game has no support-enumerated optimum"
        )
    if primal_best[0] != dual_best[0]:
        raise AssertionError(
            "exact primal and dual game values disagree; support enumeration "
            "is incomplete"
        )
    certificate = ExactZeroSumGameCertificate(
        matrix,
        primal_best[1],
        dual_best[1],
        primal_best[2],
        dual_best[2],
        primal_best[0],
        primal_examined,
        dual_examined,
        basis_cap,
    )
    if not certificate.valid:
        raise AssertionError("exact zero-sum game certificate failed validation")
    return certificate


def convex_combination_prior(
    priors: Sequence[Sequence[Fraction]],
    weights: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    supplied_priors = tuple(
        tuple(Fraction(probability) for probability in prior)
        for prior in priors
    )
    supplied_weights = tuple(Fraction(weight) for weight in weights)
    if not supplied_priors:
        raise ValueError("at least one prior is required")
    if len(supplied_weights) != len(supplied_priors):
        raise ValueError("one mixture weight is required per prior")
    width = len(supplied_priors[0])
    if any(len(prior) != width for prior in supplied_priors):
        raise ValueError("prior vectors must have equal dimension")
    if any(weight < 0 for weight in supplied_weights):
        raise ValueError("prior mixture weights must be nonnegative")
    if sum(supplied_weights, Fraction(0)) != 1:
        raise ValueError("prior mixture weights must sum to one")
    result = tuple(
        sum(
            (
                weight * prior[index]
                for weight, prior in zip(
                    supplied_weights,
                    supplied_priors,
                )
            ),
            Fraction(0),
        )
        for index in range(width)
    )
    if any(probability < 0 for probability in result):
        raise AssertionError("convex prior mixture became negative")
    if sum(result, Fraction(0)) != 1:
        raise AssertionError("convex prior mixture lost normalization")
    return result


@dataclass(frozen=True)
class FinitePriorRobustCodeCertificate:
    enumeration: RobustCandidateEnumeration
    oracle_costs: tuple[Fraction, ...]
    deterministic_minimax_index: int
    deterministic_minimax_value: Fraction
    deterministic_regret_index: int
    deterministic_regret_value: Fraction
    mixed_minimax: ExactZeroSumGameCertificate
    mixed_regret: ExactZeroSumGameCertificate

    @property
    def candidates(self) -> tuple[RobustCodeCandidate, ...]:
        return self.enumeration.candidates

    @property
    def deterministic_minimax_candidate(self) -> RobustCodeCandidate:
        return self.candidates[self.deterministic_minimax_index]

    @property
    def deterministic_regret_candidate(self) -> RobustCodeCandidate:
        return self.candidates[self.deterministic_regret_index]

    @property
    def mixed_minimax_value(self) -> Fraction:
        return self.mixed_minimax.value

    @property
    def mixed_regret_value(self) -> Fraction:
        return self.mixed_regret.value

    @property
    def randomization_length_gain(self) -> Fraction:
        return self.deterministic_minimax_value - self.mixed_minimax_value

    @property
    def randomization_regret_gain(self) -> Fraction:
        return self.deterministic_regret_value - self.mixed_regret_value

    @property
    def fixed_length_upper_bound(self) -> int:
        return self.enumeration.fixed_length_upper_bound

    @property
    def least_favorable_prior(self) -> tuple[Fraction, ...]:
        """Dual barycenter prior for the shared-randomness minimax game."""

        return convex_combination_prior(
            self.enumeration.priors,
            self.mixed_minimax.scenario_mixture,
        )

    @property
    def mixed_code_support(self) -> tuple[int, ...]:
        return self.mixed_minimax.code_support

    @property
    def mixed_scenario_support(self) -> tuple[int, ...]:
        return self.mixed_minimax.scenario_support

    @property
    def valid(self) -> bool:
        scenario_count = self.enumeration.scenario_count
        candidate_count = len(self.candidates)
        length_matrix = tuple(
            tuple(
                candidate.scenario_costs[scenario]
                for candidate in self.candidates
            )
            for scenario in range(scenario_count)
        )
        regret_matrix = tuple(
            tuple(
                candidate.scenario_costs[scenario]
                - self.oracle_costs[scenario]
                for candidate in self.candidates
            )
            for scenario in range(scenario_count)
        )
        least_favorable_costs = tuple(
            sum(
                (
                    probability * length
                    for probability, length in zip(
                        self.least_favorable_prior,
                        candidate.state_lengths,
                    )
                ),
                Fraction(0),
            )
            for candidate in self.candidates
        )
        return (
            self.enumeration.valid
            and len(self.oracle_costs) == scenario_count
            and self.oracle_costs
            == tuple(
                min(
                    candidate.scenario_costs[scenario]
                    for candidate in self.candidates
                )
                for scenario in range(scenario_count)
            )
            and 0 <= self.deterministic_minimax_index < candidate_count
            and 0 <= self.deterministic_regret_index < candidate_count
            and self.deterministic_minimax_value
            == max(self.deterministic_minimax_candidate.scenario_costs)
            and self.deterministic_regret_value
            == max(
                cost - oracle
                for cost, oracle in zip(
                    self.deterministic_regret_candidate.scenario_costs,
                    self.oracle_costs,
                )
            )
            and self.mixed_minimax.cost_matrix == length_matrix
            and self.mixed_regret.cost_matrix == regret_matrix
            and self.mixed_minimax.valid
            and self.mixed_regret.valid
            and least_favorable_costs == self.mixed_minimax.code_costs
            and len(self.mixed_code_support) <= scenario_count
            and max(self.oracle_costs) <= self.mixed_minimax_value
            and self.mixed_minimax_value
            <= self.deterministic_minimax_value
            and self.deterministic_minimax_value
            <= self.fixed_length_upper_bound
            and 0 <= self.mixed_regret_value
            <= self.deterministic_regret_value
        )


def exact_finite_prior_robust_code(
    graph: ConfusionGraph,
    prior_scenarios: Sequence[
        Sequence[RationalInput] | Mapping[object, RationalInput]
    ],
    *,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_game_bases: int = 2_000_000,
) -> FinitePriorRobustCodeCertificate:
    """Return exact deterministic and shared-randomness robust certificates."""

    enumeration = enumerate_robust_code_candidates(
        graph,
        prior_scenarios,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    scenario_count = enumeration.scenario_count
    oracle_costs = tuple(
        min(
            candidate.scenario_costs[scenario]
            for candidate in candidates
        )
        for scenario in range(scenario_count)
    )

    deterministic_minimax_index = min(
        range(len(candidates)),
        key=lambda index: (
            max(candidates[index].scenario_costs),
            _candidate_tie_key(candidates[index]),
        ),
    )
    deterministic_minimax_value = max(
        candidates[deterministic_minimax_index].scenario_costs
    )

    deterministic_regret_index = min(
        range(len(candidates)),
        key=lambda index: (
            max(
                cost - oracle
                for cost, oracle in zip(
                    candidates[index].scenario_costs,
                    oracle_costs,
                )
            ),
            _candidate_tie_key(candidates[index]),
        ),
    )
    deterministic_regret_value = max(
        cost - oracle
        for cost, oracle in zip(
            candidates[deterministic_regret_index].scenario_costs,
            oracle_costs,
        )
    )

    length_matrix = tuple(
        tuple(
            candidate.scenario_costs[scenario]
            for candidate in candidates
        )
        for scenario in range(scenario_count)
    )
    regret_matrix = tuple(
        tuple(
            candidate.scenario_costs[scenario] - oracle_costs[scenario]
            for candidate in candidates
        )
        for scenario in range(scenario_count)
    )
    certificate = FinitePriorRobustCodeCertificate(
        enumeration,
        oracle_costs,
        deterministic_minimax_index,
        deterministic_minimax_value,
        deterministic_regret_index,
        deterministic_regret_value,
        solve_exact_zero_sum_game(
            length_matrix,
            max_bases=max_game_bases,
        ),
        solve_exact_zero_sum_game(
            regret_matrix,
            max_bases=max_game_bases,
        ),
    )
    if not certificate.valid:
        raise AssertionError(
            "finite-prior robust code certificate failed validation"
        )
    return certificate


def expected_length_under_prior(
    candidate: RobustCodeCandidate,
    prior: Sequence[RationalInput] | Mapping[object, RationalInput],
) -> Fraction:
    probabilities = validate_rational_prior(candidate.graph, prior)
    return sum(
        (
            probability * length
            for probability, length in zip(
                probabilities,
                candidate.state_lengths,
            )
        ),
        Fraction(0),
    )


def mixed_expected_length_under_prior(
    certificate: FinitePriorRobustCodeCertificate,
    code_mixture: Sequence[Fraction],
    prior: Sequence[RationalInput] | Mapping[object, RationalInput],
) -> Fraction:
    weights = tuple(Fraction(weight) for weight in code_mixture)
    if len(weights) != len(certificate.candidates):
        raise ValueError("one mixture weight is required per robust candidate")
    if any(weight < 0 for weight in weights):
        raise ValueError("code mixture weights must be nonnegative")
    if sum(weights, Fraction(0)) != 1:
        raise ValueError("code mixture weights must sum to one")
    return sum(
        (
            weight * expected_length_under_prior(candidate, prior)
            for weight, candidate in zip(weights, certificate.candidates)
        ),
        Fraction(0),
    )


def k3_shared_randomness_example() -> FinitePriorRobustCodeCertificate:
    graph = ConfusionGraph.from_edges(
        (0, 1, 2),
        ((0, 1), (0, 2), (1, 2)),
    )
    return exact_finite_prior_robust_code(
        graph,
        (
            (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
            (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
        ),
    )


def k4_nonoracle_minimax_example() -> FinitePriorRobustCodeCertificate:
    graph = ConfusionGraph.from_edges(
        (0, 1, 2, 3),
        tuple(combinations(range(4), 2)),
    )
    return exact_finite_prior_robust_code(
        graph,
        (
            (
                Fraction(1, 10),
                Fraction(1, 10),
                Fraction(1, 10),
                Fraction(7, 10),
            ),
            (
                Fraction(1, 10),
                Fraction(1, 10),
                Fraction(7, 10),
                Fraction(1, 10),
            ),
        ),
    )
