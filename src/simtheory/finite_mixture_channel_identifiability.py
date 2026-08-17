"""Exact affine identifiability certificates for finite latent-mixture channels.

A prior ``pi`` over ``m`` latent components produces observed law ``q = pi K``.
The prior is identifiable from ``q`` iff the rows of the categorical channel
``K`` are affinely independent.  This module proves either side constructively:
rank failure returns two distinct rational priors with the same observed law;
full affine rank returns an exact coordinate-minor inverse and an auditable TV
conditioning bound.

The coordinate-minor bound is a certified upper bound on inverse sensitivity,
not a claim that the chosen inverse is globally TV-optimal.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence

Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]


def _channel(rows: Sequence[Sequence[Fraction]]) -> Matrix:
    k = tuple(tuple(Fraction(v) for v in row) for row in rows)
    if len(k) < 2 or not k[0]:
        raise ValueError("channel requires at least two nonempty rows")
    n = len(k[0])
    if any(
        len(row) != n
        or any(v < 0 for v in row)
        or sum(row, Fraction(0)) != 1
        for row in k
    ):
        raise ValueError("channel rows must be probability vectors on one alphabet")
    return k


def _rref(matrix: Sequence[Sequence[Fraction]]) -> tuple[Matrix, tuple[int, ...]]:
    a = [list(map(Fraction, row)) for row in matrix]
    if not a:
        return (), ()
    n = len(a[0])
    if any(len(row) != n for row in a):
        raise ValueError("matrix must be rectangular")
    pivots: list[int] = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][c]
        a[r] = [x / scale for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][c]:
                scale = a[i][c]
                a[i] = [x - scale * y for x, y in zip(a[i], a[r])]
        pivots.append(c)
        r += 1
        if r == len(a):
            break
    return tuple(tuple(row) for row in a), tuple(pivots)


def rational_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    return len(_rref(matrix)[1])


def _inverse(matrix: Sequence[Sequence[Fraction]]) -> Matrix | None:
    a = [list(map(Fraction, row)) for row in matrix]
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("inverse requires a nonempty square matrix")
    aug = [
        row + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(a)
    ]
    for c in range(n):
        pivot = next((i for i in range(c, n) if aug[i][c]), None)
        if pivot is None:
            return None
        aug[c], aug[pivot] = aug[pivot], aug[c]
        scale = aug[c][c]
        aug[c] = [x / scale for x in aug[c]]
        for i in range(n):
            if i != c and aug[i][c]:
                scale = aug[i][c]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[c])]
    return tuple(tuple(row[n:]) for row in aug)


def _right_null_vector(matrix: Sequence[Sequence[Fraction]]) -> Vector | None:
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
    for i in range(len(pivots) - 1, -1, -1):
        p = pivots[i]
        x[p] = -sum((rref[i][j] * x[j] for j in range(p + 1, n)), Fraction(0))
    return tuple(x)


def mixture_law(prior: Sequence[Fraction], channel: Sequence[Sequence[Fraction]]) -> Vector:
    k = _channel(channel)
    p = tuple(Fraction(v) for v in prior)
    if len(p) != len(k) or any(v < 0 for v in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("prior must match channel rows and sum to one")
    return tuple(
        sum((p[i] * k[i][j] for i in range(len(k))), Fraction(0))
        for j in range(len(k[0]))
    )


def total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    p, q = tuple(map(Fraction, left)), tuple(map(Fraction, right))
    if len(p) != len(q):
        raise ValueError("vectors must have equal length")
    return sum((abs(a - b) for a, b in zip(p, q)), Fraction(0)) / 2


def _difference_matrix(k: Matrix) -> Matrix:
    ref = k[-1]
    return tuple(
        tuple(k[i][j] - ref[j] for j in range(len(ref)))
        for i in range(len(k) - 1)
    )


@dataclass(frozen=True)
class CollisionWitness:
    left_prior: Vector
    right_prior: Vector
    common_observed_law: Vector


@dataclass(frozen=True)
class ReconstructionCertificate:
    selected_coordinates: tuple[int, ...]
    difference_minor: Matrix
    inverse_minor: Matrix
    full_reconstruction: Matrix
    row_l1_norm: Fraction
    selected_l1_to_tv_factor: Fraction
    tv_conditioning_constant: Fraction


@dataclass(frozen=True)
class FiniteMixtureChannelCertificate:
    channel: Matrix
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
        d = _difference_matrix(k)
        target = len(k) - 1
        if self.affine_rank != rational_rank(d):
            return False
        if not self.identifiable:
            if not (
                self.affine_rank < target
                and self.collision is not None
                and self.reconstruction is None
                and self.minors_examined == 0
            ):
                return False
            c = self.collision
            try:
                left = mixture_law(c.left_prior, k)
                right = mixture_law(c.right_prior, k)
            except ValueError:
                return False
            return c.left_prior != c.right_prior and left == right == c.common_observed_law

        r = self.reconstruction
        if not (
            self.affine_rank == target
            and self.collision is None
            and r is not None
            and self.minors_examined >= 1
            and len(r.selected_coordinates) == target
            and len(set(r.selected_coordinates)) == target
            and all(0 <= j < len(k[0]) for j in r.selected_coordinates)
        ):
            return False
        expected_minor = tuple(
            tuple(d[i][j] for j in r.selected_coordinates) for i in range(target)
        )
        if r.difference_minor != expected_minor:
            return False
        inv = _inverse(expected_minor)
        if inv is None or r.inverse_minor != inv:
            return False
        expected_full = tuple(
            tuple(inv[i]) + (-sum(inv[i], Fraction(0)),)
            for i in range(target)
        )
        expected_norm = max(
            sum((abs(v) for v in row), Fraction(0)) for row in expected_full
        )
        # If one coordinate is selected, |z_j| <= TV(z).  For two or more,
        # selected L1 mass is at most the full L1 mass = 2 TV(z).
        expected_factor = Fraction(min(2, target))
        return (
            r.full_reconstruction == expected_full
            and r.row_l1_norm == expected_norm
            and r.selected_l1_to_tv_factor == expected_factor
            and r.tv_conditioning_constant == expected_factor * expected_norm / 2
            and r.tv_conditioning_constant > 0
        )


def exact_finite_mixture_channel_certificate(
    channel: Sequence[Sequence[Fraction]], *, max_minors: int = 1_000_000
) -> FiniteMixtureChannelCertificate:
    k = _channel(channel)
    m, n = len(k), len(k[0])
    d = _difference_matrix(k)
    target = m - 1
    rank = rational_rank(d)

    if rank < target:
        # x D = 0 iff D^T x^T = 0.  Append the final coordinate so the full
        # latent perturbation sums to zero, then move symmetrically around the
        # interior uniform prior to obtain two valid colliding priors.
        dt = tuple(tuple(d[i][j] for i in range(target)) for j in range(n))
        x = _right_null_vector(dt)
        if x is None:
            raise AssertionError("rank-deficient channel had no null witness")
        delta = tuple(x) + (-sum(x, Fraction(0)),)
        uniform = (Fraction(1, m),) * m
        scale = min(Fraction(1, m) / abs(v) for v in delta if v) / 2
        left = tuple(u + scale * v for u, v in zip(uniform, delta))
        right = tuple(u - scale * v for u, v in zip(uniform, delta))
        q_left, q_right = mixture_law(left, k), mixture_law(right, k)
        if q_left != q_right:
            raise AssertionError("constructed collision does not preserve observed law")
        result = FiniteMixtureChannelCertificate(
            k, rank, False, CollisionWitness(left, right, q_left), None, 0
        )
        if not result.valid:
            raise AssertionError("nonidentifiable certificate failed validation")
        return result

    examined = 0
    best: ReconstructionCertificate | None = None
    for coords in combinations(range(n), target):
        examined += 1
        if examined > int(max_minors):
            raise ValueError("coordinate-minor search exceeded configured cap")
        minor = tuple(tuple(d[i][j] for j in coords) for i in range(target))
        inv = _inverse(minor)
        if inv is None:
            continue
        full = tuple(
            tuple(inv[i]) + (-sum(inv[i], Fraction(0)),)
            for i in range(target)
        )
        row_norm = max(sum((abs(v) for v in row), Fraction(0)) for row in full)
        factor = Fraction(min(2, target))
        candidate = ReconstructionCertificate(
            tuple(coords), minor, inv, full, row_norm, factor, factor * row_norm / 2
        )
        if best is None or (
            candidate.tv_conditioning_constant,
            candidate.selected_coordinates,
        ) < (best.tv_conditioning_constant, best.selected_coordinates):
            best = candidate
    if best is None:
        raise AssertionError("full affine rank but no invertible coordinate minor")
    result = FiniteMixtureChannelCertificate(k, rank, True, None, best, examined)
    if not result.valid:
        raise AssertionError("identifiable certificate failed validation")
    return result


def reconstruct_latent_difference(
    observed_difference: Sequence[Fraction],
    certificate: FiniteMixtureChannelCertificate,
) -> Vector:
    """Invert an observed difference known to lie in the channel tangent image."""

    if not certificate.valid or not certificate.identifiable:
        raise ValueError("an identifiable channel certificate is required")
    z = tuple(Fraction(v) for v in observed_difference)
    if len(z) != len(certificate.channel[0]) or sum(z, Fraction(0)) != 0:
        raise ValueError("observed difference must match the alphabet and sum to zero")
    r = certificate.reconstruction
    assert r is not None
    y = tuple(z[j] for j in r.selected_coordinates)
    x = tuple(
        sum((y[i] * r.inverse_minor[i][j] for i in range(len(y))), Fraction(0))
        for j in range(len(y))
    )
    return x + (-sum(x, Fraction(0)),)


def certified_latent_tv_radius(
    observed_tv_radius: Fraction,
    certificate: FiniteMixtureChannelCertificate,
) -> Fraction:
    rho = Fraction(observed_tv_radius)
    if not 0 <= rho <= 1 or not certificate.valid:
        raise ValueError("invalid radius or channel certificate")
    if not certificate.identifiable:
        return Fraction(1)
    assert certificate.reconstruction is not None
    return min(Fraction(1), certificate.reconstruction.tv_conditioning_constant * rho)
