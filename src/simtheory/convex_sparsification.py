"""Exact rational Caratheodory sparsification for shared robust mixtures.

Finite zero-sum support enumeration bounds an optimal codebook mixture by the
number of adversarial rows.  A continuous TV ball can have many polytope
vertices, so that generic game bound can be much larger than the number of
source states.

The payoff of a shared codebook mixture depends only on its expected state-value
vector.  Caratheodory's theorem therefore gives a dimension-dependent support
bound: a vector in the convex hull of points in Q^d can be represented using at
most d+1 points.  Likewise, a least-favorable prior lies in an (n-1)-dimensional
simplex and needs at most n TV-ball vertices.

This module implements the constructive theorem using exact affine-dependence
elimination.  It returns a rational replay certificate preserving the original
barycenter exactly; no floating rank tolerance is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


def _validate_vectors(
    vectors: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    supplied = tuple(
        tuple(Fraction(coordinate) for coordinate in vector)
        for vector in vectors
    )
    if not supplied:
        raise ValueError("at least one convex-hull point is required")
    dimension = len(supplied[0])
    if any(len(vector) != dimension for vector in supplied):
        raise ValueError("convex-hull points must have equal dimension")
    return supplied


def _validate_weights(
    weights: Sequence[Fraction],
    point_count: int,
) -> tuple[Fraction, ...]:
    supplied = tuple(Fraction(weight) for weight in weights)
    if len(supplied) != point_count:
        raise ValueError("one convex weight is required per point")
    if any(weight < 0 for weight in supplied):
        raise ValueError("convex weights must be nonnegative")
    if sum(supplied, Fraction(0)) != 1:
        raise ValueError("convex weights must sum exactly to one")
    return supplied


def convex_barycenter(
    vectors: Sequence[Sequence[Fraction]],
    weights: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    points = _validate_vectors(vectors)
    supplied_weights = _validate_weights(weights, len(points))
    return tuple(
        sum(
            (
                weight * point[coordinate]
                for weight, point in zip(supplied_weights, points)
            ),
            Fraction(0),
        )
        for coordinate in range(len(points[0]))
    )


def _rref_null_vector(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[Fraction, ...]:
    """Return one nonzero exact null vector of a wide rational matrix."""

    rows = [list(Fraction(value) for value in row) for row in matrix]
    if not rows:
        raise ValueError("nullspace matrix must have at least one row")
    width = len(rows[0])
    if width < 2 or any(len(row) != width for row in rows):
        raise ValueError("nullspace matrix must be rectangular and nontrivial")

    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot_value for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(rows[row], rows[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    free_columns = tuple(
        column for column in range(width) if column not in set(pivot_columns)
    )
    if not free_columns:
        raise ValueError("matrix has trivial nullspace")
    selected_free = free_columns[0]
    solution = [Fraction(0)] * width
    solution[selected_free] = Fraction(1)
    for row_index in range(len(pivot_columns) - 1, -1, -1):
        pivot_column = pivot_columns[row_index]
        solution[pivot_column] = -sum(
            (
                rows[row_index][column] * solution[column]
                for column in range(pivot_column + 1, width)
            ),
            Fraction(0),
        )
    result = tuple(solution)
    if all(value == 0 for value in result):
        raise AssertionError("constructed null vector is zero")
    for row in matrix:
        if sum(
            (Fraction(value) * coefficient for value, coefficient in zip(row, result)),
            Fraction(0),
        ) != 0:
            raise AssertionError("constructed vector is not in the nullspace")
    return result


def _affine_dependence(
    vectors: Sequence[Sequence[Fraction]],
) -> tuple[Fraction, ...]:
    points = _validate_vectors(vectors)
    matrix = [
        [Fraction(1) for _ in points],
        *[
            [point[coordinate] for point in points]
            for coordinate in range(len(points[0]))
        ],
    ]
    dependence = _rref_null_vector(matrix)
    if sum(dependence, Fraction(0)) != 0:
        raise AssertionError("affine dependence does not preserve normalization")
    if not any(value > 0 for value in dependence):
        dependence = tuple(-value for value in dependence)
    if not any(value > 0 for value in dependence) or not any(
        value < 0 for value in dependence
    ):
        raise AssertionError("nonzero affine dependence needs both signs")
    return dependence


@dataclass(frozen=True)
class CaratheodoryEliminationStep:
    active_indices_before: tuple[int, ...]
    selected_indices: tuple[int, ...]
    affine_dependence: tuple[Fraction, ...]
    step_size: Fraction
    eliminated_indices: tuple[int, ...]

    @property
    def valid(self) -> bool:
        return (
            bool(self.active_indices_before)
            and bool(self.selected_indices)
            and len(self.selected_indices) == len(self.affine_dependence)
            and set(self.selected_indices).issubset(self.active_indices_before)
            and self.step_size > 0
            and bool(self.eliminated_indices)
            and set(self.eliminated_indices).issubset(self.selected_indices)
            and sum(self.affine_dependence, Fraction(0)) == 0
            and any(value > 0 for value in self.affine_dependence)
            and any(value < 0 for value in self.affine_dependence)
        )


@dataclass(frozen=True)
class CaratheodoryCertificate:
    points: tuple[tuple[Fraction, ...], ...]
    original_weights: tuple[Fraction, ...]
    reduced_weights: tuple[Fraction, ...]
    barycenter: tuple[Fraction, ...]
    ambient_dimension: int
    support_bound: int
    steps: tuple[CaratheodoryEliminationStep, ...]

    @property
    def original_support(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, weight in enumerate(self.original_weights)
            if weight > 0
        )

    @property
    def reduced_support(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, weight in enumerate(self.reduced_weights)
            if weight > 0
        )

    @property
    def valid(self) -> bool:
        return (
            bool(self.points)
            and len(self.original_weights) == len(self.points)
            and len(self.reduced_weights) == len(self.points)
            and self.ambient_dimension == len(self.points[0])
            and self.support_bound == self.ambient_dimension + 1
            and all(weight >= 0 for weight in self.original_weights)
            and all(weight >= 0 for weight in self.reduced_weights)
            and sum(self.original_weights, Fraction(0)) == 1
            and sum(self.reduced_weights, Fraction(0)) == 1
            and convex_barycenter(self.points, self.original_weights)
            == self.barycenter
            and convex_barycenter(self.points, self.reduced_weights)
            == self.barycenter
            and len(self.reduced_support) <= self.support_bound
            and len(self.reduced_support) <= len(self.original_support)
            and all(step.valid for step in self.steps)
            and len(self.steps)
            <= max(0, len(self.original_support) - self.support_bound)
        )


def caratheodory_sparsify(
    vectors: Sequence[Sequence[Fraction]],
    weights: Sequence[Fraction],
) -> CaratheodoryCertificate:
    """Preserve one rational barycenter using at most ``dimension+1`` points."""

    points = _validate_vectors(vectors)
    original = _validate_weights(weights, len(points))
    dimension = len(points[0])
    bound = dimension + 1
    current = list(original)
    steps: list[CaratheodoryEliminationStep] = []

    while True:
        active = tuple(index for index, weight in enumerate(current) if weight > 0)
        if len(active) <= bound:
            break
        selected = active[: bound + 1]
        dependence = _affine_dependence(tuple(points[index] for index in selected))
        ratios = tuple(
            current[index] / coefficient
            for index, coefficient in zip(selected, dependence)
            if coefficient > 0
        )
        step_size = min(ratios)
        if step_size <= 0:
            raise AssertionError("Caratheodory elimination step is not positive")
        before = tuple(current)
        for index, coefficient in zip(selected, dependence):
            current[index] -= step_size * coefficient
            if current[index] < 0:
                raise AssertionError("Caratheodory elimination made a weight negative")
        eliminated = tuple(
            index
            for index in selected
            if before[index] > 0 and current[index] == 0
        )
        if not eliminated:
            raise AssertionError("Caratheodory step did not eliminate a support point")
        steps.append(
            CaratheodoryEliminationStep(
                active,
                selected,
                dependence,
                step_size,
                eliminated,
            )
        )

    certificate = CaratheodoryCertificate(
        points,
        original,
        tuple(current),
        convex_barycenter(points, original),
        dimension,
        bound,
        tuple(steps),
    )
    if not certificate.valid:
        raise AssertionError("Caratheodory sparsification certificate failed")
    return certificate


@dataclass(frozen=True)
class SharedTVMixtureSparsificationCertificate:
    codebook_mixture: CaratheodoryCertificate
    vertex_mixture: CaratheodoryCertificate
    mixed_state_lengths: tuple[Fraction, ...]
    least_favorable_prior: tuple[Fraction, ...]
    source_state_count: int

    @property
    def codebook_support_bound(self) -> int:
        return self.source_state_count + 1

    @property
    def vertex_support_bound(self) -> int:
        return self.source_state_count

    @property
    def valid(self) -> bool:
        return (
            self.codebook_mixture.valid
            and self.vertex_mixture.valid
            and self.codebook_mixture.barycenter == self.mixed_state_lengths
            and self.vertex_mixture.barycenter
            == self.least_favorable_prior[:-1]
            and len(self.codebook_mixture.reduced_support)
            <= self.codebook_support_bound
            and len(self.vertex_mixture.reduced_support)
            <= self.vertex_support_bound
        )


def sparsify_shared_tv_certificate(
    certificate: object,
) -> SharedTVMixtureSparsificationCertificate:
    """Sparsify both mixtures in a shared continuous-TV coding certificate.

    The loose ``object`` annotation avoids a module import cycle; the expected
    protocol is checked through the accessed attributes and the resulting exact
    equalities.
    """

    candidates = tuple(certificate.candidates)
    code_points = tuple(
        tuple(Fraction(length) for length in candidate.state_lengths)
        for candidate in candidates
    )
    codebook = caratheodory_sparsify(
        code_points,
        certificate.mixed_game.code_mixture,
    )

    vertex_distributions = tuple(certificate.tv_vertices.vertex_distributions)
    vertex_free_points = tuple(distribution[:-1] for distribution in vertex_distributions)
    vertices = caratheodory_sparsify(
        vertex_free_points,
        certificate.mixed_game.scenario_mixture,
    )
    source_state_count = len(certificate.nominal_prior)
    result = SharedTVMixtureSparsificationCertificate(
        codebook,
        vertices,
        tuple(certificate.mixed_state_lengths),
        tuple(certificate.least_favorable_prior),
        source_state_count,
    )
    if not result.valid:
        raise AssertionError("shared TV mixture sparsification failed validation")
    return result
