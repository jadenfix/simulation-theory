from fractions import Fraction
from random import Random

from simtheory.convex_sparsification import (
    caratheodory_sparsify,
    convex_barycenter,
    sparsify_shared_tv_certificate,
)
from simtheory.shared_tv_robust_codes import (
    exact_shared_tv_robust_prefix_code,
    full_tv_k3_shared_randomness_example,
)
from simtheory.confusion_graphs import ConfusionGraph


def test_exact_caratheodory_reduces_a_two_dimensional_mixture_to_three_points():
    points = (
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
        (Fraction(1), Fraction(1)),
        (Fraction(2), Fraction(0)),
        (Fraction(0), Fraction(2)),
    )
    weights = (Fraction(1, 6),) * 6
    certificate = caratheodory_sparsify(points, weights)
    assert certificate.valid
    assert certificate.barycenter == (Fraction(2, 3), Fraction(2, 3))
    assert len(certificate.original_support) == 6
    assert len(certificate.reduced_support) <= 3
    assert convex_barycenter(points, certificate.reduced_weights) == certificate.barycenter
    assert certificate.steps


def test_seeded_exact_sparsification_preserves_random_rational_barycenters():
    rng = Random(8675309)
    for dimension in range(0, 5):
        point_count = dimension + 7
        for _ in range(25):
            points = tuple(
                tuple(Fraction(rng.randrange(-6, 7), rng.randrange(1, 6)) for _ in range(dimension))
                for _ in range(point_count)
            )
            raw = tuple(rng.randrange(1, 10) for _ in range(point_count))
            total = sum(raw)
            weights = tuple(Fraction(value, total) for value in raw)
            certificate = caratheodory_sparsify(points, weights)
            assert certificate.valid
            assert len(certificate.reduced_support) <= dimension + 1
            assert convex_barycenter(points, weights) == convex_barycenter(
                points,
                certificate.reduced_weights,
            )


def test_shared_tv_mixtures_have_state_dimension_support_bounds():
    certificate = full_tv_k3_shared_randomness_example()
    sparse = sparsify_shared_tv_certificate(certificate)
    assert sparse.valid
    assert len(sparse.codebook_mixture.reduced_support) <= 4
    assert len(sparse.vertex_mixture.reduced_support) <= 3
    assert sparse.codebook_mixture.barycenter == certificate.mixed_state_lengths
    assert sparse.vertex_mixture.barycenter == certificate.least_favorable_prior[:-1]


def test_four_state_continuous_game_sparsification_is_independent_of_vertex_count():
    graph = ConfusionGraph.from_edges(
        (0, 1, 2, 3),
        ((0, 1), (1, 2), (2, 3), (3, 0)),
    )
    certificate = exact_shared_tv_robust_prefix_code(
        graph,
        (
            Fraction(2, 5),
            Fraction(3, 10),
            Fraction(1, 5),
            Fraction(1, 10),
        ),
        Fraction(1, 4),
        max_states=5,
        max_vertices=6,
        max_partitions=100_000,
        max_candidates=100_000,
        max_dominance_pairs=1_000_000,
        max_game_bases=2_000_000,
    )
    assert certificate.valid
    sparse = sparsify_shared_tv_certificate(certificate)
    assert sparse.valid
    assert len(sparse.codebook_mixture.reduced_support) <= 5
    assert len(sparse.vertex_mixture.reduced_support) <= 4
