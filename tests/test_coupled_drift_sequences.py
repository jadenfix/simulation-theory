from fractions import Fraction

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.coupled_drift_sequences import (
    enumerate_drift_path_polytope,
    exact_coupled_drift_cost,
    exact_precommitted_code_sequence,
)


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in range(count)
            for right in range(left + 1, count)
        ),
    )


def test_time_varying_costs_have_a_strict_coupling_gap():
    certificate = exact_coupled_drift_cost(
        (Fraction(1, 2), Fraction(1, 2)),
        ((0, 1), (1, 0)),
        Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.optimum == Fraction(5, 4)
    assert certificate.dual_value == Fraction(5, 4)
    assert certificate.marginal_relaxation_value == Fraction(7, 4)
    assert certificate.coupling_gap == Fraction(1, 2)
    assert len(certificate.dual_support) <= certificate.polytope.dimension


def test_fixed_cost_sequence_recovers_nested_marginal_extrema():
    certificate = exact_coupled_drift_cost(
        (Fraction(1, 2), Fraction(1, 2)),
        ((0, 1),) * 4,
        Fraction(1, 10),
    )
    assert certificate.valid
    assert certificate.optimum == 3
    assert certificate.marginal_relaxation_value == 3
    assert certificate.coupling_gap == 0


def test_zero_drift_reduces_to_repeated_nominal_expectations():
    prior = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    costs = ((1, 4, 2), (7, 0, 3), (2, 5, 1))
    certificate = exact_coupled_drift_cost(prior, costs, 0)
    expected = sum(
        (
            sum(
                (probability * value for probability, value in zip(prior, cost)),
                Fraction(0),
            )
            for cost in costs
        ),
        Fraction(0),
    )
    assert certificate.valid
    assert certificate.optimum == expected
    assert all(distribution == prior for distribution in certificate.maximizing_path)


def test_unit_drift_decouples_every_period():
    costs = ((1, 4, 2), (7, 0, 3), (2, 5, 1))
    certificate = exact_coupled_drift_cost(
        (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        costs,
        1,
    )
    assert certificate.valid
    assert certificate.optimum == sum(max(cost) for cost in costs)
    assert certificate.coupling_gap == 0


def test_rotating_k3_short_leaf_beats_every_static_code():
    certificate = exact_precommitted_code_sequence(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
    )
    assert certificate.valid
    assert certificate.robust_value == Fraction(11, 3)
    assert certificate.best_static_value == Fraction(23, 6)
    assert certificate.sequence_gain_over_static == Fraction(1, 6)
    assert certificate.selected_switches == 1
    assert tuple(
        candidate.scenario_costs for candidate in certificate.selected_candidates
    ) in {
        ((1, 2, 2), (2, 1, 2)),
        ((1, 2, 2), (2, 2, 1)),
        ((2, 1, 2), (1, 2, 2)),
        ((2, 1, 2), (2, 2, 1)),
        ((2, 2, 1), (1, 2, 2)),
        ((2, 2, 1), (2, 1, 2)),
    }


def test_switching_cost_has_exact_one_sixth_phase_boundary():
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
    above = exact_precommitted_code_sequence(
        graph,
        prior,
        Fraction(1, 6),
        2,
        switching_penalty=Fraction(1, 5),
    )
    assert below.selected_switches == 1
    assert below.robust_value == Fraction(11, 3) + Fraction(1, 7)
    assert boundary.selected_switches == 0
    assert boundary.robust_value == Fraction(23, 6)
    assert above.selected_switches == 0
    assert above.robust_value == Fraction(23, 6)


def test_path_and_sequence_caps_fail_loudly():
    with pytest.raises(ValueError):
        enumerate_drift_path_polytope(
            (Fraction(1, 3),) * 3,
            Fraction(1, 6),
            2,
            max_bases=10,
        )
    with pytest.raises(ValueError):
        exact_precommitted_code_sequence(
            _complete_graph(3),
            (Fraction(1, 3),) * 3,
            Fraction(1, 6),
            2,
            max_sequences=2,
        )
