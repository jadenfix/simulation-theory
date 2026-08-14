"""Closed-form geometry for visibility+phase Bell predictive families."""

from __future__ import annotations

from math import ceil, cos, log2, sin, sqrt

from .bell_predictive import BellSchedule, CANONICAL_CHSH
from .quantum_phase import PhaseState, cartesian_to_polar_state, polar_to_cartesian_state, state_total_variation


def schedule_cartesian_tv(
    state_a: PhaseState,
    state_b: PhaseState,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> float:
    """Exact weighted projection seminorm in correlation-disk coordinates.

    With q=(v cos phi,v sin phi) and setting direction
    s_xy=(cos(alpha-beta),sin(alpha-beta)),

        TV(P_q,P_q') = 1/2 sum_xy w_xy |s_xy dot (q-q')|.

    This is always a seminorm in delta-q and is a true norm exactly when the
    positive-weight setting directions span R^2.
    """
    xa, ya = polar_to_cartesian_state(state_a)
    xb, yb = polar_to_cartesian_state(state_b)
    dx, dy = xa - xb, ya - yb
    total = 0.0
    for x, alpha in enumerate(schedule.alice_angles):
        for y, beta in enumerate(schedule.bob_angles):
            w = schedule.setting_weights[x][y]
            if w == 0.0:
                continue
            theta = alpha - beta
            total += w * abs(cos(theta) * dx + sin(theta) * dy)
    return 0.5 * total


def schedule_direction_rank(schedule: BellSchedule = CANONICAL_CHSH, tolerance: float = 1e-12) -> int:
    """Rank of positive-weight measurement directions in R^2."""
    directions: list[tuple[float, float]] = []
    for x, alpha in enumerate(schedule.alice_angles):
        for y, beta in enumerate(schedule.bob_angles):
            if schedule.setting_weights[x][y] <= 0.0:
                continue
            theta = alpha - beta
            directions.append((cos(theta), sin(theta)))
    if not directions:
        return 0
    first = directions[0]
    for other in directions[1:]:
        determinant = first[0] * other[1] - first[1] * other[0]
        if abs(determinant) > tolerance:
            return 2
    return 1


def schedule_metric_is_norm(schedule: BellSchedule = CANONICAL_CHSH) -> bool:
    return schedule_direction_rank(schedule) == 2


def canonical_chsh_cartesian_tv(state_a: PhaseState, state_b: PhaseState) -> float:
    """Exact canonical-CHSH TV from correlation-disk coordinates.

    Let q=(v cos phi, v sin phi). For the four canonical CHSH setting pairs,

        TV(P_q,P_q') = ||q-q'||_infinity / (2 sqrt(2)).

    This follows because the four setting directions are +/-45 degree axes and
    |x+y|+|x-y| = 2 max(|x|,|y|).
    """
    xa, ya = polar_to_cartesian_state(state_a)
    xb, yb = polar_to_cartesian_state(state_b)
    return max(abs(xa - xb), abs(ya - yb)) / (2.0 * sqrt(2.0))


def verify_canonical_metric(state_a: PhaseState, state_b: PhaseState, tolerance: float = 1e-12) -> bool:
    return (
        abs(canonical_chsh_cartesian_tv(state_a, state_b) - state_total_variation(state_a, state_b)) <= tolerance
        and abs(schedule_cartesian_tv(state_a, state_b) - state_total_variation(state_a, state_b)) <= tolerance
    )


def constructive_square_packing(epsilon: float) -> tuple[PhaseState, ...]:
    """Analytic 2*epsilon-separated packing inside the unit visibility disk.

    The square [-1/sqrt(2),1/sqrt(2)]^2 lies inside the unit disk. Canonical
    predictive TV equals L-infinity distance divided by 2sqrt(2), so pairwise
    TV > 2 epsilon follows from Cartesian spacing > 4sqrt(2) epsilon.

    Choosing m = ceil(1/(4 epsilon)) equally spaced coordinates across the
    square gives strict separation for every epsilon where m>=2. The result
    contains m^2 physically valid states, establishing a quadratic packing
    lower bound in 1/epsilon.
    """
    if not 0.0 < epsilon < 0.25:
        raise ValueError("epsilon must lie in (0, 0.25) for this construction")
    m = ceil(1.0 / (4.0 * epsilon))
    if m < 2:
        m = 2
    radius = 1.0 / sqrt(2.0)
    step = 2.0 * radius / (m - 1)
    points = [-radius + i * step for i in range(m)]
    return tuple(cartesian_to_polar_state(x, y) for x in points for y in points)


def constructive_packing_size_lower_bound(epsilon: float) -> int:
    return len(constructive_square_packing(epsilon))


def constructive_memory_lower_bound_bits(epsilon: float) -> int:
    """Bits required for epsilon-accurate representation on the constructed set."""
    k = constructive_packing_size_lower_bound(epsilon)
    return ceil(log2(k))


def asymptotic_memory_lower_bound_bits(epsilon: float) -> float:
    """Smooth asymptotic form 2 log2(1/(4 epsilon))."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    return 2.0 * log2(1.0 / (4.0 * epsilon))
