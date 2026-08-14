"""Quantum-message causal-cut and random-access-code bounds.

A uniformly random m-bit record X is encoded before a future coordinate query
I is revealed.  The answering region receives a q-qubit system Q and later
chooses a measurement intended to recover X_I.

Without preshared entanglement, coordinatewise Fano and quantum data processing
give

    I(X;Q) >= m[1-H_2(epsilon)],

while the entropy of q qubits gives I(X;Q) <= q.  Hence

    q >= m[1-H_2(epsilon)].

With receiver-side entanglement B initially independent of X, sending q qubits
can increase I(X;B) by at most 2q, yielding

    q >= m[1-H_2(epsilon)]/2.

The factor two is tight for exact full-record transmission by superdense
coding: q preshared Bell pairs plus q transmitted qubits carry 2q classical
bits.  Entanglement changes the constant, not the linear dependence on m.

The module also implements the canonical 2->1 and 3->1 qubit random access
codes.  Their Bloch vectors point to square and cube vertices, giving success
probabilities (1+1/sqrt(2))/2 and (1+1/sqrt(3))/2 respectively.

These are internal quantum-information bounds for a declared causal interface.
They are not evidence for simulation and do not convert logical qubits into an
unknown parent substrate's hardware or energy.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import ceil, sqrt
from typing import Sequence

from .distributed_consistency import (
    uniform_index_information_lower_bound_bits,
    weighted_index_information_lower_bound_bits,
)
from .stabilizer_relations import binary_entropy

BlochVector = tuple[float, float, float]
BitRecord = tuple[int, ...]

X_AXIS: BlochVector = (1.0, 0.0, 0.0)
Y_AXIS: BlochVector = (0.0, 1.0, 0.0)
Z_AXIS: BlochVector = (0.0, 0.0, 1.0)


def _validate_record_bits(record_bits: int) -> int:
    bits = int(record_bits)
    if bits < 1:
        raise ValueError("record_bits must be positive")
    return bits


def _validate_qubits(qubits: int) -> int:
    count = int(qubits)
    if count < 0:
        raise ValueError("qubits must be nonnegative")
    return count


def _validate_error(error: float) -> float:
    value = float(error)
    if not 0.0 <= value <= 0.5:
        raise ValueError("error must lie in [0,1/2]")
    return value


def _validate_bits(bits: Sequence[int], expected_length: int | None = None) -> BitRecord:
    record = tuple(int(bit) for bit in bits)
    if not record:
        raise ValueError("record cannot be empty")
    if expected_length is not None and len(record) != expected_length:
        raise ValueError("record length mismatch")
    if any(bit not in (0, 1) for bit in record):
        raise ValueError("record must be binary")
    return record


def _validate_bloch(vector: Sequence[float]) -> BlochVector:
    values = tuple(float(component) for component in vector)
    if len(values) != 3:
        raise ValueError("Bloch vectors must have three coordinates")
    if sum(component * component for component in values) > 1.0 + 1e-12:
        raise ValueError("Bloch vector lies outside the unit ball")
    return values  # type: ignore[return-value]


def _normalize_axis(axis: Sequence[float]) -> BlochVector:
    values = tuple(float(component) for component in axis)
    if len(values) != 3:
        raise ValueError("measurement axes must have three coordinates")
    norm = sqrt(sum(component * component for component in values))
    if norm <= 0.0:
        raise ValueError("measurement axis cannot be zero")
    return tuple(component / norm for component in values)  # type: ignore[return-value]


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def unassisted_information_capacity_bits(qubits: int) -> int:
    """Holevo entropy ceiling H(Q)<=q for q transmitted qubits."""

    return _validate_qubits(qubits)


def entanglement_assisted_information_increment_bits(qubits: int) -> int:
    """Receiver mutual-information increase ceiling 2q for q sent qubits."""

    return 2 * _validate_qubits(qubits)


def unassisted_qrac_qubits_lower_bound(record_bits: int, error: float) -> float:
    return uniform_index_information_lower_bound_bits(record_bits, error)


def unassisted_qrac_integer_qubits_lower_bound(record_bits: int, error: float) -> int:
    return ceil(max(0.0, unassisted_qrac_qubits_lower_bound(record_bits, error) - 1e-12))


def entanglement_assisted_qrac_qubits_lower_bound(record_bits: int, error: float) -> float:
    return 0.5 * uniform_index_information_lower_bound_bits(record_bits, error)


def entanglement_assisted_qrac_integer_qubits_lower_bound(record_bits: int, error: float) -> int:
    return ceil(
        max(
            0.0,
            entanglement_assisted_qrac_qubits_lower_bound(record_bits, error) - 1e-12,
        )
    )


def weighted_unassisted_qrac_qubits_lower_bound(
    query_weights: Sequence[float],
    weighted_error: float,
) -> float:
    return weighted_index_information_lower_bound_bits(query_weights, weighted_error)


def weighted_entanglement_assisted_qrac_qubits_lower_bound(
    query_weights: Sequence[float],
    weighted_error: float,
) -> float:
    return 0.5 * weighted_index_information_lower_bound_bits(query_weights, weighted_error)


def exact_unassisted_qubits(record_bits: int) -> int:
    """Exact zero-error lower and trivial computational-basis upper bound."""

    return _validate_record_bits(record_bits)


def exact_entanglement_assisted_qubits(record_bits: int) -> int:
    """Exact lower and superdense-coding upper bound ceil(m/2)."""

    return ceil(_validate_record_bits(record_bits) / 2.0)


def superdense_classical_payload_bits(transmitted_qubits: int) -> int:
    return 2 * _validate_qubits(transmitted_qubits)


def superdense_exact_record_feasible(record_bits: int, transmitted_qubits: int) -> bool:
    bits = _validate_record_bits(record_bits)
    return superdense_classical_payload_bits(transmitted_qubits) >= bits


def query_known_before_message_exact_qubits(record_bits: int) -> int:
    """Once the coordinate is known, one orthogonal qubit encodes its one bit."""

    _validate_record_bits(record_bits)
    return 1


def inverse_binary_entropy(target_entropy: float, *, iterations: int = 200) -> float:
    """Inverse of H_2 on [0,1/2]."""

    target = float(target_entropy)
    if not 0.0 <= target <= 1.0:
        raise ValueError("target_entropy must lie in [0,1]")
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if target == 0.0:
        return 0.0
    if target == 1.0:
        return 0.5
    low = 0.0
    high = 0.5
    for _ in range(iterations):
        midpoint = 0.5 * (low + high)
        if binary_entropy(midpoint) < target:
            low = midpoint
        else:
            high = midpoint
    return 0.5 * (low + high)


def uniform_qrac_error_lower_bound(
    record_bits: int,
    transmitted_qubits: int,
    *,
    entanglement_assisted: bool = False,
) -> float:
    """Invert the information bound to obtain a minimum average error.

    This is a converse bound, not an assertion that a code attaining the error
    exists at every finite parameter pair.
    """

    bits = _validate_record_bits(record_bits)
    qubits = _validate_qubits(transmitted_qubits)
    accessible = (2 if entanglement_assisted else 1) * qubits
    if accessible >= bits:
        return 0.0
    required_entropy = 1.0 - accessible / bits
    return inverse_binary_entropy(required_entropy)


def qrac_2_to_1_bloch(record: Sequence[int]) -> BlochVector:
    bits = _validate_bits(record, 2)
    scale = 1.0 / sqrt(2.0)
    return (
        scale if bits[0] == 0 else -scale,
        0.0,
        scale if bits[1] == 0 else -scale,
    )


def qrac_3_to_1_bloch(record: Sequence[int]) -> BlochVector:
    bits = _validate_bits(record, 3)
    scale = 1.0 / sqrt(3.0)
    return tuple(scale if bit == 0 else -scale for bit in bits)  # type: ignore[return-value]


def canonical_qrac_axes(record_bits: int) -> tuple[BlochVector, ...]:
    bits = _validate_record_bits(record_bits)
    if bits == 2:
        return X_AXIS, Z_AXIS
    if bits == 3:
        return X_AXIS, Y_AXIS, Z_AXIS
    raise ValueError("canonical one-qubit QRAC axes are defined only for two or three bits")


def canonical_qrac_bloch(record: Sequence[int]) -> BlochVector:
    bits = _validate_bits(record)
    if len(bits) == 2:
        return qrac_2_to_1_bloch(bits)
    if len(bits) == 3:
        return qrac_3_to_1_bloch(bits)
    raise ValueError("canonical one-qubit QRAC is defined only for two or three bits")


def bloch_measurement_outcome_probability(
    vector: Sequence[float],
    axis: Sequence[float],
    outcome_sign: int,
) -> float:
    """Born probability (1+s r dot a)/2 for a projective qubit measurement."""

    bloch = _validate_bloch(vector)
    direction = _normalize_axis(axis)
    sign = int(outcome_sign)
    if sign not in (-1, 1):
        raise ValueError("outcome_sign must be -1 or +1")
    probability = 0.5 * (1.0 + sign * _dot(bloch, direction))
    return min(1.0, max(0.0, probability))


def canonical_qrac_success_probability_for_record(
    record: Sequence[int],
    query_index: int,
) -> float:
    bits = _validate_bits(record)
    axes = canonical_qrac_axes(len(bits))
    index = int(query_index)
    if not 0 <= index < len(bits):
        raise ValueError("query index out of range")
    desired_sign = 1 if bits[index] == 0 else -1
    return bloch_measurement_outcome_probability(
        canonical_qrac_bloch(bits),
        axes[index],
        desired_sign,
    )


def canonical_qrac_success_probability(record_bits: int) -> float:
    bits = _validate_record_bits(record_bits)
    if bits not in (2, 3):
        raise ValueError("canonical one-qubit QRAC is defined only for two or three bits")
    return 0.5 * (1.0 + 1.0 / sqrt(bits))


def canonical_qrac_error(record_bits: int) -> float:
    return 1.0 - canonical_qrac_success_probability(record_bits)


def brute_force_canonical_qrac_average_success(record_bits: int) -> float:
    bits = _validate_record_bits(record_bits)
    if bits not in (2, 3):
        raise ValueError("canonical one-qubit QRAC is defined only for two or three bits")
    total = 0.0
    count = 0
    for record in product((0, 1), repeat=bits):
        for query in range(bits):
            total += canonical_qrac_success_probability_for_record(record, query)
            count += 1
    return total / count


def qrac_information_slack_bits(
    record_bits: int,
    transmitted_qubits: int,
    achieved_error: float,
    *,
    entanglement_assisted: bool = False,
) -> float:
    """Accessible-information ceiling minus the Fano information requirement."""

    bits = _validate_record_bits(record_bits)
    qubits = _validate_qubits(transmitted_qubits)
    epsilon = _validate_error(achieved_error)
    capacity = (2 if entanglement_assisted else 1) * qubits
    required = uniform_index_information_lower_bound_bits(bits, epsilon)
    return capacity - required


@dataclass(frozen=True)
class QuantumCutBudget:
    """Qubit budget for one unresolved future coordinate-query cut."""

    transmitted_qubits: int
    entanglement_assisted: bool = False

    def __post_init__(self) -> None:
        _validate_qubits(self.transmitted_qubits)

    @property
    def classical_information_ceiling_bits(self) -> int:
        return (
            entanglement_assisted_information_increment_bits(self.transmitted_qubits)
            if self.entanglement_assisted
            else unassisted_information_capacity_bits(self.transmitted_qubits)
        )

    def uniform_error_converse(self, record_bits: int) -> float:
        return uniform_qrac_error_lower_bound(
            record_bits,
            self.transmitted_qubits,
            entanglement_assisted=self.entanglement_assisted,
        )
