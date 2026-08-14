from math import isclose, pi

from simtheory.quantum_phase import state_total_variation
from simtheory.quantum_phase_geometry import (
    asymptotic_memory_lower_bound_bits,
    canonical_chsh_cartesian_tv,
    constructive_memory_lower_bound_bits,
    constructive_square_packing,
    verify_canonical_metric,
)


def test_closed_form_metric_matches_probability_law():
    states = [(0.0, 0.0), (0.25, -1.0), (0.7, 0.3), (1.0, pi / 2), (0.9, -2.4)]
    for left in states:
        for right in states:
            assert verify_canonical_metric(left, right)
            assert isclose(
                canonical_chsh_cartesian_tv(left, right),
                state_total_variation(left, right),
                rel_tol=1e-12,
                abs_tol=1e-12,
            )


def test_constructive_square_is_strictly_separated():
    for epsilon in (0.02, 0.04, 0.05, 0.08, 0.12):
        packing = constructive_square_packing(epsilon)
        for i, left in enumerate(packing):
            for right in packing[i + 1 :]:
                assert state_total_variation(left, right) > 2.0 * epsilon - 1e-12


def test_constructive_packing_is_quadratic_scale():
    small = len(constructive_square_packing(0.04))
    large = len(constructive_square_packing(0.08))
    assert small > large
    assert small >= 4 * 4


def test_integer_memory_bound_covers_constructive_set():
    epsilon = 0.05
    packing = constructive_square_packing(epsilon)
    bits = constructive_memory_lower_bound_bits(epsilon)
    assert 2**bits >= len(packing)
    assert 2 ** (bits - 1) < len(packing)


def test_asymptotic_expression_increases_as_tolerance_shrinks():
    assert asymptotic_memory_lower_bound_bits(0.01) > asymptotic_memory_lower_bound_bits(0.02)
