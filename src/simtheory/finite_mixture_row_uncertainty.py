"""Robust finite-mixture identifiability under rowwise channel uncertainty.

A nominal categorical channel K is known only up to rowwise TV radii r_i.  If
K' is any admissible true channel, the global mixture modulus obeys the sharp
uniform perturbation inequality

    |alpha(K') - alpha(K)| <= 2 max_i r_i.

This module also computes a stronger face-specific lower certificate by
penalizing each latent pair action (i,j) by r_i+r_j inside the exact disjoint-
face zero-sum games.  A positive robust lower bound certifies identifiability of
every channel in the declared rowwise uncertainty set.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .finite_mixture_global_tv import (
    DisjointFaceSeparationCertificate,
    GlobalTVModulusCertificate,
    exact_global_tv_modulus,
)
from .robust_prior_codes import ExactZeroSumGameCertificate, solve_exact_zero_sum_game


@dataclass(frozen=True)
class RobustFaceLowerCertificate:
    nominal_face: DisjointFaceSeparationCertificate
    pair_penalties: tuple[Fraction, ...]
    penalized_game: ExactZeroSumGameCertificate
    unclipped_lower_bound: Fraction
    lower_bound: Fraction

    @property
    def valid(self) -> bool:
        if (
            not self.nominal_face.valid
            or not self.penalized_game.valid
            or len(self.pair_penalties) != len(self.nominal_face.pair_actions)
            or any(value < 0 for value in self.pair_penalties)
        ):
            return False
        expected = tuple(
            tuple(value - self.pair_penalties[column] for column, value in enumerate(row))
            for row in self.nominal_face.game.cost_matrix
        )
        return (
            self.penalized_game.cost_matrix == expected
            and self.unclipped_lower_bound == self.penalized_game.value
            and self.lower_bound == max(Fraction(0), self.unclipped_lower_bound)
        )


@dataclass(frozen=True)
class RowUncertainGlobalTVCertificate:
    nominal: GlobalTVModulusCertificate
    row_radii: tuple[Fraction, ...]
    face_lower_certificates: tuple[RobustFaceLowerCertificate, ...]
    simple_lower_bound: Fraction
    facewise_lower_bound: Fraction
    lipschitz_upper_bound: Fraction
    robust_inverse_upper_bound: Fraction | None

    @property
    def valid(self) -> bool:
        if (
            not self.nominal.valid
            or len(self.row_radii) != len(self.nominal.affine.channel)
            or any(not 0 <= radius <= 1 for radius in self.row_radii)
            or len(self.face_lower_certificates) != len(self.nominal.face_certificates)
            or any(not face.valid for face in self.face_lower_certificates)
        ):
            return False
        rmax = max(self.row_radii)
        simple = max(Fraction(0), self.nominal.alpha - 2 * rmax)
        facewise = min(face.lower_bound for face in self.face_lower_certificates)
        upper = min(Fraction(1), self.nominal.alpha + 2 * rmax)
        expected_inverse = None if facewise == 0 else 1 / facewise
        return (
            self.simple_lower_bound == simple
            and self.facewise_lower_bound == facewise
            and self.facewise_lower_bound >= self.simple_lower_bound
            and self.lipschitz_upper_bound == upper
            and self.robust_inverse_upper_bound == expected_inverse
        )


def exact_row_uncertain_global_tv(
    channel: Sequence[Sequence[Fraction]],
    row_radii: Sequence[Fraction],
    *,
    max_minors: int = 1_000_000,
    max_events: int = 65_536,
    max_face_pairs: int = 10_000,
    max_game_bases: int = 2_000_000,
) -> RowUncertainGlobalTVCertificate:
    nominal = exact_global_tv_modulus(
        channel,
        max_minors=max_minors,
        max_events=max_events,
        max_face_pairs=max_face_pairs,
        max_game_bases=max_game_bases,
    )
    radii = tuple(Fraction(value) for value in row_radii)
    if len(radii) != len(nominal.affine.channel) or any(not 0 <= r <= 1 for r in radii):
        raise ValueError("one TV radius in [0,1] is required per channel row")

    robust_faces: list[RobustFaceLowerCertificate] = []
    for face in nominal.face_certificates:
        penalties = tuple(radii[i] + radii[j] for i, j in face.pair_actions)
        matrix = tuple(
            tuple(value - penalties[column] for column, value in enumerate(row))
            for row in face.game.cost_matrix
        )
        game = solve_exact_zero_sum_game(matrix, max_bases=max_game_bases)
        robust = RobustFaceLowerCertificate(
            face,
            penalties,
            game,
            game.value,
            max(Fraction(0), game.value),
        )
        if not robust.valid:
            raise AssertionError("robust face lower certificate failed validation")
        robust_faces.append(robust)

    rmax = max(radii)
    simple = max(Fraction(0), nominal.alpha - 2 * rmax)
    facewise = min(face.lower_bound for face in robust_faces)
    upper = min(Fraction(1), nominal.alpha + 2 * rmax)
    result = RowUncertainGlobalTVCertificate(
        nominal,
        radii,
        tuple(robust_faces),
        simple,
        facewise,
        upper,
        None if facewise == 0 else 1 / facewise,
    )
    if not result.valid:
        raise AssertionError("row-uncertain global TV certificate failed validation")
    return result


def certified_latent_radius_with_channel_uncertainty(
    observed_tv_radius: Fraction,
    certificate: RowUncertainGlobalTVCertificate,
) -> Fraction:
    """Transfer an observed-law radius through every admissible true channel."""

    rho = Fraction(observed_tv_radius)
    if not 0 <= rho <= 1 or not certificate.valid:
        raise ValueError("invalid observed radius or uncertainty certificate")
    if certificate.facewise_lower_bound == 0:
        return Fraction(1)
    return min(Fraction(1), rho / certificate.facewise_lower_bound)
