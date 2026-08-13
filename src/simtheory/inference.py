"""Statistical inference limits for simulation hypotheses."""

from __future__ import annotations

from math import exp, log
from typing import Iterable, Sequence


def _check_probability(p: float) -> None:
    if not 0.0 < p < 1.0:
        raise ValueError("probability must lie strictly between 0 and 1")


def log_odds(p: float) -> float:
    _check_probability(p)
    return log(p / (1.0 - p))


def logistic(x: float) -> float:
    if x >= 0:
        z = exp(-x)
        return 1.0 / (1.0 + z)
    z = exp(x)
    return z / (1.0 + z)


def bayes_factor(likelihood_sim: float, likelihood_base: float) -> float:
    if likelihood_sim < 0.0 or likelihood_base <= 0.0:
        raise ValueError("likelihoods must satisfy sim>=0 and base>0")
    return likelihood_sim / likelihood_base


def posterior_from_bayes_factor(prior_sim: float, bf: float) -> float:
    _check_probability(prior_sim)
    if bf < 0.0:
        raise ValueError("Bayes factor must be nonnegative")
    if bf == 0.0:
        return 0.0
    odds = prior_sim / (1.0 - prior_sim)
    post_odds = odds * bf
    return post_odds / (1.0 + post_odds)


def evidence_ceiling(prior_sim: float, epsilon: float) -> tuple[float, float]:
    """Posterior interval when exp(-eps) <= likelihood ratio <= exp(eps)."""
    _check_probability(prior_sim)
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    center = log_odds(prior_sim)
    return logistic(center - epsilon), logistic(center + epsilon)


def normalize(weights: Iterable[float]) -> list[float]:
    xs = list(weights)
    if any(x < 0.0 for x in xs):
        raise ValueError("weights must be nonnegative")
    total = sum(xs)
    if total <= 0.0:
        raise ValueError("weights must have positive total")
    return [x / total for x in xs]


def total_variation(p: Sequence[float], q: Sequence[float]) -> float:
    """Exact finite-space total variation after validating distributions."""
    if len(p) != len(q) or not p:
        raise ValueError("distributions must be nonempty and equal length")
    if any(x < 0.0 for x in p) or any(x < 0.0 for x in q):
        raise ValueError("probabilities must be nonnegative")
    if abs(sum(p) - 1.0) > 1e-12 or abs(sum(q) - 1.0) > 1e-12:
        raise ValueError("inputs must each sum to one")
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def optimal_equal_prior_accuracy(p: Sequence[float], q: Sequence[float]) -> float:
    """Bayes-optimal classification accuracy for two simple equal-prior laws."""
    return 0.5 * (1.0 + total_variation(p, q))


def test_power_gap_bound(p_null: Sequence[float], p_alt: Sequence[float], test: Sequence[float]) -> float:
    """Return power-size; its absolute value is <= total variation.

    `test[x]` is the rejection probability on outcome x.
    """
    if len(test) != len(p_null) or any(t < 0.0 or t > 1.0 for t in test):
        raise ValueError("test must have one [0,1] value per outcome")
    size = sum(t * p for t, p in zip(test, p_null))
    power = sum(t * p for t, p in zip(test, p_alt))
    return power - size


def likelihood_ratio_path(log_likelihood_ratios: Iterable[float], prior_sim: float) -> list[float]:
    """Sequential posterior path from per-step log likelihood ratios.

    This is bookkeeping only. Valid inference still requires the supplied
    likelihood model to be correct for the observation process.
    """
    _check_probability(prior_sim)
    current = log_odds(prior_sim)
    out: list[float] = []
    for increment in log_likelihood_ratios:
        current += increment
        out.append(logistic(current))
    return out


def robust_posterior_interval(
    prior_interval: tuple[float, float],
    bayes_factor_interval: tuple[float, float],
) -> tuple[float, float]:
    """Sharp posterior range for rectangular prior/Bayes-factor uncertainty."""
    prior_low, prior_high = prior_interval
    bf_low, bf_high = bayes_factor_interval
    _check_probability(prior_low)
    _check_probability(prior_high)
    if prior_low > prior_high:
        raise ValueError("prior interval must be ordered")
    if bf_low < 0.0 or bf_high < bf_low:
        raise ValueError("Bayes-factor interval must be ordered and nonnegative")
    return (
        posterior_from_bayes_factor(prior_low, bf_low),
        posterior_from_bayes_factor(prior_high, bf_high),
    )
