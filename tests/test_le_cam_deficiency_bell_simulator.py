"""Tests for the Le Cam deficiency of a noisy Bell simulator (ST-T306 to ST-T309, ST-F60)."""

import itertools
from fractions import Fraction
from pathlib import Path

from simtheory import le_cam_deficiency as ck

LAMS = tuple(Fraction(k, 8) for k in range(9))


def test_qsqrt2_arithmetic_and_sign_are_exact():
    r = ck.INV_SQRT2
    assert r * r == Fraction(1, 2)
    assert ck.SQRT2 * r == 1
    assert (ck.QS2(Fraction(7, 5), -1)).sign() == -1  # 1.4 < sqrt2
    assert (ck.QS2(Fraction(71, 50), -1)).sign() == 1  # 1.42 > sqrt2
    assert abs(ck.QS2(-3, 2)) == ck.QS2(3, -2)


def test_mixing_kernel_attains_closed_form_on_both_schedules():
    for cs, pis, C in (ck.canonical_schedule(), ck.rational_schedule()):
        for lam in LAMS:
            delta, ident, naive = ck.primal_certificate(cs, pis, C, lam, ck.V_GRID)
            assert delta == C * (1 - lam) / (2 * (2 - C * lam))


def test_two_point_dual_lower_bound_equals_value_for_every_kernel():
    for cs, _pis, C in (ck.canonical_schedule(), ck.rational_schedule()):
        for lam in LAMS:
            for c in cs:
                w, lower = ck.dual_certificate(c, lam)
                assert lower == ck.formula_delta(C, lam)
                assert 0 <= w <= 1


def test_canonical_chsh_value_at_half_visibility():
    _cs, _pis, C = ck.canonical_schedule()
    delta = ck.formula_delta(C, Fraction(1, 2))
    assert delta == Fraction(1, 2) / (2 * (2 * ck.SQRT2 - Fraction(1, 2)))
    assert abs(float(delta) - 0.107369) < 1e-6


def test_value_lies_strictly_between_naive_bound_and_identity_kernel():
    C = Fraction(3, 5)
    for lam in LAMS[1:-1]:
        delta = ck.formula_delta(C, lam)
        assert C * (1 - lam) / 4 < delta < C * (1 - lam) / 2
    assert ck.formula_delta(C, Fraction(0)) == C / 4  # naive bound is tight at lam = 0


def test_deterministic_frontier_holds_for_all_parameters():
    assert ck.frontier_proof_all_parameters() > 0


def test_worst_setting_deterministic_value_and_strict_gap():
    for cs, pis, C in (ck.canonical_schedule(), ck.rational_schedule()):
        for lam in LAMS:
            worst, averaged = ck.det_values(cs, pis, C, lam)
            assert worst == ck.formula_det_max(C, lam)
            assert averaged >= ck.formula_hull(C, lam)
            if lam < 1:
                assert worst > ck.formula_delta(C, lam)
                assert averaged > ck.formula_delta(C, lam)


def test_no_strict_gap_at_perfect_correlation_and_zero_visibility():
    C, lam = Fraction(1), Fraction(0)
    worst, _ = ck.det_values((C,), (Fraction(1),), C, lam)
    assert worst == ck.formula_delta(C, lam) == Fraction(1, 4)


def test_physics_garbles_exactly_to_simulator():
    for lam in LAMS:
        K = tuple(
            tuple(lam * (1 if i == j else 0) + (1 - lam) / 4 for j in range(4)) for i in range(4)
        )
        for c in (Fraction(3, 5), -ck.INV_SQRT2):
            for v in ck.V_GRID:
                assert ck.push(ck.law(v, c), K) == ck.law(lam * v, c)


def test_risk_transfer_bound_and_its_tightness():
    C, lam = Fraction(3, 5), Fraction(1, 3)
    c = C
    delta = ck.formula_delta(C, lam)
    K = ck.mixing_kernel(ck.formula_s(C, lam), 1)
    losses = [Fraction(x, 3) for x in (-3, -1, 0, 2, 3)]
    for g in itertools.product(losses, repeat=4):  # bounded loss of the decision on outcome z
        for v in ck.V_GRID:
            sim = ck.push(ck.law(lam * v, c), K)
            phys = ck.law(v, c)
            gap = abs(sum(gz * (p - q) for gz, p, q in zip(g, sim, phys)))
            assert gap <= 2 * delta * max(abs(x) for x in g)
    # tightness at v = 0 with loss +1 on correlated outcomes and -1 otherwise
    g = tuple(1 if a * b == 1 else -1 for (a, b) in ck.OUTCOMES)
    sim = ck.push(ck.law(0, c), K)
    phys = ck.law(0, c)
    assert sum(gz * (p - q) for gz, p, q in zip(g, sim, phys)) == 2 * delta


def test_joint_kernel_dual_equals_the_value_under_average_aggregation():
    # The lower bound holds for every Markov kernel on the joint (setting, outcome)
    # record, including kernels that relabel the setting.
    for cs, pis, C in (ck.canonical_schedule(), ck.rational_schedule()):
        for lam in LAMS:
            _, lower = ck.joint_dual_certificate(cs, pis, lam)
            assert lower == ck.formula_delta(C, lam)


def test_setting_relabeling_deterministic_map_beats_the_setting_preserving_hull():
    cs, pis, C = ck.rational_schedule()
    lam = Fraction(1, 4)
    e0, e1 = ck.joint_map_errors(cs, pis, lam, ck.JOINT_DETERMINISTIC_MAP)
    assert (e0, e1) == (Fraction(1, 8), Fraction(23, 160))
    assert ck.formula_hull(C, lam) == Fraction(3, 14)
    assert ck.formula_delta(C, lam) == Fraction(9, 74)
    assert ck.formula_delta(C, lam) < max(e0, e1) < ck.formula_hull(C, lam)
    assert any(ck.JOINT_DETERMINISTIC_MAP[z] // 4 != z // 4 for z in range(16))


def test_corollary_1a_unequal_magnitudes_worst_setting_value():
    cs = (Fraction(1, 2), Fraction(-1, 10), Fraction(3, 5))
    for lam in LAMS:
        worst, lower, target = ck.unequal_worst_setting(cs, lam)
        assert worst == lower == target == ck.formula_delta(Fraction(3, 5), lam)


def test_joint_record_risk_transfer_with_setting_dependent_losses():
    # |R_F - R_E| <= 2 delta ||L|| for losses that depend on the setting, on the
    # joint record, after the optimal setting-preserving kernel.
    cs, pis, C = ck.rational_schedule()
    for lam in (Fraction(1, 4), Fraction(1, 2)):
        delta = ck.formula_delta(C, lam)
        s = ck.formula_s(C, lam)
        kernels = [ck.mixing_kernel(s, ck.sgn(c)) for c in cs]
        for v in (Fraction(0), Fraction(1, 2), Fraction(1)):
            for losses in itertools.product((Fraction(-1), Fraction(1)), repeat=4):
                gap = Fraction(0)
                for i, (c, K, pi) in enumerate(zip(cs, kernels, pis)):
                    simulated = ck.push(ck.law(lam * v, c), K)
                    physical = ck.law(v, c)
                    # setting-dependent loss: losses[i] on agreeing outcomes, -losses[i] otherwise
                    h = [losses[i] if a * b == ck.sgn(c) else -losses[i] for (a, b) in ck.OUTCOMES]
                    gap += pi * sum(hz * (p - q) for hz, p, q in zip(h, simulated, physical))
                assert abs(gap) <= 2 * delta


def test_receipt_matches_committed_receipt():
    root = Path(__file__).resolve().parents[1]
    committed = (root / "receipts" / "le-cam-deficiency-bell-simulator.txt").read_text(encoding="utf-8")
    assert ck.receipt_text() == committed
