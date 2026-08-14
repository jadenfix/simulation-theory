from fractions import Fraction

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.coupled_drift_sequences import exact_precommitted_code_sequence
from simtheory.adaptive_drift_policies import (
    exact_drift_information_patterns,
    exact_simplex_grid,
)


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in range(count)
            for right in range(left + 1, count)
        ),
    )


def test_three_state_denominator_six_grid_is_exact_and_symmetric():
    grid = exact_simplex_grid(3, 6, Fraction(1, 6))
    assert grid.valid
    assert grid.law_count == 28
    assert grid.candidate_law_pairs == 28**2
    for left, neighbors in enumerate(grid.transitions):
        assert left in neighbors
        for right in neighbors:
            assert left in grid.transitions[right]


def test_k3_information_patterns_are_strict_with_switching_cost():
    certificate = exact_drift_information_patterns(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.clairvoyant_value == Fraction(10, 3)
    assert certificate.current_value == Fraction(41, 12)
    assert certificate.delayed_value == Fraction(15, 4)
    assert certificate.open_loop_value == Fraction(23, 6)
    assert (
        certificate.clairvoyant_value
        < certificate.current_value
        < certificate.delayed_value
        < certificate.open_loop_value
    )


def test_zero_switching_cost_collapses_current_feedback_to_clairvoyance():
    certificate = exact_drift_information_patterns(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        Fraction(1, 6),
        2,
    )
    assert certificate.valid
    assert certificate.clairvoyant_value == Fraction(10, 3)
    assert certificate.current_value == Fraction(10, 3)
    assert certificate.delayed_value == Fraction(7, 2)
    assert certificate.open_loop_value == Fraction(11, 3)
    assert certificate.current_value == certificate.clairvoyant_value


def test_zero_drift_makes_all_information_patterns_equal():
    certificate = exact_drift_information_patterns(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        0,
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.hierarchy == (Fraction(10, 3),) * 4


def test_grid_open_loop_matches_continuous_k3_example():
    graph = _complete_graph(3)
    prior = (Fraction(1, 3),) * 3
    grid = exact_drift_information_patterns(
        graph,
        prior,
        6,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 4),
    )
    continuous = exact_precommitted_code_sequence(
        graph,
        prior,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert grid.valid and continuous.valid
    assert grid.open_loop_value <= continuous.robust_value
    assert grid.open_loop_value == continuous.robust_value == Fraction(23, 6)


def test_witnesses_are_reachable_and_have_declared_horizon():
    certificate = exact_drift_information_patterns(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        6,
        Fraction(1, 6),
        3,
        switching_penalty=Fraction(1, 10),
    )
    assert certificate.valid
    assert len(certificate.delayed_witness_path) == 3
    assert len(certificate.current_witness_path) == 3
    assert len(certificate.selected_open_loop.worst_path) == 3
    assert len(certificate.selected_clairvoyant.law_path) == 3


def test_grid_path_and_sequence_caps_fail_loudly():
    graph = _complete_graph(3)
    prior = (Fraction(1, 3),) * 3
    with pytest.raises(ValueError):
        exact_simplex_grid(3, 6, Fraction(1, 6), max_law_pairs=10)
    with pytest.raises(ValueError):
        exact_drift_information_patterns(
            graph,
            prior,
            6,
            Fraction(1, 6),
            2,
            max_paths=1,
        )
    with pytest.raises(ValueError):
        exact_drift_information_patterns(
            graph,
            prior,
            6,
            Fraction(1, 6),
            2,
            max_sequences=1,
        )


def test_initial_prior_must_lie_on_declared_grid():
    with pytest.raises(ValueError):
        exact_drift_information_patterns(
            _complete_graph(3),
            (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
            5,
            Fraction(1, 5),
            2,
        )
