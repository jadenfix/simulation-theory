from fractions import Fraction

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.feedback_regret import exact_drift_information_regret


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


def test_zero_switch_current_information_matches_the_path_oracle():
    certificate = exact_drift_information_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        Fraction(1, 6),
        2,
        switching_penalty=0,
    )
    assert certificate.valid
    assert certificate.clairvoyant_value == 0
    assert certificate.current_value == 0
    assert 0 <= certificate.delayed_value <= certificate.open_loop_value
    assert certificate.shared_open_loop_value <= certificate.open_loop_value
    assert certificate.randomization_gain_over_open_loop >= 0


def test_positive_switching_cost_makes_current_information_imperfect():
    certificate = exact_drift_information_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.clairvoyant_value == 0
    assert certificate.current_value > 0
    assert certificate.current_value <= certificate.delayed_value
    assert certificate.delayed_value <= certificate.open_loop_value
    assert certificate.shared_open_loop_value <= certificate.open_loop_value


def test_zero_drift_collapses_every_regret_pattern_to_zero():
    certificate = exact_drift_information_regret(
        _complete_graph(3),
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        10,
        0,
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.deterministic_hierarchy == (0, 0, 0, 0)
    assert certificate.shared_open_loop_value == 0
    assert len(certificate.paths) == 1


def test_regret_certificate_keeps_absolute_and_regret_values_distinct():
    certificate = exact_drift_information_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    absolute = certificate.absolute
    # The two hierarchies answer different questions and need not have equal
    # adjacent gaps or equal selected open-loop sequences.
    assert absolute.open_loop_value >= certificate.open_loop_value
    assert absolute.current_value >= certificate.current_value
    assert all(value >= 0 for value in certificate.path_oracle_costs)
    assert all(
        evaluation.decision_cost_on_witness
        - evaluation.oracle_cost_on_witness
        == evaluation.worst_regret
        for evaluation in certificate.open_loop_evaluations
    )


def test_invalid_inputs_are_rejected_by_the_underlying_exact_model():
    with pytest.raises(ValueError):
        exact_drift_information_regret(
            _complete_graph(3),
            (Fraction(1, 3),) * 3,
            6,
            Fraction(1, 6),
            0,
        )
