"""Two-parameter quantum predictive laws: visibility plus phase.

For binary outcomes a,b in {-1,+1} and coplanar projective measurement
angles alpha_x, beta_y, define

    r_xy(v, phi) = v cos(alpha_x - beta_y - phi)
    P(a,b | x,y,v,phi) = 1/4 * (1 - a*b*r_xy).

The state (v, phi) is two-dimensional: v in [0,1] controls correlation
magnitude and phi is a periodic phase offset.  This bounded model is used to
derive physical predictive-state geometry, Fisher-rank identifiability, and
finite packing lower bounds.  It is not evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import atan2, ceil, cos, inf, log2, pi, sin
from typing import Iterable, Mapping

from .bell_predictive import BellSchedule, CANONICAL_CHSH

Outcome = tuple[int, int]
PhaseState = tuple[float, float]


@dataclass(frozen=True)
class Fisher2:
    vv: float
    vphi: float
    phiphi: float

    @property
    def determinant(self) -> float:
        return self.vv * self.phiphi - self.vphi * self.vphi

    @property
    def trace(self) -> float:
        return self.vv + self.phiphi

    @property
    def rank(self) -> int:
        tol = 1e-12
        if self.trace <= tol:
            return 0
        if self.determinant > tol:
            return 2
        return 1


def wrap_phase(phi: float) -> float:
    """Canonical phase in [-pi, pi)."""
    value = (float(phi) + pi) % (2.0 * pi) - pi
    if value == pi:
        return -pi
    return value


def _check_state(visibility: float, phase: float) -> PhaseState:
    v = float(visibility)
    if not 0.0 <= v <= 1.0:
        raise ValueError("visibility must lie in [0,1]")
    return v, wrap_phase(phase)


def correlation(visibility: float, phase: float, alice_angle: float, bob_angle: float) -> float:
    v, phi = _check_state(visibility, phase)
    return v * cos(float(alice_angle) - float(bob_angle) - phi)


def conditional_outcome_law(
    visibility: float,
    phase: float,
    alice_angle: float,
    bob_angle: float,
) -> dict[Outcome, float]:
    r = correlation(visibility, phase, alice_angle, bob_angle)
    return {(a, b): 0.25 * (1.0 - a * b * r) for a, b in product((-1, 1), repeat=2)}


def state_total_variation(
    state_a: PhaseState,
    state_b: PhaseState,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> float:
    """Exact one-trial TV between two randomized-schedule predictive laws.

    For a fixed setting pair the four-outcome TV is |r-r'|/2.  Averaging over
    the externally randomized schedule therefore gives the exact expression

        TV = 1/2 sum_xy w_xy |r_xy(theta)-r_xy(theta')|.
    """
    va, pa = _check_state(*state_a)
    vb, pb = _check_state(*state_b)
    total = 0.0
    for x, alpha in enumerate(schedule.alice_angles):
        for y, beta in enumerate(schedule.bob_angles):
            ra = correlation(va, pa, alpha, beta)
            rb = correlation(vb, pb, alpha, beta)
            total += schedule.setting_weights[x][y] * abs(ra - rb)
    return 0.5 * total


def brute_force_state_tv(
    state_a: PhaseState,
    state_b: PhaseState,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> float:
    """Enumerate the joint setting/outcome law as an independent checker."""
    va, pa = _check_state(*state_a)
    vb, pb = _check_state(*state_b)
    total = 0.0
    for x, alpha in enumerate(schedule.alice_angles):
        for y, beta in enumerate(schedule.bob_angles):
            w = schedule.setting_weights[x][y]
            la = conditional_outcome_law(va, pa, alpha, beta)
            lb = conditional_outcome_law(vb, pb, alpha, beta)
            total += w * 0.5 * sum(abs(la[o] - lb[o]) for o in la)
    return total


def single_setting_fisher(
    visibility: float,
    phase: float,
    alice_angle: float,
    bob_angle: float,
) -> Fisher2:
    """Fisher matrix for one setting pair.

    If d = alpha-beta-phi and r=v cos(d), then

        grad r = (cos d, v sin d)
        I = grad(r) grad(r)^T / (1-r^2).

    A single binary-correlation setting has rank at most one, so two parameters
    require multiple non-collinear setting gradients for local identification.
    """
    v, phi = _check_state(visibility, phase)
    d = float(alice_angle) - float(bob_angle) - phi
    c, s = cos(d), sin(d)
    r = v * c
    denom = 1.0 - r * r
    if denom <= 1e-15:
        # Boundary singularity of the regular Fisher parameterization.
        return Fisher2(inf, inf, inf)
    gv, gp = c, v * s
    return Fisher2(gv * gv / denom, gv * gp / denom, gp * gp / denom)


def schedule_fisher(
    visibility: float,
    phase: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> Fisher2:
    vv = vphi = phiphi = 0.0
    for x, alpha in enumerate(schedule.alice_angles):
        for y, beta in enumerate(schedule.bob_angles):
            w = schedule.setting_weights[x][y]
            info = single_setting_fisher(visibility, phase, alpha, beta)
            if inf in (info.vv, info.vphi, info.phiphi):
                return Fisher2(inf, inf, inf)
            vv += w * info.vv
            vphi += w * info.vphi
            phiphi += w * info.phiphi
    return Fisher2(vv, vphi, phiphi)


def fisher_eigenvalues(info: Fisher2) -> tuple[float, float]:
    """Eigenvalues of a finite symmetric 2x2 Fisher matrix, ascending."""
    if inf in (info.vv, info.vphi, info.phiphi):
        return inf, inf
    half_trace = 0.5 * info.trace
    radius = ((0.5 * (info.vv - info.phiphi)) ** 2 + info.vphi**2) ** 0.5
    return half_trace - radius, half_trace + radius


def cramer_rao_covariance_lower_bound(
    visibility: float,
    phase: float,
    trials: int,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Inverse nI for regular locally unbiased two-parameter estimation.

    Returns infinities if the schedule Fisher matrix is rank deficient.
    """
    if trials <= 0:
        raise ValueError("trials must be positive")
    info = schedule_fisher(visibility, phase, schedule)
    if info.rank < 2 or inf in (info.vv, info.vphi, info.phiphi):
        return ((inf, inf), (inf, inf))
    scale = 1.0 / (trials * info.determinant)
    return (
        (info.phiphi * scale, -info.vphi * scale),
        (-info.vphi * scale, info.vv * scale),
    )


def polar_to_cartesian_state(state: PhaseState) -> tuple[float, float]:
    """Map (v,phi) to the correlation-vector coordinates (v cos phi,v sin phi)."""
    v, phi = _check_state(*state)
    return v * cos(phi), v * sin(phi)


def cartesian_to_polar_state(x: float, y: float) -> PhaseState:
    v = (float(x) ** 2 + float(y) ** 2) ** 0.5
    if v > 1.0 + 1e-12:
        raise ValueError("cartesian state lies outside the unit visibility disk")
    return min(v, 1.0), wrap_phase(atan2(y, x))


def greedy_separated_packing(
    states: Iterable[PhaseState],
    epsilon: float,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> tuple[PhaseState, ...]:
    """Construct a certified 2*epsilon-separated packing.

    This is a deterministic lower bound on the maximum packing number.  Unlike
    the 1D visibility case, greedy selection is not claimed globally optimal.
    """
    if epsilon < 0:
        raise ValueError("epsilon must be nonnegative")
    normalized = sorted({_check_state(*state) for state in states})
    chosen: list[PhaseState] = []
    for state in normalized:
        if all(state_total_variation(state, other, schedule) > 2.0 * epsilon for other in chosen):
            chosen.append(state)
    return tuple(chosen)


def exact_maximum_packing(
    states: Iterable[PhaseState],
    epsilon: float,
    schedule: BellSchedule = CANONICAL_CHSH,
    *,
    max_states: int = 48,
) -> tuple[PhaseState, ...]:
    """Exact maximum packing by branch-and-bound maximum clique on <=48 states."""
    if epsilon < 0:
        raise ValueError("epsilon must be nonnegative")
    nodes = sorted({_check_state(*state) for state in states})
    if len(nodes) > max_states:
        raise ValueError(f"exact packing capped at {max_states} states")
    n = len(nodes)
    adjacency = [0] * n
    for i, j in combinations(range(n), 2):
        if state_total_variation(nodes[i], nodes[j], schedule) > 2.0 * epsilon:
            adjacency[i] |= 1 << j
            adjacency[j] |= 1 << i

    best_mask = 0

    def expand(candidates: int, clique: int) -> None:
        nonlocal best_mask
        if clique.bit_count() + candidates.bit_count() <= best_mask.bit_count():
            return
        if candidates == 0:
            if clique.bit_count() > best_mask.bit_count():
                best_mask = clique
            return
        while candidates:
            if clique.bit_count() + candidates.bit_count() <= best_mask.bit_count():
                return
            bit = candidates & -candidates
            idx = bit.bit_length() - 1
            candidates ^= bit
            expand(candidates & adjacency[idx], clique | bit)
        if clique.bit_count() > best_mask.bit_count():
            best_mask = clique

    expand((1 << n) - 1, 0)
    return tuple(nodes[i] for i in range(n) if (best_mask >> i) & 1)


def predictive_memory_lower_bound_bits(
    states: Iterable[PhaseState],
    epsilon: float,
    schedule: BellSchedule = CANONICAL_CHSH,
    *,
    exact: bool = False,
) -> int:
    packing = exact_maximum_packing(states, epsilon, schedule) if exact else greedy_separated_packing(states, epsilon, schedule)
    return 0 if len(packing) <= 1 else ceil(log2(len(packing)))


def visibility_phase_grid(
    visibility_points: int,
    phase_points: int,
    *,
    include_zero_once: bool = True,
) -> tuple[PhaseState, ...]:
    """Finite polar grid over the unit visibility disk."""
    if visibility_points < 2 or phase_points < 2:
        raise ValueError("both grid sizes must be at least two")
    states: list[PhaseState] = []
    for i in range(visibility_points):
        v = i / (visibility_points - 1)
        if v == 0.0 and include_zero_once:
            states.append((0.0, 0.0))
            continue
        for j in range(phase_points):
            phi = -pi + 2.0 * pi * j / phase_points
            states.append((v, phi))
    return tuple(states)
