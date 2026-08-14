from fractions import Fraction
from itertools import product

from simtheory.coupled_drift import (
    enumerate_coupled_drift_path_polytope,
    optimize_coupled_drift_costs,
)


def test_seeded_two_state_grid_never_exceeds_exact_coupled_optimum():
    priors = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 3), Fraction(2, 3)),
    )
    budgets = (Fraction(1, 4), Fraction(1, 3))
    cost_pairs = (
        (((0, 1), (1, 0))),
        (((1, 3), (2, 0))),
        (((2, 1), (0, 4))),
    )
    grid = tuple(Fraction(index, 24) for index in range(25))

    for prior, eta, costs in product(priors, budgets, cost_pairs):
        polytope = enumerate_coupled_drift_path_polytope(prior, eta, 2)
        certificate = optimize_coupled_drift_costs(polytope, costs)
        assert certificate.valid
        brute = max(
            x1 * costs[0][1] + (1 - x1) * costs[0][0]
            + x2 * costs[1][1] + (1 - x2) * costs[1][0]
            for x1 in grid
            for x2 in grid
            if abs(x1 - prior[1]) <= eta and abs(x2 - x1) <= eta
        )
        assert brute <= certificate.primal_value


def test_path_polytope_vertices_are_unique_and_all_constraints_hold():
    polytope = enumerate_coupled_drift_path_polytope(
        (Fraction(1, 3),) * 3,
        (Fraction(1, 6), Fraction(1, 4)),
        2,
    )
    assert polytope.valid
    assert len(set(polytope.paths)) == len(polytope.paths)
    for vertex in polytope.vertices:
        assert all(
            constraint.satisfied(vertex.free_coordinates)
            for constraint in polytope.constraints
        )


def test_larger_drift_budget_cannot_reduce_worst_coupled_cost():
    prior = (Fraction(1, 2), Fraction(1, 2))
    costs = ((0, 1), (1, 0))
    small = optimize_coupled_drift_costs(
        enumerate_coupled_drift_path_polytope(prior, Fraction(1, 8), 2),
        costs,
    )
    large = optimize_coupled_drift_costs(
        enumerate_coupled_drift_path_polytope(prior, Fraction(1, 4), 2),
        costs,
    )
    assert small.valid and large.valid
    assert small.primal_value <= large.primal_value


def test_adding_a_constant_per_period_shifts_value_without_changing_gap():
    polytope = enumerate_coupled_drift_path_polytope(
        (Fraction(1, 2), Fraction(1, 2)),
        Fraction(1, 4),
        2,
    )
    base = optimize_coupled_drift_costs(polytope, ((0, 1), (1, 0)))
    shifted = optimize_coupled_drift_costs(polytope, ((3, 4), (6, 5)))
    assert base.valid and shifted.valid
    assert shifted.primal_value == base.primal_value + 9
    assert shifted.marginal_relaxation_gap == base.marginal_relaxation_gap
