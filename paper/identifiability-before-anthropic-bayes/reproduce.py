#!/usr/bin/env python3
"""Exact, dependency-free reproduction/audit for the P1 paper.

All arithmetic used in mathematical receipts is fractions.Fraction. Finite
enumerations are bounded and explicitly labeled as audits, not universal proofs.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fstr(x: F) -> str:
    return f"{x.numerator}/{x.denominator}"


def matmul_row(v, M):
    return tuple(sum((v[i] * M[i][j] for i in range(len(v))), F(0)) for j in range(len(M[0])))


def matmul(A, B):
    return tuple(tuple(sum((A[i][k] * B[k][j] for k in range(len(B))), F(0)) for j in range(len(B[0]))) for i in range(len(A)))


def transpose(A):
    return tuple(tuple(A[i][j] for i in range(len(A))) for j in range(len(A[0])))


def diag(v):
    return tuple(tuple(v[i] if i == j else F(0) for j in range(len(v))) for i in range(len(v)))


def eye(n):
    return tuple(tuple(F(int(i == j)) for j in range(n)) for i in range(n))


def det(A):
    n = len(A)
    M = [list(row) for row in A]
    out = F(1)
    for c in range(n):
        pivot = next((r for r in range(c, n) if M[r][c] != 0), None)
        if pivot is None:
            return F(0)
        if pivot != c:
            M[c], M[pivot] = M[pivot], M[c]
            out = -out
        p = M[c][c]
        out *= p
        for r in range(c + 1, n):
            if M[r][c] == 0:
                continue
            q = M[r][c] / p
            for j in range(c, n):
                M[r][j] -= q * M[c][j]
    return out


def inverse(A):
    n = len(A)
    I = eye(n)
    M = [list(A[i]) + list(I[i]) for i in range(n)]
    for c in range(n):
        pivot = next((r for r in range(c, n) if M[r][c] != 0), None)
        if pivot is None:
            raise ValueError("singular matrix")
        M[c], M[pivot] = M[pivot], M[c]
        p = M[c][c]
        M[c] = [x / p for x in M[c]]
        for r in range(n):
            if r == c or M[r][c] == 0:
                continue
            q = M[r][c]
            M[r] = [M[r][j] - q * M[c][j] for j in range(2 * n)]
    return tuple(tuple(M[i][n:]) for i in range(n))


def rank(A):
    if not A:
        return 0
    M = [list(row) for row in A]
    rows, cols = len(M), len(M[0])
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        p = M[r][c]
        M[r] = [x / p for x in M[r]]
        for i in range(rows):
            if i == r or M[i][c] == 0:
                continue
            q = M[i][c]
            M[i] = [M[i][j] - q * M[r][j] for j in range(cols)]
        r += 1
        if r == rows:
            break
    return r


def tv(p, q):
    return sum((abs(a - b) for a, b in zip(p, q)), F(0)) / 2


def compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def observable_equivalence_audit():
    p = (F(1, 6), F(1, 3), F(1, 2))
    q = tuple(p)
    bfs = [fstr(qi / pi) for pi, qi in zip(p, q) if pi > 0]
    return {"tv": fstr(tv(p, q)), "positive_support_bayes_factors": bfs, "all_one": all(x == "1/1" for x in bfs)}


def clone_example():
    rows = []
    for r in (1, 2, 3, 5, 20, 100):
        rows.append({
            "r": r,
            "uniform_label_sim_if_sim_cloned": fstr(F(r, r + 1)),
            "uniform_label_sim_if_base_cloned": fstr(F(1, r + 1)),
            "additive_sim_weight": fstr(F(1, 2)),
        })
    K = ((F(3, 4), F(1, 4)), (F(1, 5), F(4, 5)))
    w = F(2, 5)
    joint_parent = tuple(tuple(w * K[0][i] * K[0][j] for j in range(2)) for i in range(2))
    split = (F(1, 10), F(3, 10))
    joint_split = tuple(tuple(sum(s * K[0][i] * K[0][j] for s in split) for j in range(2)) for i in range(2))
    assert joint_parent == joint_split
    return {"counts": rows, "shared_latent_two_view_preserved": True}


def rational_additivity_audit(max_denominator=24):
    checked = 0
    for n in range(1, max_denominator + 1):
        mu_unit = F(1, n)
        assert n * mu_unit == 1
        for p in range(n + 1):
            assert p * mu_unit == F(p, n)
            checked += 1
    return {"max_denominator": max_denominator, "rational_values_checked": checked}


def persistent_example(T=100):
    a, b = F(3, 4), F(1, 4)
    return {"T": T, "persistent_bayes_factor": fstr(a / b), "independent_redraw_bayes_factor": fstr((a / b) ** T)}


def persistent_convexity_audit():
    cases = [
        ((F(1, 2), F(1, 3), F(1, 6)), (F(1, 3), F(1, 3), F(1, 3)), (F(1, 4), F(1, 2), F(3, 4))),
        ((F(2, 5), F(3, 5)), (F(1, 5), F(4, 5)), (F(2, 3), F(1, 7))),
    ]
    receipts = []
    for a, b, likelihood in cases:
        pa = sum(ai * li for ai, li in zip(a, likelihood))
        pb = sum(bi * li for bi, li in zip(b, likelihood))
        lr = pa / pb
        posterior = tuple(bi * li / pb for bi, li in zip(b, likelihood))
        reconstructed = sum(post * (ai / bi) for post, ai, bi in zip(posterior, a, b))
        assert lr == reconstructed
        ratios = [ai / bi for ai, bi in zip(a, b)]
        assert min(ratios) <= lr <= max(ratios)
        receipts.append({"lr": fstr(lr), "lower": fstr(min(ratios)), "upper": fstr(max(ratios))})
    return receipts


def support_boundary_audit():
    a = (F(1, 2), F(1, 2))
    b = (F(1), F(0))
    likelihood_y = (F(0), F(1))
    pa = sum(ai * li for ai, li in zip(a, likelihood_y))
    pb = sum(bi * li for bi, li in zip(b, likelihood_y))
    assert pa > 0 and pb == 0
    return {"numerator_probability": fstr(pa), "denominator_probability": fstr(pb), "finite_ceiling_applies": False}


def affine_rank_examples():
    identifiable = ((F(1), F(0), F(0)), (F(0), F(1), F(0)), (F(0), F(0), F(1)))
    diffs = tuple(tuple(identifiable[i][j] - identifiable[-1][j] for j in range(3)) for i in range(2))
    assert rank(diffs) == 2
    nonident = ((F(1), F(0)), (F(0), F(1)), (F(1, 2), F(1, 2)))
    diffs2 = tuple(tuple(nonident[i][j] - nonident[-1][j] for j in range(2)) for i in range(2))
    assert rank(diffs2) == 1
    pi_a = (F(1, 2), F(1, 2), F(0))
    pi_b = (F(0), F(0), F(1))
    qa, qb = matmul_row(pi_a, nonident), matmul_row(pi_b, nonident)
    assert pi_a != pi_b and qa == qb
    return {"identifiable_affine_rank": rank(diffs), "nonidentifiable_affine_rank": rank(diffs2), "collision_observed_law": list(map(fstr, qa))}


def gauge_examples():
    K = eye(2)
    pi = (F(1, 2), F(1, 2))
    receipts = []
    for a in (F(3, 5), F(2, 3), F(3, 4), F(4, 5), F(9, 10)):
        A = ((a, 1 - a), (1 - a, a))
        pip = matmul_row(pi, inverse(A))
        Kp = matmul(A, K)
        q, qp = matmul_row(pi, K), matmul_row(pip, Kp)
        assert all(x >= 0 for x in pip) and sum(pip) == 1 and q == qp and Kp != K
        T = matmul(matmul(transpose(K), diag(pi)), K)
        Tp = matmul(matmul(transpose(Kp), diag(pip)), Kp)
        receipts.append({"a": fstr(a), "one_view_equal": q == qp, "two_view_equal": T == Tp})
    return receipts


def two_view_grid_audit_2x2(denominator=8):
    K = eye(2)
    pi = (F(1, 2), F(1, 2))
    T = diag(pi)
    preserving = []
    considered = 0
    for a, b in product(range(denominator + 1), repeat=2):
        A = ((F(a, denominator), F(denominator - a, denominator)), (F(b, denominator), F(denominator - b, denominator)))
        if det(A) == 0:
            continue
        pip = matmul_row(pi, inverse(A))
        if any(x <= 0 for x in pip):
            continue
        considered += 1
        Tp = matmul(matmul(transpose(A), diag(pip)), A)
        if Tp == T:
            preserving.append(A)
    perms = [((F(1), F(0)), (F(0), F(1))), ((F(0), F(1)), (F(1), F(0)))]
    assert set(preserving) == set(perms)
    return {"denominator": denominator, "valid_positive_cases": considered, "preserving_count": len(preserving), "only_permutations": True}


def two_view_grid_audit_3x3(denominator=3):
    K = eye(3)
    pi = (F(1, 3),) * 3
    T = diag(pi)
    rows = [tuple(F(x, denominator) for x in comp) for comp in compositions(denominator, 3)]
    preserving = []
    considered = 0
    for raw in product(rows, repeat=3):
        A = tuple(raw)
        if det(A) == 0:
            continue
        pip = matmul_row(pi, inverse(A))
        if any(x <= 0 for x in pip):
            continue
        considered += 1
        Tp = matmul(matmul(transpose(A), diag(pip)), A)
        if Tp == T:
            preserving.append(A)
    assert len(preserving) == 6
    assert all(sum(row.count(F(1)) for row in A) == 3 for A in preserving)
    return {"denominator": denominator, "candidate_rows": len(rows), "valid_positive_cases": considered, "preserving_count": 6, "only_permutations": True}


def paper_numeric_assertions(receipt):
    assert receipt["clone"]["counts"][4]["uniform_label_sim_if_sim_cloned"] == "20/21"
    assert receipt["clone"]["counts"][4]["uniform_label_sim_if_base_cloned"] == "1/21"
    assert receipt["persistent"]["persistent_bayes_factor"] == "3/1"
    expected = 3 ** 100
    assert receipt["persistent"]["independent_redraw_bayes_factor"] == f"{expected}/1"
    return {"all_displayed_numeric_assertions_matched": True, "three_to_100": str(expected)}


def main():
    payload = {
        "schema": "identifiability-before-anthropic-bayes/receipt-v2",
        "observable_equivalence": observable_equivalence_audit(),
        "clone": clone_example(),
        "rational_additivity": rational_additivity_audit(),
        "persistent": persistent_example(),
        "persistent_convexity": persistent_convexity_audit(),
        "support_boundary": support_boundary_audit(),
        "affine_rank": affine_rank_examples(),
        "gauge": gauge_examples(),
        "two_view_grid_audit_2x2": two_view_grid_audit_2x2(),
        "two_view_grid_audit_3x3": two_view_grid_audit_3x3(),
    }
    payload["paper_numeric_assertions"] = paper_numeric_assertions(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    receipt = dict(payload)
    receipt["sha256_without_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    out = HERE / "receipt.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
