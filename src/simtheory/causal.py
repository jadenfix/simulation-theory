"""Selection and latent-intervention sensitivity calculations."""

from __future__ import annotations

from math import exp, log
from typing import Sequence


def _open_probability(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must lie strictly between zero and one")
    return value


def _closed_probability(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0,1]")
    return value


def logit(probability: float) -> float:
    probability = _open_probability(probability, "probability")
    return log(probability / (1.0 - probability))


def logistic(value: float) -> float:
    if value >= 0.0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def selected_binary_probability(raw_probability: float, retain_if_one: float, retain_if_zero: float) -> float:
    raw_probability = _closed_probability(raw_probability, "raw_probability")
    retain_if_one = _closed_probability(retain_if_one, "retain_if_one")
    retain_if_zero = _closed_probability(retain_if_zero, "retain_if_zero")
    numerator = raw_probability * retain_if_one
    denominator = numerator + (1.0 - raw_probability) * retain_if_zero
    if denominator <= 0.0:
        raise ValueError("retention event must have positive probability")
    return numerator / denominator


def selection_log_odds_shift(retain_if_one: float, retain_if_zero: float) -> float:
    retain_if_one = _closed_probability(retain_if_one, "retain_if_one")
    retain_if_zero = _closed_probability(retain_if_zero, "retain_if_zero")
    if retain_if_one <= 0.0 or retain_if_zero <= 0.0:
        raise ValueError("both retention probabilities must be positive")
    return log(retain_if_one / retain_if_zero)


def raw_probability_bounds_from_selected(selected_probability: float, gamma: float) -> tuple[float, float]:
    selected_probability = _open_probability(selected_probability, "selected_probability")
    gamma = float(gamma)
    if gamma < 1.0:
        raise ValueError("gamma must be at least one")
    radius = log(gamma)
    center = logit(selected_probability)
    return logistic(center - radius), logistic(center + radius)


def minimum_selection_gamma(raw_probability: float, selected_probability: float) -> float:
    raw_probability = _open_probability(raw_probability, "raw_probability")
    selected_probability = _open_probability(selected_probability, "selected_probability")
    ratio = exp(logit(selected_probability) - logit(raw_probability))
    return max(ratio, 1.0 / ratio)


def retained_distribution(raw: Sequence[float], retention: Sequence[float]) -> list[float]:
    if len(raw) != len(retention) or not raw:
        raise ValueError("raw and retention vectors must be nonempty and equal length")
    raw_values = [float(value) for value in raw]
    retention_values = [float(value) for value in retention]
    if any(value < 0.0 for value in raw_values) or abs(sum(raw_values) - 1.0) > 1e-12:
        raise ValueError("raw must be a probability distribution")
    if any(value < 0.0 or value > 1.0 for value in retention_values):
        raise ValueError("retention values must lie in [0,1]")
    weighted = [probability * weight for probability, weight in zip(raw_values, retention_values)]
    normalizer = sum(weighted)
    if normalizer <= 0.0:
        raise ValueError("retention event must have positive probability")
    return [value / normalizer for value in weighted]


def retention_policy_for_target(raw: Sequence[float], target: Sequence[float]) -> list[float]:
    if len(raw) != len(target) or not raw:
        raise ValueError("raw and target must be nonempty and equal length")
    raw_values = [float(value) for value in raw]
    target_values = [float(value) for value in target]
    if any(value < 0.0 for value in raw_values + target_values):
        raise ValueError("probabilities must be nonnegative")
    if abs(sum(raw_values) - 1.0) > 1e-12 or abs(sum(target_values) - 1.0) > 1e-12:
        raise ValueError("raw and target must each sum to one")
    ratios: list[float] = []
    for raw_value, target_value in zip(raw_values, target_values):
        if raw_value == 0.0:
            if target_value > 0.0:
                raise ValueError("target is not absolutely continuous with respect to raw")
            ratios.append(0.0)
        else:
            ratios.append(target_value / raw_value)
    scale = max(ratios)
    if scale <= 0.0:
        raise ValueError("target must have positive mass")
    return [ratio / scale for ratio in ratios]


def intervention_mixture(baseline_probability: float, intervention_probability: float, intervention_rate: float) -> float:
    baseline_probability = _closed_probability(baseline_probability, "baseline_probability")
    intervention_probability = _closed_probability(intervention_probability, "intervention_probability")
    intervention_rate = _closed_probability(intervention_rate, "intervention_rate")
    return (1.0 - intervention_rate) * baseline_probability + intervention_rate * intervention_probability


def minimum_unrestricted_intervention_rate(baseline_probability: float, observed_probability: float) -> float:
    baseline_probability = _closed_probability(baseline_probability, "baseline_probability")
    observed_probability = _closed_probability(observed_probability, "observed_probability")
    if observed_probability == baseline_probability:
        return 0.0
    if observed_probability > baseline_probability:
        if baseline_probability == 1.0:
            raise ValueError("observed probability cannot exceed a unit baseline")
        return (observed_probability - baseline_probability) / (1.0 - baseline_probability)
    if baseline_probability == 0.0:
        raise ValueError("observed probability cannot be below a zero baseline")
    return (baseline_probability - observed_probability) / baseline_probability
