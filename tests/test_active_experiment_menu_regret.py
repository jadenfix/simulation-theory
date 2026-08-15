from fractions import Fraction
from itertools import combinations

import pytest

from simtheory.active_experiment_menu_regret import exact_active_experiment_menu_regret_shift
from simtheory.active_fixed_model_experiments import active_experiment
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.fixed_model_ambiguity import fixed_model_family, fixed_model_scenario
from simtheory.stochastic_observation_beliefs import bayesian_law_model, observation_kernel


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_mass(symbol: int, count: int):
    return tuple(Fraction(1) if i == symbol else Fraction(0) for i in range(count))


def _disjoint_pair_family():
    # Model 0 emits source 0 or 1 equiprobably; model 1 emits source 2 or 3.
    # Hidden state is static, though horizon-one tests do not use transitions.
    model0 = bayesian_law_model(
        (_point_mass(0, 4), _point_mass(1, 4)),
        ((1, 0), (0, 1)),
    )
    model1 = bayesian_law_model(
        (_point_mass(2, 4), _point_mass(3, 4)),
        ((1, 0), (0, 1)),
    )
    no_signal = observation_kernel(((1,), (1,)))
    return fixed_model_family(
        (
            fixed_model_scenario("left", model0, no_signal, (Fraction(1, 2), Fraction(1, 2))),
            fixed_model_scenario("right", model1, no_signal, (Fraction(1, 2), Fraction(1, 2))),
        )
    )


def _none_two_state(family):
    return active_experiment(
        "none",
        tuple(observation_kernel(((1,), (1,))) for _ in family.scenarios),
    )


def _specialized(family, target: int):
    reveal = observation_kernel(((1, 0), (0, 1)))
    fair = observation_kernel(
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(1, 2), Fraction(1, 2)),
        )
    )
    kernels = tuple(reveal if m == target else fair for m in range(family.model_count))
    return active_experiment(f"special-{target}", kernels)


def _point_model_family(count: int):
    scenarios = []
    for model_index in range(count):
        model = bayesian_law_model((_point_mass(model_index, count),), ((1,),))
        scenarios.append(
            fixed_model_scenario(
                f"m{model_index}", model, observation_kernel(((1,),)), (1,)
            )
        )
    return fixed_model_family(tuple(scenarios))


def _none_one_state(family):
    return active_experiment(
        "none",
        tuple(observation_kernel(((1,),)) for _ in family.scenarios),
    )


def _public_coin(family):
    row = (Fraction(1, 3),) * 3
    return active_experiment(
        "coin",
        tuple(observation_kernel((row,)) for _ in family.scenarios),
    )


def test_richer_k4_menu_leaves_robust_cost_unchanged_but_doubles_own_oracle_regret():
    graph = _complete_graph(4)
    family = _disjoint_pair_family()
    none = _none_two_state(family)
    enriched = (none, _specialized(family, 0), _specialized(family, 1))

    result = exact_active_experiment_menu_regret_shift(
        graph, family, (none,), enriched, 1
    )
    assert result.valid

    # Baseline: balanced K4 code costs 2 under both models. A model-informed
    # oracle knows which disjoint source pair is possible and uses lengths 1,2,
    # so its expected cost is 3/2.
    assert result.baseline.base.robust_value == 2
    assert result.baseline.oracle_values == (Fraction(3, 2), Fraction(3, 2))
    assert result.baseline.minimax_regret == Fraction(1, 2)

    # Each enriched singleton oracle chooses its own specialized experiment and
    # learns the hidden source, reaching cost 1. The shared deterministic
    # controller cannot know which specialized experiment is the relevant one,
    # and its robust cost remains 2.
    assert result.enriched.base.robust_value == 2
    assert result.enriched.oracle_values == (1, 1)
    assert result.enriched.minimax_regret == 1
    assert result.oracle_improvements == (Fraction(1, 2), Fraction(1, 2))
    assert result.deterministic_fixed_benchmark_gain == 0
    assert result.deterministic_own_regret_change == Fraction(1, 2)
    assert result.uniform_oracle_improvement == Fraction(1, 2)
    assert result.deterministic_uniform_identity_residual == 0

    # Public mixing helps the enriched shared controller somewhat, but not as
    # much as the uniform oracle shift; mixed own-regret still rises.
    assert result.mixed_fixed_benchmark_gain == Fraction(1, 4)
    assert result.baseline_mixed_own.mixed_value == Fraction(1, 2)
    assert result.enriched_mixed_own.mixed_value == Fraction(3, 4)
    assert result.mixed_own_regret_change == Fraction(1, 4)
    assert result.mixed_uniform_identity_residual == 0


def test_when_oracle_does_not_improve_menu_expansion_can_only_reduce_own_regret():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    none = _none_one_state(family)
    coin = _public_coin(family)
    result = exact_active_experiment_menu_regret_shift(
        graph, family, (none,), (none, coin), 1
    )
    assert result.valid
    assert result.oracle_improvements == (0, 0, 0)
    assert result.baseline.minimax_regret == 1
    assert result.enriched.minimax_regret == Fraction(2, 3)
    assert result.deterministic_fixed_benchmark_gain == Fraction(1, 3)
    assert result.deterministic_own_regret_change == -Fraction(1, 3)
    assert result.uniform_oracle_improvement == 0
    assert result.deterministic_uniform_identity_residual == 0


def test_nonuniform_oracle_shift_obeys_exact_minmax_bounds():
    graph = _complete_graph(4)
    family = _disjoint_pair_family()
    none = _none_two_state(family)
    result = exact_active_experiment_menu_regret_shift(
        graph,
        family,
        (none,),
        (none, _specialized(family, 0)),
        1,
    )
    assert result.valid
    assert result.oracle_improvements[0] == Fraction(1, 2)
    assert result.oracle_improvements[1] == 0
    assert result.uniform_oracle_improvement is None
    assert result.deterministic_lower_bound <= result.enriched.minimax_regret <= result.deterministic_upper_bound
    assert result.mixed_lower_bound <= result.enriched_mixed_own.mixed_value <= result.mixed_upper_bound


def test_baseline_menu_must_be_a_literal_subset_of_enriched_menu():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    none = _none_one_state(family)
    coin = _public_coin(family)
    with pytest.raises(ValueError):
        exact_active_experiment_menu_regret_shift(graph, family, (coin,), (none,), 1)
