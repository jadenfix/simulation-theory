from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.statistical_prior_uncertainty import (
    empirical_distribution,
    exact_data_calibrated_tv_prefix_code,
    weissman_tv_confidence_radius,
)


def complete_graph(n: int) -> ConfusionGraph:
    vertices = tuple(range(n))
    edges = tuple((i, j) for i in range(n) for j in range(i + 1, n))
    return ConfusionGraph.from_edges(vertices, edges)


def test_empirical_distribution_is_exact_rational():
    assert empirical_distribution((8, 1, 1)) == (
        Fraction(4, 5),
        Fraction(1, 10),
        Fraction(1, 10),
    )


def test_weissman_radius_shrinks_with_sample_size():
    small = weissman_tv_confidence_radius((80, 10, 10), Fraction(1, 20))
    large = weissman_tv_confidence_radius((8000, 1000, 1000), Fraction(1, 20))
    assert small.valid and large.valid
    assert large.radius < small.radius
    assert small.empirical_prior == large.empirical_prior


def test_outward_rational_rounding_and_delta_monotonicity():
    loose = weissman_tv_confidence_radius(
        (800, 100, 100),
        Fraction(1, 10),
        rational_denominator=10_000,
    )
    strict = weissman_tv_confidence_radius(
        (800, 100, 100),
        Fraction(1, 100),
        rational_denominator=10_000,
    )
    assert loose.valid and strict.valid
    assert strict.radius >= loose.radius
    assert loose.radius.denominator <= 10_000


def test_data_calibrated_exact_robust_code_wires_statistical_and_exact_layers():
    graph = complete_graph(3)
    certificate = exact_data_calibrated_tv_prefix_code(
        graph,
        (800, 100, 100),
        Fraction(1, 20),
        rational_denominator=10_000,
    )
    assert certificate.valid
    assert certificate.robust_code.nominal_prior == (
        Fraction(4, 5),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    assert certificate.robust_length_upper_bound >= certificate.robust_code.nominal_optimum


def test_tiny_samples_can_saturate_at_full_simplex():
    certificate = weissman_tv_confidence_radius((1, 0, 0), Fraction(1, 20))
    assert certificate.valid
    assert certificate.radius == 1
    assert certificate.clipped_at_one
