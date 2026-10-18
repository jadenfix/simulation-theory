"""Tests for the evidence scaling dichotomy (ST-T272 to ST-T280, ST-M84, ST-F53 to ST-F55).

Derivation: docs/evidence-scaling-dichotomy.md. Module: simtheory.evidence_scaling.
"""

from __future__ import annotations

import itertools
from decimal import Decimal, localcontext
from fractions import Fraction
from math import comb
from pathlib import Path

import pytest

from simtheory import evidence_scaling as esd

ROOT = Path(__file__).resolve().parents[1]
TOL = esd.TOL
HALF = esd.HALF
third = Fraction(1, 3)


@pytest.fixture(autouse=True)
def _decimal_context():
    with localcontext(esd.CONTEXT):
        yield


# ---------------------------------------------------------------- Part I


def test_kt_closed_form_matches_sequential_product():
    for n in range(1, 11):
        for bits in itertools.product((0, 1), repeat=n):
            assert esd.kt_sequential_bayes_factor(bits) == esd.kt_bayes_factor(sum(bits), n)


def test_pathwise_regret_sandwich_is_exact_upper_and_strict_lower():
    for n in range(1, 65):
        for k in range(n + 1):
            ratio = esd.kt_regret_ratio(k, n)
            assert ratio * ratio <= 4 * n
            assert esd.dln(ratio) - HALF * (esd.PI * n / 2).ln() > TOL
    # The upper constant ln 2 is attained at n = 1.
    assert esd.kt_regret_ratio(0, 1) == 2


def test_pathwise_upper_bound_log_bf_at_most_n_kl_of_empirical_frequency():
    for n in range(1, 41):
        for k in range(n + 1):
            bf = esd.kt_bayes_factor(k, n)
            assert bf <= esd.ml_probability(k, n) * 2**n


def test_chi_square_identity_is_exact():
    for n in range(1, 25):
        for q in (Fraction(1, 7), Fraction(1, 2), Fraction(5, 6)):
            total = sum(
                comb(n, k) * q**k * (1 - q) ** (n - k) * n * (Fraction(k, n) - q) ** 2 / (q * (1 - q))
                for k in range(n + 1)
            )
            assert total == 1


def test_expected_log_bf_non_asymptotic_sandwich_and_shrinking_remainder():
    upper_const = 1 - esd.REGRET_LOW
    for q in (Fraction(1, 10), Fraction(1, 3), Fraction(1, 2)):
        previous = None
        for n in (16, 64, 256, 1024):
            e = esd.expected_log_bf(n, q)
            base = n * esd.kl_to_fair(q) - HALF * Decimal(n).ln()
            assert e - (base - esd.LN2) > TOL
            assert base + upper_const - e > TOL
            assert n * esd.kl_to_fair(q) - e > TOL
            r = abs(esd.remainder(n, q, e))
            if previous is not None:
                assert r < previous
            previous = r
    assert abs(esd.remainder(5000, Fraction(1, 3), esd.expected_log_bf(5000, Fraction(1, 3)))) < Decimal("1e-5")


def test_boundary_source_has_constant_minus_half_ln_pi():
    for n in (64, 1024):
        value = esd.expected_log_bf(n, Fraction(0))
        assert value == esd.dln(Fraction(comb(2 * n, n), 2**n))
        gap = value - (n * esd.LN2 - HALF * Decimal(n).ln() + esd.CONST_BOUNDARY)
        assert -Decimal(1) / (7 * n) < gap < -Decimal(1) / (9 * n)


def test_beacon_scale_regressions():
    from simtheory.real_data import beacon_bits, load_beacon_summary

    _, pulses = load_beacon_summary()
    bits = beacon_bits(pulses[:-1])
    n, k = len(bits), sum(bits)
    assert (n, k) == (131072, 65461)
    alpha, beta = Fraction(1, 100), Fraction(1, 20)
    d = esd.sufficient_radius(n, alpha)
    t = esd.hoeffding_slack(n, beta)
    assert Fraction(42686, 10**9) < Fraction(str(d * d)) < Fraction(42687, 10**9)
    assert Decimal("0.009914") < d + t < Decimal("0.009915")
    assert Decimal("0.0020109") < esd.converse_radius(n, alpha, beta) < Decimal("0.0020110")
    observed = esd.dln(esd.kt_bayes_factor(k, n))
    assert Decimal("-6.0318") < observed < Decimal("-6.0316")
    logs = esd.centered_log_bf(n, 900)
    threshold = esd.dln(Fraction(100))
    j_star = next(j for j in range(901) if logs[n // 2 + j] >= threshold)
    assert j_star == 839
    assert esd.necessary_radius(n, alpha) * n <= j_star <= esd.sufficient_radius(n, alpha) * n + 1


def test_small_n_power_frontier_and_le_cam_converse():
    n, alpha, beta = 64, Fraction(1, 10), Fraction(1, 10)
    d = esd.sufficient_radius(n, alpha)
    t = esd.hoeffding_slack(n, beta)
    conv = esd.converse_radius(n, alpha, beta)
    reject = [esd.kt_bayes_factor(k, n) * alpha >= 1 for k in range(n + 1)]
    assert sum(comb(n, k) for k in range(n + 1) if reject[k]) <= Fraction(2**n) * alpha
    for i in range(n + 1):
        q = Fraction(i, n)
        if abs(esd.dec(q - Fraction(1, 2))) > d + t:
            power = sum(comb(n, k) * q**k * (1 - q) ** (n - k) for k in range(n + 1) if reject[k])
            assert power >= 1 - beta
        if q > Fraction(1, 2) and esd.np_power_exact(n, q, alpha) >= 1 - beta:
            assert esd.dec(q - Fraction(1, 2)) >= conv


def test_coarsening_contracts_bias_and_keeps_fair_law_fair():
    for f in (Fraction(0), Fraction(1, 10), Fraction(1, 4)):
        for q in (Fraction(0), Fraction(1, 5), Fraction(1, 2), Fraction(9, 10)):
            observed = f + (1 - 2 * f) * q
            assert observed - Fraction(1, 2) == (1 - 2 * f) * (q - Fraction(1, 2))
            assert esd.kl_to_fair(observed) <= esd.kl_to_fair(q) + TOL


# ---------------------------------------------------------------- Part II


BINARY = ([Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 4), Fraction(3, 4)], [[1 - third, third], [third, 1 - third]])


def test_persistent_cap_monotonicity_gap_identity_and_reported_values():
    a, b, rows = BINARY
    cap = esd.kl_vector(a, b)
    assert abs(cap - HALF * Decimal(3).ln()) < TOL
    previous = Decimal(-1)
    values = {}
    for length in (1, 2, 4, 8, 16, 32, 64):
        audit = esd.persistent_audit(a, b, rows, rows, length)
        kl_t = audit["kl_t"]
        assert previous - TOL < kl_t < cap
        assert abs((cap - kl_t) - audit["gap_direct"]) < TOL
        bound, bhatt = esd.gap_bound(a, b, rows, length, audit["map_error"])
        assert cap - kl_t <= bound + TOL <= bhatt + 2 * TOL
        previous = kl_t
        values[length] = kl_t
    assert round(values[1], 3) == Decimal("0.056")
    assert round(values[4], 3) == Decimal("0.179")  # the sketch's 0.180 is a rounding slip
    assert round(values[16], 3) == Decimal("0.409")
    assert round(values[64], 3) == Decimal("0.544")


def test_support_mismatch_gap_bound_and_decay():
    a = [Fraction(1, 2), Fraction(1, 2), Fraction(0)]
    b = [third, third, third]
    rows = [[Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 4), Fraction(3, 4)]]
    cap = esd.kl_vector(a, b)
    gaps = []
    for length in (4, 16, 64):
        audit = esd.persistent_audit(a, b, rows, rows, length)
        gap = cap - audit["kl_t"]
        bound, _ = esd.gap_bound(a, b, rows, length, audit["map_error"])
        assert Decimal(0) < gap <= bound + TOL
        gaps.append(gap)
    assert gaps[0] > gaps[1] > gaps[2]


def test_infinite_cap_does_not_force_infinite_transcript_kl():
    a, b = [Fraction(1, 2), Fraction(1, 2)], [Fraction(1), Fraction(0)]
    same = [[Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 2), Fraction(1, 2)]]
    assert esd.kl_vector(a, b) is None
    assert esd.persistent_audit(a, b, same, same, 6)["kl_t"] == 0


def test_non_identifying_components_leave_a_positive_gap():
    a = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
    b = [Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)]
    rows = [[Fraction(3, 4), Fraction(1, 4)], [Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 4), Fraction(3, 4)]]
    merged = esd.kl_vector([a[0] + a[1], a[2]], [b[0] + b[1], b[2]])
    kl_t = esd.persistent_audit(a, b, rows, rows, 32)["kl_t"]
    assert kl_t <= merged + TOL
    assert esd.kl_vector(a, b) - merged > Decimal("0.1")


def test_component_kernel_decomposition_bound_and_linear_growth():
    a, b, rows_a = BINARY
    rows_b = [[Fraction(3, 5), Fraction(2, 5)], [Fraction(2, 5), Fraction(3, 5)]]
    cap = esd.kl_vector(a, b)
    within = sum(esd.dec(am) * esd.bernoulli_kl(ra[1], rb[1]) for am, ra, rb in zip(a, rows_a, rows_b))
    for length in (1, 8, 64):
        kl_t = esd.persistent_audit(a, b, rows_a, rows_b, length)["kl_t"]
        assert kl_t <= cap + length * within + TOL
    assert esd.persistent_audit(a, b, rows_a, rows_b, 128)["kl_t"] > cap


def test_continuous_latent_bias_cap_ln_four_over_pi():
    cap = (Decimal(4) / esd.PI).ln()
    previous = Decimal(-1)
    for n in (1, 4, 16, 64):
        value = esd.jeffreys_vs_uniform_kl(n)
        assert previous - TOL < value < cap
        previous = value


def test_only_if_counterexamples_have_zero_gap_without_identifying_m():
    for _, a, b, rows, lengths in esd.ONLY_IF_COUNTEREXAMPLES:
        cap = esd.kl_vector(a, b)
        assert abs(cap - Decimal("0.143841")) < Decimal("1e-6")
        for length in lengths:
            audit = esd.persistent_audit(a, b, rows, rows, length)
            assert abs(cap - audit["kl_t"]) < TOL
            assert abs(audit["gap_direct"]) < TOL
        # M is not a function of Y: two components share one emission law.
        assert len({tuple(r) for r in rows}) < len(rows)


def _two_sided_kt_power(n: int, j: int, q: Fraction) -> Fraction:
    m = Fraction(n, 2)
    return sum(
        (comb(n, k) * q**k * (1 - q) ** (n - k) for k in range(n + 1) if abs(k - m) >= j),
        Fraction(0),
    )


def test_power_monotone_in_bias_lemma():
    """X7 lemma: symmetric two-sided and one-sided binomial power is monotone in |q - 1/2|."""
    for n in (8, 16, 31):
        for j in range(1, n // 2 + 1):
            grid = [Fraction(i, 40) for i in range(20, 41)]
            powers = [_two_sided_kt_power(n, j, q) for q in grid]
            assert all(x <= y for x, y in zip(powers, powers[1:]))
            mirrored = [_two_sided_kt_power(n, j, 1 - q) for q in grid]
            assert powers == mirrored
        for c in range(n + 1):
            one_sided = [
                sum((comb(n, k) * q**k * (1 - q) ** (n - k) for k in range(c, n + 1)), Fraction(0))
                for q in [Fraction(i, 40) for i in range(41)]
            ]
            assert all(x <= y for x, y in zip(one_sided, one_sided[1:]))


@pytest.mark.slow
def test_receipt_matches_committed_receipt():
    committed = (ROOT / "receipts" / "evidence-scaling-dichotomy.txt").read_text(encoding="utf-8")
    assert esd.receipt_text() == committed


def test_manifest_ids_and_no_em_dashes():
    import json

    manifest = json.loads((ROOT / "claims" / "evidence-scaling-dichotomy-claims.json").read_text(encoding="utf-8"))
    ids = {claim["id"] for claim in manifest["claims"]}
    assert ids == {f"ST-T{i}" for i in range(272, 281)} | {"ST-M84", "ST-F53", "ST-F54", "ST-F55", "ST-O02"}
    for path in ("claims/evidence-scaling-dichotomy-claims.json", "docs/evidence-scaling-dichotomy.md"):
        assert chr(0x2014) not in (ROOT / path).read_text(encoding="utf-8")
