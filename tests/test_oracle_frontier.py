from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.oracle_frontier import (
    advance_comparator_frontier,
    comparator_frontier_for_path,
    comparator_oracle_cost_from_frontier,
    exact_frontier_feedback_regret,
    normalized_comparator_frontier,
)


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in vertices
            for right in vertices
            if left < right
        ),
    )


def test_frontier_solver_matches_full_history_feedback_values():
    certificate = exact_frontier_feedback_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        3,
        Fraction(1, 3),
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.delayed_value == certificate.full_history.delayed_value
    assert certificate.current_value == certificate.full_history.current_value
    assert certificate.delayed_frontier_state_count <= certificate.delayed_full_history_state_count
    assert certificate.current_frontier_state_count <= certificate.current_full_history_state_count


def test_frontier_oracle_matches_every_exhaustive_path_oracle():
    certificate = exact_frontier_feedback_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        3,
        Fraction(1, 3),
        2,
        switching_penalty=Fraction(1, 5),
    )
    assert certificate.valid
    full = certificate.full_history
    oracle_map = dict(zip(full.paths, full.path_oracle_costs))
    for path, expected in oracle_map.items():
        frontier = comparator_frontier_for_path(
            path,
            full.absolute.grid.laws,
            full.candidates,
            full.absolute.switching_penalty,
        )
        assert comparator_oracle_cost_from_frontier(frontier) == expected


def test_frontier_update_is_translation_equivariant():
    certificate = exact_frontier_feedback_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        3,
        Fraction(1, 3),
        1,
        switching_penalty=Fraction(1, 4),
    )
    full = certificate.full_history
    law = full.absolute.grid.laws[full.absolute.initial_law_index]
    first = advance_comparator_frontier(
        tuple(),
        law,
        full.candidates,
        full.absolute.switching_penalty,
    )
    shift = Fraction(7, 5)
    shifted = advance_comparator_frontier(
        tuple(value + shift for value in first),
        law,
        full.candidates,
        full.absolute.switching_penalty,
    )
    unshifted = advance_comparator_frontier(
        first,
        law,
        full.candidates,
        full.absolute.switching_penalty,
    )
    assert shifted == tuple(value + shift for value in unshifted)

    baseline, relative = normalized_comparator_frontier(first)
    assert baseline == min(first)
    assert min(relative) == 0
    assert tuple(baseline + value for value in relative) == first
