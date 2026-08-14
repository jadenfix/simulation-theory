"""Exact sufficient-state compression for feedback regret.

The full-history feedback-regret solver is deliberately conservative: the
terminal oracle subtraction depends on the realized source-law path, so it
stores the complete law history.  For the declared prefix-code comparator,
however, the history enters the clairvoyant oracle only through a finite dynamic
programming frontier.

After a realized prefix, let ``z_j`` be the minimum comparator cost among all
code sequences ending in codebook ``j``.  When the next law ``q`` is observed,

    z'_j = q . ell_j + min_i [z_i + kappa 1{i != j}].

At the first period there is no initial switching charge, so ``z_j`` is simply
the stage cost of codebook ``j``.  The path-specific oracle cost is ``min_j z_j``.
Therefore the exact feedback-regret Bellman state can replace the complete law
history by

    (period, current law, previous designer code, comparator frontier).

The update is translation equivariant: adding a common constant to every
frontier coordinate adds the same constant after every future update.  Hence a
scalar baseline plus the normalized relative frontier is sufficient; the
relative frontier determines future oracle switching choices while the baseline
tracks the absolute oracle cost.

This is an exact finite-state sufficiency result for the declared comparator,
not a claim that it is minimal for every model or that internal frontier entries
map to parent-substrate memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Sequence

from .adaptive_drift_policies import (
    CodeSequence,
    LawPath,
    _stage_cost,
    _switch_cost,
)
from .feedback_regret import DriftInformationRegretCertificate
from .feedback_regret_solver import exact_drift_information_regret

ComparatorFrontier = tuple[Fraction, ...]


def advance_comparator_frontier(
    frontier: Sequence[Fraction],
    law: Sequence[Fraction],
    candidates,
    switching_penalty: Fraction,
) -> ComparatorFrontier:
    """Advance the exact path-specific code-sequence oracle frontier."""

    supplied = tuple(Fraction(value) for value in frontier)
    penalty = Fraction(switching_penalty)
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")
    if supplied and len(supplied) != len(candidates):
        raise ValueError("frontier length must match the candidate count")
    stage = tuple(_stage_cost(tuple(law), candidate) for candidate in candidates)
    if not supplied:
        return stage
    return tuple(
        stage[next_code]
        + min(
            supplied[previous_code]
            + _switch_cost(previous_code, next_code, penalty)
            for previous_code in range(len(candidates))
        )
        for next_code in range(len(candidates))
    )


def comparator_frontier_for_path(
    path: LawPath,
    laws,
    candidates,
    switching_penalty: Fraction,
) -> ComparatorFrontier:
    frontier: ComparatorFrontier = tuple()
    for law_index in path:
        frontier = advance_comparator_frontier(
            frontier,
            laws[law_index],
            candidates,
            switching_penalty,
        )
    return frontier


def comparator_oracle_cost_from_frontier(frontier: Sequence[Fraction]) -> Fraction:
    supplied = tuple(Fraction(value) for value in frontier)
    if not supplied:
        raise ValueError("oracle frontier cannot be empty at a terminal state")
    return min(supplied)


def normalized_comparator_frontier(
    frontier: Sequence[Fraction],
) -> tuple[Fraction, ComparatorFrontier]:
    supplied = tuple(Fraction(value) for value in frontier)
    if not supplied:
        return Fraction(0), tuple()
    baseline = min(supplied)
    return baseline, tuple(value - baseline for value in supplied)


@dataclass(frozen=True)
class FrontierBellmanEntry:
    pattern: str
    period: int
    previous_law: int
    previous_designer_code: int
    comparator_frontier: ComparatorFrontier
    value: Fraction
    selected_designer_code: int
    selected_next_law: int


@dataclass(frozen=True)
class FrontierFeedbackRegretCertificate:
    full_history: DriftInformationRegretCertificate
    delayed_entries: tuple[FrontierBellmanEntry, ...]
    delayed_value: Fraction
    delayed_witness_path: LawPath
    delayed_witness_codes: CodeSequence
    current_entries: tuple[FrontierBellmanEntry, ...]
    current_value: Fraction
    current_witness_path: LawPath
    current_witness_codes: CodeSequence

    @property
    def delayed_full_history_state_count(self) -> int:
        return len(self.full_history.delayed_entries)

    @property
    def delayed_frontier_state_count(self) -> int:
        return len(self.delayed_entries)

    @property
    def current_full_history_state_count(self) -> int:
        return len(self.full_history.current_entries)

    @property
    def current_frontier_state_count(self) -> int:
        return len(self.current_entries)

    @property
    def delayed_state_reduction(self) -> int:
        return self.delayed_full_history_state_count - self.delayed_frontier_state_count

    @property
    def current_state_reduction(self) -> int:
        return self.current_full_history_state_count - self.current_frontier_state_count

    @property
    def valid(self) -> bool:
        full = self.full_history
        if (
            not full.valid
            or self.delayed_value != full.delayed_value
            or self.current_value != full.current_value
            or self.delayed_state_reduction < 0
            or self.current_state_reduction < 0
        ):
            return False
        oracle_map = dict(zip(full.paths, full.path_oracle_costs))
        for path, expected in oracle_map.items():
            frontier = comparator_frontier_for_path(
                path,
                full.absolute.grid.laws,
                full.candidates,
                full.absolute.switching_penalty,
            )
            if comparator_oracle_cost_from_frontier(frontier) != expected:
                return False

        delayed_table = {
            (
                entry.period,
                entry.previous_law,
                entry.previous_designer_code,
                entry.comparator_frontier,
            ): entry
            for entry in self.delayed_entries
        }
        current_table = {
            (
                entry.period,
                entry.previous_law,
                entry.previous_designer_code,
                entry.comparator_frontier,
            ): entry
            for entry in self.current_entries
        }
        if (
            len(delayed_table) != len(self.delayed_entries)
            or len(current_table) != len(self.current_entries)
        ):
            return False

        @lru_cache(maxsize=None)
        def delayed(
            period: int,
            previous_law: int,
            previous_code: int,
            frontier: ComparatorFrontier,
        ) -> Fraction:
            if period == full.absolute.horizon:
                return -comparator_oracle_cost_from_frontier(frontier)
            entry = delayed_table.get(
                (period, previous_law, previous_code, frontier)
            )
            if entry is None or entry.pattern != "delayed-frontier":
                raise KeyError((period, previous_law, previous_code, frontier))
            choices: list[tuple[Fraction, int, int]] = []
            for code, candidate in enumerate(full.candidates):
                next_values = tuple(
                    (
                        _stage_cost(full.absolute.grid.laws[next_law], candidate)
                        + delayed(
                            period + 1,
                            next_law,
                            code,
                            advance_comparator_frontier(
                                frontier,
                                full.absolute.grid.laws[next_law],
                                full.candidates,
                                full.absolute.switching_penalty,
                            ),
                        ),
                        next_law,
                    )
                    for next_law in full.absolute.grid.transitions[previous_law]
                )
                worst_value, worst_law = max(
                    next_values,
                    key=lambda item: (item[0], -item[1]),
                )
                choices.append(
                    (
                        _switch_cost(
                            previous_code,
                            code,
                            full.absolute.switching_penalty,
                        )
                        + worst_value,
                        code,
                        worst_law,
                    )
                )
            value, code, next_law = min(
                choices,
                key=lambda item: (
                    item[0],
                    int(previous_code >= 0 and item[1] != previous_code),
                    item[1],
                    item[2],
                ),
            )
            if (
                entry.value != value
                or entry.selected_designer_code != code
                or entry.selected_next_law != next_law
            ):
                raise AssertionError("delayed frontier Bellman mismatch")
            return value

        @lru_cache(maxsize=None)
        def current(
            period: int,
            previous_law: int,
            previous_code: int,
            frontier: ComparatorFrontier,
        ) -> Fraction:
            if period == full.absolute.horizon:
                return -comparator_oracle_cost_from_frontier(frontier)
            entry = current_table.get(
                (period, previous_law, previous_code, frontier)
            )
            if entry is None or entry.pattern != "current-frontier":
                raise KeyError((period, previous_law, previous_code, frontier))
            law_choices: list[tuple[Fraction, int, int]] = []
            for next_law in full.absolute.grid.transitions[previous_law]:
                next_frontier = advance_comparator_frontier(
                    frontier,
                    full.absolute.grid.laws[next_law],
                    full.candidates,
                    full.absolute.switching_penalty,
                )
                code_choices = tuple(
                    (
                        _switch_cost(
                            previous_code,
                            code,
                            full.absolute.switching_penalty,
                        )
                        + _stage_cost(full.absolute.grid.laws[next_law], candidate)
                        + current(
                            period + 1,
                            next_law,
                            code,
                            next_frontier,
                        ),
                        code,
                    )
                    for code, candidate in enumerate(full.candidates)
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
            value, next_law, code = max(
                law_choices,
                key=lambda item: (item[0], -item[1]),
            )
            if (
                entry.value != value
                or entry.selected_designer_code != code
                or entry.selected_next_law != next_law
            ):
                raise AssertionError("current frontier Bellman mismatch")
            return value

        try:
            delayed_root = delayed(
                0,
                full.absolute.initial_law_index,
                -1,
                tuple(),
            )
            current_root = current(
                0,
                full.absolute.initial_law_index,
                -1,
                tuple(),
            )
        except (KeyError, AssertionError, ValueError):
            return False
        if delayed_root != self.delayed_value or current_root != self.current_value:
            return False

        def replay(table, pattern):
            path: list[int] = []
            codes: list[int] = []
            previous_law = full.absolute.initial_law_index
            previous_code = -1
            frontier: ComparatorFrontier = tuple()
            for period in range(full.absolute.horizon):
                entry = table[(period, previous_law, previous_code, frontier)]
                if entry.pattern != pattern:
                    raise AssertionError("frontier witness pattern mismatch")
                path.append(entry.selected_next_law)
                codes.append(entry.selected_designer_code)
                frontier = advance_comparator_frontier(
                    frontier,
                    full.absolute.grid.laws[entry.selected_next_law],
                    full.candidates,
                    full.absolute.switching_penalty,
                )
                previous_law = entry.selected_next_law
                previous_code = entry.selected_designer_code
            return tuple(path), tuple(codes)

        try:
            if replay(delayed_table, "delayed-frontier") != (
                self.delayed_witness_path,
                self.delayed_witness_codes,
            ):
                return False
            if replay(current_table, "current-frontier") != (
                self.current_witness_path,
                self.current_witness_codes,
            ):
                return False
        except (KeyError, AssertionError):
            return False
        return True


def exact_frontier_feedback_regret(
    graph,
    nominal_prior,
    denominator: int,
    drift_per_step,
    horizon: int,
    *,
    switching_penalty=0,
    max_game_bases: int = 2_000_000,
    max_law_pairs: int = 2_000_000,
    max_paths: int = 250_000,
    max_sequences: int = 250_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> FrontierFeedbackRegretCertificate:
    """Solve full-history feedback regret and certify frontier compression."""

    full = exact_drift_information_regret(
        graph,
        nominal_prior,
        denominator,
        drift_per_step,
        horizon,
        switching_penalty=switching_penalty,
        max_game_bases=max_game_bases,
        max_law_pairs=max_law_pairs,
        max_paths=max_paths,
        max_sequences=max_sequences,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )

    delayed_table: dict[
        tuple[int, int, int, ComparatorFrontier], FrontierBellmanEntry
    ] = {}

    @lru_cache(maxsize=None)
    def delayed(
        period: int,
        previous_law: int,
        previous_code: int,
        frontier: ComparatorFrontier,
    ) -> Fraction:
        if period == full.absolute.horizon:
            return -comparator_oracle_cost_from_frontier(frontier)
        choices: list[tuple[Fraction, int, int]] = []
        for code, candidate in enumerate(full.candidates):
            next_values = tuple(
                (
                    _stage_cost(full.absolute.grid.laws[next_law], candidate)
                    + delayed(
                        period + 1,
                        next_law,
                        code,
                        advance_comparator_frontier(
                            frontier,
                            full.absolute.grid.laws[next_law],
                            full.candidates,
                            full.absolute.switching_penalty,
                        ),
                    ),
                    next_law,
                )
                for next_law in full.absolute.grid.transitions[previous_law]
            )
            worst_value, worst_law = max(
                next_values,
                key=lambda item: (item[0], -item[1]),
            )
            choices.append(
                (
                    _switch_cost(
                        previous_code,
                        code,
                        full.absolute.switching_penalty,
                    )
                    + worst_value,
                    code,
                    worst_law,
                )
            )
        value, code, next_law = min(
            choices,
            key=lambda item: (
                item[0],
                int(previous_code >= 0 and item[1] != previous_code),
                item[1],
                item[2],
            ),
        )
        delayed_table[(period, previous_law, previous_code, frontier)] = (
            FrontierBellmanEntry(
                "delayed-frontier",
                period,
                previous_law,
                previous_code,
                frontier,
                value,
                code,
                next_law,
            )
        )
        return value

    delayed_value = delayed(
        0,
        full.absolute.initial_law_index,
        -1,
        tuple(),
    )

    current_table: dict[
        tuple[int, int, int, ComparatorFrontier], FrontierBellmanEntry
    ] = {}

    @lru_cache(maxsize=None)
    def current(
        period: int,
        previous_law: int,
        previous_code: int,
        frontier: ComparatorFrontier,
    ) -> Fraction:
        if period == full.absolute.horizon:
            return -comparator_oracle_cost_from_frontier(frontier)
        law_choices: list[tuple[Fraction, int, int]] = []
        for next_law in full.absolute.grid.transitions[previous_law]:
            next_frontier = advance_comparator_frontier(
                frontier,
                full.absolute.grid.laws[next_law],
                full.candidates,
                full.absolute.switching_penalty,
            )
            code_choices = tuple(
                (
                    _switch_cost(
                        previous_code,
                        code,
                        full.absolute.switching_penalty,
                    )
                    + _stage_cost(full.absolute.grid.laws[next_law], candidate)
                    + current(
                        period + 1,
                        next_law,
                        code,
                        next_frontier,
                    ),
                    code,
                )
                for code, candidate in enumerate(full.candidates)
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
        value, next_law, code = max(
            law_choices,
            key=lambda item: (item[0], -item[1]),
        )
        current_table[(period, previous_law, previous_code, frontier)] = (
            FrontierBellmanEntry(
                "current-frontier",
                period,
                previous_law,
                previous_code,
                frontier,
                value,
                code,
                next_law,
            )
        )
        return value

    current_value = current(
        0,
        full.absolute.initial_law_index,
        -1,
        tuple(),
    )

    def replay(table):
        path: list[int] = []
        codes: list[int] = []
        previous_law = full.absolute.initial_law_index
        previous_code = -1
        frontier: ComparatorFrontier = tuple()
        for period in range(full.absolute.horizon):
            entry = table[(period, previous_law, previous_code, frontier)]
            path.append(entry.selected_next_law)
            codes.append(entry.selected_designer_code)
            frontier = advance_comparator_frontier(
                frontier,
                full.absolute.grid.laws[entry.selected_next_law],
                full.candidates,
                full.absolute.switching_penalty,
            )
            previous_law = entry.selected_next_law
            previous_code = entry.selected_designer_code
        return tuple(path), tuple(codes)

    delayed_path, delayed_codes = replay(delayed_table)
    current_path, current_codes = replay(current_table)
    result = FrontierFeedbackRegretCertificate(
        full,
        tuple(delayed_table[key] for key in sorted(delayed_table)),
        delayed_value,
        delayed_path,
        delayed_codes,
        tuple(current_table[key] for key in sorted(current_table)),
        current_value,
        current_path,
        current_codes,
    )
    if not result.valid:
        raise AssertionError("comparator-frontier feedback certificate failed")
    return result
