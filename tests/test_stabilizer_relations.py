from itertools import combinations, product
from math import isclose

import pytest

from simtheory.stabilizer_relations import (
    SimpleGraph,
    all_reductions_up_to_size_are_maximally_mixed,
    asymptotic_gilbert_rate_for_tv,
    brute_force_graph_generator_tv,
    code_minimum_distance,
    cycle_stabilizer_distance,
    gilbert_predictive_memory_lower_bound_bits,
    gilbert_predictive_size_lower_bound,
    graph_generator_total_variation,
    graph_generator_weight,
    greedy_binary_code,
    integer_to_label,
    minimum_hamming_distance_for_tv,
    stabilizer_distance,
    subset_reduction_is_maximally_mixed,
    verify_generator_eigenrelation,
)


def test_graph_generator_eigenrelation_against_statevector_amplitudes():
    graph = SimpleGraph.cycle(5)
    labels = [(0, 0, 0, 0, 0), (1, 0, 1, 1, 0), (1, 1, 1, 1, 1)]
    for label in labels:
        for generator in range(graph.qubits):
            assert verify_generator_eigenrelation(graph, label, generator)


def test_generator_query_geometry_is_weighted_hamming():
    left = (0, 0, 1, 0, 1)
    right = (1, 0, 1, 1, 1)
    weights = (0.05, 0.1, 0.2, 0.25, 0.4)
    expected = weights[0] + weights[3]
    assert isclose(graph_generator_total_variation(left, right, weights), expected)
    assert isclose(brute_force_graph_generator_tv(left, right, weights), expected)
    assert isclose(graph_generator_total_variation(left, right), 2.0 / 5.0)


def test_cycle_stabilizer_distance_formula_matches_exact_enumeration():
    for qubits in range(3, 11):
        graph = SimpleGraph.cycle(qubits)
        assert stabilizer_distance(graph) == cycle_stabilizer_distance(qubits)


def test_cycle_graph_has_two_local_blindness_and_three_local_generators():
    for qubits in (5, 6, 7, 8):
        graph = SimpleGraph.cycle(qubits)
        assert all(graph_generator_weight(graph, i) == 3 for i in range(qubits))
        assert all_reductions_up_to_size_are_maximally_mixed(graph, 2)
        assert not all_reductions_up_to_size_are_maximally_mixed(graph, 3)


def test_small_cycle_exception_is_detected():
    graph = SimpleGraph.cycle(4)
    assert stabilizer_distance(graph) == 2
    assert not all_reductions_up_to_size_are_maximally_mixed(graph, 2)
    assert subset_reduction_is_maximally_mixed(graph, (0,))


def test_greedy_binary_code_is_a_valid_predictive_packing():
    qubits = 8
    epsilon = 0.1
    minimum_distance = minimum_hamming_distance_for_tv(qubits, epsilon)
    code = greedy_binary_code(qubits, minimum_distance)
    assert code_minimum_distance(code) >= minimum_distance
    assert len(code) >= gilbert_predictive_size_lower_bound(qubits, epsilon)

    labels = tuple(integer_to_label(word, qubits) for word in code)
    for left, right in combinations(labels[:32], 2):
        assert graph_generator_total_variation(left, right) > 2.0 * epsilon


def test_constant_tolerance_retains_linear_predictive_memory():
    # This is a finite Gilbert certificate, not an asymptotic extrapolation.
    assert gilbert_predictive_memory_lower_bound_bits(100, 0.05) >= 55
    assert asymptotic_gilbert_rate_for_tv(0.05) > 0.5
    assert isclose(asymptotic_gilbert_rate_for_tv(0.25), 0.0, abs_tol=1e-12)


def test_input_validation_boundaries():
    with pytest.raises(ValueError):
        SimpleGraph.cycle(2)
    with pytest.raises(ValueError):
        SimpleGraph(3, ((0, 0),))
    with pytest.raises(ValueError):
        graph_generator_total_variation((0, 1), (0, 1, 0))
    with pytest.raises(ValueError):
        asymptotic_gilbert_rate_for_tv(0.3)
