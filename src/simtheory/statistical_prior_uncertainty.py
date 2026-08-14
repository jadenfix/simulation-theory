"""Finite-sample calibration of rational TV ambiguity sets from multinomial data.

Geometry and statistical coverage are different claims.  The exact TV and
polyhedral optimizers in this repository assume an ambiguity set is already
given.  This module supplies one conservative way to construct such a set from
i.i.d. categorical observations.

For alphabet size k and empirical law p_hat from n i.i.d. samples, the
Weissman--Ordentlich--Seroussi--Verdu--Weinberger L1 inequality implies the
uniform bound

    Pr(||p_hat - p||_1 >= eps) <= (2^k - 2) exp(-n eps^2 / 2).

Since TV = ||.||_1 / 2,

    Pr(TV(p_hat,p) >= rho) <= (2^k - 2) exp(-2 n rho^2).

Solving the latter for a target failure probability delta gives

    rho >= sqrt(log((2^k-2)/delta)/(2n)).

The logarithm and square root are transcendental in general, so this module does
not label that calculation an exact-rational proof.  Instead it computes at high
Decimal precision and rounds the radius *outward* to a declared rational grid.
The downstream robust optimization is then exact conditional on that rational
radius.

Reference: T. Weissman, E. Ordentlich, G. Seroussi, S. Verdu, M. J. Weinberger,
"Inequalities for the L1 Deviation of the Empirical Distribution," HP Labs
Technical Report HPL-2003-97(R.1), 2003, Theorem 2.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import TVRobustCodeCertificate, exact_tv_robust_prefix_code


def empirical_distribution(counts: Sequence[int]) -> tuple[Fraction, ...]:
    supplied = tuple(int(value) for value in counts)
    if not supplied or any(value < 0 for value in supplied):
        raise ValueError("counts must be nonnegative and nonempty")
    total = sum(supplied)
    if total < 1:
        raise ValueError("at least one observation is required")
    return tuple(Fraction(value, total) for value in supplied)


@dataclass(frozen=True)
class TVConfidenceRadiusCertificate:
    counts: tuple[int, ...]
    empirical_prior: tuple[Fraction, ...]
    failure_probability: Fraction
    alphabet_size: int
    sample_count: int
    prefactor: int
    decimal_precision: int
    rational_denominator: int
    unrounded_radius_decimal: str
    radius: Fraction
    clipped_at_one: bool

    @property
    def valid(self) -> bool:
        return (
            self.alphabet_size == len(self.counts) == len(self.empirical_prior)
            and self.alphabet_size >= 2
            and self.sample_count == sum(self.counts) >= 1
            and self.empirical_prior == empirical_distribution(self.counts)
            and self.prefactor == (1 << self.alphabet_size) - 2
            and 0 < self.failure_probability < 1
            and self.decimal_precision >= 30
            and self.rational_denominator >= 1
            and 0 <= self.radius <= 1
            and self.radius.denominator <= self.rational_denominator
        )


def weissman_tv_confidence_radius(
    counts: Sequence[int],
    failure_probability: Fraction = Fraction(1, 20),
    *,
    rational_denominator: int = 1_000_000,
    decimal_precision: int = 80,
) -> TVConfidenceRadiusCertificate:
    """Return an outward-rounded rational TV radius with finite-sample coverage.

    The coverage statement inherits the assumptions of the cited concentration
    inequality: a fixed finite alphabet and independent identically distributed
    samples from one stationary categorical law.  If those assumptions fail,
    this radius is not a valid confidence guarantee.
    """

    supplied = tuple(int(value) for value in counts)
    empirical = empirical_distribution(supplied)
    k = len(supplied)
    if k < 2:
        raise ValueError("the Weissman prefactor is used here for alphabet size >= 2")
    n = sum(supplied)
    delta = Fraction(failure_probability)
    if not 0 < delta < 1:
        raise ValueError("failure_probability must lie strictly between zero and one")
    denominator = int(rational_denominator)
    precision = int(decimal_precision)
    if denominator < 1 or precision < 30:
        raise ValueError("positive denominator and at least 30 Decimal digits required")
    prefactor = (1 << k) - 2

    with localcontext() as context:
        context.prec = precision
        ratio = Decimal(prefactor) * Decimal(delta.denominator) / Decimal(delta.numerator)
        raw = (ratio.ln() / Decimal(2 * n)).sqrt()
        scaled = (raw * Decimal(denominator)).to_integral_value(rounding=ROUND_CEILING)
        outward = Fraction(int(scaled), denominator)
    clipped = outward > 1
    radius = min(Fraction(1), outward)
    certificate = TVConfidenceRadiusCertificate(
        supplied,
        empirical,
        delta,
        k,
        n,
        prefactor,
        precision,
        denominator,
        str(raw),
        radius,
        clipped,
    )
    if not certificate.valid:
        raise AssertionError("TV confidence-radius certificate failed validation")
    return certificate


@dataclass(frozen=True)
class DataCalibratedTVCodeCertificate:
    confidence: TVConfidenceRadiusCertificate
    robust_code: TVRobustCodeCertificate

    @property
    def valid(self) -> bool:
        return (
            self.confidence.valid
            and self.robust_code.valid
            and self.robust_code.nominal_prior == self.confidence.empirical_prior
            and self.robust_code.radius == self.confidence.radius
        )

    @property
    def robust_length_upper_bound(self) -> Fraction:
        return self.robust_code.robust_value


def exact_data_calibrated_tv_prefix_code(
    graph: ConfusionGraph,
    counts: Sequence[int],
    failure_probability: Fraction = Fraction(1, 20),
    *,
    rational_denominator: int = 1_000_000,
    decimal_precision: int = 80,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
) -> DataCalibratedTVCodeCertificate:
    """Calibrate a TV ball from data, then solve the robust code exactly.

    With probability at least 1-delta under the i.i.d. sampling model, the true
    source law belongs to the calibrated TV ball.  Conditional on that event,
    ``robust_length_upper_bound`` upper-bounds the selected code's true expected
    one-shot prefix length.
    """

    confidence = weissman_tv_confidence_radius(
        counts,
        failure_probability,
        rational_denominator=rational_denominator,
        decimal_precision=decimal_precision,
    )
    if graph.vertex_count != confidence.alphabet_size:
        raise ValueError("graph state count must equal count-vector alphabet size")
    robust = exact_tv_robust_prefix_code(
        graph,
        confidence.empirical_prior,
        confidence.radius,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
    )
    certificate = DataCalibratedTVCodeCertificate(confidence, robust)
    if not certificate.valid:
        raise AssertionError("data-calibrated robust-code certificate failed")
    return certificate
