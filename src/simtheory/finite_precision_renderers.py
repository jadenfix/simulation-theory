"""Finite-precision renderer identifiability: exact and bounded checks.

Derivation: docs/finite-precision-renderer-identifiability.md (claims ST-T286
to ST-T289, ST-F57, ST-O04).

Standard library only. Exact arithmetic uses fractions.Fraction and integer
arithmetic (math.isqrt). Quantities that involve sqrt(2) or logarithms are
evaluated with decimal.Decimal at 80 significant digits and are labelled
NUMERICAL in the receipt. Binomial tail probabilities for the test-error
check use double precision and are labelled NUMERICAL.

Notation (see RESULT.md):
  * one Bell trial has outcomes (a, b) in {+1,-1}^2, ordered (++, +-, -+, --);
  * the Werner law with signed correlator parameter x = v * cos(theta) is
        P_x(a, b) = (1 - a*b*x) / 4,
    so the "anti-correlator" tau := -E[AB] equals x;
  * H_D is the set of per-setting outcome laws with every probability in (1/D)Z.

Decimal work runs in a private 80-digit context; the global Decimal context
is never modified. ``python -m simtheory.finite_precision_renderers`` prints the
receipt committed as receipts/finite-precision-renderer-identifiability.txt.
"""

from __future__ import annotations

import math
import random
import sys
from decimal import Context, Decimal, localcontext
from functools import wraps
from fractions import Fraction
from itertools import product

CONTEXT = Context(prec=80)

with localcontext(CONTEXT):
    SQRT2 = Decimal(2).sqrt()
    R_INV_SQRT2 = 1 / SQRT2  # cos(pi/4)


def _precise(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        with localcontext(CONTEXT):
            return function(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------------------
# generic grid utilities
# ---------------------------------------------------------------------------

def is_grid_law(q, D):
    """True iff q is a probability vector with every entry in (1/D)Z."""
    q = [Fraction(x) for x in q]
    return (
        all(x >= 0 for x in q)
        and sum(q) == 1
        and all((x * D).denominator == 1 for x in q)
    )


def compositions(total, parts):
    """All tuples of `parts` nonnegative integers summing to `total`."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def grid_laws(K, D):
    for counts in compositions(D, K):
        yield tuple(Fraction(c, D) for c in counts)


def largest_remainder_round(p, D):
    """l1-optimal D-grid rounding of a probability vector p.

    Works for Fraction or Decimal entries. Returns integer counts k with
    sum(k) == D. Rounds up the r coordinates with the largest fractional
    parts of D*p, where r = D - sum(floor(D*p)).
    """
    scaled = [x * D for x in p]
    floors = [int(math.floor(s)) if isinstance(s, Fraction) else int(s.to_integral_value(rounding="ROUND_FLOOR")) for s in scaled]
    fracs = [s - f for s, f in zip(scaled, floors)]
    r = D - sum(floors)
    order = sorted(range(len(p)), key=lambda i: fracs[i], reverse=True)
    counts = list(floors)
    for i in order[:r]:
        counts[i] += 1
    return tuple(counts)


def l1_to_counts(p, counts, D):
    return sum(abs(x - Fraction(c, D) if isinstance(x, Fraction) else x - Decimal(c) / D) for x, c in zip(p, counts))


def brute_min_l1(p, D):
    K = len(p)
    best = None
    for counts in compositions(D, K):
        val = l1_to_counts(p, counts, D)
        if best is None or val < best:
            best = val
    return best


def werner_law(x):
    """Werner/singlet outcome law with anti-correlator x, order (++,+-,-+,--)."""
    if isinstance(x, Fraction):
        one, four = Fraction(1), Fraction(4)
    else:
        one, four = Decimal(1), Decimal(4)
    return ((one - x) / four, (one + x) / four, (one + x) / four, (one - x) / four)


# ---------------------------------------------------------------------------
# Theorem 0: dithering boundary
# ---------------------------------------------------------------------------

def systematic_dither(p, D):
    """Exact decomposition of p into <= K D-grid laws (systematic sampling).

    Returns a list of (weight, grid_law). Each component q satisfies
    |q_i - p_i| < 1/D for all i, and sum(weight * q) == p exactly.
    """
    p = [Fraction(x) for x in p]
    K = len(p)
    floors = [math.floor(x * D) for x in p]
    fracs = [x * D - f for x, f in zip(p, floors)]
    r = sum(fracs)
    assert r.denominator == 1
    r = int(r)
    if r == 0:
        return [(Fraction(1), tuple(Fraction(f, D) for f in floors))]
    cum = [Fraction(0)]
    for f in fracs:
        cum.append(cum[-1] + f)
    cuts = sorted({c - math.floor(c) for c in cum} | {Fraction(0), Fraction(1)})
    components = []
    for lo, hi in zip(cuts, cuts[1:]):
        if hi == lo:
            continue
        u = (lo + hi) / 2
        chosen = set()
        for m in range(r):
            point = u + m
            for i in range(K):
                if cum[i] <= point < cum[i + 1]:
                    chosen.add(i)
                    break
        assert len(chosen) == r
        q = tuple(Fraction(floors[i] + (1 if i in chosen else 0), D) for i in range(K))
        components.append((hi - lo, q))
    return components


def check_dither(p, D):
    comps = systematic_dither(p, D)
    K = len(p)
    mix = [sum(w * q[i] for w, q in comps) for i in range(K)]
    ok_mix = mix == [Fraction(x) for x in p]
    ok_grid = all(is_grid_law(q, D) for _, q in comps)
    ok_close = all(abs(q[i] - Fraction(p[i])) < Fraction(1, D) for _, q in comps for i in range(K))
    ok_weights = sum(w for w, _ in comps) == 1 and all(w > 0 for w, _ in comps)
    return {
        "components": len(comps),
        "mixture_exact": ok_mix,
        "all_grid": ok_grid,
        "linf_below_1_over_D": ok_close,
        "weights_valid": ok_weights,
        "max_components_le_K": len(comps) <= K,
    }


def dither_product_identity(K, D, M):
    """Set of uniform averages of M D-grid laws equals the set of DM-grid laws."""
    base = list(grid_laws(K, D))
    averages = set()

    def rec(start, depth, acc):
        if depth == M:
            averages.add(tuple(a / M for a in acc))
            return
        for idx in range(start, len(base)):
            q = base[idx]
            rec(idx, depth + 1, tuple(a + b for a, b in zip(acc, q)))

    rec(0, 0, tuple(Fraction(0) for _ in range(K)))
    fine = set(grid_laws(K, D * M))
    return averages == fine, len(averages), len(fine)


# ---------------------------------------------------------------------------
# Theorem 1: single-cosine schedules (visibility-blind)
# ---------------------------------------------------------------------------

def werner_lattice(D):
    """L_D = {x in [-1,1] : Werner law P_x is a D-grid law} (empty for odd D)."""
    if D % 2:
        return []
    return [Fraction(4 * j - D, D) for j in range(D // 2 + 1)]


def werner_lattice_bruteforce(D):
    """Same set computed from the grid condition directly over x in (1/(4D))Z."""
    out = []
    for num in range(-4 * D, 4 * D + 1):
        x = Fraction(num, 4 * D)
        if is_grid_law(werner_law(x), D):
            out.append(x)
    return out


def single_cosine_grid_points(D, c_kind, vmin, vmax):
    """x in L_D with x = v*c, v in [vmin, vmax]; c_kind in {'one', 'inv_sqrt2'}.

    Exact: for c = 1/sqrt2 the condition vmin <= sqrt2*x <= vmax with x >= 0
    is tested as vmin^2 <= 2 x^2 <= vmax^2.
    """
    vmin, vmax = Fraction(vmin), Fraction(vmax)
    pts = []
    for x in werner_lattice(D):
        if x < 0:
            continue
        if c_kind == "one":
            ok = vmin <= x <= vmax
        else:
            ok = vmin * vmin <= 2 * x * x <= vmax * vmax
        if ok:
            pts.append(x)
    return pts


def single_cosine_sufficient(D, c_kind, vmin, vmax):
    """Sufficient condition c*(vmax-vmin) >= 4/D, evaluated exactly."""
    dv = Fraction(vmax) - Fraction(vmin)
    if c_kind == "one":
        return dv * D >= 4
    return (dv * D) ** 2 >= 32


# ---------------------------------------------------------------------------
# Theorem 2: two settings with cos ratio sqrt2, unknown visibility
# ---------------------------------------------------------------------------

def segment_linf_distance(a, b, vmin, vmax, r=R_INV_SQRT2):
    """min_{v in [vmin,vmax]} max(|a - v|, |b - r v|) (Decimal)."""
    vmin, vmax = Decimal(vmin), Decimal(vmax)
    cands = {vmin, vmax, a, b / r, (a - b) / (1 - r), (a + b) / (1 + r)}
    best = None
    for v in cands:
        v = min(max(v, vmin), vmax)
        val = max(abs(a - v), abs(b - r * v))
        if best is None or val < best:
            best = val
    return best


def grid_segment_separation(D, vmin, vmax):
    """g_D: min l_inf distance from grid anti-correlator pairs (m1/D, m2/D),
    m_i = D mod 2, |m_i| <= D, to the segment {v (1, 1/sqrt2)}.

    Uses convexity in m2 for fixed m1 (distance to a convex set is convex),
    so only the parity-lattice points bracketing the continuous minimiser
    need to be examined. Returns (g_D, argmin pair).
    """
    vmin_d, vmax_d = Decimal(vmin.numerator) / vmin.denominator, Decimal(vmax.numerator) / vmax.denominator
    Dd = Decimal(D)
    best, arg = None, None
    for m1 in range(D % 2, D + 1, 2):
        a = Decimal(m1) / Dd
        targets = {a * R_INV_SQRT2 * Dd, min(max(a, vmin_d), vmax_d) * R_INV_SQRT2 * Dd}
        cand_m2 = set()
        for t in targets:
            base = int(t.to_integral_value(rounding="ROUND_FLOOR"))
            for m2 in range(base - 3, base + 4):
                if 0 <= m2 <= D and (m2 - D) % 2 == 0:
                    cand_m2.add(m2)
        for m2 in cand_m2:
            val = segment_linf_distance(a, Decimal(m2) / Dd, vmin_d, vmax_d)
            if best is None or val < best:
                best, arg = val, (m1, m2)
    return best, arg


def g_lower_bound(D, vmin):
    """Analytic lower bound min(vmin, 1/((3+2 sqrt2) D^2))."""
    return min(Decimal(vmin.numerator) / vmin.denominator, 1 / ((3 + 2 * SQRT2) * D * D))


def pell_pairs(limit):
    """(P, Q) with P^2 - 2 Q^2 = +-1, P, Q >= 1, P <= limit (exact recurrence)."""
    out = []
    P, Q = 1, 1
    while P <= limit:
        assert abs(P * P - 2 * Q * Q) == 1
        out.append((P, Q))
        P, Q = P + 2 * Q, P + Q
    return out


def pell_multiple_renderer(D, vmin, vmax):
    """Converse construction for D = 4N: returns dict with exact grid law data.

    Choose the largest Pell numerator P <= (vmax - vmin) N, k = floor(vmax N / P),
    p = kP, q = kQ, v = p/N. Setting theta=0 is matched exactly (x1 = p/N);
    setting theta=pi/4 uses x2' = q/N against x2 = p/(sqrt2 N).
    """
    assert D % 4 == 0
    N = D // 4
    vmin, vmax = Fraction(vmin), Fraction(vmax)
    cap = (vmax - vmin) * N
    pairs = [pq for pq in pell_pairs(int(cap)) if pq[0] <= cap]
    if not pairs:
        return None
    P, Q = pairs[-1]
    k = int(vmax * N // P)
    p, q = k * P, k * Q
    v = Fraction(p, N)
    x1, x2p = Fraction(p, N), Fraction(q, N)
    law1, law2 = werner_law(x1), werner_law(x2p)
    x2 = Decimal(p) / (SQRT2 * N)
    delta = abs(x2 - Decimal(q) / N)
    exact_delta = Decimal(k) / (SQRT2 * N * (P + SQRT2 * Q))
    return {
        "D": D, "N": N, "P": P, "Q": Q, "k": k, "p": p, "q": q, "v": v,
        "v_in_range": vmin <= v <= vmax,
        "P_window": Fraction(P) > cap / 3 and P <= cap,
        "grid_theta0": is_grid_law(law1, D),
        "grid_theta_pi4": is_grid_law(law2, D),
        "grid_theta_pi2": is_grid_law(werner_law(Fraction(0)), D),
        "delta": delta,
        "delta_identity_ok": abs(delta - exact_delta) < Decimal(10) ** -60,
        "delta_bound1": Decimal(vmax.numerator) / vmax.denominator / (SQRT2 * P * P),
        "delta_bound2": 9 * (Decimal(vmax.numerator) / vmax.denominator) / (SQRT2 * (Decimal(cap.numerator) / cap.denominator) ** 2),
        "x2": x2,
        "x2p": x2p,
    }


def kl_chi2_werner(x_q, x_p):
    """KL(P_{x_q} || P_{x_p}) and chi^2(P_{x_q} || P_{x_p}) for Werner-shaped laws (Decimal)."""
    q = werner_law(Decimal(x_q.numerator) / x_q.denominator if isinstance(x_q, Fraction) else x_q)
    p = werner_law(x_p)
    kl = sum((qi * (qi / pi).ln()) for qi, pi in zip(q, p) if qi > 0)
    chi2 = sum((qi - pi) ** 2 / pi for qi, pi in zip(q, p))
    return kl, chi2


# ---------------------------------------------------------------------------
# Theorem 3: known visibility v = 1, binary grids D = 2^k
# ---------------------------------------------------------------------------

def dist_to_int_pow2_sqrt2(m):
    """||2^m sqrt2|| (distance to nearest integer), exact branch decision."""
    N = 2 * 4 ** m
    a = math.isqrt(N)
    assert a * a < N < (a + 1) * (a + 1)
    root = Decimal(N).sqrt()
    if (2 * a + 1) ** 2 > 4 * N:  # sqrt(N) < a + 1/2
        return root - a, "down"
    return (a + 1) - root, "up"


def tv_pi4_formula(k):
    """min_{Q in H_{2^k}} TV(Q, P_1 at theta = pi/4) = 2^{1-k} ||2^{k-3} sqrt2||, k >= 3."""
    d, _ = dist_to_int_pow2_sqrt2(k - 3)
    return 2 * d / Decimal(2) ** k


def tv_pi4_largest_remainder(k):
    D = 2 ** k
    p = werner_law(R_INV_SQRT2)
    counts = largest_remainder_round(p, D)
    return l1_to_counts(p, counts, D) / 2


def tv_pi4_bruteforce(k):
    D = 2 ** k
    p = werner_law(R_INV_SQRT2)
    return brute_min_l1(p, D) / 2


def adapted_design_tv(D):
    """Exact min TV from H_D to P_1 at cos(theta) = 1 - 2/D (rational target)."""
    x = 1 - Fraction(2, D)
    p = werner_law(x)
    counts = largest_remainder_round(p, D)
    return l1_to_counts(p, counts, D) / 2


def _log_binom_pmf(n, r, mu):
    if mu == 0:
        return 0.0 if r == 0 else -math.inf
    return (math.lgamma(n + 1) - math.lgamma(r + 1) - math.lgamma(n - r + 1)
            + r * math.log(mu) + (n - r) * math.log1p(-mu))


def adapted_test_errors(D, eps):
    """NUMERICAL error probabilities of the rare-outcome test at c = 1 - 2/D.

    Accept P_1 iff N_{++} >= 1, N_{--} >= 1 and N_R <= 1.5 n / D, where
    N_R = N_{++} + N_{--}. Under P_1 each rare type has probability 1/(2D).
    Under any Q in H_D the acceptance probability is at most
    P(Bin(n, 2/D) <= 1.5 n / D) (types with k1 k2 = 0 are always rejected).
    """
    n = math.ceil(16 * D * math.log(3 / eps))
    T = math.floor(1.5 * n / D)
    mu = 1 / D
    # P_1 error: 1 - sum_{r<=T} Bin(n, mu)(r) * P(both types | r)
    acc = 0.0
    for r in range(0, T + 1):
        both = 0.0 if r <= 1 else 1 - 2 * 0.5 ** r
        acc += math.exp(_log_binom_pmf(n, r, mu)) * both
    err_null = 1 - acc
    worst_alt = sum(math.exp(_log_binom_pmf(n, r, 2 / D)) for r in range(0, T + 1))
    return n, T, err_null, worst_alt


def universal_rounding_bounds(trials=200, seed=12345):
    """Exact check: largest-remainder rounding has l1 <= K/(2D), and it is optimal
    (brute force) on small instances; Hellinger^2 <= l1 (Decimal)."""
    rng = random.Random(seed)
    worst_ratio = Fraction(0)
    ok_opt = True
    ok_hel = True
    for t in range(trials):
        K = 4
        D = rng.randint(1, 9)
        weights = [rng.randint(0, 50) for _ in range(K)]
        if sum(weights) == 0:
            weights[0] = 1
        tot = sum(weights)
        p = [Fraction(w, tot) for w in weights]
        counts = largest_remainder_round(p, D)
        l1 = l1_to_counts(p, counts, D)
        worst_ratio = max(worst_ratio, l1 * D / Fraction(K, 2))
        if l1 != brute_min_l1(p, D):
            ok_opt = False
        h2 = sum((Decimal(c).sqrt() / Decimal(D).sqrt() - (Decimal(x.numerator) / x.denominator).sqrt()) ** 2 for c, x in zip(counts, p))
        if h2 > Decimal(l1.numerator) / l1.denominator + Decimal(10) ** -60:
            ok_hel = False
    return worst_ratio, ok_opt, ok_hel


# ---------------------------------------------------------------------------
# phase nuisance remark
# ---------------------------------------------------------------------------

def phase_counterexample(D):
    """Schedule {0, pi/4, pi/2}, phase phi = -pi/4: anti-correlators
    v (1/sqrt2, 0, -1/sqrt2). With v/sqrt2 = 4j/D every setting law is a D-grid law."""
    assert D % 4 == 0
    hits = []
    for j in range(1, D // 4 + 1):
        x = Fraction(4 * j, D)  # = v / sqrt2, need v = sqrt2 x <= 1 -> 2 x^2 <= 1
        if 2 * x * x <= 1:
            laws = (werner_law(x), werner_law(Fraction(0)), werner_law(-x))
            hits.append((x, all(is_grid_law(l, D) for l in laws)))
    return hits


# ---------------------------------------------------------------------------
# receipt
# ---------------------------------------------------------------------------

def main(out=sys.stdout):
    w = out.write
    w("finite-precision-renderer-identifiability receipt\n")
    w("decimal precision 80\n\n")
    all_ok = True

    # Theorem 0
    w("[T0] dithering boundary (EXACT, Fractions)\n")
    targets = [
        ((Fraction(1, 3), Fraction(1, 3), Fraction(1, 6), Fraction(1, 6)), 4),
        (werner_law(Fraction(1, 3)), 8),
        (werner_law(Fraction(5, 7)), 16),
        ((Fraction(1, 10), Fraction(2, 10), Fraction(3, 10), Fraction(4, 10)), 3),
        (werner_law(Fraction(99, 140)), 1024),  # 99/140 ~ 1/sqrt2 (Pell)
    ]
    for p, D in targets:
        res = check_dither(p, D)
        ok = all(v for k, v in res.items() if k != "components")
        all_ok &= ok
        w(f"  D={D:5d} target={[str(x) for x in p]} components={res['components']} ok={ok}\n")
    for K, D, M in [(3, 2, 3), (3, 3, 2), (4, 2, 2), (2, 5, 3)]:
        eq, na, nf = dither_product_identity(K, D, M)
        all_ok &= eq
        w(f"  uniform-{M} dithering of H_{D} on K={K}: |averages|={na} |H_{D*M}|={nf} equal={eq}\n")
    w("\n")

    # Theorem 1
    w("[T1] single-cosine schedules: Werner lattice and visibility-blind grid points (EXACT)\n")
    lat_ok = all(werner_lattice(D) == werner_lattice_bruteforce(D) for D in range(1, 41))
    all_ok &= lat_ok
    w(f"  L_D formula == brute force for D=1..40: {lat_ok}; L_D empty for all odd D<=40: "
      f"{all(not werner_lattice_bruteforce(D) for D in range(1, 41, 2))}\n")
    for c_kind in ("one", "inv_sqrt2"):
        for vmin, vmax in ((Fraction(1, 2), Fraction(1)), (Fraction(9, 10), Fraction(1))):
            n_nonempty = 0
            first_guaranteed = None
            failures = []
            criterion_ok = True
            for D in range(4, 401, 2):
                pts = single_cosine_grid_points(D, c_kind, vmin, vmax)
                exact_ok = all(is_grid_law(werner_law(x), D) for x in pts)
                criterion_ok &= exact_ok
                if single_cosine_sufficient(D, c_kind, vmin, vmax):
                    if first_guaranteed is None:
                        first_guaranteed = D
                    criterion_ok &= bool(pts)
                if pts:
                    n_nonempty += 1
                elif D % 4 == 0:
                    failures.append(D)
            all_ok &= criterion_ok
            w(f"  c={c_kind:9s} v in [{vmin},{vmax}]: even D in 4..400 with P_v in H_D for some v: {n_nonempty}/199; "
              f"sufficient condition first holds at D={first_guaranteed}; sufficiency verified={criterion_ok}; "
              f"D=0 mod 4 with no such v: {failures[:12]}{'...' if len(failures) > 12 else ''}\n")
    ce = single_cosine_grid_points(4, "inv_sqrt2", Fraction(9, 10), Fraction(1))
    w(f"  counterexample to the literal sketch: D=4, c=1/sqrt2, v in [9/10,1] -> grid points {ce} (empty={not ce})\n")
    chsh = single_cosine_grid_points(32, "inv_sqrt2", Fraction(1, 2), Fraction(1))
    w(f"  CHSH schedule (|cos|=1/sqrt2), D=32: grid anti-correlators x={[str(x) for x in chsh]} -> |S|=4x={[str(4 * x) for x in chsh]}; "
      f"x=5/8 gives law {[str(t) for t in werner_law(Fraction(5, 8))]} in H_32: {is_grid_law(werner_law(Fraction(5, 8)), 32)}\n\n")

    # Theorem 2
    w("[T2] settings theta in {0, pi/4}, v in [1/2, 1] unknown\n")
    vmin, vmax = Fraction(1, 2), Fraction(1)
    int_ok = all(m1 * m1 - 2 * m2 * m2 != 0 for m1 in range(-100, 101) for m2 in range(-100, 101) if (m1, m2) != (0, 0))
    all_ok &= int_ok
    w(f"  EXACT: m1^2 - 2 m2^2 != 0 for all (m1,m2) != 0 with |m_i| <= 100: {int_ok}\n")
    w("  NUMERICAL (Decimal 80 digits): g_D = min l_inf distance from grid anti-correlator pairs to the segment\n")
    D_list = sorted(set(list(range(4, 401, 4)) + [4 * P for P, _ in pell_pairs(2500)] + [1000, 2048, 4096, 8192, 10000, 1001, 999]))
    min_ratio = None
    max_ratio = None
    lb_ok = True
    rows = []
    for D in D_list:
        g, arg = grid_segment_separation(D, vmin, vmax)
        lb = g_lower_bound(D, vmin)
        lb_ok &= g >= lb
        ratio = g * D * D
        if D >= 8:
            min_ratio = ratio if min_ratio is None else min(min_ratio, ratio)
            max_ratio = ratio if max_ratio is None else max(max_ratio, ratio)
        rows.append((D, g, arg, ratio, lb * D * D))
    all_ok &= lb_ok
    w(f"  declared D grid: {len(D_list)} values in [4, 10000]; analytic bound g_D >= min(v_min, 1/((3+2sqrt2)D^2)) holds on all: {lb_ok}\n")
    w(f"  analytic constant 1/(3+2sqrt2) = {float(1 / (3 + 2 * SQRT2)):.6f}; empirical min/max of D^2 g_D over D>=8: {float(min_ratio):.6f} / {float(max_ratio):.6f}\n")
    for D, g, arg, ratio, lbr in rows:
        if D in (4, 8, 12, 28, 68, 164, 396, 956, 2308, 5572, 1000, 1001, 999, 10000):
            w(f"    D={D:6d} argmin (m1,m2)={arg} |m1^2-2m2^2|={abs(arg[0] ** 2 - 2 * arg[1] ** 2)} D^2 g_D={float(ratio):.6f}\n")
    w("  EXACT grid membership + NUMERICAL distances for the Pell-multiple converse renderer, all D = 0 mod 4 in [8, 2000]:\n")
    conv_ok = True
    worst_d2 = Decimal(0)
    count = 0
    for D in range(8, 2001, 4):
        res = pell_multiple_renderer(D, vmin, vmax)
        if res is None:
            continue
        count += 1
        ok = (res["v_in_range"] and res["P_window"] and res["grid_theta0"] and res["grid_theta_pi4"]
              and res["grid_theta_pi2"] and res["delta_identity_ok"]
              and res["delta"] <= res["delta_bound1"] and res["delta_bound1"] <= res["delta_bound2"])
        conv_ok &= ok
        worst_d2 = max(worst_d2, res["delta"] * D * D)
    all_ok &= conv_ok
    w(f"    D values: {count}; all checks pass: {conv_ok}; max D^2 * Delta = {float(worst_d2):.4f} "
      f"(analytic cap 144 v_max/(sqrt2 (dv)^2) = {float(144 / (SQRT2 * Decimal('0.25'))):.2f})\n")
    w("  Pell subsequence D = 4P with v = 1 (exact grid laws; NUMERICAL KL, chi^2):\n")
    for P, Q in pell_pairs(10 ** 6)[1:9]:
        D = 4 * P
        x2 = R_INV_SQRT2
        x2p = Fraction(Q, P)
        assert is_grid_law(werner_law(x2p), D) and is_grid_law(werner_law(Fraction(1)), D)
        delta = abs(x2 - Decimal(Q) / P)
        kl, chi2 = kl_chi2_werner(x2p, x2)
        g, _ = grid_segment_separation(D, vmin, vmax) if D <= 20000 else (None, None)
        w(f"    P/Q={P}/{Q} D={D:7d} D^2*TV_pi4={float(delta / 2 * D * D):.6f} D^4*KL={float(kl * D ** 4):.4f} "
          f"D^4*chi2={float(chi2 * D ** 4):.4f} D^2 g_D={float(g * D * D) if g is not None else float('nan'):.6f}\n")
    c_ach = 8 * (3 + 2 * SQRT2) ** 2
    w(f"  achievability: n_s >= 8 (3+2sqrt2)^2 D^4 ln(4/eps) = {float(c_ach):.2f} D^4 ln(4/eps) trials per setting\n")
    w(f"  converse (Pell multiples, any D=0 mod 4 with (dv)D>=4): n_pi4 >= ((dv) D / 12)^4 ln(1/(4 eps)) / v_max^2\n")
    for k in (10, 20, 53):
        D = Decimal(2) ** k
        w(f"    D=2^{k}: achievability scale {float(c_ach * D ** 4 * Decimal(math.log(4 / 0.05))):.3e} trials, "
          f"converse scale {float((Decimal('0.5') * D / 12) ** 4 * Decimal(math.log(1 / 0.2))):.3e} trials (eps=0.05)\n")
    w("\n")

    # Theorem 3
    w("[T3] known v = 1, D = 2^k\n")
    bf_ok = True
    for k in range(1, 6):
        lr = tv_pi4_largest_remainder(k)
        bf = tv_pi4_bruteforce(k)
        ok = abs(lr - bf) < Decimal(10) ** -60
        if k >= 3:
            ok &= abs(lr - tv_pi4_formula(k)) < Decimal(10) ** -60
        bf_ok &= ok
    all_ok &= bf_ok
    w(f"  fixed setting pi/4: brute force == largest remainder == 2^(1-k)||2^(k-3)sqrt2|| for k<=5: {bf_ok} (NUMERICAL Decimal)\n")
    vals = []
    for k in range(3, 65):
        d, side = dist_to_int_pow2_sqrt2(k - 3)
        vals.append((k, d, side))
    kmin = min(vals, key=lambda t: t[1])
    w(f"  2^k TV_k = 2||2^(k-3)sqrt2|| for k=3..64: min = {float(2 * kmin[1]):.6f} at k={kmin[0]}; "
      f"max = {float(2 * max(v[1] for v in vals)):.6f}\n")
    w("  first values 2^k TV_k: " + ", ".join(f"k={k}:{float(2 * d):.4f}" for k, d, _ in vals[:10]) + "\n")
    w("  (Finite check only: whether inf_k 2^k TV_k > 0 is open; Ridout gives TV_k >= 2^{-(1+e)k} for k >= k0(e), ineffective.)\n")
    ad_ok = True
    for k in range(1, 13):
        D = 2 ** k
        tv = adapted_design_tv(D)
        ad_ok &= tv == Fraction(1, D)
        if k <= 6:
            p = werner_law(1 - Fraction(2, D))
            ad_ok &= brute_min_l1(p, D) / 2 == Fraction(1, D)
        for kk in range(0, k):
            # nested coarser grids: min TV to H_{2^kk} at the same design is also >= 1/D
            pc = werner_law(1 - Fraction(2, D))
            ad_ok &= l1_to_counts(pc, largest_remainder_round(pc, 2 ** kk), 2 ** kk) / 2 >= Fraction(1, D)
    all_ok &= ad_ok
    w(f"  adapted design cos(theta)=1-2/D: min TV(H_D, P_1) = 1/D exactly for D = 2^k, k=1..12, brute force D<=64, coarser 2^j grids >= 1/D: {ad_ok} (EXACT)\n")
    odd_ok = all(adapted_design_tv(D) == Fraction(1, 2 * D) for D in (3, 5, 7, 9, 15, 33))
    even_ok = all(adapted_design_tv(D) == Fraction(1, D) for D in (6, 10, 12, 14, 18))
    all_ok &= odd_ok and even_ok
    w(f"  adapted design for other D: min TV = 1/D for even D in (6,10,12,14,18): {even_ok}; = 1/(2D) for odd D in (3,5,7,9,15,33): {odd_ok} (EXACT)\n")
    for D in (16, 64, 256, 1024):
        n, T, e0, e1 = adapted_test_errors(D, 0.05)
        w(f"    NUMERICAL test errors eps=0.05, D={D}: n={n} (=16 D ln(3/eps) rounded up), threshold T={T}, "
          f"P_1 error={e0:.3e}, worst H_D acceptance<={e1:.3e}\n")
        all_ok &= e0 <= 0.05 and e1 <= 0.05
    worst_ratio, ok_opt, ok_hel = universal_rounding_bounds()
    all_ok &= ok_opt and ok_hel and worst_ratio <= 1
    w(f"  universal converse ingredients (200 random rational K=4 targets, D<=9): largest remainder optimal={ok_opt}; "
      f"max l1*D/(K/2)={worst_ratio} (<=1); Hellinger^2<=l1: {ok_hel}\n")
    for k in (10, 20, 53):
        D = 2 ** k
        w(f"    D=2^{k}: universal lower bound n >= (D-1)/2 ln(1/(4eps)) = {(D - 1) / 2 * math.log(1 / 0.2):.3e}; "
          f"adapted-design upper bound 16 D ln(3/eps) = {16 * D * math.log(3 / 0.05):.3e} (eps=0.05)\n")
    w("\n")

    # phase remark
    w("[R] phase nuisance (visibility-phase family, ST-T11)\n")
    ph = phase_counterexample(32)
    ph_ok = all(ok for _, ok in ph) and len(ph) > 0
    all_ok &= ph_ok
    inside = [str(x) for x, _ in ph if 8 * x * x >= 1]  # v = sqrt2 x in [1/2, 1]
    outside = [str(x) for x, _ in ph if 8 * x * x < 1]
    w(f"  schedule {{0,pi/4,pi/2}}, phi=-pi/4, D=32: grid hits x=v/sqrt2 with v in [1/2,1]: {inside}; with v < 1/2: {outside}; all exact grid laws: {ph_ok}\n\n")

    w(f"ALL CHECKS PASS: {all_ok}\n")
    return all_ok


def receipt_text() -> str:
    import io

    buffer = io.StringIO()
    main(buffer)
    return buffer.getvalue()


for _name, _value in list(globals().items()):
    if callable(_value) and getattr(_value, "__module__", None) == __name__ and _name not in {"_precise", "receipt_text"} and not isinstance(_value, type):
        globals()[_name] = _precise(_value)
del _name, _value


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
