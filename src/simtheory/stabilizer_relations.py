"""Relational predictive-state bounds from graph-state stabilizers.

This module deliberately avoids the invalid inference

    Hilbert-space dimension -> parent-universe hardware cost.

Instead it starts from a declared observable family and asks how many distinct
future probability laws must be represented.

For a simple graph G on n qubits, let |G,z> = Z^z |G> be the graph-state basis,
with z in {0,1}^n.  The graph-state stabilizer generators are

    K_i = X_i product_{j in N(i)} Z_j,

and |G,z> has generator eigenvalue (-1)^{z_i}.  If a query chooses generator i
with weight w_i and records its +/-1 outcome, then the exact predictive-law
distance is

    TV(P_z, P_u) = sum_i w_i 1[z_i != u_i].

Under uniform queries this is normalized Hamming distance.  Binary codes
therefore become certified predictive packings.

The same stabilizer algebra also exposes local blindness.  A graph-basis state
has a maximally mixed reduction on a subset S whenever no nonidentity
stabilizer element is supported inside S.  For cycle graphs C_n with n >= 5,
the minimum nonidentity stabilizer weight is exactly three.  Consequently all
one- and two-qubit reductions are maximally mixed for every one of the 2^n
graph-basis labels, while weight-three generator queries reveal the labels.

All bounds here are internal predictive-representation statements for the
declared query model.  They are not evidence for simulation and are not claims
about an unknown parent substrate.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb, floor, log2
from typing import Iterable, Sequence

BitLabel = tuple[int, ...]
QueryLaw = dict[tuple[int, int], float]


@dataclass(frozen=True)
class SimpleGraph:
    """Finite undirected loop-free graph with canonicalized edges."""

    qubits: int
    edges: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if self.qubits < 1:
            raise ValueError("qubits must be positive")
        canonical: list[tuple[int, int]] = []
        for edge in self.edges:
            if len(edge) != 2:
                raise ValueError("each edge must contain exactly two vertices")
            left, right = int(edge[0]), int(edge[1])
            if not 0 <= left < self.qubits or not 0 <= right < self.qubits:
                raise ValueError("edge endpoint out of range")
            if left == right:
                raise ValueError("self-loops are not allowed")
            if left > right:
                left, right = right, left
            canonical.append((left, right))
        object.__setattr__(self, "edges", tuple(sorted(set(canonical))))

    @classmethod
    def path(cls, qubits: int) -> "SimpleGraph":
        if qubits < 2:
            raise ValueError("a path graph requires at least two qubits")
        return cls(qubits, tuple((i, i + 1) for i in range(qubits - 1)))

    @classmethod
    def cycle(cls, qubits: int) -> "SimpleGraph":
        if qubits < 3:
            raise ValueError("a cycle graph requires at least three qubits")
        return cls(qubits, tuple((i, (i + 1) % qubits) for i in range(qubits)))

    def adjacency_masks(self) -> tuple[int, ...]:
        masks = [0] * self.qubits
        for left, right in self.edges:
            masks[left] |= 1 << right
            masks[right] |= 1 << left
        return tuple(masks)

    def neighbors(self, vertex: int) -> tuple[int, ...]:
        if not 0 <= vertex < self.qubits:
            raise ValueError("vertex out of range")
        mask = self.adjacency_masks()[vertex]
        return tuple(i for i in range(self.qubits) if (mask >> i) & 1)

    def degree(self, vertex: int) -> int:
        return len(self.neighbors(vertex))

    @property
    def has_isolated_vertex(self) -> bool:
        return any(mask == 0 for mask in self.adjacency_masks())


def _validate_label(label: Sequence[int], qubits: int | None = None) -> BitLabel:
    bits = tuple(int(bit) for bit in label)
    if not bits:
        raise ValueError("label cannot be empty")
    if qubits is not None and len(bits) != qubits:
        raise ValueError("label length does not match graph size")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("labels must be binary")
    return bits


def _validate_query_weights(qubits: int, weights: Sequence[float] | None) -> tuple[float, ...]:
    if weights is None:
        return tuple(1.0 / qubits for _ in range(qubits))
    normalized = tuple(float(weight) for weight in weights)
    if len(normalized) != qubits:
        raise ValueError("one query weight is required per generator")
    if any(weight < 0.0 for weight in normalized):
        raise ValueError("query weights must be nonnegative")
    if abs(sum(normalized) - 1.0) > 1e-12:
        raise ValueError("query weights must sum to one")
    return normalized


def graph_generator_weight(graph: SimpleGraph, generator: int) -> int:
    """Pauli weight of K_i = X_i product_{j in N(i)} Z_j."""

    if not 0 <= generator < graph.qubits:
        raise ValueError("generator out of range")
    return 1 + graph.degree(generator)


def graph_generator_eigenvalue(label: Sequence[int], generator: int) -> int:
    bits = _validate_label(label)
    if not 0 <= generator < len(bits):
        raise ValueError("generator out of range")
    return -1 if bits[generator] else 1


def graph_generator_joint_law(
    label: Sequence[int],
    weights: Sequence[float] | None = None,
) -> QueryLaw:
    """Joint law over generator index and deterministic stabilizer outcome."""

    bits = _validate_label(label)
    query_weights = _validate_query_weights(len(bits), weights)
    law: QueryLaw = {}
    for generator, weight in enumerate(query_weights):
        expected = graph_generator_eigenvalue(bits, generator)
        for outcome in (-1, 1):
            law[(generator, outcome)] = weight if outcome == expected else 0.0
    return law


def graph_generator_total_variation(
    left: Sequence[int],
    right: Sequence[int],
    weights: Sequence[float] | None = None,
) -> float:
    """Exact weighted-Hamming predictive distance between graph-basis labels."""

    left_bits = _validate_label(left)
    right_bits = _validate_label(right, len(left_bits))
    query_weights = _validate_query_weights(len(left_bits), weights)
    return sum(
        weight
        for weight, left_bit, right_bit in zip(query_weights, left_bits, right_bits)
        if left_bit != right_bit
    )


def brute_force_graph_generator_tv(
    left: Sequence[int],
    right: Sequence[int],
    weights: Sequence[float] | None = None,
) -> float:
    first = graph_generator_joint_law(left, weights)
    second = graph_generator_joint_law(right, weights)
    return 0.5 * sum(abs(first[key] - second[key]) for key in first)


def worst_generator_query_distance(left: Sequence[int], right: Sequence[int]) -> float:
    left_bits = _validate_label(left)
    right_bits = _validate_label(right, len(left_bits))
    return 0.0 if left_bits == right_bits else 1.0


def graph_basis_amplitude(graph: SimpleGraph, label: Sequence[int], basis_index: int) -> float:
    """Real computational-basis amplitude of |G,z> for independent checks.

    |G> is the equal superposition whose phase is (-1) for every graph edge
    with both endpoint bits equal to one.  Z^z contributes (-1)^(z dot x).
    """

    bits_label = _validate_label(label, graph.qubits)
    if not 0 <= basis_index < 1 << graph.qubits:
        raise ValueError("basis index out of range")
    bits = tuple((basis_index >> i) & 1 for i in range(graph.qubits))
    phase = sum(bits[left] * bits[right] for left, right in graph.edges)
    phase += sum(label_bit * bit for label_bit, bit in zip(bits_label, bits))
    sign = -1.0 if phase & 1 else 1.0
    return sign / (2.0 ** (graph.qubits / 2.0))


def verify_generator_eigenrelation(
    graph: SimpleGraph,
    label: Sequence[int],
    generator: int,
    *,
    tolerance: float = 1e-12,
) -> bool:
    """Exhaustively verify K_i |G,z> = (-1)^{z_i}|G,z> for a small graph."""

    bits = _validate_label(label, graph.qubits)
    if not 0 <= generator < graph.qubits:
        raise ValueError("generator out of range")
    neighbor_mask = graph.adjacency_masks()[generator]
    eigenvalue = graph_generator_eigenvalue(bits, generator)
    for basis_index in range(1 << graph.qubits):
        z_phase = -1.0 if (basis_index & neighbor_mask).bit_count() & 1 else 1.0
        left = z_phase * graph_basis_amplitude(
            graph,
            bits,
            basis_index ^ (1 << generator),
        )
        right = eigenvalue * graph_basis_amplitude(graph, bits, basis_index)
        if abs(left - right) > tolerance:
            return False
    return True


def stabilizer_support_mask(graph: SimpleGraph, generator_mask: int) -> int:
    """Support of the product of generators selected by ``generator_mask``.

    In binary symplectic form the product has X component a and Z component
    Gamma a over GF(2), where Gamma is the graph adjacency matrix.  Its Pauli
    support is therefore support(a OR Gamma a).  Overall Pauli phase is
    irrelevant for support and local-reduction calculations.
    """

    if not 0 <= generator_mask < 1 << graph.qubits:
        raise ValueError("generator mask out of range")
    z_mask = 0
    for vertex, neighbor_mask in enumerate(graph.adjacency_masks()):
        if (generator_mask & neighbor_mask).bit_count() & 1:
            z_mask |= 1 << vertex
    return generator_mask | z_mask


def stabilizer_weight(graph: SimpleGraph, generator_mask: int) -> int:
    return stabilizer_support_mask(graph, generator_mask).bit_count()


def stabilizer_distance(graph: SimpleGraph, *, max_qubits: int = 20) -> int:
    """Minimum nonidentity stabilizer support weight by exact enumeration."""

    if graph.qubits > max_qubits:
        raise ValueError(f"exact stabilizer enumeration capped at {max_qubits} qubits")
    return min(stabilizer_weight(graph, mask) for mask in range(1, 1 << graph.qubits))


def cycle_stabilizer_distance(qubits: int) -> int:
    """Closed-form stabilizer distance for simple cycle graph states.

    C_3 and C_4 contain weight-two stabilizers.  For every C_n with n >= 5,
    each generator has weight three and no nonidentity generator product can
    have support one or two, so the distance is exactly three.
    """

    if qubits < 3:
        raise ValueError("a cycle graph requires at least three qubits")
    return 2 if qubits in (3, 4) else 3


def subset_reduction_is_maximally_mixed(
    graph: SimpleGraph,
    subset: Iterable[int],
    *,
    max_qubits: int = 20,
) -> bool:
    """Whether every graph-basis label is maximally mixed on ``subset``.

    For a stabilizer state, the reduced density matrix on S contains exactly
    the stabilizer elements whose support lies inside S.  Graph-basis labels
    change their signs but not their supports.  Therefore the reduction is
    I/2^|S| for every label iff identity is the only stabilizer supported in S.
    """

    if graph.qubits > max_qubits:
        raise ValueError(f"exact stabilizer enumeration capped at {max_qubits} qubits")
    vertices = tuple(sorted(set(int(vertex) for vertex in subset)))
    if any(not 0 <= vertex < graph.qubits for vertex in vertices):
        raise ValueError("subset vertex out of range")
    subset_mask = sum(1 << vertex for vertex in vertices)
    outside_mask = ((1 << graph.qubits) - 1) ^ subset_mask
    for generator_mask in range(1, 1 << graph.qubits):
        support = stabilizer_support_mask(graph, generator_mask)
        if support & outside_mask == 0:
            return False
    return True


def all_reductions_up_to_size_are_maximally_mixed(
    graph: SimpleGraph,
    locality: int,
    *,
    max_qubits: int = 16,
) -> bool:
    if not 0 <= locality <= graph.qubits:
        raise ValueError("locality must lie between zero and graph size")
    if graph.qubits > max_qubits:
        raise ValueError(f"subset audit capped at {max_qubits} qubits")
    return all(
        subset_reduction_is_maximally_mixed(graph, subset, max_qubits=max_qubits)
        for size in range(1, locality + 1)
        for subset in combinations(range(graph.qubits), size)
    )


def hamming_distance(left: Sequence[int], right: Sequence[int]) -> int:
    left_bits = _validate_label(left)
    right_bits = _validate_label(right, len(left_bits))
    return sum(a != b for a, b in zip(left_bits, right_bits))


def integer_hamming_distance(left: int, right: int) -> int:
    if left < 0 or right < 0:
        raise ValueError("codewords must be nonnegative integers")
    return (left ^ right).bit_count()


def minimum_hamming_distance_for_tv(qubits: int, epsilon: float) -> int:
    """Smallest integer d satisfying d/n > 2 epsilon."""

    if qubits < 1:
        raise ValueError("qubits must be positive")
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    return floor(2.0 * epsilon * qubits) + 1


def hamming_ball_volume(qubits: int, radius: int) -> int:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    if radius < 0:
        return 0
    return sum(comb(qubits, weight) for weight in range(min(radius, qubits) + 1))


def gilbert_code_size_lower_bound(qubits: int, minimum_distance: int) -> int:
    """Finite greedy/Gilbert lower bound for a binary code.

    A maximal code of minimum distance d has Hamming balls of radius d-1 that
    cover the cube.  Each ball contains V(n,d-1) words, so

        |C| >= ceil(2^n / V(n,d-1)).
    """

    if qubits < 1:
        raise ValueError("qubits must be positive")
    if minimum_distance < 1:
        raise ValueError("minimum distance must be positive")
    volume = hamming_ball_volume(qubits, minimum_distance - 1)
    words = 1 << qubits
    return (words + volume - 1) // volume


def gilbert_predictive_size_lower_bound(qubits: int, epsilon: float) -> int:
    return gilbert_code_size_lower_bound(
        qubits,
        minimum_hamming_distance_for_tv(qubits, epsilon),
    )


def _ceil_log2_integer(value: int) -> int:
    if value < 1:
        raise ValueError("value must be positive")
    return 0 if value == 1 else (value - 1).bit_length()


def gilbert_predictive_memory_lower_bound_bits(qubits: int, epsilon: float) -> int:
    return _ceil_log2_integer(gilbert_predictive_size_lower_bound(qubits, epsilon))


def binary_entropy(probability: float) -> float:
    p = float(probability)
    if not 0.0 <= p <= 1.0:
        raise ValueError("probability must lie in [0,1]")
    if p in (0.0, 1.0):
        return 0.0
    return -p * log2(p) - (1.0 - p) * log2(1.0 - p)


def asymptotic_gilbert_rate_for_tv(epsilon: float) -> float:
    """Asymptotic achievable predictive-code rate 1-H_2(2 epsilon).

    The positive-rate statement applies for 0 <= epsilon < 1/4.  At epsilon
    equal to 1/4 the expression reaches zero.  This is an asymptotic coding
    rate inside the declared normalized-Hamming query model, not a finite
    certificate for a particular block length.
    """

    if not 0.0 <= epsilon <= 0.25:
        raise ValueError("epsilon must lie in [0,1/4]")
    return 1.0 - binary_entropy(2.0 * epsilon)


def _hamming_ball_masks(qubits: int, radius: int) -> tuple[int, ...]:
    masks: list[int] = []
    for weight in range(min(radius, qubits) + 1):
        for positions in combinations(range(qubits), weight):
            mask = 0
            for position in positions:
                mask |= 1 << position
            masks.append(mask)
    return tuple(masks)


def greedy_binary_code(
    qubits: int,
    minimum_distance: int,
    *,
    max_qubits: int = 18,
) -> tuple[int, ...]:
    """Deterministic lexicographic Gilbert code for finite verification."""

    if qubits < 1:
        raise ValueError("qubits must be positive")
    if qubits > max_qubits:
        raise ValueError(f"explicit greedy code capped at {max_qubits} qubits")
    if minimum_distance < 1:
        raise ValueError("minimum distance must be positive")
    words = 1 << qubits
    available = bytearray(b"\x01") * words
    removal_masks = _hamming_ball_masks(qubits, minimum_distance - 1)
    chosen: list[int] = []
    for word in range(words):
        if not available[word]:
            continue
        chosen.append(word)
        for mask in removal_masks:
            available[word ^ mask] = 0
    return tuple(chosen)


def code_minimum_distance(codewords: Sequence[int]) -> int:
    words = tuple(int(word) for word in codewords)
    if len(words) < 2:
        return 0
    if any(word < 0 for word in words):
        raise ValueError("codewords must be nonnegative")
    return min(integer_hamming_distance(left, right) for left, right in combinations(words, 2))


def integer_to_label(word: int, qubits: int) -> BitLabel:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    if not 0 <= word < 1 << qubits:
        raise ValueError("word out of range")
    return tuple((word >> i) & 1 for i in range(qubits))
