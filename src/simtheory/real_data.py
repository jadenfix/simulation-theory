"""Finite checks on published experimental data and public physical randomness.

Two external data sets are used, each reduced to a small committed summary
under ``data/real/`` whose provenance and hashes are recorded in the file:

* the Delft 2015 loophole-free Bell test (Hensen et al., Nature 526, 682-686,
  2015; data set doi:10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31), and
* consecutive pulses of the NIST Randomness Beacon, chain 2.

Nothing here is evidence for or against a simulation hypothesis. The Bell
functions reproduce the published CHSH statistic and place it on the canonical
CHSH disk of ``quantum_phase_geometry``. The beacon functions verify the
beacon's own hash precommitments and supply real bits for the restricted
Bernoulli-signature e-processes of ``sequential``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from math import exp, lgamma, log, sqrt
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .quantum_phase import cartesian_to_polar_state
from .quantum_phase_geometry import canonical_chsh_cartesian_tv

DATA_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "real"
DELFT_SUMMARY_PATH = DATA_DIRECTORY / "delft2015-bell-trials.json"
BEACON_SUMMARY_PATH = DATA_DIRECTORY / "nist-beacon-chain2-pulses.json"

# ---------------------------------------------------------------- Delft 2015

DELFT_ZIP_URL = (
    "https://data.4tu.nl/file/e8cf2991-3153-48ad-b67d-dfd7d7d97fd3/"
    "289c4850-6ed5-45a3-8b19-de8671f873a8"
)
DELFT_ZIP_MD5 = "342f29f8288c46575818acd2acebd535"
DELFT_ZIP_SHA256 = "c28eb0f075759aef620a0b2e00a70fd675ce712bc8214d11c103f5a3d29492c0"
DELFT_RAW_MEMBER = "bell_open_data.txt"

# Published analysis parameters, copied from the authors'
# bell_open_data_analysis_example.py (Supplementary Information sections E, I, K, N).
_EVENT_READY_START = {0: 5426350, 1: 5425700}  # picoseconds after sync pulse
_EVENT_READY_LENGTH = 55000 - 2550  # picoseconds
_EVENT_READY_SEPARATION = 250000  # picoseconds
_READOUT_START = 10620  # nanoseconds
_READOUT_LENGTH = 3700  # nanoseconds
_INVALID_MARKER_LOOKBACK = 250  # sync pulses
DELFT_TAU = 5.4e-6 * 2  # predictability bias bound of the random-number generators

#: Delft setting labels (a, b) -> CHSH sign. S = E00 + E01 + E10 - E11.
DELFT_SETTING_SIGNS: Mapping[tuple[int, int], int] = {(0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): -1}


@dataclass(frozen=True)
class BellTrial:
    """One valid event-ready Bell trial: random inputs a,b and outcomes x,y in {-1,+1}."""

    timestamp: str
    a: int
    b: int
    x: int
    y: int

    def __post_init__(self) -> None:
        if self.a not in (0, 1) or self.b not in (0, 1):
            raise ValueError("settings must be 0 or 1")
        if self.x not in (-1, 1) or self.y not in (-1, 1):
            raise ValueError("outcomes must be -1 or +1")

    @property
    def chsh_win(self) -> bool:
        """CHSH game win: (-1)^(a b) x y = +1."""
        return (-1) ** (self.a * self.b) * self.x * self.y == 1


def _in_event_ready_window(time_ps: int, channel: int, offset: int) -> bool:
    if channel not in _EVENT_READY_START:
        return False
    start = _EVENT_READY_START[channel] + offset
    return start <= time_ps < start + _EVENT_READY_LENGTH


def _no_recent_invalid_marker(pulses_since_marker: int) -> bool:
    return pulses_since_marker == 0 or pulses_since_marker > _INVALID_MARKER_LOOKBACK


def _readout_click(time_ns: int) -> int:
    return 1 if _READOUT_START < time_ns <= _READOUT_START + _READOUT_LENGTH else -1


def delft_valid_trials(lines: Iterable[str]) -> list[BellTrial]:
    """Apply the published Delft valid-trial filter to raw ``bell_open_data.txt`` rows.

    This is a standard-library port of the authors' numpy filter: two
    event-ready photon clicks in opposite detectors inside the declared windows
    (psi-minus heralding), no recent invalid marker at A or B, and no photon
    detected after the excitation pulses. The outcome is +1 when a readout
    photon arrives inside the readout window and -1 otherwise.
    """

    trials: list[BellTrial] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        fields = line.split(",")
        if len(fields) != 17:
            raise ValueError(f"expected 17 comma-separated fields, found {len(fields)}")
        timestamp = fields[0]
        (
            _day,
            _run,
            click1_time,
            click1_channel,
            click2_time,
            click2_channel,
            random_a,
            random_b,
            _random_a_time,
            _random_b_time,
            readout_a,
            readout_b,
            excite_a,
            excite_b,
            invalid_a,
            invalid_b,
        ) = (int(value) for value in fields[1:])
        heralded = (
            _in_event_ready_window(click1_time, click1_channel, 0)
            and _in_event_ready_window(click2_time, click2_channel, _EVENT_READY_SEPARATION)
            and click1_channel != click2_channel
        )
        valid = (
            heralded
            and _no_recent_invalid_marker(invalid_a)
            and _no_recent_invalid_marker(invalid_b)
            and excite_a == 0
            and excite_b == 0
        )
        if valid:
            trials.append(
                BellTrial(timestamp, random_a, random_b, _readout_click(readout_a), _readout_click(readout_b))
            )
    return trials


@dataclass(frozen=True)
class ChshSummary:
    trials: int
    wins: int
    counts: tuple[int, int, int, int]
    correlations: tuple[float, float, float, float]
    correlation_errors: tuple[float, float, float, float]
    s_value: float
    s_error: float


def chsh_summary(trials: Sequence[BellTrial]) -> ChshSummary:
    """CHSH S with the paper's per-setting binomial error, setting order 00, 01, 10, 11."""

    order = ((0, 0), (0, 1), (1, 0), (1, 1))
    counts = []
    correlations = []
    errors = []
    for setting in order:
        products = [t.x * t.y for t in trials if (t.a, t.b) == setting]
        if not products:
            raise ValueError(f"no trials for setting {setting}")
        correlation = sum(products) / len(products)
        counts.append(len(products))
        correlations.append(correlation)
        errors.append(sqrt((1.0 - correlation**2) / len(products)))
    s_value = sum(DELFT_SETTING_SIGNS[setting] * e for setting, e in zip(order, correlations))
    s_error = sqrt(sum(e * e for e in errors))
    return ChshSummary(
        trials=len(trials),
        wins=sum(t.chsh_win for t in trials),
        counts=tuple(counts),  # type: ignore[arg-type]
        correlations=tuple(correlations),  # type: ignore[arg-type]
        correlation_errors=tuple(errors),  # type: ignore[arg-type]
        s_value=s_value,
        s_error=s_error,
    )


def local_win_probability_bound(tau: float = DELFT_TAU) -> float:
    """Per-trial CHSH-game win bound for local models with setting bias tau (Delft SI N)."""

    if not 0.0 <= tau < 0.25:
        raise ValueError("tau must lie in [0, 1/4)")
    return 0.75 + 3.0 * (tau + tau * tau)


def binomial_upper_tail(successes: int, trials: int, probability: float) -> float:
    """P(Binomial(trials, probability) >= successes), summed in log space."""

    if not 0 <= successes <= trials:
        raise ValueError("require 0 <= successes <= trials")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    log_p, log_q = log(probability), log(1.0 - probability)
    terms = [
        lgamma(trials + 1) - lgamma(j + 1) - lgamma(trials - j + 1) + j * log_p + (trials - j) * log_q
        for j in range(successes, trials + 1)
    ]
    peak = max(terms)
    return min(1.0, exp(peak) * sum(exp(t - peak) for t in terms))


def canonical_disk_point(correlations: Sequence[float]) -> tuple[float, float]:
    """Least-squares point q=(x,y) on the canonical CHSH disk for four correlations.

    The Delft schedule (Alice 0, pi/2; Bob -3pi/4, +3pi/4; psi-minus) is the
    canonical schedule with every setting difference shifted by pi, so its
    measured correlations E_00, E_01, E_10, E_11 equal the canonical
    correlations r_theta(q) = x cos(theta) + y sin(theta) at
    theta = -pi/4, pi/4, pi/4, 3pi/4 for a visibility-phase state q. The four
    unit directions satisfy sum s s^T = 2 I, so the equal-weight least-squares
    fit is q = (1/2) sum_j E_j s_j, and in particular x = S / (2 sqrt 2).
    """

    if len(correlations) != 4:
        raise ValueError("four correlations are required")
    e00, e01, e10, e11 = (float(c) for c in correlations)
    scale = 1.0 / (2.0 * sqrt(2.0))
    return scale * (e00 + e01 + e10 - e11), scale * (-e00 + e01 + e10 + e11)


def classical_chord_tv(point: tuple[float, float]) -> float:
    """Canonical-CHSH predictive TV from ``point`` to the S = 2 chord x = 1/sqrt 2.

    The nearest family member on the chord shares the y coordinate, so the
    exact L-infinity identity of ``canonical_chsh_cartesian_tv`` gives
    |x - 1/sqrt 2| / (2 sqrt 2) = |S - 2| / 8. The chord point must lie in the
    unit disk.
    """

    x, y = point
    chord_x = 1.0 / sqrt(2.0)
    if chord_x**2 + y**2 > 1.0 + 1e-12 or x**2 + y**2 > 1.0 + 1e-12:
        raise ValueError("both points must lie in the physical unit disk")
    return canonical_chsh_cartesian_tv(cartesian_to_polar_state(x, y), cartesian_to_polar_state(chord_x, y))


def running_chsh(trials: Sequence[BellTrial]) -> list[tuple[int, float, float]]:
    """(n, S_n, error_n) after each trial once every setting has two trials."""

    sums = {s: 0 for s in DELFT_SETTING_SIGNS}
    counts = {s: 0 for s in DELFT_SETTING_SIGNS}
    path: list[tuple[int, float, float]] = []
    for index, trial in enumerate(trials, start=1):
        key = (trial.a, trial.b)
        sums[key] += trial.x * trial.y
        counts[key] += 1
        if min(counts.values()) < 2:
            continue
        s_value = 0.0
        variance = 0.0
        for setting, sign in DELFT_SETTING_SIGNS.items():
            e = sums[setting] / counts[setting]
            s_value += sign * e
            variance += (1.0 - e * e) / counts[setting]
        path.append((index, s_value, sqrt(variance)))
    return path


def load_delft_summary(path: str | Path = DELFT_SUMMARY_PATH) -> tuple[dict[str, Any], list[BellTrial]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != "simulation-theory.real-data.bell-trials/v1":
        raise ValueError("unsupported Bell-trial summary schema")
    if payload.get("columns") != ["timestamp", "a", "b", "x", "y"]:
        raise ValueError("unexpected Bell-trial columns")
    trials = [BellTrial(*row) for row in payload["trials"]]
    digest = trial_digest(trials)
    if digest != payload["trials_sha256"]:
        raise ValueError("Bell-trial summary digest mismatch")
    return payload, trials


def trial_digest(trials: Sequence[BellTrial]) -> str:
    text = "\n".join(f"{t.timestamp},{t.a},{t.b},{t.x},{t.y}" for t in trials)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- NIST beacon

BEACON_PULSE_URL = "https://beacon.nist.gov/beacon/2.0/chain/{chain}/pulse/{index}"


def verify_beacon_precommitments(pulses: Sequence[Mapping[str, Any]]) -> int:
    """Check SHA-512(localRandomValue[i+1]) == precommitmentValue[i] for consecutive pulses.

    Returns the number of verified links. This checks the beacon's own hash
    commitments; it does not check NIST's RSA signatures or the output hash.
    """

    if len(pulses) < 2:
        raise ValueError("at least two pulses are required")
    for earlier, later in zip(pulses, pulses[1:]):
        if int(later["pulseIndex"]) != int(earlier["pulseIndex"]) + 1:
            raise ValueError("pulses must be consecutive")
        digest = hashlib.sha512(bytes.fromhex(later["localRandomValue"])).hexdigest().upper()
        if digest != str(earlier["precommitmentValue"]).upper():
            raise ValueError(f"precommitment mismatch at pulse {earlier['pulseIndex']}")
    return len(pulses) - 1


def beacon_bits(pulses: Sequence[Mapping[str, Any]]) -> list[int]:
    """Bits of localRandomValue, most significant first, for every pulse in order."""

    bits: list[int] = []
    for pulse in pulses:
        value = bytes.fromhex(pulse["localRandomValue"])
        if len(value) != 64:
            raise ValueError("localRandomValue must be 512 bits")
        for byte in value:
            bits.extend((byte >> shift) & 1 for shift in range(7, -1, -1))
    return bits


def load_beacon_summary(path: str | Path = BEACON_SUMMARY_PATH) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != "simulation-theory.real-data.nist-beacon/v1":
        raise ValueError("unsupported beacon summary schema")
    pulses = payload["pulses"]
    verify_beacon_precommitments(pulses)
    return payload, pulses


# ------------------------------------------- restricted-signature detection rate


def bernoulli_kl(p: float, q: float) -> float:
    """KL(Bernoulli(p) || Bernoulli(q)) in nats."""

    if not 0.0 <= p <= 1.0 or not 0.0 < q < 1.0:
        raise ValueError("require p in [0,1] and q in (0,1)")
    total = 0.0
    if p > 0.0:
        total += p * log(p / q)
    if p < 1.0:
        total += (1.0 - p) * log((1.0 - p) / (1.0 - q))
    return total


def coarsened_probability(probability: float, flip: float) -> float:
    """Law of a Bernoulli bit seen through a binary symmetric channel with flip probability ``flip``.

    The bias about 1/2 contracts by exactly 1 - 2 flip, the channel's Dobrushin
    coefficient (claim ST-M14).
    """

    if not 0.0 <= probability <= 1.0 or not 0.0 <= flip <= 0.5:
        raise ValueError("require probability in [0,1] and flip in [0,1/2]")
    return flip + (1.0 - 2.0 * flip) * probability


def kt_log_bayes_factor_path(bits: Iterable[int]) -> list[float]:
    """Running log Bayes factor of "IID Bernoulli(q), q ~ Beta(1/2,1/2)" against fair bits.

    The composite simulation hypothesis leaves the bias unknown; its marginal
    likelihood is the Krichevsky-Trofimov sequential predictor
    P(x_{t+1}=1 | k ones in t bits) = (k + 1/2) / (t + 1). Under fair bits the
    Bayes factor is a nonnegative martingale with mean one, so Ville's
    inequality bounds the chance it ever reaches 1/alpha by alpha.
    """

    ones = 0
    total = 0.0
    path: list[float] = []
    for trials, bit in enumerate(bits):
        if bit not in (0, 1):
            raise ValueError("bits must be zero or one")
        predictive_one = (ones + 0.5) / (trials + 1)
        total += log((predictive_one if bit else 1.0 - predictive_one) / 0.5)
        ones += bit
        path.append(total)
    return path


def kt_expected_log_bayes_factor_lower_bound(trials: int, true_probability: float) -> float:
    """Exact lower bound n KL(q || 1/2) - (1/2) ln n - ln 2 on E_q[log BF_n].

    The KT mixture satisfies log m(x^n) >= max_q log q^n(x^n) - (1/2) ln n - ln 2
    for every sequence, and E[max_q log q^n(X^n)] >= E[log q_true^n(X^n)].
    Subtracting log 2^{-n} gives the bound.
    """

    if trials < 1:
        raise ValueError("trials must be positive")
    return trials * bernoulli_kl(true_probability, 0.5) - 0.5 * log(trials) - log(2.0)
