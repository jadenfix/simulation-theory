from fractions import Fraction
from itertools import combinations

import pytest

from simtheory.active_fixed_model_experiments import (
    active_experiment,
    exact_active_fixed_model_experiment_design,
    experiment_is_source_independent,
)
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.fixed_model_ambiguity import (
    fixed_model_family,
    fixed_model_scenario,
)
from simtheory.stochastic_observation_beliefs import (
    bayesian_law_model,
    observation_kernel,
)


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_mass(symbol: int, count: int):
    return tuple(Fraction(1) if index == symbol else Fraction(0) for index in range(count))


def _point_model_family(count: int):
    scenarios = []
    for model_index in range(count):
        model = bayesian_law_model(
            (_point_mass(model_index, count),),
            ((1,),),
        )
        scenarios.append(
            fixed_model_scenario(
                f"m{model_index}",
                model,
                observation_kernel(((1,),)),
                (1,),
            )
        )
    return fixed_model_family(tuple(scenarios))


def _no_signal(family):
    return active_experiment(
        "none",
        tuple(observation_kernel(((1,),)) for _ in family.scenarios),
    )


def _public_coin(family):
    row = (Fraction(1, 3),) * 3
    return active_experiment(
        "public-coin",
        tuple(observation_kernel((row,)) for _ in family.scenarios),
    )


def _revealing(family, cost=0):
    count = family.model_count
    kernels = tuple(
        observation_kernel(
            (
                tuple(
                    Fraction(1) if obs == model_index else Fraction(0)
                    for obs in range(count)
                ),
            )
        )
        for model_index in range(count)
    )
    return active_experiment("reveal", kernels, cost)


def test_uninformative_public_signal_can_strictly_improve_deterministic_minimax_value():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    none = _no_signal(family)
    coin = _public_coin(family)
    reveal = _revealing(family)

    no_result = exact_active_fixed_model_experiment_design(graph, family, (none,), 1)
    coin_result = exact_active_fixed_model_experiment_design(graph, family, (coin,), 1)
    reveal_result = exact_active_fixed_model_experiment_design(graph, family, (reveal,), 1)

    assert no_result.valid and coin_result.valid and reveal_result.valid
    assert no_result.robust_value == 2
    assert coin_result.robust_value == Fraction(5, 3)
    assert reveal_result.robust_value == 1
    assert experiment_is_source_independent(coin)
    assert not experiment_is_source_independent(reveal)

    # Total improvement 1 decomposes into 1/3 public-randomness value and
    # 2/3 additional model-information value in this exact symmetric example.
    assert no_result.robust_value - coin_result.robust_value == Fraction(1, 3)
    assert coin_result.robust_value - reveal_result.robust_value == Fraction(2, 3)


def test_sensing_cost_threshold_must_be_measured_against_randomness_matched_baseline():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    coin = _public_coin(family)

    below = exact_active_fixed_model_experiment_design(
        graph,
        family,
        (coin, _revealing(family, Fraction(1, 2))),
        1,
    )
    at = exact_active_fixed_model_experiment_design(
        graph,
        family,
        (coin, _revealing(family, Fraction(2, 3))),
        1,
    )
    above = exact_active_fixed_model_experiment_design(
        graph,
        family,
        (coin, _revealing(family, Fraction(3, 4))),
        1,
    )

    assert below.robust_value == Fraction(3, 2)
    assert below.experiments[below.selected_experiment].name == "reveal"
    assert at.robust_value == Fraction(5, 3)
    assert at.experiments[at.selected_experiment].name == "public-coin"
    assert above.robust_value == Fraction(5, 3)
    assert above.experiments[above.selected_experiment].name == "public-coin"


def test_persistent_model_identity_makes_early_revelation_have_multi_period_option_value():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    none = _no_signal(family)
    costly_reveal = _revealing(family, Fraction(3, 2))

    static = exact_active_fixed_model_experiment_design(graph, family, (none,), 3)
    adaptive = exact_active_fixed_model_experiment_design(
        graph,
        family,
        (none, costly_reveal),
        3,
    )

    # With no observations, three deterministic K3 codes can rotate the short
    # leaf, giving every fixed model cumulative length 5.
    assert static.robust_value == 5

    # Paying 3/2 once to identify the globally fixed model lets the two later
    # periods use no-cost/no-signal observations while retaining that public
    # model knowledge: 1 + 1 + 1 + 3/2 = 9/2.
    assert adaptive.robust_value == Fraction(9, 2)
    assert adaptive.experiments[adaptive.selected_experiment].name == "reveal"
    assert adaptive.robust_value < static.robust_value


def test_adding_experiments_cannot_worsen_the_bounded_minimax_design():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    none = _no_signal(family)
    coin = _public_coin(family)
    reveal = _revealing(family, Fraction(1, 2))

    one = exact_active_fixed_model_experiment_design(graph, family, (none,), 1)
    two = exact_active_fixed_model_experiment_design(graph, family, (none, coin), 1)
    three = exact_active_fixed_model_experiment_design(graph, family, (none, coin, reveal), 1)
    assert one.robust_value >= two.robust_value >= three.robust_value


def test_validation_and_search_caps_are_explicit():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    none = _no_signal(family)

    with pytest.raises(ValueError):
        active_experiment("bad", (), 0)
    with pytest.raises(ValueError):
        exact_active_fixed_model_experiment_design(graph, family, (), 1)
    with pytest.raises(ValueError):
        exact_active_fixed_model_experiment_design(graph, family, (none,), 0)
    with pytest.raises(ValueError):
        exact_active_fixed_model_experiment_design(
            graph,
            family,
            (none,),
            3,
            max_combinations=1,
        )
