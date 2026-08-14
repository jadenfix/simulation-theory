from math import inf, isclose, pi

from simtheory.bell_predictive import BellSchedule, CANONICAL_CHSH
from simtheory.quantum_phase import (
    brute_force_state_tv,
    cartesian_to_polar_state,
    cramer_rao_covariance_lower_bound,
    exact_maximum_packing,
    fisher_eigenvalues,
    greedy_separated_packing,
    polar_to_cartesian_state,
    predictive_memory_lower_bound_bits,
    schedule_fisher,
    single_setting_fisher,
    state_total_variation,
    visibility_phase_grid,
    wrap_phase,
)


def test_phase_wrap_is_periodic():
    assert isclose(wrap_phase(0.3 + 2 * pi), 0.3, abs_tol=1e-12)
    assert isclose(wrap_phase(-0.7 - 4 * pi), -0.7, abs_tol=1e-12)


def test_exact_tv_matches_bruteforce():
    states = [(0.0, 0.0), (0.3, -0.4), (0.8, 1.2), (1.0, -2.0)]
    for left in states:
        for right in states:
            assert isclose(
                state_total_variation(left, right),
                brute_force_state_tv(left, right),
                rel_tol=1e-12,
                abs_tol=1e-12,
            )


def test_zero_visibility_erases_phase():
    assert isclose(state_total_variation((0.0, 0.0), (0.0, 2.1)), 0.0, abs_tol=1e-12)


def test_single_setting_fisher_rank_is_at_most_one():
    info = single_setting_fisher(0.6, 0.2, 0.0, pi / 4)
    assert abs(info.determinant) < 1e-12
    assert info.rank == 1


def test_canonical_chsh_identifies_two_parameters_away_from_zero_visibility():
    for phase in (-1.0, -0.2, 0.0, 0.7, 1.4):
        info = schedule_fisher(0.6, phase, CANONICAL_CHSH)
        lo, hi = fisher_eigenvalues(info)
        assert info.rank == 2
        assert lo > 0.0
        assert hi >= lo


def test_phase_is_unidentifiable_at_zero_visibility():
    info = schedule_fisher(0.0, 0.4, CANONICAL_CHSH)
    assert info.rank == 1
    covariance = cramer_rao_covariance_lower_bound(0.0, 0.4, 100, CANONICAL_CHSH)
    assert covariance == ((inf, inf), (inf, inf))


def test_one_setting_schedule_cannot_identify_both_parameters():
    schedule = BellSchedule.uniform((0.0,), (pi / 4,))
    info = schedule_fisher(0.7, 0.2, schedule)
    assert info.rank == 1


def test_cartesian_polar_roundtrip():
    for state in ((0.2, -2.2), (0.7, 0.4), (1.0, 2.5)):
        x, y = polar_to_cartesian_state(state)
        recovered = cartesian_to_polar_state(x, y)
        assert isclose(recovered[0], state[0], abs_tol=1e-12)
        assert isclose(state_total_variation(state, recovered), 0.0, abs_tol=1e-12)


def test_greedy_packing_is_certified_pairwise_separated():
    epsilon = 0.04
    states = visibility_phase_grid(5, 8)
    packing = greedy_separated_packing(states, epsilon)
    for i, left in enumerate(packing):
        for right in packing[i + 1 :]:
            assert state_total_variation(left, right) > 2.0 * epsilon


def test_exact_packing_dominates_greedy_on_small_grid():
    states = visibility_phase_grid(3, 6)
    epsilon = 0.05
    greedy = greedy_separated_packing(states, epsilon)
    exact = exact_maximum_packing(states, epsilon)
    assert len(exact) >= len(greedy)


def test_memory_bound_matches_certified_packing_size():
    states = visibility_phase_grid(4, 8)
    epsilon = 0.05
    packing = greedy_separated_packing(states, epsilon)
    bits = predictive_memory_lower_bound_bits(states, epsilon)
    assert 2**bits >= len(packing)
    if bits:
        assert 2 ** (bits - 1) < len(packing)
