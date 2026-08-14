from fractions import Fraction

from simtheory.exact_game_pruning import solve_dominance_pruned_zero_sum_game
from simtheory.robust_prior_codes import solve_exact_zero_sum_game


def test_pruned_game_lifts_to_the_full_matrix_with_zero_gap():
    # Row 1 duplicates row 0; row 2 dominates row 0 for the maximizer.
    # Column 2 is pointwise worse than column 1 for the minimizer.
    matrix = (
        (Fraction(1), Fraction(2), Fraction(3)),
        (Fraction(1), Fraction(2), Fraction(3)),
        (Fraction(2), Fraction(2), Fraction(4)),
    )
    certificate = solve_dominance_pruned_zero_sum_game(matrix)
    assert certificate.valid
    assert certificate.row_reduction >= 2
    assert certificate.column_reduction >= 1
    assert certificate.lifted_game.valid
    assert certificate.lifted_game.gap == 0
    assert certificate.lifted_game.cost_matrix == matrix
    assert certificate.value == 2


def test_pruning_matches_direct_exact_solver_when_both_searches_are_small():
    matrix = (
        (Fraction(0), Fraction(2), Fraction(1)),
        (Fraction(2), Fraction(0), Fraction(1)),
        (Fraction(1), Fraction(1), Fraction(1)),
    )
    direct = solve_exact_zero_sum_game(matrix)
    pruned = solve_dominance_pruned_zero_sum_game(matrix)
    assert direct.valid and pruned.valid
    assert pruned.value == direct.value == 1
    assert pruned.lifted_game.gap == 0


def test_no_redundancy_preserves_every_row_and_column():
    matrix = (
        (Fraction(0), Fraction(2)),
        (Fraction(2), Fraction(0)),
    )
    certificate = solve_dominance_pruned_zero_sum_game(matrix)
    assert certificate.valid
    assert certificate.retained_rows == (0, 1)
    assert certificate.retained_columns == (0, 1)
    assert certificate.row_reduction == 0
    assert certificate.column_reduction == 0
    assert certificate.value == 1
