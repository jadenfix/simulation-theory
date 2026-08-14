from math import inf, isclose, pi, sqrt

from simtheory.bell_predictive import (
    CANONICAL_CHSH,
    BellSchedule,
    adaptive_trials_necessary_for_tv,
    analytic_visibility_tv,
    brute_force_visibility_tv,
    chsh_value,
    conditional_outcome_law,
    cramer_rao_variance_lower_bound,
    maximum_epsilon_packing,
    maximum_query_kl,
    predictive_memory_lower_bound_bits,
    schedule_fisher_information,
    schedule_geometry,
    single_setting_fisher_information,
    single_setting_kl,
    uniform_visibility_grid,
    violates_chsh,
)


def test_conditional_law_normalizes_and_is_nonnegative():
    for v in (0.0, 0.2, 0.7, 1.0):
        law = conditional_outcome_law(v, 0.3, -0.7)
        assert isclose(sum(law.values()), 1.0, abs_tol=1e-12)
        assert min(law.values()) >= -1e-15


def test_analytic_tv_matches_enumeration_on_grid():
    for va in (0.0, 0.1, 0.4, 0.9, 1.0):
        for vb in (0.0, 0.25, 0.5, 0.75, 1.0):
            exact = analytic_visibility_tv(va, vb)
            brute = brute_force_visibility_tv(va, vb)
            assert isclose(exact, brute, rel_tol=1e-12, abs_tol=1e-12)


def test_canonical_chsh_geometry_is_inverse_sqrt_two():
    assert isclose(schedule_geometry(CANONICAL_CHSH), 1.0 / sqrt(2.0), rel_tol=1e-12)


def test_chsh_threshold():
    threshold = 1.0 / sqrt(2.0)
    assert isclose(chsh_value(threshold), 2.0, rel_tol=1e-12)
    assert not violates_chsh(threshold)
    assert violates_chsh(threshold + 1e-6)


def test_zero_geometry_schedule_carries_no_visibility_information():
    schedule = BellSchedule.uniform((0.0,), (pi / 2.0,))
    assert isclose(schedule_geometry(schedule), 0.0, abs_tol=1e-12)
    assert isclose(analytic_visibility_tv(0.0, 1.0, schedule), 0.0, abs_tol=1e-12)
    assert maximum_epsilon_packing((0.0, 0.5, 1.0), 0.0, schedule) == (0.0,)
    assert schedule_fisher_information(0.5, schedule) < 1e-30
    assert cramer_rao_variance_lower_bound(0.5, 100, schedule) == inf


def test_packing_is_pairwise_more_than_two_epsilon_apart():
    epsilon = 0.03
    packing = maximum_epsilon_packing(uniform_visibility_grid(101), epsilon)
    for i, left in enumerate(packing):
        for right in packing[i + 1 :]:
            assert analytic_visibility_tv(left, right) > 2.0 * epsilon


def test_greedy_packing_cardinality_against_bruteforce_small_grid():
    from itertools import combinations

    grid = uniform_visibility_grid(9)
    epsilon = 0.05
    greedy = maximum_epsilon_packing(grid, epsilon)
    best = 0
    for r in range(1, len(grid) + 1):
        for subset in combinations(grid, r):
            if all(
                analytic_visibility_tv(a, b) > 2.0 * epsilon
                for i, a in enumerate(subset)
                for b in subset[i + 1 :]
            ):
                best = max(best, r)
    assert len(greedy) == best


def test_memory_bound_tracks_packing_size():
    grid = uniform_visibility_grid(101)
    packing = maximum_epsilon_packing(grid, 0.02)
    bits = predictive_memory_lower_bound_bits(grid, 0.02)
    assert (2**bits) >= len(packing)
    if bits:
        assert 2 ** (bits - 1) < len(packing)


def test_fisher_information_matches_closed_form_at_aligned_settings():
    v = 0.4
    observed = single_setting_fisher_information(v, 0.0, 0.0)
    expected = 1.0 / (1.0 - v * v)
    assert isclose(observed, expected, rel_tol=1e-12)


def test_canonical_schedule_fisher_information_closed_form():
    v = 0.6
    # Every canonical CHSH pair has c^2 = 1/2.
    expected = 0.5 / (1.0 - 0.5 * v * v)
    assert isclose(schedule_fisher_information(v), expected, rel_tol=1e-12)
    assert isclose(
        cramer_rao_variance_lower_bound(v, 200),
        1.0 / (200.0 * expected),
        rel_tol=1e-12,
    )


def test_single_setting_kl_is_zero_only_for_equal_visibility_in_sensitive_query():
    assert isclose(single_setting_kl(0.2, 0.2, 0.0, 0.0), 0.0, abs_tol=1e-15)
    assert single_setting_kl(0.2, 0.8, 0.0, 0.0) > 0.0
    assert isclose(single_setting_kl(0.2, 0.8, 0.0, pi / 2.0), 0.0, abs_tol=1e-12)


def test_maximum_query_kl_finds_a_valid_setting_and_dominates_all_pairs():
    best, (x_best, y_best) = maximum_query_kl(0.2, 0.8)
    assert 0 <= x_best < len(CANONICAL_CHSH.alice_angles)
    assert 0 <= y_best < len(CANONICAL_CHSH.bob_angles)
    for x, alpha in enumerate(CANONICAL_CHSH.alice_angles):
        for y, beta in enumerate(CANONICAL_CHSH.bob_angles):
            assert best + 1e-15 >= single_setting_kl(0.2, 0.8, alpha, beta)


def test_adaptive_trial_lower_bound_increases_with_target_separation():
    low = adaptive_trials_necessary_for_tv(0.4, 0.6, 0.2)
    high = adaptive_trials_necessary_for_tv(0.4, 0.6, 0.8)
    assert low >= 1
    assert high >= low


def test_adaptive_trial_bound_is_infinite_when_allowed_queries_have_zero_sensitivity():
    schedule = BellSchedule.uniform((0.0,), (pi / 2.0,))
    assert adaptive_trials_necessary_for_tv(0.1, 0.9, 0.5, schedule) == 2**63 - 1
