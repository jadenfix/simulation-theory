from fractions import Fraction

from simtheory.bayesian_boolean_prior_robustness import (
    concavity_gap,
    exact_value_sensitivity_certificate,
    gain_ranking_is_tv_robust,
    marginal_gain,
    marginal_gain_interval,
    prior_total_variation,
    value_interval,
    value_ranking_is_tv_robust,
)


def test_bayesian_value_is_tightly_one_lipschitz_in_total_variation():
    table = (0, 1)
    p = (Fraction(1), Fraction(0))
    q = (Fraction(4, 5), Fraction(1, 5))
    cert = exact_value_sensitivity_certificate(table, p, q, ())
    assert cert.valid
    assert cert.total_variation == Fraction(1, 5)
    assert cert.left_value == 0
    assert cert.right_value == Fraction(1, 5)
    assert cert.slack == 0


def test_bayesian_value_is_concave_in_prior_and_can_be_strictly_so():
    table = (0, 1)
    p = (Fraction(1), Fraction(0))
    q = (Fraction(0), Fraction(1))
    assert concavity_gap(table, p, q, Fraction(1, 2), ()) == Fraction(1, 2)


def test_tv_value_and_gain_intervals_use_one_and_two_radius_constants():
    assert value_interval(Fraction(1, 4), Fraction(1, 10)) == (Fraction(3, 20), Fraction(7, 20))
    assert marginal_gain_interval(Fraction(1, 4), Fraction(1, 10)) == (Fraction(1, 20), Fraction(9, 20))


def test_experiment_value_ordering_has_exact_sufficient_tv_margin_rules():
    assert value_ranking_is_tv_robust(Fraction(1, 4), Fraction(1, 10))
    assert not value_ranking_is_tv_robust(Fraction(1, 5), Fraction(1, 10))
    assert gain_ranking_is_tv_robust(Fraction(1, 2), Fraction(1, 10))
    assert not gain_ranking_is_tv_robust(Fraction(2, 5), Fraction(1, 10))


def test_marginal_gain_changes_under_prior_shift_but_stays_bounded():
    # XOR: observing either coordinate determines nothing under uniform prior,
    # but under a skewed prior the same query can have a different gain.
    table = (0, 1, 1, 0)
    p = (Fraction(1, 4),) * 4
    q = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    tv = prior_total_variation(p, q)
    gp = marginal_gain(table, p, (), (0,))
    gq = marginal_gain(table, q, (), (0,))
    assert abs(gp - gq) <= 2 * tv
