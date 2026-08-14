"""Hierarchical Bayesian model averaging for explicit simulation scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .observer_measure import simulated_fraction


@dataclass(frozen=True)
class Scenario:
    """One fully specified branch of a simulation-analysis model.

    ``data_likelihood`` is the likelihood of the observed non-indexical data
    under the scenario. ``sim_measure`` and ``base_measure`` define the
    scenario-conditional observer-measure convention. They remain separate so
    model uncertainty over technical feasibility is not collapsed into an
    expected observer count.
    """

    name: str
    prior: float
    data_likelihood: float
    sim_measure: float
    base_measure: float

    def validate(self) -> None:
        if not self.name:
            raise ValueError("scenario name cannot be empty")
        if self.prior < 0.0 or self.data_likelihood < 0.0:
            raise ValueError("prior and likelihood must be nonnegative")
        if self.sim_measure < 0.0 or self.base_measure < 0.0:
            raise ValueError("observer measures must be nonnegative")
        if self.sim_measure + self.base_measure <= 0.0:
            raise ValueError("each scenario needs positive total observer measure")

    def conditional_simulated_probability(self) -> float:
        self.validate()
        return simulated_fraction(self.sim_measure, self.base_measure)


def posterior_scenario_weights(scenarios: Iterable[Scenario]) -> dict[str, float]:
    values = list(scenarios)
    if not values:
        raise ValueError("at least one scenario is required")
    names: set[str] = set()
    unnormalized: list[tuple[str, float]] = []
    for scenario in values:
        scenario.validate()
        if scenario.name in names:
            raise ValueError("scenario names must be unique")
        names.add(scenario.name)
        unnormalized.append((scenario.name, scenario.prior * scenario.data_likelihood))
    normalizer = sum(weight for _, weight in unnormalized)
    if normalizer <= 0.0:
        raise ValueError("posterior normalizer must be positive")
    return {name: weight / normalizer for name, weight in unnormalized}


def posterior_simulated_probability(scenarios: Iterable[Scenario]) -> float:
    values = list(scenarios)
    weights = posterior_scenario_weights(values)
    return sum(
        weights[scenario.name] * scenario.conditional_simulated_probability()
        for scenario in values
    )


def plug_in_across_scenarios(scenarios: Iterable[Scenario]) -> float:
    """Diagnostic ratio after averaging measures with posterior scenario weights.

    This is generally not equal to the correct posterior average of the
    scenario-conditional ratios. The difference exposes a second level of the
    observer-measure plug-in error.
    """
    values = list(scenarios)
    weights = posterior_scenario_weights(values)
    mean_sim = sum(weights[scenario.name] * scenario.sim_measure for scenario in values)
    mean_base = sum(weights[scenario.name] * scenario.base_measure for scenario in values)
    return simulated_fraction(mean_sim, mean_base)


def feasibility_mixture(
    feasibility_prior: float,
    feasible_sim_to_base_ratio: float,
    likelihood_if_infeasible: float = 1.0,
    likelihood_if_feasible: float = 1.0,
) -> list[Scenario]:
    """Convenience two-branch model with an explicit infeasible branch."""
    if not 0.0 <= feasibility_prior <= 1.0:
        raise ValueError("feasibility_prior must lie in [0,1]")
    if feasible_sim_to_base_ratio < 0.0:
        raise ValueError("ratio must be nonnegative")
    return [
        Scenario(
            name="infeasible",
            prior=1.0 - feasibility_prior,
            data_likelihood=likelihood_if_infeasible,
            sim_measure=0.0,
            base_measure=1.0,
        ),
        Scenario(
            name="feasible",
            prior=feasibility_prior,
            data_likelihood=likelihood_if_feasible,
            sim_measure=feasible_sim_to_base_ratio,
            base_measure=1.0,
        ),
    ]
