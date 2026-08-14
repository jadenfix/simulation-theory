from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.drifting_priors import (
    exact_drift_path_cost,
    exact_static_drift_robust_prefix_code,
    inflate_confidence_radius_for_drift,
)
from simtheory.statistical_prior_uncertainty import weissman_tv_confidence_radius


def complete_graph(n: int) -> ConfusionGraph:
    vertices = tuple(range(n))
    edges = tuple((i, j) for i in range(n) for j in range(i + 1, n))
    return ConfusionGraph.from_edges(vertices, edges)


def test_fixed_length_vector_has_one_simultaneously_attaining_drift_path():
    prior = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    certificate = exact_drift_path_cost(prior, (1, 2, 3, 3), Fraction(1, 10), 4)
    assert certificate.valid
    assert certificate.radii == (
        Fraction(1, 10),
        Fraction(1, 5),
        Fraction(3, 10),
        Fraction(2, 5),
    )
    assert certificate.cumulative_worst_cost == Fraction(8)
    assert certificate.average_worst_cost == Fraction(2)


def test_zero_drift_reduces_to_repeated_nominal_optimum():
    graph = complete_graph(4)
    prior = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    certificate = exact_static_drift_robust_prefix_code(graph, prior, 0, 5)
    assert certificate.valid
    assert certificate.robust_cumulative_value == Fraction(15, 2)
    assert certificate.drift_uplift == 0
    assert certificate.selected_candidate.state_lengths[0] == 1


def test_skew_k4_two_period_phase_change_occurs_at_one_sixth_drift():
    graph = complete_graph(4)
    prior = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))

    below = exact_static_drift_robust_prefix_code(graph, prior, Fraction(1, 7), 2)
    above = exact_static_drift_robust_prefix_code(graph, prior, Fraction(1, 5), 2)

    assert below.valid and above.valid
    assert below.robust_cumulative_value == Fraction(27, 7)
    assert sorted(below.selected_candidate.state_lengths) == [1, 2, 3, 3]
    assert below.selected_candidate.state_lengths[0] == 1

    assert above.robust_cumulative_value == 4
    assert above.selected_candidate.state_lengths == (2, 2, 2, 2)

    at_boundary = exact_static_drift_robust_prefix_code(graph, prior, Fraction(1, 6), 2)
    assert at_boundary.robust_cumulative_value == 4


def test_longer_horizon_makes_same_per_step_drift_more_consequential():
    graph = complete_graph(4)
    prior = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    eta = Fraction(1, 7)
    two = exact_static_drift_robust_prefix_code(graph, prior, eta, 2)
    three = exact_static_drift_robust_prefix_code(graph, prior, eta, 3)
    assert two.selected_candidate.state_lengths != (2, 2, 2, 2)
    assert three.selected_candidate.state_lengths == (2, 2, 2, 2)
    assert three.robust_cumulative_value == 6


def test_statistical_radius_and_declared_drift_add_by_triangle_inequality():
    confidence = weissman_tv_confidence_radius(
        (8000, 1000, 1000),
        Fraction(1, 20),
        rational_denominator=100_000,
    )
    inflated = inflate_confidence_radius_for_drift(confidence, Fraction(1, 10))
    assert inflated.valid
    assert inflated.inflated_radius == confidence.radius + Fraction(1, 10)
    assert not inflated.clipped_at_one


def test_large_drift_inflation_clips_at_full_simplex():
    confidence = weissman_tv_confidence_radius((1, 0, 0), Fraction(1, 20))
    inflated = inflate_confidence_radius_for_drift(confidence, Fraction(1, 10))
    assert inflated.valid
    assert inflated.inflated_radius == 1
    assert inflated.clipped_at_one
