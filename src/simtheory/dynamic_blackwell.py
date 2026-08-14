"""Exact finite-horizon Blackwell comparisons for hidden-law coding.

Let observation channel B be a garbling of channel A:

    B = A G,

where G is row stochastic.  A policy receiving A's signal can privately sample
G and then execute any policy designed for B.  Because the hidden transition
and observation channels are action independent, this simulation preserves the
joint hidden-state, garbled-signal, action, and switching-cost law.

The optimal expected cost under A is therefore no larger than under B.  The
repository's exact Bayesian dynamic programs return deterministic optimal
policies, but this does not weaken the argument: a deterministic optimum is no
worse than the randomized policy used to simulate the garbling.

The certificate solves both models independently and requires all quantities
that do not depend on the observation channel—no-signal cost, perfect-state
cost, and expected path-oracle cost—to agree exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .belief_state_coding import (
    BeliefStateCodingCertificate,
    ExactInput,
    hidden_law_model,
    exact_belief_state_prefix_coding,
)
from .confusion_graphs import ConfusionGraph
from .observation_channel_value import (
    RationalObservationChannel,
    garble_observation_channel,
)


@dataclass(frozen=True)
class DynamicBlackwellCertificate:
    richer: BeliefStateCodingCertificate
    poorer: BeliefStateCodingCertificate
    garbling_matrix: tuple[tuple[object, ...], ...]

    @property
    def observed_information_gain(self):
        return self.poorer.observed_value - self.richer.observed_value

    @property
    def valid(self) -> bool:
        richer_model = self.richer.model
        poorer_model = self.poorer.model
        try:
            reconstructed = garble_observation_channel(
                richer_model.observation,
                self.garbling_matrix,
            )
        except ValueError:
            return False
        return (
            self.richer.valid
            and self.poorer.valid
            and self.richer.graph == self.poorer.graph
            and self.richer.horizon == self.poorer.horizon
            and self.richer.switching_penalty == self.poorer.switching_penalty
            and richer_model.source_laws == poorer_model.source_laws
            and richer_model.initial_belief == poorer_model.initial_belief
            and richer_model.transition == poorer_model.transition
            and reconstructed == poorer_model.observation
            and self.richer.no_signal_value == self.poorer.no_signal_value
            and self.richer.perfect_value == self.poorer.perfect_value
            and self.richer.clairvoyant_expected_value
            == self.poorer.clairvoyant_expected_value
            and self.richer.observed_value <= self.poorer.observed_value
            and self.observed_information_gain >= 0
        )


def exact_dynamic_blackwell_comparison(
    graph: ConfusionGraph,
    source_laws: Sequence[Sequence[ExactInput]],
    initial_belief: Sequence[ExactInput],
    transition: Sequence[Sequence[ExactInput]],
    richer_channel: RationalObservationChannel,
    garbling_matrix: Sequence[Sequence[ExactInput]],
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_hidden_paths: int = 250_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> DynamicBlackwellCertificate:
    """Solve richer and garbled hidden-law coding models independently."""

    poorer_channel = garble_observation_channel(
        richer_channel,
        garbling_matrix,
    )
    richer_model = hidden_law_model(
        source_laws,
        initial_belief,
        transition,
        richer_channel,
    )
    poorer_model = hidden_law_model(
        source_laws,
        initial_belief,
        transition,
        poorer_channel,
    )
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
    richer = exact_belief_state_prefix_coding(
        graph,
        richer_model,
        horizon,
        **kwargs,
    )
    poorer = exact_belief_state_prefix_coding(
        graph,
        poorer_model,
        horizon,
        **kwargs,
    )
    result = DynamicBlackwellCertificate(
        richer,
        poorer,
        tuple(tuple(value for value in row) for row in garbling_matrix),
    )
    if not result.valid:
        raise AssertionError("dynamic Blackwell comparison failed validation")
    return result
