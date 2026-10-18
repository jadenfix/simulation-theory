"""Exact certificate for the Le Cam deficiency of a visibility-contracted Bell simulator.

Derivation: docs/le-cam-deficiency-bell-simulator.md (claims ST-T306 to
ST-T309, ST-F60, ST-O08). Standard library only (fractions, itertools,
hashlib); every assertion is exact. ``python -m simtheory.le_cam_deficiency``
prints the receipt committed as receipts/le-cam-deficiency-bell-simulator.txt.

Model (one trial, setting pair i drawn with public weight pi_i, outcomes
a, b in {+1, -1}):

    P_v(a, b | i) = (1 + v * a * b * c_i) / 4,   v in [0, 1],   |c_i| = C.

Physics experiment E = {P_v}; simulator F = {P_{lam v}}, 0 <= lam <= 1.
Kernels K_i act on (a, b) given the public setting i.  Total variation is
half the L1 distance.  Two aggregations of the per-setting TV are certified:

    avg:  sup_v sum_i pi_i TV_i(v)     (the repo's joint setting-outcome TV)
    max:  sup_v max_i TV_i(v)          (worst setting)

Claimed values:
    randomized   delta      = C (1 - lam) / (2 (2 - C lam))       (both)
    det, max     delta_det  = min(C (1 - lam) / 2, 1/4)
    det, avg     >= delta_hull = (1 - lam) / (2 (2 - lam))  if lam C < 2C - 1
                              = C (1 - lam) / 2             otherwise
"""

from __future__ import annotations

import hashlib
import itertools
import sys
from fractions import Fraction as Fr

# ---------------------------------------------------------------- Q(sqrt 2)


class QS2:
    """Exact element a + b*sqrt(2) of Q(sqrt 2) with Fraction coefficients."""

    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = Fr(a)
        self.b = Fr(b)

    @staticmethod
    def lift(x):
        return x if isinstance(x, QS2) else QS2(x, 0)

    def __add__(self, o):
        o = QS2.lift(o)
        return QS2(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __neg__(self):
        return QS2(-self.a, -self.b)

    def __sub__(self, o):
        return self + (-QS2.lift(o))

    def __rsub__(self, o):
        return QS2.lift(o) - self

    def __mul__(self, o):
        o = QS2.lift(o)
        return QS2(self.a * o.a + 2 * self.b * o.b, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = QS2.lift(o)
        den = o.a * o.a - 2 * o.b * o.b
        if den == 0:
            raise ZeroDivisionError("division by zero in Q(sqrt2)")
        return self * QS2(o.a / den, -o.b / den)

    def __rtruediv__(self, o):
        return QS2.lift(o) / self

    def sign(self):
        a, b = self.a, self.b
        if a >= 0 and b >= 0:
            return 0 if (a == 0 and b == 0) else 1
        if a <= 0 and b <= 0:
            return -1
        # opposite signs: compare a^2 with 2 b^2 (never equal unless both 0)
        if a > 0:
            return 1 if a * a > 2 * b * b else -1
        return 1 if 2 * b * b > a * a else -1

    def __abs__(self):
        return -self if self.sign() < 0 else self

    def _cmp(self, o):
        return (self - QS2.lift(o)).sign()

    def __eq__(self, o):
        return self._cmp(o) == 0

    def __hash__(self):
        return hash((self.a, self.b))

    def __lt__(self, o):
        return self._cmp(o) < 0

    def __le__(self, o):
        return self._cmp(o) <= 0

    def __gt__(self, o):
        return self._cmp(o) > 0

    def __ge__(self, o):
        return self._cmp(o) >= 0

    def __float__(self):
        return float(self.a) + float(self.b) * 2 ** 0.5

    def __repr__(self):
        return f"({self.a} + {self.b}*sqrt2)"


SQRT2 = QS2(0, 1)
INV_SQRT2 = QS2(0, Fr(1, 2))

# ---------------------------------------------------------------- the model

OUTCOMES = ((1, 1), (1, -1), (-1, 1), (-1, -1))


def law(v, c):
    """P_v(. | setting) as a tuple over OUTCOMES."""
    return tuple((1 + v * a * b * c) / 4 for (a, b) in OUTCOMES)


def push(p, K):
    """Push distribution p through the 4x4 row-stochastic kernel K."""
    return tuple(sum(p[i] * K[i][j] for i in range(4)) for j in range(4))


def tv(p, q):
    return sum(abs(x - y) for x, y in zip(p, q)) / 2


def identity_kernel():
    return tuple(tuple(Fr(1) if i == j else Fr(0) for j in range(4)) for i in range(4))


def deterministic_kernel(g):
    return tuple(tuple(Fr(1) if g[i] == j else Fr(0) for j in range(4)) for i in range(4))


def corr_target(sigma):
    """Map z=(a,b) -> index of (a, sigma*a): perfectly (anti)correlated output."""
    return tuple(OUTCOMES.index((a, sigma * a)) for (a, _b) in OUTCOMES)


def mixing_kernel(s, sigma):
    """(1-s) * identity + s * [output (a, sigma a)]."""
    tgt = corr_target(sigma)
    return tuple(
        tuple((1 - s) * (1 if i == j else 0) + s * (1 if tgt[i] == j else 0) for j in range(4))
        for i in range(4)
    )


def sgn(x):
    return 1 if x > 0 else -1


def formula_delta(C, lam):
    return C * (1 - lam) / (2 * (2 - C * lam))


def formula_s(C, lam):
    return C * (1 - lam) / (2 - C * lam)


def formula_det_max(C, lam):
    a = C * (1 - lam) / 2
    return a if a <= Fr(1, 4) else QS2.lift(Fr(1, 4)) if isinstance(a, QS2) else Fr(1, 4)


def formula_hull(C, lam):
    a = C * (1 - lam) / 2
    d = (1 - C) / 2
    if d < a:
        return (1 - lam) / (2 * (2 - lam))
    return a


def errors(cs, pis, kernels, lam, v):
    """Per-setting TV(P_{lam v} K_i, P_v) at parameter v."""
    return [tv(push(law(lam * v, c), K), law(v, c)) for c, K in zip(cs, kernels)]


def aggregate(errs, pis, mode):
    if mode == "avg":
        return sum(p * e for p, e in zip(pis, errs))
    return max(errs)


# ---------------------------------------------------------------- Theorem 1


def primal_certificate(cs, pis, C, lam, v_grid):
    """Optimal mixing kernel: endpoint errors equal the formula; interior grid below it."""
    s = formula_s(C, lam)
    Ks = [mixing_kernel(s, sgn(c)) for c in cs]
    target = formula_delta(C, lam)
    out = {}
    for mode in ("avg", "max"):
        e0 = aggregate(errors(cs, pis, Ks, lam, 0), pis, mode)
        e1 = aggregate(errors(cs, pis, Ks, lam, 1), pis, mode)
        assert e0 == target and e1 == target, (mode, e0, e1, target)
        for v in v_grid:
            assert aggregate(errors(cs, pis, Ks, lam, v), pis, mode) <= target
        out[mode] = target
    # identity kernel value and naive two-point bound
    Id = [identity_kernel()] * len(cs)
    ident = max(
        aggregate(errors(cs, pis, Id, lam, 0), pis, "avg"),
        aggregate(errors(cs, pis, Id, lam, 1), pis, "avg"),
    )
    assert ident == C * (1 - lam) / 2
    naive = C * (1 - lam) / 4
    return target, ident, naive


def dual_certificate(c, lam):
    """Exact min over ALL 4x4 kernels of w*<f,UK-U> + (1-w)*<f,P1-Q_lam K>.

    The objective is linear in K and K ranges over a product of simplices
    (one per input row), so the minimum is a sum of row-wise minima over
    output points.  Returns (w, lower_bound).
    """
    C = abs(c)
    sigma = sgn(c)
    w = (1 - lam * C) / (2 - lam * C)
    f = tuple(1 if a * b == sigma else 0 for (a, b) in OUTCOMES)
    U = law(0, c)
    Q = law(lam, c)
    P1 = law(1, c)
    total = QS2.lift(0) if isinstance(C, QS2) else Fr(0)
    for z in range(4):
        coeffs = [w * U[z] * f[zp] - (1 - w) * Q[z] * f[zp] for zp in range(4)]
        total = total + min(coeffs)
    const = -w * sum(fz * u for fz, u in zip(f, U)) + (1 - w) * sum(fz * p for fz, p in zip(f, P1))
    return w, total + const


# ---------------------------------------------------------------- Theorem 2


def det_pairs(c, lam):
    """(e0, e1) for all 256 deterministic relabelings of one setting."""
    pairs = {}
    U, Q, P1 = law(0, c), law(lam, c), law(1, c)
    for g in itertools.product(range(4), repeat=4):
        K = deterministic_kernel(g)
        pairs[g] = (tv(push(U, K), U), tv(push(Q, K), P1))
    return pairs


def pareto(points):
    pts = set(points)
    return sorted(
        (p for p in pts if not any(q != p and q[0] <= p[0] and q[1] <= p[1] for q in pts)),
        key=lambda p: (float(p[0]), float(p[1])),
    )


def frontier_ABD(C, lam):
    return (
        (Fr(0), C * (1 - lam) / 2),
        (Fr(1, 4), (1 - lam * C) / 4),
        (Fr(1, 2), (1 - C) / 2),
    )


def dominated_by(p, cands):
    return any(q[0] <= p[0] and q[1] <= p[1] for q in cands)


def det_values(cs, pis, C, lam):
    """Exact deterministic deficiencies on a concrete schedule.

    Returns (worst-setting value, schedule-averaged value).  Every map is
    dominated by one of A, B, D (verified here), so for the averaged value
    it suffices to let each setting choose among A, B, D.
    """
    ABD = frontier_ABD(C, lam)
    for c in cs:
        pairs = det_pairs(c, lam)
        for p in pairs.values():
            assert dominated_by(p, ABD), p
        # and A, B, D are attained
        vals = set(pairs.values())
        for q in ABD:
            assert any(p[0] == q[0] and p[1] == q[1] for p in vals), q
    worst = min(max(q) for q in ABD)
    best = None
    for choice in itertools.product(ABD, repeat=len(cs)):
        E0 = sum(p * q[0] for p, q in zip(pis, choice))
        E1 = sum(p * q[1] for p, q in zip(pis, choice))
        m = max(E0, E1)
        if best is None or m < best:
            best = m
    return worst, best


# --- all-parameter proof of the per-setting deterministic frontier ---------
#
# Write t = lam*C.  For a deterministic map g the error e1(g) is
#   (1/8) * sum_{z'} | (n_{z'} - 1) + m_{z'} t - s_{z'} C |
# with integer n, m and s = +-1 (here c = +C; c = -C is the b -> -b relabeling).
# e0(g) is a constant in {0, 1/4, 1/2, 3/4}.  The target attached to level e0 is
#   0 -> (C - t)/2,  1/4 -> (1 - t)/4,  1/2 and 3/4 -> (1 - C)/2.
# On the triangle T = {0 <= t <= C <= 1} the difference e1 - target is linear
# on each cell of the arrangement of g's own break lines and the edges of T,
# so it is >= 0 on T iff it is >= 0 at every arrangement vertex inside T.


def _line_points(lines):
    pts = set()
    for (p1, q1, r1), (p2, q2, r2) in itertools.combinations(lines, 2):
        # p + q t + r C = 0
        det = q1 * r2 - q2 * r1
        if det == 0:
            continue
        t = Fr(-p1 * r2 + p2 * r1, det)
        Cc = Fr(-q1 * p2 + q2 * p1, det)
        if 0 <= t <= Cc <= 1:
            pts.add((t, Cc))
    return pts


TRIANGLE_EDGES = ((0, 1, 0), (0, 1, -1), (-1, 0, 1))  # t=0, t=C, C=1


def frontier_proof_all_parameters():
    level_target = {
        Fr(0): lambda t, C: (C - t) / 2,
        Fr(1, 4): lambda t, C: (1 - t) / 4,
        Fr(1, 2): lambda t, C: (1 - C) / 2,
        Fr(3, 4): lambda t, C: (1 - C) / 2,
    }
    checked_points = 0
    for g in itertools.product(range(4), repeat=4):
        n = [g.count(j) for j in range(4)]
        e0 = Fr(sum(abs(nj - 1) for nj in n), 8)
        terms = []
        for j, (a2, b2) in enumerate(OUTCOMES):
            m = sum(OUTCOMES[i][0] * OUTCOMES[i][1] for i in range(4) if g[i] == j)
            terms.append((n[j] - 1, m, -(a2 * b2)))
        lines = [tt for tt in terms if (tt[1], tt[2]) != (0, 0)] + list(TRIANGLE_EDGES)
        pts = _line_points(lines)
        tgt = level_target[e0]
        for (t, C) in pts:
            e1 = sum(abs(p + q * t + r * C) for (p, q, r) in terms) / 8
            if e1 < tgt(t, C):
                raise AssertionError(("frontier violated", g, t, C))
            checked_points += 1
    return checked_points


# ------------------------------------------------- joint-record kernels


def joint_cells(k):
    """Joint (setting, outcome) cells (i, z) with z indexing OUTCOMES."""
    return [(i, z) for i in range(k) for z in range(4)]


def joint_law(v, cs, pis):
    return [pis[i] * law(v, cs[i])[z] for i, z in joint_cells(len(cs))]


def joint_dual_certificate(cs, pis, lam):
    """Exact min over ALL Markov kernels on the joint (setting, outcome) record of
    w*<f, U K - U> + (1-w)*<f, P1 - Q K>, with f the indicator of the agreeing
    cells {(i, (a,b)) : ab = sign(c_i)}; equal magnitudes C.

    The objective is linear in K, so the minimum is a sum of row-wise minima
    over the 4k output cells. Under avg aggregation this lower-bounds the
    deficiency against every joint kernel, including kernels that relabel the
    setting.
    """
    C = abs(cs[0])
    w = (1 - lam * C) / (2 - lam * C)
    cells = joint_cells(len(cs))
    f = [1 if OUTCOMES[z][0] * OUTCOMES[z][1] == sgn(cs[i]) else 0 for i, z in cells]
    U = joint_law(0, cs, pis)
    Q = joint_law(lam, cs, pis)
    P1 = joint_law(1, cs, pis)
    zero = QS2.lift(0) if isinstance(C, QS2) else Fr(0)
    total = zero
    for row in range(len(cells)):
        total = total + min(w * U[row] * f[col] - (1 - w) * Q[row] * f[col] for col in range(len(cells)))
    const = -w * sum((fz * u for fz, u in zip(f, U)), zero) + (1 - w) * sum((fz * p for fz, p in zip(f, P1)), zero)
    return w, total + const


# A deterministic map on the 16 joint cells of the rational schedule (C = 3/5,
# weights 1/2, 1/4, 1/8, 1/8) that relabels settings; found by a MILP during
# review and verified exactly here. At lam = 1/4 its errors are 1/8 (v = 0) and
# 23/160 (v = 1), below the setting-preserving hull bound 3/14.
JOINT_DETERMINISTIC_MAP = (0, 2, 1, 3, 7, 0, 3, 4, 8, 9, 5, 14, 12, 13, 11, 6)


def joint_map_errors(cs, pis, lam, mapping):
    k = len(cs)
    n = 4 * k
    errs = []
    for v in (0, 1):
        src = joint_law(lam * v, cs, pis)
        tgt = joint_law(v, cs, pis)
        image = [Fr(0)] * n
        for z, zp in enumerate(mapping):
            image[zp] += src[z]
        errs.append(sum(abs(x - y) for x, y in zip(image, tgt)) / 2)
    return tuple(errs)


def unequal_worst_setting(cs, lam):
    """Corollary 1a: per-setting mixing kernels with C_i give max_i errors V(C_max),
    and the dual at a setting attaining C_max equals V(C_max)."""
    Cmax = max(abs(c) for c in cs)
    worst = Fr(0)
    for c in cs:
        C = abs(c)
        K = mixing_kernel(formula_s(C, lam), sgn(c))
        e0 = tv(push(law(0, c), K), law(0, c))
        e1 = tv(push(law(lam, c), K), law(1, c))
        assert e0 == e1 == formula_delta(C, lam)
        worst = max(worst, e0, e1)
    c_star = next(c for c in cs if abs(c) == Cmax)
    _, lb = dual_certificate(c_star, lam)
    return worst, lb, formula_delta(Cmax, lam)


# ---------------------------------------------------------------- driver


def canonical_schedule():
    # repo convention P = 1/4 [1 - ab v cos(theta)], theta in {-pi/4, pi/4, pi/4, 3pi/4}
    cs = (-INV_SQRT2, -INV_SQRT2, -INV_SQRT2, INV_SQRT2)
    pis = (Fr(1, 4),) * 4
    return cs, pis, INV_SQRT2


def rational_schedule():
    C = Fr(3, 5)
    cs = (C, C, C, -C)
    pis = (Fr(1, 2), Fr(1, 4), Fr(1, 8), Fr(1, 8))
    return cs, pis, C


LAM_GRID = tuple(Fr(k, 8) for k in range(9))
V_GRID = tuple(Fr(k, 10) for k in range(11))


def run(verbose=True):
    lines = []

    def out(s):
        lines.append(s)
        if verbose:
            print(s)

    out("Le Cam deficiency of a visibility-contracted Bell simulator: exact receipt")
    out("TV = half L1; setting-preserving kernels unless stated; v in [0,1]; lam on grid k/8")
    n_pts = frontier_proof_all_parameters()
    out(f"[T2a] every deterministic setting-wise relabeling is dominated by one of {{A,B,D}} on all (C,lam) in [0,1]^2: "
        f"256 maps, {n_pts} arrangement vertices checked exactly (piecewise-linear certificate)")
    for name, (cs, pis, C) in (("canonical CHSH |c|=1/sqrt2, uniform", canonical_schedule()),
                               ("rational |c|=3/5, weights 1/2,1/4,1/8,1/8", rational_schedule())):
        out(f"--- schedule: {name}")
        for lam in LAM_GRID:
            delta, ident, naive = primal_certificate(cs, pis, C, lam, V_GRID)
            for c in cs:
                w, lb = dual_certificate(c, lam)
                assert lb == delta, (lb, delta)
                assert 0 <= w <= 1
            _, joint_lb = joint_dual_certificate(cs, pis, lam)
            assert joint_lb == delta, (joint_lb, delta)
            if lam < 1:
                assert naive <= delta < ident
                if C * lam > 0:
                    assert naive < delta
            worst, avgdet = det_values(cs, pis, C, lam)
            assert worst == formula_det_max(C, lam)
            hull = formula_hull(C, lam)
            assert avgdet >= hull
            if lam < 1 and C < 1:
                assert hull > delta and worst > delta and avgdet > delta
            out(f"lam={str(lam):>4}  delta={float(delta):.6f}  s={float(formula_s(C, lam)):.6f}  "
                f"identity={float(ident):.6f}  naive={float(naive):.6f}  "
                f"det_max={float(worst):.6f}  det_avg={float(avgdet):.6f}  hull={float(hull):.6f}")
        out("    primal (mixing kernel) == dual (two-point test) == formula, exactly, on every grid lam;")
        out("    the dual over ALL kernels on the joint (setting, outcome) record also equals the formula (avg aggregation)")
    cs, pis, C = canonical_schedule()
    d_half = formula_delta(C, Fr(1, 2))
    out(f"canonical lam=1/2: delta = {d_half!r} = {float(d_half):.6f} "
        f"= (1-lam)/(2(2 sqrt2 - lam)) -> {float(Fr(1, 2) / (2 * (2 * SQRT2 - Fr(1, 2)))):.6f}")
    # Blackwell direction: E garbles to F exactly
    for lam in LAM_GRID:
        Kdep = tuple(tuple(lam * (1 if i == j else 0) + (1 - lam) / 4 for j in range(4)) for i in range(4))
        for c in cs:
            for v in V_GRID:
                assert push(law(v, c), Kdep) == law(lam * v, c)
    out("delta(E,F) = 0: depolarizing kernel lam*Id + (1-lam)*Unif maps P_v to P_{lam v} exactly")
    cs_r, pis_r, C_r = rational_schedule()
    e0, e1 = joint_map_errors(cs_r, pis_r, Fr(1, 4), JOINT_DETERMINISTIC_MAP)
    relabels = any(JOINT_DETERMINISTIC_MAP[z] // 4 != z // 4 for z in range(16))
    hull_q = formula_hull(C_r, Fr(1, 4))
    delta_q = formula_delta(C_r, Fr(1, 4))
    assert (e0, e1) == (Fr(1, 8), Fr(23, 160)) and relabels and delta_q < max(e0, e1) < hull_q
    out(f"joint deterministic map that relabels settings (rational schedule, lam=1/4): errors ({e0}, {e1}), "
        f"value {max(e0, e1)} < setting-preserving hull {hull_q}; still > delta = {delta_q}")
    cs_u = (Fr(1, 2), Fr(-1, 10), Fr(3, 5))
    for lam in LAM_GRID:
        worst, lb, target = unequal_worst_setting(cs_u, lam)
        assert worst == lb == target
    out("Corollary 1a (unequal magnitudes, worst setting): c=(1/2,-1/10,3/5), every grid lam: "
        "max_i errors of the mixing kernels == dual at C_max == V(3/5)")
    digest = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    out(f"ALL CHECKS PASSED  sha256(receipt body)={digest}")
    return lines


def receipt_text() -> str:
    return "\n".join(run(verbose=False)) + "\n"


if __name__ == "__main__":
    run(verbose=True)
