"""Observer-measure and nesting models."""

from __future__ import annotations

from dataclasses import dataclass
from math import prod
from typing import Iterable, Sequence


@dataclass(frozen=True)
class CivilizationClass:
    reach_capability: float
    deploy_probability: float
    simulations: float
    observers_per_simulation: float
    consciousness_weight: float = 1.0
    evidence_compatibility: float = 1.0
    observer_moment_weight: float = 1.0

    def measure(self) -> float:
        values = (
            self.reach_capability,
            self.deploy_probability,
            self.simulations,
            self.observers_per_simulation,
            self.consciousness_weight,
            self.evidence_compatibility,
            self.observer_moment_weight,
        )
        if any(x < 0.0 for x in values):
            raise ValueError("measure factors must be nonnegative")
        return prod(values)


def total_simulated_measure(classes: Iterable[CivilizationClass]) -> float:
    return sum(c.measure() for c in classes)


def simulated_fraction(sim_measure: float, base_measure: float = 1.0) -> float:
    if sim_measure < 0.0 or base_measure < 0.0 or sim_measure + base_measure <= 0.0:
        raise ValueError("measures must be nonnegative with positive total")
    return sim_measure / (sim_measure + base_measure)


def model_averaged_simulated_fraction(samples: Iterable[float], base_measure: float = 1.0) -> float:
    xs = list(samples)
    if not xs:
        raise ValueError("samples cannot be empty")
    return sum(simulated_fraction(x, base_measure) for x in xs) / len(xs)


def plug_in_simulated_fraction(samples: Iterable[float], base_measure: float = 1.0) -> float:
    xs = list(samples)
    if not xs:
        raise ValueError("samples cannot be empty")
    return simulated_fraction(sum(xs) / len(xs), base_measure)


def selection_tilt(raw_probabilities: Sequence[float], retention: Sequence[float]) -> list[float]:
    if len(raw_probabilities) != len(retention) or not raw_probabilities:
        raise ValueError("vectors must be nonempty and equal length")
    if any(p < 0.0 for p in raw_probabilities) or abs(sum(raw_probabilities) - 1.0) > 1e-12:
        raise ValueError("raw probabilities must form a distribution")
    if any(w < 0.0 or w > 1.0 for w in retention):
        raise ValueError("retention probabilities must lie in [0,1]")
    weighted = [p * w for p, w in zip(raw_probabilities, retention)]
    z = sum(weighted)
    if z <= 0.0:
        raise ValueError("retention event must have positive probability")
    return [x / z for x in weighted]


def descendant_resource_bound(parent_budget: float, rho: float) -> float:
    if parent_budget < 0.0 or not 0.0 <= rho < 1.0:
        raise ValueError("require parent_budget>=0 and 0<=rho<1")
    return parent_budget * rho / (1.0 - rho)


def finite_descendant_resource(parent_budget: float, rho: float, levels: int) -> float:
    if parent_budget < 0.0 or not 0.0 <= rho < 1.0 or levels < 0:
        raise ValueError("invalid resource parameters")
    return sum(parent_budget * rho**k for k in range(1, levels + 1))
