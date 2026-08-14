from fractions import Fraction

from simtheory.polyhedral_duals import (
    exact_expectation_primal_dual,
    exact_farkas_infeasibility_certificate,
)
from simtheory.polyhedral_priors import (
    LinearPriorConstraint,
    enumerate_prior_polytope,
    huber_contamination_polytope,
    interval_prior_polytope,
)


def test_empty_interval_polytope_has_exact_sparse_farkas_witness():
    poly = interval_prior_polytope(
        (Fraction(3, 5), Fraction(3, 5)),
        (Fraction(1), Fraction(1)),
    )
    assert poly.empty
    certificate = exact_farkas_infeasibility_certificate(poly)
    assert certificate.valid
    assert certificate.bound_product < 0
    assert certificate.transpose_product == (Fraction(0),)
    assert len(certificate.support) <= poly.dimension + 1


def test_explicit_contradictory_halfspaces_have_farkas_receipt():
    poly = enumerate_prior_polytope(
        3,
        (
            LinearPriorConstraint.from_values((1, 0, 0), Fraction(1, 5), "q0<=1/5"),
            LinearPriorConstraint.from_values((-1, 0, 0), Fraction(-4, 5), "q0>=4/5"),
        ),
    )
    assert poly.empty
    certificate = exact_farkas_infeasibility_certificate(poly)
    assert certificate.valid
    assert sum(certificate.multipliers, Fraction(0)) == 1


def test_interval_expectation_max_and_min_have_zero_exact_duality_gap():
    poly = interval_prior_polytope(
        (Fraction(1, 10),) * 3,
        (Fraction(4, 5),) * 3,
    )
    maximum = exact_expectation_primal_dual(poly, (1, 2, 4), maximize=True)
    minimum = exact_expectation_primal_dual(poly, (1, 2, 4), maximize=False)
    assert maximum.valid and minimum.valid
    assert maximum.primal.optimum == maximum.original_dual_value == Fraction(7, 2)
    assert minimum.primal.optimum == minimum.original_dual_value == Fraction(13, 10)
    assert len(maximum.support) <= poly.dimension
    assert len(minimum.support) <= poly.dimension


def test_huber_k4_generic_dual_matches_33_over_20():
    p = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    poly = huber_contamination_polytope(p, Fraction(1, 10))
    certificate = exact_expectation_primal_dual(poly, (1, 2, 3, 3))
    assert certificate.valid
    assert certificate.primal.optimum == Fraction(33, 20)
    assert certificate.original_dual_value == Fraction(33, 20)


def test_constant_objective_uses_zero_dual_multipliers():
    poly = enumerate_prior_polytope(3, ())
    certificate = exact_expectation_primal_dual(poly, (7, 7, 7))
    assert certificate.valid
    assert certificate.primal.optimum == 7
    assert not certificate.support
    assert all(weight == 0 for weight in certificate.multipliers)
