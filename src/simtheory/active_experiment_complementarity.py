"""Exact complementarity of active experiments under a fixed oracle benchmark.

A common heuristic in experiment design is that information should exhibit
'diminishing returns': after one experiment is available, a second experiment
should become no more valuable than it was initially.  This module shows that
such submodularity is not automatic in finite active fixed-model coding.

The comparison deliberately fixes one benchmark.  Given a baseline experiment
menu B and two additional experiments a,b, first solve the full menu B+{a,b}
and use its model-informed causal oracle vector O for every comparison.  Then
solve four controller policy classes: B, B+a, B+b, and B+a+b.  Each class is
evaluated against that same O, both deterministically and after convexification
by an independent public seed.

For a value V(S) interpreted as minimax benchmark gap, the gain from adding b is

    gain_b(S) = V(S) - V(S union {b}).

Diminishing returns would require gain_b(B) >= gain_b(B+a).  Complementarity is
the reverse inequality.  Equivalently, the cost-form submodularity slack

    V(B+a) + V(B+b) - V(B) - V(B+a+b)

is negative exactly when the two experiments are complementary.

The bounded K3 construction in the tests uses four persistent fixed models
encoding two latent bits.  Either bit experiment alone leaves two possible
future source symbols; both together identify the future symbol.  The strict
complementarity remains after public-randomness resources are matched, so it is
not an artifact of deterministic coordination restrictions.

All probabilities and costs are exact rational numbers.  These are internal
finite decision results, not empirical evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .active_experiment_regret_decomposition import (
    MixedBenchmarkGapCertificate,
    exact_mixed_benchmark_gap,
)
from .active_fixed_model_experiments import (
    ActiveExperiment,
    ActiveExperimentCertificate,
    exact_active_fixed_model_experiment_design,
)
from .active_fixed_model_regret import exact_active_fixed_model_minimax_regret
from .confusion_graphs import ConfusionGraph
from .fixed_model_ambiguity import FixedModelFamily


@dataclass(frozen=True)
class FixedBenchmarkMenuValue:
    experiments: tuple[ActiveExperiment, ...]
    deterministic: ActiveExperimentCertificate
    mixed: MixedBenchmarkGapCertificate
    deterministic_gap: Fraction
    mixed_gap: Fraction

    @property
    def valid(self) -> bool:
        return (
            bool(self.experiments)
            and self.deterministic.valid
            and self.mixed.valid
            and self.deterministic_gap == self.mixed.deterministic_value
            and self.mixed_gap == self.mixed.mixed_value
            and self.mixed_gap <= self.deterministic_gap
        )


@dataclass(frozen=True)
class ActiveExperimentComplementarityCertificate:
    benchmark: tuple[Fraction, ...]
    baseline: FixedBenchmarkMenuValue
    with_a: FixedBenchmarkMenuValue
    with_b: FixedBenchmarkMenuValue
    with_both: FixedBenchmarkMenuValue
    experiment_a: str
    experiment_b: str
    deterministic_gain_b_empty: Fraction
    deterministic_gain_b_after_a: Fraction
    deterministic_complementarity: Fraction
    deterministic_submodularity_slack: Fraction
    mixed_gain_b_empty: Fraction
    mixed_gain_b_after_a: Fraction
    mixed_complementarity: Fraction
    mixed_submodularity_slack: Fraction

    @property
    def valid(self) -> bool:
        menus = (self.baseline, self.with_a, self.with_b, self.with_both)
        if (
            not self.benchmark
            or any(not value.valid for value in menus)
            or not self.experiment_a
            or not self.experiment_b
            or self.experiment_a == self.experiment_b
            or self.deterministic_gain_b_empty
            != self.baseline.deterministic_gap - self.with_b.deterministic_gap
            or self.deterministic_gain_b_after_a
            != self.with_a.deterministic_gap - self.with_both.deterministic_gap
            or self.deterministic_complementarity
            != self.deterministic_gain_b_after_a - self.deterministic_gain_b_empty
            or self.deterministic_submodularity_slack
            != -self.deterministic_complementarity
            or self.mixed_gain_b_empty
            != self.baseline.mixed_gap - self.with_b.mixed_gap
            or self.mixed_gain_b_after_a
            != self.with_a.mixed_gap - self.with_both.mixed_gap
            or self.mixed_complementarity
            != self.mixed_gain_b_after_a - self.mixed_gain_b_empty
            or self.mixed_submodularity_slack
            != -self.mixed_complementarity
        ):
            return False
        # Menu inclusion means controller value cannot worsen when an experiment
        # is added under the fixed benchmark.
        return (
            self.baseline.deterministic_gap >= self.with_a.deterministic_gap
            and self.baseline.deterministic_gap >= self.with_b.deterministic_gap
            and self.with_a.deterministic_gap >= self.with_both.deterministic_gap
            and self.with_b.deterministic_gap >= self.with_both.deterministic_gap
            and self.baseline.mixed_gap >= self.with_a.mixed_gap
            and self.baseline.mixed_gap >= self.with_b.mixed_gap
            and self.with_a.mixed_gap >= self.with_both.mixed_gap
            and self.with_b.mixed_gap >= self.with_both.mixed_gap
        )


def _append_unique(
    baseline: Sequence[ActiveExperiment],
    additions: Sequence[ActiveExperiment],
) -> tuple[ActiveExperiment, ...]:
    result = list(baseline)
    names = {experiment.name for experiment in result}
    if len(names) != len(result):
        raise ValueError("baseline experiment names must be unique")
    for experiment in additions:
        if experiment.name in names:
            raise ValueError("candidate experiment name already appears in menu")
        result.append(experiment)
        names.add(experiment.name)
    return tuple(result)


def _fixed_benchmark_value(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    experiments: Sequence[ActiveExperiment],
    horizon: int,
    benchmark: Sequence[Fraction],
    *,
    max_game_bases: int,
    solver_caps: dict[str, int],
) -> FixedBenchmarkMenuValue:
    deterministic = exact_active_fixed_model_experiment_design(
        graph,
        family,
        experiments,
        horizon,
        **solver_caps,
    )
    mixed = exact_mixed_benchmark_gap(
        deterministic,
        benchmark,
        max_game_bases=max_game_bases,
    )
    result = FixedBenchmarkMenuValue(
        tuple(experiments),
        deterministic,
        mixed,
        mixed.deterministic_value,
        mixed.mixed_value,
    )
    if not result.valid:
        raise AssertionError("fixed-benchmark menu value failed validation")
    return result


def exact_active_experiment_complementarity(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    baseline_experiments: Sequence[ActiveExperiment],
    experiment_a: ActiveExperiment,
    experiment_b: ActiveExperiment,
    horizon: int,
    *,
    max_game_bases: int = 2_000_000,
    **solver_caps: int,
) -> ActiveExperimentComplementarityCertificate:
    """Compute exact deterministic and public-mixed complementarity.

    The benchmark is the model-informed causal oracle vector under the full
    menu.  Holding it fixed across all four controller classes removes moving-
    oracle effects from the complementarity calculation.
    """

    baseline = tuple(baseline_experiments)
    if not baseline:
        raise ValueError("baseline experiment menu cannot be empty")
    menu_a = _append_unique(baseline, (experiment_a,))
    menu_b = _append_unique(baseline, (experiment_b,))
    menu_both = _append_unique(baseline, (experiment_a, experiment_b))

    full_regret = exact_active_fixed_model_minimax_regret(
        graph,
        family,
        menu_both,
        horizon,
        **solver_caps,
    )
    benchmark = full_regret.oracle_values
    caps = dict(solver_caps)

    v0 = _fixed_benchmark_value(
        graph, family, baseline, horizon, benchmark,
        max_game_bases=max_game_bases, solver_caps=caps
    )
    va = _fixed_benchmark_value(
        graph, family, menu_a, horizon, benchmark,
        max_game_bases=max_game_bases, solver_caps=caps
    )
    vb = _fixed_benchmark_value(
        graph, family, menu_b, horizon, benchmark,
        max_game_bases=max_game_bases, solver_caps=caps
    )
    vab = FixedBenchmarkMenuValue(
        menu_both,
        full_regret.base,
        exact_mixed_benchmark_gap(
            full_regret.base, benchmark, max_game_bases=max_game_bases
        ),
        full_regret.minimax_regret,
        Fraction(0),
    )
    # Use the mixed game's actual value rather than assuming it is zero.
    vab = FixedBenchmarkMenuValue(
        menu_both,
        full_regret.base,
        vab.mixed,
        vab.mixed.deterministic_value,
        vab.mixed.mixed_value,
    )
    if not vab.valid:
        raise AssertionError("full-menu fixed benchmark value failed validation")

    det_b0 = v0.deterministic_gap - vb.deterministic_gap
    det_ba = va.deterministic_gap - vab.deterministic_gap
    det_comp = det_ba - det_b0
    mix_b0 = v0.mixed_gap - vb.mixed_gap
    mix_ba = va.mixed_gap - vab.mixed_gap
    mix_comp = mix_ba - mix_b0

    certificate = ActiveExperimentComplementarityCertificate(
        tuple(benchmark),
        v0,
        va,
        vb,
        vab,
        experiment_a.name,
        experiment_b.name,
        det_b0,
        det_ba,
        det_comp,
        -det_comp,
        mix_b0,
        mix_ba,
        mix_comp,
        -mix_comp,
    )
    if not certificate.valid:
        raise AssertionError("active-experiment complementarity certificate failed validation")
    return certificate
