from math import isclose

from simtheory.causal import (
    intervention_mixture,
    logit,
    minimum_selection_gamma,
    minimum_unrestricted_intervention_rate,
    raw_probability_bounds_from_selected,
    retained_distribution,
    retention_policy_for_target,
    selected_binary_probability,
    selection_log_odds_shift,
)


def test_binary_selection_log_odds_identity():
    raw = 0.2
    selected = selected_binary_probability(raw, 0.8, 0.4)
    assert isclose(logit(selected) - logit(raw), selection_log_odds_shift(0.8, 0.4))


def test_gamma_interval_contains_compatible_raw_probability():
    raw = 0.2
    selected = selected_binary_probability(raw, 0.8, 0.4)
    gamma = minimum_selection_gamma(raw, selected)
    lo, hi = raw_probability_bounds_from_selected(selected, gamma)
    assert lo <= raw <= hi


def test_retention_policy_exactly_reweights_distribution():
    raw = [0.7, 0.2, 0.1]
    target = [0.2, 0.3, 0.5]
    retention = retention_policy_for_target(raw, target)
    observed = retained_distribution(raw, retention)
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(observed, target))


def test_minimum_intervention_rate_is_constructive():
    baseline = 0.1
    observed = 0.3
    rate = minimum_unrestricted_intervention_rate(baseline, observed)
    assert isclose(intervention_mixture(baseline, 1.0, rate), observed)
