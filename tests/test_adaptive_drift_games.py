from fractions import Fraction
from itertools import combinations

import pytest

from simtheory.adaptive_drift_games import (
    exact_feedback_dynamic_code,
    exact_observation_value,
    exact_open_loop_dynamic_code,
    finite_law_transition_model,
    transition_relation_is_subset,
    tv_law_transition_model,
)
from simtheory.confusion_graphs import ConfusionGraph


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_masses(count: int):
    return tuple(
        tuple(Fraction(1) if row == column else Fraction(0) for column in range(count))
        for row in range(count)
    )


def test_tv_transition_model_distinguishes_static_and_fully_mobile_laws():
    laws = _point_masses(3)
    static = tv_law_transition_model(laws, 0)
    mobile = tv_law_transition_model(laws, 1)

    assert static.valid and mobile.valid
    assert static.successors == ((0,), (1,), (2,))
    assert mobile.successors == ((0, 1, 2),) * 3
    assert transition_relation_is_subset(static, mobile)
    assert not transition_relation_is_subset(mobile, static)


def test_full_observation_strictly_improves_over_open_loop_for_mobile_k3():
    graph = _complete_graph(3)
    model = tv_law_transition_model(_point_masses(3), 1)
    certificate = exact_observation_value(graph, model, 0, 2)

    assert certificate.valid
    assert certificate.open_loop.selected_value == 3
    assert certificate.feedback.initial_value == 2
    assert certificate.feedback_gain == 1
    assert certificate.open_loop.worst_path[0] == 0
    assert certificate.open_loop.worst_path[1] != next(
        state
        for state, length in enumerate(
            certificate.open_loop.selected_candidates[1].scenario_costs
        )
        if length == 1
    )


def test_feedback_switching_cost_has_exact_unit_threshold():
    graph = _complete_graph(3)
    model = tv_law_transition_model(_point_masses(3), 1)

    below = exact_observation_value(
        graph,
        model,
        0,
        2,
        switching_penalty=Fraction(1, 2),
    )
    boundary = exact_observation_value(
        graph,
        model,
        0,
        2,
        switching_penalty=1,
    )

    assert below.valid and boundary.valid
    assert below.open_loop.selected_value == 3
    assert below.feedback.initial_value == Fraction(5, 2)
    assert below.feedback_gain == Fraction(1, 2)
    assert below.feedback.adversarial_path == (0, 1)
    assert below.feedback.selected_codes[0] != below.feedback.selected_codes[1]

    assert boundary.open_loop.selected_value == 3
    assert boundary.feedback.initial_value == 3
    assert boundary.feedback_gain == 0
    assert boundary.feedback.selected_codes[0] == boundary.feedback.selected_codes[1]


def test_no_source_mobility_erases_the_value_of_feedback():
    graph = _complete_graph(3)
    model = tv_law_transition_model(_point_masses(3), 0)
    certificate = exact_observation_value(graph, model, 0, 4)

    assert certificate.valid
    assert certificate.open_loop.selected_value == 4
    assert certificate.feedback.initial_value == 4
    assert certificate.feedback_gain == 0
    assert certificate.open_loop.worst_path == (0, 0, 0, 0)
    assert certificate.feedback.adversarial_path == (0, 0, 0, 0)


def test_enlarging_transition_relation_cannot_help_the_minimizing_coder():
    graph = _complete_graph(3)
    laws = _point_masses(3)
    static = tv_law_transition_model(laws, 0)
    mobile = tv_law_transition_model(laws, 1)

    static_feedback = exact_feedback_dynamic_code(graph, static, 0, 2)
    mobile_feedback = exact_feedback_dynamic_code(graph, mobile, 0, 2)
    static_open = exact_open_loop_dynamic_code(graph, static, 0, 2)
    mobile_open = exact_open_loop_dynamic_code(graph, mobile, 0, 2)

    assert static_feedback.initial_value <= mobile_feedback.initial_value
    assert static_open.selected_value <= mobile_open.selected_value


def test_explicit_directed_transition_relation_is_supported():
    laws = _point_masses(3)
    model = finite_law_transition_model(
        laws,
        (
            (0, 1),
            (1, 2),
            (2,),
        ),
    )
    certificate = exact_observation_value(_complete_graph(3), model, 0, 3)
    assert model.valid
    assert certificate.valid
    assert all(
        right in model.successors[left]
        for left, right in zip(
            certificate.feedback.adversarial_path,
            certificate.feedback.adversarial_path[1:],
        )
    )


def test_dynamic_game_validation_and_caps_are_explicit():
    graph = _complete_graph(3)
    model = tv_law_transition_model(_point_masses(3), 1)

    with pytest.raises(ValueError):
        exact_observation_value(graph, model, 3, 2)
    with pytest.raises(ValueError):
        exact_observation_value(graph, model, 0, 0)
    with pytest.raises(ValueError):
        exact_observation_value(
            graph,
            model,
            0,
            3,
            max_sequences=1,
        )
    with pytest.raises(ValueError):
        finite_law_transition_model(_point_masses(2), ((), (1,)))
