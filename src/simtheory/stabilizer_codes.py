"""Exact bounded stabilizer-code and logical-predictive calculations.

The purpose of this module is to replace a vague Hilbert-space argument with an
operational one.

For an [[n,k,d]] stabilizer code, distance d means that every Pauli operator of
weight below d either

1. anticommutes with a stabilizer and is projected to zero on the code space, or
2. belongs to the stabilizer span and acts as a scalar on the code space.

Consequently every operator supported on fewer than d qubits has the same
expectation in every encoded state, and all encoded states have identical
reduced density matrices on every subset of fewer than d qubits.  Logical
information is locally hidden until an allowed observable reaches code distance.

The module implements binary-symplectic commutation, exact GF(2) rank and span,
normalizer enumeration, code distance, logical-coset leaders, small state-vector
projectors, and reduced-density checks.  The five-qubit perfect code is included
as a finite physical example: it is [[5,1,3]], so one logical predictive bit is
invisible to every one- and two-qubit measurement but accessible to a weight-three
logical Pauli query.

These are internal predictive-state statements for declared encoded families.
They are not evidence for simulation and do not identify parent-substrate cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import ceil, inf, log2
from typing import Iterable, Sequence

PAULI_ALPHABET = frozenset("IXYZ")
ComplexVector = tuple[complex, ...]
ComplexMatrix = tuple[tuple[complex, ...], ...]
BitLabel = tuple[int, ...]


def validate_pauli_string(pauli: str, qubits: int | None = None) -> str:
    word = str(pauli).upper()
    if not word:
        raise ValueError("Pauli string cannot be empty")
    if qubits is not None and len(word) != qubits:
        raise ValueError("Pauli string length does not match code size")
    if any(symbol not in PAULI_ALPHABET for symbol in word):
        raise ValueError("Pauli strings may contain only I, X, Y, and Z")
    return word


def pauli_masks(pauli: str) -> tuple[int, int]:
    word = validate_pauli_string(pauli)
    x_mask = 0
    z_mask = 0
    for qubit, symbol in enumerate(word):
        if symbol in "XY":
            x_mask |= 1 << qubit
        if symbol in "ZY":
            z_mask |= 1 << qubit
    return x_mask, z_mask


def pauli_vector(pauli: str) -> int:
    word = validate_pauli_string(pauli)
    x_mask, z_mask = pauli_masks(word)
    return x_mask | (z_mask << len(word))


def vector_masks(vector: int, qubits: int) -> tuple[int, int]:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    if not 0 <= vector < 1 << (2 * qubits):
        raise ValueError("binary symplectic vector out of range")
    mask = (1 << qubits) - 1
    return vector & mask, (vector >> qubits) & mask


def vector_pauli(vector: int, qubits: int) -> str:
    x_mask, z_mask = vector_masks(vector, qubits)
    symbols: list[str] = []
    for qubit in range(qubits):
        x = (x_mask >> qubit) & 1
        z = (z_mask >> qubit) & 1
        symbols.append("IXZY"[x + 2 * z])
    return "".join(symbols)


def pauli_weight(pauli: str) -> int:
    return sum(symbol != "I" for symbol in validate_pauli_string(pauli))


def vector_weight(vector: int, qubits: int) -> int:
    x_mask, z_mask = vector_masks(vector, qubits)
    return (x_mask | z_mask).bit_count()


def symplectic_inner(left: int, right: int, qubits: int) -> int:
    left_x, left_z = vector_masks(left, qubits)
    right_x, right_z = vector_masks(right, qubits)
    return (
        (left_x & right_z).bit_count()
        + (left_z & right_x).bit_count()
    ) & 1


def paulis_commute(left: str, right: str) -> bool:
    first = validate_pauli_string(left)
    second = validate_pauli_string(right, len(first))
    return symplectic_inner(pauli_vector(first), pauli_vector(second), len(first)) == 0


def gf2_rank(rows: Iterable[int]) -> int:
    """Rank of integer bit rows over GF(2)."""

    pivots: dict[int, int] = {}
    for supplied in rows:
        row = int(supplied)
        if row < 0:
            raise ValueError("GF(2) rows must be nonnegative")
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def gf2_span(rows: Iterable[int]) -> tuple[int, ...]:
    """Exact span of independent or dependent integer rows."""

    basis: list[int] = []
    for supplied in rows:
        row = int(supplied)
        if row < 0:
            raise ValueError("GF(2) rows must be nonnegative")
        if gf2_rank((*basis, row)) > len(basis):
            basis.append(row)
    span = [0]
    for row in basis:
        span += [word ^ row for word in span]
    return tuple(sorted(span))


@dataclass(frozen=True)
class StabilizerCode:
    """A +1 stabilizer code specified by commuting independent generators."""

    qubits: int
    generators: tuple[str, ...]
    name: str = "stabilizer-code"

    def __post_init__(self) -> None:
        if self.qubits < 1:
            raise ValueError("qubits must be positive")
        words = tuple(validate_pauli_string(word, self.qubits) for word in self.generators)
        if len(words) > self.qubits:
            raise ValueError("a stabilizer code has at most n independent generators")
        for left, right in combinations(words, 2):
            if not paulis_commute(left, right):
                raise ValueError("stabilizer generators must commute")
        vectors = tuple(pauli_vector(word) for word in words)
        if gf2_rank(vectors) != len(vectors):
            raise ValueError("stabilizer generators must be independent over GF(2)")
        object.__setattr__(self, "generators", words)

    @property
    def rank(self) -> int:
        return len(self.generators)

    @property
    def logical_qubits(self) -> int:
        return self.qubits - self.rank

    @property
    def generator_vectors(self) -> tuple[int, ...]:
        return tuple(pauli_vector(word) for word in self.generators)

    @property
    def stabilizer_span(self) -> tuple[int, ...]:
        return gf2_span(self.generator_vectors)

    def commutes_with_stabilizer_vector(self, vector: int) -> bool:
        vector_masks(vector, self.qubits)
        return all(
            symplectic_inner(vector, generator, self.qubits) == 0
            for generator in self.generator_vectors
        )

    def commutes_with_stabilizer(self, pauli: str) -> bool:
        word = validate_pauli_string(pauli, self.qubits)
        return self.commutes_with_stabilizer_vector(pauli_vector(word))

    def is_stabilizer_vector(self, vector: int) -> bool:
        vector_masks(vector, self.qubits)
        return vector in set(self.stabilizer_span)

    def is_stabilizer(self, pauli: str) -> bool:
        word = validate_pauli_string(pauli, self.qubits)
        return self.is_stabilizer_vector(pauli_vector(word))

    def pauli_restriction_type(self, pauli: str) -> str:
        """Return projected-zero, scalar, or logical for one physical Pauli."""

        word = validate_pauli_string(pauli, self.qubits)
        vector = pauli_vector(word)
        if not self.commutes_with_stabilizer_vector(vector):
            return "projected-zero"
        if self.is_stabilizer_vector(vector):
            return "scalar"
        return "logical"


def five_qubit_code() -> StabilizerCode:
    return StabilizerCode(
        5,
        (
            "XZZXI",
            "IXZZX",
            "XIXZZ",
            "ZXIXZ",
        ),
        name="five-qubit-perfect-code",
    )


def three_qubit_repetition_code() -> StabilizerCode:
    """Bit-flip repetition code, whose full quantum distance is only one."""

    return StabilizerCode(3, ("ZZI", "IZZ"), name="three-qubit-repetition-code")


def enumerate_normalizer_vectors(
    code: StabilizerCode,
    *,
    max_qubits: int = 10,
) -> tuple[int, ...]:
    if code.qubits > max_qubits:
        raise ValueError(f"normalizer enumeration capped at {max_qubits} qubits")
    return tuple(
        vector
        for vector in range(1 << (2 * code.qubits))
        if code.commutes_with_stabilizer_vector(vector)
    )


def stabilizer_code_distance(
    code: StabilizerCode,
    *,
    max_qubits: int = 10,
) -> int | None:
    """Minimum weight normalizer element outside the stabilizer span."""

    stabilizers = set(code.stabilizer_span)
    candidates = (
        vector_weight(vector, code.qubits)
        for vector in enumerate_normalizer_vectors(code, max_qubits=max_qubits)
        if vector not in stabilizers
    )
    return min(candidates, default=None)


def normalizer_coset_leaders(
    code: StabilizerCode,
    *,
    max_qubits: int = 10,
) -> tuple[int, ...]:
    """Minimum-weight representative for every N(S)/S logical Pauli coset."""

    stabilizers = set(code.stabilizer_span)
    remaining = set(enumerate_normalizer_vectors(code, max_qubits=max_qubits))
    leaders: list[int] = []
    while remaining:
        leader = min(
            remaining,
            key=lambda vector: (vector_weight(vector, code.qubits), vector),
        )
        leaders.append(leader)
        remaining.difference_update(leader ^ stabilizer for stabilizer in stabilizers)
    expected = 1 << (2 * code.logical_qubits)
    if len(leaders) != expected:
        raise AssertionError("normalizer quotient size does not match 4^k")
    return tuple(leaders)


def minimum_logical_paulis(
    code: StabilizerCode,
    *,
    max_qubits: int = 10,
) -> tuple[str, ...]:
    return tuple(
        vector_pauli(vector, code.qubits)
        for vector in normalizer_coset_leaders(code, max_qubits=max_qubits)
        if vector != 0
    )


def all_paulis_up_to_weight(qubits: int, maximum_weight: int) -> tuple[str, ...]:
    if qubits < 1:
        raise ValueError("qubits must be positive")
    if not 0 <= maximum_weight <= qubits:
        raise ValueError("maximum_weight must lie in [0,n]")
    words: list[str] = []
    for weight in range(maximum_weight + 1):
        for positions in combinations(range(qubits), weight):
            for symbols in product("XYZ", repeat=weight):
                word = ["I"] * qubits
                for position, symbol in zip(positions, symbols):
                    word[position] = symbol
                words.append("".join(word))
    return tuple(words)


def local_indistinguishability_certificate(
    code: StabilizerCode,
    locality: int,
    *,
    max_qubits: int = 10,
) -> bool:
    """Check that no Pauli of weight <= locality acts nontrivially logically."""

    if not 0 <= locality <= code.qubits:
        raise ValueError("locality must lie in [0,n]")
    if code.qubits > max_qubits:
        raise ValueError(f"bounded certificate capped at {max_qubits} qubits")
    return all(
        code.pauli_restriction_type(pauli) != "logical"
        for pauli in all_paulis_up_to_weight(code.qubits, locality)
    )


def predicted_local_blindness_threshold(
    code: StabilizerCode,
    *,
    max_qubits: int = 10,
) -> int | None:
    distance = stabilizer_code_distance(code, max_qubits=max_qubits)
    return None if distance is None else distance - 1


def quantum_singleton_slack(code: StabilizerCode, distance: int | None = None) -> int | None:
    """n-k-2(d-1); nonnegative for codes satisfying the quantum Singleton bound."""

    d = stabilizer_code_distance(code) if distance is None else int(distance)
    if d is None:
        return None
    if d < 1:
        raise ValueError("distance must be positive")
    return code.qubits - code.logical_qubits - 2 * (d - 1)


def apply_pauli_to_state(state: Sequence[complex], pauli: str) -> ComplexVector:
    """Apply a Hermitian tensor-product Pauli to a small state vector."""

    word = validate_pauli_string(pauli)
    expected_dimension = 1 << len(word)
    if len(state) != expected_dimension:
        raise ValueError("state dimension does not match Pauli size")
    output = [0j] * expected_dimension
    for basis_index, amplitude in enumerate(state):
        if amplitude == 0:
            continue
        target = basis_index
        phase = 1.0 + 0.0j
        for qubit, symbol in enumerate(word):
            bit = (basis_index >> qubit) & 1
            if symbol == "X":
                target ^= 1 << qubit
            elif symbol == "Z":
                if bit:
                    phase = -phase
            elif symbol == "Y":
                target ^= 1 << qubit
                phase *= -1j if bit else 1j
        output[target] += phase * amplitude
    return tuple(output)


def inner_product(left: Sequence[complex], right: Sequence[complex]) -> complex:
    if len(left) != len(right):
        raise ValueError("vectors must have equal dimension")
    return sum(a.conjugate() * b for a, b in zip(left, right))


def vector_norm(state: Sequence[complex]) -> float:
    return max(0.0, inner_product(state, state).real) ** 0.5


def normalize_state(state: Sequence[complex], *, tolerance: float = 1e-14) -> ComplexVector:
    norm = vector_norm(state)
    if norm <= tolerance:
        raise ValueError("cannot normalize the zero vector")
    return tuple(amplitude / norm for amplitude in state)


def project_pauli_eigenvalue(
    state: Sequence[complex],
    pauli: str,
    eigenvalue: int,
) -> ComplexVector:
    if eigenvalue not in (-1, 1):
        raise ValueError("eigenvalue must be -1 or +1")
    transformed = apply_pauli_to_state(state, pauli)
    return tuple(
        amplitude + eigenvalue * mapped
        for amplitude, mapped in zip(state, transformed)
    )


def construct_stabilizer_codeword(
    code: StabilizerCode,
    logical_z: str,
    logical_eigenvalue: int,
    *,
    tolerance: float = 1e-12,
) -> ComplexVector:
    """Construct one encoded logical-Z eigenstate by commuting projections."""

    logical = validate_pauli_string(logical_z, code.qubits)
    if logical_eigenvalue not in (-1, 1):
        raise ValueError("logical_eigenvalue must be -1 or +1")
    if not code.commutes_with_stabilizer(logical) or code.is_stabilizer(logical):
        raise ValueError("logical_z must commute with the stabilizer but lie outside it")
    constraints = (*code.generators, logical)
    eigenvalues = (*((1,) * code.rank), logical_eigenvalue)
    dimension = 1 << code.qubits
    for seed_index in range(dimension):
        state: ComplexVector = tuple(
            1.0 + 0.0j if index == seed_index else 0.0 + 0.0j
            for index in range(dimension)
        )
        for constraint, eigenvalue in zip(constraints, eigenvalues):
            state = project_pauli_eigenvalue(state, constraint, eigenvalue)
        if vector_norm(state) > tolerance:
            return normalize_state(state)
    raise AssertionError("commuting stabilizer projections produced no codeword")


def extract_bits(index: int, positions: Sequence[int]) -> int:
    result = 0
    for output_bit, position in enumerate(positions):
        result |= ((index >> position) & 1) << output_bit
    return result


def reduced_density_matrix(
    state: Sequence[complex],
    subset: Sequence[int],
) -> ComplexMatrix:
    """Partial trace of a pure state over the complement of ``subset``."""

    dimension = len(state)
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("state dimension must be a positive power of two")
    qubits = dimension.bit_length() - 1
    supplied = tuple(int(position) for position in subset)
    positions = tuple(sorted(set(supplied)))
    if len(positions) != len(supplied):
        raise ValueError("subset positions must be unique")
    if any(not 0 <= position < qubits for position in positions):
        raise ValueError("subset position out of range")
    complement = tuple(position for position in range(qubits) if position not in positions)
    subsystem_dimension = 1 << len(positions)
    fibers: dict[int, list[complex]] = {}
    for basis_index, amplitude in enumerate(state):
        environment = extract_bits(basis_index, complement)
        subsystem = extract_bits(basis_index, positions)
        vector = fibers.setdefault(environment, [0j] * subsystem_dimension)
        vector[subsystem] = amplitude
    matrix = [[0j] * subsystem_dimension for _ in range(subsystem_dimension)]
    for vector in fibers.values():
        for row in range(subsystem_dimension):
            for column in range(subsystem_dimension):
                matrix[row][column] += vector[row] * vector[column].conjugate()
    return tuple(tuple(row) for row in matrix)


def matrix_max_difference(left: ComplexMatrix, right: ComplexMatrix) -> float:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise ValueError("matrices must have equal shape")
    return max(
        (abs(a - b) for left_row, right_row in zip(left, right) for a, b in zip(left_row, right_row)),
        default=0.0,
    )


def all_codeword_reductions_equal(
    codewords: Sequence[Sequence[complex]],
    locality: int,
    *,
    tolerance: float = 1e-10,
) -> bool:
    if not codewords:
        raise ValueError("at least one codeword is required")
    dimension = len(codewords[0])
    if any(len(state) != dimension for state in codewords):
        raise ValueError("all codewords must have equal dimension")
    qubits = dimension.bit_length() - 1
    if not 0 <= locality <= qubits:
        raise ValueError("locality must lie in [0,n]")
    reference = codewords[0]
    return all(
        matrix_max_difference(
            reduced_density_matrix(reference, subset),
            reduced_density_matrix(state, subset),
        )
        <= tolerance
        for size in range(1, locality + 1)
        for subset in combinations(range(qubits), size)
        for state in codewords[1:]
    )


def logical_label_query_total_variation(
    left: Sequence[int],
    right: Sequence[int],
    weights: Sequence[float] | None = None,
) -> float:
    """Weighted-Hamming law for deterministic logical-Z coordinate queries."""

    first = tuple(int(bit) for bit in left)
    second = tuple(int(bit) for bit in right)
    if not first or len(first) != len(second):
        raise ValueError("logical labels must have equal positive length")
    if any(bit not in (0, 1) for bit in (*first, *second)):
        raise ValueError("logical labels must be binary")
    if weights is None:
        query_weights = tuple(1.0 / len(first) for _ in first)
    else:
        query_weights = tuple(float(weight) for weight in weights)
        if len(query_weights) != len(first):
            raise ValueError("one weight is required per logical coordinate")
        if any(weight < 0 for weight in query_weights):
            raise ValueError("query weights must be nonnegative")
        if abs(sum(query_weights) - 1.0) > 1e-12:
            raise ValueError("query weights must sum to one")
    return sum(
        weight
        for left_bit, right_bit, weight in zip(first, second, query_weights)
        if left_bit != right_bit
    )


def encoded_block_worst_query_memory_bits(
    blocks: int,
    logical_qubits_per_block: int,
    epsilon: float,
) -> int:
    """Exact logical-label memory below the deterministic-query half-TV threshold."""

    if blocks < 1 or logical_qubits_per_block < 1:
        raise ValueError("block and logical-qubit counts must be positive")
    tolerance = float(epsilon)
    if tolerance < 0:
        raise ValueError("epsilon must be nonnegative")
    logical_bits = blocks * logical_qubits_per_block
    return logical_bits if tolerance < 0.5 else 0
