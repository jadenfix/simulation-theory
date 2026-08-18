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


def self_location_sampling_kernel_audit():
    """Exact finite examples for count calibration, world weighting, and refinement.

    There are two worlds.  World 0 has one F and one G center.  World 1 has
    three F and one G center.  Evidence is deliberately nondiscriminating, so
    only the world prior and self-location kernel determine the centered odds.
    """

    rho_equal = (F(1, 2), F(1, 2))
    # Within-world category masses under uniform self-location kernels.
    f_mass = (F(1, 2), F(3, 4))
    g_mass = (F(1, 2), F(1, 4))

    pf_equal = sum(rho_equal[w] * f_mass[w] for w in range(2))
    pg_equal = sum(rho_equal[w] * g_mass[w] for w in range(2))
    assert pf_equal == F(5, 8)
    assert pg_equal == F(3, 8)
    assert pf_equal / pg_equal == F(5, 3)

    # Raw center counts are 4 F versus 2 G, which is not the same as equal-world
    # weighting followed by uniform-within-world self-location.
    raw_count_odds = F(4, 2)
    assert raw_count_odds == 2
    assert raw_count_odds != pf_equal / pg_equal

    # Weight worlds by reference-class size (2 versus 4) and uniform within each
    # world.  Then every centered possibility receives the same global mass and
    # the raw global count ratio is recovered.
    rho_size = (F(1, 3), F(2, 3))
    pf_size = sum(rho_size[w] * f_mass[w] for w in range(2))
    pg_size = sum(rho_size[w] * g_mass[w] for w in range(2))
    assert pf_size / pg_size == raw_count_odds == 2

    # Representation-only refinement of the F center in world 0 into three
    # observationally identical labels.  Conserving the parent's self-location
    # mass gives 1/6 + 1/6 + 1/6 = 1/2, so the posterior remains unchanged.
    split_f_world0 = (F(1, 6), F(1, 6), F(1, 6))
    assert sum(split_f_world0, F(0)) == F(1, 2)
    refined_f_mass = (sum(split_f_world0, F(0)), F(3, 4))
    refined_g_mass = (F(1, 2), F(1, 4))
    pf_refined = sum(rho_equal[w] * refined_f_mass[w] for w in range(2))
    pg_refined = sum(rho_equal[w] * refined_g_mass[w] for w in range(2))
    assert pf_refined / pg_refined == F(5, 3)

    # If one instead resets the world-0 kernel to uniform over the four labels
    # after cloning, the world-0 F mass changes from 1/2 to 3/4.  That is a new
    # self-location model, and the centered odds change accordingly.
    relabeled_uniform_f_mass = (F(3, 4), F(3, 4))
    relabeled_uniform_g_mass = (F(1, 4), F(1, 4))
    pf_reset = sum(rho_equal[w] * relabeled_uniform_f_mass[w] for w in range(2))
    pg_reset = sum(rho_equal[w] * relabeled_uniform_g_mass[w] for w in range(2))
    assert pf_reset / pg_reset == 3

    return {
        "equal_world_prior_uniform_within_world_odds": fstr(pf_equal / pg_equal),
        "raw_global_count_odds": fstr(raw_count_odds),
        "size_weighted_world_prior_odds": fstr(pf_size / pg_size),
        "mass_conserving_refinement_odds": fstr(pf_refined / pg_refined),
        "uniform_over_refined_labels_odds": fstr(pf_reset / pg_reset),
        "equal_world_prior_category_probabilities": {
            "F": fstr(pf_equal),
            "G": fstr(pg_equal),
        },
        "world_priors": {
            "equal": [fstr(x) for x in rho_equal],
            "reference_class_size_weighted": [fstr(x) for x in rho_size],
        },
        "interpretation": "raw counts require a declared self-location/world-weighting rule; mass-conserving representational refinement leaves the posterior unchanged",
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
        "sampling_kernel": self_location_sampling_kernel_audit(),
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
