from fractions import Fraction
from itertools import combinations

from simtheory.active_fixed_model_experiments import (
    active_experiment,
    exact_active_fixed_model_experiment_design,
)
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.fixed_model_ambiguity import fixed_model_family, fixed_model_scenario
from simtheory.observation_channel_value import (
    RationalObservationChannel,
    garble_observation_channel,
)
from simtheory.stochastic_observation_beliefs import (
    bayesian_law_model,
    observation_kernel,
)


def _graph():
    vertices = (0, 1, 2)
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _family():
    scenarios = []
    for model_index in range(3):
        source = tuple(Fraction(1) if symbol == model_index else Fraction(0) for symbol in range(3))
        model = bayesian_law_model((source,), ((1,),))
        scenarios.append(
            fixed_model_scenario(
                f"m{model_index}", model, observation_kernel(((1,),)), (1,)
            )
        )
    return fixed_model_family(tuple(scenarios))


def test_blackwell_equivalent_constant_and_public_coin_signals_have_different_deterministic_minimax_values():
    graph = _graph()
    family = _family()

    constant_channel = RationalObservationChannel.from_values(((1,), (1,), (1,)))
    coin_channel = RationalObservationChannel.from_values(
        ((Fraction(1, 3),) * 3,) * 3
    )

    assert garble_observation_channel(
        constant_channel,
        ((Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),),
    ) == coin_channel
    assert garble_observation_channel(
        coin_channel,
        ((1,), (1,), (1,)),
    ) == constant_channel

    constant_experiment = active_experiment(
        "constant",
        tuple(observation_kernel(((1,),)) for _ in family.scenarios),
    )
    coin_experiment = active_experiment(
        "coin",
        tuple(
            observation_kernel(((Fraction(1, 3),) * 3,))
            for _ in family.scenarios
        ),
    )

    constant_value = exact_active_fixed_model_experiment_design(
        graph, family, (constant_experiment,), 1
    )
    coin_value = exact_active_fixed_model_experiment_design(
        graph, family, (coin_experiment,), 1
    )

    assert constant_value.robust_value == 2
    assert coin_value.robust_value == Fraction(5, 3)
    assert coin_value.robust_value < constant_value.robust_value
