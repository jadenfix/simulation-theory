"""Tests for the two-view orthogonal fiber (ST-T297 to ST-T305, ST-M86 to ST-M89, ST-F59)."""

import pathlib
from fractions import Fraction

F = Fraction

from simtheory import two_view_fiber as check
from simtheory.two_view_fiber import (
    A2_EXPECTED,
    K2,
    K3,
    K3_ANCHORED,
    O2,
    PI2,
    PI2_PRIME_EXPECTED,
    PI3,
    S2,
    S3,
    S3_SKEW,
    anchor_model,
    cayley,
    det,
    diag,
    fiber_point,
    floor_sharpness_k3,
    identified_interval_k2,
    inv,
    is_orthogonal,
    is_permutation,
    is_row_stochastic,
    mat,
    mm,
    mv,
    one_view,
    rot2,
    skew3,
    three_view,
    tr,
    two_view,
    weight_floor,
)


def F(n, d=1):
    return Fraction(n, d)


def test_signed_gauge_preserves_one_and_two_view_laws_but_not_three_view():
    pip, Kp, A = fiber_point(S2, K2, O2)
    assert is_orthogonal(O2)
    assert A == A2_EXPECTED
    assert any(x < 0 for r in A for x in r)
    assert not is_permutation(A)
    assert pip == PI2_PRIME_EXPECTED
    assert all(x > 0 for r in Kp for x in r) and is_row_stochastic(Kp)
    assert one_view(PI2, K2) == one_view(pip, Kp)
    assert two_view(PI2, K2) == two_view(pip, Kp)
    assert three_view(PI2, K2) != three_view(pip, Kp)
    assert mm(mm(tr(A), diag(pip)), A) == diag(PI2)


def test_every_alternative_factorization_is_a_weighted_orthogonal_gauge():
    pip, Kp, _ = fiber_point(S2, K2, O2)
    A = check.gauge_from_factorizations(K2, Kp)
    assert all(sum(r) == 1 for r in A)
    u = mv(O2, S2)
    assert [x * x for x in u] == pip
    O = mm(mm(diag(u), A), diag([1 / x for x in S2]))
    assert O == O2 and is_orthogonal(O)


def test_three_state_cayley_witness_is_an_interior_fiber_point():
    O = cayley(S3_SKEW)
    assert is_orthogonal(O)
    pip, Kp, A = fiber_point(S3, K3, O)
    assert pip != PI3
    assert any(x < 0 for r in A for x in r)
    assert all(x > 0 for r in Kp for x in r) and is_row_stochastic(Kp)
    assert two_view(PI3, K3) == two_view(pip, Kp)
    assert three_view(PI3, K3) != three_view(pip, Kp)


def test_three_state_interior_fiber_is_locally_three_dimensional():
    for args in [(F(1, 100), 0, 0), (0, F(1, 100), 0), (0, 0, F(1, 100))]:
        for sg in (1, -1):
            O = cayley(skew3(*[sg * F(a) for a in args]))
            assert fiber_point(S3, K3, O) is not None


def test_different_channel_signed_fiber_has_two_independent_gauges():
    pi = [F(2, 5), F(3, 5)]
    K1 = mat([[F(1, 2), F(1, 4), F(1, 4)], [F(1, 6), F(1, 3), F(1, 2)]])
    K2b = mat([[F(3, 5), F(2, 5)], [F(1, 4), F(3, 4)]])
    A = mat([[F(11, 10), F(-1, 10)], [F(1, 20), F(19, 20)]])
    pip = mv(tr(inv(A)), pi)
    B = mm(mm(diag([1 / x for x in pip]), tr(inv(A))), diag(pi))
    assert pip == [F(1, 3), F(2, 3)]
    assert B == mat([[F(38, 35), F(-3, 35)], [F(2, 35), F(33, 35)]])
    assert B != A and all(sum(r) == 1 for r in B)
    assert is_row_stochastic(mm(A, K1)) and is_row_stochastic(mm(B, K2b))
    assert two_view(pip, mm(A, K1), mm(B, K2b)) == two_view(pi, K1, K2b)


def test_nonnegative_product_gauge_forces_the_same_permutation():
    pi = [F(2, 5), F(3, 5)]
    survivors = []
    grid = [F(j, 4) for j in range(5)]
    for a in grid:
        for b in grid:
            A = mat([[a, 1 - a], [b, 1 - b]])
            if det(A) == 0:
                continue
            pip = mv(tr(inv(A)), pi)
            if any(x <= 0 for x in pip):
                continue
            B = mm(mm(diag([1 / x for x in pip]), tr(inv(A))), diag(pi))
            if all(x >= 0 for r in B for x in r):
                survivors.append((A, B))
    assert len(survivors) == 2
    assert all(is_permutation(A) and A == B for A, B in survivors)


def test_binary_identified_interval_is_rational_in_the_observable_law():
    q, T = one_view(PI2, K2), two_view(PI2, K2)
    L, U, y = identified_interval_k2(q, T, 0)
    assert (L, U, y) == (F(144, 1825), F(1849, 2425), 2)
    assert U == q[0] ** 2 / T[0][0]
    assert L == 1 - q[2] ** 2 / T[2][2]
    assert L < PI2[0] < U


def test_binary_interval_endpoints_are_attained_by_anchor_models():
    q, T = one_view(PI2, K2), two_view(PI2, K2)
    pU, KU = anchor_model(q, T, 0)
    assert pU[0] == F(1849, 2425) and KU[1][0] == 0
    assert is_row_stochastic(KU) and two_view(pU, KU) == T
    pR, KR = anchor_model(q, T, 2)
    assert 1 - pR[0] == F(144, 1825) and KR[1][2] == 0
    assert is_row_stochastic(KR) and two_view(pR, KR) == T


def test_rational_rotation_grid_stays_inside_the_interval_and_is_an_arc():
    q, T = one_view(PI2, K2), two_view(PI2, K2)
    L, U, _ = identified_interval_k2(q, T, 0)
    ts = [F(j, 100) for j in range(-50, 51)]
    adm = [(i, fiber_point(S2, K2, rot2(t))) for i, t in enumerate(ts)]
    adm = [(i, r) for i, r in adm if r is not None]
    idx = [i for i, _ in adm]
    assert idx == list(range(idx[0], idx[-1] + 1))
    assert ts.index(F(0)) in idx
    vals = [r[0][0] for _, r in adm]
    assert all(L <= v <= U for v in vals)
    assert all(a > b for a, b in zip(vals, vals[1:]))
    assert all(two_view(r[0], r[1]) == T for _, r in adm)


def test_rotations_just_past_the_arc_violate_nonnegativity():
    sec = check.section_B_k2()
    assert sec["endpoint_probes_inside_ok_outside_fail"] == {"lo": (True, True), "hi": (True, True)}


def test_interval_is_a_point_exactly_when_both_latents_have_anchors():
    pi = [F(9, 25), F(16, 25)]
    K = mat([[F(1, 2), F(1, 2), 0], [0, F(1, 3), F(2, 3)]])
    L, U, _ = identified_interval_k2(one_view(pi, K), two_view(pi, K), 0)
    assert L == U == pi[0]
    K1a = mat([[F(1, 2), F(1, 2), 0], [F(1, 4), F(1, 4), F(1, 2)]])
    L, U, _ = identified_interval_k2(one_view(pi, K1a), two_view(pi, K1a), 0)
    assert L == pi[0] and U == F(289, 325) and U > pi[0]


def test_pr68_counterexample_pair_is_the_lower_endpoint_anchor_model():
    sec = check.section_B_anchor_cases()
    assert sec["pr68_interval"] == ("1/5", "4/5")
    assert sec["pr68_pair_is_L_endpoint"]


def test_anchored_three_state_channel_admits_only_relabelings_on_a_cayley_grid():
    grid = [F(j, 40) for j in range(-3, 4)]
    for a in grid:
        for b in grid:
            for c in grid:
                if a == b == c == 0:
                    continue
                assert fiber_point(S3, K3_ANCHORED, cayley(skew3(a, b, c))) is None
    q, T = one_view(PI3, K3_ANCHORED), two_view(PI3, K3_ANCHORED)
    assert [q[x] ** 2 / T[x][x] for x in range(3)] == PI3


def test_weight_floor_is_sharp_for_k2_and_attained_for_the_k3_witness():
    q, T = one_view(PI2, K2), two_view(PI2, K2)
    L, U, _ = identified_interval_k2(q, T, 0)
    assert weight_floor(S2, K2) == min(L, 1 - U)
    ell, _, _, attained = floor_sharpness_k3(S3, K3)
    assert ell == F(4, 153) and attained
    assert ell <= min(PI3)


def test_receipt_verdict_passes_and_matches_saved_receipt():
    sections = check.run()
    assert check.verdict(sections) == []
    root = pathlib.Path(__file__).resolve().parents[1]
    saved = (root / "receipts" / "two-view-orthogonal-fiber.txt").read_text(encoding="utf-8")
    assert check.receipt_text() == saved


def test_k3_grid_points_reproduce_the_two_view_law_and_values_are_label_free():
    section = check.section_k3_inner_outer()
    assert section["grid_reproduces_T"] is True
    assert section["exact_first_weights_min_max_label_free"] == ("784/23409", "1369/2025")
    assert section["grid_adjacency_components"] > 1


def test_scattered_channel_without_anchors_is_point_identified():
    section = check.section_no_anchor_scattered()
    assert section["no_anchor_column"] and section["rank_K"] == 3
    assert section["rays_satisfy_sum_ge_norm_strict_off_axes"]
    assert section["cayley_grid_nonpermutation_admissible"].startswith("0/")


def test_nested_row_supports_break_point_identification():
    section = check.section_incomparable_supports()
    assert section["small_rotation_admissible"] and section["prior_changes"] and section["two_view_equal"]
    for t in (F(1, 100), F(1, 20)):
        _, result = check.nested_support_rotation(check.S_NESTED, check.K_NESTED, 0, 1, t)
        assert result is not None
        pip, Kp, _ = result
        assert check.two_view(pip, Kp) == check.two_view(check.PI_NESTED, check.K_NESTED)
        assert pip != check.PI_NESTED


def test_upper_endpoint_is_discontinuous_where_an_outcome_probability_vanishes():
    section = check.section_incomparable_supports()
    assert section["upper_endpoint_by_eps"] == {"1/100": "1/2", "1/1000": "1/2", "0": "4/5"}
