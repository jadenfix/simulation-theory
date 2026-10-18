"""Tests for the Bell-disk renderer-memory constants (ST-T290 to ST-T296, ST-F58)."""

import random
from fractions import Fraction as F
from pathlib import Path

from simtheory import bell_disk_zonoid
from simtheory.bell_disk_zonoid import (
    PI_HI,
    PI_LO,
    SQRT2_HI,
    SQRT2_LO,
    SQRT3_LO,
    QS,
    chsh_four_settings_qs,
    chsh_grid_counts,
    chsh_rotated_schedule,
    chsh_section_closed_form,
    clipped_center_tv,
    hexagon_closed_form,
    lemma_poly_gap,
    polar_area,
    polar_vertices,
    random_rational_schedule,
    regular_schedule_qs,
    run,
    final_symmetric_gap,
    served_region_area,
    support,
    zonotope_area,
)


def test_canonical_chsh_polar_square_has_area_32_and_mahler_8():
    two = regular_schedule_qs(2)
    four = chsh_four_settings_qs()
    x = (QS(F(3, 7), 0, 2), QS(F(-2, 5), 1, 2))
    assert support(four, x) == support(two, x)
    assert polar_area(two) == QS(32, 0, 2)
    assert polar_area(two) * zonotope_area(two) == QS(8, 0, 2)


def test_regular_three_direction_area_is_18_sqrt3_and_mahler_9():
    reg3 = regular_schedule_qs(3)
    assert polar_area(reg3) == QS(0, 18, 3)
    assert polar_area(reg3) * zonotope_area(reg3) == QS(9, 0, 3)


def test_regular_four_direction_beats_hexagon_but_not_pi_cubed():
    a4 = polar_area(regular_schedule_qs(4))
    assert a4 == QS(-512, 384, 2)
    # exact rational enclosures: pi^3 < A_4 = 384 sqrt2 - 512 < 18 sqrt3
    assert SQRT2_LO**2 < 2 < SQRT2_HI**2 and SQRT3_LO**2 < 3
    assert PI_HI**3 < -512 + 384 * SQRT2_LO
    assert -512 + 384 * SQRT2_HI < 18 * SQRT3_LO


def test_central_served_set_is_eps_scaled_polar_body():
    eps = F(1, 10)
    assert served_region_area(chsh_rotated_schedule(), [F(0)] * 4, eps) == 32 * eps * eps


def test_off_plane_served_sets_never_exceed_central_area_chsh():
    rng = random.Random(7)
    eps = F(1, 12)
    for _ in range(40):
        c = [F(rng.randint(-20, 20), 30) for _ in range(4)]
        area = served_region_area(chsh_rotated_schedule(), c, eps)
        assert area == chsh_section_closed_form(c, eps)
        assert area <= 32 * eps * eps


def test_off_plane_served_sets_never_exceed_central_area_general():
    rng = random.Random(11)
    eps = F(1, 20)
    for _ in range(12):
        m = rng.choice((3, 4))
        sch = random_rational_schedule(rng, m)
        central = served_region_area(sch, [F(0)] * m, eps)
        assert central == eps * eps * polar_area(sch)
        c = [F(rng.randint(-15, 15), 40) for _ in range(m)]
        assert served_region_area(sch, c, eps) <= central


def test_chsh_grid_count_brackets_renderer_number():
    for n in (40, 80, 160):
        meet, inside, boundary = chsh_grid_counts(n)
        assert meet == inside + boundary
        assert meet >= PI_LO * n * n / 32
        assert meet <= PI_LO * (1 + F(8, n)) ** 2 * n * n / 32
        assert boundary <= PI_LO * n


def test_clipped_centres_still_cover_boundary_cells():
    n = 12
    for i in range(-4, 4):
        for j in range(-4, 4):
            for t1 in (F(0), F(1, 2), F(1)):
                for t2 in (F(0), F(1, 4), F(1)):
                    in_disk, tv = clipped_center_tv(n, i, j, t1, t2)
                    if in_disk:
                        assert tv <= F(1, n)


def test_every_rational_schedule_has_polar_area_above_pi_cubed():
    rng = random.Random(3)
    for _ in range(20):
        sch = random_rational_schedule(rng, rng.randint(2, 6))
        assert polar_area(sch) > PI_HI ** 3


def test_hexagon_closed_form_tiling_covolume_and_lower_bound():
    rng = random.Random(5)
    for _ in range(25):
        sch = random_rational_schedule(rng, 3)
        area = polar_area(sch)
        assert area == hexagon_closed_form(sch)
        v = polar_vertices(sch)
        p1, p2, p3 = v[0], v[1], v[2]
        cov = abs((p1[0] + p2[0]) * (p2[1] + p3[1]) - (p1[1] + p2[1]) * (p2[0] + p3[0]))
        assert cov == area
        assert area * area > 972


def test_polynomial_lemma_and_schur_step_with_equality_case():
    rng = random.Random(9)
    for _ in range(300):
        X = [F(rng.randint(1, 40), rng.randint(1, 9)) for _ in range(3)]
        q = [F(rng.randint(0, 40), rng.randint(1, 9)) for _ in range(3)]
        if sum(q):
            assert lemma_poly_gap(X, q) >= 0
        x, y, z = (F(rng.randint(0, 30), rng.randint(1, 9)) for _ in range(3))
        if x + y + z:
            assert final_symmetric_gap(x, y, z) >= 0
    assert lemma_poly_gap([F(1)] * 3, [F(1)] * 3) == 0
    assert final_symmetric_gap(F(1), F(1), F(1)) == 0
    assert lemma_poly_gap([F(1)] * 3, [F(1), F(1), F(2)]) > 0


def test_two_class_schedules_minimise_at_orthogonal_equal_weights():
    rng = random.Random(13)
    for _ in range(20):
        sch = random_rational_schedule(rng, 2)
        (w1, s1), (w2, s2) = sch
        sin_angle = abs(s1[0] * s2[1] - s1[1] * s2[0])
        assert polar_area(sch) == 8 / (w1 * w2 * sin_angle)
        assert polar_area(sch) >= 32


def test_quick_receipt_passes():
    lines, results = run(quick=True)
    assert lines[-1] == "ALL CHECKS PASSED"
    assert results["chsh_area"] == QS(32, 0, 2)


def test_trine_product_schedule_realizes_regular_three_class_law_with_chsh_violation():
    assert bell_disk_zonoid.trine_product_schedule_class_weights() == {0: F(1, 3), 1: F(1, 3), 2: F(1, 3)}
    assert bell_disk_zonoid.trine_chsh_value() == F(5, 2)


def test_regular_schedules_have_isotropic_centre_fisher_matrix_for_every_m():
    # sum_k cos(2 theta_k) = sum_k sin(2 theta_k) = 0 for theta_k = k pi/m, m >= 2,
    # so sum_k s_k s_k^T / m = I/2; exact for m <= 4 via the receipt, and the
    # cosine sums are checked here numerically for larger m.
    from math import cos, pi, sin

    for m in range(2, 13):
        assert abs(sum(cos(2 * k * pi / m) for k in range(m))) < 1e-12
        assert abs(sum(sin(2 * k * pi / m) for k in range(m))) < 1e-12


def test_receipt_matches_committed_receipt():
    root = Path(__file__).resolve().parents[1]
    committed = (root / "receipts" / "bell-disk-renderer-memory.txt").read_text(encoding="utf-8")
    assert bell_disk_zonoid.receipt_text() == committed
