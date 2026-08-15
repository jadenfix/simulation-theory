"""Exact identifiability and uncertainty amplification for binary latent mixtures.

Each independent unit draws M in {0,1} with P(M=1)=theta, but M need not be
observed.  Instead one categorical emission Y is drawn from row R_M.  The
marginal emission law is Q_theta=(1-theta)R_0+theta R_1.

For any theta,eta,

    TV(Q_theta,Q_eta)=|theta-eta| TV(R_0,R_1).

Thus d=TV(R_0,R_1) is the exact inverse-conditioning coefficient.  If d=0 the
mixing weight is not identifiable from emissions at all.  If d>0, an observed-
law TV error rho implies latent-weight error at most rho/d.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


def _law(values: Sequence[Fraction]) -> tuple[Fraction, ...]:
    p = tuple(Fraction(v) for v in values)
    if not p or any(v < 0 for v in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("emission row must be a probability vector")
    return p


def total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    p, q = _law(left), _law(right)
    if len(p) != len(q):
        raise ValueError("laws must have the same alphabet")
    return sum((abs(a - b) for a, b in zip(p, q)), Fraction(0)) / 2


def binary_mixture_law(theta: Fraction, row0: Sequence[Fraction], row1: Sequence[Fraction]) -> tuple[Fraction, ...]:
    t = Fraction(theta)
    if not 0 <= t <= 1:
        raise ValueError("theta must lie in [0,1]")
    p0, p1 = _law(row0), _law(row1)
    if len(p0) != len(p1):
        raise ValueError("emission rows must share an alphabet")
    return tuple((1 - t) * a + t * b for a, b in zip(p0, p1))


@dataclass(frozen=True)
class BinaryMixtureIdentifiabilityCertificate:
    theta: Fraction
    eta: Fraction
    row_separation: Fraction
    latent_tv: Fraction
    emission_tv: Fraction

    @property
    def valid(self) -> bool:
        return (
            0 <= self.theta <= 1
            and 0 <= self.eta <= 1
            and 0 <= self.row_separation <= 1
            and self.latent_tv == abs(self.theta - self.eta)
            and self.emission_tv == self.latent_tv * self.row_separation
        )


def binary_mixture_identifiability_certificate(
    theta: Fraction,
    eta: Fraction,
    row0: Sequence[Fraction],
    row1: Sequence[Fraction],
) -> BinaryMixtureIdentifiabilityCertificate:
    t, e = Fraction(theta), Fraction(eta)
    q_t = binary_mixture_law(t, row0, row1)
    q_e = binary_mixture_law(e, row0, row1)
    separation = total_variation(row0, row1)
    result = BinaryMixtureIdentifiabilityCertificate(
        t, e, separation, abs(t - e), total_variation(q_t, q_e)
    )
    if not result.valid:
        raise AssertionError("binary latent-mixture identifiability identity failed")
    return result


def latent_radius_from_emission_radius(emission_radius: Fraction, row0: Sequence[Fraction], row1: Sequence[Fraction]) -> Fraction:
    rho = Fraction(emission_radius)
    if not 0 <= rho <= 1:
        raise ValueError("emission radius must lie in [0,1]")
    d = total_variation(row0, row1)
    if d == 0:
        return Fraction(1)
    return min(Fraction(1), rho / d)


def binary_bernoulli_emission_theta(
    observed_one_probability: Fraction,
    row0_one_probability: Fraction,
    row1_one_probability: Fraction,
) -> Fraction:
    """Invert a binary-output mixture exactly when the observed law lies on segment."""
    q = Fraction(observed_one_probability)
    p0 = Fraction(row0_one_probability)
    p1 = Fraction(row1_one_probability)
    if not all(0 <= x <= 1 for x in (q, p0, p1)):
        raise ValueError("Bernoulli probabilities must lie in [0,1]")
    if p0 == p1:
        raise ValueError("identical emission rows do not identify theta")
    theta = (q - p0) / (p1 - p0)
    if not 0 <= theta <= 1:
        raise ValueError("observed emission law lies outside the binary mixture segment")
    return theta


def bernoulli_emission_second_moment_theta_radius(
    success_count: int,
    failure_count: int,
    row0_one_probability: Fraction,
    row1_one_probability: Fraction,
    failure_probability: Fraction = Fraction(1, 20),
) -> tuple[Fraction, Fraction, Fraction]:
    """Return (theta_hat, observed squared radius, latent squared radius).

    For N iid Bernoulli emissions, E[(q_hat-q)^2]<=1/(4N). Markov gives an
    observed-law squared radius 1/(4 N alpha). Division by row separation^2
    transfers it to theta space.  This returns squared radii exactly and avoids
    square roots; callers may round outward on a rational grid if needed.
    """
    s, f = int(success_count), int(failure_count)
    if s < 0 or f < 0 or s + f < 1:
        raise ValueError("nonnegative counts with at least one observation required")
    alpha = Fraction(failure_probability)
    if not 0 < alpha < 1:
        raise ValueError("failure probability must lie in (0,1)")
    q_hat = Fraction(s, s + f)
    theta_hat = binary_bernoulli_emission_theta(q_hat, row0_one_probability, row1_one_probability)
    separation = abs(Fraction(row1_one_probability) - Fraction(row0_one_probability))
    if separation == 0:
        raise ValueError("identical Bernoulli emission rows do not identify theta")
    observed_r2 = Fraction(1, 4 * (s + f)) / alpha
    latent_r2 = observed_r2 / (separation * separation)
    return theta_hat, observed_r2, latent_r2
