from fractions import Fraction
from itertools import combinations, product

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.coupled_drift import (
    brute_force_two_state_path_grid,
    exact_coupled_drift_path,
    exact_precommitted_code_sequence,
)
from simtheory.drifting_priors import exact_drift_path_cost


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def test_antagonistic_period_costs_have_strict_coupling_gap():
    prior = (Fraction(1, 2), Fraction(1, 2))
    costs = ((0, 1), (1, 0))
    certificate = exact_coupled_drift_path(prior, costs, Fraction(1, 4))

    assert certificate.valid
    assert certificate.objective_value == Fraction(5, 4)
    assert certificate.dual_value == Fraction(5, 4)
    assert certificate.marginal_envelope == Fraction(7, 4)
    assert certificate.coupling_gap == Fraction(1, 2)
    assert not certificate.marginal_extrema_path_feasible
    assert certificate.extremal_path == (
        (Fraction(1, 4), Fraction(3, 4)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    assert len(certificate.dual_support) <= certificate.polytope.dimension
    assert brute_force_two_state_path_grid(
        Fraction(1, 2),
        costs,
        Fraction(1, 4),
        4,
    ) == Fraction(5, 4)


def test_fixed_cost_vector_recovers_nested_static_drift_identity():
    prior = (Fraction(1, 2), Fraction(1, 2))
    costs = ((0, 1),) * 3
    eta = Fraction(1, 4)

    coupled = exact_coupled_drift_path(prior, costs, eta)
    static = exact_drift_path_cost(prior, (0, 1), eta, 3)

    assert coupled.valid and static.valid
    assert coupled.objective_value == Fraction(11, 4)
    assert coupled.objective_value == static.cumulative_worst_cost
    assert coupled.marginal_envelope == coupled.objective_value
    assert coupled.coupling_gap == 0
    assert coupled.marginal_extrema_path_feasible


def test_two_state_solver_matches_complete_quarter_grid_on_many_cost_sequences():
    prior = (Fraction(1, 2), Fraction(1, 2))
    eta = Fraction(1, 4)
    vectors = ((0, 0), (0, 1), (1, 0), (1, 2), (2, 1))
    for first, second in product(vectors, repeat=2):
        exact = exact_coupled_drift_path(prior, (first, second), eta)
        brute = brute_force_two_state_path_grid(
            Fraction(1, 2),
            (first, second),
            eta,
            4,
        )
        assert exact.valid
        assert exact.objective_value == brute
        assert exact.objective_value <= exact.marginal_envelope


def test_k3_rotating_short_leaf_beats_every_static_code():
    graph = _complete_graph(3)
    prior = (Fraction(1, 3),) * 3
    certificate = exact_precommitted_code_sequence(
        graph,
        prior,
        Fraction(1, 6),
        2,
    )

    assert certificate.valid
    assert certificate.static_best_value == Fraction(23, 6)
    assert certificate.total_value == Fraction(11, 3)
    assert certificate.sequence_gain_over_static == Fraction(1, 6)
    assert certificate.switching_count == 1
    lengths = tuple(candidate.scenario_costs for candidate in certificate.selected_candidates)
    assert lengths[0] != lengths[1]
    assert all(sorted(vector) == [1, 2, 2] for vector in lengths)
    assert certificate.selected_path.coupling_gap > 0


def test_switching_cost_phase_boundary_is_exactly_one_sixth():
    graph = _complete_graph(3)
    prior = (Fraction(1, 3),) * 3

    below = exact_precommitted_code_sequence(
        graph,
        prior,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 7),
    )
    boundary = exact_precommitted_code_sequence(
        graph,
        prior,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 6),
    )

    assert below.valid and boundary.valid
    assert below.switching_count == 1
    assert below.total_value == Fraction(11, 3) + Fraction(1, 7)
    assert below.total_value < below.static_best_value

    # At equality the implementation's deterministic tie break prefers the
    # lower-reconfiguration static sequence.
    assert boundary.switching_count == 0
    assert boundary.total_value == boundary.static_best_value == Fraction(23, 6)


def test_validation_and_search_caps_are_explicit():
    with pytest.raises(ValueError):
        exact_coupled_drift_path((1,), ((0,),), 0)
    with pytest.raises(ValueError):
        exact_coupled_drift_path((Fraction(1, 2), Fraction(1, 2)), ((0, 1),), Fraction(2))
    with pytest.raises(ValueError):
        exact_precommitted_code_sequence(
            _complete_graph(3),
            (Fraction(1, 3),) * 3,
            Fraction(1, 6),
            3,
            max_sequences=1,
        )