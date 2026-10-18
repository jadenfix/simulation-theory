"""Exact certificates for the random-bit price of shared codebook randomness.

Standard library only (fractions, itertools, math).  Every value that the
receipt reports as exact is a Fraction computed without floating point.  The
only floating point quantity is the Shannon entropy used in the Knuth-Yao
sandwich H(w) <= E[T] < H(w) + 2, and that comparison is reported with its
numerical margin.

Derivation: docs/random-bit-price-shared-randomness.md (claims ST-T310 to
ST-T313, ST-M90 to ST-M93, ST-F61). ``python -m simtheory.random_bit_price``
prints the receipt committed as receipts/random-bit-price-shared-randomness.txt;
the committed instances are always cross-checked against the repository's own
exact solvers.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

Matrix = Tuple[Tuple[Fraction, ...], ...]
Vector = Tuple[Fraction, ...]

# ---------------------------------------------------------------------------
# Committed instances (rows = adversary scenarios / models, columns = codebooks)
# ---------------------------------------------------------------------------

F = Fraction


def _m(rows) -> Matrix:
    return tuple(tuple(F(x) for x in row) for row in rows)


# K3 public-randomness game: three point-mass models, code c gives the one-bit
# codeword to state c, so A[m][c] = 1 if m == c else 2 (ST-M26, ST-M45, ST-M47).
K3 = _m([[1, 2, 2], [2, 1, 2], [2, 2, 1]])

INSTANCES: Dict[str, Matrix] = {
    # ST-M21 minimax game (docs/finite-prior-robust-coding.md section 11)
    "ST-M21 minimax": _m([["6/5", "19/10"], ["19/10", "6/5"]]),
    # ST-M21 regret game
    "ST-M21 regret": _m([[0, "7/10"], ["7/10", 0]]),
    # k4_nonoracle_minimax_example minimax game
    "K4 nonoracle minimax": _m([["3/2", 2, "21/10"], ["21/10", 2, "3/2"]]),
    # ST-M26: full-TV K3 (radius one, uniform nominal) == the K3 game
    "ST-M26 full-TV K3": K3,
    # ST-M45: K3 regret game, oracle value one, so A - 1
    "ST-M45 K3 regret": _m([[0, 1, 1], [1, 0, 1], [1, 1, 0]]),
    # ST-M27: skew K3, nominal (4/5,1/10,1/10), TV radius 2/5, 7/15, 1/2
    "ST-M27 radius 2/5": _m([
        ["3/2", "8/5", "19/10"], ["19/10", "8/5", "3/2"], ["3/2", "3/2", 2],
        [2, "3/2", "3/2"], [2, 1, 2]]),
    "ST-M27 radius 7/15": _m([
        ["43/30", "5/3", "19/10"], ["19/10", "5/3", "43/30"],
        ["43/30", "47/30", 2], [2, "47/30", "43/30"], [2, 1, 2]]),
    "ST-M27 radius 1/2": _m([
        ["7/5", "17/10", "19/10"], ["19/10", "17/10", "7/5"],
        ["7/5", "8/5", 2], [2, "8/5", "7/5"], [2, 1, 2]]),
}

# Expected exact values (taken from the committed repository certificates).
EXPECTED_VALUES = {
    "ST-M21 minimax": F(31, 20),
    "ST-M21 regret": F(7, 20),
    "K4 nonoracle minimax": F(9, 5),
    "ST-M26 full-TV K3": F(5, 3),
    "ST-M45 K3 regret": F(2, 3),
    "ST-M27 radius 2/5": F(8, 5),
    "ST-M27 radius 7/15": F(5, 3),
    "ST-M27 radius 1/2": F(5, 3),
}

# ---------------------------------------------------------------------------
# Exact linear algebra
# ---------------------------------------------------------------------------


def solve_square(matrix: List[List[Fraction]], rhs: List[Fraction]) -> Optional[List[Fraction]]:
    """Gauss-Jordan over Q; None when singular."""
    n = len(matrix)
    aug = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        inv = 1 / aug[col][col]
        aug[col] = [x * inv for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [a - factor * b for a, b in zip(aug[r], aug[col])]
    return [aug[i][n] for i in range(n)]


def row_payoffs(A: Matrix, w: Sequence[Fraction]) -> Vector:
    return tuple(sum((a * x for a, x in zip(row, w)), F(0)) for row in A)


def payoff(A: Matrix, w: Sequence[Fraction]) -> Fraction:
    """Worst-scenario expected cost max_r (A w)_r of a public mixture w."""
    return max(row_payoffs(A, w))


# ---------------------------------------------------------------------------
# Exact game value by basis enumeration (independent of the repo solver)
# ---------------------------------------------------------------------------


def solve_game(A: Matrix) -> Tuple[Fraction, Vector]:
    """Return (V*, w*) for min_{w in simplex} max_r (A w)_r.

    Variables (w_1..w_n, v); constraints w_c >= 0 and (A w)_r <= v; equality
    sum w = 1.  A bounded LP attains its optimum at a basic feasible solution,
    i.e. with n of the n + R inequalities tight.  Every such basis is solved
    exactly and checked for feasibility.  Among optimal bases the one with the
    smallest support is returned.
    """
    R, n = len(A), len(A[0])
    best: Optional[Tuple[Fraction, int, Vector]] = None
    for tight in combinations(range(n + R), n):
        mat: List[List[Fraction]] = []
        rhs: List[Fraction] = []
        for t in tight:
            if t < n:
                mat.append([F(1) if c == t else F(0) for c in range(n)] + [F(0)])
            else:
                mat.append(list(A[t - n]) + [F(-1)])
            rhs.append(F(0))
        mat.append([F(1)] * n + [F(0)])
        rhs.append(F(1))
        sol = solve_square(mat, rhs)
        if sol is None:
            continue
        w, v = tuple(sol[:n]), sol[n]
        if any(x < 0 for x in w) or payoff(A, w) > v:
            continue
        key = (v, sum(1 for x in w if x > 0), w)
        if best is None or key[:2] < best[:2]:
            best = key
    assert best is not None
    return best[0], best[2]


def dual_certificate(A: Matrix, V: Fraction) -> Vector:
    """A least-favourable scenario mixture lam with min_c (lam^T A)_c = V."""
    R, n = len(A), len(A[0])
    for size in range(1, min(R, n) + 1):
        for rows in combinations(range(R), size):
            for cols in combinations(range(n), size):
                mat = [[A[r][c] for r in rows] for c in cols]
                mat.append([F(1)] * size)
                rhs = [V] * size + [F(1)]
                # size + 1 equations in size unknowns: drop one column equation
                # and verify it afterwards.
                sol = solve_square(mat[1:], rhs[1:])
                if sol is None or any(x < 0 for x in sol):
                    continue
                lam = [F(0)] * R
                for r, x in zip(rows, sol):
                    lam[r] = x
                col_costs = [sum((lam[r] * A[r][c] for r in range(R)), F(0)) for c in range(n)]
                if min(col_costs) == V:
                    return tuple(lam)
    raise AssertionError("no dual certificate found")


def optimal_set_vertices(A: Matrix, V: Fraction) -> List[Vector]:
    """Vertices of O = {w in simplex : A w <= V}."""
    R, n = len(A), len(A[0])
    verts = set()
    for tight in combinations(range(n + R), n - 1):
        mat: List[List[Fraction]] = []
        rhs: List[Fraction] = []
        for t in tight:
            if t < n:
                mat.append([F(1) if c == t else F(0) for c in range(n)])
                rhs.append(F(0))
            else:
                mat.append(list(A[t - n]))
                rhs.append(V)
        mat.append([F(1)] * n)
        rhs.append(F(1))
        sol = solve_square(mat, rhs)
        if sol is None:
            continue
        w = tuple(sol)
        if all(x >= 0 for x in w) and payoff(A, w) <= V:
            verts.add(w)
    return sorted(verts)


# ---------------------------------------------------------------------------
# Does a rational polytope contain a point of Z[1/L]^n ?
# ---------------------------------------------------------------------------


def _lcm(a: int, b: int) -> int:
    return a * b // math.gcd(a, b)


def _strip(d: int, L: int) -> int:
    """Largest divisor of d coprime to L."""
    g = math.gcd(d, L)
    while g > 1:
        while d % g == 0:
            d //= g
        g = math.gcd(d, L)
    return d


def in_ring(x: Fraction, L: int) -> bool:
    """x in Z[1/L]."""
    return _strip(x.denominator, L) == 1


def polytope_meets_ring(vertices: Sequence[Vector], L: int = 2,
                        max_states: int = 2_000_000) -> bool:
    """Decide whether conv(vertices) contains a point of Z[1/L]^n.

    Lemma (L >= 2): a rational polytope P meets Z[1/L]^n iff its affine hull
    does (Z[1/L] points of a rational affine space are dense in it once one
    exists, and relint P is open in aff P). For L = 1 density fails, so only a
    single point is decided directly.  The affine hull is parametrised by pivot
    coordinates J as x_J = z, x_{J^c} = c + G z.  With m the part of the common
    denominator of (c, G) coprime to L, Z[1/L]/m Z[1/L] = Z/m, and z ranges over
    all residues, so the question is a finite congruence search over (Z/m)^k.
    """
    v0 = vertices[0]
    n = len(v0)
    if L < 2:
        if len(vertices) > 1:
            raise ValueError("Lemma 2a needs L >= 2; L = 1 is decided only for a single point")
        return all(x.denominator == 1 for x in v0)
    dirs = [[a - b for a, b in zip(v, v0)] for v in vertices[1:]]
    # row-reduce directions to reduced echelon form
    basis: List[List[Fraction]] = []
    pivots: List[int] = []
    for d in dirs:
        d = list(d)
        for b, p in zip(basis, pivots):
            if d[p] != 0:
                f = d[p]
                d = [x - f * y for x, y in zip(d, b)]
        p = next((i for i, x in enumerate(d) if x != 0), None)
        if p is None:
            continue
        inv = 1 / d[p]
        d = [x * inv for x in d]
        new_basis = []
        for b in basis:
            if b[p] != 0:
                f = b[p]
                b = [x - f * y for x, y in zip(b, d)]
            new_basis.append(b)
        basis = new_basis + [d]
        pivots.append(p)
    k = len(basis)
    # x = v0 + sum_i t_i basis_i ; x_{p_i} = v0_{p_i} + t_i  ->  t_i = z_i - v0_{p_i}
    free = [i for i in range(n) if i not in pivots]
    c = [v0[j] - sum((basis[i][j] * v0[pivots[i]] for i in range(k)), F(0)) for j in free]
    G = [[basis[i][j] for i in range(k)] for j in free]
    entries = c + [g for row in G for g in row]
    den = reduce(_lcm, (e.denominator for e in entries), 1)
    m = _strip(den, L)
    if m == 1:
        return True
    if m ** k > max_states:
        raise ValueError("congruence search too large")

    def red(x: Fraction) -> int:
        # x * m has denominator coprime to m; reduce into Z/m
        y = x * m
        return (y.numerator * pow(y.denominator, -1, m)) % m

    cr = [red(e) for e in c]
    Gr = [[red(g) for g in row] for row in G]
    # condition: m*(c + G z) == 0 mod m, i.e. cr + (m*G) z == 0 in Z/m where
    # z is the residue of the free Z[1/L] parameter.  (m*G) reduced is Gr.
    for z in product(range(m), repeat=k):
        if all((cr[j] + sum(Gr[j][i] * z[i] for i in range(k))) % m == 0
               for j in range(len(free))):
            return True
    return False


# ---------------------------------------------------------------------------
# Fixed-budget value on the grid (1/N) Z^n  (N = 2^b or L^t)
# ---------------------------------------------------------------------------


def compositions(total: int, parts: int) -> Iterator[Tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def common_denominator(A: Matrix) -> int:
    return reduce(_lcm, (a.denominator for row in A for a in row), 1)


def grid_value(A: Matrix, N: int) -> Tuple[Fraction, Tuple[int, ...]]:
    """Exhaustive V_N = min over integer k >= 0, sum k = N of max_r (A k)_r / N."""
    D = common_denominator(A)
    Ai = [[int(a * D) for a in row] for row in A]
    best = None
    best_k: Tuple[int, ...] = ()
    for k in compositions(N, len(A[0])):
        val = max(sum(a * x for a, x in zip(row, k)) for row in Ai)
        if best is None or val < best:
            best, best_k = val, k
    return F(best, N * D), best_k


def k3_grid_value_fast(N: int) -> Fraction:
    """Exhaustive K3 value with the reduction payoff = 2 - min_c w_c."""
    best_min = -1
    for k0 in range(N + 1):
        for k1 in range(N - k0 + 1):
            mn = min(k0, k1, N - k0 - k1)
            if mn > best_min:
                best_min = mn
    return 2 - F(best_min, N)


def rounding_gap_bound(A: Matrix, w: Vector, N: int) -> Fraction:
    """Theorem 2 upper bound: Delta_S * floor(s/2) / N, S = supp w."""
    S = [c for c, x in enumerate(w) if x > 0]
    delta = max(max(row[c] for c in S) - min(row[c] for c in S) for row in A)
    return delta * (len(S) // 2) / N


def largest_remainder_round(w: Vector, N: int) -> Tuple[Fraction, ...]:
    base = [math.floor(x * N) for x in w]
    deficit = N - sum(base)
    order = sorted(range(len(w)), key=lambda c: (-(w[c] * N - base[c]), c))
    for c in order[:deficit]:
        base[c] += 1
    return tuple(F(k, N) for k in base)


# ---------------------------------------------------------------------------
# Knuth-Yao exact expected bit count
# ---------------------------------------------------------------------------


def frac_part(x: Fraction) -> Fraction:
    return x - math.floor(x)


def ky_component(x: Fraction) -> Fraction:
    """sum_{t>=0} frac(2^t x) 2^{-t}, exactly, via the eventually periodic orbit.

    The doubling map on residues p/q mod 1 is eventually periodic; with
    preperiod mu and period pi the series is the finite head plus a geometric
    tail with ratio 2^{-pi}.  Equals nu(x) = sum_k k x_k 2^{-k} for the binary
    digits x_k of x in [0,1) (terminating expansion when x is dyadic).
    """
    y = frac_part(x)
    seen: Dict[Fraction, int] = {}
    orbit: List[Fraction] = []
    t = 0
    while y not in seen:
        seen[y] = t
        orbit.append(y)
        y = frac_part(2 * y)
        t += 1
    mu = seen[y]
    period = t - mu
    head = sum((orbit[s] / F(2) ** s for s in range(mu)), F(0))
    cycle = sum((orbit[s] / F(2) ** s for s in range(mu, t)), F(0))
    return head + cycle / (1 - F(1, 2 ** period))


def ky_expected_bits(w: Sequence[Fraction]) -> Fraction:
    assert sum(w) == 1 and all(x >= 0 for x in w)
    return sum((ky_component(x) for x in w), F(0))


def nu_partial(x: Fraction, K: int) -> Fraction:
    """sum_{k=1}^K k x_k 2^{-k} with binary digits of x in [0,1)."""
    total, y = F(0), frac_part(x)
    for k in range(1, K + 1):
        y *= 2
        bit = 1 if y >= 1 else 0
        y -= bit
        total += F(k * bit, 2 ** k)
    return total


def ddg_undecided(w: Sequence[Fraction], depth: int) -> List[int]:
    """Construct the Knuth-Yao DDG tree level by level.

    U_t = number of undecided nodes at depth t.  At depth t+1 the 2 U_t
    children receive bit_{t+1}(w_c) leaves labelled c for every c; the
    construction is feasible iff 2 U_t >= sum_c bit_{t+1}(w_c), and then
    U_{t+1} = 2 U_t - sum_c bit_{t+1}(w_c).  Returns [U_0, ..., U_depth].
    """
    U = [1 if all(x < 1 for x in w) else 0]
    for t in range(depth):
        leaves = sum(math.floor(x * 2 ** (t + 1)) - 2 * math.floor(x * 2 ** t) for x in w)
        nxt = 2 * U[-1] - leaves
        assert nxt >= 0, "DDG construction infeasible"
        U.append(nxt)
    return U


def sampler_lower_bound_tail(w: Sequence[Fraction], t: int) -> Fraction:
    """Any exact sampler: P(T > t) >= 1 - sum_c floor(2^t w_c)/2^t."""
    return 1 - sum((F(math.floor(x * 2 ** t), 2 ** t) for x in w), F(0))


def entropy_bits(w: Sequence[Fraction]) -> float:
    return -sum(float(x) * math.log2(float(x)) for x in w if x > 0)


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------


def run(verbose: bool = True) -> List[str]:
    out: List[str] = []

    def say(s: str = "") -> None:
        out.append(s)
        if verbose:
            print(s)

    say("random-bit price of shared codebook randomness: exact receipt")
    say("=" * 66)

    # ---------------- Theorem 1: K3 ----------------
    say("\n[T1] K3 public-randomness game, b fair public bits, b = 0..12")
    V, w = solve_game(K3)
    assert V == F(5, 3) and w == (F(1, 3),) * 3
    assert optimal_set_vertices(K3, V) == [(F(1, 3),) * 3]
    for b in range(13):
        N = 2 ** b
        vb = k3_grid_value_fast(N)
        closed = 2 - F(N // 3, N)
        gap = F(N % 3, 3 * N)
        assert vb == closed and vb - F(5, 3) == gap > 0
        if b <= 8:  # independent generic enumeration over all dyadic vectors
            assert grid_value(K3, N)[0] == vb
        assert vb == F(5, 3) + F(1, 3 * 4 ** (b // 2))
        say(f"  b={b:2d}  V_b={str(vb):>12}  V_b-5/3={str(gap):>10}")
    say("  closed form V_b = 2 - floor(2^b/3)/2^b = 5/3 + 1/(3*4^floor(b/2)) verified; gap > 0 for all b <= 12")
    say("  generic all-dyadic-vector enumeration agrees for b <= 8; K3 min-weight reduction enumerated exhaustively for b <= 12")

    # ---------------- Theorem 2: committed instances ----------------
    say("\n[T2] dyadic dichotomy and two-sided gap bounds on committed instances, b = 0..10")
    summary = {}
    curves = {}
    for name, A in INSTANCES.items():
        V, wstar = solve_game(A)
        assert V == EXPECTED_VALUES[name], (name, V)
        lam = dual_certificate(A, V)
        verts = optimal_set_vertices(A, V)
        dyadic = polytope_meets_ring(verts, 2)
        DA, q = common_denominator(A), V.denominator
        prev = None
        hit = None
        for b in range(11):
            N = 2 ** b
            vb, _ = grid_value(A, N)
            assert vb >= V
            if prev is not None:
                assert vb <= prev
            prev = vb
            gap = vb - V
            if gap == 0:
                hit = b if hit is None else hit
            else:
                assert gap >= F(1, DA * q * N), (name, b)
            assert gap <= rounding_gap_bound(A, wstar, N), (name, b)
            wr = largest_remainder_round(wstar, N)
            assert payoff(A, wr) - V <= rounding_gap_bound(A, wstar, N)
        assert (hit is not None) == dyadic, name
        summary[name] = (V, wstar, verts, dyadic, hit)
        curves[name] = [grid_value(A, 2 ** b)[0] - V for b in range(11)]
        say(f"  {name:22s} V*={str(V):6s} w*=({', '.join(map(str, wstar))}) "
            f"|vert(O)|={len(verts)} dyadic_O={dyadic} first_exact_b={hit} "
            f"lower_const=1/{DA * q}")
    for name in ("ST-M26 full-TV K3", "ST-M27 radius 1/2"):
        say(f"  gap curve {name}: " + ", ".join(str(g) for g in curves[name]))
    say("  every instance: V_b nonincreasing, V_b - V* in {0} U [2^-b/(D_A q), Delta floor(s/2) 2^-b];")
    say("  V_b reaches V* within b<=10 exactly when O contains a dyadic point (decided independently)")

    # ---------------- Theorem 2: random small games ----------------
    say("\n[T2r] random integer games (seeded), R in 2..4 rows, n in 2..3 columns, b = 0..6")
    rng = random.Random(20261017)
    n_games = n_dyadic = n_nondyadic = n_late = 0
    for _ in range(300):
        R, n = rng.randint(2, 4), rng.randint(2, 3)
        A = _m([[rng.randint(0, 5) for _ in range(n)] for _ in range(R)])
        V, wstar = solve_game(A)
        verts = optimal_set_vertices(A, V)
        dyadic = polytope_meets_ring(verts, 2)
        DA, q = common_denominator(A), V.denominator
        hit = None
        prev = None
        for b in range(7):
            N = 2 ** b
            vb, _ = grid_value(A, N)
            gap = vb - V
            assert gap >= 0 and (prev is None or vb <= prev)
            prev = vb
            if gap == 0:
                hit = b if hit is None else hit
            else:
                assert gap >= F(1, DA * q * N)
            assert gap <= rounding_gap_bound(A, wstar, N)
        if not dyadic:
            assert hit is None
            n_nondyadic += 1
        else:
            n_dyadic += 1
            if hit is None:
                n_late += 1  # dyadic optimum exists but needs more than 6 bits
        n_games += 1
    say(f"  {n_games} games: {n_dyadic} with a dyadic optimal point ({n_dyadic - n_late} exact by b<=6,"
        f" {n_late} needing b>6), {n_nondyadic} without (never exact for b<=6, as forced); all bounds hold")

    # ---------------- Theorem 3: Knuth-Yao ----------------
    say("\n[T3] variable budget: Knuth-Yao optimal expected public bits")
    third = (F(1, 3),) * 3
    ky = ky_expected_bits(third)
    assert ky == F(8, 3)
    U = ddg_undecided(third, 40)
    for t in range(41):
        tail = F(U[t], 2 ** t)
        assert tail == F(2 ** t % 3, 2 ** t) == sampler_lower_bound_tail(third, t)
    series = sum((F(U[t], 2 ** t) for t in range(41)), F(0))
    assert series <= ky <= series + F(3, 2 ** 40)  # tail sum_{t>40} U_t 2^-t < 3/2^40
    H = entropy_bits(third)
    say(f"  K3 uniform: E[T_KY] = {ky} = {float(ky):.6f} bits;  H = log2 3 = {H:.6f};  "
        f"H <= E[T] < H+2 margin {H + 2 - float(ky):.6f}")
    say("  K3 DDG tail P(T>t) = (2^t mod 3)/2^t equals the universal lower bound for every t <= 40")
    rng = random.Random(8)
    worst_margin = 10.0
    for _ in range(200):
        n = rng.randint(2, 5)
        q = rng.randint(2, 40)
        cuts = sorted(rng.randint(0, q) for _ in range(n - 1))
        parts = [b - a for a, b in zip([0] + cuts, cuts + [q])]
        w = tuple(F(p, q) for p in parts)
        e = ky_expected_bits(w)
        # independent check 1: digit formula, truncated with exact tail bound
        K = 80
        approx = sum((nu_partial(x, K) for x in w), F(0))
        tail_bound = n * F(K + 2, 2 ** K)  # sum_{k>K} k 2^-k = (K+2)/2^K
        assert approx <= e <= approx + tail_bound
        # independent check 2: DDG construction tail sum
        Ud = ddg_undecided(w, K)
        series = sum((F(Ud[t], 2 ** t) for t in range(K + 1)), F(0))
        assert series <= e <= series + F(n, 2 ** K)  # U_t/2^t < n/2^t
        for t in range(K + 1):
            assert F(Ud[t], 2 ** t) == sampler_lower_bound_tail(w, t)
        H = entropy_bits(w)
        assert H - 1e-12 <= float(e) < H + 2
        worst_margin = min(worst_margin, H + 2 - float(e))
        dy = all(in_ring(x, 2) for x in w)
        # bounded-budget samplers exist iff every weight is dyadic
        assert dy == (Ud[K] == 0)
    say(f"  200 random rational laws: periodic closed form == digit series == DDG tail series;"
        f" H <= E[T] < H+2 (min margin {worst_margin:.4f}); DDG terminates by depth 80 iff dyadic")

    # ---------------- Theorem 4: L-ary coin ----------------
    say("\n[T4] one toss of a uniform L-ary public coin, L = 1..12")
    for L in range(1, 13):
        vL = grid_value(K3, L)[0]
        assert vL == 2 - F(L // 3, L)
        assert (vL == F(5, 3)) == (L % 3 == 0)
        assert polytope_meets_ring([third], L) == (L % 3 == 0)
        m27 = grid_value(INSTANCES["ST-M27 radius 1/2"], L)[0]
        assert (m27 == F(5, 3)) == (L % 3 == 0)
        assert m27 - F(5, 3) == 0 or m27 - F(5, 3) >= F(1, 30 * L)
        say(f"  L={L:2d}  K3 V={str(vL):>6}  (=5/3: {L % 3 == 0})   ST-M27 r=1/2 V={str(m27):>7}")
    for L in (2, 4, 5, 7, 8, 10):
        t = 1
        while L ** t <= 1000:
            assert k3_grid_value_fast(L ** t) > F(5, 3)
            t += 1
    say("  K3: V* attained by one toss iff 3 | L; never attained by t tosses with 3 not dividing L (L^t <= 1000 checked)")
    for name in ("ST-M21 minimax", "K4 nonoracle minimax"):
        A = INSTANCES[name]
        V = EXPECTED_VALUES[name]
        hits = [L for L in range(1, 13) if grid_value(A, L)[0] == V]
        assert hits == [L for L in range(1, 13) if L % 2 == 0]
    say("  ST-M21 and K4 (optimum (1/2,1/2)): one toss attains V* iff 2 | L, L <= 12")

    # ---------------- repository cross-check ----------------
    say("\n[X] cross-check against repository exact solvers")
    from .confusion_graphs import ConfusionGraph
    from .robust_prior_codes import (
        k3_shared_randomness_example,
        k4_nonoracle_minimax_example,
        solve_exact_zero_sum_game,
    )
    from .shared_tv_robust_codes import (
        exact_shared_tv_robust_prefix_code,
        full_tv_k3_shared_randomness_example,
    )

    G = ConfusionGraph.from_edges((0, 1, 2), ((0, 1), (0, 2), (1, 2)))
    repo_games = {
        "ST-M21 minimax": k3_shared_randomness_example().mixed_minimax,
        "ST-M21 regret": k3_shared_randomness_example().mixed_regret,
        "K4 nonoracle minimax": k4_nonoracle_minimax_example().mixed_minimax,
        "ST-M26 full-TV K3": full_tv_k3_shared_randomness_example().mixed_game,
    }
    for r, label in ((F(2, 5), "2/5"), (F(7, 15), "7/15"), (F(1, 2), "1/2")):
        repo_games[f"ST-M27 radius {label}"] = exact_shared_tv_robust_prefix_code(
            G, (F(4, 5), F(1, 10), F(1, 10)), r).mixed_game
    for name, g in repo_games.items():
        assert g.valid
        assert tuple(tuple(row) for row in g.cost_matrix) == INSTANCES[name], name
        assert g.value == EXPECTED_VALUES[name]
        say(f"  {name:22s} matrix and value match repo certificate (value {g.value})")
    g = solve_exact_zero_sum_game(INSTANCES["ST-M45 K3 regret"])
    assert g.valid and g.value == F(2, 3)
    say("  ST-M45 K3 regret: the hand-written matrix A - 1 is solved by the repo solver with value 2/3 "
        "(seven matrices are matched against repo certificates; for ST-M45 only the value is)")
    zero_gain = []
    for k in range(0, 16):
        r = F(k, 30)
        cert = exact_shared_tv_robust_prefix_code(G, (F(4, 5), F(1, 10), F(1, 10)), r)
        zero_gain.append(cert.mixed_game.value == cert.deterministic_value == F(6, 5) + r)
    assert all(zero_gain[:15]) and not zero_gain[15]
    say("  ST-M27 radius sweep r = k/30, k = 0..15: shared and deterministic values both equal 6/5 + r "
        "(zero bits needed) for every r <= 7/15, and differ at r = 1/2")

    say("\nALL CHECKS PASSED")
    return out


def receipt_text() -> str:
    return "\n".join(run(verbose=False)) + "\n"


if __name__ == "__main__":
    run(verbose=True)
