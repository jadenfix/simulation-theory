from itertools import combinations, product

import pytest

from simtheory.confusion_graphs import (
    ConfusionGraph,
    FiniteFunctionDemand,
    FiniteFunctionProblem,
    RandomizedSupportEncoder,
    binary_pair_problem,
    canonicalize_coloring,
    coloring_equivalence_certificate,
    coloring_is_proper,
    confusion_graph,
    confusion_graph_certificate,
    confusion_graph_multicast_certificate,
    deterministic_code_from_coloring,
    encoder_is_zero_error,
    exact_chromatic_certificate,
    greedy_dsatur_coloring,
    maximum_clique,
    maximum_independent_set,
    optimal_function_code,
    parity_coloring_for_binary_pair,
    problem_from_graph,
    randomization_no_benefit_certificate,
    side_information_refinement_certificate,
    target_coarsening_certificate,
)
from simtheory.network_coding import (
    ScalarLinearCode,
    UnitCapacityDAG,
    UnitEdge,
    evaluate_scalar_linear_code,
)


def _brute_chromatic_number(graph: ConfusionGraph) -> int:
    for color_count in range(1, graph.vertex_count + 1):
        for colors in product(range(color_count), repeat=graph.vertex_count):
            if coloring_is_proper(graph, colors):
                return color_count
    raise AssertionError("every finite graph has a vertex coloring")


def _brute_maximum_clique_size(graph: ConfusionGraph) -> int:
    best = 0
    vertices = range(graph.vertex_count)
    for size in range(1, graph.vertex_count + 1):
        for subset in combinations(vertices, size):
            if all(
                (graph.adjacency_masks[left] >> right) & 1
                for left, right in combinations(subset, 2)
            ):
                best = size
    return best


def _brute_maximum_independent_size(graph: ConfusionGraph) -> int:
    best = 0
    vertices = range(graph.vertex_count)
    for size in range(1, graph.vertex_count + 1):
        for subset in combinations(vertices, size):
            if all(
                not ((graph.adjacency_masks[left] >> right) & 1)
                for left, right in combinations(subset, 2)
            ):
                best = size
    return best


def _all_labeled_graphs(vertex_count: int):
    vertices = tuple(range(vertex_count))
    possible_edges = tuple(combinations(vertices, 2))
    for edge_mask in range(1 << len(possible_edges)):
        edges = tuple(
            edge
            for index, edge in enumerate(possible_edges)
            if (edge_mask >> index) & 1
        )
        yield ConfusionGraph.from_edges(vertices, edges)


def test_confusion_graph_witnesses_match_the_function_definition():
    problem = binary_pair_problem(complementary_side_information=True)
    certificate = confusion_graph_certificate(problem)
    graph = certificate.graph
    assert certificate.valid
    assert graph.vertex_count == 4
    assert graph.edge_count == 4

    for left, right in graph.edges():
        witness = certificate.witness(left, right)
        assert witness is not None
        assert problem.side_information(witness.sink, left) == problem.side_information(
            witness.sink,
            right,
        )
        assert problem.target(witness.sink, left) != problem.target(
            witness.sink,
            right,
        )

    # Opposite corners share the parity color and are not confusable.
    assert not graph.adjacent((0, 0), (1, 1))
    assert not graph.adjacent((0, 1), (1, 0))


def test_zero_error_encoder_is_exactly_a_proper_coloring():
    problem = binary_pair_problem(complementary_side_information=True)
    parity = parity_coloring_for_binary_pair(problem)
    certificate = coloring_equivalence_certificate(problem, parity)
    assert certificate.valid
    assert certificate.graph_proper
    assert certificate.encoder_zero_error
    assert certificate.decoder_constructed

    code = deterministic_code_from_coloring(problem, parity)
    assert code.valid
    assert code.message_states == 2
    assert code.fixed_length_bits == 1
    for state in problem.states:
        assert code.answer("t1", state) == state[0]
        assert code.answer("t2", state) == state[1]

    improper = (0, 0, 0, 0)
    bad_certificate = coloring_equivalence_certificate(problem, improper)
    assert bad_certificate.valid
    assert not bad_certificate.graph_proper
    assert not bad_certificate.encoder_zero_error
    assert not bad_certificate.decoder_constructed
    with pytest.raises(ValueError):
        deterministic_code_from_coloring(problem, improper)


def test_side_information_changes_k4_to_c4_and_two_bits_to_one():
    coarse = binary_pair_problem(complementary_side_information=False)
    refined = binary_pair_problem(complementary_side_information=True)
    coarse_graph = confusion_graph(coarse)
    refined_graph = confusion_graph(refined)
    assert coarse_graph.edge_count == 6
    assert refined_graph.edge_count == 4

    coarse_optimal = optimal_function_code(coarse)
    refined_optimal = optimal_function_code(refined)
    assert coarse_optimal.message_states == 4
    assert coarse_optimal.fixed_length_bits == 2
    assert refined_optimal.message_states == 2
    assert refined_optimal.fixed_length_bits == 1

    monotonicity = side_information_refinement_certificate(refined, coarse)
    assert monotonicity.valid
    assert monotonicity.edges_contract
    assert monotonicity.original_chromatic_number == 4
    assert monotonicity.transformed_chromatic_number == 2


def test_target_coarsening_deletes_confusion_edges_and_colors():
    original = binary_pair_problem(complementary_side_information=False)
    states = original.states
    one_coordinate = FiniteFunctionProblem.from_functions(
        states,
        (
            ("t1", lambda state: state[0], lambda _state: None),
            ("t2", lambda _state: 0, lambda _state: None),
        ),
    )
    constants = FiniteFunctionProblem.from_functions(
        states,
        (
            ("t1", lambda _state: 0, lambda _state: None),
            ("t2", lambda _state: 0, lambda _state: None),
        ),
    )

    first = target_coarsening_certificate(one_coordinate, original)
    second = target_coarsening_certificate(constants, one_coordinate)
    assert first.valid
    assert second.valid
    assert first.original_chromatic_number == 4
    assert first.transformed_chromatic_number == 2
    assert second.original_chromatic_number == 2
    assert second.transformed_chromatic_number == 1


def test_c5_needs_three_colors_even_though_largest_clique_has_two():
    cycle = ConfusionGraph.from_edges(
        tuple(range(5)),
        tuple((index, (index + 1) % 5) for index in range(5)),
    )
    certificate = exact_chromatic_certificate(cycle)
    assert certificate.valid
    assert certificate.chromatic_number == 3
    assert certificate.clique_lower_bound == 2
    assert certificate.independence_lower_bound == 3
    assert len(certificate.maximum_independent_vertices) == 2
    assert certificate.fixed_length_bits == 2
    assert coloring_is_proper(cycle, certificate.coloring)


def test_exact_chromatic_clique_and_independence_solvers_match_brute_force():
    # Exhaust every labeled simple graph on four vertices. This independently
    # checks the bounded exact graph algorithms against direct enumeration.
    for graph in _all_labeled_graphs(4):
        certificate = exact_chromatic_certificate(graph)
        assert certificate.chromatic_number == _brute_chromatic_number(graph)
        assert len(maximum_clique(graph)) == _brute_maximum_clique_size(graph)
        assert len(maximum_independent_set(graph)) == _brute_maximum_independent_size(graph)
        assert coloring_is_proper(graph, greedy_dsatur_coloring(graph))


def test_every_finite_simple_graph_is_realized_by_side_information_demands():
    examples = (
        ConfusionGraph.from_edges(tuple(range(5)), ()),
        ConfusionGraph.from_edges(
            tuple(range(5)),
            tuple((index, (index + 1) % 5) for index in range(5)),
        ),
        ConfusionGraph.from_edges(tuple(range(4)), tuple(combinations(range(4), 2))),
    )
    for graph in examples:
        problem = problem_from_graph(graph)
        realized = confusion_graph(problem)
        assert realized.vertices == graph.vertices
        assert realized.adjacency_masks == graph.adjacency_masks
        assert exact_chromatic_certificate(realized).chromatic_number == _brute_chromatic_number(graph)


def test_zero_error_randomization_cannot_reduce_the_message_alphabet():
    graph = confusion_graph(binary_pair_problem(complementary_side_information=True))
    randomized = RandomizedSupportEncoder(
        graph,
        ("a", "b", "c"),
        (
            frozenset((0, 2)),
            frozenset((1,)),
            frozenset((1,)),
            frozenset((0, 2)),
        ),
    )
    assert randomized.zero_error
    certificate = randomization_no_benefit_certificate(randomized)
    assert certificate.valid
    assert coloring_is_proper(graph, certificate.deterministic_coloring)
    assert len(set(certificate.deterministic_coloring)) == 2

    invalid = RandomizedSupportEncoder(
        graph,
        ("a", "b"),
        tuple(frozenset((0, 1)) for _ in graph.vertices),
    )
    assert not invalid.zero_error
    with pytest.raises(ValueError):
        randomization_no_benefit_certificate(invalid)


def _one_symbol_broadcast_certificate():
    network = UnitCapacityDAG(
        ("s", "b", "t1", "t2"),
        (
            UnitEdge("sb", "s", "b"),
            UnitEdge("bt1", "b", "t1"),
            UnitEdge("bt2", "b", "t2"),
        ),
    )
    code = ScalarLinearCode(
        2,
        "s",
        ("t1", "t2"),
        1,
        (
            ("sb", (1,)),
            ("bt1", (1,)),
            ("bt2", (1,)),
        ),
    )
    return evaluate_scalar_linear_code(network, code)


def test_optimal_color_index_multicasts_and_decodes_with_side_information():
    problem = binary_pair_problem(complementary_side_information=True)
    multicast = _one_symbol_broadcast_certificate()
    certificate = confusion_graph_multicast_certificate(problem, multicast)
    assert certificate.valid
    assert certificate.optimal_code.message_states == 2
    assert dict(certificate.color_vectors) == {0: (0,), 1: (1,)}

    for state in problem.states:
        vector = certificate.source_vector(state)
        assert len(vector) == 1
        assert certificate.optimal_code.code.answer("t1", state) == state[0]
        assert certificate.optimal_code.code.answer("t2", state) == state[1]

    no_side = binary_pair_problem(complementary_side_information=False)
    with pytest.raises(ValueError):
        confusion_graph_multicast_certificate(no_side, multicast)


def test_encoder_and_problem_validation_boundaries():
    problem = binary_pair_problem(complementary_side_information=True)
    assert encoder_is_zero_error(problem, parity_coloring_for_binary_pair(problem))
    with pytest.raises(ValueError):
        encoder_is_zero_error(problem, (0, 1))
    with pytest.raises(ValueError):
        canonicalize_coloring((0, -1))
    with pytest.raises(ValueError):
        FiniteFunctionDemand("", (0,), (0,))
    with pytest.raises(ValueError):
        FiniteFunctionDemand("t", (0, 1), (0,))
    with pytest.raises(ValueError):
        FiniteFunctionProblem(
            ((0,), (1,)),
            (
                FiniteFunctionDemand("t", (0, 1), (0, 1)),
                FiniteFunctionDemand("t", (1, 0), (0, 1)),
            ),
        )
    with pytest.raises(ValueError):
        ConfusionGraph((0, 1), (0b10, 0))
    with pytest.raises(ValueError):
        exact_chromatic_certificate(
            ConfusionGraph.from_edges(tuple(range(5)), ()),
            max_vertices=4,
        )
