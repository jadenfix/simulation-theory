"""Closed-form geometry for the canonical CHSH visibility+phase family."""

from __future__ import annotations

from math import ceil, log2, sqrt

from .quantum_phase import PhaseState, cartesian_to_polar_state, polar_to_cartesian_state, state_total_variation


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
    return abs(canonical_chsh_cartesian_tv(state_a, state_b) - state_total_variation(state_a, state_b)) <= tolerance


def constructive_square_packing(epsilon: float) -> tuple[PhaseState, ...]:
    """Analytic 2*epsilon-separated packing inside the unit visibility disk.

    The square [-1/sqrt(2),1/sqrt(2)]^2 lies inside the unit disk. Canonical
    predictive TV equals L-infinity distance divided by 2sqrt(2), so pairwise
    TV > 2 epsilon follows from Cartesian spacing > 4sqrt(2) epsilon.

    Choosing m = ceil(1/(4 epsilon)) equally spaced coordinates across the
    square gives strict separation for every epsilon where m>=2.  The result
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
    # The strict inequality m-1 < 1/(4 epsilon) is guaranteed by m=ceil(A)
    # except when A is an integer, where m=A and m-1<A still holds.
    points = [-radius + i * step for i in range(m)]
    return tuple(cartesian_to_polar_state(x, y) for x in points for y in points)


def constructive_packing_size_lower_bound(epsilon: float) -> int:
    return len(constructive_square_packing(epsilon))


def constructive_memory_lower_bound_bits(epsilon: float) -> int:
    """Bits required for epsilon-accurate representation on the constructed set."""
    k = constructive_packing_size_lower_bound(epsilon)
    return ceil(log2(k))


def asymptotic_memory_lower_bound_bits(epsilon: float) -> float:
    """Smooth asymptotic form 2 log2(1/(4 epsilon)).

    This is an asymptotic expression, not an integer certified bound; use
    constructive_memory_lower_bound_bits for the finite theorem.
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    return 2.0 * log2(1.0 / (4.0 * epsilon))
