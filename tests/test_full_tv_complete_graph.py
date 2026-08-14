from fractions import Fraction

from simtheory.full_tv_complete_graph import (
    full_tv_complete_graph_certificate,
)
from simtheory.shared_tv_robust_codes import (
    full_tv_k3_shared_randomness_example,
)


def test_closed_full_tv_complete_graph_values_for_one_through_sixteen_states():
    expected = {
        1: Fraction(0),
        2: Fraction(1),
        3: Fraction(5, 3),
        4: Fraction(2),
        5: Fraction(12, 5),
        6: Fraction(8, 3),
        7: Fraction(20, 7),
        8: Fraction(3),
    }
    for state_count in range(1, 17):
        certificate = full_tv_complete_graph_certificate(state_count)
        assert certificate.valid
        assert certificate.mixed_state_lengths == (
            certificate.shared_value,
        ) * state_count
        assert certificate.shared_value <= certificate.deterministic_value
        assert certificate.symmetric_support_size <= state_count
        if state_count in expected:
            assert certificate.shared_value == expected[state_count]
        if state_count & (state_count - 1) == 0:
            assert certificate.randomization_gain == 0
            assert certificate.symmetric_support_size == 1
        elif state_count > 1:
            assert certificate.randomization_gain > 0
            assert certificate.symmetric_support_size == state_count


def test_closed_k3_formula_matches_exact_continuous_game_solver():
    closed = full_tv_complete_graph_certificate(3)
    enumerated = full_tv_k3_shared_randomness_example()
    assert closed.valid and enumerated.valid
    assert closed.shared_value == enumerated.mixed_value == Fraction(5, 3)
    assert closed.deterministic_value == enumerated.deterministic_value == 2
    assert closed.mixed_state_lengths == enumerated.mixed_state_lengths


def test_cyclic_construction_uses_near_balanced_complete_tree_depths():
    certificate = full_tv_complete_graph_certificate(5)
    assert certificate.valid
    assert certificate.fixed_length_bits == 3
    assert certificate.short_leaf_count == 3
    assert certificate.long_leaf_count == 2
    assert certificate.short_depth == 2
    assert certificate.long_depth == 3
    assert certificate.minimum_total_leaf_depth == 12
    assert certificate.shared_value == Fraction(12, 5)
    assert all(
        shape.lengths.count(2) == 3 and shape.lengths.count(3) == 2
        for shape in certificate.cyclic_shapes
    )
