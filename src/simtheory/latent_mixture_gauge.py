"""Exact observational gauge transformations for latent-mixture factorizations.

If q = pi K and A is an invertible row-stochastic matrix, define

    K'  = A K,
    pi' = pi A^{-1}.

Whenever pi' remains nonnegative, (pi',K') is another valid latent-mixture
factorization of exactly the same observed law.  Non-permutation gauges can
therefore change both mixing weights and component emission rows without
changing any one-view observational distribution.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]


def _matrix(rows: Sequence[Sequence[Fraction]]) -> Matrix:
    a = tuple(tuple(Fraction(v) for v in row) for row in rows)
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError("matrix must be nonempty and rectangular")
    return a


def _inverse(matrix: Matrix) -> Matrix | None:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("inverse requires a square matrix")
    aug = [
        list(row) + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for c in range(n):
        pivot = next((i for i in range(c, n) if aug[i][c]), None)
        if pivot is None:
            return None
        aug[c], aug[pivot] = aug[pivot], aug[c]
        scale = aug[c][c]
        aug[c] = [v / scale for v in aug[c]]
        for i in range(n):
            if i != c and aug[i][c]:
                scale = aug[i][c]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[c])]
    return tuple(tuple(row[n:]) for row in aug)


def _matmul(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not align")
    return tuple(
        tuple(
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        )
        for i in range(len(left))
    )


def _row_times(row: Vector, matrix: Matrix) -> Vector:
    if len(row) != len(matrix):
        raise ValueError("row and matrix dimensions do not align")
    return tuple(
        sum((row[i] * matrix[i][j] for i in range(len(row))), Fraction(0))
        for j in range(len(matrix[0]))
    )


def _rank(matrix: Matrix) -> int:
    a = [list(row) for row in matrix]
    rows, cols = len(a), len(a[0])
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][c]
        a[r] = [v / scale for v in a[r]]
        for i in range(rows):
            if i != r and a[i][c]:
                scale = a[i][c]
                a[i] = [x - scale * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == rows:
            break
    return r


def _prior(values: Sequence[Fraction]) -> Vector:
    p = tuple(Fraction(v) for v in values)
    if not p or any(v < 0 for v in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("prior must be a probability vector")
    return p


def _channel(rows: Sequence[Sequence[Fraction]]) -> Matrix:
    k = _matrix(rows)
    if any(any(v < 0 for v in row) or sum(row, Fraction(0)) != 1 for row in k):
        raise ValueError("channel rows must be probability vectors")
    return k


def _row_stochastic(rows: Sequence[Sequence[Fraction]]) -> Matrix:
    a = _matrix(rows)
    if len(a) != len(a[0]) or any(
        any(v < 0 for v in row) or sum(row, Fraction(0)) != 1 for row in a
    ):
        raise ValueError("gauge must be square and row-stochastic")
    return a


def observed_law(prior: Sequence[Fraction], channel: Sequence[Sequence[Fraction]]) -> Vector:
    p, k = _prior(prior), _channel(channel)
    if len(p) != len(k):
        raise ValueError("prior length must match channel rows")
    return _row_times(p, k)


def affine_row_rank(channel: Sequence[Sequence[Fraction]]) -> int:
    k = _channel(channel)
    augmented = tuple(tuple(row) + (Fraction(1),) for row in k)
    return _rank(augmented) - 1


@dataclass(frozen=True)
class LatentMixtureGaugeCertificate:
    original_prior: Vector
    original_channel: Matrix
    gauge: Matrix
    gauge_inverse: Matrix
    transformed_prior: Vector
    transformed_channel: Matrix
    common_observed_law: Vector
    original_affine_rank: int
    transformed_affine_rank: int

    @property
    def nontrivial(self) -> bool:
        return (
            self.original_prior != self.transformed_prior
            or self.original_channel != self.transformed_channel
        )

    @property
    def valid(self) -> bool:
        try:
            p = _prior(self.original_prior)
            k = _channel(self.original_channel)
            a = _row_stochastic(self.gauge)
            p2 = _prior(self.transformed_prior)
            k2 = _channel(self.transformed_channel)
        except ValueError:
            return False
        if len(p) != len(k) or len(a) != len(k) or len(p2) != len(k2):
            return False
        inv = _inverse(a)
        if inv is None or inv != self.gauge_inverse:
            return False
        identity = tuple(
            tuple(Fraction(int(i == j)) for j in range(len(a)))
            for i in range(len(a))
        )
        return (
            _matmul(a, inv) == identity
            and self.transformed_channel == _matmul(a, k)
            and self.transformed_prior == _row_times(p, inv)
            and self.common_observed_law == observed_law(p, k)
            and self.common_observed_law == observed_law(p2, k2)
            and self.original_affine_rank == affine_row_rank(k)
            and self.transformed_affine_rank == affine_row_rank(k2)
            and self.original_affine_rank == self.transformed_affine_rank
        )


def exact_latent_mixture_gauge_transform(
    prior: Sequence[Fraction],
    channel: Sequence[Sequence[Fraction]],
    gauge: Sequence[Sequence[Fraction]],
) -> LatentMixtureGaugeCertificate:
    p, k, a = _prior(prior), _channel(channel), _row_stochastic(gauge)
    if len(p) != len(k) or len(a) != len(k):
        raise ValueError("prior, channel, and gauge latent dimensions must match")
    inv = _inverse(a)
    if inv is None:
        raise ValueError("gauge must be invertible")
    p2 = _row_times(p, inv)
    if any(v < 0 for v in p2):
        raise ValueError("transformed prior leaves the probability simplex")
    k2 = _matmul(a, k)
    result = LatentMixtureGaugeCertificate(
        p,
        k,
        a,
        inv,
        p2,
        k2,
        observed_law(p, k),
        affine_row_rank(k),
        affine_row_rank(k2),
    )
    if not result.valid:
        raise AssertionError("latent-mixture gauge certificate failed validation")
    return result
