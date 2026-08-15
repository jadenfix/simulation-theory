from fractions import Fraction
from itertools import combinations

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.fixed_model_ambiguity import (
    exact_fixed_model_ambiguity_game,
    fixed_model_family,
    fixed_model_scenario,
    initial_model_observation_branches,
)
from simtheory.stochastic_observation_beliefs import (
    bayesian_law_model,
    no_information_kernel,
    observation_kernel,
)


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_mass_source(symbol: int, count: int):
    return tuple(
        Fraction(1) if index == symbol else Fraction(0)
        for index in range(count)
    )


def _one_state_model(source_law):
    return bayesian_law_model((source_law,), ((1,),))


def test_fixed_model_consistency_beats_rectangular_model_reselection():
    graph = _complete_graph(3)
    scenarios = tuple(
        fixed_model_scenario(
            f"model-{state}",
            _one_state_model(_point_mass_source(state, 3)),
            no_information_kernel(1),
            (1,),
        )
        for state in range(3)
    )
    family = fixed_model_family(scenarios)
    certificate = exact_fixed_model_ambiguity_game(graph, family, 3)
    assert certificate.valid
    assert certificate.fixed_model_value == 5
    assert certificate.rectangular_value == 6
    assert certificate.model_consistency_gap == 1
    assert sorted(certificate.selected_initial_costs) == [5, 5, 5]


def test_informative_signal_has_strict_robust_value_between_none_and_full():
    graph = _complete_graph(3)
    model_a = _one_state_model(_point_mass_source(0, 3))
    model_b = _one_state_model(_point_mass_source(1, 3))
    no_signal = fixed_model_family(
        (
            fixed_model_scenario("A", model_a, no_information_kernel(1), (1,)),
            fixed_model_scenario("B", model_b, no_information_kernel(1), (1,)),
        )
    )
    noisy_signal = fixed_model_family(
        (
            fixed_model_scenario(
                "A",
                model_a,
                observation_kernel(((Fraction(3, 4), Fraction(1, 4)),)),
                (1,),
            ),
            fixed_model_scenario(
                "B",
                model_b,
                observation_kernel(((Fraction(1, 4), Fraction(3, 4)),)),
                (1,),
            ),
        )
    )
    full_signal = fixed_model_family(
        (
            fixed_model_scenario(
                "A", model_a, observation_kernel(((1, 0),)), (1,)
            ),
            fixed_model_scenario(
                "B", model_b, observation_kernel(((0, 1),)), (1,)
            ),
        )
    )
    none = exact_fixed_model_ambiguity_game(graph, no_signal, 1)
    noisy = exact_fixed_model_ambiguity_game(graph, noisy_signal, 1)
    full = exact_fixed_model_ambiguity_game(graph, full_signal, 1)
    assert none.valid and noisy.valid and full.valid
    assert none.fixed_model_value == 2
    assert noisy.fixed_model_value == Fraction(5, 4)
    assert full.fixed_model_value == 1
    assert none.fixed_model_value > noisy.fixed_model_value > full.fixed_model_value

    # Fixed-model ambiguity commits to one model before the noisy signal.  The
    # rectangular relaxation can reselect an active model after each signal;
    # because both models assign positive probability to both signals, it can
    # always retain the model whose source symbol received length two.
    assert none.rectangular_value == 2
    assert noisy.rectangular_value == 2
    assert noisy.model_consistency_gap == Fraction(3, 4)
    assert full.rectangular_value == 1


def test_zero_probability_observation_eliminates_incompatible_models():
    model_a = _one_state_model(_point_mass_source(0, 3))
    model_b = _one_state_model(_point_mass_source(1, 3))
    family = fixed_model_family(
        (
            fixed_model_scenario(
                "A", model_a, observation_kernel(((1, 0),)), (1,)
            ),
            fixed_model_scenario(
                "B", model_b, observation_kernel(((0, 1),)), (1,)
            ),
        )
    )
    branches = initial_model_observation_branches(family)
    assert tuple(branch.observation for branch in branches) == (0, 1)
    assert branches[0].next_state.model_indices == (0,)
    assert branches[1].next_state.model_indices == (1,)
    assert branches[0].probabilities == (1, 0)
    assert branches[1].probabilities == (0, 1)


def test_identical_models_have_zero_model_consistency_gap():
    graph = _complete_graph(3)
    model = _one_state_model(_point_mass_source(0, 3))
    family = fixed_model_family(
        (
            fixed_model_scenario(
                "copy-1", model, no_information_kernel(1), (1,)
            ),
            fixed_model_scenario(
                "copy-2", model, no_information_kernel(1), (1,)
            ),
        )
    )
    result = exact_fixed_model_ambiguity_game(graph, family, 3)
    assert result.valid
    assert result.fixed_model_value == 3
    assert result.rectangular_value == 3
    assert result.model_consistency_gap == 0


def test_model_family_validation_and_frontier_caps_are_explicit():
    graph = _complete_graph(3)
    model = _one_state_model(_point_mass_source(0, 3))
    with pytest.raises(ValueError):
        fixed_model_family(
            (
                fixed_model_scenario(
                    "same", model, no_information_kernel(1), (1,)
                ),
                fixed_model_scenario(
                    "same", model, no_information_kernel(1), (1,)
                ),
            )
        )

    # Three distinct point-mass models induce the terminal cost vectors
    # (1,2,2), (2,1,2), and (2,2,1).  None dominates another, so a one-entry
    # frontier cap must fail closed.
    cap_family = fixed_model_family(
        tuple(
            fixed_model_scenario(
                f"model-{state}",
                _one_state_model(_point_mass_source(state, 3)),
                no_information_kernel(1),
                (1,),
            )
            for state in range(3)
        )
    )
    with pytest.raises(ValueError):
        exact_fixed_model_ambiguity_game(
            graph,
            cap_family,
            1,
            max_frontier_entries=1,
        )
