"""Distributed causal-cut and reconciliation bounds for predictive state.

A hidden binary record X=(X_1,...,X_m) is available in an earlier region.  A
finite message or already-resident local state must cross a declared one-way
causal cut before a later query index I is revealed.  The later region must
answer X_I, or equivalently X_I xor Y_I when Y_I is locally known.

Exact zero-error answering is the one-way INDEX problem.  Every two distinct
records differ on some future query, so the encoder must be injective and needs
at least 2^m states, or m bits.

For uniform X and uniform I, binary Fano plus entropy subadditivity gives

    I(X;M|R) >= m [1-H_2(epsilon)],

where R is shared randomness independent of X.  Shared randomness coordinates
a protocol but carries no record information before communication.

For a nonuniform query distribution w, the weakest information lower bound
consistent with weighted average error epsilon maximizes sum_i H_2(e_i) under
sum_i w_i e_i <= epsilon.  Positive-weight coordinates satisfy

    e_i = 1 / (1 + 2^(lambda w_i)),

with lambda chosen to meet the error budget.  Rarely queried coordinates are
therefore forgotten first.

These are internal communication and predictive-state bounds for the declared
one-way interface.  They do not prove simulation, impose this architecture on
a simulator, or convert information bits into parent-universe hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import ceil, log2
from typing import Hashable, Mapping, Sequence

from .stabilizer_relations import binary_entropy

BitRecord = tuple[int, ...]
CollisionWitness = tuple[BitRecord, BitRecord, int]


def _validate_record(record: Sequence[int], expected_length: int | None = None) -> BitRecord:
    bits = tuple(int(bit) for bit in record)
    if not bits:
        raise ValueError("record cannot be empty")
    if expected_length is not None and len(bits) != expected_length:
        raise ValueError("record length mismatch")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("records must be binary")
    return bits


def _validate_record_bits(record_bits: int) -> int:
    bits = int(record_bits)
    if bits < 1:
        raise ValueError("record_bits must be positive")
    return bits


def _validate_error(error: float) -> float:
    value = float(error)
    if not 0.0 <= value <= 0.5:
        raise ValueError("error must lie in [0,1/2]")
    return value


def _validate_query_weights(weights: Sequence[float]) -> tuple[float, ...]:
    values = tuple(float(weight) for weight in weights)
    if not values:
        raise ValueError("query weights cannot be empty")
    if any(weight < 0.0 for weight in values):
        raise ValueError("query weights must be nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("query weights must sum to one")
    return values


def all_binary_records(record_bits: int) -> tuple[BitRecord, ...]:
    return tuple(product((0, 1), repeat=_validate_record_bits(record_bits)))


def first_differing_coordinate(left: Sequence[int], right: Sequence[int]) -> int | None:
    first = _validate_record(left)
    second = _validate_record(right, len(first))
    return next((index for index, pair in enumerate(zip(first, second)) if pair[0] != pair[1]), None)


def encoder_collision_witness(
    encoder: Mapping[BitRecord, Hashable],
    record_bits: int,
) -> CollisionWitness | None:
    """Return a message collision and a query it cannot answer for both records."""

    records = all_binary_records(record_bits)
    if set(encoder) != set(records):
        raise ValueError("encoder must define exactly one message for every record")
    seen: dict[Hashable, BitRecord] = {}
    for record in records:
        message = encoder[record]
        if message in seen:
            other = seen[message]
            coordinate = first_differing_coordinate(other, record)
            if coordinate is None:
                raise AssertionError("distinct records unexpectedly have no differing coordinate")
            return other, record, coordinate
        seen[message] = record
    return None


def exact_index_encoder_is_valid(
    encoder: Mapping[BitRecord, Hashable],
    record_bits: int,
) -> bool:
    return encoder_collision_witness(encoder, record_bits) is None


def exact_index_message_states(record_bits: int) -> int:
    return 1 << _validate_record_bits(record_bits)


def exact_index_bits_lower_bound(record_bits: int) -> int:
    return _validate_record_bits(record_bits)


def uniform_index_information_lower_bound_bits(record_bits: int, error: float) -> float:
    """Return m[1-H2(error)] for uniform record bits and query index."""

    bits = _validate_record_bits(record_bits)
    epsilon = _validate_error(error)
    return bits * (1.0 - binary_entropy(epsilon))


def uniform_index_state_bits_lower_bound(record_bits: int, error: float) -> int:
    information = uniform_index_information_lower_bound_bits(record_bits, error)
    return ceil(max(0.0, information - 1e-12))


def minimum_additional_communication_bits(
    record_bits: int,
    resident_state_bits: int,
    error: float,
) -> int:
    """Resident state plus later one-way communication must meet the cut bound."""

    resident = int(resident_state_bits)
    if resident < 0:
        raise ValueError("resident_state_bits must be nonnegative")
    required = uniform_index_information_lower_bound_bits(record_bits, error)
    return ceil(max(0.0, required - resident - 1e-12))


def exact_additional_communication_bits(record_bits: int, resident_state_bits: int) -> int:
    bits = _validate_record_bits(record_bits)
    resident = int(resident_state_bits)
    if resident < 0:
        raise ValueError("resident_state_bits must be nonnegative")
    return max(0, bits - resident)


def _logistic_error(lambda_value: float, weight: float) -> float:
    if weight == 0.0:
        return 0.5
    exponent = lambda_value * weight
    if exponent >= 1024.0:
        return 0.0
    return 1.0 / (1.0 + 2.0**exponent)


def weighted_optimal_error_allocation(
    query_weights: Sequence[float],
    weighted_error: float,
    *,
    iterations: int = 220,
) -> tuple[float, ...]:
    """Entropy-maximizing coordinate errors under a weighted error budget.

    Solves

        maximize sum_i H2(e_i)
        subject to sum_i w_i e_i <= epsilon, 0 <= e_i <= 1/2.

    The KKT equation on every positive-weight coordinate is

        log2((1-e_i)/e_i)=lambda w_i.

    Zero-weight coordinates are assigned error 1/2 because the future query
    distribution never tests them.
    """

    weights = _validate_query_weights(query_weights)
    epsilon = _validate_error(weighted_error)
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if epsilon >= 0.5:
        return tuple(0.5 for _ in weights)
    if epsilon == 0.0:
        return tuple(0.0 if weight > 0.0 else 0.5 for weight in weights)

    def achieved(lambda_value: float) -> float:
        return sum(weight * _logistic_error(lambda_value, weight) for weight in weights)

    positive_weights = tuple(weight for weight in weights if weight > 0.0)
    minimum_positive = min(positive_weights)
    # Since 1/(1+2^x) <= 2^-x, this analytic bracket guarantees
    # achieved(high) <= epsilon without an overflow-prone doubling loop.
    high = max(1.0, log2(1.0 / epsilon) / minimum_positive)
    low = 0.0
    if achieved(high) > epsilon + 1e-15:
        raise ArithmeticError("analytic KKT bracket failed")

    for _ in range(iterations):
        midpoint = 0.5 * (low + high)
        if achieved(midpoint) > epsilon:
            low = midpoint
        else:
            high = midpoint

    return tuple(_logistic_error(high, weight) for weight in weights)


def weighted_index_information_lower_bound_bits(
    query_weights: Sequence[float],
    weighted_error: float,
) -> float:
    allocation = weighted_optimal_error_allocation(query_weights, weighted_error)
    return sum(1.0 - binary_entropy(error) for error in allocation)


def weighted_index_state_bits_lower_bound(
    query_weights: Sequence[float],
    weighted_error: float,
) -> int:
    information = weighted_index_information_lower_bound_bits(query_weights, weighted_error)
    return ceil(max(0.0, information - 1e-12))


def weighted_error_of_allocation(
    query_weights: Sequence[float],
    coordinate_errors: Sequence[float],
) -> float:
    weights = _validate_query_weights(query_weights)
    errors = tuple(_validate_error(error) for error in coordinate_errors)
    if len(weights) != len(errors):
        raise ValueError("one error is required per query weight")
    return sum(weight * error for weight, error in zip(weights, errors))


def replicated_region_storage_lower_bound_bits(
    record_bits: int,
    error: float,
    regions: int,
    query_weights: Sequence[float] | None = None,
) -> int:
    """Sum of separate local-state bounds for causally isolated answer regions.

    This assumes no later communication and no shared store accessible to all
    regions.  With a shared accessible store, the replication conclusion does
    not apply to the sum of local storage.
    """

    bits = _validate_record_bits(record_bits)
    count = int(regions)
    if count < 1:
        raise ValueError("regions must be positive")
    if query_weights is None:
        per_region = uniform_index_state_bits_lower_bound(bits, error)
    else:
        weights = _validate_query_weights(query_weights)
        if len(weights) != bits:
            raise ValueError("query weight count must match record_bits")
        per_region = weighted_index_state_bits_lower_bound(weights, error)
    return count * per_region


def parity_reconciliation_information_lower_bound_bits(
    record_bits: int,
    error: float,
    query_weights: Sequence[float] | None = None,
) -> float:
    """Same lower bound for A_i xor B_i when B_i is locally known."""

    bits = _validate_record_bits(record_bits)
    if query_weights is None:
        return uniform_index_information_lower_bound_bits(bits, error)
    weights = _validate_query_weights(query_weights)
    if len(weights) != bits:
        raise ValueError("query weight count must match record_bits")
    return weighted_index_information_lower_bound_bits(weights, error)


def parity_reconciliation_answer(
    remote_record: Sequence[int],
    local_record: Sequence[int],
    query_index: int,
) -> int:
    remote = _validate_record(remote_record)
    local = _validate_record(local_record, len(remote))
    index = int(query_index)
    if not 0 <= index < len(remote):
        raise ValueError("query index out of range")
    return remote[index] ^ local[index]


def prefix_storage_average_error(record_bits: int, stored_prefix_bits: int) -> float:
    """Average error when a prefix is exact and unstored bits are guessed zero."""

    bits = _validate_record_bits(record_bits)
    stored = int(stored_prefix_bits)
    if not 0 <= stored <= bits:
        raise ValueError("stored_prefix_bits must lie in [0, record_bits]")
    return (bits - stored) / (2.0 * bits)


def prefix_storage_message(record: Sequence[int], stored_prefix_bits: int) -> BitRecord:
    bits = _validate_record(record)
    stored = int(stored_prefix_bits)
    if not 0 <= stored <= len(bits):
        raise ValueError("stored_prefix_bits must lie in [0, record length]")
    return bits[:stored]


def prefix_storage_answer(message: Sequence[int], query_index: int) -> int:
    prefix = tuple(int(bit) for bit in message)
    if any(bit not in (0, 1) for bit in prefix):
        raise ValueError("message must be binary")
    index = int(query_index)
    if index < 0:
        raise ValueError("query index must be nonnegative")
    return prefix[index] if index < len(prefix) else 0


def brute_force_prefix_storage_average_error(record_bits: int, stored_prefix_bits: int) -> float:
    bits = _validate_record_bits(record_bits)
    errors = 0
    trials = 0
    for record in all_binary_records(bits):
        message = prefix_storage_message(record, stored_prefix_bits)
        for index in range(bits):
            errors += prefix_storage_answer(message, index) != record[index]
            trials += 1
    return errors / trials


def causal_cut_capacity_deficit_bits(
    record_bits: int,
    available_bits: int,
    error: float,
    query_weights: Sequence[float] | None = None,
) -> float:
    """Positive shortfall between the information lower bound and cut capacity."""

    bits = _validate_record_bits(record_bits)
    capacity = int(available_bits)
    if capacity < 0:
        raise ValueError("available_bits must be nonnegative")
    if query_weights is None:
        required = uniform_index_information_lower_bound_bits(bits, error)
    else:
        weights = _validate_query_weights(query_weights)
        if len(weights) != bits:
            raise ValueError("query weight count must match record_bits")
        required = weighted_index_information_lower_bound_bits(weights, error)
    return max(0.0, required - capacity)


@dataclass(frozen=True)
class CausalCutBudget:
    """Bookkeeping for resident state plus later one-way communication."""

    resident_bits: int
    communication_bits: int

    def __post_init__(self) -> None:
        if self.resident_bits < 0 or self.communication_bits < 0:
            raise ValueError("cut budget components must be nonnegative")

    @property
    def total_bits(self) -> int:
        return self.resident_bits + self.communication_bits

    def uniform_error_feasible(self, record_bits: int, error: float) -> bool:
        required = uniform_index_information_lower_bound_bits(record_bits, error)
        return self.total_bits + 1e-12 >= required
