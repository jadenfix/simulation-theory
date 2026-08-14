from fractions import Fraction
from itertools import product

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.pathwise_regret import (
    affine_path_decision,
    bounded_code_sequences,
    exact_code_sequence_regret,
    exact_pathwise_regret_game,
    sequence_switch_count,
)


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in vertices
            for right in vertices
            if left < right
        ),
    )


def _binary_prediction_decisions(horizon: int):
    action_costs = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(0)))
    return tuple(
        affine_path_decision(
            "actions[" + ",".join(str(action) for action in sequence) + "]",
            tuple(action_costs[action] for action in sequence),
        )
        for sequence in product((0, 1), repeat=horizon)
    )


def test_full_drift_binary_prediction_has_exact_deterministic_and_shared_values():
    decisions = _binary_prediction_decisions(3)
    certificate = exact_pathwise_regret_game(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1),
        decisions,
    )
    assert certificate.valid
    assert certificate.deterministic_value == 3
    assert certificate.shared_value == Fraction(3, 2)
    assert certificate.randomization_gain == Fraction(3, 2)
    assert certificate.shared_game.gap == 0
    assert all(cost == 0 for cost in certificate.oracle_costs)


def test_zero_drift_reduces_pathwise_regret_to_zero():
    decisions = _binary_prediction_decisions(3)
    certificate = exact_pathwise_regret_game(
        (Fraction(1, 2), Fraction(1, 2)),
        0,
        decisions,
    )
    assert certificate.valid
    assert certificate.deterministic_value == 0
    assert certificate.shared_value == 0
    assert certificate.polytope.paths == (
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(1, 2), Fraction(1, 2)),
        ),
    )


def test_expanding_comparator_class_can_only_raise_each_fixed_decision_regret():
    all_decisions = _binary_prediction_decisions(2)
    static = tuple(
        decision
        for decision in all_decisions
        if decision.period_costs[0] == decision.period_costs[1]
    )
    static_oracle = exact_pathwise_regret_game(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1, 4),
        static,
        static,
    )
    dynamic_oracle = exact_pathwise_regret_game(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1, 4),
        static,
        all_decisions,
    )
    assert static_oracle.valid and dynamic_oracle.valid
    assert dynamic_oracle.polytope.paths == static_oracle.polytope.paths
    assert all(
        dynamic >= baseline
        for dynamic_row, baseline_row in zip(
            dynamic_oracle.regret_matrix,
            static_oracle.regret_matrix,
        )
        for dynamic, baseline in zip(dynamic_row, baseline_row)
    )
    assert dynamic_oracle.deterministic_value >= static_oracle.deterministic_value
    assert dynamic_oracle.shared_value >= static_oracle.shared_value


def test_code_sequence_regret_separates_decision_and_comparator_switch_budgets():
    graph = _complete_graph(3)
    prior = (Fraction(1, 3),) * 3
    static_oracle = exact_code_sequence_regret(
        graph,
        prior,
        Fraction(1, 6),
        2,
        decision_max_switches=0,
        comparator_max_switches=0,
    )
    dynamic_oracle = exact_code_sequence_regret(
        graph,
        prior,
        Fraction(1, 6),
        2,
        decision_max_switches=0,
        comparator_max_switches=1,
    )
    assert static_oracle.valid and dynamic_oracle.valid
    assert len(static_oracle.decision_sequences) == 3
    assert len(static_oracle.comparator_sequences) == 3
    assert len(dynamic_oracle.decision_sequences) == 3
    assert len(dynamic_oracle.comparator_sequences) == 9
    assert dynamic_oracle.deterministic_regret >= static_oracle.deterministic_regret
    assert dynamic_oracle.shared_regret >= static_oracle.shared_regret
    assert dynamic_oracle.shared_regret <= dynamic_oracle.deterministic_regret


def test_zero_drift_code_sequence_regret_is_zero():
    certificate = exact_code_sequence_regret(
        _complete_graph(3),
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        0,
        2,
        decision_max_switches=0,
        comparator_max_switches=0,
    )
    assert certificate.valid
    assert certificate.deterministic_regret == 0
    assert certificate.shared_regret == 0


def test_bounded_sequence_enumeration_and_switch_count_are_exact():
    sequences = bounded_code_sequences(3, 3, 1)
    assert len(sequences) == 15
    assert all(sequence_switch_count(sequence) <= 1 for sequence in sequences)
    assert (0, 1, 0) not in sequences
    assert (0, 0, 1) in sequences


def test_regret_rejects_missing_comparator_and_invalid_budgets():
    decisions = _binary_prediction_decisions(2)
    with pytest.raises(ValueError):
        exact_pathwise_regret_game(
            (Fraction(1, 2), Fraction(1, 2)),
            Fraction(1, 4),
            decisions,
            decisions[:1],
        )
    with pytest.raises(ValueError):
        exact_code_sequence_regret(
            _complete_graph(3),
            (Fraction(1, 3),) * 3,
            Fraction(1, 6),
            2,
            decision_max_switches=1,
            comparator_max_switches=0,
        )
