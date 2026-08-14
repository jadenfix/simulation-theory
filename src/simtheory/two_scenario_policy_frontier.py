"""Exact two-scenario Pareto frontiers for repeated-observation policy trees.

The generic sequential policy-tree solver uses bounded pairwise dominance checks
for an arbitrary number of source-law scenarios.  With exactly two scenarios,
the same Pareto frontier has an exact ``O(N log N)`` construction.

Sort distinct policy cost pairs by increasing first-scenario cost and then by
increasing second-scenario cost.  A point is nondominated exactly when its
second cost is strictly smaller than every earlier second cost.  All discarded
points are dominated by an earlier point with no larger first cost and no
larger second cost.

This module reuses the generic policy-cost and certificate types while replacing
only the dominance algorithm.  It permits exact audits of larger two-scenario
policy trees without weakening the boundedness or the proof obligation.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Mapping, Sequence

from .confusion_graphs import ConfusionGraph
from .observation_channel_value import RationalObservationChannel
from .prior_weighted_codes import RationalInput, validate_rational_prior
from .repeated_observation_policies import (
    ExactInput,
    NoObservationSequence,
    SequentialObservationPolicy,
    SequentialObservationValueCertificate,
    SequentialPolicyEnumeration,
    _fraction,
    _history_tree,
    _matrix_from_columns,
    _no_observation_sequences,
    _sequential_policy_costs,
)
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    enumerate_robust_code_candidates,
    solve_exact_zero_sum_game,
)


def _exact_two_dimensional_frontier(
    candidates: Sequence[SequentialObservationPolicy],
) -> tuple[SequentialObservationPolicy, ...]:
    """Return every nondominated distinct two-coordinate cost vector."""

    ordered = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                candidate.scenario_total_costs[0],
                candidate.scenario_total_costs[1],
                candidate.codes_by_history,
            ),
        )
    )
    frontier: list[SequentialObservationPolicy] = []
    best_second: Fraction | None = None
    for candidate in ordered:
        second = candidate.scenario_total_costs[1]
        if best_second is None or second < best_second:
            frontier.append(candidate)
            best_second = second
    return tuple(frontier)


def enumerate_two_scenario_sequential_policies(
    channel: RationalObservationChannel,
    code_enumeration: RobustCandidateEnumeration,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_policies: int = 500_000,
) -> SequentialPolicyEnumeration:
    if not channel.valid or not code_enumeration.valid:
        raise ValueError("channel and code enumeration must be valid")
    if channel.scenario_count != 2 or code_enumeration.scenario_count != 2:
        raise ValueError("two-scenario frontier requires exactly two scenarios")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")
    histories = _history_tree(channel.signal_count, periods)
    code_count = len(code_enumeration.candidates)
    raw_count = code_count ** len(histories)
    if raw_count > int(max_policies):
        raise ValueError("sequential observation-policy space exceeds configured cap")

    by_cost: dict[tuple[Fraction, ...], SequentialObservationPolicy] = {}
    for codes in product(range(code_count), repeat=len(histories)):
        source, switches, totals = _sequential_policy_costs(
            channel,
            code_enumeration.candidates,
            histories,
            codes,
            periods,
            penalty,
        )
        policy = SequentialObservationPolicy(tuple(codes), source, switches, totals)
        incumbent = by_cost.get(totals)
        if incumbent is None or policy.codes_by_history < incumbent.codes_by_history:
            by_cost[totals] = policy

    distinct = tuple(by_cost.values())
    frontier = _exact_two_dimensional_frontier(distinct)
    result = SequentialPolicyEnumeration(
        channel,
        periods,
        penalty,
        histories,
        code_enumeration,
        frontier,
        raw_count,
        len(distinct),
        len(distinct) - len(frontier),
        int(max_policies),
        0,
    )
    if not result.valid:
        raise AssertionError("two-scenario sequential frontier failed validation")
    return result


def exact_two_scenario_sequential_observation_value(
    graph: ConfusionGraph,
    source_law_scenarios: Sequence[
        Sequence[ExactInput] | Mapping[object, ExactInput]
    ],
    channel: RationalObservationChannel,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_code_dominance_pairs: int = 4_000_000,
    max_policies: int = 500_000,
    max_sequences: int = 250_000,
    max_game_bases: int = 2_000_000,
) -> SequentialObservationValueCertificate:
    supplied = tuple(source_law_scenarios)
    if len(supplied) != 2:
        raise ValueError("exactly two source-law scenarios are required")
    scenarios = tuple(validate_rational_prior(graph, scenario) for scenario in supplied)
    if not channel.valid or channel.scenario_count != 2:
        raise ValueError("observation channel must have exactly two scenario rows")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    code_enumeration = enumerate_robust_code_candidates(
        graph,
        scenarios,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_code_dominance_pairs,
    )
    policies = enumerate_two_scenario_sequential_policies(
        channel,
        code_enumeration,
        periods,
        switching_penalty=penalty,
        max_policies=max_policies,
    )
    no_sequences = _no_observation_sequences(
        code_enumeration.candidates,
        periods,
        penalty,
        max_sequences=int(max_sequences),
    )

    selected_no = min(
        no_sequences,
        key=lambda sequence: (
            max(sequence.scenario_total_costs),
            sequence.switch_count,
            sequence.codes,
        ),
    )
    selected_policy = min(
        policies.policies,
        key=lambda policy: (
            max(policy.scenario_total_costs),
            policy.codes_by_history,
        ),
    )
    perfect_sequences = tuple(
        min(
            no_sequences,
            key=lambda sequence: (
                sequence.scenario_total_costs[scenario],
                sequence.switch_count,
                sequence.codes,
            ),
        )
        for scenario in range(2)
    )
    perfect = max(
        sequence.scenario_total_costs[scenario]
        for scenario, sequence in enumerate(perfect_sequences)
    )
    no_matrix = _matrix_from_columns(
        tuple(sequence.scenario_total_costs for sequence in no_sequences)
    )
    policy_matrix = _matrix_from_columns(
        tuple(policy.scenario_total_costs for policy in policies.policies)
    )
    result = SequentialObservationValueCertificate(
        graph,
        scenarios,
        channel,
        periods,
        penalty,
        code_enumeration,
        policies,
        no_sequences,
        max(selected_no.scenario_total_costs),
        selected_no,
        solve_exact_zero_sum_game(no_matrix, max_bases=max_game_bases),
        max(selected_policy.scenario_total_costs),
        selected_policy,
        solve_exact_zero_sum_game(policy_matrix, max_bases=max_game_bases),
        perfect,
        perfect_sequences,
    )
    if not result.valid:
        raise AssertionError("two-scenario sequential value certificate failed")
    return result
