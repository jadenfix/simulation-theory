"""Exact checks for renderer-memory constants on the Bell visibility-phase disk.

Derivation: docs/bell-disk-renderer-memory.md (claims ST-T290 to ST-T296,
ST-F58, ST-O05, ST-O06).

Standard library only. All certifying comparisons use exact rational
arithmetic (fractions.Fraction) or exact arithmetic in Q(sqrt d). Floats are
used only for printing human-readable decimal values.

Setting (see RESULT.md): a schedule is a probability vector w on setting
differences theta_j with unit directions s_j=(cos theta_j, sin theta_j).  The
predictive state is q in the unit disk D and the one-trial TV is

    TV(P_q, P_q') = h_Z(q-q') = sum_j (w_j/2) |s_j . (q-q')|,

so the TV epsilon-ball is epsilon * Zpolar, Zpolar = {x : h_Z(x) <= 1}.

``python -m simtheory.bell_disk_zonoid`` prints the receipt committed as
receipts/bell-disk-renderer-memory.txt.
"""

from __future__ import annotations

import random
from fractions import Fraction as F
from itertools import product
from math import isqrt, pi, sqrt

# Rational enclosures of pi (pi = 3.14159265358979...).
PI_LO = F(314159265, 100000000)
PI_HI = F(314159266, 100000000)
# Rational enclosures of sqrt2 and sqrt3.
SQRT2_LO, SQRT2_HI = F(141421356, 10**8), F(141421357, 10**8)
SQRT3_LO = F(173205080, 10**8)


# ---------------------------------------------------------------------------
# Exact arithmetic in Q(sqrt d)
# ---------------------------------------------------------------------------
class QS:
    """Element a + b*sqrt(d) with rational a, b and squarefree d > 1."""

    __slots__ = ("a", "b", "d")

    def __init__(self, a, b=0, d=2):
        self.a = F(a)
        self.b = F(b)
        self.d = d

    def _co(self, o):
        if isinstance(o, QS):
            if o.d != self.d and o.b != 0 and self.b != 0:
                raise ValueError("mixed radicands")
            return o
        return QS(o, 0, self.d)

    def __add__(self, o):
        o = self._co(o)
        return QS(self.a + o.a, self.b + o.b, self.d)

    __radd__ = __add__

    def __neg__(self):
        return QS(-self.a, -self.b, self.d)

    def __sub__(self, o):
        return self + (-self._co(o))

    def __rsub__(self, o):
        return self._co(o) - self

    def __mul__(self, o):
        o = self._co(o)
        return QS(self.a * o.a + self.d * self.b * o.b, self.a * o.b + self.b * o.a, self.d)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = self._co(o)
        n = o.a * o.a - self.d * o.b * o.b
        if n == 0:
            raise ZeroDivisionError
        conj = QS(o.a / n, -o.b / n, self.d)
        return self * conj

    def sign(self) -> int:
        a, b, d = self.a, self.b, self.d
        sa = (a > 0) - (a < 0)
        sb = (b > 0) - (b < 0)
        if sb == 0:
            return sa
        if sa == 0:
            return sb
        if sa == sb:
            return sa
        # opposite signs: compare a^2 with d b^2
        diff = a * a - d * b * b
        return sa if diff > 0 else (sb if diff < 0 else 0)

    def __abs__(self):
        return -self if self.sign() < 0 else self

    def __eq__(self, o):
        return (self - o).sign() == 0

    def __lt__(self, o):
        return (self - o).sign() < 0

    def __le__(self, o):
        return (self - o).sign() <= 0

    def __float__(self):
        return float(self.a) + float(self.b) * sqrt(self.d)

    def __repr__(self):
        if self.b == 0:
            return f"{self.a}"
        if self.a == 0:
            return f"{self.b}*sqrt({self.d})"
        return f"{self.a} + {self.b}*sqrt({self.d})"


def _abs(x):
    return abs(x)


def _det(u, v):
    return u[0] * v[1] - u[1] * v[0]


# ---------------------------------------------------------------------------
# Polar zonotope Zpolar for a schedule
# ---------------------------------------------------------------------------
def support(schedule, x):
    """h_Z(x) = sum_j (w_j/2)|s_j . x| for schedule = [(w_j, s_j), ...]."""
    total = 0
    for w, s in schedule:
        total = total + w * _abs(s[0] * x[0] + s[1] * x[1]) / 2
    return total


def _half(v):
    """0 for the open upper half plane (plus positive x-axis), 1 otherwise."""
    zero = v[0] - v[0]
    if v[1] > zero or (v[1] == zero and v[0] > zero):
        return 0
    return 1


def _angle_sort(vectors):
    import functools

    def cmp(u, v):
        hu, hv = _half(u), _half(v)
        if hu != hv:
            return hu - hv
        dd = _det(u, v)
        zero = dd - dd
        return -1 if dd > zero else (1 if dd < zero else 0)

    return sorted(vectors, key=functools.cmp_to_key(cmp))


def polar_vertices(schedule):
    """Vertices of Zpolar = {h_Z <= 1} in counterclockwise order.

    h_Z is linear on each cone between consecutive rays +-n_j, n_j = s_j
    rotated by 90 degrees, so the vertices are +-n_j / h_Z(n_j).
    Directions must be pairwise non-parallel (merge parallel classes first).
    """
    verts = []
    for _, s in schedule:
        n = (-s[1], s[0])
        h = support(schedule, n)
        verts.append((n[0] / h, n[1] / h))
        verts.append((-n[0] / h, -n[1] / h))
    return _angle_sort(verts)


def shoelace(verts):
    total = 0
    m = len(verts)
    for i in range(m):
        total = total + _det(verts[i], verts[(i + 1) % m])
    return total / 2


def polar_area(schedule):
    return shoelace(polar_vertices(schedule))


def zonotope_area(schedule):
    """area(Z) = sum_{i<j} w_i w_j |det(s_i,s_j)| for segments of length w_j."""
    total = 0
    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            wi, si = schedule[i]
            wj, sj = schedule[j]
            total = total + wi * wj * _abs(_det(si, sj))
    return total


def rational_unit(t: F):
    """Rational point on the unit circle: angle 2*atan(t)."""
    t = F(t)
    den = 1 + t * t
    return ((1 - t * t) / den, 2 * t / den)


def hexagon_closed_form(schedule):
    """area(Zpolar) = 4(a H3 + b H1 + c H2)/(H1 H2 H3) for 3 classes, ordered by angle."""
    order = _angle_sort([s if _half(s) == 0 else (-s[0], -s[1]) for _, s in schedule])
    wmap = {}
    for w, s in schedule:
        key = s if _half(s) == 0 else (-s[0], -s[1])
        wmap[key] = w
    s1, s2, s3 = order
    w1, w2, w3 = wmap[s1], wmap[s2], wmap[s3]
    a = _abs(_det(s1, s2))
    b = _abs(_det(s2, s3))
    c = _abs(_det(s1, s3))
    h1 = w2 * a + w3 * c
    h2 = w1 * a + w3 * b
    h3 = w1 * c + w2 * b
    return 4 * (a * h3 + b * h1 + c * h2) / (h1 * h2 * h3)


# ---------------------------------------------------------------------------
# Exact region {q : sum_j (w_j/2)|c_j - s_j.q| <= eps} by half-plane clipping
# ---------------------------------------------------------------------------
def _clip(poly, a, b, r):
    """Keep {q : a*q0 + b*q1 <= r}."""
    out = []
    m = len(poly)
    for i in range(m):
        p, nq = poly[i], poly[(i + 1) % m]
        fp = a * p[0] + b * p[1] - r
        fn = a * nq[0] + b * nq[1] - r
        if fp <= 0:
            out.append(p)
        if (fp < 0 < fn) or (fn < 0 < fp):
            t = fp / (fp - fn)
            out.append((p[0] + t * (nq[0] - p[0]), p[1] + t * (nq[1] - p[1])))
    return out


def served_region_area(schedule, offsets, eps, box=F(10)):
    """Exact area of {q : sum_j (w_j/2)|c_j - s_j.q| <= eps} (rational data)."""
    poly = [(-box, -box), (box, -box), (box, box), (-box, box)]
    m = len(schedule)
    for signs in product((1, -1), repeat=m):
        # sum_j sigma_j (w_j/2)(c_j - s_j.q) <= eps
        a = sum(-sg * w * s[0] / 2 for sg, (w, s) in zip(signs, schedule))
        b = sum(-sg * w * s[1] / 2 for sg, (w, s) in zip(signs, schedule))
        r = eps - sum(sg * w * c / 2 for sg, (w, _), c in zip(signs, schedule, offsets))
        poly = _clip(poly, a, b, r)
        if not poly:
            return F(0)
    return shoelace(poly) if len(poly) >= 3 else F(0)


def chsh_rotated_schedule():
    """Canonical CHSH in rotated coordinates U=(x+y)/sqrt2, V=(x-y)/sqrt2.

    The four setting differences -pi/4, pi/4, pi/4, 3pi/4 give correlator
    directions V, U, U, -V; the rotation preserves area.
    """
    q = F(1, 4)
    return [(q, (F(0), F(1))), (q, (F(1), F(0))), (q, (F(1), F(0))), (q, (F(0), F(-1)))]


def chsh_section_closed_form(offsets, eps):
    """Area of the CHSH served set in (U,V): (t^2 - dU^2 - dV^2)/2, t = 8 eps."""
    c1, c2, c3, c4 = offsets
    t = 8 * eps
    du, dv = abs(c2 - c3), abs(c1 + c4)
    if t < du + dv:
        return F(0)
    return (t * t - du * du - dv * dv) / 2


# ---------------------------------------------------------------------------
# CHSH grid count (Theorem 2), exact integers for eps = 1/n
# ---------------------------------------------------------------------------
def chsh_grid_counts(n: int):
    """Squares of side a=4 sqrt2/n (units of a) meeting / inside / crossing D.

    In units of a the disk has radius R with R^2 = n^2/32. Square
    [i,i+1]x[j,j+1] meets D iff 32*(dmin_i^2+dmin_j^2) <= n^2 and lies in D
    iff 32*(dmax_i^2+dmax_j^2) <= n^2.
    """
    k = isqrt(n * n // 32) + 2
    n2 = n * n

    def dmin(i):
        return 0 if i <= 0 <= i + 1 else min(abs(i), abs(i + 1))

    def dmax(i):
        return max(abs(i), abs(i + 1))

    meet = inside = 0
    for i in range(-k, k):
        for j in range(-k, k):
            if 32 * (dmin(i) ** 2 + dmin(j) ** 2) <= n2:
                meet += 1
                if 32 * (dmax(i) ** 2 + dmax(j) ** 2) <= n2:
                    inside += 1
    return meet, inside, meet - inside


def clipped_center_tv(n, i, j, t1, t2):
    """Exact TV between the clipped-center emission of cell (i,j) and P_q.

    q = ((i+t1)a, (j+t2)a), a = 4 sqrt2/n. Correlators U=(x+y)/sqrt2 and
    V=(x-y)/sqrt2 are rational because a/sqrt2 = 4/n. Returns (q in D, TV).
    """
    a_over_r2 = F(4, n)
    qx, qy = i + t1, j + t2  # units of a
    in_disk = F(32, n * n) * (qx * qx + qy * qy) <= 1
    uq, vq = a_over_r2 * (qx + qy), a_over_r2 * (qx - qy)
    cx, cy = i + F(1, 2), j + F(1, 2)
    uc, vc = a_over_r2 * (cx + cy), a_over_r2 * (cx - cy)

    def clamp(z):
        return max(F(-1), min(F(1), z))

    uc, vc = clamp(uc), clamp(vc)
    # four settings, weight 1/4: TV = (1/8)(|dU|+|dU|+|dV|+|dV|)
    tv = (abs(uc - uq) + abs(vc - vq)) / 4
    return in_disk, tv


# ---------------------------------------------------------------------------
# Hexagon lemma ingredients
# ---------------------------------------------------------------------------
def lemma_poly_gap(X, q):
    """(sum q)^2 (sum X)^4 - 243 X1X2X3 sum_i X_i q_j q_k  (>= 0 claimed)."""
    x1, x2, x3 = X
    q1, q2, q3 = q
    lhs = 243 * x1 * x2 * x3 * (x1 * q2 * q3 + x2 * q1 * q3 + x3 * q1 * q2)
    rhs = (q1 + q2 + q3) ** 2 * (x1 + x2 + x3) ** 4
    return rhs - lhs


def final_symmetric_gap(x, y, z):
    """64 s^4 p2 - 243 ((x+y)(y+z)(z+x))^2  (>= 0 claimed).

    This is the final symmetric inequality of the Theorem 5(ii) proof (after the
    Ravi substitution), not Schur's inequality itself.
    """
    s = x + y + z
    p2 = x * y + y * z + z * x
    e = (x + y) * (y + z) * (z + x)
    return 64 * s ** 4 * p2 - 243 * e * e


def random_rational_schedule(rng, m, denom=24):
    """m pairwise non-parallel rational unit directions with rational weights."""
    while True:
        ts = sorted({F(rng.randint(-3 * denom, 3 * denom), denom) for _ in range(m)})
        if len(ts) < m:
            continue
        dirs = [rational_unit(t) for t in ts]
        ok = all(_det(dirs[i], dirs[j]) != 0 for i in range(m) for j in range(i + 1, m))
        if not ok:
            continue
        raw = [rng.randint(1, 30) for _ in range(m)]
        tot = sum(raw)
        return [(F(r, tot), d) for r, d in zip(raw, dirs)]


# ---------------------------------------------------------------------------
# Main receipt
# ---------------------------------------------------------------------------
def regular_schedule_qs(m):
    """Regular m-direction schedule for m in {2,3,4} in exact Q(sqrt d)."""
    if m == 2:  # CHSH classes: directions pi/4 and -pi/4, weight 1/2 each
        r = QS(0, F(1, 2), 2)
        return [(F(1, 2), (r, r)), (F(1, 2), (r, -r))]
    if m == 3:
        h = QS(0, F(1, 2), 3)
        return [
            (F(1, 3), (QS(1, 0, 3), QS(0, 0, 3))),
            (F(1, 3), (QS(F(1, 2), 0, 3), h)),
            (F(1, 3), (QS(F(-1, 2), 0, 3), h)),
        ]
    if m == 4:
        r = QS(0, F(1, 2), 2)
        return [
            (F(1, 4), (QS(1, 0, 2), QS(0, 0, 2))),
            (F(1, 4), (r, r)),
            (F(1, 4), (QS(0, 0, 2), QS(1, 0, 2))),
            (F(1, 4), (-r, r)),
        ]
    raise ValueError


def chsh_four_settings_qs():
    """The repo's four canonical CHSH differences -pi/4, pi/4, pi/4, 3pi/4."""
    r = QS(0, F(1, 2), 2)
    q = F(1, 4)
    return [(q, (r, -r)), (q, (r, r)), (q, (r, r)), (q, (-r, r))]


schur_one_var_gap = final_symmetric_gap  # backwards-compatible name


def trine_product_schedule_class_weights():
    """Class weights of the product schedule alpha, beta uniform on {0, pi/3, 2pi/3}.

    Setting differences are multiples of pi/3; directions are taken mod pi.
    Returns {class index k (direction k pi/3): weight}.
    """
    weights = {0: F(0), 1: F(0), 2: F(0)}
    for a in range(3):
        for b in range(3):
            weights[(a - b) % 3] += F(1, 9)
    return weights


def trine_chsh_value():
    """max over the four CHSH forms of |sum_xy sign E_xy| / v at phi = 0 for
    Alice {0, 60 deg}, Bob {0, 120 deg}; cosines of multiples of 60 deg are rational."""
    cos60 = {0: F(1), 1: F(1, 2), 2: F(-1, 2), 3: F(-1), 4: F(-1, 2), 5: F(1, 2)}
    alice, bob = (0, 1), (0, 2)  # in units of 60 degrees
    corr = {(x, y): -cos60[(alice[x] - bob[y]) % 6] for x in (0, 1) for y in (0, 1)}
    best = F(0)
    for minus in ((0, 0), (0, 1), (1, 0), (1, 1)):
        value = sum((-corr[p] if p == minus else corr[p]) for p in corr)
        best = max(best, abs(value))
    return best


def run(seed=20261017, quick=False):
    rng = random.Random(seed)
    lines = []
    out = lines.append
    results = {}

    # (a) exact areas and Mahler products --------------------------------
    chsh2 = regular_schedule_qs(2)
    a2 = polar_area(chsh2)
    z2 = zonotope_area(chsh2)
    four = chsh_four_settings_qs()
    # support function of the 4-setting schedule equals the 2-class one
    probe = [(QS(1, 0, 2), QS(0, 0, 2)), (QS(F(3, 7), 0, 2), QS(F(-2, 5), 1, 2)), (QS(0, 1, 2), QS(F(1, 3), 0, 2))]
    same_support = all(support(four, x) == support(chsh2, x) for x in probe)
    reg3 = regular_schedule_qs(3)
    a3 = polar_area(reg3)
    z3 = zonotope_area(reg3)
    reg4 = regular_schedule_qs(4)
    a4 = polar_area(reg4)
    results["chsh_area"] = a2
    results["reg3_area"] = a3
    results["reg4_area"] = a4
    assert same_support
    assert a2 == QS(32, 0, 2) and (a2 * z2) == QS(8, 0, 2)
    assert a3 == QS(0, 18, 3) and (a3 * z3) == QS(9, 0, 3)
    assert a4 == QS(-512, 384, 2)
    # reg4 < 18 sqrt3 and > pi^3 via rational enclosures sqrt2 in [l2,u2], sqrt3 >= l3
    l2, u2 = SQRT2_LO, SQRT2_HI
    l3 = SQRT3_LO
    assert l2 * l2 < 2 < u2 * u2 and l3 * l3 < 3
    reg4_hi = -512 + 384 * u2
    reg4_lo = -512 + 384 * l2
    assert reg4_hi < 18 * l3  # A_4 < 18 sqrt3
    assert reg4_lo > PI_HI ** 3  # A_4 > pi^3
    out("(a) exact polar areas")
    out(f"    CHSH (4 settings == 2 classes, support identical: {same_support}): area(Zpolar) = {a2}, area(Z) = {z2}, Mahler = {a2 * z2}")
    out(f"    regular 3-direction: area(Zpolar) = {a3} ~ {float(a3):.6f}, Mahler = {a3 * z3}")
    out(f"    regular 4-direction: area(Zpolar) = {a4} ~ {float(a4):.6f}  (certified pi^3 < A_4 < 18 sqrt3)")
    out(f"    pi^3 ~ {pi ** 3:.6f}")

    # Fisher at the disk centre: sum_j w_j s_j s_j^T = I/2
    for name, sch in (("CHSH", four), ("regular-3", reg3), ("regular-4", reg4)):
        m11 = sum((w * s[0] * s[0] for w, s in sch), QS(0, 0, sch[0][1][0].d))
        m12 = sum((w * s[0] * s[1] for w, s in sch), QS(0, 0, sch[0][1][0].d))
        m22 = sum((w * s[1] * s[1] for w, s in sch), QS(0, 0, sch[0][1][0].d))
        assert m11 == F(1, 2) and m22 == F(1, 2) and m12 == 0, name
    out("    centre Fisher matrix sum_j w_j s_j s_j^T = I/2 exactly for CHSH, regular-3, regular-4")

    # (b) CHSH grid counts --------------------------------------------------
    out("(b) CHSH renderer count bracket, eps = 1/n (exact integer counts)")
    out("      n   lower=ceil(pi n^2/32)   in-family<=G+3Gbd   G(meet)   G/(pi n^2/32)")
    ns = (40, 80, 120, 160, 200, 240, 280, 320, 360, 400) if not quick else (40, 80, 120)
    grid_rows = []
    for n in ns:
        meet, inside, bd = chsh_grid_counts(n)
        lower_exact = PI_LO * n * n / 32
        lower = -((-lower_exact.numerator) // lower_exact.denominator)  # ceil
        upper_formula = PI_HI * (1 + F(8, n)) ** 2 * n * n / 32
        assert lower <= meet <= upper_formula
        assert bd <= PI_HI * n  # boundary squares <= pi/eps
        ratio = meet / (pi * n * n / 32)
        grid_rows.append((n, lower, meet, bd, ratio))
        out(f"    {n:4d}   {lower:8d}              {meet + 3 * bd:8d}          {meet:7d}   {ratio:.5f}")
    results["grid_rows"] = grid_rows

    # clipped-centre covering spot check (exact)
    tested = 0
    worst = F(0)
    for n in (8, 20, 40):
        meet_cells = []
        k = isqrt(n * n // 32) + 2
        for i in range(-k, k):
            for j in range(-k, k):
                di = 0 if i <= 0 <= i + 1 else min(abs(i), abs(i + 1))
                dj = 0 if j <= 0 <= j + 1 else min(abs(j), abs(j + 1))
                if 32 * (di * di + dj * dj) <= n * n:
                    meet_cells.append((i, j))
        for (i, j) in meet_cells:
            for t1 in (F(0), F(1, 3), F(1, 2), F(1)):
                for t2 in (F(0), F(2, 5), F(1)):
                    in_disk, tv = clipped_center_tv(n, i, j, t1, t2)
                    if in_disk:
                        tested += 1
                        assert tv <= F(1, n)
                        worst = max(worst, tv * n)
    out(f"    clipped-centre cover: {tested} exact (cell, point in D) pairs, max TV/eps = {worst}")
    results["clip_tested"] = tested

    # (c) Brunn section inequality for off-plane correlator vectors ----------
    chsh_rot = chsh_rotated_schedule()
    trials = 120 if not quick else 30
    eps = F(1, 16)
    central = served_region_area(chsh_rot, [F(0)] * 4, eps)
    assert central == 32 * eps * eps
    max_ratio = F(0)
    for _ in range(trials):
        c = [F(rng.randint(-30, 30), 40) for _ in range(4)]
        area = served_region_area(chsh_rot, c, eps)
        assert area == chsh_section_closed_form(c, eps)
        assert area <= 32 * eps * eps
        max_ratio = max(max_ratio, area / (32 * eps * eps))
    out(f"(c) CHSH served-set areas: {trials} random rational off-plane c, exact area == (t^2-dU^2-dV^2)/2, max area/(32 eps^2) = {max_ratio}")
    gen_trials = 40 if not quick else 10
    gen_max = F(0)
    for _ in range(gen_trials):
        m = rng.choice((3, 4))
        sch = random_rational_schedule(rng, m)
        cen = served_region_area(sch, [F(0)] * m, eps)
        assert cen == eps * eps * polar_area(sch)
        c = [F(rng.randint(-20, 20), 40) for _ in range(m)]
        area = served_region_area(sch, c, eps)
        assert area <= cen
        gen_max = max(gen_max, area / cen)
    out(f"    random rational 3/4-direction schedules: {gen_trials} cases, central area == eps^2 area(Zpolar), max off-centre/central = {float(gen_max):.4f}")

    # Theorem 3: area(Zpolar) > pi^3 on random rational schedules -----------
    th3 = 0
    min_th3 = None
    for _ in range(60 if not quick else 15):
        m = rng.randint(2, 6)
        sch = random_rational_schedule(rng, m)
        A = polar_area(sch)
        assert A > PI_HI ** 3
        th3 += 1
        min_th3 = A if min_th3 is None else min(min_th3, A)
    out(f"(T3) {th3} random rational schedules (2..6 classes): all area(Zpolar) > pi^3 (exact vs rational pi upper bound); min ~ {float(min_th3):.4f}")

    # (d) hexagon sub-claim -------------------------------------------------
    # closed form and lattice-tiling identity on random rational 3-schedules
    for _ in range(80 if not quick else 20):
        sch = random_rational_schedule(rng, 3)
        A = polar_area(sch)
        assert A == hexagon_closed_form(sch)
        v = polar_vertices(sch)
        p1, p2, p3 = v[0], v[1], v[2]
        assert v[3] == (-p1[0], -p1[1])
        lattice_cov = abs(_det((p1[0] + p2[0], p1[1] + p2[1]), (p2[0] + p3[0], p2[1] + p3[1])))
        assert lattice_cov == A
        assert A * A > 972  # area > 18 sqrt3
    # rational grid: directions t = k/den, weights on a simplex grid
    den_t = 4 if not quick else 2
    tvals = [F(k, den_t) for k in range(0, 3 * den_t + 1)]
    tvals += [F(-k, den_t) for k in range(1, 3 * den_t + 1)]
    dirs = sorted({rational_unit(t) for t in tvals})
    W = 9 if not quick else 6
    wgrid = [(F(i, W), F(j, W), F(W - i - j, W)) for i in range(1, W) for j in range(1, W - i)]
    count = 0
    best = None
    for i1 in range(len(dirs)):
        for i2 in range(i1 + 1, len(dirs)):
            for i3 in range(i2 + 1, len(dirs)):
                d1, d2, d3 = dirs[i1], dirs[i2], dirs[i3]
                if _det(d1, d2) == 0 or _det(d1, d3) == 0 or _det(d2, d3) == 0:
                    continue
                for w in wgrid:
                    sch = [(w[0], d1), (w[1], d2), (w[2], d3)]
                    A = hexagon_closed_form(sch)
                    count += 1
                    assert A * A > 972
                    if best is None or A < best[0]:
                        best = (A, sch)
    out(f"(d) hexagon: 80 random rational 3-schedules: shoelace == closed form, tiling covolume |det(p1+p2,p2+p3)| == area, area^2 > 972")
    out(f"    rational grid: {count} (direction triple, weight) cases, all area^2 > 972 = (18 sqrt3)^2; min area ~ {float(best[0]):.6f} vs 18 sqrt3 ~ {18 * sqrt(3):.6f}")
    results["hex_grid_count"] = count
    results["hex_grid_min"] = best[0]

    # key polynomial lemma and its Schur reduction on rational samples
    gaps = 0
    for _ in range(2000 if not quick else 300):  # final symmetric inequality samples
        X = [F(rng.randint(1, 50), rng.randint(1, 20)) for _ in range(3)]
        q = [F(rng.randint(0, 50), rng.randint(1, 20)) for _ in range(3)]
        if sum(q) == 0:
            continue
        assert lemma_poly_gap(X, q) >= 0
        x, y, z = (F(rng.randint(0, 40), rng.randint(1, 15)) for _ in range(3))
        if x + y + z == 0:
            continue
        assert final_symmetric_gap(x, y, z) >= 0
        gaps += 1
    assert lemma_poly_gap([F(1)] * 3, [F(1)] * 3) == 0
    assert final_symmetric_gap(F(1), F(1), F(1)) == 0
    out(f"    polynomial lemma 243 X1X2X3 sum X_i q_j q_k <= (sum q)^2 (sum X)^4 and the final symmetric inequality 64 s^4 p2 >= 243 ((x+y)(y+z)(z+x))^2: {gaps} exact random cases, equality at X=q=(1,1,1)")
    trine = trine_product_schedule_class_weights()
    chsh_trine = trine_chsh_value()
    assert all(w == F(1, 3) for w in trine.values()) and chsh_trine == F(5, 2)
    out("    trine product schedule (alpha, beta uniform on {0, pi/3, 2pi/3}): class weights (1/3, 1/3, 1/3) = the regular 3-class law; its CHSH sub-test (Alice {0, 60}, Bob {0, 120}) has |S| = 5/2 v at phi = 0")
    eps = F(3, 25)
    side = -(-1 // (4 * eps))  # ceil(1/(4 eps))
    packing = side * side
    area = PI_HI / (32 * eps * eps)
    assert packing == 9 and area < 7
    out(f"    finite eps: at eps = 3/25 the ST-T13 construction count ceil(1/(4eps))^2 = {packing} exceeds pi/(32 eps^2) ~ {float(PI_LO / (32 * eps * eps)):.3f}; the valid finite-eps lower bound is the maximum of the two")

    # constants --------------------------------------------------------------
    out("(const) asymptotic renderer constants  lim N eps^2  (decimal, for reading)")
    out(f"    ST-T13 constructive packing  1/16          = {1 / 16:.5f}")
    out(f"    CHSH exact                   pi/32         = {pi / 32:.5f}")
    out(f"    regular-3 exact              pi/(18 sqrt3) = {pi / (18 * sqrt(3)):.5f}")
    out(f"    regular-4 lower              pi/A_4        = {pi / float(a4):.5f}")
    out(f"    area-converse ceiling        1/pi^2        = {1 / pi ** 2:.5f}")
    out(f"    universal upper (Fejes Toth, symmetric) 2/(sqrt27 pi) = {2 / (sqrt(27) * pi):.5f}")
    out("ALL CHECKS PASSED")
    return lines, results


def receipt_text() -> str:
    receipt, _ = run()
    return "\n".join(receipt) + "\n"


if __name__ == "__main__":
    receipt, _ = run()
    print("\n".join(receipt))
