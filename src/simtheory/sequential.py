"""Anytime-valid Bernoulli likelihood-ratio e-processes.

These calculations are suitable only for a restricted simulator signature
whose observations can defensibly be modeled as Bernoulli trials. They do not
turn generic anomalies into evidence for simulation.
"""

from __future__ import annotations

from math import comb, exp, inf, log
from typing import Iterable, Sequence


def _open_probability(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must lie strictly between zero and one")
    return value


def _logsumexp(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("at least one value is required")
    maximum = max(values)
    if maximum == -inf:
        return -inf
    return maximum + log(sum(exp(value - maximum) for value in values))


def bernoulli_log_likelihood_ratio(successes: int, trials: int, null_probability: float, alternative_probability: float) -> float:
    if trials < 0 or successes < 0 or successes > trials:
        raise ValueError("require 0 <= successes <= trials")
    p0 = _open_probability(null_probability, "null_probability")
    p1 = _open_probability(alternative_probability, "alternative_probability")
    return successes * log(p1 / p0) + (trials - successes) * log((1.0 - p1) / (1.0 - p0))


def bernoulli_log_e_path(observations: Iterable[int | bool], null_probability: float, alternative_probability: float) -> list[float]:
    p0 = _open_probability(null_probability, "null_probability")
    p1 = _open_probability(alternative_probability, "alternative_probability")
    successes = 0
    path: list[float] = []
    for trials, observation in enumerate(observations, start=1):
        if observation not in (0, 1, False, True):
            raise ValueError("Bernoulli observations must be zero or one")
        successes += int(observation)
        path.append(bernoulli_log_likelihood_ratio(successes, trials, p0, p1))
    return path


def first_threshold_crossing(log_e_path: Sequence[float], alpha: float) -> int | None:
    alpha = _open_probability(alpha, "alpha")
    threshold = log(1.0 / alpha)
    for index, value in enumerate(log_e_path, start=1):
        if value >= threshold:
            return index
    return None


def mixture_log_e_value(successes: int, trials: int, null_probability: float, alternatives: Sequence[float], weights: Sequence[float] | None = None) -> float:
    if not alternatives:
        raise ValueError("at least one alternative is required")
    if weights is None:
        normalized = [1.0 / len(alternatives)] * len(alternatives)
    else:
        if len(weights) != len(alternatives) or any(weight < 0.0 for weight in weights):
            raise ValueError("weights must be nonnegative with one per alternative")
        total = sum(weights)
        if total <= 0.0:
            raise ValueError("weights must have positive total")
        normalized = [weight / total for weight in weights]
    terms = []
    for weight, alternative in zip(normalized, alternatives):
        _open_probability(alternative, "alternative")
        if weight == 0.0:
            terms.append(-inf)
        else:
            terms.append(log(weight) + bernoulli_log_likelihood_ratio(successes, trials, null_probability, alternative))
    return _logsumexp(terms)


def exact_expected_e_value(trials: int, true_probability: float, null_probability: float, alternative_probability: float) -> float:
    if trials < 0:
        raise ValueError("trials must be nonnegative")
    true_p = _open_probability(true_probability, "true_probability")
    total = 0.0
    for successes in range(trials + 1):
        path_probability = comb(trials, successes) * true_p**successes * (1.0 - true_p) ** (trials - successes)
        total += path_probability * exp(bernoulli_log_likelihood_ratio(successes, trials, null_probability, alternative_probability))
    return total


def exact_anytime_rejection_probability(horizon: int, true_probability: float, null_probability: float, alternative_probability: float, alpha: float) -> float:
    if horizon < 0 or horizon > 10_000:
        raise ValueError("horizon must lie in [0,10000]")
    true_p = _open_probability(true_probability, "true_probability")
    _open_probability(null_probability, "null_probability")
    _open_probability(alternative_probability, "alternative_probability")
    alpha = _open_probability(alpha, "alpha")
    threshold = log(1.0 / alpha)
    frontier: dict[int, float] = {0: 1.0}
    rejected_probability = 0.0
    for trials in range(horizon + 1):
        next_frontier: dict[int, float] = {}
        for successes, probability in frontier.items():
            log_e = bernoulli_log_likelihood_ratio(successes, trials, null_probability, alternative_probability)
            if log_e >= threshold:
                rejected_probability += probability
                continue
            if trials == horizon:
                continue
            next_frontier[successes + 1] = next_frontier.get(successes + 1, 0.0) + probability * true_p
            next_frontier[successes] = next_frontier.get(successes, 0.0) + probability * (1.0 - true_p)
        frontier = next_frontier
    return rejected_probability


def fixed_alternative_is_composite_null_eprocess(true_probability: float, null_boundary: float, alternative_probability: float) -> bool:
    true_p = _open_probability(true_probability, "true_probability")
    p0 = _open_probability(null_boundary, "null_boundary")
    p1 = _open_probability(alternative_probability, "alternative_probability")
    if p1 > p0:
        return true_p <= p0
    if p1 < p0:
        return true_p >= p0
    return True


def mixture_log_e_path(observations: Iterable[int | bool], null_probability: float, alternatives: Sequence[float], weights: Sequence[float] | None = None) -> list[float]:
    successes = 0
    path: list[float] = []
    for trials, observation in enumerate(observations, start=1):
        if observation not in (0, 1, False, True):
            raise ValueError("Bernoulli observations must be zero or one")
        successes += int(observation)
        path.append(mixture_log_e_value(successes, trials, null_probability, alternatives, weights))
    return path


def exact_expected_mixture_e_value(trials: int, true_probability: float, null_probability: float, alternatives: Sequence[float], weights: Sequence[float] | None = None) -> float:
    if trials < 0:
        raise ValueError("trials must be nonnegative")
    true_p = _open_probability(true_probability, "true_probability")
    total = 0.0
    for successes in range(trials + 1):
        path_probability = comb(trials, successes) * true_p**successes * (1.0 - true_p) ** (trials - successes)
        total += path_probability * exp(mixture_log_e_value(successes, trials, null_probability, alternatives, weights))
    return total


def exact_anytime_mixture_rejection_probability(horizon: int, true_probability: float, null_probability: float, alternatives: Sequence[float], alpha: float, weights: Sequence[float] | None = None) -> float:
    if horizon < 0 or horizon > 10_000:
        raise ValueError("horizon must lie in [0,10000]")
    true_p = _open_probability(true_probability, "true_probability")
    alpha = _open_probability(alpha, "alpha")
    threshold = log(1.0 / alpha)
    frontier: dict[int, float] = {0: 1.0}
    rejected_probability = 0.0
    for trials in range(horizon + 1):
        next_frontier: dict[int, float] = {}
        for successes, probability in frontier.items():
            log_e = mixture_log_e_value(successes, trials, null_probability, alternatives, weights)
            if log_e >= threshold:
                rejected_probability += probability
                continue
            if trials == horizon:
                continue
            next_frontier[successes + 1] = next_frontier.get(successes + 1, 0.0) + probability * true_p
            next_frontier[successes] = next_frontier.get(successes, 0.0) + probability * (1.0 - true_p)
        frontier = next_frontier
    return rejected_probability
