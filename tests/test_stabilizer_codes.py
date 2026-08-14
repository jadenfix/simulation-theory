from itertools import combinations
from math import isclose

import pytest

from simtheory.stabilizer_codes import (
    all_codeword_reductions_equal,
    all_paulis_up_to_weight,
    apply_pauli_to_state,
    construct_stabilizer_codeword,
    encoded_block_worst_query_memory_bits,
    five_qubit_code,
    gf2_rank,
    gf2_span,
    inner_product,
    local_indistinguishability_certificate,
    logical_label_query_total_variation,
    matrix_max_difference,
    minimum_logical_paulis,
    normalizer_coset_leaders,
    normalize_state,
    pauli_vector,
    pauli_weight,
    paulis_commute,
    predicted_local_blindness_threshold,
    quantum_singleton_slack,
    reduced_density_matrix,
    stabilizer_code_distance,
    three_qubit_repetition_code,
    vector_norm,
)


def test_binary_symplectic_rank_span_and_commutation():
    rows = (0b0011, 0b0101, 0b0110)
    assert gf2_rank(rows) == 2
    assert len(gf2_span(rows)) == 4
    assert paulis_commute("XZZXI", "IXZZX")
    assert not paulis_commute("XIIII", "ZIIII")


def test_five_qubit_code_has_exact_513_parameters():
    code = five_qubit_code()
    assert code.rank == 4
    assert code.logical_qubits == 1
    assert len(code.stabilizer_span) == 16
    assert stabilizer_code_distance(code) == 3
    assert predicted_local_blindness_threshold(code) == 2
    assert quantum_singleton_slack(code, 3) == 0

    leaders = normalizer_coset_leaders(code)
    assert len(leaders) == 4
    assert sorted(pauli_weight(word) for word in minimum_logical_paulis(code)) == [3, 3, 3]


def test_three_qubit_repetition_is_not_a_distance_three_quantum_code():
    code = three_qubit_repetition_code()
    assert code.logical_qubits == 1
    assert stabilizer_code_distance(code) == 1
    assert code.pauli_restriction_type("ZII") == "logical"
    assert code.pauli_restriction_type("XII") == "projected-zero"


def test_distance_exactly_matches_local_pauli_restriction_threshold():
    code = five_qubit_code()
    assert local_indistinguishability_certificate(code, 2)
    assert not local_indistinguishability_certificate(code, 3)
    assert all(
        code.pauli_restriction_type(pauli) in {"scalar", "projected-zero"}
        for pauli in all_paulis_up_to_weight(5, 2)
    )
    assert any(
        code.pauli_restriction_type(pauli) == "logical"
        for pauli in all_paulis_up_to_weight(5, 3)
    )


def test_constructed_five_qubit_logical_codewords_obey_all_constraints():
    code = five_qubit_code()
    zero = construct_stabilizer_codeword(code, "ZZZZZ", 1)
    one = construct_stabilizer_codeword(code, "ZZZZZ", -1)
    assert isclose(vector_norm(zero), 1.0, abs_tol=1e-12)
    assert isclose(vector_norm(one), 1.0, abs_tol=1e-12)
    assert abs(inner_product(zero, one)) <= 1e-12

    for generator in code.generators:
        assert abs(inner_product(zero, apply_pauli_to_state(zero, generator)) - 1.0) <= 1e-12
        assert abs(inner_product(one, apply_pauli_to_state(one, generator)) - 1.0) <= 1e-12

    assert abs(inner_product(zero, apply_pauli_to_state(zero, "ZZZZZ")) - 1.0) <= 1e-12
    assert abs(inner_product(one, apply_pauli_to_state(one, "ZZZZZ")) + 1.0) <= 1e-12

    mapped = apply_pauli_to_state(zero, "XXXXX")
    assert isclose(abs(inner_product(one, mapped)), 1.0, abs_tol=1e-12)


def test_all_one_and_two_qubit_reductions_hide_the_logical_state():
    code = five_qubit_code()
    zero = construct_stabilizer_codeword(code, "ZZZZZ", 1)
    one = construct_stabilizer_codeword(code, "ZZZZZ", -1)
    plus = normalize_state(tuple(a + b for a, b in zip(zero, one)))
    plus_i = normalize_state(tuple(a + 1j * b for a, b in zip(zero, one)))
    assert all_codeword_reductions_equal((zero, one, plus, plus_i), 2)

    # Some weight-three logical representative must expose a difference on its
    # support. Search the exact minimum logical coset leaders rather than
    # hard-coding a representative.
    found = False
    for logical in minimum_logical_paulis(code):
        expectation_zero = inner_product(zero, apply_pauli_to_state(zero, logical)).real
        expectation_one = inner_product(one, apply_pauli_to_state(one, logical)).real
        if abs(expectation_zero - expectation_one) < 1.0:
            continue
        support = tuple(i for i, symbol in enumerate(logical) if symbol != "I")
        rho_zero = reduced_density_matrix(zero, support)
        rho_one = reduced_density_matrix(one, support)
        assert matrix_max_difference(rho_zero, rho_one) > 1e-6
        found = True
        break
    assert found


def test_logical_query_geometry_and_block_memory():
    left = (0, 1, 0, 1, 1)
    right = (1, 1, 0, 0, 1)
    weights = (0.05, 0.1, 0.2, 0.25, 0.4)
    assert isclose(logical_label_query_total_variation(left, right, weights), 0.30)
    assert isclose(logical_label_query_total_variation(left, right), 2.0 / 5.0)
    assert encoded_block_worst_query_memory_bits(20, 1, 0.49) == 20
    assert encoded_block_worst_query_memory_bits(20, 2, 0.49) == 40
    assert encoded_block_worst_query_memory_bits(20, 2, 0.5) == 0


def test_validation_rejects_noncommuting_or_dependent_generators():
    from simtheory.stabilizer_codes import StabilizerCode

    with pytest.raises(ValueError):
        StabilizerCode(2, ("XI", "ZI"))
    with pytest.raises(ValueError):
        StabilizerCode(2, ("ZZ", "ZZ"))
    with pytest.raises(ValueError):
        construct_stabilizer_codeword(five_qubit_code(), "IIIII", 1)
