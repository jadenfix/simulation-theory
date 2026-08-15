"""Exact-rational confidence calibration from independent latent-model draws.

This module is intentionally narrower than generic multinomial estimation.  It
assumes the observed counts come from N independent units, each of which draws
one latent model M_u independently from the same categorical mixing law pi.
Repeated lower-level observations from one persistent M are not additional
samples for this theorem.

For empirical law p_hat over k categories,

    E ||p_hat-p||_2^2 = (1-||p||_2^2)/N <= (k-1)/(kN).

Since ||v||_1^2 <= k ||v||_2^2 and TV=||.||_1/2,

    E TV(p_hat,p)^2 <= (k-1)/(4N).

Markov therefore gives

    Pr(TV >= rho) <= (k-1)/(4 N rho^2).

A target failure probability alpha is guaranteed whenever

    rho^2 >= (k-1)/(4 N alpha).

The implementation rounds the square root outward on an exact rational grid
using integer arithmetic.  No floating-point or transcendental calculation is
part of the certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import Sequence

from .bayesian_boolean_prior_robustness import (
    gain_ranking_is_tv_robust,
    marginal_gain_interval,
    value_interval,
    value_ranking_is_tv_robust,
)


def empirical_latent_prior(counts: Sequence[int]) -> tuple[Fraction, ...]:
    c = tuple(int(x) for x in counts)
    if len(c) < 2 or any(x < 0 for x in c) or sum(c) < 1:
        raise ValueError("counts require at least two categories and one observation")
    n = sum(c)
    return tuple(Fraction(x, n) for x in c)


def _ceil_sqrt_fraction_on_grid(target: Fraction, denominator: int) -> Fraction:
    """Smallest m/D with (m/D)^2 >= target, clipped only by caller."""
    q = Fraction(target)
    d = int(denominator)
    if q < 0 or d < 1:
        raise ValueError("target must be nonnegative and denominator positive")
    # Need m^2 * q.denominator >= q.numerator * d^2.
    numerator = q.numerator * d * d
    denom = q.denominator
    floor = isqrt(numerator // denom)
    m = floor
    while m * m * denom < numerator:
        m += 1
    while m > 0 and (m - 1) * (m - 1) * denom >= numerator:
        m -= 1
    return Fraction(m, d)


@dataclass(frozen=True)
class IndependentLatentTVConfidence:
    counts: tuple[int, ...]
    empirical_prior: tuple[Fraction, ...]
    sample_count: int
    alphabet_size: int
    failure_probability: Fraction
    raw_squared_radius: Fraction
    grid_denominator: int
    radius: Fraction
    clipped_at_one: bool

    @property
    def valid(self) -> bool:
        return (
            self.sample_count == sum(self.counts) >= 1
            and self.alphabet_size == len(self.counts) == len(self.empirical_prior) >= 2
            and self.empirical_prior == empirical_latent_prior(self.counts)
            and 0 < self.failure_probability < 1
            and self.raw_squared_radius
            == Fraction(self.alphabet_size - 1, 4 * self.sample_count) / self.failure_probability
            and self.grid_denominator >= 1
            and 0 <= self.radius <= 1
            and (self.clipped_at_one or self.radius * self.radius >= self.raw_squared_radius)
        )


def independent_latent_tv_confidence_radius(
    counts: Sequence[int],
    failure_probability: Fraction = Fraction(1, 20),
    *,
    grid_denominator: int = 1_000_000,
) -> IndependentLatentTVConfidence:
    c = tuple(int(x) for x in counts)
    empirical = empirical_latent_prior(c)
    n = sum(c)
    k = len(c)
    alpha = Fraction(failure_probability)
    if not 0 < alpha < 1:
        raise ValueError("failure probability must lie strictly between zero and one")
    raw2 = Fraction(k - 1, 4 * n) / alpha
    outward = _ceil_sqrt_fraction_on_grid(raw2, int(grid_denominator))
    clipped = outward > 1
    radius = min(Fraction(1), outward)
    result = IndependentLatentTVConfidence(c, empirical, n, k, alpha, raw2, int(grid_denominator), radius, clipped)
    if not result.valid:
        raise AssertionError("independent-latent confidence certificate failed")
    return result


@dataclass(frozen=True)
class DataCalibratedBayesianValueBand:
    confidence: IndependentLatentTVConfidence
    nominal_value: Fraction
    interval: tuple[Fraction, Fraction]

    @property
    def valid(self) -> bool:
        return self.confidence.valid and self.interval == value_interval(self.nominal_value, self.confidence.radius)


def data_calibrated_value_band(
    counts: Sequence[int],
    nominal_value: Fraction,
    failure_probability: Fraction = Fraction(1, 20),
    *,
    grid_denominator: int = 1_000_000,
) -> DataCalibratedBayesianValueBand:
    conf = independent_latent_tv_confidence_radius(
        counts, failure_probability, grid_denominator=grid_denominator
    )
    result = DataCalibratedBayesianValueBand(conf, Fraction(nominal_value), value_interval(Fraction(nominal_value), conf.radius))
    if not result.valid:
        raise AssertionError("data-calibrated value band failed validation")
    return result


def data_calibrated_gain_interval(
    counts: Sequence[int],
    nominal_gain: Fraction,
    failure_probability: Fraction = Fraction(1, 20),
    *,
    grid_denominator: int = 1_000_000,
) -> tuple[IndependentLatentTVConfidence, tuple[Fraction, Fraction]]:
    conf = independent_latent_tv_confidence_radius(
        counts, failure_probability, grid_denominator=grid_denominator
    )
    return conf, marginal_gain_interval(Fraction(nominal_gain), conf.radius)


def data_certifies_value_ranking(
    counts: Sequence[int],
    nominal_margin: Fraction,
    failure_probability: Fraction = Fraction(1, 20),
    *,
    grid_denominator: int = 1_000_000,
) -> bool:
    conf = independent_latent_tv_confidence_radius(counts, failure_probability, grid_denominator=grid_denominator)
    return value_ranking_is_tv_robust(Fraction(nominal_margin), conf.radius)


def data_certifies_gain_ranking(
    counts: Sequence[int],
    nominal_margin: Fraction,
    failure_probability: Fraction = Fraction(1, 20),
    *,
    grid_denominator: int = 1_000_000,
) -> bool:
    conf = independent_latent_tv_confidence_radius(counts, failure_probability, grid_denominator=grid_denominator)
    return gain_ranking_is_tv_robust(Fraction(nominal_margin), conf.radius)
