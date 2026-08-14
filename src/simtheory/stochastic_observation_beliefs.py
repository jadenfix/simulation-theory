"""Exact finite Bayesian coding with stochastic law observations.

The deterministic coarsened-observation lane treats hidden law states through
worst-case information sets.  This module studies a different model: a finite
hidden Markov chain with an exact rational prior, exact rational transition
matrix, and exact rational stochastic observation kernel.  Expected one-shot
zero-error prefix length is minimized over a finite horizon.

The posterior belief is a sufficient controller state.  After observing the
current signal, the controller chooses a deterministic zero-error prefix code.
The stage cost is the belief-weighted expected length plus an optional switching
penalty.  The hidden law then transitions and a new signal is emitted.  Exact
Bayes updates and backward induction produce rational value, policy, and
observation-branch certificates.

A stochastic garbling of one observation kernel is also implemented.  A finer
signal cannot increase minimum expected cost: it can simulate the coarser signal
using independent source-irrelevant randomization, and finite expected-cost
belief control has a deterministic optimal policy.  The proof concerns the
declared probabilistic model; it is not a statement about statistical coverage
or about learning unknown kernels from data.

All models are finite and exact-rational, and every reachable-belief search is
bounded by explicit caps.  This is not robust set-membership control, partial
identification, continuous-state filtering, or evidence for simulation.  It
does not translate internal expected code lengths into parent-universe hardware,
energy, mass, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)


ExactInput = int | str | Fraction
Belief = tuple[Fraction, ...]


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be supplied as exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _validate_probability_row(
    values: Sequence[ExactInput],
    *,
    name: str,
    expected_length: int | None = None,
) -> tuple[Fraction, ...]:
    row = tuple(_fraction(value, name=name) for value in values)
    if not row or (expected_length is not None and len(row) != expected_length):
        raise ValueError(f"{name} row is empty or has inconsistent length")
    if any(value < 0 for value in row):
        raise ValueError(f"{name} probabilities must be nonnegative")
    if sum(row, Fraction(0)) != 1:
        raise ValueError(f"{name} probabilities must sum exactly to one")
    return row


def _dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _simplex_vertices(state_count: int) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(
            Fraction(1) if row == column else Fraction(0)
            for column in range(state_count)
        )
        for row in range(state_count)
    )


@dataclass(frozen=True)
class BayesianLawModel:
    """Finite hidden law states and a code-independent Markov transition."""

    laws: tuple[tuple[Fraction, ...], ...]
    transition: tuple[tuple[Fraction, ...], ...]

    @property
    def hidden_state_count(self) -> int:
        return len(self.laws)

    @property
    def source_symbol_count(self) -> int:
        return len(self.laws[0])

    @property
    def valid(self) -> bool:
        return (
            self.hidden_state_count >= 1
            and self.source_symbol_count >= 1
            and len(self.transition) == self.hidden_state_count
            and all(
                len(law) == self.source_symbol_count
                and all(value >= 0 for value in law)
                and sum(law, Fraction(0)) == 1
                for law in self.laws
            )
            and all(
                len(row) == self.hidden_state_count
                and all(value >= 0 for value in row)
                and sum(row, Fraction(0)) == 1
                for row in self.transition
            )
        )


def bayesian_law_model(
    laws: Sequence[Sequence[ExactInput]],
    transition: Sequence[Sequence[ExactInput]],
) -> BayesianLawModel:
    supplied_laws = tuple(tuple(row) for row in laws)
    if not supplied_laws:
        raise ValueError("at least one hidden law state is required")
    first = _validate_probability_row(
        supplied_laws[0],
        name="source law",
    )
    validated_laws = (first,) + tuple(
        _validate_probability_row(
            row,
            name="source law",
            expected_length=len(first),
        )
        for row in supplied_laws[1:]
    )
    supplied_transition = tuple(tuple(row) for row in transition)
    if len(supplied_transition) != len(validated_laws):
        raise ValueError("one transition row is required per hidden law state")
    validated_transition = tuple(
        _validate_probability_row(
            row,
            name="transition",
            expected_length=len(validated_laws),
        )
        for row in supplied_transition
    )
    result = BayesianLawModel(validated_laws, validated_transition)
    if not result.valid:
        raise AssertionError("Bayesian law model failed validation")
    return result


@dataclass(frozen=True)
class ObservationKernel:
    probabilities: tuple[tuple[Fraction, ...], ...]

    @property
    def hidden_state_count(self) -> int:
        return len(self.probabilities)

    @property
    def observation_count(self) -> int:
        return len(self.probabilities[0])

    @property
    def valid(self) -> bool:
        return (
            self.hidden_state_count >= 1
            and self.observation_count >= 1
            and all(
                len(row) == self.observation_count
                and all(value >= 0 for value in row)
                and sum(row, Fraction(0)) == 1
                for row in self.probabilities
            )
        )


def observation_kernel(
    probabilities: Sequence[Sequence[ExactInput]],
) -> ObservationKernel:
    supplied = tuple(tuple(row) for row in probabilities)
    if not supplied:
        raise ValueError("observation kernel requires at least one hidden state")
    first = _validate_probability_row(supplied[0], name="observation")
    rows = (first,) + tuple(
        _validate_probability_row(
            row,
            name="observation",
            expected_length=len(first),
        )
        for row in supplied[1:]
    )
    result = ObservationKernel(rows)
    if not result.valid:
        raise AssertionError("observation kernel failed validation")
    return result


def no_information_kernel(hidden_state_count: int) -> ObservationKernel:
    count = int(hidden_state_count)
    if count < 1:
        raise ValueError("hidden_state_count must be positive")
    return observation_kernel(tuple((1,) for _ in range(count)))


def full_information_kernel(hidden_state_count: int) -> ObservationKernel:
    count = int(hidden_state_count)
    if count < 1:
        raise ValueError("hidden_state_count must be positive")
    return observation_kernel(
        tuple(
            tuple(1 if row == column else 0 for column in range(count))
            for row in range(count)
        )
    )


def deterministic_partition_kernel(labels: Sequence[object]) -> ObservationKernel:
    supplied = tuple(labels)
    if not supplied:
        raise ValueError("deterministic observation partition cannot be empty")
    canonical: dict[object, int] = {}
    normalized: list[int] = []
    for label in supplied:
        try:
            if label not in canonical:
                canonical[label] = len(canonical)
            normalized.append(canonical[label])
        except TypeError as error:
            raise ValueError("deterministic observation labels must be hashable") from error
    return observation_kernel(
        tuple(
            tuple(
                1 if observation == normalized[state] else 0
                for observation in range(len(canonical))
            )
            for state in range(len(supplied))
        )
    )


@dataclass(frozen=True)
class ObservationGarblingCertificate:
    finer: ObservationKernel
    garbling: tuple[tuple[Fraction, ...], ...]
    coarser: ObservationKernel

    @property
    def valid(self) -> bool:
        return (
            self.finer.valid
            and self.coarser.valid
            and self.finer.hidden_state_count == self.coarser.hidden_state_count
            and len(self.garbling) == self.finer.observation_count
            and all(
                len(row) == self.coarser.observation_count
                and all(value >= 0 for value in row)
                and sum(row, Fraction(0)) == 1
                for row in self.garbling
            )
            and self.coarser.probabilities
            == tuple(
                tuple(
                    sum(
                        (
                            self.finer.probabilities[state][fine_observation]
                            * self.garbling[fine_observation][coarse_observation]
                            for fine_observation in range(self.finer.observation_count)
                        ),
                        Fraction(0),
                    )
                    for coarse_observation in range(self.coarser.observation_count)
                )
                for state in range(self.finer.hidden_state_count)
            )
        )


def garble_observation_kernel(
    finer: ObservationKernel,
    garbling: Sequence[Sequence[ExactInput]],
) -> ObservationGarblingCertificate:
    if not finer.valid:
        raise ValueError("finer observation kernel must be valid")
    supplied = tuple(tuple(row) for row in garbling)
    if len(supplied) != finer.observation_count:
        raise ValueError("one garbling row is required per fine observation")
    first = _validate_probability_row(supplied[0], name="garbling")
    rows = (first,) + tuple(
        _validate_probability_row(
            row,
            name="garbling",
            expected_length=len(first),
        )
        for row in supplied[1:]
    )
    coarser = observation_kernel(
        tuple(
            tuple(
                sum(
                    (
                        finer.probabilities[state][fine_observation]
                        * rows[fine_observation][coarse_observation]
                        for fine_observation in range(finer.observation_count)
                    ),
                    Fraction(0),
                )
                for coarse_observation in range(len(first))
            )
            for state in range(finer.hidden_state_count)
        )
    )
    result = ObservationGarblingCertificate(finer, rows, coarser)
    if not result.valid:
        raise AssertionError("observation garbling certificate failed validation")
    return result


def _validate_belief(
    values: Sequence[ExactInput | Fraction],
    hidden_state_count: int,
) -> Belief:
    belief = tuple(_fraction(value, name="belief probability") for value in values)
    if len(belief) != hidden_state_count:
        raise ValueError("belief dimension does not match hidden-state count")
    if any(value < 0 for value in belief):
        raise ValueError("belief probabilities must be nonnegative")
    if sum(belief, Fraction(0)) != 1:
        raise ValueError("belief probabilities must sum exactly to one")
    return belief


@dataclass(frozen=True)
class BeliefObservationBranch:
    observation: int
    probability: Fraction
    posterior: Belief

    @property
    def valid(self) -> bool:
        return (
            self.observation >= 0
            and self.probability > 0
            and self.posterior
            and all(value >= 0 for value in self.posterior)
            and sum(self.posterior, Fraction(0)) == 1
        )


def _observe_belief(
    predictive_belief: Belief,
    kernel: ObservationKernel,
) -> tuple[BeliefObservationBranch, ...]:
    if len(predictive_belief) != kernel.hidden_state_count:
        raise ValueError("belief and observation-kernel dimensions differ")
    branches: list[BeliefObservationBranch] = []
    for observation in range(kernel.observation_count):
        probability = sum(
            (
                predictive_belief[state]
                * kernel.probabilities[state][observation]
                for state in range(kernel.hidden_state_count)
            ),
            Fraction(0),
        )
        if probability == 0:
            continue
        posterior = tuple(
            predictive_belief[state]
            * kernel.probabilities[state][observation]
            / probability
            for state in range(kernel.hidden_state_count)
        )
        branch = BeliefObservationBranch(observation, probability, posterior)
        if not branch.valid:
            raise AssertionError("Bayes observation branch failed validation")
        branches.append(branch)
    if sum((branch.probability for branch in branches), Fraction(0)) != 1:
        raise AssertionError("positive-probability observations do not sum to one")
    return tuple(branches)


def _predict_belief(
    belief: Belief,
    model: BayesianLawModel,
) -> Belief:
    if len(belief) != model.hidden_state_count:
        raise ValueError("belief and model dimensions differ")
    predicted = tuple(
        sum(
            (
                belief[current] * model.transition[current][next_state]
                for current in range(model.hidden_state_count)
            ),
            Fraction(0),
        )
        for next_state in range(model.hidden_state_count)
    )
    if sum(predicted, Fraction(0)) != 1 or any(value < 0 for value in predicted):
        raise AssertionError("Markov prediction left the probability simplex")
    return predicted


def initial_observation_branches(
    initial_prior: Sequence[ExactInput],
    kernel: ObservationKernel,
) -> tuple[BeliefObservationBranch, ...]:
    prior = _validate_belief(initial_prior, kernel.hidden_state_count)
    return _observe_belief(prior, kernel)


def next_observation_branches(
    belief: Sequence[ExactInput | Fraction],
    model: BayesianLawModel,
    kernel: ObservationKernel,
) -> tuple[BeliefObservationBranch, ...]:
    posterior = _validate_belief(belief, model.hidden_state_count)
    if kernel.hidden_state_count != model.hidden_state_count:
        raise ValueError("model and observation-kernel hidden-state counts differ")
    return _observe_belief(_predict_belief(posterior, model), kernel)


def _enumerate_candidates(
    graph: ConfusionGraph,
    *,
    max_vertices: int,
    max_partitions: int,
    max_candidates: int,
    max_prefix_assignments: int,
    max_prefix_shapes: int,
    max_dominance_pairs: int,
) -> RobustCandidateEnumeration:
    return enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )


def _hidden_state_code_costs(
    model: BayesianLawModel,
    candidate: RobustCodeCandidate,
) -> tuple[Fraction, ...]:
    return tuple(
        _dot(law, candidate.scenario_costs)
        for law in model.laws
    )


@dataclass(frozen=True)
class BeliefContinuation:
    observation: int
    probability: Fraction
    posterior: Belief
    continuation_value: Fraction


@dataclass(frozen=True)
class BeliefPolicyNode:
    period: int
    belief: Belief
    previous_code: int
    value: Fraction
    selected_code: int
    stage_cost: Fraction
    continuations: tuple[BeliefContinuation, ...]

    @property
    def valid_shape(self) -> bool:
        return (
            self.period >= 0
            and self.belief
            and all(value >= 0 for value in self.belief)
            and sum(self.belief, Fraction(0)) == 1
            and self.value >= 0
            and self.stage_cost >= 0
            and tuple(
                sorted(self.continuations, key=lambda branch: branch.observation)
            )
            == self.continuations
            and len({branch.observation for branch in self.continuations})
            == len(self.continuations)
            and all(
                branch.probability > 0
                and branch.continuation_value >= 0
                and sum(branch.posterior, Fraction(0)) == 1
                for branch in self.continuations
            )
        )


@dataclass(frozen=True)
class InitialBeliefChoice:
    observation: int
    probability: Fraction
    posterior: Belief
    node_value: Fraction


@dataclass(frozen=True)
class BayesianCodingGameCertificate:
    graph: ConfusionGraph
    model: BayesianLawModel
    kernel: ObservationKernel
    initial_prior: Belief
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    nodes: tuple[BeliefPolicyNode, ...]
    initial_choices: tuple[InitialBeliefChoice, ...]
    initial_value: Fraction
    nodes_built: int
    observation_branches_built: int
    max_belief_nodes: int
    max_observation_branches: int

    @property
    def valid(self) -> bool:
        candidates = self.enumeration.candidates
        code_count = len(candidates)
        sentinel = code_count
        if (
            not self.model.valid
            or not self.kernel.valid
            or self.kernel.hidden_state_count != self.model.hidden_state_count
            or self.graph.vertex_count != self.model.source_symbol_count
            or len(self.initial_prior) != self.model.hidden_state_count
            or sum(self.initial_prior, Fraction(0)) != 1
            or any(value < 0 for value in self.initial_prior)
            or self.horizon < 1
            or not candidates
            or not self.nodes
            or any(not node.valid_shape for node in self.nodes)
            or len({(node.period, node.belief, node.previous_code) for node in self.nodes})
            != len(self.nodes)
            or self.nodes_built != len(self.nodes)
            or self.nodes_built > self.max_belief_nodes
            or self.observation_branches_built > self.max_observation_branches
        ):
            return False

        node_map = {
            (node.period, node.belief, node.previous_code): node
            for node in self.nodes
        }
        hidden_costs = tuple(
            _hidden_state_code_costs(self.model, candidate)
            for candidate in candidates
        )
        for node in self.nodes:
            if not 0 <= node.selected_code < code_count:
                return False
            switch = (
                node.previous_code != sentinel
                and node.previous_code != node.selected_code
            )
            expected_stage = _dot(
                node.belief,
                hidden_costs[node.selected_code],
            ) + self.switching_penalty * int(switch)
            if node.stage_cost != expected_stage:
                return False
            if node.period == self.horizon - 1:
                if node.continuations or node.value != node.stage_cost:
                    return False
            else:
                expected_branches = next_observation_branches(
                    node.belief,
                    self.model,
                    self.kernel,
                )
                if tuple(
                    (branch.observation, branch.probability, branch.posterior)
                    for branch in node.continuations
                ) != tuple(
                    (branch.observation, branch.probability, branch.posterior)
                    for branch in expected_branches
                ):
                    return False
                continuation = Fraction(0)
                for branch in node.continuations:
                    next_node = node_map.get(
                        (
                            node.period + 1,
                            branch.posterior,
                            node.selected_code,
                        )
                    )
                    if (
                        next_node is None
                        or branch.continuation_value != next_node.value
                    ):
                        return False
                    continuation += branch.probability * branch.continuation_value
                if node.value != node.stage_cost + continuation:
                    return False

            alternative_values: list[Fraction] = []
            for code_index, candidate_costs in enumerate(hidden_costs):
                alternative_switch = (
                    node.previous_code != sentinel
                    and node.previous_code != code_index
                )
                value = _dot(node.belief, candidate_costs) + self.switching_penalty * int(
                    alternative_switch
                )
                if node.period < self.horizon - 1:
                    for branch in next_observation_branches(
                        node.belief,
                        self.model,
                        self.kernel,
                    ):
                        next_node = node_map.get(
                            (node.period + 1, branch.posterior, code_index)
                        )
                        if next_node is None:
                            return False
                        value += branch.probability * next_node.value
                alternative_values.append(value)
            if node.value != min(alternative_values):
                return False

        expected_initial = initial_observation_branches(
            self.initial_prior,
            self.kernel,
        )
        if tuple(
            (choice.observation, choice.probability, choice.posterior)
            for choice in self.initial_choices
        ) != tuple(
            (branch.observation, branch.probability, branch.posterior)
            for branch in expected_initial
        ):
            return False
        initial_value = Fraction(0)
        for choice in self.initial_choices:
            node = node_map.get((0, choice.posterior, sentinel))
            if node is None or node.value != choice.node_value:
                return False
            initial_value += choice.probability * choice.node_value
        return initial_value == self.initial_value


def exact_bayesian_coding_game(
    graph: ConfusionGraph,
    model: BayesianLawModel,
    kernel: ObservationKernel,
    initial_prior: Sequence[ExactInput],
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_belief_nodes: int = 100_000,
    max_observation_branches: int = 1_000_000,
) -> BayesianCodingGameCertificate:
    if (
        not model.valid
        or not kernel.valid
        or kernel.hidden_state_count != model.hidden_state_count
        or graph.vertex_count != model.source_symbol_count
    ):
        raise ValueError("graph, Bayesian law model, and observation kernel disagree")
    prior = _validate_belief(initial_prior, model.hidden_state_count)
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")
    if (
        int(max_belief_nodes) != max_belief_nodes
        or int(max_belief_nodes) < 1
        or int(max_observation_branches) != max_observation_branches
        or int(max_observation_branches) < 1
    ):
        raise ValueError("Bayesian belief search caps must be positive integers")

    enumeration = _enumerate_candidates(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    hidden_costs = tuple(
        _hidden_state_code_costs(model, candidate) for candidate in candidates
    )
    code_count = len(candidates)
    sentinel = code_count
    cache: dict[tuple[int, Belief, int], BeliefPolicyNode] = {}
    branches_built = 0

    def solve(period: int, belief: Belief, previous_code: int) -> BeliefPolicyNode:
        nonlocal branches_built
        key = (period, belief, previous_code)
        if key in cache:
            return cache[key]
        if len(cache) >= max_belief_nodes:
            raise ValueError("reachable Bayesian belief nodes exceed configured cap")
        next_branches = (
            ()
            if period == periods - 1
            else next_observation_branches(belief, model, kernel)
        )
        branches_built += len(next_branches)
        if branches_built > max_observation_branches:
            raise ValueError("Bayesian observation branches exceed configured cap")

        options: list[
            tuple[
                Fraction,
                int,
                Fraction,
                tuple[BeliefContinuation, ...],
            ]
        ] = []
        for code_index, costs in enumerate(hidden_costs):
            switch = previous_code != sentinel and previous_code != code_index
            stage = _dot(belief, costs) + penalty * int(switch)
            continuations: list[BeliefContinuation] = []
            value = stage
            for branch in next_branches:
                next_node = solve(period + 1, branch.posterior, code_index)
                continuations.append(
                    BeliefContinuation(
                        branch.observation,
                        branch.probability,
                        branch.posterior,
                        next_node.value,
                    )
                )
                value += branch.probability * next_node.value
            options.append((value, code_index, stage, tuple(continuations)))

        best_value = min(option[0] for option in options)
        best_options = tuple(option for option in options if option[0] == best_value)
        selected = min(
            best_options,
            key=lambda option: (
                previous_code != sentinel and previous_code != option[1],
                candidates[option[1]].scenario_costs,
                option[1],
            ),
        )
        node = BeliefPolicyNode(
            period,
            belief,
            previous_code,
            selected[0],
            selected[1],
            selected[2],
            selected[3],
        )
        if not node.valid_shape:
            raise AssertionError("Bayesian policy node failed validation")
        cache[key] = node
        return node

    initial_branches = initial_observation_branches(prior, kernel)
    initial_choices: list[InitialBeliefChoice] = []
    initial_value = Fraction(0)
    for branch in initial_branches:
        node = solve(0, branch.posterior, sentinel)
        initial_choices.append(
            InitialBeliefChoice(
                branch.observation,
                branch.probability,
                branch.posterior,
                node.value,
            )
        )
        initial_value += branch.probability * node.value

    result = BayesianCodingGameCertificate(
        graph,
        model,
        kernel,
        prior,
        periods,
        penalty,
        enumeration,
        tuple(
            sorted(
                cache.values(),
                key=lambda node: (node.period, node.belief, node.previous_code),
            )
        ),
        tuple(initial_choices),
        initial_value,
        len(cache),
        branches_built,
        int(max_belief_nodes),
        int(max_observation_branches),
    )
    if not result.valid:
        raise AssertionError("Bayesian coding game certificate failed validation")
    return result


@dataclass(frozen=True)
class BlackwellObservationComparison:
    garbling: ObservationGarblingCertificate
    finer_game: BayesianCodingGameCertificate
    coarser_game: BayesianCodingGameCertificate

    @property
    def information_gain(self) -> Fraction:
        return self.coarser_game.initial_value - self.finer_game.initial_value

    @property
    def valid(self) -> bool:
        return (
            self.garbling.valid
            and self.finer_game.valid
            and self.coarser_game.valid
            and self.finer_game.kernel == self.garbling.finer
            and self.coarser_game.kernel == self.garbling.coarser
            and self.finer_game.graph == self.coarser_game.graph
            and self.finer_game.model == self.coarser_game.model
            and self.finer_game.initial_prior == self.coarser_game.initial_prior
            and self.finer_game.horizon == self.coarser_game.horizon
            and self.finer_game.switching_penalty
            == self.coarser_game.switching_penalty
            and self.information_gain >= 0
        )


def exact_blackwell_observation_value(
    graph: ConfusionGraph,
    model: BayesianLawModel,
    initial_prior: Sequence[ExactInput],
    horizon: int,
    garbling: ObservationGarblingCertificate,
    **kwargs: object,
) -> BlackwellObservationComparison:
    if not garbling.valid:
        raise ValueError("garbling certificate must be valid")
    finer = exact_bayesian_coding_game(
        graph,
        model,
        garbling.finer,
        initial_prior,
        horizon,
        **kwargs,
    )
    coarser = exact_bayesian_coding_game(
        graph,
        model,
        garbling.coarser,
        initial_prior,
        horizon,
        **kwargs,
    )
    result = BlackwellObservationComparison(garbling, finer, coarser)
    if not result.valid:
        raise AssertionError("Blackwell observation comparison failed validation")
    return result
