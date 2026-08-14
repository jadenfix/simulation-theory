"""Finite observer-conditioning models and sensitivity diagnostics.

The names SSA, SIA, and FNC below label explicit finite weighting rules. They
are not claims that one rule is philosophically correct. In particular, the
FNC-style rule uses a caller-supplied probability that the full evidence occurs
at least once in a world model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import exp, log
from typing import Iterable, Mapping


@dataclass(frozen=True)
class WorldModel:
    name: str
    prior: float
    total_observers: float
    matching_observers: float
    evidence_exists_probability: float

    def validate(self) -> None:
        if not self.name:
            raise ValueError("world name cannot be empty")
        if self.prior < 0.0:
            raise ValueError("prior must be nonnegative")
        if self.total_observers < 0.0 or self.matching_observers < 0.0:
            raise ValueError("observer counts must be nonnegative")
        if self.matching_observers > self.total_observers:
            raise ValueError("matching observers cannot exceed total observers")
        if not 0.0 <= self.evidence_exists_probability <= 1.0:
            raise ValueError("evidence existence probability must lie in [0,1]")


def _validated_models(models: Iterable[WorldModel]) -> list[WorldModel]:
    values = list(models)
    if not values:
        raise ValueError("at least one world model is required")
    names: set[str] = set()
    for model in values:
        model.validate()
        if model.name in names:
            raise ValueError("world names must be unique")
        names.add(model.name)
    if sum(model.prior for model in values) <= 0.0:
        raise ValueError("priors must have positive total")
    return values


def _normalize(weight_pairs: Iterable[tuple[str, float]]) -> dict[str, float]:
    pairs = list(weight_pairs)
    if any(value < 0.0 for _, value in pairs):
        raise ValueError("weights must be nonnegative")
    total = sum(value for _, value in pairs)
    if total <= 0.0:
        raise ValueError("positive total weight required")
    return {name: value / total for name, value in pairs}


def reference_sampling(models: Iterable[WorldModel]) -> dict[str, float]:
    """SSA-style weighting by the within-world matching fraction."""
    values = _validated_models(models)
    return _normalize(
        (
            model.name,
            model.prior
            * (
                model.matching_observers / model.total_observers
                if model.total_observers > 0.0
                else 0.0
            ),
        )
        for model in values
    )


def observer_number_weighted(models: Iterable[WorldModel]) -> dict[str, float]:
    """SIA-style weighting by the number of matching observers."""
    values = _validated_models(models)
    return _normalize(
        (model.name, model.prior * model.matching_observers) for model in values
    )


def full_evidence_presence(models: Iterable[WorldModel]) -> dict[str, float]:
    """FNC-style weighting by P(full evidence occurs at least once | world)."""
    values = _validated_models(models)
    return _normalize(
        (model.name, model.prior * model.evidence_exists_probability)
        for model in values
    )


def conditioning_posteriors(models: Iterable[WorldModel]) -> dict[str, dict[str, float]]:
    values = _validated_models(models)
    return {
        "ssa": reference_sampling(values),
        "sia": observer_number_weighted(values),
        "fnc_presence": full_evidence_presence(values),
    }


def poisson_presence(expected_matching_copies: float) -> float:
    """P(at least one match) for a Poisson copy-count model."""
    if expected_matching_copies < 0.0:
        raise ValueError("expected count must be nonnegative")
    return 1.0 - exp(-expected_matching_copies)


def poisson_world_model(
    name: str,
    prior: float,
    total_observers: float,
    expected_matching_copies: float,
) -> WorldModel:
    if expected_matching_copies > total_observers:
        raise ValueError("expected matching copies cannot exceed total observers")
    return WorldModel(
        name=name,
        prior=prior,
        total_observers=total_observers,
        matching_observers=expected_matching_copies,
        evidence_exists_probability=poisson_presence(expected_matching_copies),
    )


def scale_observer_counts(model: WorldModel, factor: float) -> WorldModel:
    """Scale counts while preserving the separately supplied evidence probability.

    This isolates the exact duplication behavior of SSA- and SIA-style rules.
    It deliberately makes no claim about how full-evidence presence should
    change, because that requires a copy-generation model.
    """
    model.validate()
    if factor <= 0.0:
        raise ValueError("factor must be positive")
    return replace(
        model,
        total_observers=model.total_observers * factor,
        matching_observers=model.matching_observers * factor,
    )


def scale_poisson_population(model: WorldModel, factor: float) -> WorldModel:
    """Scale observer counts and recompute presence under a Poisson copy model."""
    scaled = scale_observer_counts(model, factor)
    return replace(
        scaled,
        evidence_exists_probability=poisson_presence(scaled.matching_observers),
    )


def posterior_total_variation(
    first: Mapping[str, float],
    second: Mapping[str, float],
) -> float:
    names = set(first) | set(second)
    if any(first.get(name, 0.0) < 0.0 or second.get(name, 0.0) < 0.0 for name in names):
        raise ValueError("posterior probabilities must be nonnegative")
    if abs(sum(first.values()) - 1.0) > 1e-10 or abs(sum(second.values()) - 1.0) > 1e-10:
        raise ValueError("posteriors must each sum to one")
    return 0.5 * sum(abs(first.get(name, 0.0) - second.get(name, 0.0)) for name in names)


def maximum_conditioning_disagreement(models: Iterable[WorldModel]) -> float:
    posteriors = list(conditioning_posteriors(models).values())
    return max(
        posterior_total_variation(posteriors[i], posteriors[j])
        for i in range(len(posteriors))
        for j in range(i + 1, len(posteriors))
    )


def posterior_log_odds(
    posterior: Mapping[str, float],
    numerator_world: str,
    denominator_world: str,
) -> float:
    numerator = posterior.get(numerator_world, 0.0)
    denominator = posterior.get(denominator_world, 0.0)
    if numerator <= 0.0 or denominator <= 0.0:
        raise ValueError("both named worlds must have positive posterior mass")
    return log(numerator / denominator)


def two_world_scale_sensitivity(
    fixed_world: WorldModel,
    scaled_world: WorldModel,
    scale_factors: Iterable[float],
) -> list[dict[str, float]]:
    """Return posterior mass on the scaled world under each conditioning rule."""
    fixed_world.validate()
    scaled_world.validate()
    rows: list[dict[str, float]] = []
    for factor in scale_factors:
        scaled = scale_poisson_population(scaled_world, float(factor))
        posteriors = conditioning_posteriors([fixed_world, scaled])
        rows.append(
            {
                "scale": float(factor),
                "ssa": posteriors["ssa"][scaled.name],
                "sia": posteriors["sia"][scaled.name],
                "fnc_presence": posteriors["fnc_presence"][scaled.name],
            }
        )
    return rows
