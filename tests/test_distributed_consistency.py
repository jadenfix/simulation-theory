from math import isclose

import pytest

from simtheory.distributed_consistency import (
    CausalCutBudget,
    all_binary_records,
    brute_force_prefix_storage_average_error,
    causal_cut_capacity_deficit_bits,
    encoder_collision_witness,
    exact_additional_communication_bits,
    exact_index_bits_lower_bound,
    exact_index_encoder_is_valid,
    exact_index_message_states,
    minimum_additional_communication_bits,
    parity_reconciliation_answer,
    parity_reconciliation_information_lower_bound_bits,
    prefix_storage_average_error,
    replicated_region_storage_lower_bound_bits,
    uniform_index_information_lower_bound_bits,
    uniform_index_state_bits_lower_bound,
    weighted_error_of_allocation,
    weighted_index_information_lower_bound_bits,
    weighted_index_state_bits_lower_bound,
    weighted_optimal_error_allocation,
)


def test_exact_index_encoder_must_be_injective():
    records = all_binary_records(4)
    injective = {record: index for index, record in enumerate(records)}
    assert exact_index_encoder_is_valid(injective, 4)
    assert encoder_collision_witness(injective, 4) is None
    assert exact_index_message_states(4) == 16
    assert exact_index_bits_lower_bound(4) == 4

    colliding = {record: record[:3] for record in records}
    witness = encoder_collision_witness(colliding, 4)
    assert witness is not None
    left, right, query = witness
    assert left != right
    assert colliding[left] == colliding[right]
    assert left[query] != right[query]
    assert not exact_index_encoder_is_valid(colliding, 4)


def test_uniform_information_bound_has_correct_boundaries_and_integer_consequence():
    assert uniform_index_information_lower_bound_bits(100, 0.0) == 100.0
    assert isclose(uniform_index_information_lower_bound_bits(100, 0.5), 0.0, abs_tol=1e-12)
    assert isclose(uniform_index_information_lower_bound_bits(100, 0.1), 53.10044064107188)
    assert uniform_index_state_bits_lower_bound(100, 0.1) == 54


def test_memory_communication_cut_tradeoff():
    assert exact_additional_communication_bits(100, 37) == 63
    assert exact_additional_communication_bits(100, 140) == 0
    assert minimum_additional_communication_bits(100, 20, 0.1) == 34
    assert minimum_additional_communication_bits(100, 54, 0.1) == 0

    assert not CausalCutBudget(20, 33).uniform_error_feasible(100, 0.1)
    assert CausalCutBudget(20, 34).uniform_error_feasible(100, 0.1)
    assert causal_cut_capacity_deficit_bits(100, 20, 0.1) > 33.0


def test_uniform_weighted_solution_recovers_uniform_fano_bound():
    weights = (0.25, 0.25, 0.25, 0.25)
    allocation = weighted_optimal_error_allocation(weights, 0.1)
    assert all(isclose(error, 0.1, abs_tol=1e-12) for error in allocation)
    assert isclose(weighted_error_of_allocation(weights, allocation), 0.1, abs_tol=1e-12)
    assert isclose(
        weighted_index_information_lower_bound_bits(weights, 0.1),
        uniform_index_information_lower_bound_bits(4, 0.1),
        abs_tol=1e-12,
    )


def test_skewed_query_distribution_forgets_rare_coordinates_first():
    weights = (0.7, 0.1, 0.1, 0.1)
    allocation = weighted_optimal_error_allocation(weights, 0.1)
    assert isclose(weighted_error_of_allocation(weights, allocation), 0.1, abs_tol=1e-12)
    assert allocation[0] < allocation[1]
    assert isclose(allocation[1], allocation[2], abs_tol=1e-12)
    assert isclose(allocation[2], allocation[3], abs_tol=1e-12)
    assert weighted_index_information_lower_bound_bits(weights, 0.1) < uniform_index_information_lower_bound_bits(4, 0.1)


def test_zero_weight_coordinates_need_no_information():
    weights = (0.9, 0.1, 0.0, 0.0)
    exact_allocation = weighted_optimal_error_allocation(weights, 0.0)
    assert exact_allocation == (0.0, 0.0, 0.5, 0.5)
    assert weighted_index_information_lower_bound_bits(weights, 0.0) == 2.0

    noisy_allocation = weighted_optimal_error_allocation(weights, 0.1)
    assert noisy_allocation[2:] == (0.5, 0.5)
    assert isclose(weighted_error_of_allocation(weights, noisy_allocation), 0.1, abs_tol=1e-12)


def test_weighted_integer_bound_and_replication_are_explicit():
    weights = (0.7, 0.1, 0.1, 0.1)
    per_region = weighted_index_state_bits_lower_bound(weights, 0.1)
    assert per_region == 2
    assert replicated_region_storage_lower_bound_bits(4, 0.1, 7, weights) == 14

    uniform_per_region = uniform_index_state_bits_lower_bound(100, 0.1)
    assert replicated_region_storage_lower_bound_bits(100, 0.1, 3) == 3 * uniform_per_region


def test_parity_reconciliation_is_index_after_local_xor():
    remote = (1, 0, 1, 1, 0)
    local = (0, 1, 1, 0, 0)
    for query in range(len(remote)):
        assert parity_reconciliation_answer(remote, local, query) == remote[query] ^ local[query]
    assert isclose(
        parity_reconciliation_information_lower_bound_bits(100, 0.1),
        uniform_index_information_lower_bound_bits(100, 0.1),
    )


def test_prefix_storage_scheme_matches_exact_enumeration():
    for record_bits in range(1, 8):
        for stored in range(record_bits + 1):
            analytic = prefix_storage_average_error(record_bits, stored)
            brute = brute_force_prefix_storage_average_error(record_bits, stored)
            assert isclose(analytic, brute, abs_tol=1e-12)


def test_validation_rejects_invalid_protocol_inputs():
    with pytest.raises(ValueError):
        exact_index_bits_lower_bound(0)
    with pytest.raises(ValueError):
        uniform_index_information_lower_bound_bits(3, 0.6)
    with pytest.raises(ValueError):
        weighted_optimal_error_allocation((0.4, 0.4), 0.1)
    with pytest.raises(ValueError):
        weighted_error_of_allocation((0.5, 0.5), (0.1,))
    with pytest.raises(ValueError):
        replicated_region_storage_lower_bound_bits(3, 0.1, 0)
