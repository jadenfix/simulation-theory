"""Exact resource-matched decomposition of active-experiment minimax regret.

The active fixed-model solver permits public observations before deterministic
code actions.  A signal can improve minimax performance for two distinct
reasons: it can reveal information about the globally fixed model/hidden state,
and it can act as source-independent public randomization.  This module keeps
those resources separate.

For a declared experiment menu E, let D(E) be deterministic minimax regret
against the model-informed causal oracle from ``active_fixed_model_regret``.
Let M(E) be the value after additionally allowing an independent public seed to
mix complete deterministic policy trees.  Because expected modelwise costs are
linear in that mixture, M(E) is an exact finite zero-sum game over the already
Pareto-pruned root policy vectors.

Let erase(E) replace every observation kernel by a one-symbol constant channel
while preserving experiment names and acquisition costs.  Both the actual and
erased policy classes are evaluated against the *same oracle vector from E*.
This fixed benchmark is essential: recomputing a weaker oracle after erasing
information would hide some information value inside the benchmark.

The exact identity is

    D(erase(E)) - D(E)
      = [D(erase(E)) - M(erase(E))]
        + [M(erase(E)) - M(E)]
        - [D(E) - M(E)].

The first bracket is coordination value available to an information-erased
controller, the second is information value after public-randomness resources
are matched, and the final bracket is the residual value of extra public
randomness in the actual experiment problem.

All probabilities and costs are exact rational numbers.  The mixed policy game
returns matching exact primal/dual receipts.  These are internal finite decision
results, not empirical evidence for simulation.
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
from .active_fixed_model_regret import (
    ActiveExperimentRegretCertificate,
    exact_active_fixed_model_minimax_regret,
)
from .confusion_graphs import ConfusionGraph
from .fixed_model_ambiguity import FixedModelFamily
from .robust_prior_codes import ExactZeroSumGameCertificate, solve_exact_zero_sum_game
from .stochastic_observation_beliefs import observation_kernel


@dataclass(frozen=True)
class MixedBenchmarkGapCertificate:
    """Exact convexified policy value relative to one fixed benchmark vector."""

    benchmark: tuple[Fraction, ...]
    deterministic_value: Fraction
    mixed_value: Fraction
    game: ExactZeroSumGameCertificate
    policy_costs: tuple[tuple[Fraction, ...], ...]
    policy_gaps: tuple[tuple[Fraction, ...], ...]

    @property
    def valid(self) -> bool:
        if (
            not self.benchmark
            or not self.policy_costs
            or len(self.policy_costs) != len(self.policy_gaps)
            or any(len(costs) != len(self.benchmark) for costs in self.policy_costs)
            or any(len(gaps) != len(self.benchmark) for gaps in self.policy_gaps)
            or self.policy_gaps
            != tuple(
                tuple(cost - base for cost, base in zip(costs, self.benchmark))
                for costs in self.policy_costs
            )
            or any(gap < 0 for gaps in self.policy_gaps for gap in gaps)
            or self.deterministic_value
            != min(max(gaps) for gaps in self.policy_gaps)
            or self.mixed_value != self.game.value
            or self.mixed_value > self.deterministic_value
            or not self.game.valid
        ):
            return False
        expected_matrix = tuple(
            tuple(self.policy_gaps[policy][model] for policy in range(len(self.policy_gaps)))
            for model in range(len(self.benchmark))
        )
        return self.game.cost_matrix == expected_matrix


@dataclass(frozen=True)
class ActiveExperimentRegretDecomposition:
    """Exact deterministic/mixed and information-erased regret decomposition."""

    actual: ActiveExperimentRegretCertificate
    erased: ActiveExperimentCertificate
    erased_experiments: tuple[ActiveExperiment, ...]
    actual_mixed: MixedBenchmarkGapCertificate
    erased_mixed: MixedBenchmarkGapCertificate
    erased_deterministic_gap: Fraction
    actual_deterministic_regret: Fraction
    coordination_gain_erased: Fraction
    information_gain_mixed: Fraction
    residual_randomization_gap_actual: Fraction
    total_deterministic_gain: Fraction
    identity_residual: Fraction

    @property
    def valid(self) -> bool:
        return (
            self.actual.valid
            and self.erased.valid
            and self.actual_mixed.valid
            and self.erased_mixed.valid
            and self.erased_experiments
            and self.actual_mixed.benchmark == self.actual.oracle_values
            and self.erased_mixed.benchmark == self.actual.oracle_values
            and self.actual_deterministic_regret == self.actual.minimax_regret
            and self.actual_mixed.deterministic_value == self.actual.minimax_regret
            and self.erased_deterministic_gap == self.erased_mixed.deterministic_value
            and self.coordination_gain_erased
            == self.erased_deterministic_gap - self.erased_mixed.mixed_value
            and self.information_gain_mixed
            == self.erased_mixed.mixed_value - self.actual_mixed.mixed_value
            and self.residual_randomization_gap_actual
            == self.actual_deterministic_regret - self.actual_mixed.mixed_value
            and self.total_deterministic_gain
            == self.erased_deterministic_gap - self.actual_deterministic_regret
            and self.coordination_gain_erased >= 0
            and self.information_gain_mixed >= 0
            and self.residual_randomization_gap_actual >= 0
            and self.total_deterministic_gain >= 0
            and self.identity_residual == 0
            and self.total_deterministic_gain
            == self.coordination_gain_erased
            + self.information_gain_mixed
            - self.residual_randomization_gap_actual
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


def erase_experiment_information(experiment: ActiveExperiment) -> ActiveExperiment:
    """Replace an experiment by a one-symbol channel with identical cost.

    One row ``(1,)`` is supplied for every hidden state of every model-specific
    kernel.  The result therefore carries neither hidden-state nor model
    information and supplies no endogenous random outcome.
    """

    kernels = tuple(
        observation_kernel(tuple((Fraction(1),) for _ in range(kernel.hidden_state_count)))
        for kernel in experiment.kernels
    )
    return active_experiment(experiment.name, kernels, experiment.acquisition_cost)


def erase_experiment_menu_information(
    experiments: Sequence[ActiveExperiment],
) -> tuple[ActiveExperiment, ...]:
    supplied = tuple(experiments)
    if not supplied:
        raise ValueError("experiment menu cannot be empty")
    return tuple(erase_experiment_information(experiment) for experiment in supplied)


def exact_mixed_benchmark_gap(
    certificate: ActiveExperimentCertificate,
    benchmark: Sequence[Fraction],
    *,
    max_game_bases: int = 2_000_000,
) -> MixedBenchmarkGapCertificate:
    """Convexify a complete deterministic root frontier with a public seed."""

    base = tuple(Fraction(value) for value in benchmark)
    if len(base) != certificate.family.model_count:
        raise ValueError("benchmark length must match fixed-model count")
    entries = _root_entries(certificate)
    costs = tuple(entry.costs for entry in entries)
    gaps = tuple(
        tuple(cost - oracle for cost, oracle in zip(entry.costs, base))
        for entry in entries
    )
    if any(value < 0 for row in gaps for value in row):
        raise ValueError("benchmark is stronger than at least one policy cost coordinate")
    matrix = tuple(
        tuple(gaps[policy][model] for policy in range(len(gaps)))
        for model in range(len(base))
    )
    game = solve_exact_zero_sum_game(matrix, max_bases=max_game_bases)
    result = MixedBenchmarkGapCertificate(
        base,
        min(max(row) for row in gaps),
        game.value,
        game,
        costs,
        gaps,
    )
    if not result.valid:
        raise AssertionError("mixed benchmark-gap certificate failed validation")
    return result


def exact_active_experiment_regret_decomposition(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    experiments: Sequence[ActiveExperiment],
    horizon: int,
    *,
    max_game_bases: int = 2_000_000,
    **solver_caps: int,
) -> ActiveExperimentRegretDecomposition:
    """Separate public-randomness and information contributions exactly."""

    actual = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        experiments,
        horizon,
        **solver_caps,
    )
    erased_experiments = erase_experiment_menu_information(actual.base.experiments)
    erased = exact_active_fixed_model_experiment_design(
        graph,
        family,
        erased_experiments,
        horizon,
        **solver_caps,
    )

    actual_mixed = exact_mixed_benchmark_gap(
        actual.base,
        actual.oracle_values,
        max_game_bases=max_game_bases,
    )
    erased_mixed = exact_mixed_benchmark_gap(
        erased,
        actual.oracle_values,
        max_game_bases=max_game_bases,
    )

    erased_deterministic = erased_mixed.deterministic_value
    actual_deterministic = actual.minimax_regret
    coordination = erased_deterministic - erased_mixed.mixed_value
    information = erased_mixed.mixed_value - actual_mixed.mixed_value
    residual_randomness = actual_deterministic - actual_mixed.mixed_value
    total = erased_deterministic - actual_deterministic
    identity_residual = total - (coordination + information - residual_randomness)

    result = ActiveExperimentRegretDecomposition(
        actual,
        erased,
        erased_experiments,
        actual_mixed,
        erased_mixed,
        erased_deterministic,
        actual_deterministic,
        coordination,
        information,
        residual_randomness,
        total,
        identity_residual,
    )
    if not result.valid:
        raise AssertionError("active-experiment regret decomposition failed validation")
    return result
