"""Two conditionally independent views break the continuous one-view gauge.

For latent prior pi and categorical channel K, two iid observations conditional
on the same latent component have joint law

    T = K^T diag(pi) K.

A one-view gauge K'=AK, pi'=pi A^{-1} always preserves pi K when valid.  If K
has affinely independent probability rows and pi' is strictly positive, then
preserving T as well forces the nonnegative row-stochastic A to be a permutation.
Thus a second shared-latent independent view reduces this gauge orbit to label
switching under the declared finite model.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .latent_mixture_gauge import (
    LatentMixtureGaugeCertificate,
    affine_row_rank,
    exact_latent_mixture_gauge_transform,
)

Matrix = tuple[tuple[Fraction, ...], ...]


def two_view_law(
    prior: Sequence[Fraction], channel: Sequence[Sequence[Fraction]]
) -> Matrix:
    p = tuple(Fraction(v) for v in prior)
    k = tuple(tuple(Fraction(v) for v in row) for row in channel)
    if (
        not p
        or len(p) != len(k)
        or not k[0]
        or any(len(row) != len(k[0]) for row in k)
        or any(v < 0 for v in p)
        or sum(p, Fraction(0)) != 1
        or any(any(v < 0 for v in row) or sum(row, Fraction(0)) != 1 for row in k)
    ):
        raise ValueError("valid prior and categorical channel are required")
    n = len(k[0])
    return tuple(
        tuple(
            sum((p[i] * k[i][a] * k[i][b] for i in range(len(p))), Fraction(0))
            for b in range(n)
        )
        for a in range(n)
    )


def is_permutation_matrix(matrix: Sequence[Sequence[Fraction]]) -> bool:
    a = tuple(tuple(Fraction(v) for v in row) for row in matrix)
    if not a or any(len(row) != len(a) for row in a):
        return False
    n = len(a)
    return (
        all(sum(row, Fraction(0)) == 1 and all(v in (0, 1) for v in row) for row in a)
        and all(sum((a[i][j] for i in range(n)), Fraction(0)) == 1 for j in range(n))
    )


@dataclass(frozen=True)
class TwoViewGaugeCertificate:
    gauge: LatentMixtureGaugeCertificate
    original_two_view: Matrix
    transformed_two_view: Matrix
    two_view_preserved: bool
    full_affine_rank: bool
    transformed_prior_strictly_positive: bool
    permutation_gauge: bool
    rigidity_hypotheses_hold: bool
    rigidity_conclusion_holds: bool

    @property
    def valid(self) -> bool:
        g = self.gauge
        expected_full_rank = g.original_affine_rank == len(g.original_prior) - 1
        expected_positive = all(v > 0 for v in g.transformed_prior)
        expected_permutation = is_permutation_matrix(g.gauge)
        hypotheses = expected_full_rank and expected_positive and self.two_view_preserved
        conclusion = (not hypotheses) or expected_permutation
        return (
            g.valid
            and self.original_two_view == two_view_law(g.original_prior, g.original_channel)
            and self.transformed_two_view == two_view_law(g.transformed_prior, g.transformed_channel)
            and self.two_view_preserved == (self.original_two_view == self.transformed_two_view)
            and self.full_affine_rank == expected_full_rank
            and self.transformed_prior_strictly_positive == expected_positive
            and self.permutation_gauge == expected_permutation
            and self.rigidity_hypotheses_hold == hypotheses
            and self.rigidity_conclusion_holds == conclusion
            and conclusion
        )


def exact_two_view_gauge_certificate(
    prior: Sequence[Fraction],
    channel: Sequence[Sequence[Fraction]],
    gauge: Sequence[Sequence[Fraction]],
) -> TwoViewGaugeCertificate:
    g = exact_latent_mixture_gauge_transform(prior, channel, gauge)
    original = two_view_law(g.original_prior, g.original_channel)
    transformed = two_view_law(g.transformed_prior, g.transformed_channel)
    preserved = original == transformed
    full_rank = affine_row_rank(g.original_channel) == len(g.original_prior) - 1
    positive = all(v > 0 for v in g.transformed_prior)
    permutation = is_permutation_matrix(g.gauge)
    hypotheses = full_rank and positive and preserved
    result = TwoViewGaugeCertificate(
        g,
        original,
        transformed,
        preserved,
        full_rank,
        positive,
        permutation,
        hypotheses,
        (not hypotheses) or permutation,
    )
    if not result.valid:
        raise AssertionError("two-view gauge certificate failed rigidity validation")
    return result
