"""Finite outcome channels and predictive-law contraction.

A future observable law may be followed by a record-independent stochastic
post-processing channel.  Such a channel cannot create distinguishability that
was absent before it.

For a finite Markov kernel K, define the Dobrushin coefficient

    delta(K) = max_{a,b} TV(K(.|a), K(.|b)).

Then every pair of input distributions satisfies

    TV(mu K, nu K) <= delta(K) TV(mu, nu).

For query-specific channels K_q under an exogenous query distribution w_q,

    d_after(x,u)
      <= sum_q w_q delta(K_q) TV(P(.|q,x), P(.|q,u))
      <= delta_max d_before(x,u).

Serial channel coefficients compose submultiplicatively.  The implementation
uses exact rational arithmetic for kernels and theorem certificates, while the
existing stochastic-family API remains float-compatible.

These are internal data-processing results for declared finite observable
interfaces.  They are not evidence for simulation and do not identify a parent
substrate's storage, energy, hardware, or noise law.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Hashable, Sequence

from .stochastic_predictive import (
    FiniteStochasticQueryFamily,
    maximum_stochastic_predictive_packing,
    minimum_target_centered_cover,
)

Outcome = Hashable
ProbabilityInput = int | float | str | Fraction


def _as_fraction(value: ProbabilityInput, *, name: str = "probability") -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, float):
        result = Fraction(str(value))
    else:
        result = Fraction(value)
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def _canonical_distribution(
    probabilities: Sequence[ProbabilityInput],
    expected_length: int | None = None,
    *,
    name: str = "distribution",
) -> tuple[Fraction, ...]:
    values = tuple(_as_fraction(value, name=name) for value in probabilities)
    if not values:
        raise ValueError(f"{name} cannot be empty")
    if expected_length is not None and len(values) != expected_length:
        raise ValueError(f"{name} has the wrong length")
    total = sum(values, Fraction(0))
    if total <= 0:
        raise ValueError(f"{name} must have positive total mass")
    return tuple(value / total for value in values)


def _canonical_weights(
    query_count: int,
    weights: Sequence[ProbabilityInput] | None,
) -> tuple[Fraction, ...]:
    if query_count < 1:
        raise ValueError("query_count must be positive")
    if weights is None:
        return tuple(Fraction(1, query_count) for _ in range(query_count))
    if len(weights) != query_count:
        raise ValueError("one query weight is required per query")
    return _canonical_distribution(weights, query_count, name="query weights")


def total_variation_fraction(
    left: Sequence[ProbabilityInput],
    right: Sequence[ProbabilityInput],
) -> Fraction:
    first = _canonical_distribution(left, name="left distribution")
    second = _canonical_distribution(
        right,
        len(first),
        name="right distribution",
    )
    return sum((abs(a - b) for a, b in zip(first, second)), Fraction(0)) / 2


def total_variation(
    left: Sequence[ProbabilityInput],
    right: Sequence[ProbabilityInput],
) -> float:
    return float(total_variation_fraction(left, right))


@dataclass(frozen=True)
class FiniteOutcomeChannel:
    """A finite row-stochastic Markov kernel represented exactly by fractions."""

    input_outcomes: tuple[Outcome, ...]
    output_outcomes: tuple[Outcome, ...]
    rows: tuple[tuple[Fraction, ...], ...]

    def __post_init__(self) -> None:
        inputs = tuple(self.input_outcomes)
        outputs = tuple(self.output_outcomes)
        try:
            valid_inputs = bool(inputs) and len(set(inputs)) == len(inputs)
            valid_outputs = bool(outputs) and len(set(outputs)) == len(outputs)
        except TypeError as error:
            raise ValueError("channel outcomes must be unique and hashable") from error
        if not valid_inputs:
            raise ValueError("input outcomes must be nonempty and unique")
        if not valid_outputs:
            raise ValueError("output outcomes must be nonempty and unique")
        if len(self.rows) != len(inputs):
            raise ValueError("one channel row is required per input outcome")
        canonical_rows = tuple(
            _canonical_distribution(
                row,
                len(outputs),
                name="channel row",
            )
            for row in self.rows
        )
        object.__setattr__(self, "input_outcomes", inputs)
        object.__setattr__(self, "output_outcomes", outputs)
        object.__setattr__(self, "rows", canonical_rows)

    @classmethod
    def identity(cls, outcomes: Sequence[Outcome]) -> "FiniteOutcomeChannel":
        alphabet = tuple(outcomes)
        return cls(
            alphabet,
            alphabet,
            tuple(
                tuple(Fraction(int(row == column), 1) for column in range(len(alphabet)))
                for row in range(len(alphabet))
            ),
        )

    @classmethod
    def binary_symmetric(
        cls,
        crossover: ProbabilityInput,
    ) -> "FiniteOutcomeChannel":
        q = _as_fraction(crossover, name="crossover probability")
        if q > Fraction(1, 2):
            raise ValueError("crossover probability must not exceed one half")
        return cls((0, 1), (0, 1), ((1 - q, q), (q, 1 - q)))

    @classmethod
    def erasure(
        cls,
        input_outcomes: Sequence[Outcome],
        erasure_probability: ProbabilityInput,
        *,
        erasure_outcome: Outcome = "erasure",
    ) -> "FiniteOutcomeChannel":
        inputs = tuple(input_outcomes)
        if erasure_outcome in inputs:
            raise ValueError("erasure outcome must be distinct from input outcomes")
        probability = _as_fraction(
            erasure_probability,
            name="erasure probability",
        )
        if probability > 1:
            raise ValueError("erasure probability must not exceed one")
        outputs = (*inputs, erasure_outcome)
        rows = tuple(
            tuple(
                probability
                if output == erasure_outcome
                else (1 - probability if output == input_value else Fraction(0))
                for output in outputs
            )
            for input_value in inputs
        )
        return cls(inputs, outputs, rows)

    def pushforward_fraction(
        self,
        probabilities: Sequence[ProbabilityInput],
    ) -> tuple[Fraction, ...]:
        distribution = _canonical_distribution(
            probabilities,
            len(self.input_outcomes),
            name="input distribution",
        )
        return tuple(
            sum(
                (
                    distribution[input_index]
                    * self.rows[input_index][output_index]
                    for input_index in range(len(self.input_outcomes))
                ),
                Fraction(0),
            )
            for output_index in range(len(self.output_outcomes))
        )

    def pushforward(
        self,
        probabilities: Sequence[ProbabilityInput],
    ) -> tuple[float, ...]:
        return tuple(float(value) for value in self.pushforward_fraction(probabilities))

    def compose(self, next_channel: "FiniteOutcomeChannel") -> "FiniteOutcomeChannel":
        """Apply ``self`` first and ``next_channel`` second."""

        if self.output_outcomes != next_channel.input_outcomes:
            raise ValueError("channel alphabets do not compose")
        return FiniteOutcomeChannel(
            self.input_outcomes,
            next_channel.output_outcomes,
            tuple(next_channel.pushforward_fraction(row) for row in self.rows),
        )

    @property
    def dobrushin_coefficient_fraction(self) -> Fraction:
        return max(
            (
                total_variation_fraction(self.rows[left], self.rows[right])
                for left in range(len(self.rows))
                for right in range(left + 1, len(self.rows))
            ),
            default=Fraction(0),
        )

    @property
    def dobrushin_coefficient(self) -> float:
        return float(self.dobrushin_coefficient_fraction)


@dataclass(frozen=True)
class ChannelContractionCertificate:
    before: Fraction
    after: Fraction
    coefficient: Fraction
    upper_bound: Fraction

    @property
    def valid(self) -> bool:
        return self.after <= self.upper_bound

    @property
    def slack(self) -> Fraction:
        return self.upper_bound - self.after


def channel_contraction_certificate(
    left: Sequence[ProbabilityInput],
    right: Sequence[ProbabilityInput],
    channel: FiniteOutcomeChannel,
) -> ChannelContractionCertificate:
    first = _canonical_distribution(
        left,
        len(channel.input_outcomes),
        name="left distribution",
    )
    second = _canonical_distribution(
        right,
        len(channel.input_outcomes),
        name="right distribution",
    )
    before = total_variation_fraction(first, second)
    after = total_variation_fraction(
        channel.pushforward_fraction(first),
        channel.pushforward_fraction(second),
    )
    coefficient = channel.dobrushin_coefficient_fraction
    certificate = ChannelContractionCertificate(
        before,
        after,
        coefficient,
        coefficient * before,
    )
    if not certificate.valid:
        raise AssertionError("finite channel violated Dobrushin contraction")
    return certificate


def compose_channel_chain(
    channels: Sequence[FiniteOutcomeChannel],
) -> FiniteOutcomeChannel:
    supplied = tuple(channels)
    if not supplied:
        raise ValueError("at least one channel is required")
    result = supplied[0]
    for channel in supplied[1:]:
        result = result.compose(channel)
    return result


def channel_chain_dobrushin_product_fraction(
    channels: Sequence[FiniteOutcomeChannel],
) -> Fraction:
    supplied = tuple(channels)
    if not supplied:
        return Fraction(1)
    for first, second in zip(supplied, supplied[1:]):
        if first.output_outcomes != second.input_outcomes:
            raise ValueError("channel alphabets do not compose")
    product_coefficient = Fraction(1)
    for channel in supplied:
        product_coefficient *= channel.dobrushin_coefficient_fraction
    return product_coefficient


@dataclass(frozen=True)
class ChannelChainCertificate:
    composed_coefficient: Fraction
    product_bound: Fraction

    @property
    def valid(self) -> bool:
        return self.composed_coefficient <= self.product_bound


def channel_chain_certificate(
    channels: Sequence[FiniteOutcomeChannel],
) -> ChannelChainCertificate:
    composed = compose_channel_chain(channels)
    certificate = ChannelChainCertificate(
        composed.dobrushin_coefficient_fraction,
        channel_chain_dobrushin_product_fraction(channels),
    )
    if not certificate.valid:
        raise AssertionError("serial channel coefficient exceeded product bound")
    return certificate


def apply_query_outcome_channels(
    family: FiniteStochasticQueryFamily,
    channels: Sequence[FiniteOutcomeChannel],
) -> FiniteStochasticQueryFamily:
    supplied = tuple(channels)
    if len(supplied) != family.query_count:
        raise ValueError("one outcome channel is required per query")
    for outcome_space, channel in zip(family.outcome_spaces, supplied):
        if tuple(outcome_space) != channel.input_outcomes:
            raise ValueError("channel input alphabet does not match query outcomes")
    transformed_tables = tuple(
        tuple(
            channel.pushforward(probabilities)
            for channel, probabilities in zip(supplied, table)
        )
        for table in family.conditional_laws
    )
    return FiniteStochasticQueryFamily(
        family.records,
        family.query_names,
        tuple(channel.output_outcomes for channel in supplied),
        transformed_tables,
    )


def _conditional_tv_fraction(
    left: Sequence[float],
    right: Sequence[float],
) -> Fraction:
    return total_variation_fraction(left, right)


@dataclass(frozen=True)
class QueryChannelContractionCertificate:
    before: Fraction
    after: Fraction
    querywise_bound: Fraction
    global_bound: Fraction
    max_coefficient: Fraction

    @property
    def valid(self) -> bool:
        return self.after <= self.querywise_bound <= self.global_bound


def query_channel_contraction_certificate(
    family: FiniteStochasticQueryFamily,
    left_record: Outcome,
    right_record: Outcome,
    channels: Sequence[FiniteOutcomeChannel],
    weights: Sequence[ProbabilityInput] | None = None,
) -> QueryChannelContractionCertificate:
    supplied = tuple(channels)
    if len(supplied) != family.query_count:
        raise ValueError("one outcome channel is required per query")
    for outcome_space, channel in zip(family.outcome_spaces, supplied):
        if tuple(outcome_space) != channel.input_outcomes:
            raise ValueError("channel input alphabet does not match query outcomes")
    query_weights = _canonical_weights(family.query_count, weights)
    first = family.laws(left_record)
    second = family.laws(right_record)
    conditional_before = tuple(
        _conditional_tv_fraction(left, right)
        for left, right in zip(first, second)
    )
    before = sum(
        (weight * distance for weight, distance in zip(query_weights, conditional_before)),
        Fraction(0),
    )
    conditional_after = tuple(
        total_variation_fraction(
            channel.pushforward_fraction(left),
            channel.pushforward_fraction(right),
        )
        for channel, left, right in zip(supplied, first, second)
    )
    after = sum(
        (weight * distance for weight, distance in zip(query_weights, conditional_after)),
        Fraction(0),
    )
    querywise_bound = sum(
        (
            weight * channel.dobrushin_coefficient_fraction * distance
            for weight, channel, distance in zip(
                query_weights,
                supplied,
                conditional_before,
            )
        ),
        Fraction(0),
    )
    maximum = max(
        (channel.dobrushin_coefficient_fraction for channel in supplied),
        default=Fraction(0),
    )
    certificate = QueryChannelContractionCertificate(
        before,
        after,
        querywise_bound,
        maximum * before,
        maximum,
    )
    if not certificate.valid:
        raise AssertionError("querywise Dobrushin contraction failed")
    return certificate


@dataclass(frozen=True)
class PredictiveComplexityContractionCertificate:
    before_exact_classes: int
    after_exact_classes: int
    before_packing: int
    after_packing: int
    before_target_cover: int
    after_target_cover: int

    @property
    def exact_classes_contract(self) -> bool:
        return self.after_exact_classes <= self.before_exact_classes

    @property
    def packing_contracts(self) -> bool:
        return self.after_packing <= self.before_packing

    @property
    def target_cover_contracts(self) -> bool:
        return self.after_target_cover <= self.before_target_cover

    @property
    def valid(self) -> bool:
        return (
            self.exact_classes_contract
            and self.packing_contracts
            and self.target_cover_contracts
        )


def predictive_complexity_contraction_certificate(
    family: FiniteStochasticQueryFamily,
    channels: Sequence[FiniteOutcomeChannel],
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    worst_query: bool = False,
    max_records: int = 24,
) -> PredictiveComplexityContractionCertificate:
    transformed = apply_query_outcome_channels(family, channels)
    before_packing = len(
        maximum_stochastic_predictive_packing(
            family,
            epsilon,
            weights,
            worst_query=worst_query,
            max_records=max_records,
        )
    )
    after_packing = len(
        maximum_stochastic_predictive_packing(
            transformed,
            epsilon,
            weights,
            worst_query=worst_query,
            max_records=max_records,
        )
    )
    before_cover = len(
        minimum_target_centered_cover(
            family,
            epsilon,
            weights,
            worst_query=worst_query,
            max_records=max_records,
        )
    )
    after_cover = len(
        minimum_target_centered_cover(
            transformed,
            epsilon,
            weights,
            worst_query=worst_query,
            max_records=max_records,
        )
    )
    certificate = PredictiveComplexityContractionCertificate(
        family.exact_class_count,
        transformed.exact_class_count,
        before_packing,
        after_packing,
        before_cover,
        after_cover,
    )
    if not certificate.valid:
        raise AssertionError("record-independent outcome channel increased predictive complexity")
    return certificate


def exhaustive_distribution_grid(
    outcomes: int,
    denominator: int,
) -> tuple[tuple[Fraction, ...], ...]:
    """All rational probability vectors with a fixed positive denominator."""

    if outcomes < 1 or denominator < 1:
        raise ValueError("outcomes and denominator must be positive")
    return tuple(
        tuple(Fraction(count, denominator) for count in counts)
        for counts in product(range(denominator + 1), repeat=outcomes)
        if sum(counts) == denominator
    )
