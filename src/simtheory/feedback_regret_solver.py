"""Scalable exact wrapper for finite-grid feedback-information regret.

The core validator and Bellman recurrences live in :mod:`feedback_regret`.
This module uses the same exact construction but solves the shared open-loop
regret game through certified duplicate and pointwise-dominance elimination.
The reduced game is lifted back to a full-matrix zero-gap certificate, so no
correctness claim depends on trusting the pruning routine.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from typing import Sequence

from .adaptive_drift_policies import (
    CodeSequence,
    ExactInput,
    LawPath,
    _path_sequence_cost,
    _stage_cost,
    _switch_cost,
    exact_drift_information_patterns,
)
from .confusion_graphs import ConfusionGraph
from .exact_game_pruning import solve_dominance_pruned_zero_sum_game
from .feedback_regret import (
    DriftInformationRegretCertificate,
    OpenLoopRegretEvaluation,
    RegretBellmanEntry,
)


def exact_drift_information_regret(
    graph: ConfusionGraph,
    nominal_prior: Sequence[ExactInput],
    denominator: int,
    drift_per_step: ExactInput,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
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
) -> DriftInformationRegretCertificate:
    """Solve exact feedback regret with a lifted full-game certificate."""

    absolute = exact_drift_information_patterns(
        graph,
        nominal_prior,
        denominator,
        drift_per_step,
        horizon,
        switching_penalty=switching_penalty,
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
    paths = tuple(
        evaluation.law_path
        for evaluation in absolute.clairvoyant_evaluations
    )
    oracle_map = {
        evaluation.law_path: evaluation.value
        for evaluation in absolute.clairvoyant_evaluations
    }
    oracle_costs = tuple(oracle_map[path] for path in paths)

    open_evaluations: list[OpenLoopRegretEvaluation] = []
    row_builders: list[list[Fraction]] = [[] for _ in paths]
    for evaluation in absolute.open_loop_evaluations:
        sequence = evaluation.code_sequence
        path_values = tuple(
            (
                _path_sequence_cost(
                    absolute.grid,
                    absolute.candidates,
                    path,
                    sequence,
                    absolute.switching_penalty,
                ),
                oracle_map[path],
                path,
            )
            for path in paths
        )
        decision_cost, oracle_cost, worst_path = max(
            path_values,
            key=lambda item: (
                item[0] - item[1],
                tuple(-index for index in item[2]),
            ),
        )
        open_evaluations.append(
            OpenLoopRegretEvaluation(
                sequence,
                decision_cost - oracle_cost,
                worst_path,
                decision_cost,
                oracle_cost,
            )
        )
        for row, (path_cost, path_oracle, _) in enumerate(path_values):
            row_builders[row].append(path_cost - path_oracle)
    selected_open = min(
        open_evaluations,
        key=lambda evaluation: (
            evaluation.worst_regret,
            evaluation.code_sequence,
        ),
    )
    shared_game = solve_dominance_pruned_zero_sum_game(
        tuple(tuple(row) for row in row_builders),
        max_bases=max_game_bases,
    ).lifted_game

    delayed_table: dict[tuple[int, LawPath, int], RegretBellmanEntry] = {}

    @lru_cache(maxsize=None)
    def delayed(period: int, history: LawPath, previous_code: int) -> Fraction:
        if period == absolute.horizon:
            return -oracle_map[history]
        previous_law = absolute.initial_law_index if not history else history[-1]
        choices: list[tuple[Fraction, int, int]] = []
        for code, candidate in enumerate(absolute.candidates):
            next_values = tuple(
                (
                    _stage_cost(absolute.grid.laws[next_law], candidate)
                    + delayed(period + 1, history + (next_law,), code),
                    next_law,
                )
                for next_law in absolute.grid.transitions[previous_law]
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
                        absolute.switching_penalty,
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
        delayed_table[(period, history, previous_code)] = RegretBellmanEntry(
            "delayed",
            period,
            history,
            previous_code,
            value,
            code,
            next_law,
        )
        return value

    delayed_value = delayed(0, tuple(), -1)

    current_table: dict[tuple[int, LawPath, int], RegretBellmanEntry] = {}

    @lru_cache(maxsize=None)
    def current(period: int, history: LawPath, previous_code: int) -> Fraction:
        if period == absolute.horizon:
            return -oracle_map[history]
        previous_law = absolute.initial_law_index if not history else history[-1]
        law_choices: list[tuple[Fraction, int, int]] = []
        for next_law in absolute.grid.transitions[previous_law]:
            code_choices = tuple(
                (
                    _switch_cost(
                        previous_code,
                        code,
                        absolute.switching_penalty,
                    )
                    + _stage_cost(absolute.grid.laws[next_law], candidate)
                    + current(period + 1, history + (next_law,), code),
                    code,
                )
                for code, candidate in enumerate(absolute.candidates)
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
        current_table[(period, history, previous_code)] = RegretBellmanEntry(
            "current",
            period,
            history,
            previous_code,
            value,
            code,
            next_law,
        )
        return value

    current_value = current(0, tuple(), -1)

    def witness(
        table: dict[tuple[int, LawPath, int], RegretBellmanEntry],
    ) -> tuple[LawPath, CodeSequence]:
        history: LawPath = tuple()
        codes: list[int] = []
        previous_code = -1
        for period in range(absolute.horizon):
            entry = table[(period, history, previous_code)]
            codes.append(entry.selected_code)
            history = history + (entry.selected_next_law,)
            previous_code = entry.selected_code
        return history, tuple(codes)

    delayed_path, delayed_codes = witness(delayed_table)
    current_path, current_codes = witness(current_table)

    result = DriftInformationRegretCertificate(
        absolute,
        oracle_costs,
        tuple(open_evaluations),
        selected_open,
        shared_game,
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
        raise AssertionError("finite-grid information-regret certificate failed")
    return result
