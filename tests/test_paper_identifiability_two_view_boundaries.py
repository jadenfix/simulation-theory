from fractions import Fraction as F
from itertools import product


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


def det2(A):
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def inv2(A):
    d = det2(A)
    assert d != 0
    return ((A[1][1] / d, -A[0][1] / d), (-A[1][0] / d, A[0][0] / d))


def is_permutation_2(A):
    return A in {
        ((F(1), F(0)), (F(0), F(1))),
        ((F(0), F(1)), (F(1), F(0))),
    }


def test_full_row_rank_assumption_has_exact_counterexample():
    # Rank-deficient channel: both latent states have exactly the same observable law.
    K = ((F(1),), (F(1),))
    pi = (F(1, 2), F(1, 2))
    A = ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)))
    assert det2(A) != 0
    assert not is_permutation_2(A)

    pip = matmul_row(pi, inv2(A))
    Kp = matmul(A, K)
    assert pip == pi
    assert Kp == K
    assert matmul_row(pip, Kp) == matmul_row(pi, K)

    T = matmul(matmul(transpose(K), diag(pi)), K)
    Tp = matmul(matmul(transpose(Kp), diag(pip)), Kp)
    assert T == ((F(1),),)
    assert Tp == T


def test_strict_positivity_assumption_has_exact_counterexample():
    # Full-rank channel, but the transformed prior has a zero component.
    # The unweighted row can remain non-permutation while both laws are preserved.
    K = ((F(1), F(0)), (F(0), F(1)))
    pi = (F(1), F(0))
    A = ((F(1), F(0)), (F(1, 2), F(1, 2)))
    assert det2(A) != 0
    assert not is_permutation_2(A)

    pip = matmul_row(pi, inv2(A))
    assert pip == (F(1), F(0))
    assert 0 in pip
    Kp = matmul(A, K)
    assert matmul_row(pip, Kp) == matmul_row(pi, K)

    T = matmul(matmul(transpose(K), diag(pi)), K)
    Tp = matmul(matmul(transpose(Kp), diag(pip)), Kp)
    assert Tp == T == ((F(1), F(0)), (F(0), F(0)))


def test_nonidentity_full_rank_channel_bounded_search_leaves_only_permutations():
    # A nontrivial two-state/three-outcome channel, rather than K=I.
    K = (
        (F(1, 2), F(1, 3), F(1, 6)),
        (F(1, 4), F(1, 4), F(1, 2)),
    )
    pi = (F(2, 5), F(3, 5))
    q = matmul_row(pi, K)
    T = matmul(matmul(transpose(K), diag(pi)), K)

    denominator = 8
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
        Kp = matmul(A, K)
        if matmul_row(pip, Kp) != q:
            continue
        admissible += 1
        Tp = matmul(matmul(transpose(Kp), diag(pip)), Kp)
        if Tp == T:
            preserving.append(A)

    assert admissible > 2
    assert set(preserving) == {
        ((F(1), F(0)), (F(0), F(1))),
        ((F(0), F(1)), (F(1), F(0))),
    }
