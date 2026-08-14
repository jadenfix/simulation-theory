from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.coupled_drift import (
    common_cost_ordering,
    enumerate_coupled_drift_path_polytope,
    exact_precommitted_code_sequence,
    optimize_coupled_drift_costs,
)
from simtheory.distributionally_robust_codes import total_variation_distance


def complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    edges = tuple(
        (left, right)
        for left in range(vertex_count)
        for right in range(left + 1, vertex_count)
    )
    return ConfusionGraph.from_edges(vertices, edges)


def test_coupled_two_state_objectives_can_make_marginal_extrema_incompatible():
    polytope = enumerate_coupled_drift_path_polytope(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1, 4),
        2,
    )
    certificate = optimize_coupled_drift_costs(
        polytope,
        (
            (0, 1),
            (1, 0),
        ),
    )
    assert certificate.valid
    assert certificate.primal_value == certificate.dual_value == Fraction(5, 4)
    assert certificate.marginal_upper_bound == Fraction(7, 4)
    assert certificate.marginal_relaxation_gap == Fraction(1, 2)
    previous = polytope.initial_prior
    for distribution, budget in zip(
        certificate.optimal_path,
        polytope.drift_budgets,
    ):
        assert total_variation_distance(previous, distribution) <= budget
        previous = distribution


def test_coupled_value_matches_independent_marginals_for_identical_ordering():
    polytope = enumerate_coupled_drift_path_polytope(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1, 4),
        2,
    )
    certificate = optimize_coupled_drift_costs(
        polytope,
        (
            (0, 1),
            (0, 1),
        ),
    )
    assert common_cost_ordering(certificate.cost_vectors)
    assert certificate.primal_value == Fraction(7, 4)
    assert certificate.marginal_upper_bound == Fraction(7, 4)
    assert certificate.marginal_relaxation_gap == 0


def test_two_state_coupled_value_matches_independent_rational_grid_audit():
    polytope = enumerate_coupled_drift_path_polytope(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1, 4),
        2,
    )
    certificate = optimize_coupled_drift_costs(
        polytope,
        ((0, 1), (1, 0)),
    )
    grid = tuple(Fraction(index, 16) for index in range(17))
    brute = max(
        x1 + (1 - x2)
        for x1 in grid
        for x2 in grid
        if abs(x1 - Fraction(1, 2)) <= Fraction(1, 4)
        and abs(x2 - x1) <= Fraction(1, 4)
    )
    assert brute == certificate.primal_value == Fraction(5, 4)


def test_rotating_k3_short_leaf_beats_every_static_code_under_drift():
    graph = complete_graph(3)
    certificate = exact_precommitted_code_sequence(
        graph,
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
    )
    assert certificate.valid
    assert certificate.selected_total_value == Fraction(11, 3)
    assert certificate.static_total_value == Fraction(23, 6)
    assert certificate.reconfiguration_gain == Fraction(1, 6)
    assert certificate.selected_evaluation.switch_count == 1
    assert certificate.coupled_relaxation_gap == Fraction(1, 6)
    assert certificate.selected_evaluation.cost_vectors[0] != (
        certificate.selected_evaluation.cost_vectors[1]
    )


def test_switching_penalty_has_exact_one_sixth_phase_boundary():
    graph = complete_graph(3)
    at_boundary = exact_precommitted_code_sequence(
        graph,
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 6),
    )
    above = exact_precommitted_code_sequence(
        graph,
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 5),
    )
    assert at_boundary.valid and above.valid
    assert at_boundary.selected_total_value == Fraction(23, 6)
    assert at_boundary.selected_evaluation.switch_count == 0
    assert above.selected_total_value == Fraction(23, 6)
    assert above.selected_evaluation.switch_count == 0


def test_zero_switch_budget_reproduces_static_sequence_baseline():
    graph = complete_graph(3)
    certificate = exact_precommitted_code_sequence(
        graph,
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
        max_switches=0,
    )
    assert certificate.valid
    assert certificate.selected_total_value == certificate.static_total_value
    assert certificate.selected_total_value == Fraction(23, 6)
    assert certificate.selected_evaluation.switch_count == 0


def test_one_state_path_is_well_defined_and_has_zero_dual_support():
    polytope = enumerate_coupled_drift_path_polytope((1,), Fraction(1, 3), 3)
    certificate = optimize_coupled_drift_costs(
        polytope,
        ((2,), (5,), (7,)),
    )
    assert polytope.valid and certificate.valid
    assert certificate.optimal_path == ((Fraction(1),),) * 3
    assert certificate.primal_value == 14
    assert certificate.dual_value == 14
    assert not certificate.dual_support


def test_common_ordering_detects_rotating_preferences():
    assert common_cost_ordering(((1, 2, 3), (4, 6, 9)))
    assert not common_cost_ordering(((1, 2, 3), (2, 1, 3)))
