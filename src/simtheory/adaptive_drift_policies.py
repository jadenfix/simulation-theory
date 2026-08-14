"""Exact finite-grid games for source-drift information patterns.

The coupled-drift lane chooses an entire codebook sequence before the source-law
path.  This module varies *when* the designer learns the evolving source law.

Four deterministic information patterns are separated:

* open-loop: choose the complete code sequence before the path;
* delayed feedback: observe q_{t-1}, choose c_t, then nature chooses q_t;
* current-law feedback: nature chooses q_t, then the designer observes it and
  chooses c_t;
* clairvoyant: nature chooses the complete path, then the designer chooses the
  complete code sequence.

The source law is restricted to an exact rational simplex grid, and adjacent
laws must satisfy one declared exact total-variation step bound.  This turns the
problem into a finite directed game.  Dynamic programming solves the two
feedback games exactly over fractions; complete bounded enumeration solves the
open-loop and clairvoyant games.

The value hierarchy is

    V_clairvoyant <= V_current <= V_delayed <= V_open_loop,

because each information pattern gives the minimizing designer weakly more
information than the pattern to its right.  With zero switching cost,
current-law feedback and clairvoyance coincide: once q_t is observed, the code
choice decomposes period by period.

The finite grid is a restriction of the continuous bounded-TV path adversary.
Accordingly its open-loop value is a lower bound on the continuous open-loop
adversarial value for the same code universe.  Equality in examples is checked
rather than assumed.

All claims are finite-grid, finite-horizon, deterministic, exact-rational, and
bounded by explicit search caps.  They are not evidence for simulation and do
not translate source-coding costs into parent-substrate hardware or physics.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb
from typing import Iterable, Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import total_variation_distance
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)

ExactInput = RationalInput | Fraction | int
Distribution = tuple[Fraction, ...]
CodeSequence = tuple[int, ...]
LawPath = tuple[int, ...]


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


def _compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts < 1 or total < 0:
        return
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in _compositions(total - first, parts - 1):
            yield (first,) + tail


@dataclass(frozen=True)
class RationalSimplexGrid:
    state_count: int
    denominator: int
    drift_per_step: Fraction
    laws: tuple[Distribution, ...]
    transitions: tuple[tuple[int, ...], ...]
    candidate_law_pairs: int
    pairs_examined: int
    max_law_pairs: int

    @property
    def law_count(self) -> int:
        return len(self.laws)

    @property
    def valid(self) -> bool:
        if (
            self.state_count < 1
            or self.denominator < 1
            or not 0 <= self.drift_per_step <= 1
            or self.candidate_law_pairs != self.law_count * self.law_count
            or self.pairs_examined != self.candidate_law_pairs
            or self.pairs_examined > self.max_law_pairs
            or len(self.transitions) != self.law_count
            or len(set(self.laws)) != self.law_count
        ):
            return False
        expected_count = comb(
            self.denominator + self.state_count - 1,
            self.state_count - 1,
        )
        if self.law_count != expected_count:
            return False
        for law in self.laws:
            if (
                len(law) != self.state_count
                or any(value < 0 for value in law)
                or sum(law, Fraction(0)) != 1
                or any(value.denominator > self.denominator for value in law)
            ):
                return False
        for left, neighbors in enumerate(self.transitions):
            if left not in neighbors or tuple(sorted(set(neighbors))) != neighbors:
                return False
            for right in neighbors:
                if (
                    not 0 <= right < self.law_count
                    or left not in self.transitions[right]
                    or total_variation_distance(self.laws[left], self.laws[right])
                    > self.drift_per_step
                ):
                    return False
        return True


def exact_simplex_grid(
    state_count: int,
    denominator: int,
    drift_per_step: ExactInput,
    *,
    max_law_pairs: int = 2_000_000,
) -> RationalSimplexGrid:
    """Construct the exact denominator grid and its TV transition graph."""

    n = int(state_count)
    denominator_value = int(denominator)
    if n != state_count or n < 1:
        raise ValueError("state_count must be a positive integer")
    if denominator_value != denominator or denominator_value < 1:
        raise ValueError("denominator must be a positive integer")
    eta = _fraction(drift_per_step, name="drift_per_step")
    if not 0 <= eta <= 1:
        raise ValueError("drift_per_step must lie in [0,1]")
    pair_cap = int(max_law_pairs)
    if pair_cap < 1:
        raise ValueError("max_law_pairs must be positive")

    laws = tuple(
        tuple(Fraction(count, denominator_value) for count in composition)
        for composition in _compositions(denominator_value, n)
    )
    candidate_pairs = len(laws) * len(laws)
    if candidate_pairs > pair_cap:
        raise ValueError("simplex-grid law-pair space exceeds configured cap")
    transitions = tuple(
        tuple(
            right
            for right, second in enumerate(laws)
            if total_variation_distance(first, second) <= eta
        )
        for first in laws
    )
    result = RationalSimplexGrid(
        n,
        denominator_value,
        eta,
        laws,
        transitions,
        candidate_pairs,
        candidate_pairs,
        pair_cap,
    )
    if not result.valid:
        raise AssertionError("rational simplex-grid certificate failed")
    return result


def _grid_index(grid: RationalSimplexGrid, law: Distribution) -> int:
    try:
        return grid.laws.index(law)
    except ValueError as error:
        raise ValueError(
            "initial law is not on the declared rational simplex grid"
        ) from error


def _simplex_vertices(state_count: int) -> tuple[Distribution, ...]:
    return tuple(
        tuple(
            Fraction(1) if state == vertex else Fraction(0)
            for state in range(state_count)
        )
        for vertex in range(state_count)
    )


def _candidate_cost(candidate: RobustCodeCandidate) -> tuple[Fraction, ...]:
    return tuple(candidate.scenario_costs)


def _stage_cost(
    law: Distribution,
    candidate: RobustCodeCandidate,
) -> Fraction:
    return sum(
        (
            probability * length
            for probability, length in zip(law, candidate.scenario_costs)
        ),
        Fraction(0),
    )


def _switch_cost(previous_code: int, current_code: int, penalty: Fraction) -> Fraction:
    return penalty if previous_code >= 0 and previous_code != current_code else Fraction(0)


def _switch_count(sequence: Sequence[int]) -> int:
    return sum(left != right for left, right in zip(sequence, sequence[1:]))


def _enumerate_paths(
    grid: RationalSimplexGrid,
    initial_law_index: int,
    horizon: int,
    *,
    max_paths: int,
) -> tuple[LawPath, ...]:
    paths: list[LawPath] = []

    def visit(previous: int, prefix: tuple[int, ...]) -> None:
        if len(prefix) == horizon:
            paths.append(prefix)
            if len(paths) > max_paths:
                raise ValueError("finite-grid path enumeration exceeded configured cap")
            return
        for next_law in grid.transitions[previous]:
            visit(next_law, prefix + (next_law,))

    visit(initial_law_index, tuple())
    return tuple(paths)


@dataclass(frozen=True)
class OpenLoopEvaluation:
    code_sequence: CodeSequence
    worst_value: Fraction
    worst_path: LawPath
    switch_count: int


@dataclass(frozen=True)
class PathOracleEvaluation:
    law_path: LawPath
    value: Fraction
    code_sequence: CodeSequence


@dataclass(frozen=True)
class BellmanEntry:
    pattern: str
    period: int
    previous_law: int
    previous_code: int
    value: Fraction
    selected_code: int
    selected_next_law: int


@dataclass(frozen=True)
class DriftInformationPatternCertificate:
    graph: ConfusionGraph
    nominal_prior: Distribution
    initial_law_index: int
    horizon: int
    switching_penalty: Fraction
    grid: RationalSimplexGrid
    enumeration: RobustCandidateEnumeration
    open_loop_evaluations: tuple[OpenLoopEvaluation, ...]
    selected_open_loop: OpenLoopEvaluation
    delayed_bellman_entries: tuple[BellmanEntry, ...]
    delayed_value: Fraction
    delayed_witness_path: LawPath
    delayed_witness_codes: CodeSequence
    current_bellman_entries: tuple[BellmanEntry, ...]
    current_value: Fraction
    current_witness_path: LawPath
    current_witness_codes: CodeSequence
    clairvoyant_evaluations: tuple[PathOracleEvaluation, ...]
    selected_clairvoyant: PathOracleEvaluation
    max_sequences: int
    max_paths: int

    @property
    def candidates(self) -> tuple[RobustCodeCandidate, ...]:
        return self.enumeration.candidates

    @property
    def open_loop_value(self) -> Fraction:
        return self.selected_open_loop.worst_value

    @property
    def clairvoyant_value(self) -> Fraction:
        return self.selected_clairvoyant.value

    @property
    def hierarchy(self) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        return (
            self.clairvoyant_value,
            self.current_value,
            self.delayed_value,
            self.open_loop_value,
        )

    @property
    def hierarchy_valid(self) -> bool:
        clairvoyant, current, delayed, open_loop = self.hierarchy
        return clairvoyant <= current <= delayed <= open_loop

    @property
    def valid(self) -> bool:
        candidates = self.candidates
        if (
            not self.grid.valid
            or not self.enumeration.valid
            or self.enumeration.graph != self.graph
            or self.graph.vertex_count != self.grid.state_count
            or self.nominal_prior != self.grid.laws[self.initial_law_index]
            or self.horizon < 1
            or self.switching_penalty < 0
            or not candidates
            or not self.open_loop_evaluations
            or self.selected_open_loop not in self.open_loop_evaluations
            or not self.clairvoyant_evaluations
            or self.selected_clairvoyant not in self.clairvoyant_evaluations
            or not self.hierarchy_valid
        ):
            return False

        sequence_count = len(candidates) ** self.horizon
        if (
            sequence_count > self.max_sequences
            or len(self.open_loop_evaluations) != sequence_count
        ):
            return False
        paths = _enumerate_paths(
            self.grid,
            self.initial_law_index,
            self.horizon,
            max_paths=self.max_paths,
        )
        if len(paths) != len(self.clairvoyant_evaluations):
            return False

        open_expected: list[OpenLoopEvaluation] = []
        for sequence in product(range(len(candidates)), repeat=self.horizon):
            path_values = tuple(
                (
                    _path_sequence_cost(
                        self.grid,
                        candidates,
                        path,
                        sequence,
                        self.switching_penalty,
                    ),
                    path,
                )
                for path in paths
            )
            value, worst_path = max(
                path_values,
                key=lambda item: (item[0], tuple(-x for x in item[1])),
            )
            open_expected.append(
                OpenLoopEvaluation(
                    tuple(sequence),
                    value,
                    worst_path,
                    _switch_count(sequence),
                )
            )
        if tuple(open_expected) != self.open_loop_evaluations:
            return False
        expected_open = min(
            self.open_loop_evaluations,
            key=lambda item: (
                item.worst_value,
                item.switch_count,
                item.code_sequence,
            ),
        )
        if expected_open != self.selected_open_loop:
            return False

        delayed_table = {
            (entry.period, entry.previous_law, entry.previous_code): entry
            for entry in self.delayed_bellman_entries
        }
        current_table = {
            (entry.period, entry.previous_law, entry.previous_code): entry
            for entry in self.current_bellman_entries
        }
        if (
            len(delayed_table) != len(self.delayed_bellman_entries)
            or len(current_table) != len(self.current_bellman_entries)
        ):
            return False

        @lru_cache(maxsize=None)
        def delayed_value(period: int, previous_law: int, previous_code: int) -> Fraction:
            if period == self.horizon:
                return Fraction(0)
            key = (period, previous_law, previous_code)
            entry = delayed_table.get(key)
            if entry is None or entry.pattern != "delayed":
                raise KeyError(key)
            code_values: list[tuple[Fraction, int, int]] = []
            for code, candidate in enumerate(candidates):
                law_values = tuple(
                    (
                        _stage_cost(self.grid.laws[next_law], candidate)
                        + delayed_value(period + 1, next_law, code),
                        next_law,
                    )
                    for next_law in self.grid.transitions[previous_law]
                )
                worst_value, worst_law = max(
                    law_values,
                    key=lambda item: (item[0], -item[1]),
                )
                code_values.append(
                    (
                        _switch_cost(
                            previous_code,
                            code,
                            self.switching_penalty,
                        )
                        + worst_value,
                        code,
                        worst_law,
                    )
                )
            value, code, worst_law = min(
                code_values,
                key=lambda item: (
                    item[0],
                    int(previous_code >= 0 and item[1] != previous_code),
                    item[1],
                    item[2],
                ),
            )
            if (
                entry.value != value
                or entry.selected_code != code
                or entry.selected_next_law != worst_law
            ):
                raise AssertionError("delayed Bellman entry mismatch")
            return value

        @lru_cache(maxsize=None)
        def current_value(period: int, previous_law: int, previous_code: int) -> Fraction:
            if period == self.horizon:
                return Fraction(0)
            key = (period, previous_law, previous_code)
            entry = current_table.get(key)
            if entry is None or entry.pattern != "current":
                raise KeyError(key)
            law_values: list[tuple[Fraction, int, int]] = []
            for next_law in self.grid.transitions[previous_law]:
                code_values = tuple(
                    (
                        _switch_cost(
                            previous_code,
                            code,
                            self.switching_penalty,
                        )
                        + _stage_cost(self.grid.laws[next_law], candidate)
                        + current_value(period + 1, next_law, code),
                        code,
                    )
                    for code, candidate in enumerate(candidates)
                )
                best_value, best_code = min(
                    code_values,
                    key=lambda item: (
                        item[0],
                        int(previous_code >= 0 and item[1] != previous_code),
                        item[1],
                    ),
                )
                law_values.append((best_value, next_law, best_code))
            value, worst_law, code = max(
                law_values,
                key=lambda item: (item[0], -item[1]),
            )
            if (
                entry.value != value
                or entry.selected_code != code
                or entry.selected_next_law != worst_law
            ):
                raise AssertionError("current Bellman entry mismatch")
            return value

        try:
            delayed_root = delayed_value(
                0,
                self.initial_law_index,
                -1,
            )
            current_root = current_value(
                0,
                self.initial_law_index,
                -1,
            )
        except (KeyError, AssertionError):
            return False
        if delayed_root != self.delayed_value or current_root != self.current_value:
            return False

        previous_law = self.initial_law_index
        previous_code = -1
        delayed_path: list[int] = []
        delayed_codes: list[int] = []
        for period in range(self.horizon):
            entry = delayed_table[(period, previous_law, previous_code)]
            delayed_codes.append(entry.selected_code)
            delayed_path.append(entry.selected_next_law)
            previous_law = entry.selected_next_law
            previous_code = entry.selected_code
        if (
            tuple(delayed_path) != self.delayed_witness_path
            or tuple(delayed_codes) != self.delayed_witness_codes
        ):
            return False

        previous_law = self.initial_law_index
        previous_code = -1
        current_path: list[int] = []
        current_codes: list[int] = []
        for period in range(self.horizon):
            entry = current_table[(period, previous_law, previous_code)]
            current_codes.append(entry.selected_code)
            current_path.append(entry.selected_next_law)
            previous_law = entry.selected_next_law
            previous_code = entry.selected_code
        if (
            tuple(current_path) != self.current_witness_path
            or tuple(current_codes) != self.current_witness_codes
        ):
            return False

        clair_expected: list[PathOracleEvaluation] = []
        for path in paths:
            sequence_values = tuple(
                (
                    _path_sequence_cost(
                        self.grid,
                        candidates,
                        path,
                        sequence,
                        self.switching_penalty,
                    ),
                    tuple(sequence),
                )
                for sequence in product(range(len(candidates)), repeat=self.horizon)
            )
            value, sequence = min(
                sequence_values,
                key=lambda item: (
                    item[0],
                    _switch_count(item[1]),
                    item[1],
                ),
            )
            clair_expected.append(PathOracleEvaluation(path, value, sequence))
        if tuple(clair_expected) != self.clairvoyant_evaluations:
            return False
        expected_clairvoyant = max(
            self.clairvoyant_evaluations,
            key=lambda item: (item.value, tuple(-x for x in item.law_path)),
        )
        return expected_clairvoyant == self.selected_clairvoyant


def _path_sequence_cost(
    grid: RationalSimplexGrid,
    candidates: Sequence[RobustCodeCandidate],
    path: LawPath,
    sequence: Sequence[int],
    switching_penalty: Fraction,
) -> Fraction:
    if len(path) != len(sequence):
        raise ValueError("path and code sequence horizons differ")
    total = Fraction(0)
    previous_code = -1
    for law_index, code_index in zip(path, sequence):
        total += _switch_cost(previous_code, code_index, switching_penalty)
        total += _stage_cost(grid.laws[law_index], candidates[code_index])
        previous_code = code_index
    return total


def exact_drift_information_patterns(
    graph: ConfusionGraph,
    nominal_prior: Sequence[ExactInput],
    denominator: int,
    drift_per_step: ExactInput,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_law_pairs: int = 2_000_000,
    max_paths: int = 250_000,
    max_sequences: int = 250_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> DriftInformationPatternCertificate:
    """Solve four exact finite-grid drift information patterns.

    The code universe is the complete bounded componentwise-undominated set of
    deterministic zero-error binary prefix codes.  The source law follows the
    exact rational grid transition graph.
    """

    prior = _validate_prior(nominal_prior)
    if len(prior) != graph.vertex_count:
        raise ValueError("graph and nominal prior dimensions differ")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    grid = exact_simplex_grid(
        graph.vertex_count,
        denominator,
        drift_per_step,
        max_law_pairs=max_law_pairs,
    )
    initial = _grid_index(grid, prior)
    paths = _enumerate_paths(
        grid,
        initial,
        periods,
        max_paths=int(max_paths),
    )

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
        raise ValueError("finite-grid code-sequence space exceeds configured cap")

    # Open-loop: code sequence first, source path second.
    open_evaluations: list[OpenLoopEvaluation] = []
    for sequence in product(range(len(candidates)), repeat=periods):
        path_values = tuple(
            (
                _path_sequence_cost(
                    grid,
                    candidates,
                    path,
                    sequence,
                    penalty,
                ),
                path,
            )
            for path in paths
        )
        value, worst_path = max(
            path_values,
            key=lambda item: (item[0], tuple(-x for x in item[1])),
        )
        open_evaluations.append(
            OpenLoopEvaluation(
                tuple(sequence),
                value,
                worst_path,
                _switch_count(sequence),
            )
        )
    selected_open = min(
        open_evaluations,
        key=lambda item: (
            item.worst_value,
            item.switch_count,
            item.code_sequence,
        ),
    )

    # Delayed feedback: code sees q_{t-1}; nature then selects q_t.
    delayed_table: dict[tuple[int, int, int], BellmanEntry] = {}

    @lru_cache(maxsize=None)
    def delayed(period: int, previous_law: int, previous_code: int) -> Fraction:
        if period == periods:
            return Fraction(0)
        code_choices: list[tuple[Fraction, int, int]] = []
        for code, candidate in enumerate(candidates):
            law_choices = tuple(
                (
                    _stage_cost(grid.laws[next_law], candidate)
                    + delayed(period + 1, next_law, code),
                    next_law,
                )
                for next_law in grid.transitions[previous_law]
            )
            worst_value, worst_law = max(
                law_choices,
                key=lambda item: (item[0], -item[1]),
            )
            code_choices.append(
                (
                    _switch_cost(previous_code, code, penalty) + worst_value,
                    code,
                    worst_law,
                )
            )
        value, code, worst_law = min(
            code_choices,
            key=lambda item: (
                item[0],
                int(previous_code >= 0 and item[1] != previous_code),
                item[1],
                item[2],
            ),
        )
        delayed_table[(period, previous_law, previous_code)] = BellmanEntry(
            "delayed",
            period,
            previous_law,
            previous_code,
            value,
            code,
            worst_law,
        )
        return value

    delayed_value = delayed(0, initial, -1)
    delayed_path: list[int] = []
    delayed_codes: list[int] = []
    previous_law = initial
    previous_code = -1
    for period in range(periods):
        entry = delayed_table[(period, previous_law, previous_code)]
        delayed_codes.append(entry.selected_code)
        delayed_path.append(entry.selected_next_law)
        previous_law = entry.selected_next_law
        previous_code = entry.selected_code

    # Current-law feedback: nature picks q_t, then code observes q_t.
    current_table: dict[tuple[int, int, int], BellmanEntry] = {}

    @lru_cache(maxsize=None)
    def current(period: int, previous_law: int, previous_code: int) -> Fraction:
        if period == periods:
            return Fraction(0)
        law_choices: list[tuple[Fraction, int, int]] = []
        for next_law in grid.transitions[previous_law]:
            code_choices = tuple(
                (
                    _switch_cost(previous_code, code, penalty)
                    + _stage_cost(grid.laws[next_law], candidate)
                    + current(period + 1, next_law, code),
                    code,
                )
                for code, candidate in enumerate(candidates)
            )
            best_value, best_code = min(
                code_choices,
                key=lambda item: (
                    item[0],
                    int(previous_code >= 0 and item[1] != previous_code),
                    item[1],
                ),
            )
            law_choices.append((best_value, next_law, best_code))
        value, worst_law, code = max(
            law_choices,
            key=lambda item: (item[0], -item[1]),
        )
        current_table[(period, previous_law, previous_code)] = BellmanEntry(
            "current",
            period,
            previous_law,
            previous_code,
            value,
            code,
            worst_law,
        )
        return value

    current_value = current(0, initial, -1)
    current_path: list[int] = []
    current_codes: list[int] = []
    previous_law = initial
    previous_code = -1
    for period in range(periods):
        entry = current_table[(period, previous_law, previous_code)]
        current_codes.append(entry.selected_code)
        current_path.append(entry.selected_next_law)
        previous_law = entry.selected_next_law
        previous_code = entry.selected_code

    # Clairvoyant: path first, entire code sequence second.
    clair_evaluations: list[PathOracleEvaluation] = []
    for path in paths:
        sequence_values = tuple(
            (
                _path_sequence_cost(
                    grid,
                    candidates,
                    path,
                    sequence,
                    penalty,
                ),
                sequence,
            )
            for sequence in product(range(len(candidates)), repeat=periods)
        )
        value, best_sequence = min(
            sequence_values,
            key=lambda item: (
                item[0],
                _switch_count(item[1]),
                item[1],
            ),
        )
        clair_evaluations.append(
            PathOracleEvaluation(path, value, best_sequence)
        )
    selected_clair = max(
        clair_evaluations,
        key=lambda item: (item.value, tuple(-x for x in item.law_path)),
    )

    result = DriftInformationPatternCertificate(
        graph,
        prior,
        initial,
        periods,
        penalty,
        grid,
        enumeration,
        tuple(open_evaluations),
        selected_open,
        tuple(
            delayed_table[key]
            for key in sorted(delayed_table)
        ),
        delayed_value,
        tuple(delayed_path),
        tuple(delayed_codes),
        tuple(
            current_table[key]
            for key in sorted(current_table)
        ),
        current_value,
        tuple(current_path),
        tuple(current_codes),
        tuple(clair_evaluations),
        selected_clair,
        int(max_sequences),
        int(max_paths),
    )
    if not result.valid:
        raise AssertionError("drift information-pattern certificate failed")
    return result
