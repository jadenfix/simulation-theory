"""Exact global total-variation conditioning for finite latent-mixture channels.

For channel rows K_i and zero-sum latent perturbation delta, define

    alpha(K) = inf TV(delta K) / TV(delta).

Normalizing TV(delta)=1 decomposes delta into disjoint-support probability
vectors u-v.  Therefore alpha is the minimum TV distance between convex hulls
of disjoint nonempty row subsets.  For each face pair this distance is solved as
an exact finite zero-sum game using TV(p,q)=max_A[p(A)-q(A)].

This layer computes the globally optimal inverse modulus C*=1/alpha when alpha
is positive, rather than the conservative coordinate-minor bound of the affine
identifiability layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Sequence

from .finite_mixture_channel_identifiability import (
    FiniteMixtureChannelCertificate,
    exact_finite_mixture_channel_certificate,
    mixture_law,
    total_variation,
)
from .robust_prior_codes import ExactZeroSumGameCertificate, solve_exact_zero_sum_game


@dataclass(frozen=True)
class DisjointFaceSeparationCertificate:
    positive_indices: tuple[int, ...]
    negative_indices: tuple[int, ...]
    pair_actions: tuple[tuple[int, int], ...]
    events: tuple[tuple[int, ...], ...]
    game: ExactZeroSumGameCertificate
    positive_prior: tuple[Fraction, ...]
    negative_prior: tuple[Fraction, ...]
    positive_observed_law: tuple[Fraction, ...]
    negative_observed_law: tuple[Fraction, ...]
    separation: Fraction

    @property
    def valid(self) -> bool:
        m = len(self.positive_prior)
        if (
            not self.positive_indices
            or not self.negative_indices
            or set(self.positive_indices) & set(self.negative_indices)
            or len(self.negative_prior) != m
            or any(v < 0 for v in self.positive_prior + self.negative_prior)
            or sum(self.positive_prior, Fraction(0)) != 1
            or sum(self.negative_prior, Fraction(0)) != 1
            or any(self.positive_prior[i] != 0 for i in range(m) if i not in self.positive_indices)
            or any(self.negative_prior[i] != 0 for i in range(m) if i not in self.negative_indices)
            or self.pair_actions
            != tuple((i, j) for i in self.positive_indices for j in self.negative_indices)
            or not self.game.valid
            or len(self.game.code_mixture) != len(self.pair_actions)
            or self.separation != self.game.value
            or self.separation
            != total_variation(self.positive_observed_law, self.negative_observed_law)
        ):
            return False
        left = [Fraction(0)] * m
        right = [Fraction(0)] * m
        for weight, (i, j) in zip(self.game.code_mixture, self.pair_actions):
            left[i] += weight
            right[j] += weight
        return tuple(left) == self.positive_prior and tuple(right) == self.negative_prior


@dataclass(frozen=True)
class GlobalTVModulusCertificate:
    affine: FiniteMixtureChannelCertificate
    face_certificates: tuple[DisjointFaceSeparationCertificate, ...]
    alpha: Fraction
    optimal_inverse_constant: Fraction | None
    minimizing_face_index: int
    event_count: int
    face_pair_count: int

    @property
    def valid(self) -> bool:
        if (
            not self.affine.valid
            or not self.face_certificates
            or any(not face.valid for face in self.face_certificates)
            or self.face_pair_count != len(self.face_certificates)
            or not 0 <= self.minimizing_face_index < len(self.face_certificates)
        ):
            return False
        values = tuple(face.separation for face in self.face_certificates)
        if self.alpha != min(values) or self.alpha != values[self.minimizing_face_index]:
            return False
        if self.affine.identifiable:
            if self.alpha <= 0 or self.optimal_inverse_constant != 1 / self.alpha:
                return False
            assert self.affine.reconstruction is not None
            if self.affine.reconstruction.tv_conditioning_constant < self.optimal_inverse_constant:
                return False
        else:
            if self.alpha != 0 or self.optimal_inverse_constant is not None:
                return False
        return self.event_count == len(self.face_certificates[0].events)


def _events(output_count: int, max_events: int) -> tuple[tuple[int, ...], ...]:
    n = int(output_count)
    if n < 1:
        raise ValueError("output alphabet must be nonempty")
    if n == 1:
        return ((),)
    count = (1 << n) - 2
    if count > int(max_events):
        raise ValueError("TV event enumeration exceeds configured cap")
    return tuple(
        tuple(j for j in range(n) if mask & (1 << j))
        for mask in range(1, (1 << n) - 1)
    )


def _face_pairs(component_count: int, max_face_pairs: int):
    m = int(component_count)
    seen = 0
    for labels in product((0, 1, 2), repeat=m):
        positive = tuple(i for i, label in enumerate(labels) if label == 1)
        negative = tuple(i for i, label in enumerate(labels) if label == 2)
        if not positive or not negative or positive > negative:
            continue
        seen += 1
        if seen > int(max_face_pairs):
            raise ValueError("disjoint face-pair enumeration exceeds configured cap")
        yield positive, negative


def _face_certificate(
    channel: tuple[tuple[Fraction, ...], ...],
    positive: tuple[int, ...],
    negative: tuple[int, ...],
    events: tuple[tuple[int, ...], ...],
    *,
    max_game_bases: int,
) -> DisjointFaceSeparationCertificate:
    actions = tuple((i, j) for i in positive for j in negative)
    matrix = tuple(
        tuple(
            sum((channel[i][k] - channel[j][k] for k in event), Fraction(0))
            for i, j in actions
        )
        for event in events
    )
    game = solve_exact_zero_sum_game(matrix, max_bases=max_game_bases)
    m = len(channel)
    left = [Fraction(0)] * m
    right = [Fraction(0)] * m
    for weight, (i, j) in zip(game.code_mixture, actions):
        left[i] += weight
        right[j] += weight
    left_prior, right_prior = tuple(left), tuple(right)
    q_left = mixture_law(left_prior, channel)
    q_right = mixture_law(right_prior, channel)
    separation = total_variation(q_left, q_right)
    result = DisjointFaceSeparationCertificate(
        positive,
        negative,
        actions,
        events,
        game,
        left_prior,
        right_prior,
        q_left,
        q_right,
        separation,
    )
    if not result.valid or separation != game.value:
        raise AssertionError("disjoint-face TV certificate failed validation")
    return result


def exact_global_tv_modulus(
    channel: Sequence[Sequence[Fraction]],
    *,
    max_minors: int = 1_000_000,
    max_events: int = 65_536,
    max_face_pairs: int = 10_000,
    max_game_bases: int = 2_000_000,
) -> GlobalTVModulusCertificate:
    """Compute exact alpha(K) and the optimal inverse TV constant when finite."""

    affine = exact_finite_mixture_channel_certificate(channel, max_minors=max_minors)
    k = affine.channel
    events = _events(len(k[0]), max_events)
    faces = tuple(
        _face_certificate(
            k,
            positive,
            negative,
            events,
            max_game_bases=max_game_bases,
        )
        for positive, negative in _face_pairs(len(k), max_face_pairs)
    )
    if not faces:
        raise AssertionError("at least one disjoint nonempty face pair is required")
    best_index = min(range(len(faces)), key=lambda i: (faces[i].separation, i))
    alpha = faces[best_index].separation
    inverse = None if alpha == 0 else 1 / alpha
    result = GlobalTVModulusCertificate(
        affine,
        faces,
        alpha,
        inverse,
        best_index,
        len(events),
        len(faces),
    )
    if not result.valid:
        raise AssertionError("global TV modulus certificate failed validation")
    return result
