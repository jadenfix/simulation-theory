"""Exact probabilistic bisimulation for hidden source-law models.

Syntactically distinct hidden states need not be predictively distinct.  Two
hidden states are behaviorally equivalent for the declared coding interface when

1. they select the same categorical source law;
2. they emit the same observation-channel row;
3. they assign the same transition probability to every equivalence class.

The coarsest relation satisfying these conditions is computed by exact rational
partition refinement.  The quotient hidden Markov model aggregates initial mass
and transition probabilities by equivalence class while retaining one common
source law and observation row per class.

For every finite-horizon zero-error prefix-coding problem built on the model,
the quotient preserves no-signal, noisy-observation, perfect-current-state, and
expected clairvoyant path-oracle values.  Exact state identity within one class
cannot help because stage costs, signal laws, and future class-transition laws
are identical.

This is a predictive-state quotient theorem for the declared finite stochastic
model.  It does not claim that two physically distinct systems are ontologically
identical, and it does not turn hidden-state count into parent-substrate memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

from .belief_state_coding import (
    BeliefStateCodingCertificate,
    HiddenLawModel,
    hidden_law_model,
    exact_belief_state_prefix_coding,
)
from .confusion_graphs import ConfusionGraph
from .observation_channel_value import RationalObservationChannel

Partition = tuple[tuple[int, ...], ...]


def _canonical_partition(blocks: Iterable[Iterable[int]]) -> Partition:
    canonical = tuple(
        tuple(sorted(set(int(state) for state in block)))
        for block in blocks
    )
    if not canonical or any(not block for block in canonical):
        raise ValueError("partition blocks must be nonempty")
    flattened = tuple(state for block in canonical for state in block)
    if len(flattened) != len(set(flattened)):
        raise ValueError("partition blocks must be disjoint")
    return tuple(sorted(canonical, key=lambda block: (block[0], block)))


def _state_to_block(partition: Partition, state_count: int) -> tuple[int, ...]:
    mapping = [-1] * state_count
    for block_index, block in enumerate(partition):
        for state in block:
            if not 0 <= state < state_count or mapping[state] != -1:
                raise ValueError("partition does not contain valid unique states")
            mapping[state] = block_index
    if any(index < 0 for index in mapping):
        raise ValueError("partition does not cover every hidden state")
    return tuple(mapping)


def hidden_state_label(model: HiddenLawModel, state: int):
    index = int(state)
    if not 0 <= index < model.hidden_state_count:
        raise ValueError("hidden state out of range")
    return model.source_laws[index], model.observation.matrix[index]


def initial_label_partition(model: HiddenLawModel) -> Partition:
    if not model.valid:
        raise ValueError("hidden-law model must be valid")
    groups: dict[object, list[int]] = {}
    for state in range(model.hidden_state_count):
        groups.setdefault(hidden_state_label(model, state), []).append(state)
    return _canonical_partition(groups.values())


def transition_signature(
    model: HiddenLawModel,
    state: int,
    partition: Partition,
) -> tuple[Fraction, ...]:
    _state_to_block(partition, model.hidden_state_count)
    return tuple(
        sum(
            (model.transition[state][target] for target in block),
            Fraction(0),
        )
        for block in partition
    )


def refine_hidden_law_partition(
    model: HiddenLawModel,
    partition: Partition,
) -> Partition:
    """Split blocks by exact transition mass into the current blocks."""

    mapping = _state_to_block(partition, model.hidden_state_count)
    del mapping
    refined: list[tuple[int, ...]] = []
    for block in partition:
        groups: dict[tuple[Fraction, ...], list[int]] = {}
        for state in block:
            groups.setdefault(
                transition_signature(model, state, partition),
                [],
            ).append(state)
        refined.extend(tuple(group) for group in groups.values())
    return _canonical_partition(refined)


def partition_is_hidden_law_bisimulation(
    model: HiddenLawModel,
    partition: Partition,
) -> bool:
    try:
        _state_to_block(partition, model.hidden_state_count)
    except ValueError:
        return False
    for block in partition:
        representative = block[0]
        label = hidden_state_label(model, representative)
        signature = transition_signature(model, representative, partition)
        for state in block[1:]:
            if (
                hidden_state_label(model, state) != label
                or transition_signature(model, state, partition) != signature
            ):
                return False
    return True


@dataclass(frozen=True)
class HiddenLawBisimulationCertificate:
    model: HiddenLawModel
    refinement_trace: tuple[Partition, ...]
    partition: Partition

    @property
    def quotient_state_count(self) -> int:
        return len(self.partition)

    @property
    def state_reduction(self) -> int:
        return self.model.hidden_state_count - self.quotient_state_count

    @property
    def valid(self) -> bool:
        if (
            not self.model.valid
            or not self.refinement_trace
            or self.refinement_trace[0] != initial_label_partition(self.model)
            or self.refinement_trace[-1] != self.partition
            or self.state_reduction < 0
            or not partition_is_hidden_law_bisimulation(
                self.model,
                self.partition,
            )
        ):
            return False
        for current, following in zip(
            self.refinement_trace,
            self.refinement_trace[1:],
        ):
            if refine_hidden_law_partition(self.model, current) != following:
                return False
            current_map = _state_to_block(current, self.model.hidden_state_count)
            following_map = _state_to_block(
                following,
                self.model.hidden_state_count,
            )
            if any(
                current_map[left] != current_map[right]
                and following_map[left] == following_map[right]
                for left in range(self.model.hidden_state_count)
                for right in range(self.model.hidden_state_count)
            ):
                return False
        return refine_hidden_law_partition(self.model, self.partition) == self.partition


def exact_hidden_law_bisimulation(
    model: HiddenLawModel,
) -> HiddenLawBisimulationCertificate:
    """Return the coarsest stable partition respecting source/signal labels."""

    if not model.valid:
        raise ValueError("hidden-law model must be valid")
    trace = [initial_label_partition(model)]
    while True:
        refined = refine_hidden_law_partition(model, trace[-1])
        if refined == trace[-1]:
            break
        trace.append(refined)
    result = HiddenLawBisimulationCertificate(
        model,
        tuple(trace),
        trace[-1],
    )
    if not result.valid:
        raise AssertionError("hidden-law bisimulation certificate failed")
    return result


def quotient_hidden_law_model(
    certificate: HiddenLawBisimulationCertificate,
) -> HiddenLawModel:
    """Construct the exact class-level hidden Markov model."""

    if not certificate.valid:
        raise ValueError("bisimulation certificate must be valid")
    model = certificate.model
    partition = certificate.partition
    source_laws = tuple(model.source_laws[block[0]] for block in partition)
    observation_rows = tuple(
        model.observation.matrix[block[0]] for block in partition
    )
    initial = tuple(
        sum((model.initial_belief[state] for state in block), Fraction(0))
        for block in partition
    )
    transition = tuple(
        transition_signature(model, block[0], partition)
        for block in partition
    )
    return hidden_law_model(
        source_laws,
        initial,
        transition,
        RationalObservationChannel.from_values(observation_rows),
    )


def aggregate_hidden_belief(
    belief: Sequence[Fraction],
    partition: Partition,
) -> tuple[Fraction, ...]:
    supplied = tuple(Fraction(value) for value in belief)
    _state_to_block(partition, len(supplied))
    return tuple(
        sum((supplied[state] for state in block), Fraction(0))
        for block in partition
    )


@dataclass(frozen=True)
class HiddenLawQuotientValueCertificate:
    bisimulation: HiddenLawBisimulationCertificate
    quotient_model: HiddenLawModel
    original: BeliefStateCodingCertificate
    quotient: BeliefStateCodingCertificate

    @property
    def valid(self) -> bool:
        expected_quotient = quotient_hidden_law_model(self.bisimulation)
        return (
            self.bisimulation.valid
            and self.quotient_model == expected_quotient
            and self.original.valid
            and self.quotient.valid
            and self.original.graph == self.quotient.graph
            and self.original.horizon == self.quotient.horizon
            and self.original.switching_penalty
            == self.quotient.switching_penalty
            and self.original.model == self.bisimulation.model
            and self.quotient.model == self.quotient_model
            and self.original.no_signal_value == self.quotient.no_signal_value
            and self.original.observed_value == self.quotient.observed_value
            and self.original.perfect_value == self.quotient.perfect_value
            and self.original.clairvoyant_expected_value
            == self.quotient.clairvoyant_expected_value
            and self.original.no_signal_regret == self.quotient.no_signal_regret
            and self.original.observed_regret == self.quotient.observed_regret
            and self.original.perfect_regret == self.quotient.perfect_regret
        )


def exact_hidden_law_quotient_values(
    graph: ConfusionGraph,
    model: HiddenLawModel,
    horizon: int,
    *,
    switching_penalty=0,
    max_hidden_paths: int = 250_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> HiddenLawQuotientValueCertificate:
    """Solve original and quotient coding models independently and compare."""

    bisimulation = exact_hidden_law_bisimulation(model)
    quotient_model = quotient_hidden_law_model(bisimulation)
    kwargs = dict(
        switching_penalty=switching_penalty,
        max_hidden_paths=max_hidden_paths,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    original = exact_belief_state_prefix_coding(
        graph,
        model,
        horizon,
        **kwargs,
    )
    quotient = exact_belief_state_prefix_coding(
        graph,
        quotient_model,
        horizon,
        **kwargs,
    )
    result = HiddenLawQuotientValueCertificate(
        bisimulation,
        quotient_model,
        original,
        quotient,
    )
    if not result.valid:
        raise AssertionError("hidden-law quotient value certificate failed")
    return result
