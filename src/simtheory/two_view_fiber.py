"""Exact certificates for the two-view orthogonal fiber and its identified set.

Standard library only. All model-level identities use fractions.Fraction.
Floating point is used only to (a) locate arc endpoints so that exact rational
probe points can be placed on either side of them, and (b) report a KL number
for the three-view separation. Every pass/fail decision below is exact.

Derivation: docs/two-view-orthogonal-fiber.md (claims ST-T297 to ST-T305,
ST-M86 to ST-M89, ST-F59, ST-O07). ``python -m simtheory.two_view_fiber``
prints the receipt committed as receipts/two-view-orthogonal-fiber.txt.
"""

from __future__ import annotations

import hashlib
import math
from fractions import Fraction as F
from itertools import combinations, product

# ---------------------------------------------------------------------------
# exact linear algebra on lists of Fractions
# ---------------------------------------------------------------------------


def mat(rows):
    return [[F(x) for x in r] for r in rows]


def tr(A):
    return [list(c) for c in zip(*A)]


def mm(A, B):
    Bt = tr(B)
    return [[sum((a * b for a, b in zip(r, c)), F(0)) for c in Bt] for r in A]


def diag(v):
    n = len(v)
    return [[F(v[i]) if i == j else F(0) for j in range(n)] for i in range(n)]


def eye(n):
    return diag([1] * n)


def mv(A, v):
    return [sum((a * x for a, x in zip(r, v)), F(0)) for r in A]


def inv(A):
    n = len(A)
    M = [list(map(F, r)) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            raise ZeroDivisionError("singular matrix")
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [r[n:] for r in M]


def det(A):
    n = len(A)
    M = [list(map(F, r)) for r in A]
    d = F(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return F(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return d


def rank(A):
    M = [list(map(F, r)) for r in A]
    rk, rows, cols = 0, len(M), len(M[0])
    for c in range(cols):
        p = next((r for r in range(rk, rows) if M[r][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for r in range(rows):
            if r != rk and M[r][c] != 0:
                f = M[r][c] / M[rk][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[rk])]
        rk += 1
    return rk


def is_nonneg(A):
    return all(x >= 0 for r in A for x in r)


def is_pos(A):
    return all(x > 0 for r in A for x in r)


def is_row_stochastic(A):
    return is_nonneg(A) and all(sum(r) == 1 for r in A)


def is_orthogonal(O):
    return mm(tr(O), O) == eye(len(O))


def is_permutation(A):
    return all(x in (0, 1) for r in A for x in r) and all(sum(r) == 1 for r in A) and all(
        sum(c) == 1 for c in tr(A)
    )


# ---------------------------------------------------------------------------
# observable laws
# ---------------------------------------------------------------------------


def one_view(pi, K):
    return mv(tr(K), pi)


def two_view(pi, K1, K2=None):
    K2 = K1 if K2 is None else K2
    return mm(mm(tr(K1), diag(pi)), K2)


def three_view(pi, K):
    n = len(K[0])
    return [
        [[sum((p * r[a] * r[b] * r[c] for p, r in zip(pi, K)), F(0)) for c in range(n)] for b in range(n)]
        for a in range(n)
    ]


# ---------------------------------------------------------------------------
# Theorem A: orthogonal parametrization of the same-channel fiber
# ---------------------------------------------------------------------------


def cayley(S):
    n = len(S)
    I = eye(n)
    return mm([[I[i][j] - S[i][j] for j in range(n)] for i in range(n)], inv([[I[i][j] + S[i][j] for j in range(n)] for i in range(n)]))


def skew3(a, b, c):
    return mat([[0, a, b], [-a, 0, c], [-b, -c, 0]])


def rot2(t):
    """Rational rotation by angle theta with tan(theta/2) = t."""
    t = F(t)
    c = (1 - t * t) / (1 + t * t)
    s = 2 * t / (1 + t * t)
    return [[c, -s], [s, c]]


def fiber_point(s, K, O):
    """Map an orthogonal O to (pi', K', A) if O D_s K >= 0, else None.

    s = sqrt(pi) must be supplied exactly (rational in all witnesses).
    """
    W = mm(diag(s), K)
    M = mm(O, W)
    if not is_nonneg(M):
        return None
    u = [sum(r) for r in M]  # = O s
    if any(x <= 0 for x in u):
        return None
    Kp = [[x / ui for x in r] for r, ui in zip(M, u)]
    pip = [x * x for x in u]
    A = mm(mm(diag([1 / x for x in u]), O), diag(s))
    return pip, Kp, A


def gauge_from_factorizations(K, Kp):
    """A with Kp = A K, via the right inverse R = K^T (K K^T)^{-1}."""
    R = mm(tr(K), inv(mm(K, tr(K))))
    A = mm(Kp, R)
    assert mm(A, K) == Kp, "row spaces differ: Kp is not A K"
    return A


# ---------------------------------------------------------------------------
# Theorem B: k = 2 sharp identified interval from the observable law only
# ---------------------------------------------------------------------------


def c_values(q, T):
    return {x: q[x] * q[x] / T[x][x] for x in range(len(q)) if q[x] > 0}


def extreme_pair(q, T):
    """Outcome pair with the widest column angle: minimizes T_xy^2/(T_xx T_yy)."""
    xs = [x for x in range(len(q)) if q[x] > 0]
    best = None
    for x, y in combinations(xs, 2):
        v = T[x][y] * T[x][y] / (T[x][x] * T[y][y])
        if best is None or v < best[0]:
            best = (v, x, y)
    return best[1], best[2]


def identified_interval_k2(q, T, x_star):
    """Identified set [L, U] for the weight of the latent favoured by outcome x_star.

    x_star must be one end of the extreme pair. Returns (L, U, y_star).
    """
    x, y = extreme_pair(q, T)
    if x_star == y:
        x, y = y, x
    assert x_star == x
    c = c_values(q, T)
    return 1 - c[y], c[x], y


def anchor_model(q, T, x):
    """k = 2 model in which outcome x is an anchor for latent 0 (rational in q, T)."""
    n = len(q)
    p0 = q[x] * q[x] / T[x][x]
    r0 = [T[x][y] / q[x] for y in range(n)]
    p1 = 1 - p0
    r1 = [(q[y] - p0 * r0[y]) / p1 for y in range(n)]
    return [p0, p1], [r0, r1]


def float_arc_k2(s, K):
    """Float location of the admissible rotation arc [theta_lo, theta_hi]."""
    ang = [math.atan2(float(s[1] * K[1][x]), float(s[0] * K[0][x])) for x in range(len(K[0])) if K[0][x] + K[1][x] > 0]
    return -min(ang), math.pi / 2 - max(ang)


# ---------------------------------------------------------------------------
# outer weight floor: ell(T) = min over extreme rays nu of C* of (nu.s)^2/|nu|^2
# ---------------------------------------------------------------------------


def cofactor_normal(vecs):
    """Generalized cross product of k-1 vectors in R^k."""
    k = len(vecs[0])
    out = []
    for j in range(k):
        minor = [[v[i] for i in range(k) if i != j] for v in vecs]
        out.append((-1) ** j * det(minor) if minor and minor[0] else F((-1) ** j))
    return out


def weight_floor(s, K, return_ray=False):
    """Exact ell for W = D_s K, computed from supporting facet normals of cone(W columns)."""
    W = mm(diag(s), K)
    k = len(W)
    cols = [list(c) for c in tr(W) if any(c)]
    best = None
    for sub in combinations(range(len(cols)), k - 1):
        nu = cofactor_normal([cols[i] for i in sub]) if k > 1 else [F(1)]
        if all(x == 0 for x in nu):
            continue
        dots = [sum(a * b for a, b in zip(nu, c)) for c in cols]
        if all(d >= 0 for d in dots):
            pass
        elif all(d <= 0 for d in dots):
            nu = [-x for x in nu]
        else:
            continue
        val = sum(a * b for a, b in zip(nu, s)) ** 2 / sum(a * a for a in nu)
        if best is None or val < best[0]:
            best = (val, nu)
    return best if return_ray else best[0]


def cross3(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def floor_sharpness_k3(s, K):
    """Exact test that ell is attained (k = 3).

    nu is a minimizing extreme ray of C* = {o : o.w_x >= 0}. The slice
    P = C* intersect nu^perp is a planar convex cone whose boundary rays lie among
    +-(nu x w_x). If two feasible rays have nonpositive dot product, P contains two
    orthogonal unit vectors o2, o3, and (nu/|nu|, o2, o3) is an orthonormal frame in C*
    whose first latent weight equals ell exactly.
    """
    W = mm(diag(s), K)
    cols = [list(c) for c in tr(W)]
    ell, nu = weight_floor(s, K, return_ray=True)
    rays = []
    for w in cols:
        d = cross3(nu, w)
        for sg in (1, -1):
            r = [sg * x for x in d]
            if any(r) and all(sum(a * b for a, b in zip(r, c)) >= 0 for c in cols):
                rays.append(r)
    obtuse = any(sum(a * b for a, b in zip(r1, r2)) <= 0 for r1, r2 in combinations(rays, 2))
    return ell, nu, rays, obtuse


# ---------------------------------------------------------------------------
# witnesses
# ---------------------------------------------------------------------------

PI2 = [F(9, 25), F(16, 25)]
S2 = [F(3, 5), F(4, 5)]
K2 = mat([[F(1, 2), F(1, 4), F(1, 4)], [F(1, 6), F(1, 3), F(1, 2)]])
O2 = mat([[F(24, 25), F(-7, 25)], [F(7, 25), F(24, 25)]])
A2_EXPECTED = mat([[F(18, 11), F(-7, 11)], [F(7, 39), F(32, 39)]])
PI2_PRIME_EXPECTED = [F(1936, 15625), F(13689, 15625)]

PI3 = [F(1, 9), F(4, 9), F(4, 9)]
S3 = [F(1, 3), F(2, 3), F(2, 3)]
K3 = mat(
    [
        [F(1, 2), F(1, 4), F(1, 8), F(1, 8)],
        [F(1, 8), F(1, 2), F(1, 4), F(1, 8)],
        [F(1, 8), F(1, 8), F(1, 4), F(1, 2)],
    ]
)
S3_SKEW = skew3(F(1, 20), F(-1, 30), F(1, 25))

K3_ANCHORED = mat(
    [
        [F(1, 2), 0, 0, F(1, 2)],
        [0, F(2, 3), 0, F(1, 3)],
        [0, 0, F(3, 4), F(1, 4)],
    ]
)

PI_AP = [F(2, 5), F(3, 5)]
K1_AP = mat([[F(1, 2), F(1, 4), F(1, 4)], [F(1, 6), F(1, 3), F(1, 2)]])
K2_AP = mat([[F(3, 5), F(2, 5)], [F(1, 4), F(3, 4)]])
A_AP = mat([[F(11, 10), F(-1, 10)], [F(1, 20), F(19, 20)]])


# ---------------------------------------------------------------------------
# certificate sections
# ---------------------------------------------------------------------------


def section_A_k2():
    out = {}
    pip, Kp, A = fiber_point(S2, K2, O2)
    out["O_orthogonal"] = is_orthogonal(O2)
    out["A_matches_expected"] = A == A2_EXPECTED
    out["A_rows_sum_to_one"] = all(sum(r) == 1 for r in A)
    out["A_has_negative_entry"] = any(x < 0 for r in A for x in r)
    out["A_not_permutation"] = not is_permutation(A)
    out["pi_prime_matches"] = pip == PI2_PRIME_EXPECTED
    out["weighted_orthogonality"] = mm(mm(tr(A), diag(pip)), A) == diag(PI2)
    out["K_prime_strictly_positive_stochastic"] = is_pos(Kp) and is_row_stochastic(Kp)
    out["one_view_equal"] = one_view(PI2, K2) == one_view(pip, Kp)
    out["two_view_equal"] = two_view(PI2, K2) == two_view(pip, Kp)
    T3a, T3b = three_view(PI2, K2), three_view(pip, Kp)
    out["three_view_differ"] = T3a != T3b
    out["three_view_000"] = (str(T3a[0][0][0]), str(T3b[0][0][0]))
    # converse direction of Theorem A: recover A from K' and O from A
    A_rec = gauge_from_factorizations(K2, Kp)
    u = [x for x in (O2[0][0] * S2[0] + O2[0][1] * S2[1], O2[1][0] * S2[0] + O2[1][1] * S2[1])]
    O_rec = mm(mm(diag(u), A_rec), diag([1 / x for x in S2]))
    out["converse_recovers_A_and_O"] = A_rec == A and O_rec == O2
    # Bayes factor between the two fiber points: exactly 1 on every two-view dataset
    out["two_view_BF_identically_one"] = two_view(PI2, K2) == two_view(pip, Kp)
    kl = 0.0
    n = len(K2[0])
    for a, b, c in product(range(n), repeat=3):
        p, r = float(T3a[a][b][c]), float(T3b[a][b][c])
        kl += p * math.log(p / r)
    out["three_view_KL_per_triple_nats"] = round(kl, 9)
    out["three_view_KL_positive"] = kl > 0
    out["T"] = [[str(x) for x in r] for r in two_view(PI2, K2)]
    out["K_prime"] = [[str(x) for x in r] for r in Kp]
    return out


def section_A_k3():
    out = {}
    O = cayley(S3_SKEW)
    out["rank_K"] = rank(K3)
    out["O_orthogonal"] = is_orthogonal(O)
    res = fiber_point(S3, K3, O)
    out["admissible"] = res is not None
    pip, Kp, A = res
    out["A_has_negative_entry"] = any(x < 0 for r in A for x in r)
    out["A_rows_sum_to_one"] = all(sum(r) == 1 for r in A)
    out["K_prime_strictly_positive_stochastic"] = is_pos(Kp) and is_row_stochastic(Kp)
    out["pi_prime"] = [str(x) for x in pip]
    out["pi_prime_differs"] = pip != PI3
    out["two_view_equal"] = two_view(PI3, K3) == two_view(pip, Kp)
    out["three_view_differ"] = three_view(PI3, K3) != three_view(pip, Kp)
    out["converse_recovers_A"] = gauge_from_factorizations(K3, Kp) == A
    # local dimension 3 = k(k-1)/2: each one-parameter skew direction is admissible near I
    dirs = [skew3(F(1, 100), 0, 0), skew3(0, F(1, 100), 0), skew3(0, 0, F(1, 100))]
    out["all_three_skew_directions_admissible"] = all(
        fiber_point(S3, K3, cayley([[sg * x for x in r] for r in D])) is not None for D in dirs for sg in (1, -1)
    )
    return out


def section_A_prime():
    out = {}
    T = two_view(PI_AP, K1_AP, K2_AP)
    A = A_AP
    pip = mv(tr(inv(A)), PI_AP)  # pi' = A^{-T} pi
    B = mm(mm(diag([1 / x for x in pip]), tr(inv(A))), diag(PI_AP))
    K1p, K2p = mm(A, K1_AP), mm(B, K2_AP)
    out["K1_ne_K2"] = K1_AP != K2_AP
    out["A_rows_sum_to_one"] = all(sum(r) == 1 for r in A)
    out["B_rows_sum_to_one"] = all(sum(r) == 1 for r in B)
    out["A_has_negative_entry"] = any(x < 0 for r in A for x in r)
    out["B_ne_A"] = B != A
    out["pi_prime_positive"] = all(x > 0 for x in pip)
    out["K1p_K2p_stochastic"] = is_row_stochastic(K1p) and is_row_stochastic(K2p)
    out["cross_view_equal"] = two_view(pip, K1p, K2p) == T
    out["identity_AtDB_eq_Dpi"] = mm(mm(tr(A), diag(pip)), B) == diag(PI_AP)
    out["pi_prime"] = [str(x) for x in pip]
    out["B"] = [[str(x) for x in r] for r in B]
    # (k^2 - k) = 2 dimensional local family: grid of A = I + E with E 1 = 0
    ok = 0
    tot = 0
    for e1, e2 in product([F(j, 100) for j in range(-3, 4)], repeat=2):
        Ae = mat([[1 + e1, -e1], [e2, 1 - e2]])
        pe = mv(tr(inv(Ae)), PI_AP)
        Be = mm(mm(diag([1 / x for x in pe]), tr(inv(Ae))), diag(PI_AP))
        tot += 1
        if all(x > 0 for x in pe) and is_row_stochastic(mm(Ae, K1_AP)) and is_row_stochastic(mm(Be, K2_AP)):
            if two_view(pe, mm(Ae, K1_AP), mm(Be, K2_AP)) == T:
                ok += 1
    out["two_param_grid_admissible"] = f"{ok}/{tot}"
    # product-gauge rigidity: nonnegative row-stochastic A and forced B >= 0 only for permutations
    grid = [F(j, 4) for j in range(5)]
    survivors = []
    for a, b in product(grid, repeat=2):
        Ag = mat([[a, 1 - a], [b, 1 - b]])
        if det(Ag) == 0:
            continue
        pg = mv(tr(inv(Ag)), PI_AP)
        if any(x <= 0 for x in pg):
            continue
        Bg = mm(mm(diag([1 / x for x in pg]), tr(inv(Ag))), diag(PI_AP))
        if is_nonneg(Bg):
            survivors.append((is_permutation(Ag), Bg == Ag))
    out["product_rigidity_survivors"] = survivors
    out["product_rigidity_only_same_permutation"] = all(p and e for p, e in survivors) and len(survivors) == 2
    return out


def section_B_k2():
    out = {}
    q = one_view(PI2, K2)
    T = two_view(PI2, K2)
    # true labeling: latent 0 is favoured by the outcome minimizing K[1][x]/K[0][x]
    x_star = min(range(3), key=lambda x: K2[1][x] / K2[0][x])
    L, U, y_star = identified_interval_k2(q, T, x_star)
    out["x_star_y_star"] = (x_star, y_star)
    out["L"] = str(L)
    out["U"] = str(U)
    out["L_float"] = round(float(L), 6)
    out["U_float"] = round(float(U), 6)
    out["L_expected"] = L == F(144, 1825)
    out["U_expected"] = U == F(1849, 2425)
    out["true_pi1_inside"] = L < PI2[0] < U
    out["witness_pi1_prime_inside"] = L < PI2_PRIME_EXPECTED[0] < U
    # endpoints are attained by exact rational anchor models
    pU, KU = anchor_model(q, T, x_star)
    pL_rev, KL_rev = anchor_model(q, T, y_star)  # y_star anchors the other latent
    pL, KL = [pL_rev[1], pL_rev[0]], [KL_rev[1], KL_rev[0]]
    out["U_model_valid"] = is_row_stochastic(KU) and two_view(pU, KU) == T and pU[0] == U and KU[1][x_star] == 0
    out["L_model_valid"] = is_row_stochastic(KL) and two_view(pL, KL) == T and pL[0] == L and KL[0][y_star] == 0
    out["U_model_K"] = [[str(x) for x in r] for r in KU]
    out["L_model_K"] = [[str(x) for x in r] for r in KL]
    # rational tan(theta/2) grid over [-1/2, 1/2]
    ts = [F(j, 200) for j in range(-100, 101)]
    adm = []
    for t in ts:
        r = fiber_point(S2, K2, rot2(t))
        if r is not None:
            pip, Kp, A = r
            assert two_view(pip, Kp) == T
            adm.append((t, pip[0]))
    idx = [ts.index(t) for t, _ in adm]
    out["grid_points"] = len(ts)
    out["grid_admissible"] = len(adm)
    out["admissible_grid_contiguous"] = idx == list(range(idx[0], idx[-1] + 1))
    out["admissible_contains_zero"] = any(t == 0 for t, _ in adm)
    out["all_admissible_in_[L,U]"] = all(L <= p <= U for _, p in adm)
    out["pi1_strictly_decreasing_in_t"] = all(adm[i][1] > adm[i + 1][1] for i in range(len(adm) - 1))
    out["inner_range_from_grid"] = (round(float(adm[-1][1]), 6), round(float(adm[0][1]), 6))
    # exact probes on both sides of each float-located arc endpoint
    th_lo, th_hi = float_arc_k2(S2, K2)
    probes = {}
    for name, th in (("lo", th_lo), ("hi", th_hi)):
        t0 = F(math.tan(th / 2)).limit_denominator(10**9)
        eps = F(1, 10**6)
        inside = t0 + eps if name == "lo" else t0 - eps
        outside = t0 - eps if name == "lo" else t0 + eps
        probes[name] = (fiber_point(S2, K2, rot2(inside)) is not None, fiber_point(S2, K2, rot2(outside)) is None)
    out["endpoint_probes_inside_ok_outside_fail"] = probes
    out["arc_theta_float"] = (round(th_lo, 9), round(th_hi, 9))
    # floor ell equals min(L, 1-U) for k = 2
    ell = weight_floor(S2, K2)
    out["ell"] = str(ell)
    out["ell_equals_min_L_1mU"] = ell == min(L, 1 - U)
    # label-free identified set
    out["label_free_set"] = f"[{L},{U}] union [{1 - U},{1 - L}]"
    return out


def section_B_anchor_cases():
    out = {}
    # both latents anchored -> point
    pi = [F(9, 25), F(16, 25)]
    K = mat([[F(1, 2), F(1, 2), 0], [0, F(1, 3), F(2, 3)]])
    q, T = one_view(pi, K), two_view(pi, K)
    L, U, _ = identified_interval_k2(q, T, 0)
    out["two_anchors_point"] = L == U == pi[0]
    out["two_anchors_no_small_rotation"] = all(
        fiber_point(S2, K, rot2(t)) is None for t in [F(j, 1000) for j in range(-20, 21) if j != 0]
    )
    # one anchor only (outcome 2 anchors latent 1) -> one-sided interval [pi1, U] with U > pi1
    K1a = mat([[F(1, 2), F(1, 2), 0], [F(1, 4), F(1, 4), F(1, 2)]])
    q, T = one_view(pi, K1a), two_view(pi, K1a)
    x_star = 0  # ratio K[1]/K[0] minimal (tie with 1; same column angle)
    L, U, _ = identified_interval_k2(q, T, x_star)
    out["one_anchor_interval"] = (str(L), str(U))
    out["one_anchor_L_is_pi1_and_U_gt_pi1"] = L == pi[0] and U > pi[0]
    # PR #68 audit finding 3 pair is exactly the lower-endpoint anchor model of a symmetric channel
    piS = [F(1, 2), F(1, 2)]
    KS = mat([[F(3, 4), F(1, 4)], [F(1, 4), F(3, 4)]])
    qS, TS = one_view(piS, KS), two_view(piS, KS)
    LS, US, yS = identified_interval_k2(qS, TS, 0)
    pR, KR = anchor_model(qS, TS, yS)
    pr68_pi, pr68_K = [F(1, 5), F(4, 5)], mat([[1, 0], [F(3, 8), F(5, 8)]])
    out["pr68_interval"] = (str(LS), str(US))
    out["pr68_pair_is_L_endpoint"] = (
        (LS, US) == (F(1, 5), F(4, 5))
        and [pR[1], pR[0]] == pr68_pi
        and [KR[1], KR[0]] == pr68_K
        and two_view(pr68_pi, pr68_K) == TS
    )
    return out


def section_C():
    out = {}
    # (i) anchored k = 3: no non-identity Cayley rotation is admissible on a grid
    grid = [F(j, 40) for j in range(-4, 5)]
    n_adm = 0
    n_tot = 0
    for a, b, c in product(grid, repeat=3):
        if a == b == c == 0:
            continue
        n_tot += 1
        if fiber_point(S3, K3_ANCHORED, cayley(skew3(a, b, c))) is not None:
            n_adm += 1
    out["anchored_k3_nonidentity_admissible"] = f"{n_adm}/{n_tot}"
    out["anchored_identity_admissible"] = fiber_point(S3, K3_ANCHORED, eye(3)) is not None
    P = mat([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    rp = fiber_point(S3, K3_ANCHORED, P)
    out["anchored_permutation_admissible_and_relabels"] = rp is not None and rp[2] == P
    q, T = one_view(PI3, K3_ANCHORED), two_view(PI3, K3_ANCHORED)
    out["anchor_formula_recovers_pi"] = [q[x] * q[x] / T[x][x] for x in range(3)] == PI3
    # (ii) three-view separation of the k = 2 fiber witness is recorded in section_A_k2
    return out


def _grid_components(points):
    """Connected components of a set of integer grid indices (axis neighbours)."""
    remaining = set(points)
    components = []
    while remaining:
        start = remaining.pop()
        stack, component = [start], {start}
        while stack:
            p = stack.pop()
            for axis in range(len(p)):
                for step in (-1, 1):
                    nb = tuple(p[i] + (step if i == axis else 0) for i in range(len(p)))
                    if nb in remaining:
                        remaining.remove(nb)
                        component.add(nb)
                        stack.append(nb)
        components.append(component)
    return components


def section_k3_inner_outer():
    out = {}
    grid = [F(j, 10) for j in range(-10, 11)]
    vals = []
    floor = weight_floor(S3, K3)
    viol = 0
    T = two_view(PI3, K3)
    reproduces = True
    admissible = {}
    for (ia, a), (ib, b), (ic, c) in product(enumerate(grid), repeat=3):
        r = fiber_point(S3, K3, cayley(skew3(a, b, c)))
        if r is None:
            continue
        pip, Kp, _ = r
        reproduces = reproduces and two_view(pip, Kp) == T and is_row_stochastic(Kp)
        admissible[(ia, ib, ic)] = pip[0]
        vals.append(pip[0])
        if any(p < floor for p in pip):
            viol += 1
    components = _grid_components(admissible)
    identity = next(comp for comp in components if (10, 10, 10) in comp)
    identity_vals = [admissible[p] for p in identity]
    out["grid_points"] = len(grid) ** 3
    out["grid_admissible"] = len(vals)
    out["grid_reproduces_T"] = reproduces
    # Label-free values: the maximum is attained near a cyclic relabeling, so
    # "first weight" is some latent's weight, and the grid values are not an interval.
    out["exact_first_weights_min_max_label_free"] = (str(min(vals)), str(max(vals)))
    out["exact_first_weights_min_max_float"] = (round(float(min(vals)), 6), round(float(max(vals)), 6))
    out["grid_adjacency_components"] = len(components)
    out["identity_component_first_weight_range_float"] = (round(float(min(identity_vals)), 6), round(float(max(identity_vals)), 6))
    out["ell_floor"] = str(floor)
    out["ell_floor_float"] = round(float(floor), 6)
    out["outer_pi_i_range"] = (round(float(floor), 6), round(float(1 - 2 * floor), 6))
    out["floor_violations_on_grid"] = viol
    out["ell_le_min_true_pi"] = floor <= min(PI3)
    ell, nu, rays, obtuse = floor_sharpness_k3(S3, K3)
    out["floor_ray_nu"] = [str(x) for x in nu]
    out["floor_slice_feasible_rays"] = len(rays)
    out["floor_attained_label_free"] = obtuse
    out["T_rank"] = rank(T)
    return out


# No-anchor channel that two views still point-identify (sufficiently scattered;
# Huang-Sidiropoulos-Swami 2014). With pi uniform, s is proportional to 1, so the
# fiber condition O D_s K >= 0 is O K >= 0.
K_SCATTERED = mat(
    [
        [0, 0, F(1, 8), F(3, 8), F(1, 8), F(3, 8)],
        [F(1, 8), F(3, 8), 0, 0, F(3, 8), F(1, 8)],
        [F(3, 8), F(1, 8), F(3, 8), F(1, 8), 0, 0],
    ]
)


def dual_cone_extreme_rays_3d(cols):
    """All extreme rays of C* = {y : y.c >= 0 for every column c} in R^3.

    For a pointed full-dimensional polyhedral cone in R^3 every extreme ray lies on
    two independent facet planes, so it is +-(c_i x c_j) for some pair; keep the
    feasible ones, normalized to a primitive representative.
    """
    rays = set()
    for ci, cj in combinations(cols, 2):
        d = cross3(ci, cj)
        if not any(d):
            continue
        for sg in (1, -1):
            r = [sg * x for x in d]
            if all(sum(a * b for a, b in zip(r, c)) >= 0 for c in cols):
                scale = max(abs(x) for x in r)
                rays.add(tuple(x / scale for x in r))
    return sorted(rays)


def section_no_anchor_scattered():
    out = {}
    K = K_SCATTERED
    cols = [list(c) for c in tr(K)]
    out["rank_K"] = rank(K)
    out["row_stochastic"] = is_row_stochastic(K)
    out["no_anchor_column"] = all(sum(1 for x in c if x > 0) == 2 for c in cols)
    rays = dual_cone_extreme_rays_3d(cols)
    out["dual_cone_extreme_rays"] = [[str(x) for x in r] for r in rays]
    coordinate = {tuple(F(int(i == j)) for i in range(3)) for j in range(3)}
    # f(y) = y.1 - |y| >= 0 on every extreme ray, with equality only on coordinate rays.
    def margin_ok(r):
        total = sum(r)
        norm2 = sum(x * x for x in r)
        if r in coordinate:
            return total > 0 and total * total == norm2
        return total > 0 and total * total > norm2

    out["rays_satisfy_sum_ge_norm_strict_off_axes"] = all(margin_ok(r) for r in rays) and coordinate <= set(rays)
    grid = [F(j, 20) for j in range(-6, 7)]
    nonperm = 0
    total = 0
    for a, b, c in product(grid, repeat=3):
        if a == b == c == 0:
            continue
        total += 1
        O = cayley(skew3(a, b, c))
        if is_nonneg(mm(O, K)) and not is_permutation(O):
            nonperm += 1
    out["cayley_grid_nonpermutation_admissible"] = f"{nonperm}/{total}"
    return out


# Necessary condition: if supp(K_j) is contained in supp(K_i), a small rotation in
# the (i, j) plane stays in G(W) and changes the prior.
PI_NESTED = [F(9, 25), F(16, 25)]
S_NESTED = [F(3, 5), F(4, 5)]
K_NESTED = mat([[F(1, 2), F(1, 4), F(1, 4)], [F(1, 2), F(1, 2), 0]])


def nested_support_rotation(s, K, i, j, t):
    """Rotate rows (i, j) of D_s K by the rational angle with tan(theta/2) = t:
    new_i = cos W_i - sin W_j, new_j = sin W_i + cos W_j."""
    k = len(K)
    c, sn = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    O = eye(k)
    O[i][i], O[i][j], O[j][i], O[j][j] = c, -sn, sn, c
    return O, fiber_point(s, K, O)


def section_incomparable_supports():
    out = {}
    O, r = nested_support_rotation(S_NESTED, K_NESTED, 0, 1, F(1, 50))
    out["nested_support_row1_in_row0"] = all(K_NESTED[0][x] > 0 for x in range(3) if K_NESTED[1][x] > 0)
    out["small_rotation_admissible"] = r is not None
    if r is not None:
        pip, Kp, A = r
        out["prior_changes"] = pip != PI_NESTED and pip != PI_NESTED[::-1]
        out["two_view_equal"] = two_view(pip, Kp) == two_view(PI_NESTED, K_NESTED)
        out["pi_prime"] = [str(x) for x in pip]
    # GK remark: the upper endpoint jumps when an outcome probability tends to zero.
    jumps = {}
    for eps in (F(1, 100), F(1, 1000), F(0)):
        K = mat([[F(3, 4) - eps, F(1, 4), eps], [F(1, 4), F(3, 4), F(0)]])
        pi = [F(1, 2), F(1, 2)]
        q, T = one_view(pi, K), two_view(pi, K)
        x, y = extreme_pair(q, T)
        # U is the endpoint for the latent favoured by the outcome of the
        # extreme pair with the smaller likelihood ratio K_1x / K_0x (latent 0).
        x_star = min((x, y), key=lambda z: K[1][z] / K[0][z])
        lower, upper, _ = identified_interval_k2(q, T, x_star)
        jumps[str(eps)] = str(upper)
    out["upper_endpoint_by_eps"] = jumps
    out["upper_endpoint_jumps_at_zero"] = jumps["1/100"] == jumps["1/1000"] == "1/2" and jumps["0"] == "4/5"
    return out


def run():
    sections = {
        "A_k2_witness": section_A_k2(),
        "A_k3_witness": section_A_k3(),
        "A_prime_different_channels": section_A_prime(),
        "B_k2_identified_interval": section_B_k2(),
        "B_anchor_cases": section_B_anchor_cases(),
        "C_ladder": section_C(),
        "k3_inner_outer": section_k3_inner_outer(),
        "no_anchor_scattered": section_no_anchor_scattered(),
        "incomparable_supports": section_incomparable_supports(),
    }
    return sections


REQUIRED_TRUE = {
    "A_k2_witness": [
        "O_orthogonal", "A_matches_expected", "A_rows_sum_to_one", "A_has_negative_entry", "A_not_permutation",
        "pi_prime_matches", "weighted_orthogonality", "K_prime_strictly_positive_stochastic", "one_view_equal",
        "two_view_equal", "three_view_differ", "converse_recovers_A_and_O", "two_view_BF_identically_one",
        "three_view_KL_positive",
    ],
    "A_k3_witness": [
        "O_orthogonal", "admissible", "A_has_negative_entry", "A_rows_sum_to_one",
        "K_prime_strictly_positive_stochastic", "pi_prime_differs", "two_view_equal", "three_view_differ",
        "converse_recovers_A", "all_three_skew_directions_admissible",
    ],
    "A_prime_different_channels": [
        "K1_ne_K2", "A_rows_sum_to_one", "B_rows_sum_to_one", "A_has_negative_entry", "B_ne_A",
        "pi_prime_positive", "K1p_K2p_stochastic", "cross_view_equal", "identity_AtDB_eq_Dpi",
        "product_rigidity_only_same_permutation",
    ],
    "B_k2_identified_interval": [
        "L_expected", "U_expected", "true_pi1_inside", "witness_pi1_prime_inside", "U_model_valid", "L_model_valid",
        "admissible_grid_contiguous", "admissible_contains_zero", "all_admissible_in_[L,U]",
        "pi1_strictly_decreasing_in_t", "ell_equals_min_L_1mU",
    ],
    "B_anchor_cases": ["two_anchors_point", "two_anchors_no_small_rotation", "one_anchor_L_is_pi1_and_U_gt_pi1", "pr68_pair_is_L_endpoint"],
    "C_ladder": ["anchored_identity_admissible", "anchored_permutation_admissible_and_relabels", "anchor_formula_recovers_pi"],
    "k3_inner_outer": ["ell_le_min_true_pi", "floor_attained_label_free", "grid_reproduces_T"],
    "no_anchor_scattered": ["row_stochastic", "no_anchor_column", "rays_satisfy_sum_ge_norm_strict_off_axes"],
    "incomparable_supports": ["nested_support_row1_in_row0", "small_rotation_admissible", "prior_changes", "two_view_equal", "upper_endpoint_jumps_at_zero"],
}


def verdict(sections):
    fails = []
    for sec, keys in REQUIRED_TRUE.items():
        for k in keys:
            if sections[sec][k] is not True:
                fails.append(f"{sec}.{k}")
    b = sections["B_k2_identified_interval"]["endpoint_probes_inside_ok_outside_fail"]
    if not all(all(v) for v in b.values()):
        fails.append("B_k2_identified_interval.endpoint_probes")
    if sections["C_ladder"]["anchored_k3_nonidentity_admissible"].split("/")[0] != "0":
        fails.append("C_ladder.anchored_k3_nonidentity_admissible")
    if sections["k3_inner_outer"]["floor_violations_on_grid"] != 0:
        fails.append("k3_inner_outer.floor_violations_on_grid")
    if sections["A_prime_different_channels"]["two_param_grid_admissible"] != "49/49":
        fails.append("A_prime_different_channels.two_param_grid_admissible")
    if sections["no_anchor_scattered"]["cayley_grid_nonpermutation_admissible"].split("/")[0] != "0":
        fails.append("no_anchor_scattered.cayley_grid_nonpermutation_admissible")
    if sections["no_anchor_scattered"]["rank_K"] != 3:
        fails.append("no_anchor_scattered.rank_K")
    return fails


def receipt_lines():
    sections = run()
    lines = ["receipt: two-view-orthogonal-fiber-identified-set", "arithmetic: fractions.Fraction (exact); floats only for endpoint location and KL report"]
    for sec, d in sections.items():
        lines.append(f"[{sec}]")
        for k, v in d.items():
            lines.append(f"  {k} = {v}")
    fails = verdict(sections)
    body = "\n".join(lines)
    lines.append(f"payload_sha256 = {hashlib.sha256(body.encode()).hexdigest()}")
    lines.append("VERDICT = " + ("PASS" if not fails else "FAIL " + ", ".join(fails)))
    return lines, fails


def receipt_text() -> str:
    lines, _ = receipt_lines()
    return "\n".join(lines) + "\n"


def main():
    lines, fails = receipt_lines()
    print("\n".join(lines))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
