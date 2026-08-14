"""Exact repeated-observation channels and finite policy trees.

One noisy signal and a sequence of noisy signals are different information
structures.  This module keeps two repeated-observation questions separate.

Terminal decision
-----------------
A hidden source-law scenario is fixed, ``T`` conditionally independent public
signals are observed, and one zero-error prefix codebook is selected at the end.
The product channel is exact rational.  Projection from a longer history to a
prefix is an explicit deterministic garbling, so longer histories Blackwell-
dominate shorter ones for the shared-randomness terminal decision value.

Sequential decision
-------------------
After each new public signal, a deterministic policy tree chooses the period
codebook.  The hidden scenario remains fixed.  A rational switching penalty is
charged whenever adjacent selected codebooks differ.  The bounded checker
exhausts every complete signal-history policy, computes its exact scenario
costs, prunes componentwise-dominated policies, and solves deterministic and
public-shared-randomness minimax games exactly.

The public signal can provide both source information and coordination
randomness.  These remain distinct from an additional public seed independent
of the source scenario.

All claims are finite-scenario, finite-horizon, rational, bounded, deterministic
at the policy level, and internal to the declared coding model.  They are not
evidence for simulation and do not identify parent-substrate hardware, energy,
mass, or computation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb
from typing import Mapping, Sequence

from .confusion_graphs import ConfusionGraph
from .observation_channel_value import (
    ObservationValueCertificate,
    RationalObservationChannel,
    exact_observation_channel_value,
    garble_observation_channel,
)
from .prior_weighted_codes import RationalInput, validate_rational_prior
from .robust_prior_codes import (
    ExactZeroSumGameCertificate,
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
    solve_exact_zero_sum_game,
)

ExactInput = RationalInput | Fraction | int
Distribution = tuple[Fraction, ...]
History = tuple[int, ...]
Matrix = tuple[tuple[Fraction, ...], ...]


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _histories(signal_count: int, repetitions: int) -> tuple[History, ...]:
    signals = int(signal_count)
    count = int(repetitions)
    if signals != signal_count or signals < 1:
        raise ValueError("signal_count must be a positive integer")
    if count != repetitions or count < 0:
        raise ValueError("repetitions must be a nonnegative integer")
    if count == 0:
        return (tuple(),)
    return tuple(product(range(signals), repeat=count))


def _history_tree(signal_count: int, horizon: int) -> tuple[History, ...]:
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    return tuple(
        history
        for length in range(1, periods + 1)
        for history in _histories(signal_count, length)
    )


def _history_probability(
    channel: RationalObservationChannel,
    scenario: int,
    history: History,
) -> Fraction:
    probability = Fraction(1)
    for signal in history:
        probability *= channel.matrix[scenario][signal]
    return probability


@dataclass(frozen=True)
class ProductObservationChannelCertificate:
    base_channel: RationalObservationChannel
    repetitions: int
    histories: tuple[History, ...]
    channel: RationalObservationChannel

    @property
    def valid(self) -> bool:
        if (
            not self.base_channel.valid
            or self.repetitions < 1
            or len(self.histories)
            != self.base_channel.signal_count**self.repetitions
            or len(set(self.histories)) != len(self.histories)
            or not self.channel.valid
            or self.channel.scenario_count != self.base_channel.scenario_count
            or self.channel.signal_count != len(self.histories)
        ):
            return False
        expected = tuple(
            tuple(
                _history_probability(self.base_channel, scenario, history)
                for history in self.histories
            )
            for scenario in range(self.base_channel.scenario_count)
        )
        return self.channel.matrix == expected


def product_observation_channel(
    base_channel: RationalObservationChannel,
    repetitions: int,
    *,
    max_histories: int = 1_000_000,
) -> ProductObservationChannelCertificate:
    """Return the exact conditionally IID product observation channel."""

    if not base_channel.valid:
        raise ValueError("base observation channel must be valid")
    count = int(repetitions)
    if count != repetitions or count < 1:
        raise ValueError("repetitions must be a positive integer")
    history_count = base_channel.signal_count**count
    if history_count > int(max_histories):
        raise ValueError("product observation history space exceeds configured cap")
    histories = _histories(base_channel.signal_count, count)
    matrix = tuple(
        tuple(
            _history_probability(base_channel, scenario, history)
            for history in histories
        )
        for scenario in range(base_channel.scenario_count)
    )
    result = ProductObservationChannelCertificate(
        base_channel,
        count,
        histories,
        RationalObservationChannel(matrix),
    )
    if not result.valid:
        raise AssertionError("product observation channel failed validation")
    return result


def history_projection_garbling(
    signal_count: int,
    full_repetitions: int,
    retained_repetitions: int,
    *,
    max_entries: int = 2_000_000,
) -> Matrix:
    """Deterministically project a full signal history to its retained prefix."""

    full = int(full_repetitions)
    retained = int(retained_repetitions)
    if full != full_repetitions or full < 1:
        raise ValueError("full_repetitions must be a positive integer")
    if retained != retained_repetitions or not 1 <= retained <= full:
        raise ValueError("retained_repetitions must lie in [1, full_repetitions]")
    full_histories = _histories(signal_count, full)
    retained_histories = _histories(signal_count, retained)
    entries = len(full_histories) * len(retained_histories)
    if entries > int(max_entries):
        raise ValueError("history-projection matrix exceeds configured cap")
    retained_index = {
        history: index for index, history in enumerate(retained_histories)
    }
    return tuple(
        tuple(
            Fraction(1)
            if output == retained_index[history[:retained]]
            else Fraction(0)
            for output in range(len(retained_histories))
        )
        for history in full_histories
    )


@dataclass(frozen=True)
class RepeatedTerminalObservationCertificate:
    product: ProductObservationChannelCertificate
    value: ObservationValueCertificate

    @property
    def shared_value(self) -> Fraction:
        return self.value.shared_observation_value

    @property
    def deterministic_value(self) -> Fraction:
        return self.value.deterministic_observation_value

    @property
    def valid(self) -> bool:
        return (
            self.product.valid
            and self.value.valid
            and self.value.channel == self.product.channel
        )


def exact_repeated_terminal_observation_value(
    graph: ConfusionGraph,
    source_law_scenarios: Sequence[
        Sequence[ExactInput] | Mapping[object, ExactInput]
    ],
    base_channel: RationalObservationChannel,
    repetitions: int,
    *,
    max_histories: int = 1_000_000,
    **solver_kwargs: object,
) -> RepeatedTerminalObservationCertificate:
    product_channel = product_observation_channel(
        base_channel,
        repetitions,
        max_histories=max_histories,
    )
    value = exact_observation_channel_value(
        graph,
        source_law_scenarios,
        product_channel.channel,
        **solver_kwargs,
    )
    result = RepeatedTerminalObservationCertificate(product_channel, value)
    if not result.valid:
        raise AssertionError("repeated terminal observation certificate failed")
    return result


@dataclass(frozen=True)
class RepeatedTerminalBlackwellCertificate:
    longer: RepeatedTerminalObservationCertificate
    shorter: RepeatedTerminalObservationCertificate
    projection_garbling: Matrix

    @property
    def value_improvement(self) -> Fraction:
        return self.shorter.shared_value - self.longer.shared_value

    @property
    def valid(self) -> bool:
        return (
            self.longer.valid
            and self.shorter.valid
            and self.longer.product.base_channel
            == self.shorter.product.base_channel
            and self.longer.product.repetitions
            >= self.shorter.product.repetitions
            and garble_observation_channel(
                self.longer.product.channel,
                self.projection_garbling,
            )
            == self.shorter.product.channel
            and self.longer.shared_value <= self.shorter.shared_value
            and self.value_improvement >= 0
        )


def exact_repeated_terminal_blackwell_comparison(
    graph: ConfusionGraph,
    source_law_scenarios: Sequence[
        Sequence[ExactInput] | Mapping[object, ExactInput]
    ],
    base_channel: RationalObservationChannel,
    longer_repetitions: int,
    shorter_repetitions: int,
    *,
    max_histories: int = 1_000_000,
    max_projection_entries: int = 2_000_000,
    **solver_kwargs: object,
) -> RepeatedTerminalBlackwellCertificate:
    longer = exact_repeated_terminal_observation_value(
        graph,
        source_law_scenarios,
        base_channel,
        longer_repetitions,
        max_histories=max_histories,
        **solver_kwargs,
    )
    shorter = exact_repeated_terminal_observation_value(
        graph,
        source_law_scenarios,
        base_channel,
        shorter_repetitions,
        max_histories=max_histories,
        **solver_kwargs,
    )
    projection = history_projection_garbling(
        base_channel.signal_count,
        longer_repetitions,
        shorter_repetitions,
        max_entries=max_projection_entries,
    )
    result = RepeatedTerminalBlackwellCertificate(longer, shorter, projection)
    if not result.valid:
        raise AssertionError("repeated terminal Blackwell certificate failed")
    return result


def binary_symmetric_majority_accuracy(
    correct_probability: ExactInput,
    repetitions: int,
) -> Fraction:
    """Exact majority accuracy with a fair public tie break for even samples."""

    correct = _fraction(correct_probability, name="correct_probability")
    if not Fraction(1, 2) <= correct <= 1:
        raise ValueError("correct_probability must lie in [1/2,1]")
    count = int(repetitions)
    if count != repetitions or count < 1:
        raise ValueError("repetitions must be a positive integer")
    wrong = Fraction(1) - correct
    result = Fraction(0)
    for successes in range(count + 1):
        probability = (
            comb(count, successes)
            * correct**successes
            * wrong ** (count - successes)
        )
        if successes * 2 > count:
            result += probability
        elif successes * 2 == count:
            result += probability / 2
    return result


def symmetric_binary_terminal_cost(
    low_cost: ExactInput,
    high_cost: ExactInput,
    correct_probability: ExactInput,
    repetitions: int,
) -> Fraction:
    low = _fraction(low_cost, name="low_cost")
    high = _fraction(high_cost, name="high_cost")
    if low > high:
        raise ValueError("low_cost must not exceed high_cost")
    accuracy = binary_symmetric_majority_accuracy(
        correct_probability,
        repetitions,
    )
    return accuracy * low + (Fraction(1) - accuracy) * high


@dataclass(frozen=True)
class SequentialObservationPolicy:
    codes_by_history: tuple[int, ...]
    scenario_source_costs: tuple[Fraction, ...]
    scenario_expected_switches: tuple[Fraction, ...]
    scenario_total_costs: tuple[Fraction, ...]


@dataclass(frozen=True)
class SequentialPolicyEnumeration:
    channel: RationalObservationChannel
    horizon: int
    switching_penalty: Fraction
    histories: tuple[History, ...]
    code_enumeration: RobustCandidateEnumeration
    policies: tuple[SequentialObservationPolicy, ...]
    raw_policy_count: int
    distinct_cost_count: int
    dominated_count: int
    max_policies: int
    max_dominance_pairs: int

    @property
    def candidates(self) -> tuple[RobustCodeCandidate, ...]:
        return self.code_enumeration.candidates

    @property
    def valid(self) -> bool:
        if (
            not self.channel.valid
            or not self.code_enumeration.valid
            or self.channel.scenario_count != self.code_enumeration.scenario_count
            or self.horizon < 1
            or self.switching_penalty < 0
            or self.histories
            != _history_tree(self.channel.signal_count, self.horizon)
            or not self.policies
            or self.raw_policy_count < self.distinct_cost_count
            or self.distinct_cost_count != len(self.policies) + self.dominated_count
            or len({policy.scenario_total_costs for policy in self.policies})
            != len(self.policies)
        ):
            return False
        for policy in self.policies:
            expected = _sequential_policy_costs(
                self.channel,
                self.candidates,
                self.histories,
                policy.codes_by_history,
                self.horizon,
                self.switching_penalty,
            )
            if expected != (
                policy.scenario_source_costs,
                policy.scenario_expected_switches,
                policy.scenario_total_costs,
            ):
                return False
        return not any(
            _dominates(left.scenario_total_costs, right.scenario_total_costs)
            for left_index, left in enumerate(self.policies)
            for right_index, right in enumerate(self.policies)
            if left_index != right_index
        )


def _dominates(left: Sequence[Fraction], right: Sequence[Fraction]) -> bool:
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def _sequential_policy_costs(
    channel: RationalObservationChannel,
    candidates: Sequence[RobustCodeCandidate],
    histories: Sequence[History],
    codes_by_history: Sequence[int],
    horizon: int,
    switching_penalty: Fraction,
) -> tuple[
    tuple[Fraction, ...],
    tuple[Fraction, ...],
    tuple[Fraction, ...],
]:
    if len(histories) != len(codes_by_history):
        raise ValueError("one code decision is required per signal-history node")
    history_index = {history: index for index, history in enumerate(histories)}
    complete_histories = _histories(channel.signal_count, horizon)
    source_costs: list[Fraction] = []
    switch_expectations: list[Fraction] = []
    total_costs: list[Fraction] = []
    for scenario in range(channel.scenario_count):
        source = Fraction(0)
        switches = Fraction(0)
        for full_history in complete_histories:
            probability = _history_probability(channel, scenario, full_history)
            previous_code = -1
            history_source = Fraction(0)
            history_switches = 0
            for length in range(1, horizon + 1):
                prefix = full_history[:length]
                code = codes_by_history[history_index[prefix]]
                if not 0 <= code < len(candidates):
                    raise ValueError("policy references an invalid code index")
                history_source += candidates[code].scenario_costs[scenario]
                if previous_code >= 0 and code != previous_code:
                    history_switches += 1
                previous_code = code
            source += probability * history_source
            switches += probability * history_switches
        source_costs.append(source)
        switch_expectations.append(switches)
        total_costs.append(source + switching_penalty * switches)
    return tuple(source_costs), tuple(switch_expectations), tuple(total_costs)


def enumerate_sequential_observation_policies(
    channel: RationalObservationChannel,
    code_enumeration: RobustCandidateEnumeration,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    max_policies: int = 500_000,
    max_dominance_pairs: int = 4_000_000,
) -> SequentialPolicyEnumeration:
    if not channel.valid or not code_enumeration.valid:
        raise ValueError("channel and code enumeration must be valid")
    if channel.scenario_count != code_enumeration.scenario_count:
        raise ValueError("channel rows and source-law scenarios differ")
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
        candidate = SequentialObservationPolicy(tuple(codes), source, switches, totals)
        incumbent = by_cost.get(totals)
        if incumbent is None or candidate.codes_by_history < incumbent.codes_by_history:
            by_cost[totals] = candidate

    distinct = tuple(by_cost.values())
    if len(distinct) * max(0, len(distinct) - 1) > int(max_dominance_pairs):
        raise ValueError("sequential policy dominance space exceeds configured cap")
    nondominated = tuple(
        sorted(
            (
                candidate
                for index, candidate in enumerate(distinct)
                if not any(
                    _dominates(other.scenario_total_costs, candidate.scenario_total_costs)
                    for other_index, other in enumerate(distinct)
                    if other_index != index
                )
            ),
            key=lambda candidate: (
                candidate.scenario_total_costs,
                candidate.codes_by_history,
            ),
        )
    )
    result = SequentialPolicyEnumeration(
        channel,
        periods,
        penalty,
        histories,
        code_enumeration,
        nondominated,
        raw_count,
        len(distinct),
        len(distinct) - len(nondominated),
        int(max_policies),
        int(max_dominance_pairs),
    )
    if not result.valid:
        raise AssertionError("sequential observation-policy enumeration failed")
    return result


@dataclass(frozen=True)
class NoObservationSequence:
    codes: tuple[int, ...]
    scenario_total_costs: tuple[Fraction, ...]
    switch_count: int


def _no_observation_sequences(
    candidates: Sequence[RobustCodeCandidate],
    horizon: int,
    switching_penalty: Fraction,
    *,
    max_sequences: int,
) -> tuple[NoObservationSequence, ...]:
    count = len(candidates) ** horizon
    if count > max_sequences:
        raise ValueError("no-observation code-sequence space exceeds configured cap")
    by_cost: dict[tuple[Fraction, ...], NoObservationSequence] = {}
    for sequence in product(range(len(candidates)), repeat=horizon):
        switches = sum(left != right for left, right in zip(sequence, sequence[1:]))
        totals = tuple(
            sum(
                (candidates[code].scenario_costs[scenario] for code in sequence),
                Fraction(0),
            )
            + switching_penalty * switches
            for scenario in range(len(candidates[0].scenario_costs))
        )
        candidate = NoObservationSequence(tuple(sequence), totals, switches)
        incumbent = by_cost.get(totals)
        if incumbent is None or (candidate.switch_count, candidate.codes) < (
            incumbent.switch_count,
            incumbent.codes,
        ):
            by_cost[totals] = candidate
    distinct = tuple(by_cost.values())
    return tuple(
        sorted(
            (
                candidate
                for index, candidate in enumerate(distinct)
                if not any(
                    _dominates(other.scenario_total_costs, candidate.scenario_total_costs)
                    for other_index, other in enumerate(distinct)
                    if other_index != index
                )
            ),
            key=lambda candidate: (
                candidate.scenario_total_costs,
                candidate.switch_count,
                candidate.codes,
            ),
        )
    )


def _matrix_from_columns(columns: Sequence[Sequence[Fraction]]) -> Matrix:
    supplied = tuple(tuple(Fraction(value) for value in column) for column in columns)
    if not supplied:
        raise ValueError("at least one cost column is required")
    rows = len(supplied[0])
    if rows < 1 or any(len(column) != rows for column in supplied):
        raise ValueError("cost columns must have equal positive length")
    return tuple(
        tuple(supplied[column][row] for column in range(len(supplied)))
        for row in range(rows)
    )


@dataclass(frozen=True)
class SequentialObservationValueCertificate:
    graph: ConfusionGraph
    scenarios: tuple[Distribution, ...]
    channel: RationalObservationChannel
    horizon: int
    switching_penalty: Fraction
    code_enumeration: RobustCandidateEnumeration
    policy_enumeration: SequentialPolicyEnumeration
    no_observation_sequences: tuple[NoObservationSequence, ...]
    deterministic_no_observation_value: Fraction
    selected_no_observation_sequence: NoObservationSequence
    shared_no_observation_game: ExactZeroSumGameCertificate
    deterministic_observation_value: Fraction
    selected_observation_policy: SequentialObservationPolicy
    shared_observation_game: ExactZeroSumGameCertificate
    perfect_information_value: Fraction
    perfect_sequences: tuple[NoObservationSequence, ...]

    @property
    def shared_no_observation_value(self) -> Fraction:
        return self.shared_no_observation_game.value

    @property
    def shared_observation_value(self) -> Fraction:
        return self.shared_observation_game.value

    @property
    def information_value_over_shared_randomness(self) -> Fraction:
        return self.shared_no_observation_value - self.shared_observation_value

    @property
    def valid(self) -> bool:
        policies = self.policy_enumeration.policies
        if (
            not self.channel.valid
            or not self.code_enumeration.valid
            or not self.policy_enumeration.valid
            or self.policy_enumeration.code_enumeration != self.code_enumeration
            or self.policy_enumeration.channel != self.channel
            or self.policy_enumeration.horizon != self.horizon
            or self.policy_enumeration.switching_penalty != self.switching_penalty
            or self.scenarios != self.code_enumeration.priors
            or not self.no_observation_sequences
            or self.selected_no_observation_sequence not in self.no_observation_sequences
            or self.selected_observation_policy not in policies
            or not self.shared_no_observation_game.valid
            or not self.shared_observation_game.valid
            or len(self.perfect_sequences) != len(self.scenarios)
        ):
            return False
        no_matrix = _matrix_from_columns(
            tuple(sequence.scenario_total_costs for sequence in self.no_observation_sequences)
        )
        policy_matrix = _matrix_from_columns(
            tuple(policy.scenario_total_costs for policy in policies)
        )
        perfect_sequences = tuple(
            min(
                self.no_observation_sequences,
                key=lambda sequence: (
                    sequence.scenario_total_costs[scenario],
                    sequence.switch_count,
                    sequence.codes,
                ),
            )
            for scenario in range(len(self.scenarios))
        )
        perfect = max(
            sequence.scenario_total_costs[scenario]
            for scenario, sequence in enumerate(perfect_sequences)
        )
        return (
            self.shared_no_observation_game.cost_matrix == no_matrix
            and self.shared_observation_game.cost_matrix == policy_matrix
            and self.deterministic_no_observation_value
            == min(max(sequence.scenario_total_costs) for sequence in self.no_observation_sequences)
            and max(self.selected_no_observation_sequence.scenario_total_costs)
            == self.deterministic_no_observation_value
            and self.deterministic_observation_value
            == min(max(policy.scenario_total_costs) for policy in policies)
            and max(self.selected_observation_policy.scenario_total_costs)
            == self.deterministic_observation_value
            and self.perfect_sequences == perfect_sequences
            and self.perfect_information_value == perfect
            and self.perfect_information_value
            <= self.shared_observation_value
            <= self.shared_no_observation_value
            <= self.deterministic_no_observation_value
            and self.shared_observation_value
            <= self.deterministic_observation_value
            <= self.deterministic_no_observation_value
            and self.information_value_over_shared_randomness >= 0
        )


def exact_sequential_observation_value(
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
    max_policy_dominance_pairs: int = 4_000_000,
    max_sequences: int = 250_000,
    max_game_bases: int = 2_000_000,
) -> SequentialObservationValueCertificate:
    supplied = tuple(source_law_scenarios)
    if not supplied:
        raise ValueError("at least one source-law scenario is required")
    scenarios = tuple(validate_rational_prior(graph, scenario) for scenario in supplied)
    if not channel.valid or channel.scenario_count != len(scenarios):
        raise ValueError("channel rows must match source-law scenarios")
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
    policies = enumerate_sequential_observation_policies(
        channel,
        code_enumeration,
        periods,
        switching_penalty=penalty,
        max_policies=max_policies,
        max_dominance_pairs=max_policy_dominance_pairs,
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
        for scenario in range(len(scenarios))
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
        raise AssertionError("sequential observation value certificate failed")
    return result
