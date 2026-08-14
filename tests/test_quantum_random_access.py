from itertools import product
from math import isclose, sqrt

import pytest

from simtheory.quantum_random_access import (
    QuantumCutBudget,
    bloch_measurement_outcome_probability,
    brute_force_canonical_qrac_average_success,
    canonical_qrac_bloch,
    canonical_qrac_error,
    canonical_qrac_success_probability,
    canonical_qrac_success_probability_for_record,
    entanglement_assisted_information_increment_bits,
    entanglement_assisted_qrac_integer_qubits_lower_bound,
    entanglement_assisted_qrac_qubits_lower_bound,
    exact_entanglement_assisted_qubits,
    exact_unassisted_qubits,
    inverse_binary_entropy,
    qrac_2_to_1_bloch,
    qrac_3_to_1_bloch,
    qrac_information_slack_bits,
    query_known_before_message_exact_qubits,
    superdense_classical_payload_bits,
    superdense_exact_record_feasible,
    unassisted_information_capacity_bits,
    unassisted_qrac_integer_qubits_lower_bound,
    unassisted_qrac_qubits_lower_bound,
    uniform_qrac_error_lower_bound,
    weighted_entanglement_assisted_qrac_qubits_lower_bound,
    weighted_unassisted_qrac_qubits_lower_bound,
)
from simtheory.stabilizer_relations import binary_entropy


def _norm(vector):
    return sqrt(sum(component * component for component in vector))


def test_exact_quantum_cut_bounds_and_query_timing():
    assert exact_unassisted_qubits(100) == 100
    assert exact_entanglement_assisted_qubits(100) == 50
    assert exact_entanglement_assisted_qubits(101) == 51
    assert query_known_before_message_exact_qubits(100) == 1
    assert unassisted_information_capacity_bits(7) == 7
    assert entanglement_assisted_information_increment_bits(7) == 14


def test_superdense_coding_matches_the_exact_assisted_bound():
    for record_bits in range(1, 20):
        qubits = exact_entanglement_assisted_qubits(record_bits)
        assert superdense_exact_record_feasible(record_bits, qubits)
        assert superdense_classical_payload_bits(qubits) >= record_bits
        if qubits > 0 and record_bits > 1:
            assert not superdense_exact_record_feasible(record_bits, qubits - 1)


def test_unassisted_and_entanglement_assisted_fano_bounds_differ_by_two():
    for record_bits in (2, 10, 100):
        for error in (0.0, 0.05, 0.1, 0.25, 0.5):
            unassisted = unassisted_qrac_qubits_lower_bound(record_bits, error)
            assisted = entanglement_assisted_qrac_qubits_lower_bound(record_bits, error)
            assert isclose(assisted, 0.5 * unassisted, abs_tol=1e-12)
    assert unassisted_qrac_integer_qubits_lower_bound(100, 0.1) == 54
    assert entanglement_assisted_qrac_integer_qubits_lower_bound(100, 0.1) == 27


def test_weighted_quantum_bounds_inherit_the_same_factor_two():
    weights = (0.7, 0.1, 0.1, 0.1)
    unassisted = weighted_unassisted_qrac_qubits_lower_bound(weights, 0.1)
    assisted = weighted_entanglement_assisted_qrac_qubits_lower_bound(weights, 0.1)
    assert isclose(assisted, 0.5 * unassisted, abs_tol=1e-12)
    assert 0.0 < assisted < unassisted < 4.0


def test_inverse_binary_entropy_round_trip_and_boundaries():
    assert inverse_binary_entropy(0.0) == 0.0
    assert inverse_binary_entropy(1.0) == 0.5
    for probability in (0.01, 0.05, 0.1, 0.2, 0.4):
        recovered = inverse_binary_entropy(binary_entropy(probability))
        assert isclose(recovered, probability, abs_tol=1e-12)


def test_uniform_error_converse_has_expected_behavior():
    assert uniform_qrac_error_lower_bound(10, 0) == 0.5
    assert uniform_qrac_error_lower_bound(10, 10) == 0.0
    assert uniform_qrac_error_lower_bound(10, 5, entanglement_assisted=True) == 0.0
    assert isclose(uniform_qrac_error_lower_bound(2, 1), 0.11002786443835955, abs_tol=1e-12)
    assert isclose(uniform_qrac_error_lower_bound(3, 1), 0.1739523314093953, abs_tol=1e-12)


def test_two_to_one_qrac_bloch_geometry_and_success():
    expected = 0.5 * (1.0 + 1.0 / sqrt(2.0))
    for record in product((0, 1), repeat=2):
        vector = qrac_2_to_1_bloch(record)
        assert isclose(_norm(vector), 1.0, abs_tol=1e-12)
        assert vector == canonical_qrac_bloch(record)
        for query in range(2):
            assert isclose(
                canonical_qrac_success_probability_for_record(record, query),
                expected,
                abs_tol=1e-12,
            )
    assert isclose(canonical_qrac_success_probability(2), expected, abs_tol=1e-12)
    assert isclose(brute_force_canonical_qrac_average_success(2), expected, abs_tol=1e-12)


def test_three_to_one_qrac_bloch_geometry_and_success():
    expected = 0.5 * (1.0 + 1.0 / sqrt(3.0))
    for record in product((0, 1), repeat=3):
        vector = qrac_3_to_1_bloch(record)
        assert isclose(_norm(vector), 1.0, abs_tol=1e-12)
        assert vector == canonical_qrac_bloch(record)
        for query in range(3):
            assert isclose(
                canonical_qrac_success_probability_for_record(record, query),
                expected,
                abs_tol=1e-12,
            )
    assert isclose(canonical_qrac_success_probability(3), expected, abs_tol=1e-12)
    assert isclose(brute_force_canonical_qrac_average_success(3), expected, abs_tol=1e-12)


def test_born_probabilities_normalize_and_qrac_codes_respect_the_converse():
    vector = qrac_2_to_1_bloch((0, 1))
    axis = (2.0, 0.0, 0.0)
    assert isclose(
        bloch_measurement_outcome_probability(vector, axis, 1)
        + bloch_measurement_outcome_probability(vector, axis, -1),
        1.0,
        abs_tol=1e-12,
    )

    for record_bits in (2, 3):
        achieved_error = canonical_qrac_error(record_bits)
        converse = uniform_qrac_error_lower_bound(record_bits, 1)
        assert achieved_error >= converse - 1e-12
        assert qrac_information_slack_bits(record_bits, 1, achieved_error) >= -1e-12


def test_quantum_cut_budget_wrapper():
    unassisted = QuantumCutBudget(1)
    assisted = QuantumCutBudget(1, entanglement_assisted=True)
    assert unassisted.classical_information_ceiling_bits == 1
    assert assisted.classical_information_ceiling_bits == 2
    assert assisted.uniform_error_converse(2) == 0.0
    assert unassisted.uniform_error_converse(2) > 0.0


def test_validation_rejects_invalid_quantum_cut_inputs():
    with pytest.raises(ValueError):
        exact_unassisted_qubits(0)
    with pytest.raises(ValueError):
        unassisted_information_capacity_bits(-1)
    with pytest.raises(ValueError):
        inverse_binary_entropy(1.1)
    with pytest.raises(ValueError):
        qrac_2_to_1_bloch((0, 1, 0))
    with pytest.raises(ValueError):
        canonical_qrac_success_probability(4)
    with pytest.raises(ValueError):
        bloch_measurement_outcome_probability((1.2, 0.0, 0.0), (1.0, 0.0, 0.0), 1)
