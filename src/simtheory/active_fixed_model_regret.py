"""Exact minimax regret for active experiments under one globally fixed model.

This layer reuses the exact deterministic active-experiment policy frontier.  The
benchmark oracle is deliberately strong but causally simple: it is told the one
fixed model identity before the horizon begins, then faces the same experiment
menu, acquisition costs, source laws, hidden-state dynamics, horizon, and
zero-error code universe as the non-oracle controller.

For fixed model m, let O_m be that singleton-model oracle value.  Any shared
public policy represented by a root frontier vector C=(C_m)_m has modelwise
regret R_m=C_m-O_m.  The exact minimax-regret policy therefore minimizes
max_m R_m over the same Pareto-minimal root frontier used by the robust-cost
solver.  Subtracting the fixed oracle vector preserves componentwise dominance,
so no policy discarded by the cost frontier can become regret-optimal.

The oracle definition matters.  It does not know future hidden-state draws or
future observations, and it does not receive free experiments.  Changing those
resources changes the regret theorem.  These are exact finite decision results,
not statistical estimates and not evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .active_fixed_model_experiments import (
    ActiveExperiment,
    ActiveExperimentCertificate,
    ActivePolicyEntry,
    active_experiment,
    exact_active_fixed_model_experiment_design,
)
from .confusion_graphs import ConfusionGraph
from .fixed_model_ambiguity import FixedModelFamily, fixed_model_family


@dataclass(frozen=True)
class ModelOracleValue:
    model_index: int
    model_name: str
    value: Fraction
    selected_experiment: int

    @property
    def valid(self) -> bool:
        return self.model_index >= 0 and bool(self.model_name) and self.value >= 0


@dataclass(frozen=True)
class ActiveExperimentRegretCertificate:
    """Exact minimax-regret certificate against model-informed causal oracles."""

    base: ActiveExperimentCertificate
    oracles: tuple[ModelOracleValue, ...]
    selected_costs: tuple[Fraction, ...]
    selected_regrets: tuple[Fraction, ...]
    minimax_regret: Fraction
    robust_cost_of_regret_policy: Fraction
    selected_experiment: int
    robust_cost_regrets: tuple[Fraction, ...]
    regret_of_robust_cost_policy: Fraction

    @property
    def oracle_values(self) -> tuple[Fraction, ...]:
        return tuple(item.value for item in self.oracles)

    @property
    def valid(self) -> bool:
        if (
            not self.base.valid
            or len(self.oracles) != self.base.family.model_count
            or any(not item.valid for item in self.oracles)
            or tuple(item.model_index for item in self.oracles)
            != tuple(range(self.base.family.model_count))
            or len(self.selected_costs) != self.base.family.model_count
            or len(self.selected_regrets) != self.base.family.model_count
            or len(self.robust_cost_regrets) != self.base.family.model_count
            or any(value < 0 for value in self.selected_regrets)
            or any(value < 0 for value in self.robust_cost_regrets)
            or self.minimax_regret != max(self.selected_regrets)
            or self.robust_cost_of_regret_policy != max(self.selected_costs)
            or self.regret_of_robust_cost_policy != max(self.robust_cost_regrets)
            or not 0 <= self.selected_experiment < len(self.base.experiments)
        ):
            return False
        oracle_values = self.oracle_values
        if self.selected_regrets != tuple(
            cost - oracle
            for cost, oracle in zip(self.selected_costs, oracle_values)
        ):
            return False
        if self.robust_cost_regrets != tuple(
            cost - oracle
            for cost, oracle in zip(self.base.selected_costs, oracle_values)
        ):
            return False
        root = _root_entries(self.base)
        selected = min(root, key=lambda entry: _regret_key(entry, oracle_values, self.base.experiments))
        return (
            selected.costs == self.selected_costs
            and selected.selected_experiment == self.selected_experiment
            and self.minimax_regret
            <= self.regret_of_robust_cost_policy
        )


def _root_entries(certificate: ActiveExperimentCertificate) -> tuple[ActivePolicyEntry, ...]:
    root = next(
        record
        for record in certificate.frontiers
        if record.period == 0 and record.state == certificate.initial_state
    )
    if not root.entries:
        raise AssertionError("active-experiment root frontier is empty")
    return root.entries


def _entry_regrets(
    entry: ActivePolicyEntry,
    oracle_values: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    regrets = tuple(
        cost - oracle
        for cost, oracle in zip(entry.costs, oracle_values)
    )
    if any(value < 0 for value in regrets):
        raise AssertionError("shared policy beats a model-informed oracle")
    return regrets


def _regret_key(
    entry: ActivePolicyEntry,
    oracle_values: Sequence[Fraction],
    experiments: Sequence[ActiveExperiment],
) -> tuple[object, ...]:
    regrets = _entry_regrets(entry, oracle_values)
    return (
        max(regrets),
        regrets,
        max(entry.costs),
        entry.costs,
        experiments[entry.selected_experiment].name,
        entry.selected_experiment,
    )


def _singleton_experiments(
    experiments: Sequence[ActiveExperiment],
    model_index: int,
) -> tuple[ActiveExperiment, ...]:
    return tuple(
        active_experiment(
            experiment.name,
            (experiment.kernels[model_index],),
            experiment.acquisition_cost,
        )
        for experiment in experiments
    )


def exact_active_fixed_model_minimax_regret(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    experiments: Sequence[ActiveExperiment],
    horizon: int,
    **solver_caps: int,
) -> ActiveExperimentRegretCertificate:
    """Solve exact minimax regret relative to model-informed causal oracles.

    The returned oracle for model m solves the same active-experiment problem on
    the singleton family {m}.  It knows only the fixed model identity in advance;
    hidden states and future observations retain their declared stochastic laws.
    """

    base = exact_active_fixed_model_experiment_design(
        graph,
        family,
        experiments,
        horizon,
        **solver_caps,
    )

    oracles: list[ModelOracleValue] = []
    for model_index, scenario in enumerate(family.scenarios):
        singleton = fixed_model_family((scenario,))
        singleton_experiments = _singleton_experiments(base.experiments, model_index)
        result = exact_active_fixed_model_experiment_design(
            graph,
            singleton,
            singleton_experiments,
            horizon,
            **solver_caps,
        )
        oracles.append(
            ModelOracleValue(
                model_index,
                scenario.name,
                result.robust_value,
                result.selected_experiment,
            )
        )

    oracle_values = tuple(item.value for item in oracles)
    root_entries = _root_entries(base)
    selected = min(
        root_entries,
        key=lambda entry: _regret_key(entry, oracle_values, base.experiments),
    )
    selected_regrets = _entry_regrets(selected, oracle_values)
    robust_cost_regrets = tuple(
        cost - oracle
        for cost, oracle in zip(base.selected_costs, oracle_values)
    )
    certificate = ActiveExperimentRegretCertificate(
        base,
        tuple(oracles),
        selected.costs,
        selected_regrets,
        max(selected_regrets),
        max(selected.costs),
        selected.selected_experiment,
        robust_cost_regrets,
        max(robust_cost_regrets),
    )
    if not certificate.valid:
        raise AssertionError("active fixed-model regret certificate failed validation")
    return certificate
