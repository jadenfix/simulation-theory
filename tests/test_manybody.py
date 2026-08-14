from math import isclose

from simtheory.manybody import (
    basis_predictive_distance,
    brute_force_product_z_tv,
    cartesian_code_memory_lower_bound_bits,
    cartesian_code_packing,
    computational_basis_states,
    exact_basis_renderer_bits_lower_bound,
    exact_basis_renderer_states_lower_bound,
    product_z_total_variation,
    qary_product_memory_lower_bound_bits,
    qary_product_packing,
)


def test_computational_basis_family_has_2_to_n_states():
    for n in range(1, 8):
        states = computational_basis_states(n)
        assert len(states) == 2**n
        assert exact_basis_renderer_states_lower_bound(n) == 2**n
        assert exact_basis_renderer_bits_lower_bound(n) == n


def test_distinct_basis_states_have_worst_query_tv_one():
    states = computational_basis_states(4)
    for i, left in enumerate(states):
        assert basis_predictive_distance(left, left) == 0.0
        for right in states[i + 1 :]:
            assert basis_predictive_distance(left, right) == 1.0


def test_product_z_closed_form_matches_enumeration():
    states = [(-0.8, 0.1, 0.6), (0.2, -0.5, 0.9), (0.0, 0.0, 0.0)]
    for left in states:
        for right in states:
            assert isclose(
                product_z_total_variation(left, right),
                brute_force_product_z_tv(left, right),
                rel_tol=1e-12,
                abs_tol=1e-12,
            )


def test_binary_vertex_packing_is_pairwise_separated():
    dimension = 6
    epsilon = 0.04
    packing = cartesian_code_packing(dimension, epsilon)
    assert len(packing) == 2**dimension
    for i, left in enumerate(packing):
        for right in packing[i + 1 :]:
            assert product_z_total_variation(left, right) > 2 * epsilon
    assert cartesian_code_memory_lower_bound_bits(dimension, epsilon) == dimension


def test_qary_grid_gives_dimension_times_log_levels_scaling():
    dimension = 3
    levels = 4
    epsilon = 0.02
    packing = qary_product_packing(dimension, levels, epsilon)
    assert len(packing) == levels**dimension
    bits = qary_product_memory_lower_bound_bits(dimension, levels, epsilon)
    assert 2**bits >= levels**dimension
    for i, left in enumerate(packing):
        for right in packing[i + 1 :]:
            assert product_z_total_variation(left, right) > 2 * epsilon
