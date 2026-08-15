from fractions import Fraction
from itertools import combinations

from simtheory.active_fixed_model_experiments import active_experiment
from simtheory.active_fixed_model_regret import exact_active_fixed_model_minimax_regret
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


def test_k3_no_signal_has_unit_minimax_regret_against_model_informed_oracle():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        (_no_signal(family),),
        1,
    )
    assert result.valid
    assert result.oracle_values == (1, 1, 1)
    assert result.base.robust_value == 2
    assert result.minimax_regret == 1
    assert result.selected_regrets == (0, 1, 1) or max(result.selected_regrets) == 1


def test_public_randomness_reduces_regret_without_reducing_model_uncertainty():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        (_public_coin(family),),
        1,
    )
    assert result.valid
    assert result.oracle_values == (1, 1, 1)
    assert result.base.robust_value == Fraction(5, 3)
    assert result.minimax_regret == Fraction(2, 3)
    assert result.selected_regrets == (Fraction(2, 3),) * 3


def test_full_model_revelation_eliminates_one_period_regret_when_free():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        (_revealing(family),),
        1,
    )
    assert result.valid
    assert result.oracle_values == (1, 1, 1)
    assert result.base.robust_value == 1
    assert result.minimax_regret == 0
    assert result.selected_regrets == (0, 0, 0)


def test_regret_uses_same_experiment_cost_accounting_for_controller_and_oracle():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    reveal = _revealing(family, Fraction(2, 3))
    result = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        (reveal,),
        1,
    )
    assert result.valid
    assert result.oracle_values == (Fraction(5, 3),) * 3
    assert result.base.robust_value == Fraction(5, 3)
    assert result.minimax_regret == 0


def test_minimax_regret_never_exceeds_regret_of_robust_cost_optimizer():
    graph = _complete_graph(3)
    family = _point_model_family(3)
    result = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        (_no_signal(family), _public_coin(family), _revealing(family, Fraction(3, 4))),
        1,
    )
    assert result.valid
    assert result.minimax_regret <= result.regret_of_robust_cost_policy
