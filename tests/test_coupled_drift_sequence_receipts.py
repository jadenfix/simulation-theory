from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.coupled_drift import (
    coupled_path_value,
    exact_precommitted_code_sequence,
)


def complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in range(vertex_count)
            for right in range(left + 1, vertex_count)
        ),
    )


def test_every_reported_k3_sequence_cost_replays_against_the_path_polytope():
    certificate = exact_precommitted_code_sequence(
        complete_graph(3),
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
    )
    assert certificate.valid
    for evaluation in certificate.evaluations:
        value, vertex_index = coupled_path_value(
            certificate.path_polytope,
            evaluation.cost_vectors,
        )
        assert value == evaluation.adversarial_path_value
        assert vertex_index == evaluation.maximizing_vertex_index


def test_switch_cost_changes_total_only_through_declared_switch_count():
    graph = complete_graph(3)
    zero = exact_precommitted_code_sequence(
        graph,
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
        switching_penalty=0,
    )
    penalty = Fraction(1, 10)
    priced = exact_precommitted_code_sequence(
        graph,
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
        switching_penalty=penalty,
    )
    by_indices_zero = {item.code_indices: item for item in zero.evaluations}
    by_indices_priced = {item.code_indices: item for item in priced.evaluations}
    assert set(by_indices_zero) == set(by_indices_priced)
    for indices, original in by_indices_zero.items():
        updated = by_indices_priced[indices]
        assert updated.adversarial_path_value == original.adversarial_path_value
        assert updated.total_value == (
            original.adversarial_path_value
            + updated.switch_count * penalty
        )
