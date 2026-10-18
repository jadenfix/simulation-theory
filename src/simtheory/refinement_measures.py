"""Refinement-additive measure uniqueness on rational latent weights.

If a local mass rule mu on rational weights is normalized by mu(1)=1 and is
additive under every finite rational refinement, then mu(p/q)=p/q.  Ordinary
probability weight is therefore the unique normalized local rational rule with
full refinement additivity.

The module also audits integer-power escort scores.  Equal r-way cloning scales
a component's unnormalized score w^gamma by r^(1-gamma); only gamma=1 is
refinement invariant.  gamma=0 recovers positive-label counting.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


def forced_refinement_mass(weight: Fraction) -> Fraction:
    """Value forced by normalization and rational refinement additivity."""

    w = Fraction(weight)
    if not 0 <= w <= 1:
        raise ValueError("weight must lie in [0,1]")
    return w


@dataclass(frozen=True)
class RationalRefinementUniquenessCertificate:
    weight: Fraction
    numerator: int
    denominator: int
    unit_piece: Fraction
    forced_mass: Fraction

    @property
    def valid(self) -> bool:
        return (
            0 <= self.weight <= 1
            and self.weight == Fraction(self.numerator, self.denominator)
            and self.denominator > 0
            and self.unit_piece == Fraction(1, self.denominator)
            and self.forced_mass == self.numerator * self.unit_piece == self.weight
        )


def rational_refinement_uniqueness_certificate(
    weight: Fraction,
) -> RationalRefinementUniquenessCertificate:
    w = Fraction(weight)
    if not 0 <= w <= 1:
        raise ValueError("weight must lie in [0,1]")
    result = RationalRefinementUniquenessCertificate(
        w,
        w.numerator,
        w.denominator,
        Fraction(1, w.denominator),
        w,
    )
    if not result.valid:
        raise AssertionError("rational refinement uniqueness certificate failed")
    return result


def escort_score(weight: Fraction, power: int) -> Fraction:
    w = Fraction(weight)
    gamma = int(power)
    if not 0 <= w <= 1 or gamma < 0:
        raise ValueError("weight must lie in [0,1] and power must be nonnegative")
    if gamma == 0:
        return Fraction(int(w > 0))
    return w**gamma


def equal_clone_score_scaling(weight: Fraction, clones: int, power: int) -> Fraction:
    w = Fraction(weight)
    r = int(clones)
    gamma = int(power)
    if not 0 < w <= 1 or r < 2 or gamma < 0:
        raise ValueError("positive weight, at least two clones, and nonnegative power required")
    return r * escort_score(w / r, gamma) / escort_score(w, gamma)


def escort_category_mass(
    prior: Sequence[Fraction],
    categories: Sequence[str],
    target: str,
    power: int,
) -> Fraction:
    p = tuple(Fraction(v) for v in prior)
    labels = tuple(str(value) for value in categories)
    if (
        not p
        or len(p) != len(labels)
        or any(v < 0 for v in p)
        or sum(p, Fraction(0)) != 1
    ):
        raise ValueError("valid prior and one category per component are required")
    scores = tuple(escort_score(v, power) for v in p)
    total = sum(scores, Fraction(0))
    if total == 0:
        raise ValueError("escort scores have zero total mass")
    return sum(
        (score for score, label in zip(scores, labels) if label == target),
        Fraction(0),
    ) / total
