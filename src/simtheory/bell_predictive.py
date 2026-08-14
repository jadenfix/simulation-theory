"""Physically derived predictive laws for finite Bell experiments.

This module uses a bounded two-qubit Werner/singlet correlation family.  For
binary outcomes a,b in {-1,+1} and coplanar projective measurement angles
alpha_x, beta_y, the model is

    P(a,b | x,y,v) = 1/4 * (1 - a*b*v*cos(alpha_x-beta_y)),

where v in [0,1] is the Werner visibility.  v=1 is the ideal singlet
correlation law for the chosen plane and v=0 is uniform white noise.

The purpose is not to claim that our universe is a simulator.  It is to derive
predictive-state packing bounds from an explicit physical experiment family
rather than from arbitrary probability vectors.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import ceil, cos, log2, pi, sqrt
from typing import Iterable, Mapping, Sequence

Outcome = tuple[int, int]
Setting = tuple[int, int]
TranscriptAtom = tuple[int, int, int, int]


@dataclass(frozen=True)
class BellSchedule:
    """Finite measurement settings and a distribution over setting pairs."""

    alice_angles: tuple[float, ...]
    bob_angles: tuple[float, ...]
    setting_weights: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if not self.alice_angles or not self.bob_angles:
            raise ValueError("at least one setting per party is required")
        if len(self.setting_weights) != len(self.alice_angles):
            raise ValueError("setting_weights must have one row per Alice setting")
        if any(len(row) != len(self.bob_angles) for row in self.setting_weights):
            raise ValueError("setting_weights must have one column per Bob setting")
        flat = [w for row in self.setting_weights for w in row]
        if any(w < 0 for w in flat):
            raise ValueError("setting weights must be nonnegative")
        if abs(sum(flat) - 1.0) > 1e-12:
            raise ValueError("setting weights must sum to one")

    @classmethod
    def uniform(cls, alice_angles: Sequence[float], bob_angles: Sequence[float]) -> "BellSchedule":
        if not alice_angles or not bob_angles:
            raise ValueError("at least one setting per party is required")
        weight = 1.0 / (len(alice_angles) * len(bob_angles))
        return cls(
            tuple(float(x) for x in alice_angles),
            tuple(float(y) for y in bob_angles),
            tuple(tuple(weight for _ in bob_angles) for _ in alice_angles),
        )


CANONICAL_CHSH = BellSchedule.uniform(
    alice_angles=(0.0, pi / 2.0),
    bob_angles=(pi / 4.0, -pi / 4.0),
)


def _check_visibility(visibility: float) -> float:
    v = float(visibility)
    if not 0.0 <= v <= 1.0:
        raise ValueError("visibility must lie in [0,1]")
    return v


def outcome_probability(
    visibility: float,
    alice_angle: float,
    bob_angle: float,
    alice_outcome: int,
    bob_outcome: int,
) -> float:
    """Return P(a,b | alpha,beta,v) for the Werner/singlet family."""

    v = _check_visibility(visibility)
    if alice_outcome not in (-1, 1) or bob_outcome not in (-1, 1):
        raise ValueError("outcomes must be -1 or +1")
    return 0.25 * (
        1.0
        - alice_outcome
        * bob_outcome
        * v
        * cos(float(alice_angle) - float(bob_angle))
    )


def conditional_outcome_law(
    visibility: float,
    alice_angle: float,
    bob_angle: float,
) -> dict[Outcome, float]:
    """Probability law over the four outcomes for one setting pair."""

    return {
        (a, b): outcome_probability(visibility, alice_angle, bob_angle, a, b)
        for a, b in product((-1, 1), repeat=2)
    }


def joint_setting_outcome_law(
    visibility: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> dict[TranscriptAtom, float]:
    """Joint law over a random setting pair and its two outcomes."""

    v = _check_visibility(visibility)
    law: dict[TranscriptAtom, float] = {}
    for x, alpha in enumerate(schedule.alice_angles):
        for y, beta in enumerate(schedule.bob_angles):
            w = schedule.setting_weights[x][y]
            for (a, b), p in conditional_outcome_law(v, alpha, beta).items():
                law[(x, y, a, b)] = w * p
    return law


def total_variation(p: Mapping[object, float], q: Mapping[object, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(float(p.get(k, 0.0)) - float(q.get(k, 0.0))) for k in keys)


def schedule_geometry(schedule: BellSchedule = CANONICAL_CHSH) -> float:
    """Return C = sum_xy w_xy |cos(alpha_x-beta_y)|.

    For the visibility family, the joint predictive-law distance is exactly

        TV(P_v, P_u) = |v-u| C / 2.
    """

    return sum(
        schedule.setting_weights[x][y]
        * abs(cos(alpha - beta))
        for x, alpha in enumerate(schedule.alice_angles)
        for y, beta in enumerate(schedule.bob_angles)
    )


def analytic_visibility_tv(
    visibility_a: float,
    visibility_b: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> float:
    """Closed-form TV distance between two visibility-indexed predictive laws."""

    va = _check_visibility(visibility_a)
    vb = _check_visibility(visibility_b)
    return 0.5 * abs(va - vb) * schedule_geometry(schedule)


def brute_force_visibility_tv(
    visibility_a: float,
    visibility_b: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> float:
    return total_variation(
        joint_setting_outcome_law(visibility_a, schedule),
        joint_setting_outcome_law(visibility_b, schedule),
    )


def chsh_value(visibility: float) -> float:
    """Absolute CHSH value for the canonical angle convention.

    The canonical settings attain |S| = 2*sqrt(2)*v.  A value above 2 violates
    the local-hidden-variable CHSH bound within this model.
    """

    return 2.0 * sqrt(2.0) * _check_visibility(visibility)


def violates_chsh(visibility: float, *, tolerance: float = 1e-12) -> bool:
    return chsh_value(visibility) > 2.0 + tolerance


def maximum_epsilon_packing(
    visibilities: Iterable[float],
    epsilon: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> tuple[float, ...]:
    """Return a maximum 2*epsilon-separated packing on a finite visibility grid.

    Because the TV metric is a positive constant times |v-u|, the problem is
    one-dimensional interval packing.  Sorting and greedily choosing the
    smallest feasible next point is optimal for maximum cardinality.
    """

    if epsilon < 0:
        raise ValueError("epsilon must be nonnegative")
    values = sorted({_check_visibility(v) for v in visibilities})
    if not values:
        return ()
    geometry = schedule_geometry(schedule)
    if geometry == 0.0:
        return (values[0],)

    chosen = [values[0]]
    for value in values[1:]:
        if 0.5 * (value - chosen[-1]) * geometry > 2.0 * epsilon:
            chosen.append(value)
    return tuple(chosen)


def predictive_memory_lower_bound_bits(
    visibilities: Iterable[float],
    epsilon: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> int:
    """Bits required by any epsilon-accurate state representation on the grid.

    If K candidate future laws are pairwise more than 2*epsilon apart in TV,
    no one internal renderer state can approximate two of them within epsilon.
    Hence at least K states, or ceil(log2 K) bits, are necessary.
    """

    k = len(maximum_epsilon_packing(visibilities, epsilon, schedule))
    if k <= 1:
        return 0
    return ceil(log2(k))


def uniform_visibility_grid(points: int) -> tuple[float, ...]:
    if points < 2:
        raise ValueError("points must be at least two")
    return tuple(i / (points - 1) for i in range(points))
