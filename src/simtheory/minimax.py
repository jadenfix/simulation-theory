"""Finite minimax and information-theoretic lower bounds."""

from __future__ import annotations

from math import ceil, inf, log
from typing import Sequence

Distribution = Sequence[float]


def _validate_distribution(distribution: Distribution) -> tuple[float, ...]:
    values = tuple(float(value) for value in distribution)
    if not values or any(value < 0.0 for value in values):
        raise ValueError("distribution must be nonempty and nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("distribution must sum to one")
    return values


def total_variation(p: Distribution, q: Distribution) -> float:
    p_values = _validate_distribution(p)
    q_values = _validate_distribution(q)
    if len(p_values) != len(q_values):
        raise ValueError("distributions must have equal length")
    return 0.5 * sum(abs(a - b) for a, b in zip(p_values, q_values))


def kl_divergence(p: Distribution, q: Distribution) -> float:
    """Finite KL(P||Q), with infinity on unsupported positive P mass."""
    p_values = _validate_distribution(p)
    q_values = _validate_distribution(q)
    if len(p_values) != len(q_values):
        raise ValueError("distributions must have equal length")
    total = 0.0
    for p_value, q_value in zip(p_values, q_values):
        if p_value == 0.0:
            continue
        if q_value == 0.0:
            return inf
        total += p_value * log(p_value / q_value)
    return total


def mixture_distribution(
    models: Sequence[Distribution],
    weights: Sequence[float] | None = None,
) -> list[float]:
    if len(models) < 1:
        raise ValueError("at least one model is required")
    validated = [_validate_distribution(model) for model in models]
    support_size = len(validated[0])
    if any(len(model) != support_size for model in validated):
        raise ValueError("all models must use the same support")
    if weights is None:
        normalized_weights = [1.0 / len(validated)] * len(validated)
    else:
        if len(weights) != len(validated) or any(weight < 0.0 for weight in weights):
            raise ValueError("weights must be nonnegative with one per model")
        total_weight = sum(weights)
        if total_weight <= 0.0:
            raise ValueError("weights must have positive total")
        normalized_weights = [weight / total_weight for weight in weights]
    return [
        sum(weight * model[outcome] for weight, model in zip(normalized_weights, validated))
        for outcome in range(support_size)
    ]


def uniform_model_information(models: Sequence[Distribution]) -> float:
    """I(Theta;X) for a uniform finite model index and one observation."""
    if len(models) < 2:
        raise ValueError("at least two models are required")
    mixture = mixture_distribution(models)
    return sum(kl_divergence(model, mixture) for model in models) / len(models)


def fano_error_lower_bound(models: Sequence[Distribution]) -> float:
    """Uniform-prior one-observation Fano lower bound on model-ID error."""
    model_count = len(models)
    if model_count < 2:
        raise ValueError("at least two models are required")
    information = uniform_model_information(models)
    bound = 1.0 - (information + log(2.0)) / log(float(model_count))
    return min(1.0, max(0.0, bound))


def fano_iid_error_lower_bound(models: Sequence[Distribution], samples: int) -> float:
    """Fano lower bound using I(Theta;X^n) <= n I(Theta;X_1)."""
    if samples < 0:
        raise ValueError("samples must be nonnegative")
    model_count = len(models)
    if model_count < 2:
        raise ValueError("at least two models are required")
    information_upper_bound = samples * uniform_model_information(models)
    bound = 1.0 - (information_upper_bound + log(2.0)) / log(float(model_count))
    return min(1.0, max(0.0, bound))


def necessary_iid_samples_for_error(
    models: Sequence[Distribution],
    target_error: float,
) -> int | float:
    """Necessary sample count from the same Fano relaxation.

    Any method achieving error at most ``target_error`` must have at least the
    returned number of conditionally IID observations, unless the result is
    zero (the bound is vacuous) or infinity (the models are observationally
    identical under this one-sample experiment).
    """
    if target_error < 0.0 or target_error >= 1.0:
        raise ValueError("target_error must lie in [0,1)")
    model_count = len(models)
    if model_count < 2:
        raise ValueError("at least two models are required")
    numerator = (1.0 - target_error) * log(float(model_count)) - log(2.0)
    if numerator <= 0.0:
        return 0
    information = uniform_model_information(models)
    if information == 0.0:
        return inf
    return ceil(numerator / information)


def le_cam_absolute_risk_lower_bound(
    parameter_separation: float,
    p: Distribution,
    q: Distribution,
) -> float:
    """Two-point lower bound for worst-case expected absolute estimation loss.

    For two parameter values separated by ``Delta``, any estimator has
    worst-case expected absolute loss at least

        Delta * (1 - TV(P,Q)) / 4.
    """
    if parameter_separation < 0.0:
        raise ValueError("parameter separation must be nonnegative")
    return 0.25 * parameter_separation * (1.0 - total_variation(p, q))
