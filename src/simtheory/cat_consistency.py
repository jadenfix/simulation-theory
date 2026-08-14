"""Distributed-correlation and online-consistency bounds from cat states.

For one block of ell qubits, define the phase-labeled cat state

    |Cat_z> = (|0^ell> + (-1)^z |1^ell>) / sqrt(2),  z in {0,1}.

If every qubit is measured locally in the X basis with outcomes x_i in
{-1,+1}, then

    P_z(x_1,...,x_ell) = 2^{-(ell-1)}

when product_i x_i = (-1)^z, and zero otherwise.  Every proper marginal is
uniform and independent of z, while the complete transcript determines z by a
global parity relation.

This yields two distinct predictive-state lower bounds.

1. Hidden relational information.  For m independent blocks labeled by
   z in {0,1}^m, the 2^m complete transcript laws have disjoint supports, even
   though no query omitting at least one qubit from each differing block sees
   the label.

2. Streaming consistency memory.  After an online renderer has emitted ell-1
   local X outcomes in every block, it must retain the accumulated parity of
   each block.  There are exactly 2^m predictive-equivalence classes at that
   checkpoint, so exact continuation requires exactly m bits of dynamic state.
   The lower bound remains m bits for worst-block approximation error less than
   1/2.  It is tight because the parity vector itself is a sufficient state.

These are bounded internal consistency results.  They do not imply that a
parent substrate uses classical bits and do not constitute evidence that
reality is simulated.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Sequence

from .stabilizer_relations import gilbert_predictive_memory_lower_bound_bits

OutcomeVector = tuple[int, ...]
PhaseLabel = tuple[int, ...]
CheckpointSignature = tuple[int, ...]


def _phase_sign(phase_bit: int) -> int:
    bit = int(phase_bit)
    if bit not in (0, 1):
        raise ValueError("phase bit must be zero or one")
    return -1 if bit else 1


def _validate_label(label: Sequence[int]) -> PhaseLabel:
    bits = tuple(int(bit) for bit in label)
    if not bits:
        raise ValueError("label cannot be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("label must be binary")
    return bits


def _validate_outcomes(outcomes: Sequence[int], *, expected_length: int | None = None) -> OutcomeVector:
    values = tuple(int(outcome) for outcome in outcomes)
    if expected_length is not None and len(values) != expected_length:
        raise ValueError("outcome vector has the wrong length")
    if any(outcome not in (-1, 1) for outcome in values):
        raise ValueError("outcomes must be -1 or +1")
    return values


def _product_sign(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        if value not in (-1, 1):
            raise ValueError("signs must be -1 or +1")
        result *= value
    return result


def cat_x_transcript_probability(phase_bit: int, outcomes: Sequence[int]) -> float:
    """Exact local-X transcript probability for one cat block."""

    values = _validate_outcomes(outcomes)
    if len(values) < 2:
        raise ValueError("cat block size must be at least two")
    if _product_sign(values) != _phase_sign(phase_bit):
        return 0.0
    return 2.0 ** (-(len(values) - 1))


def cat_x_transcript_law(phase_bit: int, block_size: int) -> dict[OutcomeVector, float]:
    if block_size < 2:
        raise ValueError("block size must be at least two")
    return {
        outcomes: cat_x_transcript_probability(phase_bit, outcomes)
        for outcomes in product((-1, 1), repeat=block_size)
    }


def cat_x_marginal_law(
    phase_bit: int,
    block_size: int,
    observed_positions: Sequence[int],
) -> dict[OutcomeVector, float]:
    """Exact marginal on selected X outcomes.

    Every proper subset is uniform and phase-independent.  The complete subset
    is the parity-constrained full transcript law.
    """

    _phase_sign(phase_bit)
    if block_size < 2:
        raise ValueError("block size must be at least two")
    positions = tuple(sorted(set(int(position) for position in observed_positions)))
    if len(positions) != len(tuple(observed_positions)):
        raise ValueError("observed positions must be unique")
    if any(not 0 <= position < block_size for position in positions):
        raise ValueError("observed position out of range")
    if len(positions) < block_size:
        probability = 2.0 ** (-len(positions))
        return {
            assignment: probability
            for assignment in product((-1, 1), repeat=len(positions))
        }
    return cat_x_transcript_law(phase_bit, block_size)


def cat_x_marginal_total_variation(
    left_phase: int,
    right_phase: int,
    block_size: int,
    observed_positions: Sequence[int],
) -> float:
    """Zero on every proper subset; one on the full block for opposite phases."""

    left_sign = _phase_sign(left_phase)
    right_sign = _phase_sign(right_phase)
    positions = tuple(sorted(set(int(position) for position in observed_positions)))
    if any(not 0 <= position < block_size for position in positions):
        raise ValueError("observed position out of range")
    if left_sign == right_sign or len(positions) < block_size:
        return 0.0
    return 1.0


def block_cat_x_transcript_probability(
    label: Sequence[int],
    block_size: int,
    outcomes: Sequence[int],
) -> float:
    bits = _validate_label(label)
    if block_size < 2:
        raise ValueError("block size must be at least two")
    values = _validate_outcomes(outcomes, expected_length=len(bits) * block_size)
    probability = 1.0
    for block, phase_bit in enumerate(bits):
        start = block * block_size
        probability *= cat_x_transcript_probability(
            phase_bit,
            values[start : start + block_size],
        )
        if probability == 0.0:
            return 0.0
    return probability


def block_cat_x_transcript_law(
    label: Sequence[int],
    block_size: int,
    *,
    max_qubits: int = 20,
) -> dict[OutcomeVector, float]:
    bits = _validate_label(label)
    total_qubits = len(bits) * block_size
    if block_size < 2:
        raise ValueError("block size must be at least two")
    if total_qubits > max_qubits:
        raise ValueError(f"explicit transcript enumeration capped at {max_qubits} qubits")
    return {
        outcomes: block_cat_x_transcript_probability(bits, block_size, outcomes)
        for outcomes in product((-1, 1), repeat=total_qubits)
    }


def block_cat_full_transcript_tv(
    left_label: Sequence[int],
    right_label: Sequence[int],
) -> float:
    left = _validate_label(left_label)
    right = _validate_label(right_label)
    if len(left) != len(right):
        raise ValueError("labels must have equal length")
    return 0.0 if left == right else 1.0


def block_cat_marginal_tv(
    left_label: Sequence[int],
    right_label: Sequence[int],
    block_size: int,
    observed_positions: Sequence[int],
) -> float:
    """Exact marginal TV for selected physical qubit positions.

    A differing phase bit becomes visible exactly when every qubit in that
    block is included.  Otherwise that block's selected marginal is uniform.
    Product factors are therefore either identical or support-disjoint, so the
    total marginal TV is exactly zero or one.
    """

    left = _validate_label(left_label)
    right = _validate_label(right_label)
    if len(left) != len(right):
        raise ValueError("labels must have equal length")
    if block_size < 2:
        raise ValueError("block size must be at least two")
    total_qubits = len(left) * block_size
    positions = set(int(position) for position in observed_positions)
    if len(positions) != len(tuple(observed_positions)):
        raise ValueError("observed positions must be unique")
    if any(not 0 <= position < total_qubits for position in positions):
        raise ValueError("observed position out of range")
    for block, (left_bit, right_bit) in enumerate(zip(left, right)):
        if left_bit == right_bit:
            continue
        block_positions = set(range(block * block_size, (block + 1) * block_size))
        if block_positions <= positions:
            return 1.0
    return 0.0


def checkpoint_signature(
    label: Sequence[int],
    prefix_parities: Sequence[int],
) -> CheckpointSignature:
    """Required final X outcome in each block after ell-1 outcomes are known."""

    bits = _validate_label(label)
    parities = _validate_outcomes(prefix_parities, expected_length=len(bits))
    return tuple(_phase_sign(bit) * parity for bit, parity in zip(bits, parities))


def _validate_block_weights(blocks: int, weights: Sequence[float] | None) -> tuple[float, ...]:
    if weights is None:
        return tuple(1.0 / blocks for _ in range(blocks))
    values = tuple(float(weight) for weight in weights)
    if len(values) != blocks:
        raise ValueError("one query weight is required per block")
    if any(weight < 0.0 for weight in values):
        raise ValueError("query weights must be nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("query weights must sum to one")
    return values


def checkpoint_joint_query_law(
    label: Sequence[int],
    prefix_parities: Sequence[int],
    weights: Sequence[float] | None = None,
) -> dict[tuple[int, int], float]:
    """Law over a selected block and its parity-forced final X outcome."""

    signature = checkpoint_signature(label, prefix_parities)
    block_weights = _validate_block_weights(len(signature), weights)
    law: dict[tuple[int, int], float] = {}
    for block, (required, weight) in enumerate(zip(signature, block_weights)):
        for outcome in (-1, 1):
            law[(block, outcome)] = weight if outcome == required else 0.0
    return law


def checkpoint_total_variation(
    left_label: Sequence[int],
    left_prefix_parities: Sequence[int],
    right_label: Sequence[int],
    right_prefix_parities: Sequence[int],
    weights: Sequence[float] | None = None,
) -> float:
    left_signature = checkpoint_signature(left_label, left_prefix_parities)
    right_signature = checkpoint_signature(right_label, right_prefix_parities)
    if len(left_signature) != len(right_signature):
        raise ValueError("checkpoint states must have equal block counts")
    block_weights = _validate_block_weights(len(left_signature), weights)
    return sum(
        weight
        for left, right, weight in zip(left_signature, right_signature, block_weights)
        if left != right
    )


def brute_force_checkpoint_tv(
    left_label: Sequence[int],
    left_prefix_parities: Sequence[int],
    right_label: Sequence[int],
    right_prefix_parities: Sequence[int],
    weights: Sequence[float] | None = None,
) -> float:
    left = checkpoint_joint_query_law(left_label, left_prefix_parities, weights)
    right = checkpoint_joint_query_law(right_label, right_prefix_parities, weights)
    return 0.5 * sum(abs(left[key] - right[key]) for key in left)


def checkpoint_worst_query_distance(
    left_label: Sequence[int],
    left_prefix_parities: Sequence[int],
    right_label: Sequence[int],
    right_prefix_parities: Sequence[int],
) -> float:
    left = checkpoint_signature(left_label, left_prefix_parities)
    right = checkpoint_signature(right_label, right_prefix_parities)
    if len(left) != len(right):
        raise ValueError("checkpoint states must have equal block counts")
    return 0.0 if left == right else 1.0


def checkpoint_exact_predictive_state_count(blocks: int) -> int:
    """Exactly 2^m parity signatures occur at the ell-1 checkpoint."""

    if blocks < 1:
        raise ValueError("blocks must be positive")
    return 1 << blocks


def checkpoint_exact_memory_bits(blocks: int) -> int:
    if blocks < 1:
        raise ValueError("blocks must be positive")
    return blocks


def checkpoint_worst_query_memory_lower_bound_bits(blocks: int, epsilon: float) -> int:
    """Worst-query approximate memory lower bound.

    Distinct checkpoint signatures differ by deterministic opposite outcomes on
    some final-block query, so their worst-query TV is one.  No one predictive
    state can approximate both within epsilon < 1/2.  At epsilon >= 1/2 this
    function returns only the trivial lower bound zero.
    """

    if blocks < 1:
        raise ValueError("blocks must be positive")
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    return blocks if epsilon < 0.5 else 0


def checkpoint_average_query_memory_lower_bound_bits(blocks: int, epsilon: float) -> int:
    """Finite Gilbert lower bound under a uniformly random final-block query."""

    return gilbert_predictive_memory_lower_bound_bits(blocks, epsilon)


def prefix_parity_vectors(blocks: int) -> tuple[OutcomeVector, ...]:
    if blocks < 1:
        raise ValueError("blocks must be positive")
    return tuple(product((-1, 1), repeat=blocks))


@dataclass(frozen=True)
class CatConsistencyState:
    """Explicit sufficient state for exact online local-X generation.

    ``counts[b]`` records how many outcomes have been emitted in block b and
    ``parities[b]`` stores their product.  Once ell-1 outcomes have been emitted,
    the final outcome is fixed by the hidden phase label and stored parity.
    """

    counts: tuple[int, ...]
    parities: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.counts or len(self.counts) != len(self.parities):
            raise ValueError("counts and parities must have equal positive length")
        if any(count < 0 for count in self.counts):
            raise ValueError("counts must be nonnegative")
        _validate_outcomes(self.parities, expected_length=len(self.counts))

    @classmethod
    def initial(cls, blocks: int) -> "CatConsistencyState":
        if blocks < 1:
            raise ValueError("blocks must be positive")
        return cls(tuple(0 for _ in range(blocks)), tuple(1 for _ in range(blocks)))

    def observe(self, block: int, outcome: int, block_size: int) -> "CatConsistencyState":
        if block_size < 2:
            raise ValueError("block size must be at least two")
        if not 0 <= block < len(self.counts):
            raise ValueError("block out of range")
        if outcome not in (-1, 1):
            raise ValueError("outcome must be -1 or +1")
        if self.counts[block] >= block_size:
            raise ValueError("block is already complete")
        counts = list(self.counts)
        parities = list(self.parities)
        counts[block] += 1
        parities[block] *= outcome
        return CatConsistencyState(tuple(counts), tuple(parities))

    def next_outcome_law(
        self,
        label: Sequence[int],
        block: int,
        block_size: int,
    ) -> dict[int, float]:
        bits = _validate_label(label)
        if len(bits) != len(self.counts):
            raise ValueError("label length does not match state")
        if block_size < 2:
            raise ValueError("block size must be at least two")
        if not 0 <= block < len(self.counts):
            raise ValueError("block out of range")
        count = self.counts[block]
        if count >= block_size:
            raise ValueError("block is already complete")
        if count < block_size - 1:
            return {-1: 0.5, 1: 0.5}
        required = _phase_sign(bits[block]) * self.parities[block]
        return {-1: 1.0 if required == -1 else 0.0, 1: 1.0 if required == 1 else 0.0}
