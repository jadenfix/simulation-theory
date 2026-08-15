"""Exact regret shifts under active-experiment menu expansion.

Adding an experiment cannot worsen the controller's absolute robust cost because
the old menu remains available.  Minimax regret, however, uses a moving
model-informed oracle benchmark.  The oracle may benefit more from the added
experiment than the shared controller, so own-oracle regret need not be
monotone under menu expansion.

This module separates those effects.  For baseline menu B and enriched menu E
with B subset E, let O^B and O^E be the corresponding model-informed oracle
vectors.  The coordinatewise oracle improvement is

    delta_m = O^B_m - O^E_m >= 0.

Evaluate baseline policies against the *enriched* benchmark O^E.  If D_B^E is
the resulting deterministic minimax gap and R_E is enriched own-oracle regret,
then

    gain = D_B^E - R_E >= 0

is the controller improvement under a fixed benchmark.  Baseline own regret R_B
and enriched own regret R_E satisfy

    R_B + min(delta) - gain
      <= R_E <=
    R_B + max(delta) - gain.

When every oracle coordinate improves by the same amount d, the relation is
exact:

    R_E = R_B + d - gain.

The same construction is implemented after convexifying both frontiers with an
independent public seed.  Therefore a richer experiment menu can improve robust
cost while increasing regret, or even leave robust cost unchanged while regret
increases, without any contradiction: the benchmark moved.

All quantities are exact rational finite-horizon decision values, not
statistical estimates and not evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .active_experiment_regret_decomposition import (
    MixedBenchmarkGapCertificate,
    exact_mixed_benchmark_gap,
)
from .active_fixed_model_experiments import ActiveExperiment
from .active_fixed_model_regret import (
    ActiveExperimentRegretCertificate,
    exact_active_fixed_model_minimax_regret,
)
from .confusion_graphs import ConfusionGraph
from .fixed_model_ambiguity import FixedModelFamily


@dataclass(frozen=True)
class ActiveExperimentMenuRegretShift:
    baseline: ActiveExperimentRegretCertificate
    enriched: ActiveExperimentRegretCertificate
    oracle_improvements: tuple[Fraction, ...]
    baseline_under_enriched_benchmark: MixedBenchmarkGapCertificate
    enriched_under_enriched_benchmark: MixedBenchmarkGapCertificate
    baseline_mixed_own: MixedBenchmarkGapCertificate
    enriched_mixed_own: MixedBenchmarkGapCertificate
    deterministic_fixed_benchmark_gain: Fraction
    mixed_fixed_benchmark_gain: Fraction
    deterministic_own_regret_change: Fraction
    mixed_own_regret_change: Fraction
    deterministic_lower_bound: Fraction
    deterministic_upper_bound: Fraction
    mixed_lower_bound: Fraction
    mixed_upper_bound: Fraction
    uniform_oracle_improvement: Fraction | None
    deterministic_uniform_identity_residual: Fraction | None
    mixed_uniform_identity_residual: Fraction | None

    @property
    def valid(self) -> bool:
        if (
            not self.baseline.valid
            or not self.enriched.valid
            or self.baseline.base.family != self.enriched.base.family
            or self.baseline.base.horizon != self.enriched.base.horizon
            or len(self.oracle_improvements) != self.enriched.base.family.model_count
            or any(value < 0 for value in self.oracle_improvements)
            or not self.baseline_under_enriched_benchmark.valid
            or not self.enriched_under_enriched_benchmark.valid
            or not self.baseline_mixed_own.valid
            or not self.enriched_mixed_own.valid
            or self.deterministic_fixed_benchmark_gain < 0
            or self.mixed_fixed_benchmark_gain < 0
            or not (
                self.deterministic_lower_bound
                <= self.enriched.minimax_regret
                <= self.deterministic_upper_bound
            )
            or not (
                self.mixed_lower_bound
                <= self.enriched_mixed_own.mixed_value
                <= self.mixed_upper_bound
            )
            or self.deterministic_own_regret_change
            != self.enriched.minimax_regret - self.baseline.minimax_regret
            or self.mixed_own_regret_change
            != self.enriched_mixed_own.mixed_value - self.baseline_mixed_own.mixed_value
        ):
            return False

        if self.uniform_oracle_improvement is None:
            return (
                self.deterministic_uniform_identity_residual is None
                and self.mixed_uniform_identity_residual is None
            )
        return (
            self.deterministic_uniform_identity_residual == 0
            and self.mixed_uniform_identity_residual == 0
            and self.enriched.minimax_regret
            == self.baseline.minimax_regret
            + self.uniform_oracle_improvement
            - self.deterministic_fixed_benchmark_gain
            and self.enriched_mixed_own.mixed_value
            == self.baseline_mixed_own.mixed_value
            + self.uniform_oracle_improvement
            - self.mixed_fixed_benchmark_gain
        )


def _menu_is_subset(
    baseline: Sequence[ActiveExperiment],
    enriched: Sequence[ActiveExperiment],
) -> bool:
    by_name = {experiment.name: experiment for experiment in enriched}
    return all(by_name.get(experiment.name) == experiment for experiment in baseline)


def exact_active_experiment_menu_regret_shift(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    baseline_experiments: Sequence[ActiveExperiment],
    enriched_experiments: Sequence[ActiveExperiment],
    horizon: int,
    *,
    max_game_bases: int = 2_000_000,
    **solver_caps: int,
) -> ActiveExperimentMenuRegretShift:
    """Compare baseline and enriched menus with moving and fixed benchmarks."""

    baseline_menu = tuple(baseline_experiments)
    enriched_menu = tuple(enriched_experiments)
    if not baseline_menu or not enriched_menu:
        raise ValueError("both experiment menus must be nonempty")
    if not _menu_is_subset(baseline_menu, enriched_menu):
        raise ValueError("baseline experiment menu must be contained in enriched menu")

    baseline = exact_active_fixed_model_minimax_regret(
        graph, family, baseline_menu, horizon, **solver_caps
    )
    enriched = exact_active_fixed_model_minimax_regret(
        graph, family, enriched_menu, horizon, **solver_caps
    )

    delta = tuple(
        old - new
        for old, new in zip(baseline.oracle_values, enriched.oracle_values)
    )
    if any(value < 0 for value in delta):
        raise AssertionError("adding experiments worsened a model-informed oracle")

    baseline_new_benchmark = exact_mixed_benchmark_gap(
        baseline.base,
        enriched.oracle_values,
        max_game_bases=max_game_bases,
    )
    enriched_new_benchmark = exact_mixed_benchmark_gap(
        enriched.base,
        enriched.oracle_values,
        max_game_bases=max_game_bases,
    )
    baseline_mixed_own = exact_mixed_benchmark_gap(
        baseline.base,
        baseline.oracle_values,
        max_game_bases=max_game_bases,
    )
    enriched_mixed_own = enriched_new_benchmark

    det_gain = (
        baseline_new_benchmark.deterministic_value
        - enriched_new_benchmark.deterministic_value
    )
    mix_gain = baseline_new_benchmark.mixed_value - enriched_new_benchmark.mixed_value
    if det_gain < 0 or mix_gain < 0:
        raise AssertionError("menu expansion worsened a fixed-benchmark controller")

    min_delta = min(delta)
    max_delta = max(delta)
    det_lower = baseline.minimax_regret + min_delta - det_gain
    det_upper = baseline.minimax_regret + max_delta - det_gain
    mix_lower = baseline_mixed_own.mixed_value + min_delta - mix_gain
    mix_upper = baseline_mixed_own.mixed_value + max_delta - mix_gain

    uniform = delta[0] if all(value == delta[0] for value in delta) else None
    det_residual = None
    mix_residual = None
    if uniform is not None:
        det_residual = (
            enriched.minimax_regret
            - (baseline.minimax_regret + uniform - det_gain)
        )
        mix_residual = (
            enriched_mixed_own.mixed_value
            - (baseline_mixed_own.mixed_value + uniform - mix_gain)
        )

    certificate = ActiveExperimentMenuRegretShift(
        baseline,
        enriched,
        delta,
        baseline_new_benchmark,
        enriched_new_benchmark,
        baseline_mixed_own,
        enriched_mixed_own,
        det_gain,
        mix_gain,
        enriched.minimax_regret - baseline.minimax_regret,
        enriched_mixed_own.mixed_value - baseline_mixed_own.mixed_value,
        det_lower,
        det_upper,
        mix_lower,
        mix_upper,
        uniform,
        det_residual,
        mix_residual,
    )
    if not certificate.valid:
        raise AssertionError("active-experiment menu regret-shift certificate failed validation")
    return certificate
