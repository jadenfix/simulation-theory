"""Exact dual optimality certificates for total-variation mass transport.

For maximization over a TV ball, all removed non-maximum mass can be placed on
one maximum-value state.  The inner problem therefore reduces to a bounded
fractional knapsack:

    maximize sum_i a_i (f_max - f_i)
    subject to 0 <= a_i <= p_i and sum_i a_i <= rho.

Its exact dual is

    minimize rho * lambda + sum_i p_i * mu_i
    subject to lambda + mu_i >= f_max - f_i,
               lambda >= 0, mu_i >= 0.

Eliminating mu gives the threshold form

    min_{lambda >= 0}
        rho * lambda + sum_i p_i * max(g_i - lambda, 0).

The minimization side is identical after replacing gains by f_i - f_min.
This module derives a rational threshold from the greedy transfer receipt and
checks primal feasibility, dual feasibility, complementary slackness, and zero
rational duality gap.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .distributionally_robust_codes import TVExpectationCertificate


@dataclass(frozen=True)
class TVKnapsackDualCertificate:
    transport: TVExpectationCertificate
    gain_vector: tuple[Fraction, ...]
    removed_mass_by_state: tuple[Fraction, ...]
    threshold: Fraction
    upper_bound_duals: tuple[Fraction, ...]
    primal_gain: Fraction
    dual_gain: Fraction

    @property
    def gap(self) -> Fraction:
        return self.dual_gain - self.primal_gain

    @property
    def budget_slack(self) -> Fraction:
        return self.transport.radius - sum(
            self.removed_mass_by_state,
            Fraction(0),
        )

    @property
    def valid(self) -> bool:
        p = self.transport.nominal_distribution
        count = len(p)
        if (
            not self.transport.valid
            or len(self.gain_vector) != count
            or len(self.removed_mass_by_state) != count
            or len(self.upper_bound_duals) != count
            or self.threshold < 0
            or any(gain < 0 for gain in self.gain_vector)
            or any(mass < 0 for mass in self.removed_mass_by_state)
            or any(
                mass > probability
                for mass, probability in zip(
                    self.removed_mass_by_state,
                    p,
                )
            )
            or any(dual < 0 for dual in self.upper_bound_duals)
            or self.budget_slack < 0
        ):
            return False

        dual_feasible = all(
            self.threshold + dual >= gain
            for gain, dual in zip(
                self.gain_vector,
                self.upper_bound_duals,
            )
        )
        upper_complementarity = all(
            dual * (probability - mass) == 0
            for dual, probability, mass in zip(
                self.upper_bound_duals,
                p,
                self.removed_mass_by_state,
            )
        )
        lower_complementarity = all(
            mass * (self.threshold + dual - gain) == 0
            for mass, dual, gain in zip(
                self.removed_mass_by_state,
                self.upper_bound_duals,
                self.gain_vector,
            )
        )
        budget_complementarity = self.threshold * self.budget_slack == 0
        return (
            dual_feasible
            and upper_complementarity
            and lower_complementarity
            and budget_complementarity
            and self.primal_gain
            == sum(
                (
                    mass * gain
                    for mass, gain in zip(
                        self.removed_mass_by_state,
                        self.gain_vector,
                    )
                ),
                Fraction(0),
            )
            and self.dual_gain
            == self.transport.radius * self.threshold
            + sum(
                (
                    probability * dual
                    for probability, dual in zip(
                        p,
                        self.upper_bound_duals,
                    )
                ),
                Fraction(0),
            )
            and self.gap == 0
        )


def tv_knapsack_dual_certificate(
    transport: TVExpectationCertificate,
) -> TVKnapsackDualCertificate:
    """Build an exact primal-dual receipt from a transport certificate."""

    values = transport.state_values
    extreme_value = max(values) if transport.maximize else min(values)
    gains = tuple(
        extreme_value - value
        if transport.maximize
        else value - extreme_value
        for value in values
    )
    removed = [Fraction(0)] * len(values)
    for transfer in transport.transfers:
        removed[transfer.donor_index] += transfer.mass
    removed_mass = tuple(removed)
    moved = sum(removed_mass, Fraction(0))

    if transport.radius == 0:
        threshold = max(gains)
    elif moved < transport.radius:
        # Every positive-gain donor is exhausted and the objective has
        # saturated, so the TV budget constraint is slack.
        threshold = Fraction(0)
    else:
        active_gains = tuple(
            gain
            for gain, mass in zip(gains, removed_mass)
            if mass > 0
        )
        if not active_gains:
            # A constant value vector has zero gain everywhere.
            threshold = Fraction(0)
        else:
            threshold = min(active_gains)

    upper_duals = tuple(
        max(Fraction(0), gain - threshold)
        for gain in gains
    )
    primal_gain = (
        transport.extremal_expectation - transport.nominal_expectation
        if transport.maximize
        else transport.nominal_expectation - transport.extremal_expectation
    )
    dual_gain = transport.radius * threshold + sum(
        (
            probability * dual
            for probability, dual in zip(
                transport.nominal_distribution,
                upper_duals,
            )
        ),
        Fraction(0),
    )
    certificate = TVKnapsackDualCertificate(
        transport,
        gains,
        removed_mass,
        threshold,
        upper_duals,
        primal_gain,
        dual_gain,
    )
    if not certificate.valid:
        raise AssertionError("TV knapsack primal-dual certificate failed")
    return certificate
