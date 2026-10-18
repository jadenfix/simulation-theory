"""Evidence scaling dichotomy: bounded exact and high-precision certificates.

Derivation: docs/evidence-scaling-dichotomy.md (claims ST-T272 to ST-T280,
ST-M84, ST-F53 to ST-F55, ST-O02).

Part I: the Krichevsky-Trofimov (KT) composite Bayes factor of IID
Bernoulli(q) bits against fair bits. Part II: transcript KL between two
mixing-weight hypotheses for one persistent latent draw that share a kernel,
and the different-kernel decomposition.

Arithmetic. Probabilities are exact Fractions or exact integers. Logarithms
are Decimal values at PREC significant digits, computed inside a private
Decimal context (the global context is never modified); Decimal.ln is
correctly rounded, and ln of a huge integer is reduced to ln of a 200-bit
integer plus a multiple of ln 2 (truncation error below 2**-199). Every
comparison that involves a logarithm is asserted with a margin of at least
TOL = 1e-30, while the accumulated rounding error of every sum below is
bounded by (number of operations) * 10**(-PREC + 2) * (largest magnitude)
< 1e-40. Comparisons that need no logarithm are exact rational comparisons.

Standard library only. ``python -m simtheory.evidence_scaling`` prints the
receipt committed as receipts/evidence-scaling-dichotomy.txt.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from decimal import Context, Decimal, localcontext
from fractions import Fraction
from math import comb

PREC = 60
CONTEXT = Context(prec=PREC, Emin=-999999, Emax=999999)
TOL = Decimal("1e-30")

with localcontext(CONTEXT):
    PI = Decimal(
        "3.14159265358979323846264338327950288419716939937510582097494459230781640628620899"
    )
    LN2 = Decimal(2).ln()
    LNPI = PI.ln()
    E1 = Decimal(1).exp()
    HALF = Decimal(1) / 2

    # Asymptotic constants (nats).
    CONST_INTERIOR = HALF * (2 * E1 / PI).ln()  # (1/2) ln(2e/pi) ~ 0.2742
    CONST_BOUNDARY = -HALF * LNPI  # -(1/2) ln pi ~ -0.5724
    REGRET_LOW = HALF * (PI / 2).ln()  # (1/2) ln(pi/2) ~ 0.2258


def precise():
    """Context manager for callers: ``with precise(): ...`` runs at PREC digits.

    The receipt runs inside it; the functions below assume it and never touch
    the global Decimal context.
    """

    return localcontext(CONTEXT)


# ---------------------------------------------------------------------------
# Logarithm helpers
# ---------------------------------------------------------------------------


def ln_int(value: int) -> Decimal:
    """ln of a positive integer, robust for integers with ~10**5 digits."""
    if value <= 0:
        raise ValueError("ln_int needs a positive integer")
    shift = max(0, value.bit_length() - 200)
    return Decimal(value >> shift).ln() + shift * LN2


def dln(x: Fraction) -> Decimal:
    x = Fraction(x)
    if x <= 0:
        raise ValueError("dln needs a positive rational")
    return ln_int(x.numerator) - ln_int(x.denominator)


def dec(x: Fraction) -> Decimal:
    x = Fraction(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def xlnx_ratio(p: Fraction, q: Fraction) -> Decimal:
    """p ln(p/q) with 0 ln 0 = 0."""
    if p == 0:
        return Decimal(0)
    return dec(p) * dln(Fraction(p) / Fraction(q))


def bernoulli_kl(p: Fraction, q: Fraction) -> Decimal:
    p, q = Fraction(p), Fraction(q)
    return xlnx_ratio(p, q) + xlnx_ratio(1 - p, 1 - q)


def kl_vector(a, b) -> Decimal | None:
    """KL(a || b) for finite vectors; None encodes +infinity."""
    total = Decimal(0)
    for am, bm in zip(a, b):
        if am == 0:
            continue
        if bm == 0:
            return None
        total += xlnx_ratio(am, bm)
    return total


# ---------------------------------------------------------------------------
# Part I: KT Bayes factor
# ---------------------------------------------------------------------------


def kt_bayes_factor(ones: int, trials: int) -> Fraction:
    """Exact BF_n = P_KT(x^n) / 2^-n for a sequence with `ones` ones.

    Uses Gamma(m + 1/2) = (2m)! sqrt(pi) / (4^m m!), which turns the Beta
    integral into C(2k,k) C(2n-2k,n-k) / (2^n C(n,k)).
    """
    k, n = ones, trials
    return Fraction(comb(2 * k, k) * comb(2 * n - 2 * k, n - k), 2**n * comb(n, k))


def kt_sequential_bayes_factor(bits) -> Fraction:
    value = Fraction(1)
    ones = 0
    for t, bit in enumerate(bits):
        p_one = Fraction(2 * ones + 1, 2 * t + 2)
        value *= 2 * (p_one if bit else 1 - p_one)
        ones += bit
    return value


def ml_probability(ones: int, trials: int) -> Fraction:
    """max_q q^k (1-q)^(n-k) = (k/n)^k ((n-k)/n)^(n-k), with 0^0 = 1."""
    k, n = ones, trials
    return Fraction(k, n) ** k * Fraction(n - k, n) ** (n - k)


def kt_regret_ratio(ones: int, trials: int) -> Fraction:
    """Exact ratio max_q P_q(x^n) / P_KT(x^n)."""
    return ml_probability(ones, trials) * 2**trials / kt_bayes_factor(ones, trials)


def log_bf_table(trials: int) -> list[Decimal]:
    """ln BF_n(k) for k = 0..n via the exact ratio (2k+1)/(2(n-k)-1)."""
    n = trials
    values = [dln(kt_bayes_factor(0, n))]
    for k in range(n):
        values.append(values[-1] + dln(Fraction(2 * k + 1, 2 * (n - k) - 1)))
    return values


def binomial_weights(trials: int, q: Fraction) -> list[Decimal]:
    n, q = trials, Fraction(q)
    if q == 0 or q == 1:
        return [Decimal(1 if (k == 0) == (q == 0) else 0) for k in range(n + 1)]
    weights = [dec(1 - q) ** n]
    step = dec(q / (1 - q))
    for k in range(n):
        weights.append(weights[-1] * (n - k) / (k + 1) * step)
    return weights


def expected_log_bf(trials: int, q: Fraction, table=None) -> Decimal:
    table = table if table is not None else log_bf_table(trials)
    return sum((w * l for w, l in zip(binomial_weights(trials, q), table)), Decimal(0))


def kl_to_fair(q: Fraction) -> Decimal:
    return bernoulli_kl(Fraction(q), Fraction(1, 2))


def remainder(trials: int, q: Fraction, expected: Decimal) -> Decimal:
    """E_q[ln BF_n] - [n KL(q||1/2) - (1/2) ln n + (1/2) ln(2e/pi)]."""
    n = trials
    return expected - (n * kl_to_fair(q) - HALF * Decimal(n).ln() + CONST_INTERIOR)


# Power frontier quantities ------------------------------------------------


def sufficient_radius(trials: int, alpha: Fraction) -> Decimal:
    """d_n: |qhat - 1/2| >= d_n forces BF_n >= 1/alpha pathwise."""
    n = trials
    return ((dln(1 / Fraction(alpha)) + HALF * Decimal(n).ln() + LN2) / (2 * n)).sqrt()


def necessary_radius(trials: int, alpha: Fraction) -> Decimal:
    """e_n: BF_n >= 1/alpha forces |qhat - 1/2| >= e_n pathwise."""
    n = trials
    return ((dln(1 / Fraction(alpha)) + HALF * (PI * n / 2).ln()) / (4 * n)).sqrt()


def hoeffding_slack(trials: int, beta: Fraction) -> Decimal:
    return (dln(1 / Fraction(beta)) / (2 * trials)).sqrt()


def converse_radius(trials: int, alpha: Fraction, beta: Fraction) -> Decimal:
    """Any level-alpha test with power >= 1-beta at q needs |q-1/2| >= this."""
    n = trials
    alpha, beta = Fraction(alpha), Fraction(beta)
    pinsker = dec(1 - alpha - beta) / Decimal(2 * n).sqrt()
    if alpha + beta < Fraction(1, 2):
        bh = (dln(1 / (2 * (alpha + beta))) / (4 * n)).sqrt()
    else:
        bh = Decimal(0)
    return max(pinsker, bh)


def np_power_exact(trials: int, q: Fraction, alpha: Fraction) -> Fraction:
    """Exact power at q > 1/2 of the randomized Neyman-Pearson level-alpha test of 1/2 vs q."""
    n = trials
    total = 2**n
    tail = 0  # numerator of P_{1/2}(K > c)
    for c in range(n, -1, -1):
        if Fraction(tail + comb(n, c), total) > alpha:
            break
        tail += comb(n, c)
    else:
        return Fraction(1)
    gamma = (Fraction(alpha) - Fraction(tail, total)) / Fraction(comb(n, c), total)
    power = sum(
        (comb(n, j) * q**j * (1 - q) ** (n - j) for j in range(c + 1, n + 1)), Fraction(0)
    )
    return power + gamma * comb(n, c) * q**c * (1 - q) ** (n - c)


# Large-n (beacon scale) helpers ----------------------------------------------


def centered_log_bf(trials: int, half_width: int) -> dict[int, Decimal]:
    """ln BF_n(m + j) for |j| <= half_width, n = 2m, from the exact centre value C(n,m)/2^n."""
    n = trials
    m = n // 2
    assert n == 2 * m
    values = {m: ln_int(comb(n, m)) - n * LN2}
    for k in range(m, m + half_width):
        values[k + 1] = values[k] + dln(Fraction(2 * k + 1, 2 * (n - k) - 1))
    for j in range(1, half_width + 1):
        values[m - j] = values[m + j]
    return values


def tail_power_dec(weights: list[Decimal], lower: int, upper: int) -> Decimal:
    """P(K <= lower) + P(K >= upper)."""
    return sum(weights[: lower + 1], Decimal(0)) + sum(weights[upper:], Decimal(0))


def np_threshold_large(trials: int, alpha: Fraction) -> tuple[int, Fraction]:
    """Smallest c with P_{1/2}(K >= c) <= alpha, and the exact randomization gamma at c-1."""
    n = trials
    total = 2**n
    tail = 0
    term = 1  # comb(n, n)
    c = n
    while True:
        if (tail + term) * alpha.denominator > alpha.numerator * total:
            break
        tail += term
        term = term * c // (n - c + 1)  # comb(n, c-1)
        c -= 1
    # now tail = numerator of P(K >= c + 1); P(K >= c) > alpha
    gamma = (alpha * total - tail) / Fraction(term)
    return c + 1, gamma  # reject K >= c+1, randomize gamma at K = c


# ---------------------------------------------------------------------------
# Part II: persistent latent mixtures with a shared kernel
# ---------------------------------------------------------------------------


def count_vectors(length: int, alphabet: int):
    if alphabet == 1:
        yield (length,)
        return
    for first in range(length + 1):
        for rest in count_vectors(length - first, alphabet - 1):
            yield (first,) + rest


def multinomial(counts) -> int:
    total, out = 0, 1
    for c in counts:
        total += c
        out *= comb(total, c)
    return out


def sequence_probability(row, counts) -> Fraction:
    out = Fraction(1)
    for p, c in zip(row, counts):
        if c:
            out *= Fraction(p) ** c
    return out


def persistent_audit(a, b, rows_a, rows_b, length: int) -> dict:
    """Exact-law audit of a length-T conditionally IID transcript from one latent draw.

    rows_a[m] (rows_b[m]) is the emission law of component m under hypothesis a (b).
    Returns transcript KL, the direct posterior-gap expectation (shared kernel only),
    the exact MAP error under a, and bound ingredients.
    """
    a = [Fraction(x) for x in a]
    b = [Fraction(x) for x in b]
    shared = rows_a == rows_b
    kl_t = Decimal(0)
    gap = Decimal(0)
    map_error = Fraction(0)
    infinite = False
    gap_infinite = False
    for counts in count_vectors(length, len(rows_a[0])):
        mult = multinomial(counts)
        ka = [sequence_probability(r, counts) for r in rows_a]
        kb = [sequence_probability(r, counts) for r in rows_b]
        joint_a = [am * k for am, k in zip(a, ka)]
        joint_b = [bm * k for bm, k in zip(b, kb)]
        pa, pb = sum(joint_a), sum(joint_b)
        if pa == 0:
            continue
        if pb == 0:
            infinite = True
            continue
        kl_t += mult * xlnx_ratio(pa, pb)
        map_error += mult * (pa - max(joint_a))
        if shared:
            post_a = [x / pa for x in joint_a]
            post_b = [x / pb for x in joint_b]
            inner = Decimal(0)
            for x, y in zip(post_a, post_b):
                if x and not y:
                    gap_infinite = True
                elif x:
                    inner += xlnx_ratio(x, y)
            gap += mult * dec(pa) * inner
    return {
        "kl_t": None if infinite else kl_t,
        "gap_direct": (None if gap_infinite else gap) if shared else None,
        "map_error": map_error,
    }


def gap_bound(a, b, rows, length: int, map_error: Fraction) -> tuple[Decimal, Decimal]:
    """Return ((R-1) P_a(MAP err) + mismatch term, Bhattacharyya-only version)."""
    a = [Fraction(x) for x in a]
    b = [Fraction(x) for x in b]
    support = [m for m, x in enumerate(a) if x > 0]
    extra = [m for m, x in enumerate(a) if x == 0 and b[m] > 0]
    ratios = [a[m] / b[m] for m in support]
    big_r = max(ratios) / min(ratios)

    def rho(m1, m2):
        return sum((dec(Fraction(p1 * p2)).sqrt() for p1, p2 in zip(rows[m1], rows[m2])), Decimal(0))

    mismatch = Decimal(0)
    for m in support:
        for mm in extra:
            mismatch += 2 * dec(a[m]) * dec(b[mm] / b[m]).sqrt() * rho(m, mm) ** length
    bhatt = Decimal(0)
    for i, m1 in enumerate(support):
        for m2 in support[i + 1 :]:
            bhatt += dec(a[m1] * a[m2]).sqrt() * rho(m1, m2) ** length
    first = dec(big_r - 1) * dec(map_error) + mismatch
    second = dec(big_r - 1) * bhatt + mismatch
    return first, second


ONLY_IF_COUNTEREXAMPLES = (
    (
        "a = (1/4,1/4,1/2), b = (1/8,1/8,3/4), laws (1/2,1/2,0), (1/2,1/2,0), (0,0,1)",
        (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
        (Fraction(1, 8), Fraction(1, 8), Fraction(3, 4)),
        (
            (Fraction(1, 2), Fraction(1, 2), Fraction(0)),
            (Fraction(1, 2), Fraction(1, 2), Fraction(0)),
            (Fraction(0), Fraction(0), Fraction(1)),
        ),
        (1, 3, 6),
    ),
    (
        "deterministic theta = (0,1,1), a = (1/2,1/4,1/4), b = (1/4,3/8,3/8)",
        (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
        (Fraction(1, 4), Fraction(3, 8), Fraction(3, 8)),
        ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)), (Fraction(0), Fraction(1))),
        (1, 4),
    ),
)


def jeffreys_vs_uniform_kl(trials: int) -> Decimal:
    """KL between the Jeffreys-mixture and uniform-mixture laws of n Bernoulli bits."""
    n = trials
    total = Decimal(0)
    for k in range(n + 1):
        pa = comb(n, k) * kt_bayes_factor(k, n) / 2**n  # law of the count under Jeffreys
        pb = Fraction(1, n + 1)
        total += xlnx_ratio(pa, pb)
    return total


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------


def fmt(x, digits=6):
    if x is None:
        return "inf"
    return f"{float(x):.{digits}f}"


def part_one(lines: list[str], record: dict) -> None:
    lines.append("== Part I: fresh draws (KT composite Bayes factor vs fair bits) ==")

    # A1 pathwise: exact sequential KT product equals the closed form.
    for n in range(1, 13):
        for bits in itertools.product((0, 1), repeat=n):
            assert kt_sequential_bayes_factor(bits) == kt_bayes_factor(sum(bits), n)
    lines.append("A1 closed form BF_n(k) = C(2k,k)C(2n-2k,n-k)/(2^n C(n,k)) matches the sequential KT product on all 8190 sequences with 1 <= n <= 12")

    # A1 pathwise regret sandwich on every count vector n <= 128.
    worst_upper = Decimal(10)
    worst_lower = Decimal(10)
    for n in range(1, 129):
        for k in range(n + 1):
            ratio = kt_regret_ratio(k, n)
            assert ratio * ratio <= 4 * n  # regret <= (1/2) ln n + ln 2, exact
            regret = dln(ratio)
            lower_gap = regret - HALF * (PI * n / 2).ln()
            assert lower_gap > TOL
            worst_lower = min(worst_lower, lower_gap)
            worst_upper = min(worst_upper, HALF * Decimal(n).ln() + LN2 - regret)
    lines.append(
        "A1 pathwise regret: (1/2) ln(pi n/2) < ln[max_q P_q / P_KT] <= (1/2) ln n + ln 2 on all count vectors, 1 <= n <= 128"
        f" (upper exact rational; min lower margin {fmt(worst_lower, 8)}, min upper margin {fmt(worst_upper, 8)})"
    )
    record["A1_min_lower_margin"] = fmt(worst_lower, 10)

    # chi-square identity E_q[n chi^2(qhat||q)] = 1, exact.
    grid = [Fraction(1, 10), Fraction(1, 5), Fraction(1, 4), Fraction(1, 3), Fraction(2, 5), Fraction(1, 2)]
    for n in range(1, 41):
        for q in grid + [Fraction(7, 9)]:
            s = sum(
                (comb(n, k) * q**k * (1 - q) ** (n - k) * n * (Fraction(k, n) - q) ** 2 / (q * (1 - q)) for k in range(n + 1)),
                Fraction(0),
            )
            assert s == 1
    lines.append("A1 identity E_q[n chi^2(qhat || q)] = 1 holds exactly (Fractions) for 1 <= n <= 40 and 7 rational q")

    # A2 remainder table and non-asymptotic sandwich.
    ns = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 5000]
    lines.append("A2 remainder r_n(q) = E_q[ln BF_n] - [n KL(q||1/2) - (1/2) ln n + (1/2) ln(2e/pi)]   ((1/2) ln(2e/pi) = " + fmt(CONST_INTERIOR, 6) + ")")
    lines.append("     n " + "".join(f"{str(q):>12}" for q in grid) + "     q=0 (vs -(1/2)ln pi)")
    table_record = {}
    upper_const = 1 - REGRET_LOW
    for n in ns:
        table = log_bf_table(n)
        row = []
        for q in grid:
            e = expected_log_bf(n, q, table)
            base = n * kl_to_fair(q) - HALF * Decimal(n).ln()
            # Non-asymptotic sandwich.
            assert e - (base - LN2) > TOL
            assert (base + upper_const) - e > TOL
            assert n * kl_to_fair(q) - e > -TOL  # redundancy R_n(q) >= 0 (= 0 only at n = 1, q = 1/2)
            r = remainder(n, q, e)
            row.append(r)
            table_record[f"{n}:{q}"] = fmt(r, 8)
        boundary = table[0] - (n * LN2 - HALF * Decimal(n).ln() + CONST_BOUNDARY)
        lines.append(f"{n:>6} " + "".join(f"{float(r):>12.6f}" for r in row) + f"{float(boundary):>14.6f}")
    record["A2_remainder"] = table_record
    scaled = []
    for q in grid[:-1]:
        r_hi = remainder(5000, q, expected_log_bf(5000, q))
        r_lo = remainder(2048, q, expected_log_bf(2048, q))
        conj = (1 - 2 * q) ** 2 / (24 * q * (1 - q))
        scaled.append(f"q={q}: {float(2048 * r_lo):.4f} -> {float(5000 * r_hi):.4f} (conjecture {float(conj):.4f})")
        assert r_hi > 0 and r_lo > r_hi
    lines.append("A2 n * r_n(q) from n = 2048 to n = 5000 (finite evidence of an O(1/n) remainder; not proved): " + "; ".join(scaled))
    lines.append(
        "A2 non-asymptotic sandwich n KL - (1/2) ln n - ln 2 < E_q[ln BF_n] < n KL - (1/2) ln n + 1 - (1/2) ln(pi/2) "
        f"(= +{fmt(upper_const, 4)}) and E_q[ln BF_n] < n KL hold on every table entry"
    )

    # Precision cross-check of one entry: 80-digit working precision, with the
    # constants (pi, ln 2) still the 60-digit module constants, so this is a
    # check of accumulated rounding, not an independent 80-digit recomputation.
    with localcontext(Context(prec=80, Emin=-999999, Emax=999999)):
        hi = expected_log_bf(512, Fraction(1, 3))
    lo = expected_log_bf(512, Fraction(1, 3))
    assert abs(hi - lo) < Decimal("1e-50")
    lines.append(f"A2 precision cross-check (n=512, q=1/3): 80-digit working precision (60-digit constants) agrees with 60 digits to {fmt(abs(hi-lo), 3)} (< 1e-50)")

    # Beacon scale: q = 1/2, n = 131072.
    n = 131072
    m = n // 2
    width = 4000
    logs = centered_log_bf(n, width)
    w_center = (ln_int(comb(n, m)) - n * LN2).exp()
    expected = w_center * logs[m]
    w = w_center
    for j in range(1, width + 1):
        w = w * (m - j + 1) / (m + j)
        expected += 2 * w * logs[m + j]
    # Truncation: P(|K-m| > 4000) <= 2 exp(-2*4000^2/n) < 1e-100 and |ln BF| <= n ln 2.
    predicted = -HALF * Decimal(n).ln() + CONST_INTERIOR
    # The committed NIST beacon pulses (ST-F52): n bits and k ones are
    # re-derived from the pinned pulse file, not copied from the docs.
    from .real_data import beacon_bits, load_beacon_summary

    _, pulses = load_beacon_summary()
    beacon = beacon_bits(pulses[:-1])
    assert len(beacon) == n
    observed_k = sum(beacon)
    assert observed_k == 65461
    observed = ln_int(comb(2 * observed_k, observed_k)) + ln_int(comb(2 * n - 2 * observed_k, n - observed_k)) - n * LN2 - ln_int(comb(n, observed_k))
    qhat = Fraction(observed_k, n)
    nkl_hat = n * kl_to_fair(qhat)
    assert nkl_hat - HALF * Decimal(n).ln() - LN2 < observed < nkl_hat - HALF * Decimal(n).ln() - REGRET_LOW
    lines.append(
        f"Beacon scale n = {n}, q = 1/2: exact E[ln BF_n] = {fmt(expected, 6)}; asymptotic prediction -(1/2) ln n + (1/2) ln(2e/pi) = {fmt(predicted, 6)}; "
        f"remainder = {float(expected - predicted):.3e}"
    )
    assert abs(expected - predicted) < Decimal("1e-6")
    lines.append(
        f"Beacon data k = {observed_k}: ln BF_n = {fmt(observed, 6)} (k re-derived from the pinned pulse file; ST-F52 reports -6.03); pathwise sandwich "
        f"[{fmt(nkl_hat - HALF*Decimal(n).ln() - LN2, 4)}, {fmt(nkl_hat - HALF*Decimal(n).ln() - REGRET_LOW, 4)}], n KL(qhat||1/2) = {fmt(nkl_hat, 6)}"
    )
    record["beacon_expected_log_bf_fair"] = fmt(expected, 8)
    record["beacon_observed_log_bf"] = fmt(observed, 8)

    # A3 frontier at beacon scale.
    alpha, beta = Fraction(1, 100), Fraction(1, 20)
    d = sufficient_radius(n, alpha)
    t = hoeffding_slack(n, beta)
    e_rad = necessary_radius(n, alpha)
    conv = converse_radius(n, alpha, beta)
    frontier = d + t
    assert Decimal("0.00991") < frontier < Decimal("0.00992")
    # Exact KT rejection threshold j*: reject iff |K - m| >= j*.
    threshold = dln(Fraction(100))
    j_star = next(j for j in range(width + 1) if logs[m + j] >= threshold)
    assert logs[m + j_star] - threshold > TOL and threshold - logs[m + j_star - 1] > TOL
    assert e_rad * n <= j_star <= d * n + 1
    # Exact KT-test power-0.95 frontier on the grid q = (m + i)/n.
    def kt_power(i):
        wts = binomial_weights(n, Fraction(m + i, n))
        return tail_power_dec(wts, m - j_star, m + j_star)
    lo_i, hi_i = 0, int(frontier * n) + 1
    assert kt_power(hi_i) >= Decimal("0.95")
    while hi_i - lo_i > 1:
        mid = (lo_i + hi_i) // 2
        if kt_power(mid) >= Decimal("0.95"):
            hi_i = mid
        else:
            lo_i = mid
    kt_lo, kt_hi = kt_power(lo_i), kt_power(hi_i)
    assert kt_lo < Decimal("0.95") - TOL and kt_hi > Decimal("0.95") + TOL
    # Exact one-sided randomized Neyman-Pearson frontier (optimal for each simple alternative).
    c_np, gamma = np_threshold_large(n, alpha)
    def np_power(i):
        wts = binomial_weights(n, Fraction(m + i, n))
        return sum(wts[c_np:], Decimal(0)) + dec(gamma) * wts[c_np - 1]
    lo_np, hi_np = 0, hi_i
    assert np_power(hi_np) >= Decimal("0.95")
    while hi_np - lo_np > 1:
        mid = (lo_np + hi_np) // 2
        if np_power(mid) >= Decimal("0.95"):
            hi_np = mid
        else:
            lo_np = mid
    np_lo, np_hi = np_power(lo_np), np_power(hi_np)
    assert np_lo < Decimal("0.95") - TOL and np_hi > Decimal("0.95") + TOL
    assert conv * n <= hi_np and hi_np <= hi_i and hi_i <= frontier * n + 1
    lines.append(f"A3 beacon power frontier (alpha = 1/100, beta = 1/20, n = {n}):")
    lines.append(f"    converse (Bretagnolle-Huber/Pinsker): no level-alpha test has power 0.95 at |q-1/2| < {fmt(conv, 6)}")
    lines.append(f"    exact optimal one-sided NP test reaches power 0.95 between {lo_np}/n = {fmt(Fraction(lo_np, n), 6)} (power {fmt(np_lo, 4)}) and {hi_np}/n = {fmt(Fraction(hi_np, n), 6)} (power {fmt(np_hi, 4)})")
    lines.append(f"    exact KT test (reject iff |k - n/2| >= {j_star}, i.e. |qhat-1/2| >= {fmt(Fraction(j_star, n), 6)}; pathwise e_n = {fmt(e_rad, 6)}, d_n = {fmt(d, 6)})")
    lines.append(f"    reaches power 0.95 between {lo_i}/n = {fmt(Fraction(lo_i, n), 6)} (power {fmt(kt_lo, 4)}) and {hi_i}/n = {fmt(Fraction(hi_i, n), 6)} (power {fmt(kt_hi, 4)})")
    lines.append(f"    sufficient closed-form frontier d_n + sqrt(ln(1/beta)/(2n)) = {fmt(d, 6)} + {fmt(t, 6)} = {fmt(frontier, 6)}")
    record["beacon_frontier"] = {
        "converse": fmt(conv, 8),
        "np_interval": [lo_np, hi_np],
        "kt_threshold_j": j_star,
        "kt_interval": [lo_i, hi_i],
        "closed_form": fmt(frontier, 8),
    }

    # Small-n exact power and converse checks.
    for n_small, a_s, b_s in [(32, Fraction(1, 10), Fraction(1, 10)), (64, Fraction(1, 10), Fraction(1, 10)), (128, Fraction(1, 20), Fraction(1, 10)), (256, Fraction(1, 100), Fraction(1, 20))]:
        d_s = sufficient_radius(n_small, a_s)
        e_s = necessary_radius(n_small, a_s)
        t_s = hoeffding_slack(n_small, b_s)
        reject = [kt_bayes_factor(k, n_small) * a_s >= 1 for k in range(n_small + 1)]
        for k in range(n_small + 1):
            dev = abs(dec(Fraction(k, n_small) - Fraction(1, 2)))
            if dev - d_s > TOL:
                assert reject[k]
            if reject[k]:
                assert dev - e_s > -TOL
        checked = 0
        for i in range(n_small + 1):
            q = Fraction(i, n_small)
            if abs(dec(q - Fraction(1, 2))) - (d_s + t_s) > TOL:
                power = sum((comb(n_small, k) * q**k * (1 - q) ** (n_small - k) for k in range(n_small + 1) if reject[k]), Fraction(0))
                assert power >= 1 - b_s
                checked += 1
        conv_s = converse_radius(n_small, a_s, b_s)
        conv_checked = 0
        for i in range(n_small // 2 + 1, n_small + 1):
            q = Fraction(i, n_small)
            if np_power_exact(n_small, q, a_s) >= 1 - b_s:
                assert dec(q - Fraction(1, 2)) - conv_s > -TOL
                conv_checked += 1
        lines.append(
            f"A3 n = {n_small}, alpha = {a_s}, beta = {b_s}: pathwise d_n/e_n region checks pass on all k; exact KT power >= 1-beta at all {checked} grid q beyond d_n + t_n; "
            f"converse verified against the exact NP power at {conv_checked} grid q"
        )

    # BSC coarsening (extends ST-M83).
    lines.append("A3/M83 coarsening: observed bits are IID Bernoulli(f + (1-2f) q); the frontier in q scales by 1/(1-2f)")
    for f in [Fraction(0), Fraction(1, 10), Fraction(1, 4), Fraction(2, 5)]:
        lines.append(f"    f = {str(f):>4}: closed-form frontier {fmt(frontier / dec(1 - 2 * f), 6)}, converse {fmt(conv / dec(1 - 2 * f), 6)}")
    # Boundary source made interior: q = 0 through f = 1/10 is Bernoulli(1/10), already in the A2 table.
    lines.append("    f > 0 maps q in {0,1} into the interior, so the interior constant (1/2) ln(2e/pi) applies (A2 table column q = 1/10 is q = 0 seen through f = 1/10)")


def part_two(lines: list[str], record: dict) -> None:
    lines.append("")
    lines.append("== Part II: one persistent latent draw ==")
    third = Fraction(1, 3)

    examples = [
        ("binary latent, theta = (1/3, 2/3), a = (3/4,1/4), b = (1/4,3/4)",
         [Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 4), Fraction(3, 4)],
         [[1 - third, third], [third, 1 - third]], [1, 2, 4, 8, 16, 32, 64]),
        ("ternary latent, theta = (1/4, 1/2, 3/4), a = (1/2,1/3,1/6), b = (1/6,1/3,1/2)",
         [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)], [Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)],
         [[Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 4), Fraction(3, 4)]], [1, 2, 4, 8, 16, 32, 64]),
        ("support mismatch, theta = (1/4, 1/2, 3/4), a = (1/2,1/2,0), b = (1/3,1/3,1/3)",
         [Fraction(1, 2), Fraction(1, 2), Fraction(0)], [third, third, third],
         [[Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 4), Fraction(3, 4)]], [1, 2, 4, 8, 16, 32, 64]),
        ("ternary emissions, rows (1/2,1/4,1/4), (1/4,1/4,1/2), a = (2/3,1/3), b = (1/3,2/3)",
         [Fraction(2, 3), Fraction(1, 3)], [Fraction(1, 3), Fraction(2, 3)],
         [[Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)], [Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)]], [1, 2, 4, 8, 16, 32]),
        ("non-identifying, theta = (1/4, 1/4, 3/4), a = (1/2,1/3,1/6), b = (1/6,1/3,1/2)",
         [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)], [Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)],
         [[Fraction(3, 4), Fraction(1, 4)], [Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 4), Fraction(3, 4)]], [1, 4, 16, 64]),
    ]
    record["part_two"] = {}
    for name, a, b, rows, lengths in examples:
        cap = kl_vector(a, b)
        lines.append(f"B1/B2 {name}: KL(a||b) = {fmt(cap, 6)}")
        previous = Decimal(-1)
        entry = {}
        for length in lengths:
            audit = persistent_audit(a, b, rows, rows, length)
            kl_t = audit["kl_t"]
            gap = cap - kl_t
            assert kl_t - previous > -TOL  # nondecreasing in T
            assert cap - kl_t > -TOL  # B1 ceiling
            assert abs(gap - audit["gap_direct"]) < TOL  # B2 identity
            bound, bhatt = gap_bound(a, b, rows, length, audit["map_error"])
            assert bound - gap > -TOL and bhatt - bound > -TOL  # B2 gap bound, then its Bhattacharyya relaxation
            previous = kl_t
            entry[length] = fmt(kl_t, 8)
            lines.append(
                f"    T = {length:>2}: KL_T = {fmt(kl_t, 6)}, gap = {fmt(gap, 6)} (direct E_a KL(post) agrees), "
                f"P_a(MAP err) = {fmt(audit['map_error'], 6)}, bound = {fmt(bound, 6)}, Bhattacharyya bound = {fmt(bhatt, 6)}"
            )
        record["part_two"][name] = entry

    # Non-identifying limit: gap converges to E over the merged classes, not to zero.
    a = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
    b = [Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)]
    merged_a, merged_b = [a[0] + a[1], a[2]], [b[0] + b[1], b[2]]
    # The best possible transcript reveals only the class {1,2} vs {3}.
    limit_kl = kl_vector(merged_a, merged_b)
    lines.append(
        f"B2 non-identifying example: KL_T increases to at most KL(merged a || merged b) = {fmt(limit_kl, 6)} < KL(a||b) = {fmt(kl_vector(a, b), 6)}; "
        "the gap stays >= KL(a||b) - KL(merged) = " + fmt(kl_vector(a, b) - limit_kl, 6) + " > 0 for every T, so 'gap -> 0' needs distinguishable component laws (this is not a counterexample to the zero-gap condition)"
    )
    for length in [16, 64]:
        audit = persistent_audit(a, b, examples[4][3], examples[4][3], length)
        assert limit_kl - audit["kl_t"] > -TOL

    # Genuine counterexamples to "gap = 0 only if M is a function of Y":
    # the gap is exactly zero while M is not a function of Y.
    for name, a3, b3, rows3, lengths3 in ONLY_IF_COUNTEREXAMPLES:
        cap3 = kl_vector(a3, b3)
        for length in lengths3:
            audit = persistent_audit(a3, b3, rows3, rows3, length)
            assert abs(cap3 - audit["kl_t"]) < TOL and abs(audit["gap_direct"]) < TOL
        lines.append(
            f"B2 'only if' counterexample ({name}): KL_T = KL(a||b) = {fmt(cap3, 6)} for T in {list(lengths3)}, so the gap is 0, "
            "yet M is not a function of Y (two components with equal ratio a_m/b_m share one law)"
        )

    # Infinite-cap counterexample to 'both sides infinite together'.
    a2, b2 = [Fraction(1, 2), Fraction(1, 2)], [Fraction(1), Fraction(0)]
    same = [[Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 2), Fraction(1, 2)]]
    audit = persistent_audit(a2, b2, same, same, 8)
    assert kl_vector(a2, b2) is None and audit["kl_t"] == 0
    lines.append("B1 counterexample: a = (1/2,1/2), b = (1,0), identical component laws: KL(a||b) = +inf but KL_T = 0 for all T (the infinities need not coincide)")
    diff = [[1 - third, third], [third, 1 - third]]
    growth = [persistent_audit(a2, b2, diff, diff, length)["kl_t"] for length in (4, 16, 64)]
    assert growth[0] < growth[1] < growth[2]
    lines.append(
        "B1 no-domination growth: same a, b with theta = (1/3,2/3): KL_T = "
        + ", ".join(fmt(g, 4) for g in growth)
        + " at T = 4, 16, 64 (unbounded because a is not << b; this is the Part I mechanism)"
    )

    # N independent world draws: additivity.
    a, b, rows = examples[0][1], examples[0][2], examples[0][3]
    one = persistent_audit(a, b, rows, rows, 3)["kl_t"]
    two = Decimal(0)
    laws = []
    for counts in count_vectors(3, 2):
        mult = multinomial(counts)
        pa = sum(am * sequence_probability(r, counts) for am, r in zip(a, rows))
        pb = sum(bm * sequence_probability(r, counts) for bm, r in zip(b, rows))
        laws.append((mult, pa, pb))
    for (m1, pa1, pb1), (m2, pa2, pb2) in itertools.product(laws, laws):
        two += m1 * m2 * xlnx_ratio(pa1 * pa2, pb1 * pb2)
    assert abs(two - 2 * one) < TOL and 2 * kl_vector(a, b) - two > -TOL
    lines.append(f"B1 two independent world draws (T = 3 each): KL = {fmt(two, 6)} = 2 x {fmt(one, 6)} <= 2 KL(a||b) = {fmt(2*kl_vector(a, b), 6)}")

    # B3: different component kernels.
    rows_a = [[1 - third, third], [third, 1 - third]]
    rows_b = [[Fraction(3, 5), Fraction(2, 5)], [Fraction(2, 5), Fraction(3, 5)]]
    a, b = examples[0][1], examples[0][2]
    within = sum((dec(am) * bernoulli_kl(ra[1], rb[1]) for am, ra, rb in zip(a, rows_a, rows_b)), Decimal(0))
    cap = kl_vector(a, b)
    lines.append(f"B3 component kernels differ (theta^a = (1/3,2/3), theta^b = (2/5,3/5)); per-step within-component KL = {fmt(within, 6)}")
    beyond = None
    for length in [1, 4, 16, 64, 256]:
        kl_t = persistent_audit(a, b, rows_a, rows_b, length)["kl_t"]
        bound = cap + length * within
        assert bound - kl_t > -TOL
        if beyond is None and kl_t > cap:
            beyond = length
        lines.append(f"    T = {length:>3}: KL_T = {fmt(kl_t, 6)} <= KL(a||b) + T * within = {fmt(bound, 6)}")
    assert beyond is not None
    lines.append(f"    KL_T first exceeds the world-level cap KL(a||b) = {fmt(cap, 6)} at T = {beyond} in this list")

    # Continuous latent: Jeffreys versus uniform prior on the bias.
    cap_cont = (Decimal(4) / PI).ln()
    previous = Decimal(-1)
    values = []
    for n in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
        v = jeffreys_vs_uniform_kl(n)
        assert v - previous > -TOL and cap_cont - v > TOL
        previous = v
        values.append((n, v))
    lines.append(
        "B1 continuous latent bias (a = Beta(1/2,1/2), b = Beta(1,1)), cap ln(4/pi) = " + fmt(cap_cont, 6) + ": KL_n = "
        + ", ".join(f"{fmt(v, 4)} (n={n})" for n, v in values)
    )
    record["jeffreys_uniform"] = {str(n): fmt(v, 8) for n, v in values}


def receipt_lines() -> list[str]:
    lines: list[str] = []
    record: dict = {}
    with localcontext(CONTEXT):
        lines.append("evidence-scaling-dichotomy check")
        lines.append(f"Decimal precision {PREC}, assertion margin {TOL}")
        part_one(lines, record)
        part_two(lines, record)
    digest = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    lines.append("")
    lines.append(f"ALL CHECKS PASSED; record sha256 = {digest}")
    return lines


def receipt_text() -> str:
    return "\n".join(receipt_lines()) + "\n"


def main() -> int:
    sys.stdout.write(receipt_text())
    return 0




if __name__ == "__main__":
    raise SystemExit(main())
