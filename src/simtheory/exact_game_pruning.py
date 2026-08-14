"""Exact dominance pruning for finite rational zero-sum games.

The repository's generic exact game solver enumerates primal and dual support
bases.  Its search count can become large when a game contains many duplicated
or pointwise dominated path rows or decision columns.  These redundancies can
be removed without changing the game value:

* the maximizing player never needs row r when another retained row s satisfies
  A[s,c] >= A[r,c] for every retained column c;
* the minimizing player never needs column c when another retained column d
  satisfies A[r,d] <= A[r,c] for every retained row r.

This module iterates exact rational duplicate/dominance elimination, solves the
reduced game, and then lifts the reduced primal and dual mixtures back to the
full matrix.  The lifted ``ExactZeroSumGameCertificate`` independently checks
all original rows and columns, so the pruning procedure is not trusted as an
uncertified shortcut: a wrong elimination would fail full-matrix primal or dual
feasibility or produce a nonzero exact gap.

The pruning receipt also stores one retained pointwise witness for every removed
row and column.  It is finite, exact rational, and fail-closed under the same
support-basis cap as the underlying game solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .robust_prior_codes import (
    ExactZeroSumGameCertificate,
    solve_exact_zero_sum_game,
)

Matrix = tuple[tuple[Fraction, ...], ...]


def _matrix(values: Sequence[Sequence[Fraction]]) -> Matrix:
    matrix = tuple(tuple(Fraction(value) for value in row) for row in values)
    if not matrix or not matrix[0]:
        raise ValueError("zero-sum game matrix must be nonempty")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("zero-sum game matrix must be rectangular")
    return matrix


def _row_dominates(
    matrix: Matrix,
    dominant: int,
    dominated: int,
    columns: Sequence[int],
) -> bool:
    """Whether maximizer row ``dominant`` is no smaller on every kept column."""

    return all(
        matrix[dominant][column] >= matrix[dominated][column]
        for column in columns
    )


def _column_dominates(
    matrix: Matrix,
    dominant: int,
    dominated: int,
    rows: Sequence[int],
) -> bool:
    """Whether minimizer column ``dominant`` is no larger on every kept row."""

    return all(
        matrix[row][dominant] <= matrix[row][dominated]
        for row in rows
    )


def _strict_row_dominates(
    matrix: Matrix,
    dominant: int,
    dominated: int,
    columns: Sequence[int],
) -> bool:
    return _row_dominates(matrix, dominant, dominated, columns) and any(
        matrix[dominant][column] > matrix[dominated][column]
        for column in columns
    )


def _strict_column_dominates(
    matrix: Matrix,
    dominant: int,
    dominated: int,
    rows: Sequence[int],
) -> bool:
    return _column_dominates(matrix, dominant, dominated, rows) and any(
        matrix[row][dominant] < matrix[row][dominated]
        for row in rows
    )


def _prune_indices(matrix: Matrix) -> tuple[tuple[int, ...], tuple[int, ...]]:
    rows = list(range(len(matrix)))
    columns = list(range(len(matrix[0])))

    changed = True
    while changed:
        changed = False

        kept_columns: list[int] = []
        for column in columns:
            removable = False
            for other in columns:
                if other == column:
                    continue
                equal = all(
                    matrix[row][other] == matrix[row][column]
                    for row in rows
                )
                if equal and other < column:
                    removable = True
                    break
                if _strict_column_dominates(
                    matrix,
                    other,
                    column,
                    rows,
                ):
                    removable = True
                    break
            if not removable:
                kept_columns.append(column)
        if len(kept_columns) != len(columns):
            columns = kept_columns
            changed = True

        kept_rows: list[int] = []
        for row in rows:
            removable = False
            for other in rows:
                if other == row:
                    continue
                equal = all(
                    matrix[other][column] == matrix[row][column]
                    for column in columns
                )
                if equal and other < row:
                    removable = True
                    break
                if _strict_row_dominates(
                    matrix,
                    other,
                    row,
                    columns,
                ):
                    removable = True
                    break
            if not removable:
                kept_rows.append(row)
        if len(kept_rows) != len(rows):
            rows = kept_rows
            changed = True

    return tuple(rows), tuple(columns)


def _find_row_witness(
    matrix: Matrix,
    removed: int,
    retained_rows: Sequence[int],
    retained_columns: Sequence[int],
) -> int:
    witnesses = tuple(
        row
        for row in retained_rows
        if _row_dominates(matrix, row, removed, retained_columns)
    )
    if not witnesses:
        raise AssertionError("removed game row has no retained dominance witness")
    return min(witnesses)


def _find_column_witness(
    matrix: Matrix,
    removed: int,
    retained_rows: Sequence[int],
    retained_columns: Sequence[int],
) -> int:
    witnesses = tuple(
        column
        for column in retained_columns
        if _column_dominates(matrix, column, removed, retained_rows)
    )
    if not witnesses:
        raise AssertionError("removed game column has no retained dominance witness")
    return min(witnesses)


@dataclass(frozen=True)
class DominancePrunedGameCertificate:
    original_matrix: Matrix
    retained_rows: tuple[int, ...]
    retained_columns: tuple[int, ...]
    removed_row_witnesses: tuple[tuple[int, int], ...]
    removed_column_witnesses: tuple[tuple[int, int], ...]
    reduced_game: ExactZeroSumGameCertificate
    lifted_game: ExactZeroSumGameCertificate

    @property
    def reduced_matrix(self) -> Matrix:
        return tuple(
            tuple(
                self.original_matrix[row][column]
                for column in self.retained_columns
            )
            for row in self.retained_rows
        )

    @property
    def row_reduction(self) -> int:
        return len(self.original_matrix) - len(self.retained_rows)

    @property
    def column_reduction(self) -> int:
        return len(self.original_matrix[0]) - len(self.retained_columns)

    @property
    def value(self) -> Fraction:
        return self.lifted_game.value

    @property
    def valid(self) -> bool:
        row_count = len(self.original_matrix)
        column_count = len(self.original_matrix[0]) if self.original_matrix else 0
        retained_row_set = set(self.retained_rows)
        retained_column_set = set(self.retained_columns)
        removed_rows = tuple(
            row for row in range(row_count) if row not in retained_row_set
        )
        removed_columns = tuple(
            column
            for column in range(column_count)
            if column not in retained_column_set
        )
        if (
            not self.original_matrix
            or not self.original_matrix[0]
            or any(len(row) != column_count for row in self.original_matrix)
            or not self.retained_rows
            or not self.retained_columns
            or tuple(sorted(set(self.retained_rows))) != self.retained_rows
            or tuple(sorted(set(self.retained_columns))) != self.retained_columns
            or any(not 0 <= row < row_count for row in self.retained_rows)
            or any(
                not 0 <= column < column_count
                for column in self.retained_columns
            )
            or not self.reduced_game.valid
            or not self.lifted_game.valid
            or self.reduced_game.cost_matrix != self.reduced_matrix
            or self.lifted_game.cost_matrix != self.original_matrix
            or self.reduced_game.value != self.lifted_game.value
            or tuple(removed for removed, _ in self.removed_row_witnesses)
            != removed_rows
            or tuple(removed for removed, _ in self.removed_column_witnesses)
            != removed_columns
        ):
            return False

        for removed, witness in self.removed_row_witnesses:
            if (
                witness not in retained_row_set
                or not _row_dominates(
                    self.original_matrix,
                    witness,
                    removed,
                    self.retained_columns,
                )
            ):
                return False
        for removed, witness in self.removed_column_witnesses:
            if (
                witness not in retained_column_set
                or not _column_dominates(
                    self.original_matrix,
                    witness,
                    removed,
                    self.retained_rows,
                )
            ):
                return False

        expected_code_mixture = [Fraction(0)] * column_count
        for reduced_index, original_index in enumerate(self.retained_columns):
            expected_code_mixture[original_index] = self.reduced_game.code_mixture[
                reduced_index
            ]
        expected_scenario_mixture = [Fraction(0)] * row_count
        for reduced_index, original_index in enumerate(self.retained_rows):
            expected_scenario_mixture[original_index] = (
                self.reduced_game.scenario_mixture[reduced_index]
            )
        return (
            self.lifted_game.code_mixture == tuple(expected_code_mixture)
            and self.lifted_game.scenario_mixture
            == tuple(expected_scenario_mixture)
        )


def solve_dominance_pruned_zero_sum_game(
    cost_matrix: Sequence[Sequence[Fraction]],
    *,
    max_bases: int = 2_000_000,
) -> DominancePrunedGameCertificate:
    """Prune exact pointwise redundancies, solve, and lift to the full game."""

    matrix = _matrix(cost_matrix)
    retained_rows, retained_columns = _prune_indices(matrix)
    reduced_matrix = tuple(
        tuple(matrix[row][column] for column in retained_columns)
        for row in retained_rows
    )
    reduced = solve_exact_zero_sum_game(
        reduced_matrix,
        max_bases=max_bases,
    )

    full_code_mixture = [Fraction(0)] * len(matrix[0])
    for reduced_index, original_index in enumerate(retained_columns):
        full_code_mixture[original_index] = reduced.code_mixture[reduced_index]
    full_scenario_mixture = [Fraction(0)] * len(matrix)
    for reduced_index, original_index in enumerate(retained_rows):
        full_scenario_mixture[original_index] = reduced.scenario_mixture[
            reduced_index
        ]

    scenario_costs = tuple(
        sum(
            (
                weight * matrix[row][column]
                for column, weight in enumerate(full_code_mixture)
            ),
            Fraction(0),
        )
        for row in range(len(matrix))
    )
    code_costs = tuple(
        sum(
            (
                weight * matrix[row][column]
                for row, weight in enumerate(full_scenario_mixture)
            ),
            Fraction(0),
        )
        for column in range(len(matrix[0]))
    )
    lifted = ExactZeroSumGameCertificate(
        matrix,
        tuple(full_code_mixture),
        tuple(full_scenario_mixture),
        scenario_costs,
        code_costs,
        reduced.value,
        reduced.primal_bases_examined,
        reduced.dual_bases_examined,
        reduced.configured_basis_cap,
    )
    if not lifted.valid:
        raise AssertionError(
            "dominance-pruned game solution did not lift to a full exact receipt"
        )

    retained_row_set = set(retained_rows)
    retained_column_set = set(retained_columns)
    row_witnesses = tuple(
        (
            row,
            _find_row_witness(
                matrix,
                row,
                retained_rows,
                retained_columns,
            ),
        )
        for row in range(len(matrix))
        if row not in retained_row_set
    )
    column_witnesses = tuple(
        (
            column,
            _find_column_witness(
                matrix,
                column,
                retained_rows,
                retained_columns,
            ),
        )
        for column in range(len(matrix[0]))
        if column not in retained_column_set
    )
    result = DominancePrunedGameCertificate(
        matrix,
        retained_rows,
        retained_columns,
        row_witnesses,
        column_witnesses,
        reduced,
        lifted,
    )
    if not result.valid:
        raise AssertionError("dominance-pruned game certificate failed validation")
    return result
