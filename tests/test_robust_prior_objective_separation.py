from fractions import Fraction
from itertools import combinations

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.robust_prior_codes import exact_finite_prior_robust_code


def test_minimax_length_and_minimax_regret_can_select_different_codes():
    graph = ConfusionGraph.from_edges(
        tuple(range(4)),
        tuple(combinations(range(4), 2)),
    )
    certificate = exact_finite_prior_robust_code(
        graph,
        (
            (
                Fraction(1, 10),
                Fraction(1, 10),
                Fraction(1, 10),
                Fraction(7, 10),
            ),
            (
                Fraction(1, 10),
                Fraction(1, 5),
                Fraction(1, 2),
                Fraction(1, 5),
            ),
        ),
    )
    assert certificate.valid
    assert certificate.oracle_costs == (Fraction(3, 2), Fraction(9, 5))

    # Absolute minimax balances both scenarios at two bits.
    assert certificate.deterministic_minimax_value == 2
    assert certificate.deterministic_minimax_candidate.scenario_costs == (2, 2)
    assert certificate.deterministic_minimax_candidate.state_lengths == (2, 2, 2, 2)

    # Regret instead preserves the first scenario's oracle and accepts 21/10
    # in the second: regrets are (0, 3/10), better than the balanced code's
    # regrets (1/2, 1/5).
    assert certificate.deterministic_regret_value == Fraction(3, 10)
    assert certificate.deterministic_regret_candidate.scenario_costs == (
        Fraction(3, 2),
        Fraction(21, 10),
    )
    assert (
        certificate.deterministic_minimax_candidate.state_lengths
        != certificate.deterministic_regret_candidate.state_lengths
    )

    # Shared codebook randomness convexifies both objectives, but by different
    # mixture weights and to different values.
    assert certificate.mixed_minimax_value == Fraction(19, 10)
    assert certificate.mixed_regret_value == Fraction(1, 5)
