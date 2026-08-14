"""Exact total-variation distributionally robust zero-error prefix coding.

The finite-prior robust lane protects against a declared convex hull of finitely
many source priors.  This module treats a different uncertainty set: the full
total-variation ball around one exact rational nominal prior.

For a fixed rational state-value vector, the continuous inner optimization has
an exact mass-transport solution.  Total variation is the probability mass
removed from donor states and added to recipient states.  To maximize
expectation, move mass from the shortest-value states toward a maximum-value
state; to minimize it, reverse the order.  Exact rational transfer receipts
replace numerical linear programming.

The outer coding problem then exhausts every bounded proper confusion-graph
partition and every complete binary prefix shape.  It returns the deterministic
code minimizing worst-case expected length over the entire continuous TV ball,
with exact radius-zero and radius-one endpoint certificates.

The module distinguishes TV balls from Huber contamination, nominal cost from
uncertainty uplift, and expected robust cost from peak codeword length.  It is
finite, one-shot, binary-prefix, deterministic, rational, and zero-error.  It is
not evidence for simulation and does not translate internal message lengths
into parent-universe hardware, energy, mass, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Sequence

from .confusion_graphs import (
    ChromaticCertificate,
    ConfusionGraph,
    exact_chromatic_certificate,
)
from .prior_weighted_codes import (
    Partition,
    RationalInput,
    canonicalize_partition,
    coloring_from_partition,
    iter_proper_partitions,
    partition_is_proper,
    validate_rational_prior,
)
from .robust_prior_codes import CompletePrefixShape, complete_prefix_shapes

ValueInput = int | str | Fraction


def _as_fraction(value: ValueInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(
            f"{name} must be supplied as int, str, or Fraction for exact arithmetic"
        )
    try:
        result = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{name} is not an exact rational value") from error
    return result


def _validate_values(
    probabilities: Sequence[Fraction],
    values: Sequence[ValueInput],
) -> tuple[Fraction, ...]:
    supplied = tuple(
        _as_fraction(value, name="state value")
        for value in values
    )
    if len(supplied) != len(probabilities):
        raise ValueError("one state value is required per probability")
    if not supplied:
        raise ValueError("at least one state value is required")
    return supplied


def _validate_radius(radius: ValueInput) -> Fraction:
    supplied = _as_fraction(radius, name="total-variation radius")
    if not 0 <= supplied <= 1:
        raise ValueError("total-variation radius must lie in [0,1]")
    return supplied


def total_variation_distance(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> Fraction:
    first = tuple(Fraction(value) for value in left)
    second = tuple(Fraction(value) for value in right)
    if len(first) != len(second) or not first:
        raise ValueError("probability vectors must be nonempty and equal length")
    if any(value < 0 for value in (*first, *second)):
        raise ValueError("probabilities must be nonnegative")
    if sum(first, Fraction(0)) != 1 or sum(second, Fraction(0)) != 1:
        raise ValueError("probability vectors must sum to one")
    return sum(
        (abs(a - b) for a, b in zip(first, second)),
        Fraction(0),
    ) / 2


def exact_expectation(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
) -> Fraction:
    if len(probabilities) != len(values):
        raise ValueError("probability and value vectors must have equal length")
    return sum(
        (
            probability * value
            for probability, value in zip(probabilities, values)
        ),
        Fraction(0),
    )


@dataclass(frozen=True)
class TVTransfer:
    donor_index: int
    recipient_index: int
    mass: Fraction
    donor_value: Fraction
    recipient_value: Fraction

    @property
    def signed_expectation_change(self) -> Fraction:
        return self.mass * (self.recipient_value - self.donor_value)

    @property
    def valid(self) -> bool:
        return (
            self.donor_index >= 0
            and self.recipient_index >= 0
            and self.donor_index != self.recipient_index
            and self.mass > 0
            and self.donor_value != self.recipient_value
        )


@dataclass(frozen=True)
class TVExpectationCertificate:
    nominal_distribution: tuple[Fraction, ...]
    state_values: tuple[Fraction, ...]
    radius: Fraction
    maximize: bool
    extremal_distribution: tuple[Fraction, ...]
    transfers: tuple[TVTransfer, ...]
    nominal_expectation: Fraction
    extremal_expectation: Fraction
    moved_mass: Fraction
    saturation_radius: Fraction
    full_range_tight_radius: Fraction

    @property
    def tv_distance(self) -> Fraction:
        return total_variation_distance(
            self.nominal_distribution,
            self.extremal_distribution,
        )

    @property
    def unused_radius(self) -> Fraction:
        return self.radius - self.moved_mass

    @property
    def expectation_change(self) -> Fraction:
        return self.extremal_expectation - self.nominal_expectation

    @property
    def value_range(self) -> Fraction:
        return max(self.state_values) - min(self.state_values)

    @property
    def range_bound(self) -> Fraction:
        direction = 1 if self.maximize else -1
        return (
            self.nominal_expectation
            + direction * self.radius * self.value_range
        )

    @property
    def range_bound_slack(self) -> Fraction:
        if self.maximize:
            return self.range_bound - self.extremal_expectation
        return self.extremal_expectation - self.range_bound

    @property
    def valid(self) -> bool:
        count = len(self.nominal_distribution)
        if (
            count == 0
            or len(self.state_values) != count
            or len(self.extremal_distribution) != count
            or any(probability < 0 for probability in self.nominal_distribution)
            or any(probability < 0 for probability in self.extremal_distribution)
            or sum(self.nominal_distribution, Fraction(0)) != 1
            or sum(self.extremal_distribution, Fraction(0)) != 1
            or not 0 <= self.radius <= 1
            or not 0 <= self.saturation_radius <= 1
            or not 0 <= self.full_range_tight_radius <= 1
        ):
            return False

        reconstructed = list(self.nominal_distribution)
        for transfer in self.transfers:
            if (
                not transfer.valid
                or transfer.donor_index >= count
                or transfer.recipient_index >= count
                or transfer.donor_value
                != self.state_values[transfer.donor_index]
                or transfer.recipient_value
                != self.state_values[transfer.recipient_index]
            ):
                return False
            if self.maximize and transfer.recipient_value <= transfer.donor_value:
                return False
            if not self.maximize and transfer.recipient_value >= transfer.donor_value:
                return False
            reconstructed[transfer.donor_index] -= transfer.mass
            reconstructed[transfer.recipient_index] += transfer.mass
        if tuple(reconstructed) != self.extremal_distribution:
            return False

        signed_change = sum(
            (
                transfer.signed_expectation_change
                for transfer in self.transfers
            ),
            Fraction(0),
        )
        donor_values = tuple(transfer.donor_value for transfer in self.transfers)
        recipient_values = tuple(
            transfer.recipient_value for transfer in self.transfers
        )
        ordered = (
            donor_values == tuple(sorted(donor_values))
            and recipient_values == tuple(sorted(recipient_values, reverse=True))
            if self.maximize
            else donor_values == tuple(sorted(donor_values, reverse=True))
            and recipient_values == tuple(sorted(recipient_values))
        )
        expected_moved = min(self.radius, self.saturation_radius)
        direction_correct = (
            signed_change >= 0 if self.maximize else signed_change <= 0
        )
        tight_if_small = (
            self.range_bound_slack == 0
            if self.radius <= self.full_range_tight_radius
            else self.range_bound_slack >= 0
        )
        return (
            ordered
            and direction_correct
            and all(value >= 0 for value in reconstructed)
            and self.nominal_expectation
            == exact_expectation(
                self.nominal_distribution,
                self.state_values,
            )
            and self.extremal_expectation
            == exact_expectation(
                self.extremal_distribution,
                self.state_values,
            )
            and self.extremal_expectation
            == self.nominal_expectation + signed_change
            and self.moved_mass
            == sum(
                (transfer.mass for transfer in self.transfers),
                Fraction(0),
            )
            and self.moved_mass == self.tv_distance
            and self.moved_mass == expected_moved
            and self.moved_mass <= self.radius
            and self.unused_radius >= 0
            and self.range_bound_slack >= 0
            and tight_if_small
        )


def _extremal_saturation_radius(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    *,
    maximize: bool,
) -> Fraction:
    target = max(values) if maximize else min(values)
    target_mass = sum(
        (
            probability
            for probability, value in zip(probabilities, values)
            if value == target
        ),
        Fraction(0),
    )
    return 1 - target_mass


def _full_range_tight_radius(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    *,
    maximize: bool,
) -> Fraction:
    donor_value = min(values) if maximize else max(values)
    recipient_value = max(values) if maximize else min(values)
    donor_mass = sum(
        (
            probability
            for probability, value in zip(probabilities, values)
            if value == donor_value
        ),
        Fraction(0),
    )
    recipient_nominal_mass = sum(
        (
            probability
            for probability, value in zip(probabilities, values)
            if value == recipient_value
        ),
        Fraction(0),
    )
    recipient_capacity = 1 - recipient_nominal_mass
    return min(donor_mass, recipient_capacity)


def _extremize_expectation_tv_ball(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    radius: Fraction,
    *,
    maximize: bool,
) -> TVExpectationCertificate:
    nominal = tuple(Fraction(probability) for probability in probabilities)
    supplied_values = tuple(Fraction(value) for value in values)
    count = len(nominal)
    if (
        count == 0
        or len(supplied_values) != count
        or any(probability < 0 for probability in nominal)
        or sum(nominal, Fraction(0)) != 1
        or not 0 <= radius <= 1
    ):
        raise ValueError("invalid exact TV-ball expectation inputs")

    donor_order = tuple(
        sorted(
            range(count),
            key=lambda index: (
                supplied_values[index],
                index,
            ),
            reverse=not maximize,
        )
    )
    recipient_order = tuple(
        sorted(
            range(count),
            key=lambda index: (
                supplied_values[index],
                -index,
            ),
            reverse=maximize,
        )
    )
    donor_remaining = list(nominal)
    recipient_remaining = [1 - probability for probability in nominal]
    extremal = list(nominal)
    transfers: list[TVTransfer] = []
    remaining_radius = radius
    donor_position = 0
    recipient_position = 0

    while remaining_radius > 0:
        while (
            donor_position < count
            and donor_remaining[donor_order[donor_position]] == 0
        ):
            donor_position += 1
        while (
            recipient_position < count
            and recipient_remaining[recipient_order[recipient_position]] == 0
        ):
            recipient_position += 1
        if donor_position == count or recipient_position == count:
            break

        donor = donor_order[donor_position]
        recipient = recipient_order[recipient_position]
        donor_value = supplied_values[donor]
        recipient_value = supplied_values[recipient]
        profitable = (
            recipient_value > donor_value
            if maximize
            else recipient_value < donor_value
        )
        if not profitable:
            break
        if donor == recipient:
            raise AssertionError(
                "a profitable total-variation transfer cannot use one state twice"
            )

        mass = min(
            remaining_radius,
            donor_remaining[donor],
            recipient_remaining[recipient],
        )
        if mass <= 0:
            raise AssertionError("positive-gap transport selected zero mass")
        donor_remaining[donor] -= mass
        recipient_remaining[recipient] -= mass
        extremal[donor] -= mass
        extremal[recipient] += mass
        transfers.append(
            TVTransfer(
                donor,
                recipient,
                mass,
                donor_value,
                recipient_value,
            )
        )
        remaining_radius -= mass

    saturation = _extremal_saturation_radius(
        nominal,
        supplied_values,
        maximize=maximize,
    )
    certificate = TVExpectationCertificate(
        nominal,
        supplied_values,
        radius,
        maximize,
        tuple(extremal),
        tuple(transfers),
        exact_expectation(nominal, supplied_values),
        exact_expectation(extremal, supplied_values),
        sum((transfer.mass for transfer in transfers), Fraction(0)),
        saturation,
        _full_range_tight_radius(
            nominal,
            supplied_values,
            maximize=maximize,
        ),
    )
    if not certificate.valid:
        raise AssertionError("TV-ball expectation certificate failed validation")
    return certificate


def maximize_expectation_tv_ball(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    radius: Fraction,
) -> TVExpectationCertificate:
    return _extremize_expectation_tv_ball(
        probabilities,
        values,
        radius,
        maximize=True,
    )


def minimize_expectation_tv_ball(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    radius: Fraction,
) -> TVExpectationCertificate:
    return _extremize_expectation_tv_ball(
        probabilities,
        values,
        radius,
        maximize=False,
    )


def exact_tv_expectation_bounds(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    radius: Fraction,
) -> tuple[TVExpectationCertificate, TVExpectationCertificate]:
    return (
        minimize_expectation_tv_ball(probabilities, values, radius),
        maximize_expectation_tv_ball(probabilities, values, radius),
    )


@dataclass(frozen=True)
class TVExpectationSegment:
    start_radius: Fraction
    end_radius: Fraction
    start_expectation: Fraction
    marginal_change: Fraction

    @property
    def end_expectation(self) -> Fraction:
        return self.start_expectation + (
            self.end_radius - self.start_radius
        ) * self.marginal_change

    @property
    def valid(self) -> bool:
        return (
            0 <= self.start_radius <= self.end_radius <= 1
            and self.start_radius < self.end_radius
        )


@dataclass(frozen=True)
class TVExpectationProfile:
    nominal_distribution: tuple[Fraction, ...]
    state_values: tuple[Fraction, ...]
    maximize: bool
    segments: tuple[TVExpectationSegment, ...]

    def evaluate(self, radius: ValueInput) -> Fraction:
        supplied = _validate_radius(radius)
        for segment in self.segments:
            if segment.start_radius <= supplied <= segment.end_radius:
                return segment.start_expectation + (
                    supplied - segment.start_radius
                ) * segment.marginal_change
        raise AssertionError("TV expectation profile does not cover the radius")

    @property
    def valid(self) -> bool:
        if not self.segments or not all(segment.valid for segment in self.segments):
            return False
        if self.segments[0].start_radius != 0:
            return False
        if self.segments[-1].end_radius != 1:
            return False
        for left, right in zip(self.segments, self.segments[1:]):
            if (
                left.end_radius != right.start_radius
                or left.end_expectation != right.start_expectation
            ):
                return False
        slopes = tuple(segment.marginal_change for segment in self.segments)
        return (
            slopes == tuple(sorted(slopes, reverse=True))
            if self.maximize
            else slopes == tuple(sorted(slopes))
        )


def tv_expectation_profile(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    *,
    maximize: bool = True,
) -> TVExpectationProfile:
    full = _extremize_expectation_tv_ball(
        probabilities,
        values,
        Fraction(1),
        maximize=maximize,
    )
    current_radius = Fraction(0)
    current_expectation = full.nominal_expectation
    raw_segments: list[TVExpectationSegment] = []
    for transfer in full.transfers:
        slope = transfer.recipient_value - transfer.donor_value
        raw_segments.append(
            TVExpectationSegment(
                current_radius,
                current_radius + transfer.mass,
                current_expectation,
                slope,
            )
        )
        current_radius += transfer.mass
        current_expectation += transfer.mass * slope
    if current_radius < 1:
        raw_segments.append(
            TVExpectationSegment(
                current_radius,
                Fraction(1),
                current_expectation,
                Fraction(0),
            )
        )

    merged: list[TVExpectationSegment] = []
    for segment in raw_segments:
        if (
            merged
            and merged[-1].marginal_change == segment.marginal_change
            and merged[-1].end_radius == segment.start_radius
        ):
            previous = merged.pop()
            merged.append(
                TVExpectationSegment(
                    previous.start_radius,
                    segment.end_radius,
                    previous.start_expectation,
                    previous.marginal_change,
                )
            )
        else:
            merged.append(segment)
    profile = TVExpectationProfile(
        full.nominal_distribution,
        full.state_values,
        maximize,
        tuple(merged),
    )
    if not profile.valid:
        raise AssertionError("TV expectation profile failed validation")
    return profile


@dataclass(frozen=True)
class HuberContaminationCertificate:
    nominal_distribution: tuple[Fraction, ...]
    state_values: tuple[Fraction, ...]
    contamination_fraction: Fraction
    maximize: bool
    contamination_distribution: tuple[Fraction, ...]
    contaminated_distribution: tuple[Fraction, ...]
    nominal_expectation: Fraction
    contaminated_expectation: Fraction
    tv_distance_from_nominal: Fraction

    @property
    def valid(self) -> bool:
        epsilon = self.contamination_fraction
        target_value = (
            max(self.state_values) if self.maximize else min(self.state_values)
        )
        return (
            0 <= epsilon <= 1
            and len(self.nominal_distribution) == len(self.state_values)
            == len(self.contamination_distribution)
            == len(self.contaminated_distribution)
            and all(value >= 0 for value in self.contamination_distribution)
            and sum(self.contamination_distribution, Fraction(0)) == 1
            and all(
                probability == 0 or value == target_value
                for probability, value in zip(
                    self.contamination_distribution,
                    self.state_values,
                )
            )
            and self.contaminated_distribution
            == tuple(
                (1 - epsilon) * nominal + epsilon * contamination
                for nominal, contamination in zip(
                    self.nominal_distribution,
                    self.contamination_distribution,
                )
            )
            and self.nominal_expectation
            == exact_expectation(
                self.nominal_distribution,
                self.state_values,
            )
            and self.contaminated_expectation
            == exact_expectation(
                self.contaminated_distribution,
                self.state_values,
            )
            and self.tv_distance_from_nominal
            == total_variation_distance(
                self.nominal_distribution,
                self.contaminated_distribution,
            )
            and self.tv_distance_from_nominal <= epsilon
        )


def huber_extremal_expectation(
    probabilities: Sequence[Fraction],
    values: Sequence[Fraction],
    contamination_fraction: Fraction,
    *,
    maximize: bool = True,
) -> HuberContaminationCertificate:
    nominal = tuple(Fraction(probability) for probability in probabilities)
    supplied_values = tuple(Fraction(value) for value in values)
    epsilon = Fraction(contamination_fraction)
    if (
        not nominal
        or len(nominal) != len(supplied_values)
        or any(probability < 0 for probability in nominal)
        or sum(nominal, Fraction(0)) != 1
        or not 0 <= epsilon <= 1
    ):
        raise ValueError("invalid Huber contamination inputs")
    target = max(supplied_values) if maximize else min(supplied_values)
    target_index = next(
        index for index, value in enumerate(supplied_values) if value == target
    )
    contamination = tuple(
        Fraction(1) if index == target_index else Fraction(0)
        for index in range(len(nominal))
    )
    contaminated = tuple(
        (1 - epsilon) * probability + epsilon * replacement
        for probability, replacement in zip(nominal, contamination)
    )
    certificate = HuberContaminationCertificate(
        nominal,
        supplied_values,
        epsilon,
        maximize,
        contamination,
        contaminated,
        exact_expectation(nominal, supplied_values),
        exact_expectation(contaminated, supplied_values),
        total_variation_distance(nominal, contaminated),
    )
    if not certificate.valid:
        raise AssertionError("Huber contamination certificate failed validation")
    return certificate


@dataclass(frozen=True)
class TVRobustCodeCandidate:
    graph: ConfusionGraph
    partition: Partition
    coloring: tuple[int, ...]
    prefix_shape: CompletePrefixShape
    state_lengths: tuple[int, ...]
    nominal_expectation: Fraction
    worst_case: TVExpectationCertificate
    best_case: TVExpectationCertificate

    @property
    def message_count(self) -> int:
        return len(self.partition)

    @property
    def maximum_length(self) -> int:
        return self.prefix_shape.maximum_length

    @property
    def worst_case_expectation(self) -> Fraction:
        return self.worst_case.extremal_expectation

    @property
    def best_case_expectation(self) -> Fraction:
        return self.best_case.extremal_expectation

    @property
    def valid(self) -> bool:
        return (
            partition_is_proper(self.graph, self.partition)
            and self.coloring == coloring_from_partition(self.graph, self.partition)
            and self.prefix_shape.valid
            and self.prefix_shape.message_count == self.message_count
            and self.state_lengths
            == tuple(
                self.prefix_shape.lengths[self.coloring[index]]
                for index in range(self.graph.vertex_count)
            )
            and self.worst_case.valid
            and self.best_case.valid
            and self.worst_case.maximize
            and not self.best_case.maximize
            and self.worst_case.state_values
            == tuple(Fraction(length) for length in self.state_lengths)
            and self.best_case.state_values == self.worst_case.state_values
            and self.nominal_expectation
            == self.worst_case.nominal_expectation
            == self.best_case.nominal_expectation
            and self.best_case_expectation
            <= self.nominal_expectation
            <= self.worst_case_expectation
        )


def _tv_candidate_tie_key(
    candidate: TVRobustCodeCandidate,
) -> tuple[object, ...]:
    return (
        candidate.worst_case_expectation,
        candidate.nominal_expectation,
        candidate.maximum_length,
        candidate.message_count,
        candidate.state_lengths,
        candidate.partition,
    )


@dataclass(frozen=True)
class TVRobustCodeCertificate:
    graph: ConfusionGraph
    chromatic_certificate: ChromaticCertificate
    nominal_prior: tuple[Fraction, ...]
    radius: Fraction
    optimal_candidate: TVRobustCodeCandidate
    nominal_optimum: Fraction
    hard_peak_optimum: int
    raw_candidates_examined: int
    distinct_state_length_vectors: int
    max_vertices: int
    max_partitions: int
    max_candidates: int

    @property
    def robust_value(self) -> Fraction:
        return self.optimal_candidate.worst_case_expectation

    @property
    def selected_nominal_value(self) -> Fraction:
        return self.optimal_candidate.nominal_expectation

    @property
    def price_of_robustness(self) -> Fraction:
        return self.selected_nominal_value - self.nominal_optimum

    @property
    def uncertainty_uplift(self) -> Fraction:
        return self.robust_value - self.selected_nominal_value

    @property
    def total_robust_gap(self) -> Fraction:
        return self.robust_value - self.nominal_optimum

    @property
    def fixed_length_bits(self) -> int:
        return self.chromatic_certificate.fixed_length_bits

    @property
    def valid(self) -> bool:
        endpoint_valid = True
        if self.radius == 0:
            endpoint_valid = self.robust_value == self.nominal_optimum
        if self.radius == 1:
            endpoint_valid = (
                self.robust_value
                == self.hard_peak_optimum
                == self.fixed_length_bits
            )
        return (
            self.chromatic_certificate.valid
            and self.chromatic_certificate.graph == self.graph
            and len(self.nominal_prior) == self.graph.vertex_count
            and all(probability >= 0 for probability in self.nominal_prior)
            and sum(self.nominal_prior, Fraction(0)) == 1
            and 0 <= self.radius <= 1
            and self.optimal_candidate.valid
            and self.optimal_candidate.graph == self.graph
            and self.optimal_candidate.worst_case.nominal_distribution
            == self.nominal_prior
            and self.optimal_candidate.worst_case.radius == self.radius
            and self.nominal_optimum <= self.selected_nominal_value
            and self.selected_nominal_value <= self.robust_value
            and self.robust_value <= self.hard_peak_optimum
            and self.hard_peak_optimum == self.fixed_length_bits
            and self.raw_candidates_examined
            >= self.distinct_state_length_vectors
            >= 1
            and self.price_of_robustness >= 0
            and self.uncertainty_uplift >= 0
            and self.total_robust_gap
            == self.price_of_robustness + self.uncertainty_uplift
            and endpoint_valid
        )


def exact_tv_robust_prefix_code(
    graph: ConfusionGraph,
    nominal_prior: Sequence[RationalInput] | Mapping[object, RationalInput],
    radius: ValueInput,
    *,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
) -> TVRobustCodeCertificate:
    """Exact deterministic code minimizing worst expectation in one TV ball."""

    prior = validate_rational_prior(graph, nominal_prior)
    supplied_radius = _validate_radius(radius)
    candidate_cap = int(max_candidates)
    if candidate_cap < 1:
        raise ValueError("candidate cap must be positive")
    chromatic = exact_chromatic_certificate(
        graph,
        max_vertices=max_vertices,
    )

    by_state_lengths: dict[tuple[int, ...], TVRobustCodeCandidate] = {}
    raw_count = 0
    for partition in iter_proper_partitions(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    ):
        canonical = canonicalize_partition(partition)
        coloring = coloring_from_partition(graph, canonical)
        for shape in complete_prefix_shapes(
            len(canonical),
            max_prefix_assignments=max_prefix_assignments,
            max_shapes=max_prefix_shapes,
        ):
            raw_count += 1
            if raw_count > candidate_cap:
                raise ValueError(
                    "TV-robust code enumeration exceeded the configured "
                    "candidate cap; no exact optimum was certified"
                )
            state_lengths = tuple(
                shape.lengths[coloring[index]]
                for index in range(graph.vertex_count)
            )
            if state_lengths in by_state_lengths:
                continue
            values = tuple(Fraction(length) for length in state_lengths)
            candidate = TVRobustCodeCandidate(
                graph,
                canonical,
                coloring,
                shape,
                state_lengths,
                exact_expectation(prior, values),
                maximize_expectation_tv_ball(
                    prior,
                    values,
                    supplied_radius,
                ),
                minimize_expectation_tv_ball(
                    prior,
                    values,
                    supplied_radius,
                ),
            )
            if not candidate.valid:
                raise AssertionError("TV-robust code candidate failed validation")
            by_state_lengths[state_lengths] = candidate

    candidates = tuple(by_state_lengths.values())
    if not candidates:
        raise AssertionError("finite graph has no zero-error prefix code")
    optimal = min(candidates, key=_tv_candidate_tie_key)
    nominal_optimum = min(candidate.nominal_expectation for candidate in candidates)
    hard_peak_optimum = min(candidate.maximum_length for candidate in candidates)
    certificate = TVRobustCodeCertificate(
        graph,
        chromatic,
        prior,
        supplied_radius,
        optimal,
        nominal_optimum,
        hard_peak_optimum,
        raw_count,
        len(candidates),
        int(max_vertices),
        int(max_partitions),
        candidate_cap,
    )
    if not certificate.valid:
        raise AssertionError("TV-robust code certificate failed validation")
    return certificate


def skew_k4_tv_robust_example(
    radius: ValueInput,
) -> TVRobustCodeCertificate:
    graph = ConfusionGraph.from_edges(
        (0, 1, 2, 3),
        (
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 2),
            (1, 3),
            (2, 3),
        ),
    )
    return exact_tv_robust_prefix_code(
        graph,
        (
            Fraction(7, 10),
            Fraction(1, 10),
            Fraction(1, 10),
            Fraction(1, 10),
        ),
        radius,
    )
