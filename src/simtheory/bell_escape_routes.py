"""Exact certificates for CHSH escape-route frontiers and an anytime-valid Delft check.

Derivation: docs/bell-escape-route-frontiers.md (claims ST-T281 to ST-T285,
ST-M85, ST-F56, ST-O03).

Standard library only. Every frontier statement is certified with Fractions or
exact arithmetic in Q(sqrt 2). Floats appear only in printed summaries and in
the logarithmic constants of the statistical-strength and sample-size
statements, which are checked with stated tolerances (1e-14 or 1e-15).

Conventions. CHSH game: settings x, y in {0, 1}, output bits a, b in {0, 1},
win iff a XOR b = x AND y. Settings are uniform unless stated otherwise.
The Delft data (loaded through simtheory.real_data with the trial digest
pinned in code) use columns (timestamp, a, b, x, y) with a, b the settings
and x, y in {-1, +1} the outcomes; a trial is a win iff (-1)^(a b) x y = +1,
which is the same game after the relabelling bit = (1 - outcome) / 2.

``python -m simtheory.bell_escape_routes`` prints the receipt committed as
receipts/bell-escape-route-frontiers.txt.
"""

from __future__ import annotations

import itertools
import random
import sys
from collections import Counter
from fractions import Fraction as Fr
from math import comb, erfc, exp, factorial, log, pi, sqrt

TAU = Fr(27, 2500000)  # 1.08e-5, the paper's setting-predictability bound
XI = Fr(3, 4) + 3 * (TAU + TAU * TAU)  # Delft local win bound
PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))
SILENT = "N"


# --------------------------------------------------------------------------- Q(sqrt 2)

class Q2:
    """Exact numbers a + b sqrt(2) with rational a, b."""

    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = Fr(a)
        self.b = Fr(b)

    @staticmethod
    def lift(v):
        return v if isinstance(v, Q2) else Q2(v, 0)

    def __add__(self, o):
        o = Q2.lift(o)
        return Q2(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __neg__(self):
        return Q2(-self.a, -self.b)

    def __sub__(self, o):
        return self + (-Q2.lift(o))

    def __rsub__(self, o):
        return Q2.lift(o) - self

    def __mul__(self, o):
        o = Q2.lift(o)
        return Q2(self.a * o.a + 2 * self.b * o.b, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = Q2.lift(o)
        norm = o.a * o.a - 2 * o.b * o.b
        if norm == 0:
            raise ZeroDivisionError
        return self * Q2(o.a / norm, -o.b / norm)

    def __eq__(self, o):
        o = Q2.lift(o)
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def sign(self) -> int:
        """Exact sign of a + b sqrt 2."""
        a, b = self.a, self.b
        if a >= 0 and b >= 0:
            return 0 if (a == 0 and b == 0) else 1
        if a <= 0 and b <= 0:
            return -1
        # opposite signs: compare a^2 with 2 b^2
        if a > 0:  # b < 0
            return 1 if a * a > 2 * b * b else (-1 if a * a < 2 * b * b else 0)
        return 1 if 2 * b * b > a * a else (-1 if 2 * b * b < a * a else 0)

    def __float__(self):
        return float(self.a) + float(self.b) * sqrt(2.0)

    def __repr__(self):
        return f"({self.a} + {self.b}*sqrt2)"


SQRT2 = Q2(0, 1)
INV_SQRT2 = Q2(0, Fr(1, 2))


# --------------------------------------------------------------------------- binary KL

def kl_bern(p: float, q: float) -> float:
    """d(p || q) in nats for Bernoulli laws."""
    out = 0.0
    if p > 0:
        out += p * log(p / q)
    if p < 1:
        out += (1 - p) * log((1 - p) / (1 - q))
    return out


# --------------------------------------------------------------------------- Theorem 1

def bet_factor(q: Fr, f: Fr, win: int) -> Fr:
    """One-trial betting factor for the null P(win | past) <= f."""
    return q / f if win else (1 - q) / (1 - f)


def bet_conditional_mean(q: Fr, f: Fr, p: Fr) -> Fr:
    return p * bet_factor(q, f, 1) + (1 - p) * bet_factor(q, f, 0)


def uniform_mixture_e_value(k: int, m: int, f: Fr) -> Fr:
    """E = (1/(1-f)) int_f^1 (q/f)^k ((1-q)/(1-f))^m dq, exactly.

    Uses int_f^1 q^k (1-q)^m dq = k! m!/(n+1)! * P(Bin(n+1, f) <= k), n = k + m,
    so with f = N/D every term is a positive integer and
    E = k! m! S / ((n+1)! N^k (D-N)^(m+1)),  S = sum_{j<=k} C(n+1,j) N^j (D-N)^(n+1-j).
    """
    if not 0 < f < 1:
        raise ValueError("f must lie in (0,1)")
    n = k + m
    N, D = f.numerator, f.denominator
    M = D - N
    s = sum(comb(n + 1, j) * N**j * M ** (n + 1 - j) for j in range(k + 1))
    return Fr(factorial(k) * factorial(m) * s, factorial(n + 1) * N**k * M ** (m + 1))


def mixture_by_antiderivative(k: int, m: int, f: Fr) -> Fr:
    """Independent route: expand (1-u)^k with u = 1-q and integrate term by term."""
    g = 1 - f
    integral = sum(Fr((-1) ** j * comb(k, j)) * g ** (m + j + 1) / (m + j + 1) for j in range(k + 1))
    return integral / (f**k * g ** (m + 1))


def crossing_probability(f: Fr, p: Fr, horizon: int, threshold: Fr) -> Fr:
    """Exact P(max_{n<=horizon} E_n(f) >= threshold) for IID Bernoulli(p) wins (lattice DP)."""
    alive = {(0, 0): Fr(1)}
    crossed = Fr(0)
    for _ in range(horizon):
        nxt = {}
        for (k, m), mass in alive.items():
            for (k2, m2), pr in (((k + 1, m), p), ((k, m + 1), 1 - p)):
                if pr == 0:
                    continue
                if uniform_mixture_e_value(k2, m2, f) >= threshold:
                    crossed += mass * pr
                else:
                    nxt[(k2, m2)] = nxt.get((k2, m2), Fr(0)) + mass * pr
        alive = nxt
    return crossed


def fixed_bet_e_value(k: int, m: int, q: Fr, f: Fr) -> Fr:
    return (q / f) ** k * ((1 - q) / (1 - f)) ** m


def constant_bet_ceiling(k: int, m: int, f: Fr) -> Fr:
    """sup over q in [f,1] of the fixed-bet e-value; bounds every mixture over [f,1]."""
    n = k + m
    if n == 0:
        return Fr(1)
    ph = Fr(k, n)
    if ph <= f:
        return Fr(1)
    return fixed_bet_e_value(k, m, ph, f)


# --------------------------------------------------------------------------- local strategies

def local_strategies():
    """All 16 deterministic local strategies as (A, B) with A[x], B[y] output bits."""
    return [(A, B) for A in itertools.product((0, 1), repeat=2) for B in itertools.product((0, 1), repeat=2)]


def local_win_count(A, B) -> int:
    return sum(1 for x, y in PAIRS if (A[x] ^ B[y]) == (x & y))


# --------------------------------------------------------------------------- Theorem 2(a)(b)(c)

def signalling_strategies(non_silent_symbols: int = 2):
    """Deterministic one-way strategies with message alphabet {N, 0, ..., s-1}.

    With the default ternary alphabet there are 2304 strategies; with four
    symbols there are 16384. Yields (cost, win) as Fractions with
    cost = P(message != N) under uniform x.
    """
    msgs = (SILENT,) + tuple(range(non_silent_symbols))
    out = []
    for A in itertools.product((0, 1), repeat=2):
        for M in itertools.product(msgs, repeat=2):
            for Bvals in itertools.product((0, 1), repeat=2 * len(msgs)):
                B = {(y, s): Bvals[2 * i + y] for i, s in enumerate(msgs) for y in (0, 1)}
                wins = sum(1 for x, y in PAIRS if (A[x] ^ B[(y, M[x])]) == (x & y))
                cost = Fr(sum(1 for x in (0, 1) if M[x] != SILENT), 2)
                out.append((cost, Fr(wins, 4)))
    return out


def flag_strategies():
    """Deterministic strategies whose send flag F is fixed independently of x.

    F = 0: Bob sees silence (16 local strategies, cost 0).
    F = 1: Alice always sends one bit M(x) (4 * 4 * 16 = 256 strategies, cost 1).
    """
    out = []
    for A, B in local_strategies():
        out.append((Fr(0), Fr(local_win_count(A, B), 4)))
    for A in itertools.product((0, 1), repeat=2):
        for M in itertools.product((0, 1), repeat=2):
            for Bvals in itertools.product((0, 1), repeat=4):
                wins = sum(1 for x, y in PAIRS if (A[x] ^ Bvals[2 * M[x] + y]) == (x & y))
                out.append((Fr(1), Fr(wins, 4)))
    return out


def upper_concave_hull(points):
    """Vertices of the upper concave hull of finitely many (cost, win) points."""
    best = {}
    for c, w in points:
        if c not in best or w > best[c]:
            best[c] = w
    pts = sorted(best.items())
    hull = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            # drop hull[-1] if it lies on or below the chord from hull[-2] to p
            if (y2 - y1) * (p[0] - x1) <= (p[1] - y1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def check_dual_inequality(points, slope: Fr, intercept: Fr) -> bool:
    return all(w <= intercept + slope * c for c, w in points)


# --------------------------------------------------------------------------- Theorem 2(d)

def losing_pairs(A, B):
    return [(x, y) for x, y in PAIRS if (A[x] ^ B[y]) != (x & y)]


def measurement_dependence_model(l: Fr):
    """Symmetrized attaining model: four strategies, each losing exactly one pair.

    Strategy s_j loses only on pair j; given s_j the settings law puts l on pair j
    and (1-l)/3 on each other pair. lambda is uniform over the four strategies.
    Returns (joint law over (strategy, pair), list of strategies).
    """
    chosen = []
    for target in PAIRS:
        for A, B in local_strategies():
            if losing_pairs(A, B) == [target]:
                chosen.append((A, B))
                break
    joint = {}
    for j, (A, B) in enumerate(chosen):
        for pair in PAIRS:
            joint[(j, pair)] = Fr(1, 4) * (l if pair == PAIRS[j] else (1 - l) / 3)
    return joint, chosen


# --------------------------------------------------------------------------- Theorem 2(e)

OUT3 = ("+", "-", "0")  # "0" = no click


def detection_behaviour(eta: Q2):
    """Maximal-entanglement CHSH law with independent detection efficiency eta on each side.

    E_xy = s_xy / sqrt 2 with s = (+,+,+,-); marginals uniform on clicks.
    """
    E = {(0, 0): INV_SQRT2, (0, 1): INV_SQRT2, (1, 0): INV_SQRT2, (1, 1): -INV_SQRT2}
    val = {"+": 1, "-": -1}
    P = {}
    for x, y in PAIRS:
        for a in OUT3:
            for b in OUT3:
                if a != "0" and b != "0":
                    P[(x, y, a, b)] = eta * eta * (1 + val[a] * val[b] * E[(x, y)]) / 4
                elif a != "0" or b != "0":
                    P[(x, y, a, b)] = eta * (1 - eta) / 2
                else:
                    P[(x, y, a, b)] = (1 - eta) * (1 - eta)
    return P


ETA_STAR = Q2(-2, 2)  # 2/(1+sqrt2) = 2 sqrt2 - 2

# Support of the local model at eta*, found by a simplex solve and then fixed here;
# weights are closed-form elements of Q(sqrt 2). Strategy = (A(0), A(1)), (B(0), B(1)).
_W_FULL = ETA_STAR * ETA_STAR * Q2(2, -1) / 8  # eta^2 (2 - sqrt2)/8
_W_HALF = ETA_STAR * (1 - ETA_STAR) / 2  # eta (1-eta)/2
_W_NONE = (1 - ETA_STAR) * (1 - ETA_STAR)
DETECTION_MODEL = [
    (("+", "+"), ("+", "+"), _W_FULL), (("+", "+"), ("+", "-"), _W_FULL),
    (("+", "-"), ("+", "+"), _W_FULL), (("+", "-"), ("-", "+"), _W_FULL),
    (("-", "+"), ("+", "-"), _W_FULL), (("-", "+"), ("-", "-"), _W_FULL),
    (("-", "-"), ("-", "+"), _W_FULL), (("-", "-"), ("-", "-"), _W_FULL),
    (("+", "+"), ("+", "0"), _W_HALF), (("+", "-"), ("0", "+"), _W_HALF),
    (("+", "0"), ("+", "+"), _W_HALF), (("-", "+"), ("0", "-"), _W_HALF),
    (("-", "-"), ("-", "0"), _W_HALF), (("-", "0"), ("-", "-"), _W_HALF),
    (("0", "+"), ("+", "-"), _W_HALF), (("0", "-"), ("-", "+"), _W_HALF),
    (("0", "0"), ("0", "0"), _W_NONE),
]


def model_behaviour(model):
    P = {}
    for x, y in PAIRS:
        for a in OUT3:
            for b in OUT3:
                P[(x, y, a, b)] = Q2(0)
    for A, B, w in model:
        for x, y in PAIRS:
            P[(x, y, A[x], B[y])] = P[(x, y, A[x], B[y])] + w
    return P


def ch_value_deterministic(A, B) -> int:
    """CH functional P(++|00)+P(++|01)+P(++|10)-P(++|11)-P_A(+|0)-P_B(+|0) on a deterministic strategy."""
    pp = lambda x, y: 1 if (A[x] == "+" and B[y] == "+") else 0
    return pp(0, 0) + pp(0, 1) + pp(1, 0) - pp(1, 1) - (A[0] == "+") - (B[0] == "+")


def ch_value_behaviour(P) -> Q2:
    pp = lambda x, y: P[(x, y, "+", "+")]
    pa = sum((P[(0, 0, "+", b)] for b in OUT3), Q2(0))
    pb = sum((P[(0, 0, a, "+")] for a in OUT3), Q2(0))
    return pp(0, 0) + pp(0, 1) + pp(1, 0) - pp(1, 1) - pa - pb


# --------------------------------------------------------------------------- Theorem 3

def isotropic_box(e_abs: float):
    """Uniform-setting joint law on (x,y,a,b) with P(win|xy) = (1+e_abs)/2, uniform within win/loss."""
    w = (1 + e_abs) / 2
    P = {}
    for x, y in PAIRS:
        for a in (0, 1):
            for b in (0, 1):
                P[(x, y, a, b)] = 0.25 * ((w if (a ^ b) == (x & y) else 1 - w) / 2)
    return P


def local_mixture_law_exact(weights):
    """Exact (Fraction) uniform-setting joint law of a mixture of local strategies."""
    P = {(x, y, a, b): Fr(0) for x, y in PAIRS for a in (0, 1) for b in (0, 1)}
    for (A, B), w in zip(local_strategies(), weights):
        for x, y in PAIRS:
            P[(x, y, A[x], B[y])] += Fr(1, 4) * w
    return P


def isotropic_box_exact(win: Fr):
    """Exact uniform-setting law with P(win|xy) = win, uniform within win and loss classes."""
    return {
        (x, y, a, b): Fr(1, 4) * ((win if (a ^ b) == (x & y) else 1 - win) / 2)
        for x, y in PAIRS
        for a in (0, 1)
        for b in (0, 1)
    }


def local_mixture_law(weights):
    """Uniform-setting joint law of a mixture of the 16 deterministic local strategies."""
    P = {(x, y, a, b): 0.0 for x, y in PAIRS for a in (0, 1) for b in (0, 1)}
    for (A, B), w in zip(local_strategies(), weights):
        for x, y in PAIRS:
            P[(x, y, A[x], B[y])] += 0.25 * w
    return P


def kl_joint(P, L) -> float:
    total = 0.0
    for key, p in P.items():
        if p > 0:
            if L[key] <= 0:
                return float("inf")
            total += p * log(p / L[key])
    return total


# --------------------------------------------------------------------------- Delft

def _delft_trials():
    from .real_data import load_delft_summary

    _, trials = load_delft_summary()  # digest pinned in code (ST-F50)
    stamps = [t.timestamp for t in trials]
    if stamps != sorted(stamps):
        raise ValueError("Delft trials are not in timestamp order")
    return trials


def load_delft():
    """Win indicators of the 245 committed Delft valid trials, in timestamp order."""
    return [1 if t.chsh_win else 0 for t in _delft_trials()]


def delft_setting_counts() -> dict[tuple[int, int], int]:
    """Counts of the four setting pairs (a, b) among the Delft valid trials."""
    counts = Counter((t.a, t.b) for t in _delft_trials())
    return {pair: counts[pair] for pair in PAIRS}


def plugin_bet_running_sup(wins, f: Fr, rule: str) -> Fr:
    """Running supremum of a predictable plug-in betting e-process on the win sequence.

    Before trial i the bet is q_i = max(f, estimate) with the Laplace estimate
    (k+1)/(n+2) or the KT estimate (k+1/2)/(n+1) of the past win rate. The bet
    is predictable, so the product is a test supermartingale under H(f)
    (ST-T281). This is an exploration of adaptive bets, not a bound over them.
    """

    k = n = 0
    value = Fr(1)
    best = Fr(1)
    for w in wins:
        estimate = Fr(k + 1, n + 2) if rule == "laplace" else Fr(2 * k + 1, 2 * n + 2)
        q = max(f, min(Fr(1), estimate))
        value *= bet_factor(q, f, w)
        best = max(best, value)
        k += w
        n += 1
    return best


def chi_square_three_df_tail(statistic: float) -> float:
    """P(chi^2_3 >= statistic) = erfc(sqrt(x/2)) + sqrt(2x/pi) exp(-x/2)."""
    x = float(statistic)
    return erfc(sqrt(x / 2)) + sqrt(2 * x / pi) * exp(-x / 2)


def prefix_counts(wins):
    k = m = 0
    out = []
    for w in wins:
        k += w
        m += 1 - w
        out.append((k, m))
    return out


def running_sup(values):
    best, arg = None, None
    for i, v in enumerate(values, start=1):
        if best is None or v > best:
            best, arg = v, i
    return best, arg


# --------------------------------------------------------------------------- driver

def receipt_lines() -> tuple[list[str], bool]:
    lines = []
    ok = True

    def record(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        lines.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))

    lines.append("bell-escape-route-anytime-frontiers receipt")
    lines.append("standard library only")
    lines.append("")

    # ---- Theorem 1: betting factor is a supermartingale increment under the null
    grid = [Fr(i, 20) for i in range(1, 20)]
    t1 = True
    for f in grid:
        for q in [g for g in grid if g >= f] + [Fr(1)]:
            for p in [g for g in [Fr(0)] + grid if g <= f]:
                mean = bet_conditional_mean(q, f, p)
                # exact linear form 1 + (p - f)(q - f)/(f(1-f))
                t1 = t1 and mean == 1 + (p - f) * (q - f) / (f * (1 - f)) and mean <= 1
    record("T1 conditional mean of every bet q>=f is 1+(p-f)(q-f)/(f(1-f)) <= 1 on a 19x20x20 rational grid", t1)
    t1b = all(
        uniform_mixture_e_value(k, m, f) == mixture_by_antiderivative(k, m, f)
        for f in (Fr(3, 4), Fr(2, 3), XI)
        for k in range(0, 9)
        for m in range(0, 9)
    )
    record("T1 closed-form mixture e-value equals term-by-term antiderivative (k,m<=8; f=3/4,2/3,xi)", t1b)

    audit = crossing_probability(Fr(3, 4), Fr(3, 4), 40, Fr(4))
    record("T1 exact Ville audit: IID Bernoulli(3/4) null, horizon 40, P(sup E_n >= 4) <= 1/4",
           audit <= Fr(1, 4), f"P = {float(audit):.6f}")

    # ---- Theorem 2(a)
    sig = signalling_strategies()
    hull_a = upper_concave_hull(sig)
    record("T2a enumerated deterministic ternary-message strategies", len(sig) == 2304, f"count={len(sig)}")
    record("T2a hull vertices", hull_a == [(Fr(0), Fr(3, 4)), (Fr(1, 2), Fr(1)), (Fr(1), Fr(1))],
           str([(str(c), str(w)) for c, w in hull_a]))
    record("T2a dual certificate win <= 3/4 + c/2 holds for all 2304", check_dual_inequality(sig, Fr(1, 2), Fr(3, 4)))
    tight_a = [p for p in sig if p[1] == Fr(3, 4) + p[0] / 2]
    n0 = sum(1 for c, w in tight_a if c == 0)
    nh = sum(1 for c, w in tight_a if c == Fr(1, 2))
    record("T2a certificate tight at both vertices", n0 > 0 and nh > 0, f"tight strategies: cost0={n0}, cost1/2={nh}")

    # ---- Theorem 2(b)
    flg = flag_strategies()
    hull_b = upper_concave_hull(flg)
    record("T2b enumerated flag strategies", len(flg) == 272, f"count={len(flg)}")
    record("T2b hull vertices", hull_b == [(Fr(0), Fr(3, 4)), (Fr(1), Fr(1))])
    record("T2b dual certificate win <= 3/4 + c/4 holds for all 272", check_dual_inequality(flg, Fr(1, 4), Fr(3, 4)))
    record("T2b every flag (cost, win) point is a T2a (cost, win) point with cost in {0, 1} (a consistency check on the point sets only)",
           set(flg) <= set(sig) and all(c in (0, 1) for c, _ in flg))
    sig4 = signalling_strategies(3)
    record("T2a alphabet independence: all 16384 deterministic strategies with a 4-symbol alphabet satisfy win - c/2 <= 3/4, with equality attained",
           len(sig4) == 16384 and max(w - c / 2 for c, w in sig4) == Fr(3, 4), f"count={len(sig4)}")

    # ---- Theorem 2(c): one bit always suffices
    zero_bit = max(Fr(local_win_count(A, B), 4) for A, B in local_strategies())
    one_bit = max(w for c, w in flg if c == 1)
    record("T2c zero bits: local max win 3/4; one always-sent bit: win 1", zero_bit == Fr(3, 4) and one_bit == 1)
    # exact one-bit simulation of the Tsirelson behaviour: Alice sends x, outputs uniform a;
    # Bob samples b from P(b | a, x, y). Check the reproduced law equals the target exactly.
    target = {}
    for x, y in PAIRS:
        for a in (0, 1):
            for b in (0, 1):
                s = 1 if (x, y) != (1, 1) else -1
                corr = 1 if a == b else -1
                target[(x, y, a, b)] = (1 + corr * s * INV_SQRT2) / 4
    sim_ok = True
    for x, y in PAIRS:
        for a in (0, 1):
            pa = target[(x, y, a, 0)] + target[(x, y, a, 1)]
            sim_ok = sim_ok and pa == Q2(Fr(1, 2))  # Alice's marginal is 1/2, free of y
            for b in (0, 1):
                bob = target[(x, y, a, b)] / pa  # Bob's conditional, computable from (y, message x, shared a)
                sim_ok = sim_ok and bob.sign() >= 0 and (Q2(Fr(1, 2)) * bob) == target[(x, y, a, b)]
    record("T2c one-bit model: Alice's marginal is 1/2 free of y and Bob's conditionals are nonnegative, so sending x reproduces the Tsirelson law exactly in Q(sqrt2)", sim_ok)

    # ---- Theorem 2(d)
    every_loses = all(len(losing_pairs(A, B)) >= 1 for A, B in local_strategies())
    parity = all(sum((A[x] ^ B[y]) ^ (x & y) for x, y in PAIRS) % 2 == 1 for A, B in local_strategies())
    loss_hist = sorted(len(losing_pairs(A, B)) for A, B in local_strategies())
    record("T2d every deterministic local strategy loses >= 1 pair (odd number by parity)", every_loses and parity,
           f"loss counts={loss_hist}")
    # dual certificate: for every strategy D, multiplier 1 on the constraint mu(D, lose(D)) >= l * mu(D, .)
    # gives sum_xy mu(D,xy) win(D,xy) <= (1 - l) mu(D, .). Check the coefficient identity exactly.
    cert_ok = True
    for A, B in local_strategies():
        lp = losing_pairs(A, B)[0]
        for l in (Fr(0), Fr(1, 8), Fr(1, 4)):
            # sum_xy mu(xy) [win(xy) - (1-l)] + 1 * (mu(lp) - l sum_xy mu(xy))
            #   = sum_xy mu(xy) [win(xy) - 1 + [xy == lp]]  and every coefficient is <= 0
            for xy in PAIRS:
                win = 1 if (A[xy[0]] ^ B[xy[1]]) == (xy[0] & xy[1]) else 0
                coeff = (win - (1 - l)) + ((1 if xy == lp else 0) - l)
                cert_ok = cert_ok and coeff == win - 1 + (1 if xy == lp else 0) and coeff <= 0
    record("T2d dual certificate: per-strategy coefficients win - 1 + [xy = losing pair] are <= 0", cert_ok)
    md_ok = True
    for l in (Fr(0), Fr(1, 4)):
        joint, chosen = measurement_dependence_model(l)
        total = sum(joint.values())
        marg = {pair: sum(joint[(j, pair)] for j in range(4)) for pair in PAIRS}
        win = sum(p for (j, pair), p in joint.items()
                  if (chosen[j][0][pair[0]] ^ chosen[j][1][pair[1]]) == (pair[0] & pair[1]))
        cond_ok = all(joint[(j, pair)] / Fr(1, 4) >= l for j in range(4) for pair in PAIRS)
        md_ok = md_ok and total == 1 and all(v == Fr(1, 4) for v in marg.values()) and win == 1 - l and cond_ok
    record("T2d attaining model at l=0 and l=1/4: uniform observed settings, p(xy|lambda)>=l, win=1-l "
           "(all entries affine in l, so the interval [0,1/4] follows)", md_ok)
    tau_l = (Fr(1, 2) - TAU) ** 2
    record("T2d corollary: per-bit bias tau gives l=(1/2-tau)^2 and win <= 3/4+tau-tau^2 <= xi",
           1 - tau_l == Fr(3, 4) + TAU - TAU * TAU and 1 - tau_l <= XI, f"1-l={float(1 - tau_l):.10f}, xi={float(XI):.10f}")

    # ---- Theorem 2(e)
    record("T2e eta* = 2/(1+sqrt2) = 2 sqrt2 - 2", ETA_STAR * (1 + SQRT2) == 2)
    target_e = detection_behaviour(ETA_STAR)
    model_e = model_behaviour(DETECTION_MODEL)
    weights_ok = all(w.sign() > 0 for _, _, w in DETECTION_MODEL)
    sum_ok = sum((w for _, _, w in DETECTION_MODEL), Q2(0)) == 1
    match_ok = all(model_e[key] == target_e[key] for key in target_e)
    record("T2e explicit 17-strategy local model reproduces all 36 entries at eta* exactly in Q(sqrt2)",
           weights_ok and sum_ok and match_ok)
    det3 = [(A, B) for A in itertools.product(OUT3, repeat=2) for B in itertools.product(OUT3, repeat=2)]
    ch_max = max(ch_value_deterministic(A, B) for A, B in det3)
    record("T2e CH functional <= 0 on all 81 deterministic 3-outcome strategies", len(det3) == 81 and ch_max == 0)
    ch_formula_ok = True
    for eta in (ETA_STAR, Q2(Fr(4, 5)), Q2(Fr(17, 20)), Q2(1), Q2(Fr(9, 10))):
        val = ch_value_behaviour(detection_behaviour(eta))
        ch_formula_ok = ch_formula_ok and val == eta * eta * (1 + SQRT2) / 2 - eta
    sign_ok = (ch_value_behaviour(detection_behaviour(ETA_STAR)).sign() == 0
               and ch_value_behaviour(detection_behaviour(Q2(Fr(83, 100)))).sign() == 1
               and ch_value_behaviour(detection_behaviour(Q2(Fr(82, 100)))).sign() == -1)
    record("T2e CH value = eta^2 (1+sqrt2)/2 - eta: zero at eta*, positive at 0.83, negative at 0.82",
           ch_formula_ok and sign_ok)

    # ---- Theorem 3
    w1 = (2 + sqrt(2)) / 4
    rate_bits = kl_bern(w1, 0.75) / log(2)
    record("T3 rate at v=1 is d(cos^2(pi/8) || 3/4) = 0.0462738 bits", abs(rate_bits - 0.0462738) < 5e-8,
           f"{rate_bits:.9f} bits = {kl_bern(w1, 0.75):.9f} nats")
    # L* = uniform mixture of the 8 strategies losing exactly one pair is the isotropic local box
    opt = [s for s in local_strategies() if len(losing_pairs(*s)) == 1]
    lstar = local_mixture_law_exact([Fr(1, 8) if len(losing_pairs(*s)) == 1 else 0 for s in local_strategies()])
    iso = isotropic_box(0.5)
    record("T3 L* (uniform over the 8 one-loss strategies) is exactly (Fractions) the isotropic box with win 3/4",
           len(opt) == 8 and lstar == isotropic_box_exact(Fr(3, 4)))
    exact_ok = True
    for v in (0.75, 0.8, 0.9, 1.0):
        P = isotropic_box(v / sqrt(2))
        wv = (1 + v / sqrt(2)) / 2
        exact_ok = exact_ok and abs(kl_joint(P, iso) - kl_bern(wv, 0.75)) < 1e-14
    record("T3 D(P_v || L*) = d(w_v || 3/4) at v = 0.75, 0.8, 0.9, 1 (float, tolerance 1e-14)", exact_ok)
    rng = random.Random(20151021)
    P1 = isotropic_box(1 / sqrt(2))
    floor = kl_bern(w1, 0.75)
    worst = float("inf")
    for _ in range(3000):
        raw = [rng.random() ** rng.choice((1, 3, 8)) for _ in range(16)]
        tot = sum(raw)
        worst = min(worst, kl_joint(P1, local_mixture_law([r / tot for r in raw])))
    record("T3 random local mixtures (3000, seeded) never beat the lower bound", worst >= floor - 1e-15,
           f"min sampled D = {worst:.6f} >= {floor:.6f} nats")

    # ---- Theorem 4 consequences
    for label, p in (("Tsirelson rate", w1), ("Delft empirical rate 196/245", 0.8)):
        dn = kl_bern(p, float(XI))
        lines.append(f"     T4 expected-sample-size floor at alpha=0.05 vs xi, {label}: "
                     f"ln 20 / d = {log(20) / dn:.1f} trials (d = {dn:.6f} nats)")
    record("T4 Tsirelson-rate floor ln(20)/d(cos^2(pi/8)||xi) lies in (93, 94)",
           93 < log(20) / kl_bern(w1, float(XI)) < 94)

    # ---- Delft finite check
    wins = load_delft()
    counts = prefix_counts(wins)
    record("Delft digest (pinned in code), timestamp order, n=245, k=196", len(wins) == 245 and sum(wins) == 196)
    settings = delft_setting_counts()
    chi2 = sum((Fr(v) - Fr(245, 4)) ** 2 / Fr(245, 4) for v in settings.values())
    lines.append(
        "     context only (no inferential claim): setting counts "
        + ", ".join(f"{a}{b}:{settings[(a, b)]}" for a, b in PAIRS)
        + f"; fixed-n chi-square vs uniform = {float(chi2):.2f} on 3 df, p = {chi_square_three_df_tail(chi2):.3f}"
        + " (RNG independence is assumed through tau, not tested)"
    )
    lines.append(f"     xi = {XI} = {float(XI):.12f}")

    for f_label, f in (("3/4", Fr(3, 4)), ("xi", XI)):
        mix = [uniform_mixture_e_value(k, m, f) for k, m in counts]
        sup_mix, arg_mix = running_sup(mix)
        fixed = [fixed_bet_e_value(k, m, Fr(17, 20), f) for k, m in counts]
        sup_fix, arg_fix = running_sup(fixed)
        ceil_final = constant_bet_ceiling(196, 49, f)
        lines.append(f"     f={f_label}: uniform mixture E_245 = {float(mix[-1]):.6f}, "
                     f"sup_n E_n = {float(sup_mix):.6f} at n={arg_mix}; anytime p = {float(1 / sup_mix):.4f}")
        lines.append(f"     f={f_label}: fixed bet q=17/20 E_245 = {float(fixed[-1]):.6f}, "
                     f"sup_n = {float(sup_fix):.6f} at n={arg_fix}")
        lines.append(f"     f={f_label}: hindsight constant-bet ceiling at n=245 = {float(ceil_final):.6f} "
                     f"(log = {log(float(ceil_final)):.6f} nats)")
    mix34 = [uniform_mixture_e_value(k, m, Fr(3, 4)) for k, m in counts]
    mixxi = [uniform_mixture_e_value(k, m, XI) for k, m in counts]
    record("Delft E_245 (uniform mixture, f=xi) in [1.3669, 1.3670]", Fr(13669, 10000) <= mixxi[-1] <= Fr(1367, 1000))
    record("Delft sup_n E_n (uniform mixture, f=xi) in [2.7815, 2.7817], attained at n=6",
           Fr(27815, 10000) <= max(mixxi) <= Fr(27817, 10000) and mixxi.index(max(mixxi)) == 5)
    record("Delft E_245 (uniform mixture, f=3/4) in [1.3697, 1.3698]", Fr(13697, 10000) <= mix34[-1] <= Fr(13698, 10000))
    ceil245 = constant_bet_ceiling(196, 49, Fr(3, 4))
    record("Delft ceiling 245 d(196/245||3/4) = ln of (16/15)^196 (4/5)^49 in [1.7155, 1.7156] nats",
           Fr(5559, 1000) <= ceil245 <= Fr(5560, 1000) and abs(log(float(ceil245)) - 245 * kl_bern(0.8, 0.75)) < 1e-12,
           f"{log(float(ceil245)):.6f} nats, e^ = {float(ceil245):.4f}")
    # uniform-in-f ceiling: for every f >= 3/4 and every n <= 245, any mixture over q in [f,1]
    # has E_n(f) <= constant_bet_ceiling(k_n, m_n, 3/4)
    ceilings = [constant_bet_ceiling(k, m, Fr(3, 4)) for k, m in counts]
    cmax, carg = running_sup(ceilings)
    record("Delft: max over prefixes of the constant-bet ceiling at f=3/4 is < 20 (and < 7.78)",
           cmax < 20 and cmax < Fr(778, 100), f"{float(cmax):.6f} at n={carg}, k={counts[carg - 1][0]}")
    record("Delft: mixture e-values never exceed the ceiling (f=3/4 and xi)",
           all(e <= c for e, c in zip(mix34, ceilings))
           and all(e <= constant_bet_ceiling(k, m, XI) for e, (k, m) in zip(mixxi, counts)))
    lines.append("     => at alpha = 0.05 (threshold 20) no f >= 3/4 is rejected by any constant-bet mixture,")
    lines.append("        so the anytime-valid confidence sets are c in [0,1/2] (T2a), c in [0,1] (T2b),")
    lines.append(f"        l in [0,1/4] (T2d): trivial. They stay trivial for every alpha < 1/{float(cmax):.4f} "
                 f"= {float(1 / cmax):.4f}.")
    lines.append("     exploration only (not a bound over adaptive bets): predictable plug-in bets on the win sequence,")
    for f_label, f in (("3/4", Fr(3, 4)), ("xi", XI)):
        laplace = plugin_bet_running_sup(wins, f, "laplace")
        kt = plugin_bet_running_sup(wins, f, "kt")
        lines.append(f"       f={f_label}: running sup Laplace-rule {float(laplace):.4f}, KT-rule {float(kt):.4f} (threshold 20)")
    # anytime-valid p-value function for the default uniform mixture
    lines.append("     anytime-valid p(r) = 1/sup_n E_n(f(r)) for the default data-independent uniform mixture")
    lines.append("     (chosen after the data were public, without tuning; the negative result rests on the ceiling above):")
    for label, f in (("c=0 (a,b), l=1/4", Fr(3, 4)), ("c=1/100 (a)", Fr(3, 4) + Fr(1, 200)),
                     ("c=1/100 (b)", Fr(3, 4) + Fr(1, 400)), ("l=1/5", Fr(4, 5)), ("c=1/10 (a)", Fr(4, 5))):
        s = max(uniform_mixture_e_value(k, m, f) for k, m in counts)
        lines.append(f"       {label:18s} f={float(f):.4f}: sup E = {float(s):.4f}, p = {float(min(1, 1 / s)):.4f}")

    lines.append("")
    lines.append("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return lines, ok


def receipt_text() -> str:
    lines, _ = receipt_lines()
    return "\n".join(lines) + "\n"


def main() -> int:
    lines, ok = receipt_lines()
    sys.stdout.write("\n".join(lines) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
