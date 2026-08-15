from fractions import Fraction
from itertools import combinations

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.stochastic_observation_beliefs import (
    bayesian_law_model,
    deterministic_partition_kernel,
    exact_bayesian_coding_game,
    exact_blackwell_observation_value,
    full_information_kernel,
    garble_observation_kernel,
    initial_observation_branches,
    next_observation_branches,
    no_information_kernel,
    observation_kernel,
)


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_masses(count: int):
    return tuple(
        tuple(Fraction(1) if row == column else Fraction(0) for column in range(count))
        for row in range(count)
    )


def _identity_transition(count: int):
    return _point_masses(count)


def test_exact_bayes_update_and_markov_prediction_are_rational():
    model = bayesian_law_model(
        _point_masses(2),
        (
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
        ),
    )
    kernel = observation_kernel(
        (
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
        )
    )
    initial = initial_observation_branches((Fraction(1, 2), Fraction(1, 2)), kernel)
    assert tuple(branch.probability for branch in initial) == (Fraction(1, 2), Fraction(1, 2))
    assert initial[0].posterior == (Fraction(3, 4), Fraction(1, 4))
    assert initial[1].posterior == (Fraction(1, 4), Fraction(3, 4))
    next_branches = next_observation_branches(initial[0].posterior, model, kernel)
    assert sum((branch.probability for branch in next_branches), Fraction(0)) == 1
    assert all(branch.valid for branch in next_branches)


def test_k3_no_partial_and_full_observation_have_strict_expected_cost_chain():
    graph = _complete_graph(3)
    model = bayesian_law_model(_point_masses(3), _identity_transition(3))
    prior = (Fraction(1, 3),) * 3
    none = exact_bayesian_coding_game(graph, model, no_information_kernel(3), prior, 2)
    partial = exact_bayesian_coding_game(graph, model, deterministic_partition_kernel((0, 1, 1)), prior, 2)
    full = exact_bayesian_coding_game(graph, model, full_information_kernel(3), prior, 2)
    assert none.valid and partial.valid and full.valid
    assert none.initial_value == Fraction(10, 3)
    assert partial.initial_value == Fraction(8, 3)
    assert full.initial_value == 2
    assert none.initial_value > partial.initial_value > full.initial_value


def test_stochastic_garbling_has_exact_intermediate_information_value():
    graph = _complete_graph(3)
    model = bayesian_law_model(_point_masses(3), _identity_transition(3))
    prior = (Fraction(1, 3),) * 3
    full = full_information_kernel(3)
    reveal_or_unknown = garble_observation_kernel(full, ((Fraction(1, 2), 0, 0, Fraction(1, 2)), (0, Fraction(1, 2), 0, Fraction(1, 2)), (0, 0, Fraction(1, 2), Fraction(1, 2))))
    noisy_comparison = exact_blackwell_observation_value(graph, model, prior, 1, reveal_or_unknown)
    erase_everything = garble_observation_kernel(reveal_or_unknown.coarser, ((1,), (1,), (1,), (1,)))
    no_information_comparison = exact_blackwell_observation_value(graph, model, prior, 1, erase_everything)
    assert noisy_comparison.valid and no_information_comparison.valid
    assert noisy_comparison.finer_game.initial_value == 1
    assert noisy_comparison.coarser_game.initial_value == Fraction(4, 3)
    assert noisy_comparison.information_gain == Fraction(1, 3)
    assert no_information_comparison.finer_game.initial_value == Fraction(4, 3)
    assert no_information_comparison.coarser_game.initial_value == Fraction(5, 3)
    assert no_information_comparison.information_gain == Fraction(1, 3)


def test_switching_penalty_is_part_of_the_belief_state_control_problem():
    graph = _complete_graph(3)
    model = bayesian_law_model(_point_masses(3), _identity_transition(3))
    prior = (Fraction(1, 3),) * 3
    result = exact_bayesian_coding_game(graph, model, full_information_kernel(3), prior, 3, switching_penalty=Fraction(5))
    assert result.valid
    assert result.initial_value == 3


def test_deterministic_partition_is_a_garbling_of_full_information():
    full = full_information_kernel(3)
    partition = garble_observation_kernel(full, ((1, 0), (0, 1), (0, 1)))
    assert partition.valid
    assert partition.coarser == deterministic_partition_kernel((0, 1, 1))


def test_validation_and_reachable_belief_caps_are_explicit():
    graph = _complete_graph(3)
    model = bayesian_law_model(_point_masses(3), _identity_transition(3))
    prior = (Fraction(1, 3),) * 3
    with pytest.raises(ValueError):
        observation_kernel(((Fraction(1, 2), Fraction(1, 2)),))
    with pytest.raises(ValueError):
        bayesian_law_model(_point_masses(2), ((1, 0),))
    with pytest.raises(ValueError):
        exact_bayesian_coding_game(graph, model, full_information_kernel(3), prior, 0)
    with pytest.raises(ValueError):
        exact_bayesian_coding_game(graph, model, full_information_kernel(3), prior, 3, max_belief_nodes=1)
