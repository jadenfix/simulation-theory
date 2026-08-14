"""Noisy relational consistency and predictive rate-distortion bounds.

This module adds independent local readout flips to the exact cat-state and
checkpoint models.

For an ell-qubit phase-labeled cat state, ideal local-X outcomes have global
parity (-1)^z.  If every local outcome is independently flipped with
probability p in [0,1/2], the observed parity is flipped with probability

    q_ell(p) = [1 - (1-2p)^ell] / 2,

and the surviving parity visibility is

    c_ell(p) = 1 - 2 q_ell(p) = (1-2p)^ell.

The complete noisy transcript law is

    P_z(y) = 2^{-ell} [1 + (-1)^z c_ell(p) product_i y_i].

Every proper marginal remains exactly uniform and phase-independent, while the
TV distance between opposite complete phase laws is c_ell(p).

At the online checkpoint after ell-1 observed outcomes in each of m blocks,
each required final outcome is transmitted through a BSC(q). Under a uniform
future block query the exact predictive metric is

    TV(P_s,P_t) = c d_H(s,t)/m,

where c=1-2q. Under worst-block queries, all 2^m signatures remain distinct for
any approximation tolerance epsilon<c/2, and one unbiased state suffices when
epsilon>=c/2.

For a uniformly random hidden signature and average predictive TV distortion D,
the exact single-letter rate-distortion function is the binary Hamming function
scaled by c:

    R(D) = 1 - H_2(D/c),  0 <= D <= c/2.

The proof uses conditional medians: for any internal state, an optimal predicted
Bernoulli bias can be replaced by +/-c without increasing expected absolute
bias loss.  The problem therefore reduces exactly to Bernoulli(1/2) Hamming
rate-distortion.

These are internal predictive-representation results for declared noise and
query models.  They are not parent-hardware bounds and are not evidence that
reality is simulated.
"""

from __future__ import annotations

from itertools import product
from math import ceil, comb, inf, log, log2, sqrt
from typing import Iterable, Sequence

from .stabilizer_relations import (
    binary_entropy,
    gilbert_code_size_lower_bound,
)

OutcomeVector = tuple[int, ...]
Signature = tuple[int, ...]


def _check_probability(value: float, *, name: str = "probability") -> float:
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"{name} must lie in [0,1]")
    return probability


def _check_crossover(crossover: float) -> float:
    probability = _check_probability(crossover, name="crossover probability")
    if probability > 0.5:
        raise ValueError("crossover probability must not exceed one half")
    return probability


def _validate_signs(values: Sequence[int], *, nonempty: bool = True) -> tuple[int, ...]:
    signs = tuple(int(value) for value in values)
    if nonempty and not signs:
        raise ValueError("sign vector cannot be empty")
    if any(value not in (-1, 1) for value in signs):
        raise ValueError("signs must be -1 or +1")
    return signs


def _validate_phase_bit(phase_bit: int) -> int:
    bit = int(phase_bit)
    if bit not in (0, 1):
        raise ValueError("phase bit must be zero or one")
    return bit


def _product_sign(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        if value not in (-1, 1):
            raise ValueError("signs must be -1 or +1")
        result *= value
    return result


def effective_parity_visibility(local_flip_probability: float, block_size: int) -> float:
    """Return c=(1-2p)^ell for independent local flips."""

    p = _check_crossover(local_flip_probability)
    if block_size < 1:
        raise ValueError("block size must be positive")
    return (1.0 - 2.0 * p) ** block_size


def effective_parity_flip_probability(local_flip_probability: float, block_size: int) -> float:
    """Return q=[1-(1-2p)^ell]/2, the probability of an odd flip count."""

    visibility = effective_parity_visibility(local_flip_probability, block_size)
    return 0.5 * (1.0 - visibility)


def explicit_odd_flip_probability(local_flip_probability: float, block_size: int) -> float:
    """Binomial odd-count enumeration used as an independent checker."""

    p = _check_crossover(local_flip_probability)
    if block_size < 1:
        raise ValueError("block size must be positive")
    return sum(
        comb(block_size, flips)
        * p**flips
        * (1.0 - p) ** (block_size - flips)
        for flips in range(1, block_size + 1, 2)
    )


def noisy_cat_transcript_probability(
    phase_bit: int,
    outcomes: Sequence[int],
    local_flip_probability: float,
) -> float:
    """Exact probability of one complete noisy local-X transcript."""

    bit = _validate_phase_bit(phase_bit)
    signs = _validate_signs(outcomes)
    if len(signs) < 2:
        raise ValueError("cat block size must be at least two")
    visibility = effective_parity_visibility(local_flip_probability, len(signs))
    target_sign = -1 if bit else 1
    return 2.0 ** (-len(signs)) * (
        1.0 + target_sign * visibility * _product_sign(signs)
    )


def noisy_cat_transcript_law(
    phase_bit: int,
    block_size: int,
    local_flip_probability: float,
) -> dict[OutcomeVector, float]:
    if block_size < 2:
        raise ValueError("cat block size must be at least two")
    return {
        outcomes: noisy_cat_transcript_probability(
            phase_bit,
            outcomes,
            local_flip_probability,
        )
        for outcomes in product((-1, 1), repeat=block_size)
    }


def noisy_cat_marginal_law(
    phase_bit: int,
    block_size: int,
    observed_positions: Sequence[int],
    local_flip_probability: float,
) -> dict[OutcomeVector, float]:
    """Exact selected marginal; every proper subset is uniform.

    For the complete subset this returns the complete noisy transcript law.
    """

    _validate_phase_bit(phase_bit)
    _check_crossover(local_flip_probability)
    if block_size < 2:
        raise ValueError("cat block size must be at least two")
    supplied = tuple(int(position) for position in observed_positions)
    positions = tuple(sorted(set(supplied)))
    if len(positions) != len(supplied):
        raise ValueError("observed positions must be unique")
    if any(not 0 <= position < block_size for position in positions):
        raise ValueError("observed position out of range")
    if len(positions) < block_size:
        probability = 2.0 ** (-len(positions))
        return {
            assignment: probability
            for assignment in product((-1, 1), repeat=len(positions))
        }
    return noisy_cat_transcript_law(
        phase_bit,
        block_size,
        local_flip_probability,
    )


def noisy_cat_phase_total_variation(
    local_flip_probability: float,
    block_size: int,
) -> float:
    """Exact TV between opposite complete noisy cat-phase transcript laws."""

    return effective_parity_visibility(local_flip_probability, block_size)


def brute_force_noisy_cat_phase_tv(
    local_flip_probability: float,
    block_size: int,
) -> float:
    first = noisy_cat_transcript_law(0, block_size, local_flip_probability)
    second = noisy_cat_transcript_law(1, block_size, local_flip_probability)
    return 0.5 * sum(abs(first[outcome] - second[outcome]) for outcome in first)


def bsc_mutual_information_bits(crossover: float) -> float:
    """Mutual information of a uniform binary input through BSC(q)."""

    q = _check_crossover(crossover)
    return 1.0 - binary_entropy(q)


def bsc_opposite_kl_nats(crossover: float) -> float:
    """KL(Bernoulli(q) || Bernoulli(1-q)) in nats."""

    q = _check_crossover(crossover)
    if q == 0.0:
        return inf
    if q == 0.5:
        return 0.0
    return (1.0 - 2.0 * q) * log((1.0 - q) / q)


def repeated_bsc_total_variation(crossover: float, repetitions: int) -> float:
    """Exact TV between r repeated parity observations under opposite phases."""

    q = _check_crossover(crossover)
    if repetitions < 0:
        raise ValueError("repetitions must be nonnegative")
    if repetitions == 0:
        return 0.0
    return 0.5 * sum(
        comb(repetitions, negative_count)
        * abs(
            q**negative_count * (1.0 - q) ** (repetitions - negative_count)
            - (1.0 - q) ** negative_count * q ** (repetitions - negative_count)
        )
        for negative_count in range(repetitions + 1)
    )


def repeated_bsc_bayes_error(crossover: float, repetitions: int) -> float:
    """Equal-prior optimal phase-classification error."""

    return 0.5 * (1.0 - repeated_bsc_total_variation(crossover, repetitions))


def minimum_repetitions_for_total_variation(
    crossover: float,
    target_tv: float,
    *,
    max_repetitions: int = 100_000,
) -> int | None:
    """Smallest exact repetition count reaching target TV, or None if absent."""

    q = _check_crossover(crossover)
    target = float(target_tv)
    if not 0.0 < target < 1.0:
        raise ValueError("target_tv must lie strictly between zero and one")
    if max_repetitions < 1:
        raise ValueError("max_repetitions must be positive")
    if q == 0.5:
        return None
    for repetitions in range(1, max_repetitions + 1):
        if repeated_bsc_total_variation(q, repetitions) >= target:
            return repetitions
    return None


def pinsker_repetitions_necessary_for_tv(
    crossover: float,
    target_tv: float,
) -> int | None:
    """KL/Pinsker necessary repetitions for a target TV separation.

    The result is necessary, not sufficient.  None means the hypotheses are
    identical and no finite number of IID parity observations can separate them.
    """

    q = _check_crossover(crossover)
    target = float(target_tv)
    if not 0.0 < target < 1.0:
        raise ValueError("target_tv must lie strictly between zero and one")
    divergence = bsc_opposite_kl_nats(q)
    if divergence == 0.0:
        return None
    if divergence == inf:
        return 1
    return max(1, ceil(2.0 * target * target / divergence))


def bsc_bhattacharyya_coefficient(crossover: float) -> float:
    q = _check_crossover(crossover)
    return 2.0 * sqrt(q * (1.0 - q))


def repeated_bsc_bayes_error_upper_bound(crossover: float, repetitions: int) -> float:
    """Bhattacharyya upper bound 0.5 [2 sqrt(q(1-q))]^r."""

    if repetitions < 0:
        raise ValueError("repetitions must be nonnegative")
    coefficient = bsc_bhattacharyya_coefficient(crossover)
    return 0.5 * coefficient**repetitions


def minimum_repetitions_bhattacharyya_sufficient(
    crossover: float,
    target_error: float,
) -> int | None:
    """Sufficient repetitions for the Bhattacharyya error bound <= target."""

    q = _check_crossover(crossover)
    target = float(target_error)
    if not 0.0 < target < 0.5:
        raise ValueError("target_error must lie strictly between zero and one half")
    coefficient = bsc_bhattacharyya_coefficient(q)
    if coefficient == 1.0:
        return None
    if coefficient == 0.0:
        return 1
    return max(1, ceil(log(2.0 * target) / log(coefficient)))


def _validate_signatures(left: Sequence[int], right: Sequence[int]) -> tuple[Signature, Signature]:
    first = _validate_signs(left)
    second = _validate_signs(right)
    if len(first) != len(second):
        raise ValueError("signatures must have equal length")
    return first, second


def _validate_weights(length: int, weights: Sequence[float] | None) -> tuple[float, ...]:
    if weights is None:
        return tuple(1.0 / length for _ in range(length))
    values = tuple(float(weight) for weight in weights)
    if len(values) != length:
        raise ValueError("one query weight is required per signature coordinate")
    if any(weight < 0.0 for weight in values):
        raise ValueError("query weights must be nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("query weights must sum to one")
    return values


def noisy_checkpoint_query_law(
    signature: Sequence[int],
    crossover: float,
    weights: Sequence[float] | None = None,
) -> dict[tuple[int, int], float]:
    signs = _validate_signs(signature)
    q = _check_crossover(crossover)
    query_weights = _validate_weights(len(signs), weights)
    return {
        (coordinate, outcome): weight
        * ((1.0 - q) if outcome == sign else q)
        for coordinate, (sign, weight) in enumerate(zip(signs, query_weights))
        for outcome in (-1, 1)
    }


def noisy_checkpoint_total_variation(
    left_signature: Sequence[int],
    right_signature: Sequence[int],
    crossover: float,
    weights: Sequence[float] | None = None,
) -> float:
    """Exact c times weighted Hamming distance, c=1-2q."""

    left, right = _validate_signatures(left_signature, right_signature)
    q = _check_crossover(crossover)
    query_weights = _validate_weights(len(left), weights)
    visibility = 1.0 - 2.0 * q
    return visibility * sum(
        weight
        for left_sign, right_sign, weight in zip(left, right, query_weights)
        if left_sign != right_sign
    )


def brute_force_noisy_checkpoint_tv(
    left_signature: Sequence[int],
    right_signature: Sequence[int],
    crossover: float,
    weights: Sequence[float] | None = None,
) -> float:
    first = noisy_checkpoint_query_law(left_signature, crossover, weights)
    second = noisy_checkpoint_query_law(right_signature, crossover, weights)
    return 0.5 * sum(abs(first[key] - second[key]) for key in first)


def noisy_checkpoint_worst_query_memory_bits(
    blocks: int,
    crossover: float,
    epsilon: float,
) -> int:
    """Sharp one-step worst-query memory threshold for all 2^m signatures."""

    if blocks < 1:
        raise ValueError("blocks must be positive")
    q = _check_crossover(crossover)
    tolerance = float(epsilon)
    if tolerance < 0.0:
        raise ValueError("epsilon must be nonnegative")
    visibility = 1.0 - 2.0 * q
    return blocks if 2.0 * tolerance < visibility else 0


def noisy_checkpoint_minimum_hamming_distance(
    blocks: int,
    crossover: float,
    epsilon: float,
) -> int:
    """Smallest d with c*d/m > 2 epsilon under uniform block queries."""

    if blocks < 1:
        raise ValueError("blocks must be positive")
    q = _check_crossover(crossover)
    tolerance = float(epsilon)
    if tolerance < 0.0:
        raise ValueError("epsilon must be nonnegative")
    visibility = 1.0 - 2.0 * q
    if visibility == 0.0:
        return blocks + 1
    return int((2.0 * tolerance * blocks) // visibility) + 1


def noisy_checkpoint_gilbert_size_lower_bound(
    blocks: int,
    crossover: float,
    epsilon: float,
) -> int:
    minimum_distance = noisy_checkpoint_minimum_hamming_distance(
        blocks,
        crossover,
        epsilon,
    )
    return gilbert_code_size_lower_bound(blocks, minimum_distance)


def _ceil_log2_integer(value: int) -> int:
    if value < 1:
        raise ValueError("value must be positive")
    return 0 if value == 1 else (value - 1).bit_length()


def noisy_checkpoint_gilbert_memory_lower_bound_bits(
    blocks: int,
    crossover: float,
    epsilon: float,
) -> int:
    return _ceil_log2_integer(
        noisy_checkpoint_gilbert_size_lower_bound(blocks, crossover, epsilon)
    )


def noisy_average_predictive_rate_distortion_per_bit(
    crossover: float,
    average_tv_distortion: float,
) -> float:
    """Exact Bernoulli rate-distortion R(D)=1-H2(D/c) for D<=c/2.

    The hidden signature bit is uniform.  A decoder may output any Bernoulli
    bias in [-1,1].  Conditional median optimality reduces the absolute-bias TV
    distortion exactly to c times binary Hamming distortion.
    """

    q = _check_crossover(crossover)
    distortion = float(average_tv_distortion)
    if distortion < 0.0:
        raise ValueError("average_tv_distortion must be nonnegative")
    visibility = 1.0 - 2.0 * q
    if visibility == 0.0 or distortion >= 0.5 * visibility:
        return 0.0
    return 1.0 - binary_entropy(distortion / visibility)


def noisy_average_predictive_information_lower_bound_bits(
    blocks: int,
    crossover: float,
    average_tv_distortion: float,
) -> float:
    if blocks < 1:
        raise ValueError("blocks must be positive")
    return blocks * noisy_average_predictive_rate_distortion_per_bit(
        crossover,
        average_tv_distortion,
    )


def noisy_average_predictive_memory_lower_bound_bits(
    blocks: int,
    crossover: float,
    average_tv_distortion: float,
) -> int:
    """Integer state-memory consequence of the information lower bound."""

    information = noisy_average_predictive_information_lower_bound_bits(
        blocks,
        crossover,
        average_tv_distortion,
    )
    return ceil(max(0.0, information - 1e-12))


def bsc_codeword_total_variation(
    differing_coordinates: int,
    crossover: float,
) -> float:
    """Exact TV between two product-BSC codeword laws at Hamming distance h."""

    if differing_coordinates < 0:
        raise ValueError("differing_coordinates must be nonnegative")
    q = _check_crossover(crossover)
    h = differing_coordinates
    if h == 0:
        return 0.0
    return 0.5 * sum(
        comb(h, negative_count)
        * abs(
            q**negative_count * (1.0 - q) ** (h - negative_count)
            - (1.0 - q) ** negative_count * q ** (h - negative_count)
        )
        for negative_count in range(h + 1)
    )


def bsc_codeword_tv_bhattacharyya_lower_bound(
    differing_coordinates: int,
    crossover: float,
) -> float:
    """Lower bound TV >= 1-[2 sqrt(q(1-q))]^h."""

    if differing_coordinates < 0:
        raise ValueError("differing_coordinates must be nonnegative")
    coefficient = bsc_bhattacharyya_coefficient(crossover)
    return 1.0 - coefficient**differing_coordinates
