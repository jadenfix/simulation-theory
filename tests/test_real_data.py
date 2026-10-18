from itertools import product
from math import comb, exp, isclose, log, sqrt
from pathlib import Path
from random import Random

import pytest

from simtheory.claims import load_claim_manifest, validate_local_evidence_paths
from simtheory.real_data import (
    BellTrial,
    beacon_bits,
    bernoulli_kl,
    binomial_upper_tail,
    canonical_disk_point,
    chsh_summary,
    classical_chord_tv,
    coarsened_probability,
    delft_valid_trials,
    kt_expected_log_bayes_factor_lower_bound,
    kt_log_bayes_factor_path,
    load_beacon_summary,
    load_delft_summary,
    local_win_probability_bound,
    running_chsh,
    verify_beacon_precommitments,
)
from simtheory.sequential import exact_expected_e_value

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def delft():
    return load_delft_summary()


def test_delft_summary_reproduces_published_chsh_statistic(delft):
    payload, trials = delft
    summary = chsh_summary(trials)
    published = payload["source"]["published_values"]
    assert summary.trials == published["trials"] == 245
    assert summary.wins == 196
    assert summary.counts == (53, 79, 62, 51)
    assert round(summary.s_value, 2) == published["S"]
    assert round(summary.s_error, 2) == published["S_error"]
    assert isclose(summary.s_value, 2.4224998704613703, rel_tol=1e-12)


def test_delft_p_value_matches_publication(delft):
    _, trials = delft
    summary = chsh_summary(trials)
    xi = local_win_probability_bound()
    p_value = binomial_upper_tail(summary.wins, summary.trials, xi)
    assert round(p_value, 3) == 0.039
    # Without the setting-bias correction the bound is exactly 3/4 and p is smaller.
    assert binomial_upper_tail(summary.wins, summary.trials, 0.75) < p_value


def test_delft_point_lies_right_of_the_classical_chord_on_the_canonical_disk(delft):
    _, trials = delft
    summary = chsh_summary(trials)
    x, y = canonical_disk_point(summary.correlations)
    assert isclose(x, summary.s_value / (2 * sqrt(2)), rel_tol=1e-12)
    assert 1 / sqrt(2) < x < 1
    assert x * x + y * y < 1
    assert isclose(classical_chord_tv((x, y)), (summary.s_value - 2) / 8, rel_tol=1e-12)


def test_running_chsh_ends_at_the_full_sample_statistic(delft):
    _, trials = delft
    path = running_chsh(trials)
    summary = chsh_summary(trials)
    assert path[-1][0] == 245
    assert isclose(path[-1][1], summary.s_value, rel_tol=1e-12)
    assert isclose(path[-1][2], summary.s_error, rel_tol=1e-12)


def test_delft_filter_on_synthetic_rows():
    stamp = "2015-06-26 17:24:12.119993"
    good = f"{stamp},1,2,5445065,1,5690000,0,1,1,10379,10371,11281,13113,0,0,0,0"
    same_detector = good.replace(",5690000,0,", ",5690000,1,")
    outside_herald = good.replace(",5690000,0,", ",5671004,0,")
    late_readout = good.replace(",11281,13113,", ",11281,14400,")
    invalid_marker = good[: -len(",0,0")] + ",12,0"
    excitation = good.replace(",13113,0,0,0,0", ",13113,7,0,0,0")
    rows = [good, same_detector, outside_herald, late_readout, invalid_marker, excitation]
    assert delft_valid_trials(rows) == [BellTrial(stamp, 1, 1, 1, 1), BellTrial(stamp, 1, 1, 1, -1)]


def test_local_hidden_variable_strategies_never_beat_three_quarters():
    # Exhaust the 16 deterministic local strategies; mixtures are convex combinations.
    best = 0.0
    for fa0 in (-1, 1):
        for fa1 in (-1, 1):
            for fb0 in (-1, 1):
                for fb1 in (-1, 1):
                    wins = sum(
                        (-1) ** (a * b) * (fa0, fa1)[a] * (fb0, fb1)[b] == 1 for a in (0, 1) for b in (0, 1)
                    )
                    best = max(best, wins / 4)
    assert best == 0.75 == local_win_probability_bound(0.0)


def test_beacon_precommitment_chain_and_bits():
    payload, pulses = load_beacon_summary()
    assert verify_beacon_precommitments(pulses) == payload["count"] - 1 == 256
    bits = beacon_bits(pulses[:-1])
    assert len(bits) == 256 * 512
    ones = sum(bits)
    # A loose four-sigma sanity window for fair bits; the data are fixed and committed.
    assert abs(ones - len(bits) / 2) < 4 * sqrt(len(bits)) / 2
    tampered = [dict(p) for p in pulses[:3]]
    tampered[1]["localRandomValue"] = "00" * 64
    with pytest.raises(ValueError):
        verify_beacon_precommitments(tampered)


def test_beacon_bits_keep_the_composite_bayes_factor_near_zero():
    _, pulses = load_beacon_summary()
    bits = beacon_bits(pulses[:-1])
    path = kt_log_bayes_factor_path(bits)
    assert max(path) < log(100)  # never reaches the Ville threshold at alpha = 0.01
    # Under the base law the log Bayes factor drifts only like -(1/2) ln n.
    assert -0.5 * log(len(bits)) - 4 < path[-1] < 4


def test_kt_regret_bound_holds_for_every_short_sequence():
    for n in range(1, 13):
        for ones in range(n + 1):
            bits = [1] * ones + [0] * (n - ones)
            log_marginal = kt_log_bayes_factor_path(bits)[-1] - n * log(2.0)
            best = 0.0
            if 0 < ones < n:
                q = ones / n
                best = ones * log(q) + (n - ones) * log(1 - q)
            assert log_marginal >= best - 0.5 * log(n) - log(2.0) - 1e-12


def test_kt_bayes_factor_is_a_mean_one_martingale_under_fair_bits():
    for n in (1, 5, 10):
        mean = sum(exp(kt_log_bayes_factor_path(bits)[-1]) for bits in product((0, 1), repeat=n)) / 2**n
        assert isclose(mean, 1.0, rel_tol=1e-12)


def test_restricted_simulator_is_detected_at_the_kl_rate():
    for q, flip in ((0.60, 0.0), (0.60, 0.2)):
        seen = coarsened_probability(q, flip)
        finals = []
        for seed in range(20):
            rng = Random(seed)
            bits = [int(rng.random() < seen) for _ in range(3000)]
            finals.append(kt_log_bayes_factor_path(bits)[-1])
        average = sum(finals) / len(finals)
        assert average >= kt_expected_log_bayes_factor_lower_bound(3000, seen) - 3.0
        assert average <= 3000 * bernoulli_kl(seen, 0.5) + 3.0


def test_exact_expected_log_bayes_factor_respects_the_lower_bound():
    for q in (0.3, 0.5, 0.6):
        for n in (1, 4, 9, 16):
            expected = 0.0
            for ones in range(n + 1):
                bits = [1] * ones + [0] * (n - ones)  # KT depends only on the counts
                expected += comb(n, ones) * q**ones * (1 - q) ** (n - ones) * kt_log_bayes_factor_path(bits)[-1]
            assert expected >= kt_expected_log_bayes_factor_lower_bound(n, q) - 1e-12


def test_coarsening_contracts_bias_and_evidence_rate():
    seen = coarsened_probability(0.6, 0.2)
    assert isclose(seen - 0.5, 0.6 * (0.6 - 0.5), rel_tol=1e-12)
    assert bernoulli_kl(seen, 0.5) < bernoulli_kl(0.6, 0.5)
    assert coarsened_probability(0.5, 0.3) == 0.5
    # The fixed-alternative e-process of ST-T08 has expectation one under the null.
    assert isclose(exact_expected_e_value(40, 0.5, 0.5, 0.55), 1.0, rel_tol=1e-9)


def test_real_data_claims_manifest_is_valid():
    path = ROOT / "claims" / "real-data-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, ROOT)
    kinds = {claim["id"]: claim["kind"] for claim in manifest["claims"]}
    assert kinds == {
        "ST-F50": "FINITE_CHECK",
        "ST-F51": "FINITE_CHECK",
        "ST-F52": "FINITE_CHECK",
        "ST-T271": "THEOREM",
        "ST-M83": "MODEL_RESULT",
    }
    assert all(claim["nonclaims"] for claim in manifest["claims"])


def test_delft_schedule_is_the_canonical_schedule_shifted_by_pi():
    from math import pi

    from simtheory.bell_predictive import CANONICAL_CHSH
    from simtheory.quantum_phase import correlation

    delft_alice, delft_bob = (0.0, pi / 2), (-3 * pi / 4, 3 * pi / 4)
    rng = Random(7)
    for _ in range(50):
        v, phi = rng.random(), rng.uniform(-pi, pi)
        for a in (0, 1):
            for b in (0, 1):
                measured = -correlation(v, phi, delft_alice[a], delft_bob[b])  # E[xy] for psi-minus
                canonical = correlation(v, phi, CANONICAL_CHSH.alice_angles[a], CANONICAL_CHSH.bob_angles[b])
                assert isclose(measured, canonical, abs_tol=1e-12)
