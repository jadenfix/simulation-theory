"""Tests for the CHSH escape-route frontiers and the Delft anytime-valid check (ST-T281 to ST-T285, ST-M85, ST-F56)."""

import itertools
from fractions import Fraction as Fr
from math import isclose, log, sqrt
from pathlib import Path

import pytest

from simtheory import bell_escape_routes as check
from simtheory.bell_escape_routes import (
    DETECTION_MODEL,
    ETA_STAR,
    OUT3,
    SQRT2,
    XI,
    Q2,
    bet_conditional_mean,
    ch_value_behaviour,
    ch_value_deterministic,
    check_dual_inequality,
    constant_bet_ceiling,
    crossing_probability,
    detection_behaviour,
    fixed_bet_e_value,
    flag_strategies,
    isotropic_box,
    kl_bern,
    kl_joint,
    load_delft,
    local_mixture_law,
    local_strategies,
    losing_pairs,
    measurement_dependence_model,
    mixture_by_antiderivative,
    model_behaviour,
    prefix_counts,
    signalling_strategies,
    uniform_mixture_e_value,
    upper_concave_hull,
)


@pytest.fixture(scope="module")
def delft_counts():
    return prefix_counts(load_delft())


@pytest.fixture(scope="module")
def ternary():
    return signalling_strategies()


# ---------------------------------------------------------------- Theorem 1


@pytest.mark.parametrize("f", [Fr(3, 4), Fr(4, 5), XI])
def test_betting_factor_has_mean_at_most_one_under_the_conditional_null(f):
    for q in (f, (f + 1) / 2, Fr(99, 100), Fr(1)):
        for p in (Fr(0), f / 2, f):
            mean = bet_conditional_mean(q, f, p)
            assert mean == 1 + (p - f) * (q - f) / (f * (1 - f))
            assert mean <= 1
        assert bet_conditional_mean(q, f, f) == 1


def test_mixture_closed_form_matches_independent_expansion():
    for f in (Fr(3, 4), Fr(5, 7), XI):
        for k, m in itertools.product(range(7), repeat=2):
            assert uniform_mixture_e_value(k, m, f) == mixture_by_antiderivative(k, m, f)
    assert uniform_mixture_e_value(0, 0, Fr(3, 4)) == 1


def test_mixture_is_bounded_by_the_best_constant_bet():
    for f in (Fr(3, 4), Fr(9, 10)):
        for k, m in itertools.product(range(12), repeat=2):
            assert uniform_mixture_e_value(k, m, f) <= constant_bet_ceiling(k, m, f)


def test_exact_ville_crossing_audit_under_iid_null():
    assert crossing_probability(Fr(3, 4), Fr(3, 4), 30, Fr(4)) <= Fr(1, 4)
    assert crossing_probability(Fr(3, 4), Fr(1, 2), 30, Fr(4)) <= Fr(1, 4)


# ---------------------------------------------------------------- Theorem 2


def test_free_silence_signalling_frontier(ternary):
    assert len(ternary) == 2304
    assert upper_concave_hull(ternary) == [(Fr(0), Fr(3, 4)), (Fr(1, 2), Fr(1)), (Fr(1), Fr(1))]
    assert check_dual_inequality(ternary, Fr(1, 2), Fr(3, 4))
    assert not check_dual_inequality(ternary, Fr(1, 2) - Fr(1, 100), Fr(3, 4))
    assert not check_dual_inequality(ternary, Fr(1, 2), Fr(3, 4) - Fr(1, 100))


def test_x_independent_send_flag_frontier(ternary):
    flags = flag_strategies()
    assert len(flags) == 272
    assert upper_concave_hull(flags) == [(Fr(0), Fr(3, 4)), (Fr(1), Fr(1))]
    assert check_dual_inequality(flags, Fr(1, 4), Fr(3, 4))
    assert set(flags) <= set(ternary)


def test_s_value_forms_of_the_signalling_frontiers():
    for c in (Fr(0), Fr(1, 8), Fr(1, 2)):
        assert 8 * (Fr(3, 4) + c / 2) - 4 == 2 + 4 * c
        assert 8 * (Fr(3, 4) + c / 4) - 4 == 2 + 2 * c


def test_every_local_strategy_loses_an_odd_number_of_pairs():
    counts = sorted(len(losing_pairs(A, B)) for A, B in local_strategies())
    assert counts == [1] * 8 + [3] * 8


@pytest.mark.parametrize("l", [Fr(0), Fr(1, 10), Fr(1, 4)])
def test_measurement_dependence_attaining_model(l):
    joint, chosen = measurement_dependence_model(l)
    assert sum(joint.values()) == 1
    for pair in check.PAIRS:
        assert sum(joint[(j, pair)] for j in range(4)) == Fr(1, 4)
    assert all(4 * p >= l for p in joint.values())
    win = sum(
        p for (j, pair), p in joint.items() if (chosen[j][0][pair[0]] ^ chosen[j][1][pair[1]]) == (pair[0] & pair[1])
    )
    assert win == 1 - l
    assert 8 * win - 4 == 4 - 8 * l


def test_tau_predictability_gives_a_tighter_local_bound_than_xi():
    l = (Fr(1, 2) - check.TAU) ** 2
    assert 1 - l < XI


def test_q_sqrt2_sign_is_exact():
    assert (SQRT2 - Fr(141421, 100000)).sign() == 1
    assert (SQRT2 - Fr(141422, 100000)).sign() == -1
    assert (ETA_STAR * (1 + SQRT2) - 2).sign() == 0


def test_detection_threshold_local_model_is_exact():
    target = detection_behaviour(ETA_STAR)
    model = model_behaviour(DETECTION_MODEL)
    assert len(DETECTION_MODEL) == 17
    assert all(w.sign() == 1 for _, _, w in DETECTION_MODEL)
    assert all(model[key] == target[key] for key in target)


def test_detection_threshold_ch_certificate():
    det = [(A, B) for A in itertools.product(OUT3, repeat=2) for B in itertools.product(OUT3, repeat=2)]
    assert max(ch_value_deterministic(A, B) for A, B in det) == 0
    assert ch_value_behaviour(detection_behaviour(ETA_STAR)).sign() == 0
    assert ch_value_behaviour(detection_behaviour(Q2(Fr(829, 1000)))).sign() == 1
    assert ch_value_behaviour(detection_behaviour(Q2(Fr(828, 1000)))).sign() == -1
    assert isclose(float(ETA_STAR), 0.8284271247461903)


# ---------------------------------------------------------------- Theorems 3 and 4


def test_statistical_strength_at_full_visibility():
    w = (2 + sqrt(2)) / 4
    assert isclose(kl_bern(w, 0.75) / log(2), 0.0462738, abs_tol=5e-8)
    iso = isotropic_box(0.5)
    lstar = local_mixture_law([Fr(1, 8) if len(losing_pairs(*s)) == 1 else 0 for s in local_strategies()])
    assert all(isclose(lstar[k], iso[k], abs_tol=1e-15) for k in iso)
    assert isclose(kl_joint(isotropic_box(1 / sqrt(2)), iso), kl_bern(w, 0.75), rel_tol=1e-13)


def test_statistical_strength_vanishes_below_the_chord():
    # v <= 1/sqrt 2: P_v = t L* + (1-t) U with t = v sqrt 2 is local, so D = 0
    v = 0.6
    t = v * sqrt(2)
    iso = isotropic_box(0.5)
    uniform = local_mixture_law([1 / 16] * 16)
    mix = {k: t * iso[k] + (1 - t) * uniform[k] for k in iso}
    target = isotropic_box(v / sqrt(2))
    assert all(isclose(mix[k], target[k], abs_tol=1e-15) for k in iso)


def test_expected_sample_size_floor_at_tsirelson_rate():
    d = kl_bern((2 + sqrt(2)) / 4, float(XI))
    assert 93 < log(20) / d < 94


# ---------------------------------------------------------------- Delft


def test_delft_counts(delft_counts):
    assert len(delft_counts) == 245
    assert delft_counts[-1] == (196, 49)
    assert delft_counts[5] == (6, 0)


def test_delft_uniform_mixture_e_values(delft_counts):
    path = [uniform_mixture_e_value(k, m, XI) for k, m in delft_counts]
    assert Fr(13669, 10000) <= path[-1] <= Fr(1367, 1000)
    assert Fr(27815, 10000) <= max(path) <= Fr(27817, 10000)
    assert path.index(max(path)) == 5
    path34 = [uniform_mixture_e_value(k, m, Fr(3, 4)) for k, m in delft_counts]
    assert Fr(13697, 10000) <= path34[-1] <= Fr(13698, 10000)


def test_delft_fixed_bet_at_tsirelson_like_rate_loses(delft_counts):
    k, m = delft_counts[-1]
    assert fixed_bet_e_value(k, m, Fr(17, 20), Fr(3, 4)) < 1
    assert fixed_bet_e_value(k, m, Fr(17, 20), XI) < 1


def test_delft_constant_bet_ceilings(delft_counts):
    final = constant_bet_ceiling(196, 49, Fr(3, 4))
    assert final == (Fr(16, 15) ** 196) * (Fr(4, 5) ** 49)
    assert isclose(log(float(final)), 245 * kl_bern(0.8, 0.75), rel_tol=1e-12)
    assert Fr(5559, 1000) <= final <= Fr(556, 100)
    ceilings = [constant_bet_ceiling(k, m, Fr(3, 4)) for k, m in delft_counts]
    best = max(ceilings)
    assert Fr(7779, 1000) <= best <= Fr(778, 100)
    assert ceilings.index(best) + 1 == 241
    # every f >= 3/4 and every data-independent constant-bet mixture over [f,1] stays below 1/alpha = 20
    assert best < 20


def test_delft_anytime_confidence_sets_are_trivial_at_five_percent(delft_counts):
    # spot-check inside the resource ranges; the full-range statement is the ceiling bound above
    for f in (Fr(3, 4), XI, Fr(3, 4) + Fr(1, 200), Fr(4, 5), Fr(9, 10)):
        assert max(uniform_mixture_e_value(k, m, f) for k, m in delft_counts) < 20


def test_four_symbol_alphabet_does_not_change_the_signalling_frontier():
    points = signalling_strategies(3)
    assert len(points) == 16384
    assert max(w - c / 2 for c, w in points) == Fr(3, 4)


def test_delft_setting_counts_context():
    counts = check.delft_setting_counts()
    assert counts == {(0, 0): 53, (0, 1): 79, (1, 0): 62, (1, 1): 51}
    chi2 = sum((Fr(v) - Fr(245, 4)) ** 2 / Fr(245, 4) for v in counts.values())
    assert isclose(float(chi2), 7.9796, abs_tol=1e-4)
    assert isclose(check.chi_square_three_df_tail(chi2), 0.0464, abs_tol=1e-4)


def test_exact_isotropic_local_box():
    weights = [Fr(1, 8) if len(losing_pairs(*s)) == 1 else 0 for s in local_strategies()]
    assert check.local_mixture_law_exact(weights) == check.isotropic_box_exact(Fr(3, 4))


def test_fixed_n_binomial_p_value_against_xi():
    # P(Bin(245, xi) >= 196) = 0.039175, so 1/p = 25.53 (context for ST-F50).
    from math import comb as _comb

    xi = float(XI)
    tail = sum(_comb(245, j) * xi**j * (1 - xi) ** (245 - j) for j in range(196, 246))
    assert isclose(tail, 0.039175, abs_tol=2e-6)


def test_receipt_matches_committed_receipt():
    root = Path(__file__).resolve().parents[1]
    committed = (root / "receipts" / "bell-escape-route-frontiers.txt").read_text(encoding="utf-8")
    assert check.receipt_text() == committed
