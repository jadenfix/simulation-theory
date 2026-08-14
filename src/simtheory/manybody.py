"""First-principles many-body predictive-state lower bounds.

Two bounded families are implemented.

1. Computational-basis states |z> for z in {0,1}^n under coordinate Z
   measurements. Exact prediction of every allowed query requires 2^n
   distinct predictive states, hence at least n internal state bits.

2. Product-qubit Z-polarization states q=(q_1,...,q_d) in [-r,r]^d. A query
   chooses coordinate i uniformly and returns s in {-1,+1} with

       P(s | i,q) = (1 + s q_i)/2.

   The one-query joint law over (i,s) has exact total variation

       TV(P_q,P_u) = ||q-u||_1 / (2d).

   This gives explicit d-dimensional epsilon packings and memory lower bounds.

These are internal predictive representation bounds for declared observable
families. They are not parent-hardware bounds and are not evidence that reality
is simulated.
"""

from __future__ import annotations

from itertools import product
from math import ceil, log2
from typing import Iterable, Sequence

BitString = tuple[int, ...]
VectorState = tuple[float, ...]


def computational_basis_states(qubits: int) -> tuple[BitString, ...]:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    return tuple(product((0, 1), repeat=qubits))


def basis_query_probability(state: BitString, qubit: int, outcome: int) -> float:
    if not state:
        raise ValueError("state cannot be empty")
    if not 0 <= qubit < len(state):
        raise ValueError("qubit out of range")
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1")
    return 1.0 if state[qubit] == outcome else 0.0


def basis_predictive_distance(left: BitString, right: BitString) -> float:
    """Worst-query TV between computational-basis states.

    It is 0 for identical states and 1 for every distinct pair because a
    differing coordinate can be queried and produces disjoint deterministic
    outcome laws.
    """
    if len(left) != len(right) or not left:
        raise ValueError("states must have equal positive length")
    return 0.0 if left == right else 1.0


def exact_basis_renderer_states_lower_bound(qubits: int) -> int:
    """Number of predictive states needed for exact coordinate-Z prediction."""
    if qubits < 1:
        raise ValueError("qubits must be positive")
    return 1 << qubits


def exact_basis_renderer_bits_lower_bound(qubits: int) -> int:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    return qubits


def _validate_vector(state: Sequence[float], radius: float | None = None) -> VectorState:
    if not state:
        raise ValueError("state cannot be empty")
    q = tuple(float(x) for x in state)
    bound = 1.0 if radius is None else float(radius)
    if bound <= 0.0 or bound > 1.0:
        raise ValueError("radius must lie in (0,1]")
    if any(abs(x) > bound + 1e-12 for x in q):
        raise ValueError("state lies outside declared polarization cube")
    return q


def product_z_query_probability(state: Sequence[float], coordinate: int, outcome: int) -> float:
    q = _validate_vector(state)
    if not 0 <= coordinate < len(q):
        raise ValueError("coordinate out of range")
    if outcome not in (-1, 1):
        raise ValueError("outcome must be -1 or +1")
    return 0.5 * (1.0 + outcome * q[coordinate])


def product_z_joint_law(state: Sequence[float]) -> dict[tuple[int, int], float]:
    """Law when the coordinate query is selected uniformly."""
    q = _validate_vector(state)
    d = len(q)
    return {
        (i, s): product_z_query_probability(q, i, s) / d
        for i in range(d)
        for s in (-1, 1)
    }


def product_z_total_variation(left: Sequence[float], right: Sequence[float]) -> float:
    """Exact TV = ||left-right||_1/(2d)."""
    q = _validate_vector(left)
    u = _validate_vector(right)
    if len(q) != len(u):
        raise ValueError("states must have the same dimension")
    return sum(abs(a - b) for a, b in zip(q, u)) / (2.0 * len(q))


def brute_force_product_z_tv(left: Sequence[float], right: Sequence[float]) -> float:
    p = product_z_joint_law(left)
    q = product_z_joint_law(right)
    return 0.5 * sum(abs(p[key] - q[key]) for key in p)


def polarization_grid(dimension: int, levels: int, radius: float = 1.0) -> tuple[VectorState, ...]:
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if levels < 2:
        raise ValueError("levels must be at least two")
    if not 0.0 < radius <= 1.0:
        raise ValueError("radius must lie in (0,1]")
    values = tuple(-radius + 2.0 * radius * i / (levels - 1) for i in range(levels))
    return tuple(product(values, repeat=dimension))


def cartesian_code_packing(
    dimension: int,
    epsilon: float,
    radius: float = 1.0,
) -> tuple[VectorState, ...]:
    """Construct a 2*epsilon-separated packing using binary cube vertices.

    For q in {-r,+r}^d, TV(q,u) = r * Hamming(q,u)/d. All distinct vertices
    therefore have minimum TV r/d. When epsilon < r/(2d), all 2^d vertices
    form a valid 2*epsilon packing, yielding d predictive bits.

    This deliberately simple construction proves exponential state growth with
    subsystem count without invoking a stabilizer-state counting formula.
    """
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    if not 0.0 < radius <= 1.0:
        raise ValueError("radius must lie in (0,1]")
    if not epsilon < radius / (2.0 * dimension):
        raise ValueError("epsilon is too large for the all-vertices separation guarantee")
    return tuple(product((-radius, radius), repeat=dimension))


def cartesian_code_memory_lower_bound_bits(
    dimension: int,
    epsilon: float,
    radius: float = 1.0,
) -> int:
    packing = cartesian_code_packing(dimension, epsilon, radius)
    return ceil(log2(len(packing)))


def qary_product_packing(
    dimension: int,
    levels: int,
    epsilon: float,
    radius: float = 1.0,
) -> tuple[VectorState, ...]:
    """Certified full-grid packing when adjacent one-coordinate gaps suffice.

    Grid spacing is Delta=2r/(levels-1). Distinct grid states may differ in
    only one coordinate, giving minimum TV Delta/(2d)=r/[d(levels-1)]. Thus
    the full levels^d grid is 2*epsilon-separated whenever

        epsilon < r / [2 d (levels-1)].
    """
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    if levels < 2 or dimension < 1:
        raise ValueError("invalid grid dimensions")
    if not 0.0 < radius <= 1.0:
        raise ValueError("radius must lie in (0,1]")
    if not epsilon < radius / (2.0 * dimension * (levels - 1)):
        raise ValueError("epsilon is too large for the full-grid separation guarantee")
    return polarization_grid(dimension, levels, radius)


def qary_product_memory_lower_bound_bits(
    dimension: int,
    levels: int,
    epsilon: float,
    radius: float = 1.0,
) -> int:
    return ceil(log2(len(qary_product_packing(dimension, levels, epsilon, radius))))
