#!/usr/bin/env python3
"""Exact-rational reproduction and bounded falsification suite for the paper."""
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path


def matmul_row(v, M):
    return tuple(sum((v[i] * M[i][j] for i in range(len(v))), F(0)) for j in range(len(M[0])))


def matmul(A, B):
    return tuple(
        tuple(sum((A[i][k] * B[k][j] for k in range(len(B))), F(0)) for j in range(len(B[0])))
        for i in range(len(A))
    )


def transpose(A):
    return tuple(tuple(A[j][i] for j in range(len(A))) for i in range(len(A[0])))


def diag(v):
    return tuple(tuple(v[i] if i == j else F(0) for j in range(len(v))) for i in range(len(v)))


def fstr(x):
    return f"{x.numerator}/{x.denominator}"


def det2(A):
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def inv2(A):
    d = det2(A)
    if d == 0:
        raise ValueError("singular")
    return ((A[1][1] / d, -A[0][1] / d), (-A[1][0] / d, A[0][0] / d))


def det3(A):
    return (
        A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
        - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
        + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])
    )


def inv3(A):
    d = det3(A)
    if d == 0:
        raise ValueError("singular")
    cof = (
        (
            A[1][1] * A[2][2] - A[1][2] * A[2][1],
            -(A[1][0] * A[2][2] - A[1][2] * A[2][0]),
            A[1][0] * A[2][1] - A[1][1] * A[2][0],
        ),
        (
            -(A[0][1] * A[2][2] - A[0][2] * A[2][1]),
            A[0][0] * A[2][2] - A[0][2] * A[2][0],
            -(A[0][0] * A[2][1] - A[0][1] * A[2][0]),
        ),
        (
            A[0][1] * A[1][2] - A[0][2] * A[1][1],
            -(A[0][0] * A[1][2] - A[0][2] * A[1][0]),
            A[0][0] * A[1][1] - A[0][1] * A[1][0],
        ),
    )
    return tuple(tuple(cof[j][i] / d for j in range(3)) for i in range(3))


def clone_example(r=20):
    return {
        "initial": fstr(F(1, 2)),
        "clone_sim": fstr(F(r, r + 1)),
        "clone_base": fstr(F(1, r + 1)),
        "weighted": fstr(F(1, 2)),
    }


def persistent_example(T=100):
    a, b = F(3, 4), F(1, 4)
    return {
        "T": T,
        "persistent_bayes_factor": fstr(a / b),
        "redraw_bayes_factor": fstr((a / b) ** T),
    }


def persistent_mixture_identity_audit():
    # Three unrelated exact rational component likelihoods for one realized transcript.
    a = (F(1, 2), F(1, 3), F(1, 6))
    b = (F(1, 4), F(1, 2), F(1, 4))
    py = (F(2, 5), F(3, 7), F(5, 11))
    pa = sum(a[i] * py[i] for i in range(3))
    pb = sum(b[i] * py[i] for i in range(3))
    post_b = tuple(b[i] * py[i] / pb for i in range(3))
    rhs = sum(post_b[i] * (a[i] / b[i]) for i in range(3))
    assert pa / pb == rhs
    return {
        "likelihood_ratio": fstr(pa / pb),
        "posterior_weighted_ratio": fstr(rhs),
        "posterior_weights": [fstr(x) for x in post_b],
    }


def support_mismatch_boundary():
    # Numerator allows y through component 0; denominator gives that component zero mass.
    a = (F(1), F(0))
    b = (F(0), F(1))
    py = (F(1), F(0))
    pa = sum(a[i] * py[i] for i in range(2))
    pb = sum(b[i] * py[i] for i in range(2))
    assert pa == 1 and pb == 0
    return {"numerator_probability": "1/1", "denominator_probability": "0/1", "finite_ceiling_applies": False}


def known_channel_identifiability_audit():
    full = ((F(1), F(0), F(0)), (F(0), F(1), F(0)), (F(0), F(0), F(1)))
    pa = (F(1, 2), F(1, 3), F(1, 6))
    qa = matmul_row(pa, full)
    assert qa == pa

    deficient = ((F(1), F(0)), (F(0), F(1)), (F(1, 2), F(1, 2)))
    p1 = (F(1, 2), F(1, 2), F(0))
    p2 = (F(0), F(0), F(1))
    q1, q2 = matmul_row(p1, deficient), matmul_row(p2, deficient)
    assert p1 != p2 and q1 == q2 == (F(1, 2), F(1, 2))
    return {
        "full_rank_reconstruction": [fstr(x) for x in qa],
        "rank_deficient_collision_prior_a": [fstr(x) for x in p1],
        "rank_deficient_collision_prior_b": [fstr(x) for x in p2],
        "common_observed_law": [fstr(x) for x in q1],
    }


def gauge_examples():
    K = ((F(1), F(0)), (F(0), F(1)))
    pi = (F(1, 2), F(1, 2))
    transforms = (
        ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4))),
        ((F(2, 3), F(1, 3)), (F(1, 3), F(2, 3))),
    )
    records = []
    q = matmul_row(pi, K)
    T = matmul(matmul(transpose(K), diag(pi)), K)
    for A in transforms:
        Ai = inv2(A)
        pip = matmul_row(pi, Ai)
        assert all(x >= 0 for x in pip)
        Kp = matmul(A, K)
        qp = matmul_row(pip, Kp)
        Tp = matmul(matmul(transpose(Kp), diag(pip)), Kp)
        assert qp == q and Kp != K and Tp != T
        records.append({
            "A": [[fstr(x) for x in row] for row in A],
            "transformed_prior": [fstr(x) for x in pip],
            "one_view_equal": True,
            "two_view_equal": False,
        })

    invalid_A = ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)))
    invalid_pi = (F(1), F(0))
    invalid_pip = matmul_row(invalid_pi, inv2(invalid_A))
    assert any(x < 0 for x in invalid_pip)
    return {"valid_examples": records, "invalid_transformed_prior": [fstr(x) for x in invalid_pip]}


def two_state_permutation_audit(denominator=8):
    K = ((F(1), F(0)), (F(0), F(1)))
    pi = (F(1, 2), F(1, 2))
    T = diag(pi)
    admissible = 0
    preserving = []
    for a, b in product(range(denominator + 1), repeat=2):
        A = (
            (F(a, denominator), F(denominator - a, denominator)),
            (F(b, denominator), F(denominator - b, denominator)),
        )
        if det2(A) == 0:
            continue
        pip = matmul_row(pi, inv2(A))
        if any(x <= 0 for x in pip):
            continue
        admissible += 1
        Tp = matmul(matmul(transpose(A), diag(pip)), A)
        if Tp == T:
            preserving.append(A)
    expected = {
        ((F(1), F(0)), (F(0), F(1))),
        ((F(0), F(1)), (F(1), F(0))),
    }
    assert set(preserving) == expected
    return {"denominator": denominator, "admissible_count": admissible, "preserving_count": 2, "only_permutations": True}


def simplex_rows(total, dimension):
    if dimension == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in simplex_rows(total - first, dimension - 1):
            yield (first,) + rest


def three_state_permutation_audit(denominator=3, expected_admissible=None):
    rows = [tuple(F(x, denominator) for x in counts) for counts in simplex_rows(denominator, 3)]
    pi = (F(1, 3), F(1, 3), F(1, 3))
    T = diag(pi)
    admissible = 0
    preserving = []
    for A in product(rows, repeat=3):
        A = tuple(A)
        if det3(A) == 0:
            continue
        pip = matmul_row(pi, inv3(A))
        if any(x <= 0 for x in pip):
            continue
        admissible += 1
        Tp = matmul(matmul(transpose(A), diag(pip)), A)
        if Tp == T:
            preserving.append(A)
    if expected_admissible is not None:
        assert admissible == expected_admissible
    assert len(preserving) == 6
    assert all(all(sum(x == 1 for x in row) == 1 and all(x in (0, 1) for x in row) for row in A) for A in preserving)
    return {"denominator": denominator, "admissible_count": admissible, "preserving_count": 6, "only_permutations": True}


def main():
    payload = {
        "clone": clone_example(),
        "persistent": persistent_example(),
        "persistent_identity_audit": persistent_mixture_identity_audit(),
        "support_mismatch_boundary": support_mismatch_boundary(),
        "known_channel_identifiability": known_channel_identifiability_audit(),
        "gauge": gauge_examples(),
        "two_view_grid_audit_2state": two_state_permutation_audit(),
        "two_view_grid_audit_2state_extended": two_state_permutation_audit(denominator=32),
        "two_view_grid_audit_3state": three_state_permutation_audit(expected_admissible=108),
        "two_view_grid_audit_3state_extended": three_state_permutation_audit(denominator=6, expected_admissible=3492),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    receipt = dict(payload)
    receipt["sha256_without_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    out = Path(__file__).with_name("receipt.json")
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
