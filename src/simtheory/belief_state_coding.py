"""Exact finite-horizon coding under a hidden Markov source law.

The adversarial source-path lanes and a stochastic hidden-law model answer
different questions.  This module declares a finite rational hidden Markov
model:

* hidden scenario S_t selects one categorical source law;
* S_1 has a declared rational initial distribution;
* S_{t+1} follows a declared rational Markov transition matrix;
* before selecting the period-t codebook, the designer observes a signal Y_t
  through a declared rational channel P(Y_t | S_t);
* one deterministic zero-error prefix codebook is selected after the signal;
* changing codebooks incurs one declared rational switching charge.

The posterior belief over S_t is an exact sufficient statistic for expected-cost
optimization.  The module solves three causal information patterns:

1. no source-law signal;
2. noisy current signal and exact Bayesian filtering;
3. perfect current hidden-state observation.

It also enumerates every positive-probability hidden-state path and computes the
path-specific clairvoyant code-sequence oracle.  Since expected regret against
that oracle equals expected policy cost minus one policy-independent constant,
the expected-cost-optimal policy is also Bayes-regret optimal.

The exact hierarchy is

    E[oracle] <= V_perfect <= V_observed <= V_no_signal.

An identity observation channel collapses observed and perfect-state values.  A
signal independent of the hidden state collapses observed and no-signal values:
in a Bayesian expected-cost problem exogenous randomization cannot beat the
best deterministic policy, unlike in a minimax game where public randomization
can convexify worst-case loss.

All arithmetic is exact rational after the finite model is declared.  The model
is Bayesian rather than distributionally robust, action-independent in its
hidden dynamics and observation channel, finite-horizon, and bounded by explicit
enumeration caps.  It is not evidence for simulation and does not map internal
beliefs, code lengths, or switching charges to parent-substrate resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .observation_channel_value import RationalObservationChannel
from .prior_weighted_codes import RationalInput, validate_rational_prior
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)

ExactInput = RationalInput | Fraction | int
Distribution = tuple[Fraction, ...]
Belief = tuple[Fraction, ...]
Matrix = tuple[tuple[Fraction, ...], ...]
HiddenPath = tuple[int, ...]


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _validate_distribution(
    values: Sequence[ExactInput],
    *,
    name: str,
    expected_length: int | None = None,
) -> Distribution:
    distribution = tuple(_fraction(value, name=name) for value in values)
    if not distribution:
        raise ValueError(f"{name} cannot be empty")
    if expected_length is not None and len(distribution) != expected_length:
        raise ValueError(f"{name} has the wrong dimension")
    if any(value < 0 for value in distribution):
        raise ValueError(f"{name} must be nonnegative")
    if sum(distribution, Fraction(0)) != 1:
        raise ValueError(f"{name} must sum exactly to one")
    return distribution


def _validate_stochastic_matrix(
    values: Sequence[Sequence[ExactInput]],
    *,
    state_count: int,
    name: str,
) -> Matrix:
    matrix = tuple(
        _validate_distribution(
            row,
            name=f"{name} row",
            expected_length=state_count,
        )
        for row in values
    )
    if len(matrix) != state_count:
        raise ValueError(f"{name} requires one row per hidden state")
    return matrix


def predict_belief(belief: Belief, transition: Matrix) -> Belief:
    if not belief or len(transition) != len(belief):
        raise ValueError("belief and transition dimensions differ")
    if any(len(row) != len(belief) for row in transition):
        raise ValueError("transition matrix must be square")
    result = tuple(
        sum(
            (
                belief[state] * transition[state][next_state]
                for state in range(len(belief))
            ),
            Fraction(0),
        )
        for next_state in range(len(belief))
    )
    if any(value < 0 for value in result) or sum(result, Fraction(0)) != 1:
        raise AssertionError("belief prediction left the probability simplex")
    return result


def signal_probability(
    belief: Belief,
    channel: RationalObservationChannel,
    signal: int,
) -> Fraction:
    if not channel.valid or channel.scenario_count != len(belief):
        raise ValueError("belief and observation channel dimensions differ")
    index = int(signal)
    if not 0 <= index < channel.signal_count:
        raise ValueError("signal index out of range")
    return sum(
        (
            belief[state] * channel.matrix[state][index]
            for state in range(len(belief))
        ),
        Fraction(0),
    )


def posterior_belief(
    belief: Belief,
    channel: RationalObservationChannel,
    signal: int,
) -> Belief:
    probability = signal_probability(belief, channel, signal)
    if probability <= 0:
        raise ValueError("cannot condition on a zero-probability signal")
    result = tuple(
        belief[state] * channel.matrix[state][signal] / probability
        for state in range(len(belief))
    )
    if any(value < 0 for value in result) or sum(result, Fraction(0)) != 1:
        raise AssertionError("Bayesian posterior left the probability simplex")
    return result


def expected_candidate_cost(
    belief: Belief,
    candidate: RobustCodeCandidate,
) -> Fraction:
    if len(belief) != len(candidate.scenario_costs):
        raise ValueError("belief and candidate scenario dimensions differ")
    return sum(
        (
            probability * cost
            for probability, cost in zip(belief, candidate.scenario_costs)
        ),
        Fraction(0),
    )


def _switch_cost(previous_code: int, next_code: int, penalty: Fraction) -> Fraction:
    return (
        penalty
        if previous_code >= 0 and previous_code != next_code
        else Fraction(0)
    )


@dataclass(frozen=True)
class HiddenLawModel:
    source_laws: tuple[Distribution, ...]
    initial_belief: Belief
    transition: Matrix
    observation: RationalObservationChannel

    @property
    def hidden_state_count(self) -> int:
        return len(self.source_laws)

    @property
    def source_symbol_count(self) -> int:
        return len(self.source_laws[0]) if self.source_laws else 0

    @property
    def observation_is_uninformative(self) -> bool:
        return all(row == self.observation.matrix[0] for row in self.observation.matrix)

    @property
    def observation_is_identity(self) -> bool:
        count = self.hidden_state_count
        return (
            self.observation.signal_count == count
            and self.observation.matrix
            == tuple(
                tuple(
                    Fraction(1) if row == column else Fraction(0)
                    for column in range(count)
                )
                for row in range(count)
            )
        )

    @property
    def valid(self) -> bool:
        state_count = self.hidden_state_count
        symbol_count = self.source_symbol_count
        return (
            state_count >= 1
            and symbol_count >= 1
            and len(self.initial_belief) == state_count
            and all(value >= 0 for value in self.initial_belief)
            and sum(self.initial_belief, Fraction(0)) == 1
            and len(self.transition) == state_count
            and all(
                len(row) == state_count
                and all(value >= 0 for value in row)
                and sum(row, Fraction(0)) == 1
                for row in self.transition
            )
            and all(
                len(law) == symbol_count
                and all(value >= 0 for value in law)
                and sum(law, Fraction(0)) == 1
                for law in self.source_laws
            )
            and self.observation.valid
            and self.observation.scenario_count == state_count
        )


def hidden_law_model(
    source_laws: Sequence[Sequence[ExactInput]],
    initial_belief: Sequence[ExactInput],
    transition: Sequence[Sequence[ExactInput]],
    observation: RationalObservationChannel,
) -> HiddenLawModel:
    laws = tuple(
        _validate_distribution(law, name="source law")
        for law in source_laws
    )
    if not laws or any(len(law) != len(laws[0]) for law in laws):
        raise ValueError("source laws must have one common positive alphabet")
    initial = _validate_distribution(
        initial_belief,
        name="initial hidden-state belief",
        expected_length=len(laws),
    )
    transition_matrix = _validate_stochastic_matrix(
        transition,
        state_count=len(laws),
        name="hidden-state transition",
    )
    model = HiddenLawModel(laws, initial, transition_matrix, observation)
    if not model.valid:
        raise ValueError("hidden-law model failed validation")
    return model


@dataclass(frozen=True)
class NoSignalPolicyEntry:
    period: int
    prior_belief: Belief
    previous_code: int
    value: Fraction
    selected_code: int
    next_belief: Belief


@dataclass(frozen=True)
class SignalPolicyChoice:
    signal: int
    signal_probability: Fraction
    posterior: Belief
    selected_code: int
    next_belief: Belief
    conditional_value: Fraction


@dataclass(frozen=True)
class ObservedPolicyEntry:
    period: int
    prior_belief: Belief
    previous_code: int
    value: Fraction
    signal_choices: tuple[SignalPolicyChoice, ...]


@dataclass(frozen=True)
class PerfectPolicyEntry:
    period: int
    hidden_state: int
    previous_code: int
    value: Fraction
    selected_code: int


@dataclass(frozen=True)
class HiddenPathOracleReceipt:
    hidden_path: HiddenPath
    probability: Fraction
    oracle_cost: Fraction
    terminal_frontier: tuple[Fraction, ...]


@dataclass(frozen=True)
class BeliefStateCodingCertificate:
    graph: ConfusionGraph
    model: HiddenLawModel
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    no_signal_entries: tuple[NoSignalPolicyEntry, ...]
    no_signal_value: Fraction
    observed_entries: tuple[ObservedPolicyEntry, ...]
    observed_value: Fraction
    perfect_entries: tuple[PerfectPolicyEntry, ...]
    perfect_value: Fraction
    path_oracles: tuple[HiddenPathOracleReceipt, ...]
    clairvoyant_expected_value: Fraction

    @property
    def candidates(self) -> tuple[RobustCodeCandidate, ...]:
        return self.enumeration.candidates

    @property
    def no_signal_regret(self) -> Fraction:
        return self.no_signal_value - self.clairvoyant_expected_value

    @property
    def observed_regret(self) -> Fraction:
        return self.observed_value - self.clairvoyant_expected_value

    @property
    def perfect_regret(self) -> Fraction:
        return self.perfect_value - self.clairvoyant_expected_value

    @property
    def information_value(self) -> Fraction:
        return self.no_signal_value - self.observed_value

    @property
    def perfect_state_increment(self) -> Fraction:
        return self.observed_value - self.perfect_value

    @property
    def future_foresight_value(self) -> Fraction:
        return self.perfect_value - self.clairvoyant_expected_value

    @property
    def information_telescope(self) -> Fraction:
        return (
            self.information_value
            + self.perfect_state_increment
            + self.future_foresight_value
        )

    @property
    def hierarchy_valid(self) -> bool:
        return (
            self.clairvoyant_expected_value
            <= self.perfect_value
            <= self.observed_value
            <= self.no_signal_value
        )

    @property
    def valid(self) -> bool:
        if (
            not self.model.valid
            or self.horizon < 1
            or self.switching_penalty < 0
            or not self.enumeration.valid
            or self.enumeration.graph != self.graph
            or self.enumeration.priors != self.model.source_laws
            or not self.candidates
            or not self.path_oracles
            or not self.hierarchy_valid
            or self.no_signal_regret < 0
            or self.observed_regret < 0
            or self.perfect_regret < 0
            or self.information_telescope != self.no_signal_regret
        ):
            return False

        no_signal_table = {
            (entry.period, entry.prior_belief, entry.previous_code): entry
            for entry in self.no_signal_entries
        }
        observed_table = {
            (entry.period, entry.prior_belief, entry.previous_code): entry
            for entry in self.observed_entries
        }
        perfect_table = {
            (entry.period, entry.hidden_state, entry.previous_code): entry
            for entry in self.perfect_entries
        }
        if (
            len(no_signal_table) != len(self.no_signal_entries)
            or len(observed_table) != len(self.observed_entries)
            or len(perfect_table) != len(self.perfect_entries)
        ):
            return False

        @lru_cache(maxsize=None)
        def no_signal(period: int, belief: Belief, previous_code: int) -> Fraction:
            if period == self.horizon:
                return Fraction(0)
            entry = no_signal_table.get((period, belief, previous_code))
            if entry is None:
                raise KeyError((period, belief, previous_code))
            next_belief = predict_belief(belief, self.model.transition)
            choices = tuple(
                (
                    _switch_cost(previous_code, code, self.switching_penalty)
                    + expected_candidate_cost(belief, candidate)
                    + no_signal(period + 1, next_belief, code),
                    code,
                )
                for code, candidate in enumerate(self.candidates)
            )
            value, code = min(
                choices,
                key=lambda item: (
                    item[0],
                    int(previous_code >= 0 and item[1] != previous_code),
                    item[1],
                ),
            )
            if (
                entry.value != value
                or entry.selected_code != code
                or entry.next_belief != next_belief
            ):
                raise AssertionError("no-signal Bellman entry mismatch")
            return value

        @lru_cache(maxsize=None)
        def observed(period: int, belief: Belief, previous_code: int) -> Fraction:
            if period == self.horizon:
                return Fraction(0)
            entry = observed_table.get((period, belief, previous_code))
            if entry is None:
                raise KeyError((period, belief, previous_code))
            expected_choices: list[SignalPolicyChoice] = []
            total = Fraction(0)
            for signal in range(self.model.observation.signal_count):
                probability = signal_probability(
                    belief,
                    self.model.observation,
                    signal,
                )
                if probability == 0:
                    continue
                posterior = posterior_belief(
                    belief,
                    self.model.observation,
                    signal,
                )
                next_belief = predict_belief(posterior, self.model.transition)
                choices = tuple(
                    (
                        _switch_cost(previous_code, code, self.switching_penalty)
                        + expected_candidate_cost(posterior, candidate)
                        + observed(period + 1, next_belief, code),
                        code,
                    )
                    for code, candidate in enumerate(self.candidates)
                )
                conditional, code = min(
                    choices,
                    key=lambda item: (
                        item[0],
                        int(previous_code >= 0 and item[1] != previous_code),
                        item[1],
                    ),
                )
                expected_choices.append(
                    SignalPolicyChoice(
                        signal,
                        probability,
                        posterior,
                        code,
                        next_belief,
                        conditional,
                    )
                )
                total += probability * conditional
            if entry.value != total or entry.signal_choices != tuple(expected_choices):
                raise AssertionError("observed-belief Bellman entry mismatch")
            return total

        @lru_cache(maxsize=None)
        def perfect(period: int, state: int, previous_code: int) -> Fraction:
            if period == self.horizon:
                return Fraction(0)
            entry = perfect_table.get((period, state, previous_code))
            if entry is None:
                raise KeyError((period, state, previous_code))
            choices = tuple(
                (
                    _switch_cost(previous_code, code, self.switching_penalty)
                    + candidate.scenario_costs[state]
                    + sum(
                        (
                            self.model.transition[state][next_state]
                            * perfect(period + 1, next_state, code)
                            for next_state in range(self.model.hidden_state_count)
                        ),
                        Fraction(0),
                    ),
                    code,
                )
                for code, candidate in enumerate(self.candidates)
            )
            value, code = min(
                choices,
                key=lambda item: (
                    item[0],
                    int(previous_code >= 0 and item[1] != previous_code),
                    item[1],
                ),
            )
            if entry.value != value or entry.selected_code != code:
                raise AssertionError("perfect-state Bellman entry mismatch")
            return value

        try:
            no_signal_value = no_signal(0, self.model.initial_belief, -1)
            observed_value = observed(0, self.model.initial_belief, -1)
            perfect_value = sum(
                (
                    self.model.initial_belief[state]
                    * perfect(0, state, -1)
                    for state in range(self.model.hidden_state_count)
                ),
                Fraction(0),
            )
        except (KeyError, AssertionError, ValueError):
            return False
        if (
            no_signal_value != self.no_signal_value
            or observed_value != self.observed_value
            or perfect_value != self.perfect_value
        ):
            return False

        expected_paths = _hidden_path_oracles(
            self.model,
            self.candidates,
            self.horizon,
            self.switching_penalty,
            max_paths=max(1, len(self.path_oracles)),
        )
        if expected_paths != self.path_oracles:
            return False
        expected_clairvoyant = sum(
            (
                receipt.probability * receipt.oracle_cost
                for receipt in self.path_oracles
            ),
            Fraction(0),
        )
        if self.clairvoyant_expected_value != expected_clairvoyant:
            return False
        if sum(
            (receipt.probability for receipt in self.path_oracles),
            Fraction(0),
        ) != 1:
            return False

        if self.model.observation_is_uninformative and (
            self.observed_value != self.no_signal_value
        ):
            return False
        if self.model.observation_is_identity and (
            self.observed_value != self.perfect_value
        ):
            return False
        return True


def _advance_oracle_frontier(
    frontier: tuple[Fraction, ...],
    hidden_state: int,
    candidates: Sequence[RobustCodeCandidate],
    switching_penalty: Fraction,
) -> tuple[Fraction, ...]:
    stage = tuple(
        candidate.scenario_costs[hidden_state]
        for candidate in candidates
    )
    if not frontier:
        return stage
    return tuple(
        stage[next_code]
        + min(
            frontier[previous_code]
            + _switch_cost(previous_code, next_code, switching_penalty)
            for previous_code in range(len(candidates))
        )
        for next_code in range(len(candidates))
    )


def _hidden_path_oracles(
    model: HiddenLawModel,
    candidates: Sequence[RobustCodeCandidate],
    horizon: int,
    switching_penalty: Fraction,
    *,
    max_paths: int,
) -> tuple[HiddenPathOracleReceipt, ...]:
    cap = int(max_paths)
    if cap < 1:
        raise ValueError("max_paths must be positive")
    receipts: list[HiddenPathOracleReceipt] = []
    for path in product(range(model.hidden_state_count), repeat=horizon):
        probability = model.initial_belief[path[0]]
        for previous, current in zip(path, path[1:]):
            probability *= model.transition[previous][current]
        if probability == 0:
            continue
        frontier: tuple[Fraction, ...] = tuple()
        for state in path:
            frontier = _advance_oracle_frontier(
                frontier,
                state,
                candidates,
                switching_penalty,
            )
        receipts.append(
            HiddenPathOracleReceipt(
                tuple(path),
                probability,
                min(frontier),
                frontier,
            )
        )
        if len(receipts) > cap:
            raise ValueError("positive-probability hidden path count exceeds cap")
    if not receipts:
        raise AssertionError("hidden Markov model produced no positive path")
    return tuple(receipts)


def exact_belief_state_prefix_coding(
    graph: ConfusionGraph,
    model: HiddenLawModel,
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
) -> BeliefStateCodingCertificate:
    """Solve exact no-signal, Bayesian-signal, perfect-state, and oracle costs."""

    if not model.valid:
        raise ValueError("hidden-law model must be valid")
    if graph.vertex_count != model.source_symbol_count:
        raise ValueError("graph and source-law alphabets differ")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    enumeration = enumerate_robust_code_candidates(
        graph,
        model.source_laws,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates

    no_signal_table: dict[tuple[int, Belief, int], NoSignalPolicyEntry] = {}

    @lru_cache(maxsize=None)
    def no_signal(period: int, belief: Belief, previous_code: int) -> Fraction:
        if period == periods:
            return Fraction(0)
        next_belief = predict_belief(belief, model.transition)
        choices = tuple(
            (
                _switch_cost(previous_code, code, penalty)
                + expected_candidate_cost(belief, candidate)
                + no_signal(period + 1, next_belief, code),
                code,
            )
            for code, candidate in enumerate(candidates)
        )
        value, code = min(
            choices,
            key=lambda item: (
                item[0],
                int(previous_code >= 0 and item[1] != previous_code),
                item[1],
            ),
        )
        no_signal_table[(period, belief, previous_code)] = NoSignalPolicyEntry(
            period,
            belief,
            previous_code,
            value,
            code,
            next_belief,
        )
        return value

    no_signal_value = no_signal(0, model.initial_belief, -1)

    observed_table: dict[tuple[int, Belief, int], ObservedPolicyEntry] = {}

    @lru_cache(maxsize=None)
    def observed(period: int, belief: Belief, previous_code: int) -> Fraction:
        if period == periods:
            return Fraction(0)
        signal_choices: list[SignalPolicyChoice] = []
        total = Fraction(0)
        for signal in range(model.observation.signal_count):
            probability = signal_probability(belief, model.observation, signal)
            if probability == 0:
                continue
            posterior = posterior_belief(belief, model.observation, signal)
            next_belief = predict_belief(posterior, model.transition)
            choices = tuple(
                (
                    _switch_cost(previous_code, code, penalty)
                    + expected_candidate_cost(posterior, candidate)
                    + observed(period + 1, next_belief, code),
                    code,
                )
                for code, candidate in enumerate(candidates)
            )
            conditional, code = min(
                choices,
                key=lambda item: (
                    item[0],
                    int(previous_code >= 0 and item[1] != previous_code),
                    item[1],
                ),
            )
            signal_choices.append(
                SignalPolicyChoice(
                    signal,
                    probability,
                    posterior,
                    code,
                    next_belief,
                    conditional,
                )
            )
            total += probability * conditional
        observed_table[(period, belief, previous_code)] = ObservedPolicyEntry(
            period,
            belief,
            previous_code,
            total,
            tuple(signal_choices),
        )
        return total

    observed_value = observed(0, model.initial_belief, -1)

    perfect_table: dict[tuple[int, int, int], PerfectPolicyEntry] = {}

    @lru_cache(maxsize=None)
    def perfect(period: int, state: int, previous_code: int) -> Fraction:
        if period == periods:
            return Fraction(0)
        choices = tuple(
            (
                _switch_cost(previous_code, code, penalty)
                + candidate.scenario_costs[state]
                + sum(
                    (
                        model.transition[state][next_state]
                        * perfect(period + 1, next_state, code)
                        for next_state in range(model.hidden_state_count)
                    ),
                    Fraction(0),
                ),
                code,
            )
            for code, candidate in enumerate(candidates)
        )
        value, code = min(
            choices,
            key=lambda item: (
                item[0],
                int(previous_code >= 0 and item[1] != previous_code),
                item[1],
            ),
        )
        perfect_table[(period, state, previous_code)] = PerfectPolicyEntry(
            period,
            state,
            previous_code,
            value,
            code,
        )
        return value

    perfect_value = sum(
        (
            model.initial_belief[state] * perfect(0, state, -1)
            for state in range(model.hidden_state_count)
        ),
        Fraction(0),
    )

    path_oracles = _hidden_path_oracles(
        model,
        candidates,
        periods,
        penalty,
        max_paths=max_hidden_paths,
    )
    clairvoyant = sum(
        (
            receipt.probability * receipt.oracle_cost
            for receipt in path_oracles
        ),
        Fraction(0),
    )
    result = BeliefStateCodingCertificate(
        graph,
        model,
        periods,
        penalty,
        enumeration,
        tuple(no_signal_table[key] for key in sorted(no_signal_table)),
        no_signal_value,
        tuple(observed_table[key] for key in sorted(observed_table)),
        observed_value,
        tuple(perfect_table[key] for key in sorted(perfect_table)),
        perfect_value,
        path_oracles,
        clairvoyant,
    )
    if not result.valid:
        raise AssertionError("belief-state coding certificate failed validation")
    return result
