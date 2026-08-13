from math import isclose

from simtheory.inference import (
    evidence_ceiling,
    log_odds,
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
