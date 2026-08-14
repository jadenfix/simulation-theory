from fractions import Fraction
from itertools import product

from simtheory.pathwise_regret import affine_path_decision, exact_pathwise_regret_game
from simtheory.pathwise_regret_bounds import exact_regret_value_bounds


def _binary_prediction_decisions(horizon: int):
    action_costs = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(0)))
    return tuple(
        affine_path_decision(
            "actions[" + ",".join(str(action) for action in sequence) + "]",
            tuple(action_costs[action] for action in sequence),
        )
        for sequence in product((0, 1), repeat=horizon)
    )


def test_robust_value_difference_can_be_strictly_smaller_than_regret():
    regret = exact_pathwise_regret_game(
        (Fraction(1, 2), Fraction(1, 2)),
        1,
        _binary_prediction_decisions(3),
    )
    bounds = exact_regret_value_bounds(regret)
    assert bounds.valid

    assert bounds.deterministic_absolute_value == 3
    assert bounds.oracle_vertex_maximum == 0
    assert bounds.oracle_maximum == Fraction(3, 2)
    assert bounds.oracle_interior_gain == Fraction(3, 2)
    assert not bounds.oracle_barycenter_is_vertex
    assert bounds.oracle_maximizing_path == (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    assert all(
        cost == Fraction(3, 2)
        for cost in bounds.oracle_barycenter_comparator_costs
    )

    assert bounds.deterministic_lower_bound == Fraction(3, 2)
    assert regret.deterministic_value == 3
    assert bounds.deterministic_slack_above_value_gap == Fraction(3, 2)

    assert bounds.shared_absolute_game.value == Fraction(3, 2)
    assert bounds.shared_lower_bound == 0
    assert regret.shared_value == Fraction(3, 2)
    assert bounds.shared_slack_above_value_gap == Fraction(3, 2)


def test_regret_value_bounds_collapse_when_oracle_cost_is_constant():
    decisions = (
        affine_path_decision("constant-low", ((1, 1), (1, 1))),
        affine_path_decision("constant-high", ((2, 2), (2, 2))),
    )
    regret = exact_pathwise_regret_game(
        (Fraction(3, 4), Fraction(1, 4)),
        Fraction(1, 3),
        decisions,
    )
    bounds = exact_regret_value_bounds(regret)
    assert bounds.valid
    assert bounds.oracle_minimum == bounds.oracle_maximum == 2
    assert bounds.oracle_interior_gain == 0
    assert bounds.deterministic_lower_bound == bounds.deterministic_upper_bound == 0
    assert bounds.shared_lower_bound == bounds.shared_upper_bound == 0
    assert regret.deterministic_value == regret.shared_value == 0
