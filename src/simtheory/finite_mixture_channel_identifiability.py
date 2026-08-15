"""Exact affine identifiability certificates for finite latent-mixture channels.

A latent prior ``pi`` over ``m`` components is mapped to an observed categorical
law ``q = pi K``, where rows of ``K`` are component emission laws.  The prior is
identifiable from ``q`` exactly when the channel rows are affinely independent,
equivalently when the ``(m-1)`` row-difference matrix has rank ``m-1``.

If affine rank fails, this module returns two distinct rational priors with
exactly the same observed law.  If affine rank is full, it searches square
coordinate minors, constructs exact rational inverses, and returns the searched
minor with the smallest certified TV reconstruction constant.

The returned conditioning constant is deliberately an auditable upper bound on
the inverse map, not a claim of optimal conditioning.  A later layer can solve
the exact global TV modulus over the zero-sum tangent space.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence


def _channel(rows: Sequence[Sequence[Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
    k = tuple(tuple(Fraction(v) for v in row) for row in rows)
    if len(k) < 2 or not k[0]:
        raise ValueError("channel requires at least two nonempty rows")
    width = len(k[0])
    if any(
        len(row) != width
        or any(v < 0 for v in row)
        or sum(row, Fraction(0)) != 1
        for row in k
    ):
        raise ValueError("channel rows must be probability vectors on one alphabet")
    return k


def _rref(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[tuple[tuple[Fraction, ...], ...], tuple[int, ...]]:
    a = [list(map(Fraction, row)) for row in matrix]
    if not a:
        return (), ()
    cols = len(a[0])
    if any(len(row) != cols for row in a):
        raise ValueError("matrix must be rectangular")
    pivot_cols: list[int] = []
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, len(a)) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [x / pv for x in a[r]]
        for i in range(len(a)):
            if i == r:
                continue
            factor = a[i][c]
            if factor:
                a[i] = [x - factor * y for x, y in zip(a[i], a[r])]
        pivot_cols.append(c)
        r += 1
        if r == len(a):
            break
    return tuple(tuple(row) for row in a), tuple(pivot_cols)


def rational_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    return len(_rref(matrix)[1])


def _inverse(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...] | None:
    a = [list(map(Fraction, row)) for row in matrix]
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("inverse requires a nonempty square matrix")
    aug = [
        row + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(a)
    ]
    for c in range(n):
        pivot = next((i for i in range(c, n) if aug[i][c] != 0), None)
        if pivot is None:
            return None
        aug[c], aug[pivot] = aug[pivot], aug[c]
        pv = aug[c][c]
        aug[c] = [x / pv for x in aug[c]]
        for i in range(n):
            if i == c:
                continue
            factor = aug[i][c]
            if factor:
                aug[i] = [x - factor * y for x, y in zip(aug[i], aug[c])]
    return tuple(tuple(row[n:]) for row in aug)


def _null_vector(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[Fraction, ...] | None:
    """Return one nonzero vector in the right nullspace, if one exists."""

    rows = tuple(tuple(map(Fraction, row)) for row in matrix)
    if not rows:
        return None
    rref, pivots = _rref(rows)
    n = len(rows[0])
    free = next((j for j in range(n) if j not in pivots), None)
    if free is None:
        return None
    x = [Fraction(0)] * n
    x[free] = 1
    for row_index in range(len(pivots) - 1, -1, -1):
        pivot = pivots[row_index]
        x[pivot] = -sum(
            (rref[row_index][j] * x[j] for j in range(pivot + 1, n)),
            Fraction(0),
        )
    result = tuple(x)
    if all(v == 0 for v in result):
        raise AssertionError("constructed null vector is zero")
    return result


def mixture_law(
    prior: Sequence[Fraction],
    channel: Sequence[Sequence[Fraction]],
) -> tuple[Fraction, ...]:
    k = _channel(channel)
    p = tuple(Fraction(v) for v in prior)
    if (
        len(p) != len(k)
        or any(v < 0 for v in p)
        or sum(p, Fraction(0)) != 1
    ):
        raise ValueError("prior must match channel rows and sum to one")
    return tuple(
        sum((p[i] * k[i][j] for i in range(len(k))), Fraction(0))
        for j in range(len(k[0]))
    )


def total_variation(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> Fraction:
    p, q = tuple(map(Fraction, left)), tuple(map(Fraction, right))
    if len(p) != len(q):
        raise ValueError("vectors must have equal length")
    return sum((abs(a - b) for a, b in zip(p, q)), Fraction(0)) / 2


@dataclass(frozen=True)
class CollisionWitness:
    left_prior: tuple[Fraction, ...]
    right_prior: tuple[Fraction, ...]
    common_observed_law: tuple[Fraction, ...]

    @property
    def valid(self) -> bool:
        return (
            self.left_prior != self.right_prior
            and all(v >= 0 for v in self.left_prior + self.right_prior)
            and sum(self.left_prior, Fraction(0)) == 1
            and sum(self.right_prior, Fraction(0)) == 1
            and all(v >= 0 for v in self.common_observed_law)
            and sum(self.common_observed_law, Fraction(0)) == 1
        )


@dataclass(frozen=True)
class ReconstructionCertificate:
    selected_coordinates: tuple[int, ...]
    difference_minor: tuple[tuple[Fraction, ...], ...]
    inverse_minor: tuple[tuple[Fraction, ...], ...]
    full_reconstruction: tuple[tuple[Fraction, ...], ...]
    row_l1_norm: Fraction
    selected_l1_to_tv_factor: Fraction
    tv_conditioning_constant: Fraction

    @property
    def valid(self) -> bool:
        r = len(self.selected_coordinates)
        if (
            r < 1
            or len(self.difference_minor) != r
            or len(self.inverse_minor) != r
            or any(len(row) != r for row in self.difference_minor)
            or any(len(row) != r for row in self.inverse_minor)
        ):
            return False
        identity = tuple(
            tuple(
                sum(
                    (
                        self.difference_minor[i][k]
                        * self.inverse_minor[k][j]
                        for k in range(r)
                    ),
                    Fraction(0),
                )
                for j in range(r)
            )
            for i in range(r)
        )
        expected_identity = tuple(
            tuple(Fraction(int(i == j)) for j in range(r)) for i in range(r)
        )
        expected_full = tuple(
            tuple(self.inverse_minor[i])
            + (-sum(self.inverse_minor[i], Fraction(0)),)
            for i in range(r)
        )
        expected_norm = max(
            sum((abs(v) for v in row), Fraction(0)) for row in expected_full
        )
        # For an observed zero-sum difference z, one selected coordinate has
        # |z_j| <= TV(z), while any >=2 selected coordinates have L1 mass at
        # most 2 TV(z).  This is the only place the min(2,r) factor enters.
        expected_selected_factor = Fraction(min(2, r))
        expected_constant = expected_selected_factor * expected_norm / 2
        return (
            identity == expected_identity
            and self.full_reconstruction == expected_full
            and self.row_l1_norm == expected_norm
            and self.selected_l1_to_tv_factor == expected_selected_factor
            and self.tv_conditioning_constant == expected_constant
            and self.tv_conditioning_constant > 0
        )


@dataclass(frozen=True)
class FiniteMixtureChannelCertificate:
    channel: tuple[tuple[Fraction, ...], ...]
    affine_rank: int
    identifiable: bool
    collision: CollisionWitness | None
    reconstruction: ReconstructionCertificate | None
    minors_examined: int

    @property
    def valid(self) -> bool:
        try:
            k = _channel(self.channel)
        except ValueError:
            return False
        target = len(k) - 1
        reference = k[-1]
        differences = tuple(
            tuple(k[i][j] - reference[j] for j in range(len(reference)))
            for i in range(target)
        )
        if self.affine_rank != rational_rank(differences):
            return False
        if self.identifiable:
            return (
                self.affine_rank == target
                and self.collision is None
                and self.reconstruction is not None
                and self.reconstruction.valid
                and self.minors_examined >= 1
                and all(
                    0 <= coordinate < len(reference)
                    for coordinate in self.reconstruction.selected_coordinates
                )
                and self.reconstruction.difference_minor
                == tuple(
                    tuple(
                        differences[i][j]
                        for j in self.reconstruction.selected_coordinates
                    )
                    for i in range(target)
                )
            )
        if not (
            self.affine_rank < target
            and self.collision is not None
            and self.collision.valid
            and self.reconstruction is None
            and self.minors_examined == 0
        ):
            return False
        try:
            left = mixture_law(self.collision.left_prior, k)
            right = mixture_law(self.collision.right_prior, k)
        except ValueError:
            return False
        return left == right == self.collision.common_observed_law


def exact_finite_mixture_channel_certificate(
    channel: Sequence[Sequence[Fraction]],
    *,
    max_minors: int = 1_000_000,
) -> FiniteMixtureChannelCertificate:
    k = _channel(channel)
    m, n = len(k), len(k[0])
    reference = k[-1]
    differences = tuple(
        tuple(k[i][j] - reference[j] for j in range(n))
        for i in range(m - 1)
    )
    rank = rational_rank(differences)
    target = m - 1

    if rank < target:
        # x * differences = 0 is the right nullspace of differences^T.
        transposed = tuple(
            tuple(differences[i][j] for i in range(target)) for j in range(n)
        )
        x = _null_vector(transposed)
        if x is None:
            raise AssertionError("rank-deficient affine channel had no null witness")
        delta = tuple(x) + (-sum(x, Fraction(0)),)
        uniform = (Fraction(1, m),) * m
        scale = min(Fraction(1, m) / abs(v) for v in delta if v != 0) / 2
        left = tuple(u + scale * d for u, d in zip(uniform, delta))
        right = tuple(u - scale * d for u, d in zip(uniform, delta))
        q_left = mixture_law(left, k)
        q_right = mixture_law(right, k)
        if q_left != q_right:
            raise AssertionError("collision witness does not preserve observed law")
        collision = CollisionWitness(left, right, q_left)
        result = FiniteMixtureChannelCertificate(
            k, rank, False, collision, None, 0
        )
        if not result.valid:
            raise AssertionError("nonidentifiable channel certificate failed validation")
        return result

    minor_count = 0
    best: ReconstructionCertificate | None = None
    for coords in combinations(range(n), target):
        minor_count += 1
        if minor_count > int(max_minors):
            raise ValueError("coordinate-minor search exceeded configured cap")
        a = tuple(
            tuple(differences[i][j] for j in coords) for i in range(target)
        )
        inv = _inverse(a)
        if inv is None:
            continue
        # y = x A, hence x = y A^{-1}.  Append the final zero-sum latent
        # coordinate delta_m = -sum_{i<m} delta_i.
        full = tuple(
            tuple(inv[i]) + (-sum(inv[i], Fraction(0)),)
            for i in range(target)
        )
        row_norm = max(
            sum((abs(v) for v in row), Fraction(0)) for row in full
        )
        selected_factor = Fraction(min(2, target))
        constant = selected_factor * row_norm / 2
        candidate = ReconstructionCertificate(
            tuple(coords),
            a,
            inv,
            full,
            row_norm,
            selected_factor,
            constant,
        )
        if not candidate.valid:
            raise AssertionError("reconstruction candidate failed validation")
        if best is None or (
            candidate.tv_conditioning_constant,
            candidate.selected_coordinates,
        ) < (
            best.tv_conditioning_constant,
            best.selected_coordinates,
        ):
            best = candidate