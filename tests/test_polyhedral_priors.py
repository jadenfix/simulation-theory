from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.polyhedral_priors import (
    LinearPriorConstraint,
    enumerate_prior_polytope,
    exact_polyhedral_robust_prefix_code,
    extremal_expectation,
    huber_contamination_polytope,
    interval_prior_polytope,
)


def complete_graph(n: int) -> ConfusionGraph:
    vertices = tuple(range(n))
    edges = tuple((i, j) for i in range(n) for j in range(i + 1, n))
    return ConfusionGraph.from_edges(vertices, edges)


def test_simplex_has_exact_basis_vertices():
    poly = enumerate_prior_polytope(3, ())
    assert poly.valid
    assert set(poly.distributions) == {
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
    }


def test_interval_prior_vertices_and_extremal_expectation():
    poly = interval_prior_polytope(
        (Fraction(1, 10),) * 3,
        (Fraction(4, 5),) * 3,
    )
    expected = {
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
        (Fraction(1, 10), Fraction(1, 10), Fraction(4, 5)),
    }
    assert set(poly.distributions) == expected
    cert = extremal_expectation(poly, (1, 2, 4))
    assert cert.valid
    assert cert.optimum == Fraction(7, 2)
    assert cert.optimizer == (Fraction(1, 10), Fraction(1, 10), Fraction(4, 5))


def test_general_halfspace_can_cut_simplex():
    poly = enumerate_prior_polytope(
        3,
        (
            LinearPriorConstraint.from_values((1, 0, 0), Fraction(1, 2), "q0 cap"),
        ),
    )
    assert poly.valid
    assert (Fraction(1, 2), Fraction(1, 2), Fraction(0)) in poly.distributions
    assert (Fraction(1, 2), Fraction(0), Fraction(1, 2)) in poly.distributions
    assert (Fraction(0), Fraction(1), Fraction(0)) in poly.distributions
    assert (Fraction(0), Fraction(0), Fraction(1)) in poly.distributions


def test_huber_polytope_is_exact_affine_contamination_set():
    p = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    poly = huber_contamination_polytope(p, Fraction(1, 10))
    assert poly.valid
    # Its vertices are (1-e)p + e e_i.
    expected = {
        tuple(Fraction(9, 10) * p[j] + (Fraction(1, 10) if i == j else 0) for j in range(4))
        for i in range(4)
    }
    assert set(poly.distributions) == expected
    cert = extremal_expectation(poly, (1, 2, 3, 3))
    assert cert.optimum == Fraction(33, 20)


def test_symmetric_k3_interval_robust_length_and_regret_games():
    graph = complete_graph(3)
    poly = interval_prior_polytope(
        (Fraction(1, 10),) * 3,
        (Fraction(4, 5),) * 3,
    )
    length = exact_polyhedral_robust_prefix_code(graph, poly, criterion="length")
    regret = exact_polyhedral_robust_prefix_code(graph, poly, criterion="regret")
    assert length.valid and regret.valid
    assert length.deterministic_value == Fraction(19, 10)
    assert length.shared_value == Fraction(5, 3)
    assert length.randomization_gain == Fraction(7, 30)
    # Each skew vertex has nominal K3 Huffman optimum 6/5.
    assert regret.oracle_costs == (Fraction(6, 5),) * 3
    assert regret.deterministic_value == Fraction(7, 10)
    assert regret.shared_value == Fraction(7, 15)


def test_singleton_ambiguity_has_zero_minimax_regret():
    graph = complete_graph(3)
    p = (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10))
    poly = interval_prior_polytope(p, p)
    regret = exact_polyhedral_robust_prefix_code(graph, poly, criterion="regret")
    assert regret.valid
    assert regret.deterministic_value == 0
    assert regret.shared_value == 0


def test_empty_interval_set_is_detected_without_fake_optimum():
    poly = interval_prior_polytope(
        (Fraction(3, 5), Fraction(3, 5)),
        (Fraction(1), Fraction(1)),
    )
    assert poly.valid
    assert poly.empty
