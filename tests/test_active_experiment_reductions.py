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
    exact_observation_channel_value,
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


def _family(count: int):
    scenarios = []
    for model_index in range(count):
        model = bayesian_law_model((_point_mass(model_index, count),), ((1,),))
        scenarios.append(
            fixed_model_scenario(
                f"m{model_index}", model, observation_kernel(((1,),)), (1,)
            )
        )
    return fixed_model_family(tuple(scenarios))


def _active_from_channel(name, channel, family):
    kernels = tuple(
        observation_kernel((channel.matrix[model_index],))
        for model_index in range(family.model_count)
    )
    return active_experiment(name, kernels)


def test_one_period_one_state_fixed_models_reduce_to_existing_observation_channel_game():
    graph = _complete_graph(3)
    family = _family(3)
    scenarios = tuple(_point_mass(index, 3) for index in range(3))

    channels = (
        RationalObservationChannel.from_values(
            ((Fraction(1, 3),) * 3,) * 3
        ),
        RationalObservationChannel.from_values(
            (
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1),
            )
        ),
        RationalObservationChannel.from_values(
            (
                (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
                (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
                (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
            )
        ),
    )

    for index, channel in enumerate(channels):
        old = exact_observation_channel_value(graph, scenarios, channel)
        new = exact_active_fixed_model_experiment_design(
            graph,
            family,
            (_active_from_channel(f"e{index}", channel, family),),
            1,
        )
        assert old.valid and new.valid
        assert new.robust_value == old.deterministic_observation_value
