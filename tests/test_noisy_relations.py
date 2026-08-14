from itertools import product
from math import comb, isclose

import pytest

from simtheory.noisy_relations import (
    bsc_codeword_total_variation,
    bsc_codeword_tv_bhattacharyya_lower_bound,
    bsc_mutual_information_bits,
    bsc_opposite_kl_nats,
    brute_force_noisy_cat_phase_tv,
    brute_force_noisy_checkpoint_tv,
    effective_parity_flip_probability,
    effective_parity_visibility,
    explicit_odd_flip_probability,
    minimum_repetitions_bhattacharyya_sufficient,
    minimum_repetitions_for_total_variation,
    noisy_average_predictive_information_lower_bound_bits,
    noisy_average_predictive_memory_lower_bound_bits,
    noisy_average_predictive_rate_distortion_per_bit,
    noisy_cat_marginal_law,
    noisy_cat_phase_total_variation,
    noisy_cat_transcript_law,
    noisy_checkpoint_gilbert_memory_lower_bound_bits,
    noisy_checkpoint_minimum_hamming_distance,
    noisy_checkpoint_total_variation,
    noisy_checkpoint_worst_query_memory_bits,
    pinsker_repetitions_necessary_for_tv,
    repeated_bsc_bayes_error,
    repeated_bsc_bayes_error_upper_bound,
    repeated_bsc_total_variation,
)


def _marginalize_full_law(law, positions):
    marginal = {}
    for outcomes, probability in law.items():
        key = tuple(outcomes[position] for position in positions)
        marginal[key] = marginal.get(key, 0.0) + probability
    return marginal


def test_effective_parity_noise_matches_odd_binomial_enumeration():
    for p in (0.0, 0.01, 0.1, 0.25, 0.5):
        for block_size in range(1, 11):
            q = effective_parity_flip_probability(p, block_size)
            brute = explicit_odd_flip_probability(p, block_size)
            assert isclose(q, brute, rel_tol=1e-12, abs_tol=1e-12)
            assert isclose(1.0 - 2.0 * q, effective_parity_visibility(p, block_size), abs_tol=1e-12)


def test_noisy_cat_transcript_law_normalizes_and_has_expected_phase_tv():
    for p in (0.0, 0.04, 0.2, 0.5):
        for block_size in (2, 3, 5, 7):
            plus = noisy_cat_transcript_law(0, block_size, p)
            minus = noisy_cat_transcript_law(1, block_size, p)
            assert isclose(sum(plus.values()), 1.0, abs_tol=1e-12)
            assert isclose(sum(minus.values()), 1.0, abs_tol=1e-12)
            assert min(plus.values()) >= -1e-15
            assert min(minus.values()) >= -1e-15
            expected = effective_parity_visibility(p, block_size)
            assert isclose(noisy_cat_phase_total_variation(p, block_size), expected)
            assert isclose(brute_force_noisy_cat_phase_tv(p, block_size), expected, abs_tol=1e-12)


def test_every_proper_noisy_cat_marginal_is_exactly_uniform_and_phase_blind():
    block_size = 6
    p = 0.17
    plus_full = noisy_cat_transcript_law(0, block_size, p)
    minus_full = noisy_cat_transcript_law(1, block_size, p)
    for positions in ((0,), (1, 4), (0, 2, 3), (0, 1, 2, 4, 5)):
        analytic_plus = noisy_cat_marginal_law(0, block_size, positions, p)
        analytic_minus = noisy_cat_marginal_law(1, block_size, positions, p)
        brute_plus = _marginalize_full_law(plus_full, positions)
        brute_minus = _marginalize_full_law(minus_full, positions)
        assert analytic_plus == analytic_minus
        assert all(isclose(value, 2.0 ** (-len(positions)), abs_tol=1e-12) for value in analytic_plus.values())
        for assignment in analytic_plus:
            assert isclose(analytic_plus[assignment], brute_plus[assignment], abs_tol=1e-12)
            assert isclose(analytic_minus[assignment], brute_minus[assignment], abs_tol=1e-12)


def test_noiseless_and_maximally_noisy_boundaries():
    assert noisy_cat_phase_total_variation(0.0, 9) == 1.0
    assert isclose(noisy_cat_phase_total_variation(0.5, 9), 0.0, abs_tol=1e-15)
    assert bsc_mutual_information_bits(0.0) == 1.0
    assert isclose(bsc_mutual_information_bits(0.5), 0.0, abs_tol=1e-15)
    assert bsc_opposite_kl_nats(0.0) == float("inf")
    assert bsc_opposite_kl_nats(0.5) == 0.0


def test_repeated_bsc_tv_is_monotone_and_bayes_error_identity_holds():
    q = 0.2
    values = [repeated_bsc_total_variation(q, repetitions) for repetitions in range(9)]
    assert values[0] == 0.0
    assert isclose(values[1], 1.0 - 2.0 * q, abs_tol=1e-12)
    assert all(right + 1e-12 >= left for left, right in zip(values, values[1:]))
    for repetitions, tv in enumerate(values):
        assert isclose(repeated_bsc_bayes_error(q, repetitions), 0.5 * (1.0 - tv), abs_tol=1e-12)
        assert repeated_bsc_bayes_error(q, repetitions) <= repeated_bsc_bayes_error_upper_bound(q, repetitions) + 1e-12


def test_exact_and_information_bound_repetition_counts_have_correct_order():
    q = 0.15
    target_tv = 0.9
    exact = minimum_repetitions_for_total_variation(q, target_tv, max_repetitions=200)
    necessary = pinsker_repetitions_necessary_for_tv(q, target_tv)
    assert exact is not None
    assert necessary is not None
    assert necessary <= exact
    assert repeated_bsc_total_variation(q, exact) >= target_tv
    if exact > 1:
        assert repeated_bsc_total_variation(q, exact - 1) < target_tv

    sufficient = minimum_repetitions_bhattacharyya_sufficient(q, 0.01)
    assert sufficient is not None
    assert repeated_bsc_bayes_error_upper_bound(q, sufficient) <= 0.01 + 1e-15
    if sufficient > 1:
        assert repeated_bsc_bayes_error_upper_bound(q, sufficient - 1) > 0.01 - 1e-15


def test_noisy_checkpoint_geometry_matches_brute_force_weighted_hamming():
    left = (1, -1, 1, 1, -1)
    right = (-1, -1, 1, -1, -1)
    q = 0.12
    weights = (0.05, 0.1, 0.2, 0.25, 0.4)
    expected = (1.0 - 2.0 * q) * (weights[0] + weights[3])
    assert isclose(noisy_checkpoint_total_variation(left, right, q, weights), expected)
    assert isclose(brute_force_noisy_checkpoint_tv(left, right, q, weights), expected)
    assert isclose(noisy_checkpoint_total_variation(left, right, q), (1.0 - 2.0 * q) * 2.0 / 5.0)


def test_worst_query_memory_has_a_sharp_half_visibility_threshold():
    blocks = 23
    q = 0.2
    visibility = 1.0 - 2.0 * q
    assert noisy_checkpoint_worst_query_memory_bits(blocks, q, visibility / 2.0 - 1e-9) == blocks
    assert noisy_checkpoint_worst_query_memory_bits(blocks, q, visibility / 2.0) == 0
    assert noisy_checkpoint_worst_query_memory_bits(blocks, 0.5, 0.0) == 0


def test_uniform_query_gilbert_bound_scales_with_effective_visibility():
    blocks = 100
    q = 0.1
    epsilon = 0.04
    visibility = 1.0 - 2.0 * q
    required = noisy_checkpoint_minimum_hamming_distance(blocks, q, epsilon)
    assert required == int((2.0 * epsilon * blocks) // visibility) + 1
    bits = noisy_checkpoint_gilbert_memory_lower_bound_bits(blocks, q, epsilon)
    assert bits >= 46
    assert noisy_checkpoint_gilbert_memory_lower_bound_bits(blocks, 0.5, epsilon) == 0


def test_average_predictive_rate_distortion_has_exact_scaled_binary_form():
    q = 0.1
    visibility = 1.0 - 2.0 * q
    assert noisy_average_predictive_rate_distortion_per_bit(q, 0.0) == 1.0
    assert noisy_average_predictive_rate_distortion_per_bit(q, visibility / 2.0) == 0.0
    low = noisy_average_predictive_rate_distortion_per_bit(q, 0.04)
    high = noisy_average_predictive_rate_distortion_per_bit(q, 0.08)
    assert low > high > 0.0

    information = noisy_average_predictive_information_lower_bound_bits(100, q, 0.04)
    integer_bits = noisy_average_predictive_memory_lower_bound_bits(100, q, 0.04)
    assert isclose(information, 100.0 * low)
    assert integer_bits >= information - 1e-12
    assert integer_bits - 1 < information + 1e-12


def test_product_bsc_codeword_tv_and_bhattacharyya_bound():
    q = 0.18
    values = [bsc_codeword_total_variation(h, q) for h in range(9)]
    assert values[0] == 0.0
    assert isclose(values[1], 1.0 - 2.0 * q, abs_tol=1e-12)
    assert all(right + 1e-12 >= left for left, right in zip(values, values[1:]))
    for h, tv in enumerate(values):
        lower = bsc_codeword_tv_bhattacharyya_lower_bound(h, q)
        assert 0.0 <= lower <= tv + 1e-12


def test_validation_rejects_invalid_noise_and_shapes():
    with pytest.raises(ValueError):
        effective_parity_visibility(0.6, 3)
    with pytest.raises(ValueError):
        noisy_cat_transcript_law(0, 1, 0.1)
    with pytest.raises(ValueError):
        noisy_checkpoint_total_variation((1, -1), (1,), 0.1)
    with pytest.raises(ValueError):
        noisy_average_predictive_rate_distortion_per_bit(0.1, -0.01)
    with pytest.raises(ValueError):
        minimum_repetitions_for_total_variation(0.1, 1.0)
