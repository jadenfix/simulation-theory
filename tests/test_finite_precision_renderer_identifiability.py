"""Tests for finite-precision renderer identifiability (ST-T286 to ST-T289, ST-F57)."""

from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import pytest

from simtheory import finite_precision_renderers as ck

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _decimal_context():
    with localcontext(ck.CONTEXT):
        yield

V_RANGE = (Fraction(1, 2), Fraction(1))


def test_systematic_dither_reproduces_target_exactly_with_local_grid_components():
    targets = [
        ((Fraction(1, 3), Fraction(1, 3), Fraction(1, 6), Fraction(1, 6)), 4),
        (ck.werner_law(Fraction(1, 3)), 8),
        (ck.werner_law(Fraction(99, 140)), 1024),
        ((Fraction(1, 10), Fraction(2, 10), Fraction(3, 10), Fraction(4, 10)), 3),
    ]
    for p, D in targets:
        result = ck.check_dither(p, D)
        assert result["mixture_exact"]
        assert result["all_grid"]
        assert result["linf_below_1_over_D"]
        assert result["weights_valid"]
        assert result["max_components_le_K"]


def test_uniform_m_dithering_of_grid_d_is_exactly_grid_dm():
    for K, D, M in [(3, 2, 3), (3, 3, 2), (4, 2, 2), (2, 5, 3)]:
        equal, n_avg, n_fine = ck.dither_product_identity(K, D, M)
        assert equal and n_avg == n_fine


def test_werner_lattice_formula_matches_bruteforce_and_is_empty_for_odd_precision():
    for D in range(1, 41):
        assert ck.werner_lattice(D) == ck.werner_lattice_bruteforce(D)
        if D % 2:
            assert ck.werner_lattice(D) == []


def test_single_cosine_sufficient_condition_always_yields_exact_grid_werner_law():
    for c_kind in ("one", "inv_sqrt2"):
        for vmin, vmax in (V_RANGE, (Fraction(9, 10), Fraction(1))):
            for D in range(4, 201, 2):
                points = ck.single_cosine_grid_points(D, c_kind, vmin, vmax)
                assert all(ck.is_grid_law(ck.werner_law(x), D) for x in points)
                if ck.single_cosine_sufficient(D, c_kind, vmin, vmax):
                    assert points


def test_literal_divisible_by_four_claim_fails_for_small_precision():
    assert ck.single_cosine_grid_points(4, "inv_sqrt2", Fraction(9, 10), Fraction(1)) == []
    assert ck.single_cosine_grid_points(4, "inv_sqrt2", *V_RANGE) == []


def test_chsh_schedule_admits_five_bit_renderer_with_s_equal_five_halves():
    law = ck.werner_law(Fraction(5, 8))
    assert law == (Fraction(3, 32), Fraction(13, 32), Fraction(13, 32), Fraction(3, 32))
    assert ck.is_grid_law(law, 32)
    assert Fraction(5, 8) in ck.single_cosine_grid_points(32, "inv_sqrt2", *V_RANGE)


def test_pell_pairs_and_no_rational_point_on_sqrt2_ray():
    for P, Q in ck.pell_pairs(10 ** 6):
        assert abs(P * P - 2 * Q * Q) == 1
    assert all(
        m1 * m1 != 2 * m2 * m2
        for m1 in range(-60, 61)
        for m2 in range(-60, 61)
        if (m1, m2) != (0, 0)
    )


def test_grid_segment_separation_respects_analytic_inverse_square_bound():
    vmin, vmax = V_RANGE
    for D in (4, 8, 12, 28, 68, 100, 164, 396, 999, 1000):
        g, (m1, m2) = ck.grid_segment_separation(D, vmin, vmax)
        assert g >= ck.g_lower_bound(D, vmin)
        assert g * D * D < 3
        assert (m1 - D) % 2 == 0 and (m2 - D) % 2 == 0


def test_pell_multiple_renderer_is_exact_grid_and_inverse_square_close():
    vmin, vmax = V_RANGE
    for D in range(8, 801, 4):
        res = ck.pell_multiple_renderer(D, vmin, vmax)
        assert res is not None
        assert res["v_in_range"] and res["P_window"]
        assert res["grid_theta0"] and res["grid_theta_pi4"] and res["grid_theta_pi2"]
        assert res["delta_identity_ok"]
        assert res["delta"] <= res["delta_bound1"] <= res["delta_bound2"]


def test_pell_subsequence_kl_scales_as_thirty_two_over_d_to_fourth():
    P, Q = 1393, 985
    D = 4 * P
    kl, chi2 = ck.kl_chi2_werner(Fraction(Q, P), ck.R_INV_SQRT2)
    assert abs(kl * D ** 4 - 32) < Decimal("0.01")
    assert abs(chi2 * D ** 4 - 64) < Decimal("0.01")
    assert ck.is_grid_law(ck.werner_law(Fraction(Q, P)), D)


def test_fixed_pi4_distance_is_governed_by_binary_digits_of_sqrt2():
    for k in range(1, 6):
        assert abs(ck.tv_pi4_largest_remainder(k) - ck.tv_pi4_bruteforce(k)) < Decimal(10) ** -60
    for k in range(3, 6):
        assert abs(ck.tv_pi4_largest_remainder(k) - ck.tv_pi4_formula(k)) < Decimal(10) ** -60
    for k in range(3, 65):
        tv = ck.tv_pi4_formula(k)
        assert 0 < tv <= Decimal(2) ** -k


def test_adapted_design_has_exact_distance_one_over_d_including_coarser_grids():
    for k in range(1, 11):
        D = 2 ** k
        assert ck.adapted_design_tv(D) == Fraction(1, D)
        p = ck.werner_law(1 - Fraction(2, D))
        for j in range(k):
            coarse = 2 ** j
            l1 = ck.l1_to_counts(p, ck.largest_remainder_round(p, coarse), coarse)
            assert l1 / 2 >= Fraction(1, D)
    for k in range(1, 6):
        D = 2 ** k
        assert ck.brute_min_l1(ck.werner_law(1 - Fraction(2, D)), D) == Fraction(2, D)


def test_rare_outcome_test_meets_error_target_numerically():
    for D in (16, 64, 256):
        n, threshold, err_null, worst_alt = ck.adapted_test_errors(D, 0.05)
        assert err_null <= 0.05
        assert worst_alt <= 0.05


def test_largest_remainder_is_optimal_and_obeys_universal_rounding_bound():
    worst_ratio, optimal, hellinger_ok = ck.universal_rounding_bounds(trials=120, seed=7)
    assert optimal
    assert hellinger_ok
    assert worst_ratio <= 1


def test_phase_nuisance_three_setting_schedule_counterexample():
    hits = ck.phase_counterexample(32)
    assert hits and all(ok for _, ok in hits)
    in_range = [x for x, _ in hits if Fraction(1, 4) <= 2 * x * x <= 1]
    assert Fraction(5, 8) in in_range


def test_adapted_design_minimum_tv_is_one_over_two_d_for_odd_d():
    for D in (3, 5, 7, 9, 15, 33):
        assert ck.adapted_design_tv(D) == Fraction(1, 2 * D)
    for D in (6, 10, 12, 14, 18):
        assert ck.adapted_design_tv(D) == Fraction(1, D)


def test_general_quadratic_irrational_ratio_has_no_nonzero_integer_root():
    # rho = sqrt3/2 (settings 0 and pi/6) is a root of 4 t^2 - 3: the binary form
    # 4 m2^2 - 3 m1^2 never vanishes off the origin, which drives the Omega(1/D^2) bound.
    for m1 in range(-60, 61):
        for m2 in range(-60, 61):
            if (m1, m2) != (0, 0):
                assert 4 * m2 * m2 - 3 * m1 * m1 != 0


def test_pell_renderer_is_an_exact_werner_law_at_a_nearby_cosine():
    # The Pell renderer uses x' = Q/P times v on the pi/4 settings: a Werner law at
    # cosine Q/P, within 1/(sqrt2 P^2) of 1/sqrt2. A cosine uncertainty of that
    # order therefore puts it inside the family (the exact-angle assumption).
    for P, Q in ck.pell_pairs(2000):
        assert P * P - 2 * Q * Q in (1, -1)
        gap = abs(Decimal(Q) / Decimal(P) - ck.R_INV_SQRT2)
        assert gap < 1 / (Decimal(2).sqrt() * P * P)


def test_every_werner_correlator_is_within_two_over_d_of_the_lattice():
    for D in (4, 8, 16, 64):
        lattice = [Fraction(4 * j - D, D) for j in range(D // 2 + 1)]
        for i in range(-50, 51):
            x = Fraction(i, 50)
            assert min(abs(x - y) for y in lattice) <= Fraction(2, D)


def test_receipt_matches_committed_receipt():
    committed = (ROOT / "receipts" / "finite-precision-renderer-identifiability.txt").read_text(encoding="utf-8")
    assert ck.receipt_text() == committed
