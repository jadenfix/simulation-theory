from fractions import Fraction
from itertools import product

import pytest

from simtheory.confusion_graphs import ConfusionGraph, coloring_is_proper
from simtheory.prior_weighted_codes import exact_prior_weighted_prefix_code
from simtheory.robust_prior_codes import (
    canonical_codewords_from_lengths,
    complete_prefix_shapes,
    convex_combination_prior,
    exact_finite_prior_robust_code,
    expected_length_under_prior,
    k3_shared_randomness_example,
    k4_nonoracle_minimax_example,
    mixed_expected_length_under_prior,
    solve_exact_zero_sum_game,
)


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
        if sum(
            Fraction(1, 1 << length)
            for length in lengths
        )
        == 1
    )


def _direct_cost_vectors(graph, priors):
    count = graph.vertex_count
    seen = set()
    costs = []
    for raw_colors in product(range(count), repeat=count):
        colors = _canonical_coloring(raw_colors)
        if colors in seen:
            continue
        seen.add(colors)
        if not coloring_is_proper(graph, colors):
            continue
        message_count = len(set(colors))
        for lengths in _direct_complete_lengths(message_count):
            state_lengths = tuple(lengths[color] for color in colors)
            costs.append(
                tuple(
                    sum(
                        probability * length
                        for probability, length in zip(prior, state_lengths)
                    )
                    for prior in priors
                )
            )
    assert costs
    return tuple(costs)


def _two_scenario_mixed_value(cost_vectors):
    assert cost_vectors and all(len(vector) == 2 for vector in cost_vectors)
    best = min(max(vector) for vector in cost_vectors)
    for left in cost_vectors:
        for right in cost_vectors:
            denominator = (left[0] - right[0]) - (left[1] - right[1])
            if denominator == 0:
                continue
            weight = (right[1] - right[0]) / denominator
            if not 0 <= weight <= 1:
                continue
            first = weight * left[0] + (1 - weight) * right[0]
            second = weight * left[1] + (1 - weight) * right[1]
            assert first == second
            best = min(best, first)
    return best


def test_complete_prefix_shape_enumeration_is_exact_on_small_alphabets():
    assert {shape.lengths for shape in complete_prefix_shapes(1)} == {(0,)}
    assert {shape.lengths for shape in complete_prefix_shapes(2)} == {(1, 1)}
    assert {shape.lengths for shape in complete_prefix_shapes(3)} == {
        (1, 2, 2),
        (2, 1, 2),
        (2, 2, 1),
    }
    four = complete_prefix_shapes(4)
    assert len(four) == 13
    assert (2, 2, 2, 2) in {shape.lengths for shape in four}
    assert all(shape.valid for shape in four)
    assert canonical_codewords_from_lengths((1, 2, 3, 3)) == (
        "0",
        "10",
        "110",
        "111",
    )


def test_exact_zero_sum_game_matches_matching_pennies_value():
    certificate = solve_exact_zero_sum_game(
        (
            (Fraction(0), Fraction(1)),
            (Fraction(1), Fraction(0)),
        )
    )
    assert certificate.valid
    assert certificate.value == Fraction(1, 2)
    assert certificate.code_mixture == (Fraction(1, 2), Fraction(1, 2))
    assert certificate.scenario_mixture == (
        Fraction(1, 2),
        Fraction(1, 2),
    )
    assert certificate.gap == 0


def test_k3_shared_randomness_strictly_improves_robust_mean_and_regret():
    certificate = k3_shared_randomness_example()
    assert certificate.valid
    assert certificate.oracle_costs == (Fraction(6, 5), Fraction(6, 5))
    assert certificate.deterministic_minimax_value == Fraction(19, 10)
    assert certificate.deterministic_regret_value == Fraction(7, 10)
    assert certificate.mixed_minimax_value == Fraction(31, 20)
    assert certificate.mixed_regret_value == Fraction(7, 20)
    assert certificate.randomization_length_gain == Fraction(7, 20)
    assert certificate.randomization_regret_gain == Fraction(7, 20)
    assert certificate.mixed_minimax.code_mixture == (
        Fraction(1, 2),
        Fraction(1, 2),
    )
    assert certificate.mixed_minimax.scenario_mixture == (
        Fraction(1, 2),
        Fraction(1, 2),
    )
    assert certificate.least_favorable_prior == (
        Fraction(9, 20),
        Fraction(9, 20),
        Fraction(1, 10),
    )
    assert len(certificate.mixed_code_support) == 2
    assert len(certificate.mixed_code_support) <= 2
    assert certificate.fixed_length_upper_bound == 2


def test_k4_deterministic_robust_tree_is_not_an_oracle_huffman_tree():
    certificate = k4_nonoracle_minimax_example()
    assert certificate.valid
    assert certificate.oracle_costs == (Fraction(3, 2), Fraction(3, 2))
    assert certificate.deterministic_minimax_value == 2
    assert certificate.deterministic_minimax_candidate.state_lengths == (
        2,
        2,
        2,
        2,
    )
    assert all(
        expected_length_under_prior(candidate=certificate.deterministic_minimax_candidate, prior=prior)
        > oracle
        for prior, oracle in zip(certificate.enumeration.priors, certificate.oracle_costs)
    )
    assert certificate.deterministic_regret_value == Fraction(1, 2)
    assert certificate.mixed_minimax_value == Fraction(9, 5)
    assert certificate.mixed_regret_value == Fraction(3, 10)
    assert certificate.least_favorable_prior == (
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(2, 5),
        Fraction(2, 5),
    )


def test_one_scenario_robust_solver_reduces_to_nominal_prior_optimum():
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
    robust = exact_finite_prior_robust_code(graph, (prior,))
    assert robust.valid
    assert robust.oracle_costs == (nominal.expected_length,)
    assert robust.deterministic_minimax_value == nominal.expected_length
    assert robust.mixed_minimax_value == nominal.expected_length
    assert robust.deterministic_regret_value == 0
    assert robust.mixed_regret_value == 0


def test_convex_hull_prior_cost_is_the_same_convex_combination():
    certificate = k3_shared_randomness_example()
    weights = (Fraction(1, 3), Fraction(2, 3))
    barycenter = convex_combination_prior(certificate.enumeration.priors, weights)
    candidate = certificate.deterministic_minimax_candidate
    direct = expected_length_under_prior(candidate, barycenter)
    combined = sum(
        weight * cost
        for weight, cost in zip(weights, candidate.scenario_costs)
    )
    assert direct == combined

    mixed_direct = mixed_expected_length_under_prior(
        certificate,
        certificate.mixed_minimax.code_mixture,
        barycenter,
    )
    mixed_combined = sum(
        weight * cost
        for weight, cost in zip(weights, certificate.mixed_minimax.scenario_costs)
    )
    assert mixed_direct == mixed_combined
    assert mixed_direct <= max(certificate.mixed_minimax.scenario_costs)


def test_all_labeled_four_vertex_graphs_match_independent_robust_enumeration():
    priors = (
        (Fraction(1, 10), Fraction(2, 10), Fraction(3, 10), Fraction(4, 10)),
        (Fraction(4, 10), Fraction(3, 10), Fraction(2, 10), Fraction(1, 10)),
    )
    for edge_mask in range(1 << 6):
        graph = _graph_from_edge_mask(4, edge_mask)
        direct_costs = _direct_cost_vectors(graph, priors)
        oracle = tuple(
            min(cost[scenario] for cost in direct_costs)
            for scenario in range(2)
        )
        direct_deterministic = min(max(cost) for cost in direct_costs)
        direct_regret = min(
            max(cost[scenario] - oracle[scenario] for scenario in range(2))
            for cost in direct_costs
        )
        direct_mixed = _two_scenario_mixed_value(direct_costs)
        direct_mixed_regret = _two_scenario_mixed_value(
            tuple(
                tuple(cost[scenario] - oracle[scenario] for scenario in range(2))
                for cost in direct_costs
            )
        )

        certificate = exact_finite_prior_robust_code(
            graph,
            priors,
            max_vertices=6,
            max_partitions=100_000,
            max_candidates=100_000,
            max_dominance_pairs=1_000_000,
        )
        assert certificate.oracle_costs == oracle
        assert certificate.deterministic_minimax_value == direct_deterministic
        assert certificate.deterministic_regret_value == direct_regret
        assert certificate.mixed_minimax_value == direct_mixed
        assert certificate.mixed_regret_value == direct_mixed_regret


def test_search_and_mixture_validation_fail_closed():
    graph = ConfusionGraph.from_edges(
        (0, 1, 2),
        ((0, 1), (0, 2), (1, 2)),
    )
    priors = (
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
    )
    with pytest.raises(ValueError):
        complete_prefix_shapes(5, max_prefix_assignments=100)
    with pytest.raises(ValueError, match="no exact optimum"):
        exact_finite_prior_robust_code(graph, priors, max_candidates=1)
    with pytest.raises(ValueError):
        solve_exact_zero_sum_game(((0, 1), (1, 0)), max_bases=1)
    with pytest.raises(ValueError):
        exact_finite_prior_robust_code(graph, ())

    certificate = k3_shared_randomness_example()
    with pytest.raises(ValueError):
        mixed_expected_length_under_prior(
            certificate,
            (Fraction(1),),
            priors[0],
        )
    with pytest.raises(ValueError):
        mixed_expected_length_under_prior(
            certificate,
            (Fraction(2), Fraction(-1)),
            priors[0],
        )
