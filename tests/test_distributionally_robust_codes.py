from fractions import Fraction
from itertools import product
from random import Random

import pytest

from simtheory.confusion_graphs import ConfusionGraph, coloring_is_proper
from simtheory.distributionally_robust_codes import (
    exact_tv_robust_prefix_code,
    huber_extremal_expectation,
    maximize_expectation_tv_ball,
    minimize_expectation_tv_ball,
    skew_k4_tv_robust_example,
    total_variation_distance,
    tv_expectation_profile,
)
from simtheory.prior_weighted_codes import exact_prior_weighted_prefix_code


def _compositions(total, count):
    if count == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, count - 1):
            yield (first, *rest)


def _grid_extrema(nominal_counts, values, radius_counts, denominator):
    feasible = []
    for counts in _compositions(denominator, len(nominal_counts)):
        if sum(abs(left - right) for left, right in zip(counts, nominal_counts)) <= 2 * radius_counts:
            expectation = sum(
                Fraction(count, denominator) * value
                for count, value in zip(counts, values)
            )
            feasible.append((expectation, counts))
    assert feasible
    return min(feasible), max(feasible)


def _graph_from_edge_mask(vertex_count, edge_mask):
    edges = []
    bit = 0
    for left in range(vertex_count):
        for right in range(left + 1, vertex_count):
            if (edge_mask >> bit) & 1:
                edges.append((left, right))
            bit += 1
    return ConfusionGraph.from_edges(tuple(range(vertex_count)), tuple(edges))


def _canonical_coloring(colors):
    renaming = {}
    return tuple(
        renaming.setdefault(color, len(renaming))
        for color in colors
    )


def _direct_complete_lengths(message_count):
    if message_count == 1:
        return ((0,),)
    return tuple(
        lengths
        for lengths in product(range(1, message_count), repeat=message_count)
        if sum(Fraction(1, 1 << length) for length in lengths) == 1
    )


def _direct_state_length_vectors(graph):
    count = graph.vertex_count
    colorings = set()
    vectors = set()
    for raw in product(range(count), repeat=count):
        coloring = _canonical_coloring(raw)
        if coloring in colorings:
            continue
        colorings.add(coloring)
        if not coloring_is_proper(graph, coloring):
            continue
        for lengths in _direct_complete_lengths(len(set(coloring))):
            vectors.add(tuple(lengths[color] for color in coloring))
    assert vectors
    return tuple(vectors)


def test_exact_mass_transport_matches_full_rational_simplex_grid():
    rng = Random(20260814)
    denominator = 10
    for _ in range(40):
        nominal_counts = rng.choice(tuple(_compositions(denominator, 4)))
        values = tuple(Fraction(rng.randrange(-3, 6)) for _ in range(4))
        radius_counts = rng.randrange(denominator + 1)
        nominal = tuple(Fraction(count, denominator) for count in nominal_counts)
        radius = Fraction(radius_counts, denominator)
        direct_min, direct_max = _grid_extrema(
            nominal_counts,
            values,
            radius_counts,
            denominator,
        )
        minimum = minimize_expectation_tv_ball(nominal, values, radius)
        maximum = maximize_expectation_tv_ball(nominal, values, radius)
        assert minimum.valid and maximum.valid
        assert minimum.extremal_expectation == direct_min[0]
        assert maximum.extremal_expectation == direct_max[0]
        assert minimum.tv_distance <= radius
        assert maximum.tv_distance <= radius


def test_skew_k4_fixed_code_has_exact_transport_receipts():
    nominal = (
        Fraction(7, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    values = (Fraction(1), Fraction(2), Fraction(3), Fraction(3))
    radius = Fraction(1, 10)
    worst = maximize_expectation_tv_ball(nominal, values, radius)
    best = minimize_expectation_tv_ball(nominal, values, radius)

    assert worst.valid and best.valid
    assert worst.nominal_expectation == Fraction(3, 2)
    assert worst.extremal_expectation == Fraction(17, 10)
    assert best.extremal_expectation == Fraction(13, 10)
    assert worst.expectation_change == Fraction(1, 5)
    assert best.expectation_change == Fraction(-1, 5)
    assert worst.saturation_radius == Fraction(4, 5)
    assert best.saturation_radius == Fraction(3, 10)
    assert worst.full_range_tight_radius == Fraction(7, 10)
    assert best.full_range_tight_radius == Fraction(1, 5)
    assert worst.range_bound_slack == 0
    assert best.range_bound_slack == 0
    assert worst.transfers[0].donor_index == 0
    assert worst.transfers[0].recipient_value == 3


def test_tv_expectation_profile_is_piecewise_linear_and_saturates():
    nominal = (
        Fraction(7, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    values = (Fraction(1), Fraction(2), Fraction(3), Fraction(3))
    worst_profile = tv_expectation_profile(nominal, values, maximize=True)
    best_profile = tv_expectation_profile(nominal, values, maximize=False)
    assert worst_profile.valid and best_profile.valid
    assert tuple(segment.marginal_change for segment in worst_profile.segments) == (
        Fraction(2),
        Fraction(1),
        Fraction(0),
    )
    assert tuple(segment.end_radius for segment in worst_profile.segments) == (
        Fraction(7, 10),
        Fraction(4, 5),
        Fraction(1),
    )
    assert worst_profile.evaluate(Fraction(1, 10)) == Fraction(17, 10)
    assert worst_profile.evaluate(Fraction(4, 5)) == 3
    assert worst_profile.evaluate(1) == 3
    assert best_profile.evaluate(Fraction(1, 10)) == Fraction(13, 10)
    assert best_profile.evaluate(Fraction(3, 10)) == 1
    assert best_profile.evaluate(1) == 1


def test_huber_contamination_is_a_strict_subset_of_same_radius_tv_ball():
    nominal = (
        Fraction(7, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    values = (Fraction(1), Fraction(2), Fraction(3), Fraction(3))
    epsilon = Fraction(1, 10)
    huber = huber_extremal_expectation(
        nominal,
        values,
        epsilon,
        maximize=True,
    )
    tv = maximize_expectation_tv_ball(nominal, values, epsilon)
    assert huber.valid
    assert huber.contaminated_expectation == Fraction(33, 20)
    assert huber.tv_distance_from_nominal == Fraction(9, 100)
    assert huber.tv_distance_from_nominal <= epsilon
    assert huber.contaminated_expectation < tv.extremal_expectation


def test_skew_k4_robust_code_has_exact_radius_phase_change():
    zero = skew_k4_tv_robust_example(0)
    small = skew_k4_tv_robust_example(Fraction(1, 10))
    boundary = skew_k4_tv_robust_example(Fraction(1, 4))
    beyond = skew_k4_tv_robust_example(Fraction(3, 10))
    full = skew_k4_tv_robust_example(1)

    assert zero.robust_value == Fraction(3, 2)
    assert zero.optimal_candidate.state_lengths == (1, 2, 3, 3)
    assert small.robust_value == Fraction(17, 10)
    assert small.optimal_candidate.state_lengths == (1, 2, 3, 3)
    assert small.price_of_robustness == 0
    assert small.uncertainty_uplift == Fraction(1, 5)

    assert boundary.robust_value == 2
    # At the exact tie, the deterministic tie-break retains lower nominal cost.
    assert boundary.optimal_candidate.state_lengths == (1, 2, 3, 3)
    assert beyond.robust_value == 2
    assert beyond.optimal_candidate.state_lengths == (2, 2, 2, 2)
    assert beyond.price_of_robustness == Fraction(1, 2)
    assert beyond.uncertainty_uplift == 0
    assert full.robust_value == full.fixed_length_bits == 2
    assert full.optimal_candidate.state_lengths == (2, 2, 2, 2)


def test_radius_zero_and_one_match_nominal_and_peak_theorems():
    graph = ConfusionGraph.from_edges(
        tuple(range(5)),
        (
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
            (3, 4),
        ),
    )
    prior = (
        Fraction(12, 50),
        Fraction(19, 50),
        Fraction(1, 50),
        Fraction(5, 50),
        Fraction(13, 50),
    )
    nominal = exact_prior_weighted_prefix_code(graph, prior)
    zero = exact_tv_robust_prefix_code(graph, prior, 0)
    full = exact_tv_robust_prefix_code(graph, prior, 1)
    assert zero.valid and full.valid
    assert zero.robust_value == nominal.expected_length == Fraction(37, 25)
    assert full.robust_value == full.fixed_length_bits == 2


def test_all_labeled_four_vertex_graphs_match_independent_tv_robust_search():
    nominal_counts = (1, 2, 3, 4)
    prior = tuple(Fraction(count, 10) for count in nominal_counts)
    radius_counts = 1
    feasible_counts = tuple(
        counts
        for counts in _compositions(10, 4)
        if sum(abs(left - right) for left, right in zip(counts, nominal_counts)) <= 2 * radius_counts
    )
    for edge_mask in range(1 << 6):
        graph = _graph_from_edge_mask(4, edge_mask)
        direct = min(
            max(
                sum(Fraction(count, 10) * length for count, length in zip(counts, lengths))
                for counts in feasible_counts
            )
            for lengths in _direct_state_length_vectors(graph)
        )
        certificate = exact_tv_robust_prefix_code(
            graph,
            prior,
            Fraction(1, 10),
            max_vertices=6,
            max_partitions=100_000,
            max_candidates=100_000,
        )
        assert certificate.valid
        assert certificate.robust_value == direct


def test_robust_value_is_monotone_in_radius():
    graph = ConfusionGraph.from_edges(
        tuple(range(4)),
        ((0, 1), (1, 2), (2, 3), (3, 0)),
    )
    prior = (
        Fraction(1, 10),
        Fraction(2, 10),
        Fraction(3, 10),
        Fraction(4, 10),
    )
    values = tuple(
        exact_tv_robust_prefix_code(graph, prior, radius).robust_value
        for radius in (
            Fraction(0),
            Fraction(1, 10),
            Fraction(1, 4),
            Fraction(1, 2),
            Fraction(1),
        )
    )
    assert values == tuple(sorted(values))


def test_transport_symmetry_and_validation_boundaries():
    nominal = (Fraction(1, 4),) * 4
    values = (Fraction(-2), Fraction(0), Fraction(1), Fraction(5))
    radius = Fraction(3, 10)
    maximum = maximize_expectation_tv_ball(nominal, values, radius)
    negative_minimum = minimize_expectation_tv_ball(
        nominal,
        tuple(-value for value in values),
        radius,
    )
    assert maximum.extremal_expectation == -negative_minimum.extremal_expectation
    assert total_variation_distance(nominal, maximum.extremal_distribution) <= radius

    graph = ConfusionGraph.from_edges((0, 1, 2), ((0, 1), (1, 2)))
    with pytest.raises(ValueError):
        exact_tv_robust_prefix_code(graph, (0.2, 0.3, 0.5), Fraction(1, 10))
    with pytest.raises(ValueError):
        exact_tv_robust_prefix_code(
            graph,
            (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)),
            Fraction(11, 10),
        )
    with pytest.raises(ValueError, match="no exact optimum"):
        exact_tv_robust_prefix_code(
            graph,
            (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)),
            Fraction(1, 10),
            max_candidates=1,
        )
