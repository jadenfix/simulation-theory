from math import isclose

import pytest

from simtheory.inference import (
    evidence_ceiling,
    log_odds,
    posterior_from_bayes_factor,
    robust_posterior_interval,
    total_variation,
)


def test_matching_laws():
    p = [0.2, 0.8]
    assert total_variation(p, p) == 0.0


def test_log_odds_bound():
    prior = 0.37
    lo, hi = evidence_ceiling(prior, 0.42)
    assert isclose(log_odds(lo) - log_odds(prior), -0.42, abs_tol=1e-12)
    assert isclose(log_odds(hi) - log_odds(prior), 0.42, abs_tol=1e-12)


def test_robust_posterior_interval_is_monotone():
    lo, hi = robust_posterior_interval((0.1, 0.3), (0.5, 4.0))
    assert 0.0 < lo < hi < 1.0


def test_posterior_is_stable_for_extreme_finite_bayes_factor():
    assert posterior_from_bayes_factor(0.9, 1e308) == 1.0


def test_positive_infinite_bayes_factor_has_limiting_posterior_one():
    assert posterior_from_bayes_factor(0.5, float("inf")) == 1.0


def test_nan_bayes_factor_is_rejected():
    with pytest.raises(ValueError, match="not NaN"):
        posterior_from_bayes_factor(0.5, float("nan"))


def test_robust_interval_accepts_infinite_upper_bayes_factor():
    lo, hi = robust_posterior_interval((0.1, 0.9), (0.5, float("inf")))
    assert isclose(lo, 1.0 / 19.0)
    assert hi == 1.0
