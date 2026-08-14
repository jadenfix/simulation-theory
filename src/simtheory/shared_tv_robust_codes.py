"""Shared-randomness zero-error coding against continuous TV prior balls.

A deterministic code has one state-length vector.  If encoder and every decoder
share a source-independent seed, they may instead select a complete
deterministic codebook at random before the source state is encoded.  The
resulting expected state-length vector is a convex combination of deterministic
vectors.

The source-law adversary is modeled as choosing one distribution from a finite
TV ball independently of the realized seed.  Because the payoff is bilinear,
the continuous game is exactly equivalent to a finite zero-sum game against all
vertices of the rational TV-ball polytope.  This module enumerates those
vertices from exact event inequalities, solves the finite game with the
existing rational primal-dual support solver, and independently replays the
continuous TV mass-transport optimum on the mixed expected length vector.

The dual vertex mixture yields a least-favorable barycenter prior in the TV
ball, and the game value equals the nominal optimal prefix-code cost at that
prior.  A separate seed-observing adversary timing model is reported: if the
source law may depend on the realized codebook seed, shared randomization cannot
improve the optimum over the best deterministic robust code.

All results are finite, bounded, rational, one-shot, binary-prefix,
common-message, and zero-error.  Shared randomness is explicit and its exact
sampling cost is not priced.  These are not parent-resource or simulation
evidence claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Mapping, Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import (
    TVExpectationCertificate,
    exact_tv_robust_prefix_code,
    maximize_expectation_tv_ball,
    total_variation_distance,
)
from .prior_weighted_codes import (
    RationalInput,
    exact_prior_weighted_prefix_code,
    validate_rational_prior,
)
from .robust_prior_codes import (
    ExactZeroSumGameCertificate,
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    convex_combination_prior,
    enumerate_robust_code_candidates,
    solve_exact_zero_sum_game,
)


@dataclass(frozen=True)
class TVBallInequality:
    label: str
    coefficients: tuple[Fraction, ...]
    bound: Fraction

    def value(self, free_coordinates: Sequence[Fraction]) -> Fraction:
        if len(free_coordinates) != len(self.coefficients):
            raise ValueError("free-coordinate vector has the wrong dimension")
        return sum(
            (
                coefficient * coordinate
                for coefficient, coordinate in zip(
                    self.coefficients,
                    free_coordinates,
                )
            ),
            Fraction(0),
        )

    def satisfied(self, free_coordinates: Sequence[Fraction]) -> bool:
        return self.value(free_coordinates) <= self.bound


@dataclass(frozen=True)
class TVBallVertex:
    distribution: tuple[Fraction, ...]
    active_inequalities: tuple[str, ...]


@dataclass(frozen=True)
class TVBallVertexCertificate:
    nominal_distribution: tuple[Fraction, ...]
    radius: Fraction
    inequalities: tuple[TVBallInequality, ...]
    vertices: tuple[TVBallVertex, ...]
    ambient_dimension: int
    candidate_bases: int
    bases_examined: int
    nonsingular_bases: int
    max_states: int
    max_bases: int

    @property
    def vertex_distributions(self) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(vertex.distribution for vertex in self.vertices)

    @property
    def valid(self) -> bool:
        count = len(self.nominal_distribution)
        if (
            count == 0
            or self.ambient_dimension != count - 1
            or any(probability < 0 for probability in self.nominal_distribution)
            or sum(self.nominal_distribution, Fraction(0)) != 1
            or not 0 <= self.radius <= 1
            or not self.vertices
            or len(set(self.vertex_distributions)) != len(self.vertices)
            or self.bases_examined != self.candidate_bases
            or not 0 <= self.nonsingular_bases <= self.bases_examined
        ):
            return False
        expected_inequalities = (
            0
            if count == 1
            else count + 2 * ((1 << (count - 1)) - 1)
        )
        if len(self.inequalities) != expected_inequalities:
            return False
        for vertex in self.vertices:
            distribution = vertex.distribution
            if (
                len(distribution) != count
                or any(probability < 0 for probability in distribution)
                or sum(distribution, Fraction(0)) != 1
                or total_variation_distance(
                    self.nominal_distribution,
                    distribution,
                )
                > self.radius
            ):
                return False
            free = distribution[:-1]
            if not all(
                inequality.satisfied(free)
                for inequality in self.inequalities
            ):
                return False
            if self.ambient_dimension:
                active = {
                    inequality.label
                    for inequality in self.inequalities
                    if inequality.value(free) == inequality.bound
                }
                if not set(vertex.active_inequalities).issubset(active):
                    return False
                if len(vertex.active_inequalities) != self.ambient_dimension:
                    return False
        if self.radius == 0:
            return self.vertex_distributions == (self.nominal_distribution,)
        if self.radius == 1:
            simplex_vertices = {
                tuple(
                    Fraction(1) if index == chosen else Fraction(0)
                    for index in range(count)
                )
                for chosen in range(count)
            }
            return set(self.vertex_distributions) == simplex_vertices
        return True


def _exact_fraction(value: RationalInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(
            f"{name} must be supplied as int, str, or Fraction for exact arithmetic"
        )
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{name} is not an exact rational value") from error


def _validate_distribution(
    probabilities: Sequence[RationalInput],
) -> tuple[Fraction, ...]:
    supplied = tuple(
        _exact_fraction(value, name="nominal probability")
        for value in probabilities
    )
    if not supplied:
        raise ValueError("nominal distribution must be nonempty")
    if any(probability < 0 for probability in supplied):
        raise ValueError("nominal probabilities must be nonnegative")
    if sum(supplied, Fraction(0)) != 1:
        raise ValueError("nominal probabilities must sum exactly to one")
    return supplied


def _solve_square_system(
    matrix: Sequence[Sequence[Fraction]],
    target: Sequence[Fraction],
) -> tuple[Fraction, ...] | None:
    rows = tuple(tuple(Fraction(value) for value in row) for row in matrix)
    right = tuple(Fraction(value) for value in target)
    if len(rows) != len(right):
        raise ValueError("square-system target has the wrong length")
    if not rows:
        return ()
    width = len(rows[0])
    if width != len(rows) or any(len(row) != width for row in rows):
        raise ValueError("vertex solver requires a square matrix")
    augmented = [list(row) + [value] for row, value in zip(rows, right)]
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(column, width)
                if augmented[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        pivot_value = augmented[column][column]
        augmented[column] = [
            value / pivot_value for value in augmented[column]
        ]
        for row in range(width):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(
                        augmented[row],
                        augmented[column],
                    )
                ]
    return tuple(augmented[row][-1] for row in range(width))


def _subset_affine_form(
    state_count: int,
    mask: int,
) -> tuple[Fraction, tuple[Fraction, ...]]:
    """Return ``constant + coefficients dot q[:-1]`` for q(S)."""

    last = state_count - 1
    includes_last = bool(mask & (1 << last))
    constant = Fraction(1) if includes_last else Fraction(0)
    coefficients: list[Fraction] = []
    for index in range(last):
        includes = bool(mask & (1 << index))
        if includes_last:
            coefficients.append(Fraction(0) if includes else Fraction(-1))
        else:
            coefficients.append(Fraction(1) if includes else Fraction(0))
    return constant, tuple(coefficients)


def tv_ball_event_inequalities(
    nominal_distribution: Sequence[RationalInput],
    radius: RationalInput,
) -> tuple[TVBallInequality, ...]:
    """Exact halfspace description using one subset from each complement pair."""

    nominal = _validate_distribution(nominal_distribution)
    supplied_radius = _exact_fraction(radius, name="TV radius")
    if not 0 <= supplied_radius <= 1:
        raise ValueError("TV radius must lie in [0,1]")
    count = len(nominal)
    if count == 1:
        return ()
    dimension = count - 1
    inequalities: list[TVBallInequality] = []

    for index in range(dimension):
        coefficients = tuple(
            Fraction(-1) if coordinate == index else Fraction(0)
            for coordinate in range(dimension)
        )
        inequalities.append(
            TVBallInequality(f"simplex:q{index}>=0", coefficients, Fraction(0))
        )
    inequalities.append(
        TVBallInequality(
            f"simplex:q{count - 1}>=0",
            tuple(Fraction(1) for _ in range(dimension)),
            Fraction(1),
        )
    )

    full_mask = (1 << count) - 1
    # Every nonempty proper subset is paired with its complement.  Retain the
    # unique representative containing state zero and include both signs.
    for mask in range(1, full_mask):
        if not (mask & 1):
            continue
        constant, coefficients = _subset_affine_form(count, mask)
        nominal_mass = sum(
            (
                nominal[index]
                for index in range(count)
                if mask & (1 << index)
            ),
            Fraction(0),
        )
        inequalities.append(
            TVBallInequality(
                f"event:{mask}:upper",
                coefficients,
                supplied_radius + nominal_mass - constant,
            )
        )
        inequalities.append(
            TVBallInequality(
                f"event:{mask}:lower",
                tuple(-coefficient for coefficient in coefficients),
                supplied_radius - nominal_mass + constant,
            )
        )
    return tuple(inequalities)


def enumerate_tv_ball_vertices(
    nominal_distribution: Sequence[RationalInput],
    radius: RationalInput,
    *,
    max_states: int = 5,
    max_bases: int = 2_000_000,
) -> TVBallVertexCertificate:
    """Enumerate every vertex of a bounded rational TV-ball polytope."""

    nominal = _validate_distribution(nominal_distribution)
    supplied_radius = _exact_fraction(radius, name="TV radius")
    if not 0 <= supplied_radius <= 1:
        raise ValueError("TV radius must lie in [0,1]")
    state_cap = int(max_states)
    basis_cap = int(max_bases)
    if state_cap < 1 or basis_cap < 1:
        raise ValueError("vertex-enumeration caps must be positive")
    if len(nominal) > state_cap:
        raise ValueError(
            f"exact TV-ball vertex enumeration capped at {state_cap} states"
        )
    dimension = len(nominal) - 1
    inequalities = tv_ball_event_inequalities(nominal, supplied_radius)
    if dimension == 0:
        certificate = TVBallVertexCertificate(
            nominal,
            supplied_radius,
            inequalities,
            (TVBallVertex((Fraction(1),), ()),),
            0,
            1,
            1,
            1,
            state_cap,
            basis_cap,
        )
        if not certificate.valid:
            raise AssertionError("one-state TV vertex certificate failed")
        return certificate

    candidate_bases = comb(len(inequalities), dimension)
    if candidate_bases > basis_cap:
        raise ValueError(
            "TV-ball active-set space exceeds the configured basis cap"
        )
    by_distribution: dict[tuple[Fraction, ...], tuple[str, ...]] = {}
    nonsingular = 0
    examined = 0
    for basis_indices in combinations(range(len(inequalities)), dimension):
        examined += 1
        basis = tuple(inequalities[index] for index in basis_indices)
        solution = _solve_square_system(
            tuple(inequality.coefficients for inequality in basis),
            tuple(inequality.bound for inequality in basis),
        )
        if solution is None:
            continue
        nonsingular += 1
        if not all(
            inequality.satisfied(solution)
            for inequality in inequalities
        ):
            continue
        final_probability = Fraction(1) - sum(solution, Fraction(0))
        distribution = (*solution, final_probability)
        if any(probability < 0 for probability in distribution):
            continue
        if total_variation_distance(nominal, distribution) > supplied_radius:
            continue
        labels = tuple(inequality.label for inequality in basis)
        incumbent = by_distribution.get(distribution)
        if incumbent is None or labels < incumbent:
            by_distribution[distribution] = labels

    vertices = tuple(
        TVBallVertex(distribution, by_distribution[distribution])
        for distribution in sorted(by_distribution)
    )
    certificate = TVBallVertexCertificate(
        nominal,
        supplied_radius,
        inequalities,
        vertices,
        dimension,
        candidate_bases,
        examined,
        nonsingular,
        state_cap,
        basis_cap,
    )
    if not certificate.valid:
        raise AssertionError("TV-ball vertex certificate failed validation")
    return certificate


@dataclass(frozen=True)
class SharedTVRobustCodeCertificate:
    graph: ConfusionGraph
    nominal_prior: tuple[Fraction, ...]
    radius: Fraction
    tv_vertices: TVBallVertexCertificate
    candidate_enumeration: RobustCandidateEnumeration
    deterministic_candidate_index: int
    deterministic_value: Fraction
    deterministic_reference_value: Fraction
    mixed_game: ExactZeroSumGameCertificate
    mixed_state_lengths: tuple[Fraction, ...]
    mixed_continuous_worst_case: TVExpectationCertificate
    least_favorable_prior: tuple[Fraction, ...]
    least_favorable_oracle_value: Fraction
    selected_mixture_seed_observing_cost: Fraction

    @property
    def candidates(self) -> tuple[RobustCodeCandidate, ...]:
        return self.candidate_enumeration.candidates

    @property
    def mixed_value(self) -> Fraction:
        return self.mixed_game.value

    @property
    def randomization_gain(self) -> Fraction:
        return self.deterministic_value - self.mixed_value

    @property
    def optimal_seed_observing_value(self) -> Fraction:
        """If the adversary may condition on the realized shared seed."""

        return self.deterministic_value

    @property
    def code_support(self) -> tuple[int, ...]:
        return self.mixed_game.code_support

    @property
    def vertex_support(self) -> tuple[int, ...]:
        return self.mixed_game.scenario_support

    @property
    def valid(self) -> bool:
        vertex_distributions = self.tv_vertices.vertex_distributions
        candidate_count = len(self.candidates)
        vertex_count = len(vertex_distributions)
        cost_matrix = tuple(
            tuple(
                candidate.scenario_costs[vertex]
                for candidate in self.candidates
            )
            for vertex in range(vertex_count)
        )
        expected_mixed_lengths = tuple(
            sum(
                (
                    weight * candidate.state_lengths[state]
                    for weight, candidate in zip(
                        self.mixed_game.code_mixture,
                        self.candidates,
                    )
                ),
                Fraction(0),
            )
            for state in range(self.graph.vertex_count)
        )
        expected_least_favorable = convex_combination_prior(
            vertex_distributions,
            self.mixed_game.scenario_mixture,
        )
        selected_seed_observing = sum(
            (
                weight * max(candidate.scenario_costs)
                for weight, candidate in zip(
                    self.mixed_game.code_mixture,
                    self.candidates,
                )
            ),
            Fraction(0),
        )
        return (
            self.tv_vertices.valid
            and self.tv_vertices.nominal_distribution == self.nominal_prior
            and self.tv_vertices.radius == self.radius
            and self.candidate_enumeration.valid
            and self.candidate_enumeration.graph == self.graph
            and self.candidate_enumeration.priors == vertex_distributions
            and 0 <= self.deterministic_candidate_index < candidate_count
            and self.deterministic_value
            == max(
                self.candidates[
                    self.deterministic_candidate_index
                ].scenario_costs
            )
            and self.deterministic_value
            == min(max(candidate.scenario_costs) for candidate in self.candidates)
            and self.deterministic_reference_value == self.deterministic_value
            and self.mixed_game.valid
            and self.mixed_game.cost_matrix == cost_matrix
            and self.mixed_state_lengths == expected_mixed_lengths
            and self.mixed_continuous_worst_case.valid
            and self.mixed_continuous_worst_case.nominal_distribution
            == self.nominal_prior
            and self.mixed_continuous_worst_case.radius == self.radius
            and self.mixed_continuous_worst_case.state_values
            == self.mixed_state_lengths
            and self.mixed_continuous_worst_case.extremal_expectation
            == self.mixed_value
            and self.least_favorable_prior == expected_least_favorable
            and total_variation_distance(
                self.nominal_prior,
                self.least_favorable_prior,
            )
            <= self.radius
            and self.least_favorable_oracle_value == self.mixed_value
            and self.selected_mixture_seed_observing_cost
            == selected_seed_observing
            and self.mixed_value <= self.deterministic_value
            and self.selected_mixture_seed_observing_cost
            >= self.mixed_value
            and self.optimal_seed_observing_value == self.deterministic_value
            and len(self.code_support) <= vertex_count
            and len(self.vertex_support) <= candidate_count
        )


def exact_shared_tv_robust_prefix_code(
    graph: ConfusionGraph,
    nominal_prior: Sequence[RationalInput] | Mapping[object, RationalInput],
    radius: RationalInput,
    *,
    max_states: int = 5,
    max_vertex_bases: int = 2_000_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_game_bases: int = 2_000_000,
) -> SharedTVRobustCodeCertificate:
    """Exact shared-codebook-randomness game against one continuous TV ball."""

    nominal = validate_rational_prior(graph, nominal_prior)
    supplied_radius = _exact_fraction(radius, name="TV radius")
    if not 0 <= supplied_radius <= 1:
        raise ValueError("TV radius must lie in [0,1]")
    tv_vertices = enumerate_tv_ball_vertices(
        nominal,
        supplied_radius,
        max_states=max_states,
        max_bases=max_vertex_bases,
    )
    enumeration = enumerate_robust_code_candidates(
        graph,
        tv_vertices.vertex_distributions,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    deterministic_index = min(
        range(len(candidates)),
        key=lambda index: (
            max(candidates[index].scenario_costs),
            candidates[index].maximum_length,
            candidates[index].state_lengths,
            candidates[index].partition,
        ),
    )
    deterministic_value = max(candidates[deterministic_index].scenario_costs)
    deterministic_reference = exact_tv_robust_prefix_code(
        graph,
        nominal,
        supplied_radius,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
    )
    cost_matrix = tuple(
        tuple(
            candidate.scenario_costs[vertex]
            for candidate in candidates
        )
        for vertex in range(len(tv_vertices.vertices))
    )
    game = solve_exact_zero_sum_game(
        cost_matrix,
        max_bases=max_game_bases,
    )
    mixed_lengths = tuple(
        sum(
            (
                weight * candidate.state_lengths[state]
                for weight, candidate in zip(
                    game.code_mixture,
                    candidates,
                )
            ),
            Fraction(0),
        )
        for state in range(graph.vertex_count)
    )
    continuous_worst = maximize_expectation_tv_ball(
        nominal,
        mixed_lengths,
        supplied_radius,
    )
    least_favorable = convex_combination_prior(
        tv_vertices.vertex_distributions,
        game.scenario_mixture,
    )
    oracle = exact_prior_weighted_prefix_code(
        graph,
        least_favorable,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    )
    selected_seed_observing = sum(
        (
            weight * max(candidate.scenario_costs)
            for weight, candidate in zip(game.code_mixture, candidates)
        ),
        Fraction(0),
    )
    certificate = SharedTVRobustCodeCertificate(
        graph,
        nominal,
        supplied_radius,
        tv_vertices,
        enumeration,
        deterministic_index,
        deterministic_value,
        deterministic_reference.robust_value,
        game,
        mixed_lengths,
        continuous_worst,
        least_favorable,
        oracle.expected_length,
        selected_seed_observing,
    )
    if not certificate.valid:
        raise AssertionError("shared TV-robust code certificate failed validation")
    return certificate


def full_tv_k3_shared_randomness_example(
    nominal_prior: Sequence[RationalInput] = (
        Fraction(1, 3),
        Fraction(1, 3),
        Fraction(1, 3),
    ),
) -> SharedTVRobustCodeCertificate:
    graph = ConfusionGraph.from_edges(
        (0, 1, 2),
        ((0, 1), (0, 2), (1, 2)),
    )
    return exact_shared_tv_robust_prefix_code(
        graph,
        nominal_prior,
        Fraction(1),
    )
