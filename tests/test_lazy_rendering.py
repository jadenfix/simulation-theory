from math import isclose

from simtheory.lazy_rendering import (
    approximate_memory_bits_lower_bound,
    approximate_state_packing_lower_bound,
    conditional_tv_profile,
    minimum_exact_memory_bits,
    minimum_exact_state_count,
    sequential_pinsker_bound,
    sequential_total_variation_bound,
    sequential_union_bound,
    transcript_total_variation,
)


def test_predictive_state_bound():
    laws = {
        (("a",),): [0.5, 0.5],
        (("b",),): [0.9, 0.1],
        (("c",),): [0.5, 0.5],
        (("d",),): [0.1, 0.9],
    }
    assert minimum_exact_state_count(laws) == 3
    assert minimum_exact_memory_bits(laws) == 2


def test_sequential_coupling_bound_dominates_exact_tree_tv():
    target = {
        (): [0.5, 0.5],
        (0,): [0.9, 0.1],
        (1,): [0.2, 0.8],
    }
    renderer = {
        (): [0.55, 0.45],
        (0,): [0.85, 0.15],
        (1,): [0.25, 0.75],
    }
    profile = conditional_tv_profile(target, renderer, 2)
    exact = transcript_total_variation(target, renderer, 2)
    assert exact <= sequential_total_variation_bound(profile) + 1e-12
    assert sequential_total_variation_bound(profile) <= sequential_union_bound(profile)


def test_product_coupling_formula():
    assert isclose(sequential_total_variation_bound([0.1, 0.2]), 0.28)


def test_approximate_packing_lower_bound():
    laws = {
        ("a",): [1.0, 0.0, 0.0],
        ("b",): [0.0, 1.0, 0.0],
        ("c",): [0.0, 0.0, 1.0],
        ("near-a",): [0.95, 0.05, 0.0],
    }
    assert approximate_state_packing_lower_bound(laws, epsilon=0.1) == 3
    assert approximate_memory_bits_lower_bound(laws, epsilon=0.1) == 2


def test_pinsker_bound_caps_at_one():
    assert sequential_pinsker_bound([10.0]) == 1.0
