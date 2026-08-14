"""Exact static zero-error prefix coding under bounded source-law drift.

A one-shot ambiguity ball and a changing source law are different models.  This
module considers a path

    q_0 = p,
    TV(q_t, q_{t-1}) <= eta,   t=1,...,T,

and a *single deterministic codebook* that must be used for all T future
periods.  For a fixed state-length vector ``ell``, triangle inequality gives

    TV(q_t,p) <= min(t eta, 1).

The exact TV mass-transport maximizers for one fixed linear objective can be
chosen nested as radius increases.  The repository's deterministic transport
construction has this property: it progressively moves mass from low-length
donors to a maximum-length recipient.  Consequently the pointwise bounds at
radii eta, 2 eta, ... are simultaneously attained by one feasible drift path.
Thus

    sup_path sum_t q_t . ell
      = sum_t sup_{TV(q,p)<=min(t eta,1)} q . ell.

The outer solver enumerates a complete componentwise-undominated deterministic
zero-error code universe by evaluating every code on all simplex-vertex priors.
Componentwise dominance is safe for every source-law path because source
probabilities are nonnegative.

This is a finite-horizon, static-code, rational, one-shot-per-period model.  It
does not model code switching, learning from realized states, or source-law
feedback from the selected codebook.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import (
    TVExpectationCertificate,
    maximize_expectation_tv_ball,
    total_variation_distance,
)
from .prior_weighted_codes import RationalInput, validate_rational_prior
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)
from .statistical_prior_uncertainty import TVConfidenceRadiusCertificate


def _fraction(value: RationalInput | Fraction | int, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _simplex_vertices(state_count: int) -> tuple[tuple[Fraction, ...], ...]:
    n = int(state_count)
    return tuple(
        tuple(Fraction(1) if i == j else Fraction(0) for j in range(n))
        for i in range(n)
    )


@dataclass(frozen=True)
class DriftPathCostCertificate:
    nominal_prior: tuple[Fraction, ...]
    state_lengths: tuple[Fraction, ...]
    drift_per_step: Fraction
    horizon: int
    radii: tuple[Fraction, ...]
    period_certificates: tuple[TVExpectationCertificate, ...]
    extremal_path: tuple[tuple[Fraction, ...], ...]
    cumulative_worst_cost: Fraction

    @property
    def average_worst_cost(self) -> Fraction:
        return self.cumulative_worst_cost / self.horizon

    @property
    def valid(self) -> bool:
        if (
            self.horizon < 1
            or len(self.state_lengths) != len(self.nominal_prior)
            or len(self.radii) != self.horizon
            or len(self.period_certificates) != self.horizon
            or len(self.extremal_path) != self.horizon
            or not 0 <= self.drift_per_step <= 1
        ):
            return False
        expected_radii = tuple(
            min(Fraction(1), self.drift_per_step * t)
            for t in range(1, self.horizon + 1)
        )
        if self.radii != expected_radii:
            return False
        previous = self.nominal_prior
        total = Fraction(0)
        for radius, certificate, distribution in zip(
            self.radii,
            self.period_certificates,
            self.extremal_path,
        ):
            if (
                not certificate.valid
                or not certificate.maximize
                or certificate.nominal_distribution != self.nominal_prior
                or certificate.state_values != self.state_lengths
                or certificate.radius != radius
                or certificate.extremal_distribution != distribution
                or total_variation_distance(previous, distribution) > self.drift_per_step
            ):
                return False
            total += certificate.extremal_expectation
            previous = distribution
        return total == self.cumulative_worst_cost


def exact_drift_path_cost(
    nominal_prior: Sequence[RationalInput],
    state_lengths: Sequence[RationalInput],
    drift_per_step: RationalInput,
    horizon: int,
) -> DriftPathCostCertificate:
    """Return the exact worst cumulative cost for one fixed code under TV drift."""

    prior = validate_rational_prior(nominal_prior)
    lengths = tuple(_fraction(value, name="state length") for value in state_lengths)
    if len(lengths) != len(prior):
        raise ValueError("one state length is required per source state")
    eta = _fraction(drift_per_step, name="drift_per_step")
    if not 0 <= eta <= 1:
        raise ValueError("drift_per_step must lie in [0,1]")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")

    radii = tuple(min(Fraction(1), eta * t) for t in range(1, periods + 1))
    certificates = tuple(
        maximize_expectation_tv_ball(prior, lengths, radius)
        for radius in radii
    )
    path = tuple(certificate.extremal_distribution for certificate in certificates)
    result = DriftPathCostCertificate(
        prior,
        lengths,
        eta,
        periods,
        radii,
        certificates,
        path,
        sum((certificate.extremal_expectation for certificate in certificates), Fraction(0)),
    )
    if not result.valid:
        raise AssertionError(
            "nested TV transport did not reconstruct a feasible exact drift path"
        )
    return result


@dataclass(frozen=True)
class StaticDriftRobustCodeCertificate:
    graph: ConfusionGraph
    nominal_prior: tuple[Fraction, ...]
    drift_per_step: Fraction
    horizon: int
    enumeration: RobustCandidateEnumeration
    candidate_path_costs: tuple[Fraction, ...]
    selected_candidate: RobustCodeCandidate
    selected_path: DriftPathCostCertificate
    nominal_cumulative_optimum: Fraction

    @property
    def robust_cumulative_value(self) -> Fraction:
        return self.selected_path.cumulative_worst_cost

    @property
    def robust_average_value(self) -> Fraction:
        return self.selected_path.average_worst_cost

    @property
    def drift_uplift(self) -> Fraction:
        return self.robust_cumulative_value - self.nominal_cumulative_optimum

    @property
    def valid(self) -> bool:
        candidates = self.enumeration.candidates
        if (
            self.graph.vertex_count != len(self.nominal_prior)
            or self.horizon < 1
            or not candidates
            or len(self.candidate_path_costs) != len(candidates)
            or self.selected_candidate not in candidates
            or not self.selected_path.valid
            or self.selected_path.nominal_prior != self.nominal_prior
            or self.selected_path.drift_per_step != self.drift_per_step
            or self.selected_path.horizon != self.horizon
        ):
            return False
        costs = tuple(
            exact_drift_path_cost(
                self.nominal_prior,
                candidate.scenario_costs,
                self.drift_per_step,
                self.horizon,
            ).cumulative_worst_cost
            for candidate in candidates
        )
        nominal_best = min(
            sum(
                (
                    self.nominal_prior[state] * candidate.scenario_costs[state]
                    for state in range(self.graph.vertex_count)
                ),
                Fraction(0),
            )
            for candidate in candidates
        )
        return (
            costs == self.candidate_path_costs
            and self.robust_cumulative_value == min(costs)
            and self.candidate_path_costs[candidates.index(self.selected_candidate)]
            == self.robust_cumulative_value
            and self.nominal_cumulative_optimum == self.horizon * nominal_best
            and self.drift_uplift >= 0
        )


def exact_static_drift_robust_prefix_code(
    graph: ConfusionGraph,
    nominal_prior: Sequence[RationalInput],
    drift_per_step: RationalInput,
    horizon: int,
    *,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> StaticDriftRobustCodeCertificate:
    """Choose one deterministic zero-error prefix code for a bounded-drift path."""

    prior = validate_rational_prior(nominal_prior)
    if graph.vertex_count != len(prior):
        raise ValueError("graph and nominal prior dimensions differ")
    eta = _fraction(drift_per_step, name="drift_per_step")
    if not 0 <= eta <= 1:
        raise ValueError("drift_per_step must lie in [0,1]")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")

    # Pure-state priors make scenario costs equal the state-length vector.  Any
    # candidate pruned as Pareto dominated here is componentwise no shorter and
    # can never improve expected length under any source-law path.
    enumeration = enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    path_certificates = tuple(
        exact_drift_path_cost(prior, candidate.scenario_costs, eta, periods)
        for candidate in enumeration.candidates
    )
    costs = tuple(certificate.cumulative_worst_cost for certificate in path_certificates)
    best = min(costs)
    index = costs.index(best)
    nominal_best = min(
        sum(
            (
                prior[state] * candidate.scenario_costs[state]
                for state in range(graph.vertex_count)
            ),
            Fraction(0),
        )
        for candidate in enumeration.candidates
    )
    result = StaticDriftRobustCodeCertificate(
        graph,
        prior,
        eta,
        periods,
        enumeration,
        costs,
        enumeration.candidates[index],
        path_certificates[index],
        periods * nominal_best,
    )
    if not result.valid:
        raise AssertionError("static drift-robust prefix-code certificate failed")
    return result


@dataclass(frozen=True)
class DriftInflatedConfidenceRadius:
    statistical_radius: Fraction
    declared_drift_budget: Fraction
    inflated_radius: Fraction
    clipped_at_one: bool

    @property
    def valid(self) -> bool:
        return (
            0 <= self.statistical_radius <= 1
            and 0 <= self.declared_drift_budget <= 1
            and self.inflated_radius
            == min(Fraction(1), self.statistical_radius + self.declared_drift_budget)
            and self.clipped_at_one
            == (self.statistical_radius + self.declared_drift_budget > 1)
        )


def inflate_confidence_radius_for_drift(
    confidence: TVConfidenceRadiusCertificate,
    declared_drift_budget: RationalInput,
) -> DriftInflatedConfidenceRadius:
    """Combine estimation error and declared source drift by TV triangle inequality.

    If, on the confidence event, ``TV(p_hat,p_train)<=r`` and the current law
    satisfies ``TV(p_current,p_train)<=D``, then
    ``TV(p_current,p_hat)<=min(1,r+D)``.
    """

    if not confidence.valid:
        raise ValueError("confidence certificate must be valid")
    drift = _fraction(declared_drift_budget, name="declared_drift_budget")
    if not 0 <= drift <= 1:
        raise ValueError("declared_drift_budget must lie in [0,1]")
    total = confidence.radius + drift
    result = DriftInflatedConfidenceRadius(
        confidence.radius,
        drift,
        min(Fraction(1), total),
        total > 1,
    )
    if not result.valid:
        raise AssertionError("drift-inflated confidence radius failed validation")
    return result
