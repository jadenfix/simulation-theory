from fractions import Fraction
from itertools import combinations, product

import pytest

from simtheory.confusion_graphs import (
    ConfusionGraph,
    binary_pair_problem,
    coloring_is_proper,
)
from simtheory.prior_weighted_codes import (
    exact_entropy_order_product,
    exact_prior_weighted_function_code,
    exact_prior_weighted_prefix_code,
    optimal_binary_prefix_code,
    positive_support_code_certificate,
    prefix_free,
    prior_weighted_edge_deletion_certificate,
    richer_than_chromatic_example,
    validate_rational_prior,
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
    result = []
    for color in colors:
        result.append(renaming.setdefault(color, len(renaming)))
    return tuple(result)


def _brute_prefix_cost(probabilities):
    count = len(probabilities)
    if count == 1:
        return Fraction(0)
    best = None
    # Every full binary tree with k leaves has maximum depth at most k-1.
    # Kraft's inequality is also sufficient for the existence of a binary
    # prefix code, so this independently audits Huffman on the bounded cases.
    for lengths in product(range(1, count), repeat=count):
        if sum(Fraction(1, 1 << length) for length in lengths) > 1:
            continue
        cost = sum(
            probability * length
            for probability, length in zip(probabilities, lengths)
        )
        if best is None or cost < best:
            best = cost
    assert best is not None
    return best


def _brute_graph_prefix_optimum(graph, prior):
    count = graph.vertex_count
    seen = set()
    best = None
    for raw_colors in product(range(count), repeat=count):
        colors = _canonical_coloring(raw_colors)
        if colors in seen:
            continue
        seen.add(colors)
        if not coloring_is_proper(graph, colors):
            continue
        message_count = len(set(colors))
        masses = tuple(
            sum(
                (prior[index] for index, color in enumerate(colors) if color == message),
                Fraction(0),
            )
            for message in range(message_count)
        )
        cost = _brute_prefix_cost(masses)
        if best is None or cost < best:
            best = cost
    assert best is not None
    return best


def test_exact_huffman_matches_independent_kraft_enumeration():
    distributions = (
        (Fraction(1),),
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)),
        (Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(6, 25), Fraction(16, 25), Fraction(1, 50), Fraction(1, 10)),
    )
    for probabilities in distributions:
        certificate = optimal_binary_prefix_code(probabilities)
        assert certificate.valid
        assert prefix_free(certificate.codewords)
        assert certificate.expected_length == _brute_prefix_cost(probabilities)


def test_skew_complete_graph_separates_mean_peak_and_fixed_length():
    graph = ConfusionGraph.from_edges(
        tuple(range(4)),
        tuple(combinations(range(4), 2)),
    )
    certificate = exact_prior_weighted_prefix_code(
        graph,
        (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)),
    )
    assert certificate.valid
    assert certificate.chromatic_number == 4
    assert certificate.fixed_length_bits == 2
    assert certificate.expected_length == Fraction(3, 2)
    assert certificate.maximum_codeword_length == 3
    assert certificate.expected_length < certificate.fixed_length_bits
    assert certificate.maximum_codeword_length > certificate.fixed_length_bits


def test_expected_optimum_can_use_more_messages_than_chromatic_number():
    graph, prior = richer_than_chromatic_example()
    certificate = exact_prior_weighted_prefix_code(graph, prior)
    assert certificate.valid
    assert certificate.chromatic_number == 3
    assert certificate.expected_optimal_message_count == 4
    assert certificate.expected_length == Fraction(37, 25)
    frontier = {point.message_count: point for point in certificate.message_count_frontier}
    assert frontier[3].exact_best_expected_length == Fraction(38, 25)
    assert frontier[4].exact_best_expected_length == Fraction(37, 25)
    assert frontier[5].exact_best_expected_length == Fraction(21, 10)
    assert certificate.expected_optimal_code.partition == (
        (0,),
        (1, 4),
        (2,),
        (3,),
    )


def test_uniform_five_cycle_has_exact_eight_fifths_cost():
    graph = ConfusionGraph.from_edges(
        tuple(range(5)),
        ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0)),
    )
    certificate = exact_prior_weighted_prefix_code(
        graph,
        (Fraction(1, 5),) * 5,
    )
    assert certificate.valid
    assert certificate.chromatic_number == 3
    assert certificate.expected_length == Fraction(8, 5)
    assert sorted(certificate.expected_optimal_code.class_probabilities) == [
        Fraction(1, 5),
        Fraction(2, 5),
        Fraction(2, 5),
    ]


def test_all_labeled_four_vertex_graphs_match_direct_enumeration():
    prior = (Fraction(1, 10), Fraction(2, 10), Fraction(3, 10), Fraction(4, 10))
    for edge_mask in range(1 << 6):
        graph = _graph_from_edge_mask(4, edge_mask)
        certificate = exact_prior_weighted_prefix_code(
            graph,
            prior,
            max_vertices=6,
            max_partitions=100_000,
        )
        assert certificate.expected_length == _brute_graph_prefix_optimum(
            graph,
            prior,
        )


def test_exact_entropy_ordering_uses_rational_product_not_float_sorting():
    denominator = 4
    uniform = (Fraction(1, 2), Fraction(1, 2))
    skew = (Fraction(3, 4), Fraction(1, 4))
    # Larger product means lower entropy because Q=2^(-D H).
    assert exact_entropy_order_product(skew, denominator) > exact_entropy_order_product(
        uniform,
        denominator,
    )


def test_edge_deletion_cannot_increase_prior_weighted_optimum():
    original = ConfusionGraph.from_edges(
        tuple(range(4)),
        tuple(combinations(range(4), 2)),
    )
    reduced = ConfusionGraph.from_edges(
        tuple(range(4)),
        ((0, 1), (1, 2), (2, 3), (3, 0)),
    )
    certificate = prior_weighted_edge_deletion_certificate(
        original,
        reduced,
        (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)),
    )
    assert certificate.valid
    assert certificate.reduced.expected_length <= certificate.original.expected_length


def test_zero_mass_states_depend_on_declared_error_convention():
    graph = ConfusionGraph.from_edges(
        tuple(range(3)),
        tuple(combinations(range(3), 2)),
    )
    certificate = positive_support_code_certificate(graph, (1, 0, 0))
    assert certificate.valid
    # Strong zero error still assigns codewords to the two zero-mass states.
    assert certificate.declared_state_code.expected_length == 1
    # Almost-sure zero error on the positive support sees one state and needs no bit.
    assert certificate.support_only_code.expected_length == 0


def test_function_problem_wrapper_preserves_exact_decodability():
    problem = binary_pair_problem(complementary_side_information=True)
    certificate = exact_prior_weighted_function_code(
        problem,
        (Fraction(1, 4),) * 4,
    )
    assert certificate.valid
    assert certificate.deterministic_message_code_valid
    assert certificate.weighted_code.expected_length == 1


def test_validation_and_search_caps_fail_closed():
    graph = ConfusionGraph.from_edges((0, 1), ((0, 1),))
    with pytest.raises(ValueError):
        validate_rational_prior(graph, (0.4, 0.6))
    with pytest.raises(ValueError):
        validate_rational_prior(graph, (Fraction(1, 3), Fraction(1, 3)))
    with pytest.raises(ValueError):
        exact_prior_weighted_prefix_code(
            graph,
            (Fraction(1, 2), Fraction(1, 2)),
            max_vertices=1,
        )
    with pytest.raises(ValueError, match="no exact optimum"):
        exact_prior_weighted_prefix_code(
            ConfusionGraph.from_edges(tuple(range(5)), ()),
            (Fraction(1, 5),) * 5,
            max_partitions=2,
        )
