from fractions import Fraction
from itertools import combinations

from simtheory.active_experiment_regret_decomposition import (
    erase_experiment_information,
    exact_active_experiment_regret_decomposition,
)
from simtheory.active_fixed_model_experiments import active_experiment
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.fixed_model_ambiguity import fixed_model_family, fixed_model_scenario
from simtheory.stochastic_observation_beliefs import bayesian_law_model, observation_kernel


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_mass(symbol: int, count: int):
    return tuple(Fraction(1) if index == symbol else Fraction(0) for index in range(count))


def _point_model_family(count: int):
    scenarios = []
    for model_index in range(count):
        model = bayesian_law_model((_point_mass(model_index, count),), ((1,),))
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
    return active_experiment(
        "reveal",
        tuple(
            observation_kernel(
                (
                    tuple(
                        Fraction(1) if obs == model_index else Fraction(0)
                        for obs in range(count)
                    ),
                )
            )
            for model_index in range(count)
        ),
        cost,
    )


def _noisy_model_signal(family):
    # Three one-state models. Under model m, signal m has probability 1/2 and
    # each other signal probability 1/4. The channel carries model information
    # and also supplies public randomness.
    count = family.model_count
    kernels = []
    for model_index in range(count):
        row = tuple(
            Fraction(1, 2) if obs == model_index else Fraction(1, 4)
            for obs in range(count)
        )
        kernels.append(observation_kernel((row,)))
    return active_experiment("noisy", tuple(kernels))


def test_perfect_revelation_splits_total_regret_gain_into_coordination_and_information():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_experiment_regret_decomposition(
        graph, family, (_revealing(family),), 1
    )
    assert result.valid
    assert result.actual.oracle_values == (1, 1, 1)
    assert result.erased_deterministic_gap == 1
    assert result.erased_mixed.mixed_value == Fraction(2, 3)
    assert result.actual_mixed.mixed_value == 0
    assert result.actual_deterministic_regret == 0
    assert result.coordination_gain_erased == Fraction(1, 3)
    assert result.information_gain_mixed == Fraction(2, 3)
    assert result.residual_randomization_gap_actual == 0
    assert result.total_deterministic_gain == 1
    assert result.identity_residual == 0
    assert result.erased_mixed.game.gap == 0
    assert result.actual_mixed.game.gap == 0


def test_source_independent_public_coin_has_coordination_value_but_zero_information_value():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_experiment_regret_decomposition(
        graph, family, (_public_coin(family),), 1
    )
    assert result.valid
    assert result.erased_deterministic_gap == 1
    assert result.erased_mixed.mixed_value == Fraction(2, 3)
    assert result.actual_deterministic_regret == Fraction(2, 3)
    assert result.actual_mixed.mixed_value == Fraction(2, 3)
    assert result.coordination_gain_erased == Fraction(1, 3)
    assert result.information_gain_mixed == 0
    assert result.residual_randomization_gap_actual == 0
    assert result.total_deterministic_gain == Fraction(1, 3)


def test_no_signal_has_no_total_gain_and_randomization_terms_cancel_exactly():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_experiment_regret_decomposition(
        graph, family, (_no_signal(family),), 1
    )
    assert result.valid
    assert result.erased_deterministic_gap == result.actual_deterministic_regret == 1
    assert result.erased_mixed.mixed_value == result.actual_mixed.mixed_value == Fraction(2, 3)
    assert result.coordination_gain_erased == Fraction(1, 3)
    assert result.information_gain_mixed == 0
    assert result.residual_randomization_gap_actual == Fraction(1, 3)
    assert result.total_deterministic_gain == 0
    assert result.identity_residual == 0


def test_noisy_signal_has_strict_information_value_after_public_randomness_is_matched():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_experiment_regret_decomposition(
        graph, family, (_noisy_model_signal(family),), 1
    )
    assert result.valid
    assert result.information_gain_mixed > 0
    assert result.actual_mixed.mixed_value < result.erased_mixed.mixed_value
    assert result.total_deterministic_gain >= 0
    assert result.identity_residual == 0


def test_information_erasure_preserves_experiment_name_cost_and_hidden_dimensions():
    family = _point_model_family(3)
    experiment = _revealing(family, Fraction(5, 7))
    erased = erase_experiment_information(experiment)
    assert erased.name == experiment.name
    assert erased.acquisition_cost == experiment.acquisition_cost
    assert erased.observation_count == 1
    assert tuple(kernel.hidden_state_count for kernel in erased.kernels) == tuple(
        kernel.hidden_state_count for kernel in experiment.kernels
    )
    assert all(kernel.probabilities == ((1,),) for kernel in erased.kernels)
