from fractions import Fraction
from random import Random

from simtheory.distributionally_robust_codes import (
    maximize_expectation_tv_ball,
    minimize_expectation_tv_ball,
)
from simtheory.tv_transport_duals import tv_knapsack_dual_certificate


def _compositions(total, count):
    if count == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, count - 1):
            yield (first, *rest)


def test_exact_dual_receipts_on_seeded_rational_instances():
    rng = Random(314159)
    denominator = 12
    compositions = tuple(_compositions(denominator, 5))
    for _ in range(80):
        counts = rng.choice(compositions)
        nominal = tuple(Fraction(count, denominator) for count in counts)
        values = tuple(Fraction(rng.randrange(-4, 8)) for _ in range(5))
        radius = Fraction(rng.randrange(denominator + 1), denominator)
        for transport in (
            maximize_expectation_tv_ball(nominal, values, radius),
            minimize_expectation_tv_ball(nominal, values, radius),
        ):
            dual = tv_knapsack_dual_certificate(transport)
            assert dual.valid
            assert dual.gap == 0
            assert dual.primal_gain == dual.dual_gain


def test_skew_k4_dual_threshold_tracks_the_active_donor_level():
    nominal = (
        Fraction(7, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    values = (Fraction(1), Fraction(2), Fraction(3), Fraction(3))

    small = tv_knapsack_dual_certificate(
        maximize_expectation_tv_ball(
            nominal,
            values,
            Fraction(1, 10),
        )
    )
    assert small.threshold == 2
    assert small.upper_bound_duals == (0, 0, 0, 0)
    assert small.primal_gain == Fraction(1, 5)

    after_minimum_mass = tv_knapsack_dual_certificate(
        maximize_expectation_tv_ball(
            nominal,
            values,
            Fraction(3, 4),
        )
    )
    assert after_minimum_mass.threshold == 1
    assert after_minimum_mass.upper_bound_duals == (1, 0, 0, 0)
    assert after_minimum_mass.gap == 0

    saturated = tv_knapsack_dual_certificate(
        maximize_expectation_tv_ball(nominal, values, 1)
    )
    assert saturated.threshold == 0
    assert saturated.budget_slack == Fraction(1, 5)
    assert saturated.gap == 0


def test_radius_zero_and_constant_values_have_valid_degenerate_duals():
    nominal = (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))
    values = (Fraction(-1), Fraction(2), Fraction(5))
    zero = tv_knapsack_dual_certificate(
        maximize_expectation_tv_ball(nominal, values, 0)
    )
    assert zero.threshold == 6
    assert zero.primal_gain == zero.dual_gain == 0

    constant = tv_knapsack_dual_certificate(
        maximize_expectation_tv_ball(
            nominal,
            (Fraction(7), Fraction(7), Fraction(7)),
            Fraction(4, 5),
        )
    )
    assert constant.threshold == 0
    assert constant.primal_gain == constant.dual_gain == 0
    assert constant.budget_slack == Fraction(4, 5)
