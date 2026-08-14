"""Exact finite-grid regret for source-law information patterns.

The absolute-value information-pattern solver asks how much cumulative cost is
unavoidable under open-loop commitment, delayed source-law feedback, current-law
feedback, or clairvoyance.  This module asks a different question: how far each
information pattern lies above the path-specific clairvoyant code-sequence
oracle on the *same* source-law path.

For a grid path p and code sequence a, write C(a,p) for cumulative expected
prefix length plus the declared switching charge.  The comparator oracle is

    O(p) = min_a C(a,p).

Open-loop regret is solved by exact sequence/path enumeration.  Delayed and
current-law regret are solved by exact Bellman recurrences on the full observed
law history, because the terminal subtraction O(p) is path dependent and is not
in general a Markov function of the current law alone.  This full-history state
is deliberate: replacing it with the absolute-cost Markov state would silently
change the regret game.

The deterministic hierarchy is

    0 = R_clairvoyant <= R_current <= R_delayed <= R_open.

A separate source-independent common mixture over open-loop sequences is solved
as an exact finite rational zero-sum game.  It is not generally comparable with
deterministic current or delayed feedback, because randomization and information
are different resources.

All results are finite-grid, finite-horizon, deterministic-feedback or
source-independent shared-open-loop, exact-rational, and bounded by explicit
caps. They are not evidence for simulation and do not turn internal code lengths
or switching charges into parent-substrate resource claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Sequence

from .adaptive_drift_policies import (
    CodeSequence,
    DriftInformationPatternCertificate,
    ExactInput,
    LawPath,
    _path_sequence_cost,
    _stage_cost,
    _switch_cost,
    exact_drift_information_patterns,
)
from .confusion_graphs import ConfusionGraph
from .robust_prior_codes import ExactZeroSumGameCertificate, solve_exact_zero_sum_game


@dataclass(frozen=True)
class OpenLoopRegretEvaluation:
    code_sequence: CodeSequence
    worst_regret: Fraction
    worst_path: LawPath
    decision_cost_on_witness: Fraction
    oracle_cost_on_witness: Fraction


@dataclass(frozen=True)
class RegretBellmanEntry:
    pattern: str
    period: int
    law_history: LawPath
    previous_code: int
    value: Fraction
    selected_code: int
    selected_next_law: int


@dataclass(frozen=True)
class DriftInformationRegretCertificate:
    absolute: DriftInformationPatternCertificate
    path_oracle_costs: tuple[Fraction, ...]
    open_loop_evaluations: tuple[OpenLoopRegretEvaluation, ...]
    selected_open_loop: OpenLoopRegretEvaluation
    shared_open_loop_game: ExactZeroSumGameCertificate
    delayed_entries: tuple[RegretBellmanEntry, ...]
    delayed_value: Fraction
    delayed_witness_path: LawPath
    delayed_witness_codes: CodeSequence
    current_entries: tuple[RegretBellmanEntry, ...]
    current_value: Fraction
    current_witness_path: LawPath
    current_witness_codes: CodeSequence

    @property
    def paths(self) -> tuple[LawPath, ...]:
        return tuple(
            evaluation.law_path
            for evaluation in self.absolute.clairvoyant_evaluations
        )

    @property
    def candidates(self):
        return self.absolute.candidates

    @property
    def open_loop_value(self) -> Fraction:
        return self.selected_open_loop.worst_regret

    @property
    def shared_open_loop_value(self) -> Fraction:
        return self.shared_open_loop_game.value

    @property
    def clairvoyant_value(self) -> Fraction:
        return Fraction(0)

    @property
    def deterministic_hierarchy(self) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        return (
            self.clairvoyant_value,
            self.current_value,
            self.delayed_value,
            self.open_loop_value,
        )

    @property
    def hierarchy_valid(self) -> bool:
        clairvoyant, current, delayed, open_loop = self.deterministic_hierarchy
        return clairvoyant <= current <= delayed <= open_loop

    @property
    def randomization_gain_over_open_loop(self) -> Fraction:
        return self.open_loop_value - self.shared_open_loop_value

    @property
    def valid(self) -> bool:
        if (
            not self.absolute.valid
            or not self.paths
            or len(self.path_oracle_costs) != len(self.paths)
            or not self.open_loop_evaluations
            or self.selected_open_loop not in self.open_loop_evaluations
            or not self.shared_open_loop_game.valid
            or not self.hierarchy_valid
            or self.shared_open_loop_value > self.open_loop_value
            or self.randomization_gain_over_open_loop < 0
        ):
            return False

        oracle_map = {
            evaluation.law_path: evaluation.value
            for evaluation in self.absolute.clairvoyant_evaluations
        }
        if (
            len(oracle_map) != len(self.paths)
            or self.path_oracle_costs
            != tuple(oracle_map[path] for path in self.paths)
        ):
            return False

        sequence_evaluations: list[OpenLoopRegretEvaluation] = []
        regret_matrix_rows: list[tuple[Fraction, ...]] = [
            tuple() for _ in self.paths
        ]
        row_builders: list[list[Fraction]] = [[] for _ in self.paths]
        for open_evaluation in self.absolute.open_loop_evaluations:
            sequence = open_evaluation.code_sequence
            path_values = tuple(
                (
                    _path_sequence_cost(
                        self.absolute.grid,
                        self.candidates,
                        path,
                        sequence,
                        self.absolute.switching_penalty,
                    ),
                    oracle_map[path],
                    path,
                )
                for path in self.paths
            )
            decision_cost, oracle_cost, worst_path = max(
                path_values,
                key=lambda item: (
                    item[0] - item[1],
                    tuple(-index for index in item[2]),
                ),
            )
            sequence_evaluations.append(
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
        regret_matrix_rows = [tuple(row) for row in row_builders]
        expected_open = tuple(sequence_evaluations)
        if self.open_loop_evaluations != expected_open:
            return False
        selected = min(
            expected_open,
            key=lambda evaluation: (
                evaluation.worst_regret,
                evaluation.code_sequence,
            ),
        )
        if selected != self.selected_open_loop:
            return False
        if self.shared_open_loop_game.cost_matrix != tuple(regret_matrix_rows):
            return False
        if any(value < 0 for row in regret_matrix_rows for value in row):
            return False

        delayed_table = {
            (entry.period, entry.law_history, entry.previous_code): entry
            for entry in self.delayed_entries
        }
        current_table = {
            (entry.period, entry.law_history, entry.previous_code): entry
            for entry in self.current_entries
        }
        if (
            len(delayed_table) != len(self.delayed_entries)
            or len(current_table) != len(self.current_entries)
        ):
            return False

        @lru_cache(maxsize=None)
        def delayed(period: int, history: LawPath, previous_code: int) -> Fraction:
            if period == self.absolute.horizon:
                return -oracle_map[history]
            previous_law = (
                self.absolute.initial_law_index
                if not history
                else history[-1]
            )
            entry = delayed_table.get((period, history, previous_code))
            if entry is None or entry.pattern != "delayed":
                raise KeyError((period, history, previous_code))
            choices: list[tuple[Fraction, int, int]] = []
            for code, candidate in enumerate(self.candidates):
                next_values = tuple(
                    (
                        _stage_cost(self.absolute.grid.laws[next_law], candidate)
                        + delayed(period + 1, history + (next_law,), code),
                        next_law,
                    )
                    for next_law in self.absolute.grid.transitions[previous_law]
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
                            self.absolute.switching_penalty,
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
                or entry.selected_code != code
                or entry.selected_next_law != next_law
            ):
                raise AssertionError("delayed regret Bellman entry mismatch")
            return value

        @lru_cache(maxsize=None)
        def current(period: int, history: LawPath, previous_code: int) -> Fraction:
            if period == self.absolute.horizon:
                return -oracle_map[history]
            previous_law = (
                self.absolute.initial_law_index
                if not history
                else history[-1]
            )
            entry = current_table.get((period, history, previous_code))
            if entry is None or entry.pattern != "current":
                raise KeyError((period, history, previous_code))
            law_choices: list[tuple[Fraction, int, int]] = []
            for next_law in self.absolute.grid.transitions[previous_law]:
                code_choices = tuple(
                    (
                        _switch_cost(
                            previous_code,
                            code,
                            self.absolute.switching_penalty,
                        )
                        + _stage_cost(self.absolute.grid.laws[next_law], candidate)
                        + current(period + 1, history + (next_law,), code),
                        code,
                    )
                    for code, candidate in enumerate(self.candidates)
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
                or entry.selected_code != code
                or entry.selected_next_law != next_law
            ):
                raise AssertionError("current regret Bellman entry mismatch")
            return value

        try:
            delayed_root = delayed(0, tuple(), -1)
            current_root = current(0, tuple(), -1)
        except (KeyError, AssertionError):
            return False
        if delayed_root != self.delayed_value or current_root != self.current_value:
            return False

        def replay_witness(
            table: dict[tuple[int, LawPath, int], RegretBellmanEntry],
        ) -> tuple[LawPath, CodeSequence]:
            history: LawPath = tuple()
            codes: list[int] = []
            previous_code = -1
            for period in range(self.absolute.horizon):
                entry = table[(period, history, previous_code)]
                codes.append(entry.selected_code)
                history = history + (entry.selected_next_law,)
                previous_code = entry.selected_code
            return history, tuple(codes)

        if replay_witness(delayed_table) != (
            self.delayed_witness_path,
            self.delayed_witness_codes,
        ):
            return False
        if replay_witness(current_table) != (
            self.current_witness_path,
            self.current_witness_codes,
        ):
            return False

        if self.absolute.switching_penalty == 0 and self.current_value != 0:
            return False
        if len(self.paths) == 1 and any(
            value != 0
            for value in (
                self.open_loop_value,
                self.shared_open_loop_value,
                self.delayed_value,
                self.current_value,
            )
        ):
            return False
        return True


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
    """Solve exact finite-grid regret for four information patterns."""

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
    shared_game = solve_exact_zero_sum_game(
        tuple(tuple(row) for row in row_builders),
        max_bases=max_game_bases,
    )

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
