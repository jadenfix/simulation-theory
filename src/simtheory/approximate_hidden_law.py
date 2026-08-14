"""Finite-horizon value bounds for approximate hidden-law quotients.

Exact bisimulation is brittle: empirical source laws, observation channels, and
transition kernels are rarely identical rational objects.  This module compares
one detailed hidden-law model with one declared abstract model through a mapping
from detailed states to abstract states.

The comparison records five exact deviations:

* initial abstract-state total variation;
* categorical source-law total variation;
* induced stage-cost deviation over the complete bounded zero-error codebook
  universe;
* observation-row total variation;
* abstract transition-kernel total variation.

A sequential maximal-coupling argument gives one explicit mismatch bound.  If
initial abstract states are coupled, then at every period matched states can
emit the same signal with probability at least ``1-e_obs`` and can move to the
same next abstract state with probability at least ``1-e_trans``.  Therefore

    P(no divergence through T)
      >= (1-e_init) (1-e_obs)^T (1-e_trans)^(T-1).

On the no-divergence event, every common signal-history policy selects the same
codebooks and switching events, while each stage cost differs by at most
``e_stage``.  On the complement, the total cost difference is bounded by the
full finite-horizon cost ceiling.  Consequently every common policy satisfies

    |E C_P - E C_Q|
      <= T e_stage + M_T P(divergence).

The same uniform bound transfers to optimal no-signal and noisy-observation
values.  A separate transition-only coupling bounds the expected clairvoyant
code-sequence oracle.  Bayes-regret differences are bounded by the sum of the
policy-value and oracle bounds.

The result is deliberately conservative and finite horizon.  It does not claim
that the chosen partition is optimal, that coupling bounds are tight, or that
abstract-state count is parent-substrate memory.  Perfect observation of the
*detailed* hidden state is not covered unless exact bisimulation removes the
extra information.
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
from .distributionally_robust_codes import total_variation_distance
from .observation_channel_value import RationalObservationChannel
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    enumerate_robust_code_candidates,
)

Partition = tuple[tuple[int, ...], ...]


def _partition(
    blocks: Iterable[Iterable[int]],
    state_count: int,
) -> tuple[Partition, tuple[int, ...]]:
    canonical = tuple(
        tuple(sorted(set(int(state) for state in block)))
        for block in blocks
    )
    if not canonical or any(not block for block in canonical):
        raise ValueError("partition blocks must be nonempty")
    canonical = tuple(sorted(canonical, key=lambda block: (block[0], block)))
    mapping = [-1] * state_count
    for block_index, block in enumerate(canonical):
        for state in block:
            if not 0 <= state < state_count or mapping[state] != -1:
                raise ValueError("partition contains an invalid or duplicate state")
            mapping[state] = block_index
    if any(index < 0 for index in mapping):
        raise ValueError("partition must cover every detailed hidden state")
    return canonical, tuple(mapping)


def _simplex_vertices(state_count: int):
    return tuple(
        tuple(
            Fraction(1) if state == vertex else Fraction(0)
            for state in range(state_count)
        )
        for vertex in range(state_count)
    )


def _expected_length(law, lengths) -> Fraction:
    return sum(
        (probability * length for probability, length in zip(law, lengths)),
        Fraction(0),
    )


def aggregate_transition_to_partition(
    model: HiddenLawModel,
    state: int,
    partition: Partition,
) -> tuple[Fraction, ...]:
    if not 0 <= state < model.hidden_state_count:
        raise ValueError("detailed hidden state out of range")
    return tuple(
        sum((model.transition[state][target] for target in block), Fraction(0))
        for block in partition
    )


def representative_approximate_quotient(
    model: HiddenLawModel,
    blocks: Iterable[Iterable[int]],
) -> HiddenLawModel:
    """Choose the first state in each block as a deterministic abstraction.

    Initial mass is aggregated exactly.  Source laws, observation rows, and
    abstract transition rows are taken from the first state in each block.  The
    accompanying deviation certificate quantifies the approximation introduced
    by this representative choice.
    """

    if not model.valid:
        raise ValueError("detailed hidden-law model must be valid")
    partition, _ = _partition(blocks, model.hidden_state_count)
    source_laws = tuple(model.source_laws[block[0]] for block in partition)
    observation_rows = tuple(
        model.observation.matrix[block[0]] for block in partition
    )
    initial = tuple(
        sum((model.initial_belief[state] for state in block), Fraction(0))
        for block in partition
    )
    transition = tuple(
        aggregate_transition_to_partition(model, block[0], partition)
        for block in partition
    )
    return hidden_law_model(
        source_laws,
        initial,
        transition,
        RationalObservationChannel.from_values(observation_rows),
    )


@dataclass(frozen=True)
class ApproximateHiddenLawCertificate:
    graph: ConfusionGraph
    detailed_model: HiddenLawModel
    abstract_model: HiddenLawModel
    partition: Partition
    state_to_abstract: tuple[int, ...]
    horizon: int
    switching_penalty: Fraction
    common_codebooks: RobustCandidateEnumeration
    initial_tv: Fraction
    maximum_source_tv: Fraction
    maximum_stage_deviation: Fraction
    maximum_observation_tv: Fraction
    maximum_transition_tv: Fraction
    maximum_codeword_length: int
    maximum_codeword_span: int
    no_signal_divergence_bound: Fraction
    observed_divergence_bound: Fraction
    total_cost_ceiling: Fraction
    no_signal_value_bound: Fraction
    observed_value_bound: Fraction
    oracle_value_bound: Fraction
    detailed_values: BeliefStateCodingCertificate
    abstract_values: BeliefStateCodingCertificate

    @property
    def detailed_regrets(self) -> tuple[Fraction, Fraction]:
        return (
            self.detailed_values.no_signal_regret,
            self.detailed_values.observed_regret,
        )

    @property
    def abstract_regrets(self) -> tuple[Fraction, Fraction]:
        return (
            self.abstract_values.no_signal_regret,
            self.abstract_values.observed_regret,
        )

    @property
    def no_signal_regret_bound(self) -> Fraction:
        return self.no_signal_value_bound + self.oracle_value_bound

    @property
    def observed_regret_bound(self) -> Fraction:
        return self.observed_value_bound + self.oracle_value_bound

    @property
    def exact_limit(self) -> bool:
        return all(
            deviation == 0
            for deviation in (
                self.initial_tv,
                self.maximum_stage_deviation,
                self.maximum_observation_tv,
                self.maximum_transition_tv,
            )
        )

    @property
    def valid(self) -> bool:
        if (
            not self.detailed_model.valid
            or not self.abstract_model.valid
            or self.graph.vertex_count != self.detailed_model.source_symbol_count
            or self.graph.vertex_count != self.abstract_model.source_symbol_count
            or self.detailed_model.observation.signal_count
            != self.abstract_model.observation.signal_count
            or self.horizon < 1
            or self.switching_penalty < 0
            or not self.common_codebooks.valid
            or self.common_codebooks.graph != self.graph
            or len(self.state_to_abstract) != self.detailed_model.hidden_state_count
            or len(self.partition) != self.abstract_model.hidden_state_count
            or any(
                not 0 <= index < self.abstract_model.hidden_state_count
                for index in self.state_to_abstract
            )
            or not self.detailed_values.valid
            or not self.abstract_values.valid
        ):
            return False

        try:
            partition, mapping = _partition(
                self.partition,
                self.detailed_model.hidden_state_count,
            )
        except ValueError:
            return False
        if partition != self.partition or mapping != self.state_to_abstract:
            return False

        aggregated_initial = tuple(
            sum(
                (
                    self.detailed_model.initial_belief[state]
                    for state in block
                ),
                Fraction(0),
            )
            for block in self.partition
        )
        initial_tv = total_variation_distance(
            aggregated_initial,
            self.abstract_model.initial_belief,
        )
        source_tv = max(
            total_variation_distance(
                self.detailed_model.source_laws[state],
                self.abstract_model.source_laws[self.state_to_abstract[state]],
            )
            for state in range(self.detailed_model.hidden_state_count)
        )
        observation_tv = max(
            total_variation_distance(
                self.detailed_model.observation.matrix[state],
                self.abstract_model.observation.matrix[
                    self.state_to_abstract[state]
                ],
            )
            for state in range(self.detailed_model.hidden_state_count)
        )
        transition_tv = max(
            total_variation_distance(
                aggregate_transition_to_partition(
                    self.detailed_model,
                    state,
                    self.partition,
                ),
                self.abstract_model.transition[self.state_to_abstract[state]],
            )
            for state in range(self.detailed_model.hidden_state_count)
        )
        candidates = self.common_codebooks.candidates
        stage_deviation = max(
            abs(
                _expected_length(
                    self.detailed_model.source_laws[state],
                    candidate.scenario_costs,
                )
                - _expected_length(
                    self.abstract_model.source_laws[
                        self.state_to_abstract[state]
                    ],
                    candidate.scenario_costs,
                )
            )
            for state in range(self.detailed_model.hidden_state_count)
            for candidate in candidates
        )
        maximum_length = max(
            max(candidate.scenario_costs) for candidate in candidates
        )
        maximum_span = max(
            max(candidate.scenario_costs) - min(candidate.scenario_costs)
            for candidate in candidates
        )
        no_signal_divergence = Fraction(1) - (
            (Fraction(1) - initial_tv)
            * (Fraction(1) - transition_tv) ** (self.horizon - 1)
        )
        observed_divergence = Fraction(1) - (
            (Fraction(1) - initial_tv)
            * (Fraction(1) - observation_tv) ** self.horizon
            * (Fraction(1) - transition_tv) ** (self.horizon - 1)
        )
        total_ceiling = (
            self.horizon * maximum_length
            + (self.horizon - 1) * self.switching_penalty
        )
        no_signal_bound = (
            self.horizon * stage_deviation
            + total_ceiling * no_signal_divergence
        )
        observed_bound = (
            self.horizon * stage_deviation
            + total_ceiling * observed_divergence
        )
        oracle_bound = no_signal_bound

        exact_differences = (
            abs(
                self.detailed_values.no_signal_value
                - self.abstract_values.no_signal_value
            ),
            abs(
                self.detailed_values.observed_value
                - self.abstract_values.observed_value
            ),
            abs(
                self.detailed_values.clairvoyant_expected_value
                - self.abstract_values.clairvoyant_expected_value
            ),
            abs(
                self.detailed_values.no_signal_regret
                - self.abstract_values.no_signal_regret
            ),
            abs(
                self.detailed_values.observed_regret
                - self.abstract_values.observed_regret
            ),
        )
        return (
            self.initial_tv == initial_tv
            and self.maximum_source_tv == source_tv
            and self.maximum_stage_deviation == stage_deviation
            and self.maximum_observation_tv == observation_tv
            and self.maximum_transition_tv == transition_tv
            and self.maximum_codeword_length == maximum_length
            and self.maximum_codeword_span == maximum_span
            and self.maximum_stage_deviation
            <= self.maximum_source_tv * self.maximum_codeword_span
            and self.no_signal_divergence_bound == no_signal_divergence
            and self.observed_divergence_bound == observed_divergence
            and 0 <= no_signal_divergence <= observed_divergence <= 1
            and self.total_cost_ceiling == total_ceiling
            and self.no_signal_value_bound == no_signal_bound
            and self.observed_value_bound == observed_bound
            and self.oracle_value_bound == oracle_bound
            and exact_differences[0] <= self.no_signal_value_bound
            and exact_differences[1] <= self.observed_value_bound
            and exact_differences[2] <= self.oracle_value_bound
            and exact_differences[3] <= self.no_signal_regret_bound
            and exact_differences[4] <= self.observed_regret_bound
            and (
                not self.exact_limit
                or all(difference == 0 for difference in exact_differences)
            )
        )


def exact_approximate_hidden_law_comparison(
    graph: ConfusionGraph,
    detailed_model: HiddenLawModel,
    abstract_model: HiddenLawModel,
    blocks: Iterable[Iterable[int]],
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
) -> ApproximateHiddenLawCertificate:
    """Compute exact deviations, coupling bounds, and independently solved values."""

    if not detailed_model.valid or not abstract_model.valid:
        raise ValueError("both hidden-law models must be valid")
    partition, mapping = _partition(
        blocks,
        detailed_model.hidden_state_count,
    )
    if len(partition) != abstract_model.hidden_state_count:
        raise ValueError("one abstract hidden state is required per partition block")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = Fraction(switching_penalty)
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")
    if (
        graph.vertex_count != detailed_model.source_symbol_count
        or graph.vertex_count != abstract_model.source_symbol_count
    ):
        raise ValueError("graph and source-law alphabets differ")
    if (
        detailed_model.observation.signal_count
        != abstract_model.observation.signal_count
    ):
        raise ValueError("observation signal alphabets differ")

    common_codebooks = enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = common_codebooks.candidates
    aggregated_initial = tuple(
        sum((detailed_model.initial_belief[state] for state in block), Fraction(0))
        for block in partition
    )
    initial_tv = total_variation_distance(
        aggregated_initial,
        abstract_model.initial_belief,
    )
    source_tv = max(
        total_variation_distance(
            detailed_model.source_laws[state],
            abstract_model.source_laws[mapping[state]],
        )
        for state in range(detailed_model.hidden_state_count)
    )
    stage_deviation = max(
        abs(
            _expected_length(
                detailed_model.source_laws[state],
                candidate.scenario_costs,
            )
            - _expected_length(
                abstract_model.source_laws[mapping[state]],
                candidate.scenario_costs,
            )
        )
        for state in range(detailed_model.hidden_state_count)
        for candidate in candidates
    )
    observation_tv = max(
        total_variation_distance(
            detailed_model.observation.matrix[state],
            abstract_model.observation.matrix[mapping[state]],
        )
        for state in range(detailed_model.hidden_state_count)
    )
    transition_tv = max(
        total_variation_distance(
            aggregate_transition_to_partition(detailed_model, state, partition),
            abstract_model.transition[mapping[state]],
        )
        for state in range(detailed_model.hidden_state_count)
    )
    maximum_length = max(max(candidate.scenario_costs) for candidate in candidates)
    maximum_span = max(
        max(candidate.scenario_costs) - min(candidate.scenario_costs)
        for candidate in candidates
    )
    no_signal_divergence = Fraction(1) - (
        (Fraction(1) - initial_tv)
        * (Fraction(1) - transition_tv) ** (periods - 1)
    )
    observed_divergence = Fraction(1) - (
        (Fraction(1) - initial_tv)
        * (Fraction(1) - observation_tv) ** periods
        * (Fraction(1) - transition_tv) ** (periods - 1)
    )
    total_ceiling = periods * maximum_length + (periods - 1) * penalty
    no_signal_bound = periods * stage_deviation + total_ceiling * no_signal_divergence
    observed_bound = periods * stage_deviation + total_ceiling * observed_divergence

    solve_kwargs = dict(
        switching_penalty=penalty,
        max_hidden_paths=max_hidden_paths,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    detailed_values = exact_belief_state_prefix_coding(
        graph,
        detailed_model,
        periods,
        **solve_kwargs,
    )
    abstract_values = exact_belief_state_prefix_coding(
        graph,
        abstract_model,
        periods,
        **solve_kwargs,
    )
    result = ApproximateHiddenLawCertificate(
        graph,
        detailed_model,
        abstract_model,
        partition,
        mapping,
        periods,
        penalty,
        common_codebooks,
        initial_tv,
        source_tv,
        stage_deviation,
        observation_tv,
        transition_tv,
        maximum_length,
        maximum_span,
        no_signal_divergence,
        observed_divergence,
        total_ceiling,
        no_signal_bound,
        observed_bound,
        no_signal_bound,
        detailed_values,
        abstract_values,
    )
    if not result.valid:
        raise AssertionError("approximate hidden-law comparison failed validation")
    return result
