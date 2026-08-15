"""Exact finite coding under fixed probabilistic model ambiguity.

A Bayesian belief game assumes one transition/observation model.  This module
keeps a finite family of complete rational hidden-Markov source models and lets
nature choose one model once, before observations are generated.  The selected
model remains fixed for the full horizon.

The controller observes public signals but not the selected model.  A public
history induces, for every still possible model, a model-conditional posterior
belief.  Exact deterministic policies are represented by Pareto frontiers of
expected continuation-cost vectors indexed by the fixed model scenarios.
Continuation choices are shared across models that can emit the same public
observation, while each vector coordinate averages using that model's own
observation probabilities.

A separate scalar "rectangular" recursion is provided as a relaxation.  It
remaximizes over the active model set after every public observation and can
therefore splice together different models across time.  Its value is an upper
bound on the fixed-model game and may be strictly larger.

All probabilities and costs are exact rational.  Model, belief, continuation,
frontier, and dominance searches are bounded by explicit caps.  This is a
finite robust decision theorem, not parameter estimation, not Bayesian model
averaging, not continuous ambiguity, and not evidence for simulation or a
parent-substrate resource claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)
from .stochastic_observation_beliefs import (
    BayesianLawModel,
    Belief,
    ObservationKernel,
    _predict_belief,
    _validate_belief,
    _observe_belief,
)


ExactInput = int | str | Fraction


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be supplied as exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


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
class FixedModelScenario:
    name: str
    model: BayesianLawModel
    kernel: ObservationKernel
    initial_prior: Belief

    @property
    def valid(self) -> bool:
        return (
            bool(self.name)
            and self.model.valid
            and self.kernel.valid
            and self.kernel.hidden_state_count == self.model.hidden_state_count
            and len(self.initial_prior) == self.model.hidden_state_count
            and all(value >= 0 for value in self.initial_prior)
            and sum(self.initial_prior, Fraction(0)) == 1
        )


def fixed_model_scenario(
    name: str,
    model: BayesianLawModel,
    kernel: ObservationKernel,
    initial_prior: Sequence[ExactInput],
) -> FixedModelScenario:
    if not model.valid or not kernel.valid:
        raise ValueError("scenario model and observation kernel must be valid")
    if kernel.hidden_state_count != model.hidden_state_count:
        raise ValueError("scenario model and observation kernel dimensions differ")
    scenario = FixedModelScenario(
        str(name),
        model,
        kernel,
        _validate_belief(initial_prior, model.hidden_state_count),
    )
    if not scenario.valid:
        raise ValueError("invalid fixed-model scenario")
    return scenario


@dataclass(frozen=True)
class FixedModelFamily:
    scenarios: tuple[FixedModelScenario, ...]

    @property
    def model_count(self) -> int:
        return len(self.scenarios)

    @property
    def source_symbol_count(self) -> int:
        return self.scenarios[0].model.source_symbol_count

    @property
    def observation_count(self) -> int:
        return self.scenarios[0].kernel.observation_count

    @property
    def valid(self) -> bool:
        return (
            self.model_count >= 1
            and len({scenario.name for scenario in self.scenarios})
            == self.model_count
            and all(scenario.valid for scenario in self.scenarios)
            and all(
                scenario.model.source_symbol_count == self.source_symbol_count
                and scenario.kernel.observation_count == self.observation_count
                for scenario in self.scenarios
            )
        )


def fixed_model_family(
    scenarios: Sequence[FixedModelScenario],
) -> FixedModelFamily:
    result = FixedModelFamily(tuple(scenarios))
    if not result.valid:
        raise ValueError(
            "model family requires unique names and common source/observation alphabets"
        )
    return result


@dataclass(frozen=True)
class MultiModelBeliefState:
    model_indices: tuple[int, ...]
    beliefs: tuple[Belief, ...]

    @property
    def valid(self) -> bool:
        return (
            self.model_indices
            and tuple(sorted(set(self.model_indices))) == self.model_indices
            and len(self.model_indices) == len(self.beliefs)
            and all(
                belief
                and all(value >= 0 for value in belief)
                and sum(belief, Fraction(0)) == 1
                for belief in self.beliefs
            )
        )

    def belief_for_model(self, model_index: int) -> Belief:
        try:
            position = self.model_indices.index(model_index)
        except ValueError as error:
            raise KeyError("model is inactive in this public history") from error
        return self.beliefs[position]


@dataclass(frozen=True)
class MultiModelObservationBranch:
    observation: int
    current_model_indices: tuple[int, ...]
    probabilities: tuple[Fraction, ...]
    next_state: MultiModelBeliefState

    @property
    def valid(self) -> bool:
        return (
            self.observation >= 0
            and self.current_model_indices
            and len(self.current_model_indices) == len(self.probabilities)
            and all(value >= 0 for value in self.probabilities)
            and any(value > 0 for value in self.probabilities)
            and self.next_state.valid
            and self.next_state.model_indices
            == tuple(
                model
                for model, probability in zip(
                    self.current_model_indices,
                    self.probabilities,
                )
                if probability > 0
            )
        )

    def probability_for_model(self, model_index: int) -> Fraction:
        try:
            position = self.current_model_indices.index(model_index)
        except ValueError as error:
            raise KeyError("model is absent from branch source state") from error
        return self.probabilities[position]


def _multi_model_observation_branches(
    family: FixedModelFamily,
    state: MultiModelBeliefState | None,
    *,
    initial: bool,
) -> tuple[MultiModelObservationBranch, ...]:
    if initial:
        current_models = tuple(range(family.model_count))
        current_beliefs = tuple(
            scenario.initial_prior for scenario in family.scenarios
        )
    else:
        if state is None or not state.valid:
            raise ValueError("noninitial branch construction requires a valid state")
        current_models = state.model_indices
        current_beliefs = state.beliefs

    per_model: dict[int, dict[int, tuple[Fraction, Belief]]] = {}
    for model_index, belief in zip(current_models, current_beliefs):
        scenario = family.scenarios[model_index]
        predictive = belief if initial else _predict_belief(belief, scenario.model)
        branches = _observe_belief(predictive, scenario.kernel)
        per_model[model_index] = {
            branch.observation: (branch.probability, branch.posterior)
            for branch in branches
        }

    observations = tuple(
        sorted(
            {
                observation
                for mapping in per_model.values()
                for observation in mapping
            }
        )
    )
    results: list[MultiModelObservationBranch] = []
    for observation in observations:
        probabilities = tuple(
            per_model[model_index].get(
                observation,
                (Fraction(0), ()),
            )[0]
            for model_index in current_models
        )
        next_models = tuple(
            model_index
            for model_index, probability in zip(current_models, probabilities)
            if probability > 0
        )
        next_beliefs = tuple(
            per_model[model_index][observation][1]
            for model_index in next_models
        )
        branch = MultiModelObservationBranch(
            observation,
            current_models,
            probabilities,
            MultiModelBeliefState(next_models, next_beliefs),
        )
        if not branch.valid:
            raise AssertionError("multi-model observation branch failed validation")
        results.append(branch)
    return tuple(results)


def initial_model_observation_branches(
    family: FixedModelFamily,
) -> tuple[MultiModelObservationBranch, ...]:
    if not family.valid:
        raise ValueError("model family must be valid")
    return _multi_model_observation_branches(family, None, initial=True)


def next_model_observation_branches(
    family: FixedModelFamily,
    state: MultiModelBeliefState,
) -> tuple[MultiModelObservationBranch, ...]:
    if not family.valid:
        raise ValueError("model family must be valid")
    return _multi_model_observation_branches(family, state, initial=False)


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


def _scenario_stage_cost(
    scenario: FixedModelScenario,
    belief: Belief,
    candidate: RobustCodeCandidate,
) -> Fraction:
    hidden_state_costs = tuple(
        _dot(source_law, candidate.scenario_costs)
        for source_law in scenario.model.laws
    )
    return _dot(belief, hidden_state_costs)


def _cost_for_model(
    model_indices: Sequence[int],
    costs: Sequence[Fraction],
    model_index: int,
) -> Fraction:
    try:
        return costs[tuple(model_indices).index(model_index)]
    except ValueError as error:
        raise AssertionError("model is absent from its positive-probability branch") from error


@dataclass(frozen=True)
class ModelContinuationChoice:
    observation: int
    probabilities: tuple[Fraction, ...]
    next_state: MultiModelBeliefState
    next_costs: tuple[Fraction, ...]


@dataclass(frozen=True)
class ModelPolicyVectorEntry:
    period: int
    state: MultiModelBeliefState
    previous_code: int
    costs: tuple[Fraction, ...]
    selected_code: int
    continuations: tuple[ModelContinuationChoice, ...]

    @property
    def worst_value(self) -> Fraction:
        return max(self.costs)

    @property
    def valid_shape(self) -> bool:
        return (
            self.period >= 0
            and self.state.valid
            and len(self.costs) == len(self.state.model_indices)
            and all(value >= 0 for value in self.costs)
            and tuple(
                sorted(self.continuations, key=lambda item: item.observation)
            )
            == self.continuations
            and len({item.observation for item in self.continuations})
            == len(self.continuations)
        )


@dataclass(frozen=True)
class ModelFrontierRecord:
    period: int
    state: MultiModelBeliefState
    previous_code: int
    entries: tuple[ModelPolicyVectorEntry, ...]
    raw_count: int
    distinct_count: int
    dominated_count: int
    combinations_examined: int

    @property
    def valid_shape(self) -> bool:
        return (
            self.entries
            and all(
                entry.valid_shape
                and entry.period == self.period
                and entry.state == self.state
                and entry.previous_code == self.previous_code
                for entry in self.entries
            )
            and len({entry.costs for entry in self.entries}) == len(self.entries)
            and self.raw_count >= self.distinct_count
            and self.distinct_count == len(self.entries) + self.dominated_count
            and not any(
                _dominates(left.costs, right.costs)
                for left_index, left in enumerate(self.entries)
                for right_index, right in enumerate(self.entries)
                if left_index != right_index
            )
        )


def _dominates(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> bool:
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def _entry_tie_key(
    entry: ModelPolicyVectorEntry,
    candidates: Sequence[RobustCodeCandidate],
    sentinel: int,
) -> tuple[object, ...]:
    return (
        entry.previous_code != sentinel
        and entry.previous_code != entry.selected_code,
        candidates[entry.selected_code].scenario_costs,
        entry.selected_code,
        tuple(
            (
                continuation.observation,
                continuation.next_state.model_indices,
                continuation.next_state.beliefs,
                continuation.next_costs,
            )
            for continuation in entry.continuations
        ),
    )


def _prune_entries(
    entries: Sequence[ModelPolicyVectorEntry],
    candidates: Sequence[RobustCodeCandidate],
    sentinel: int,
    *,
    max_frontier_entries: int,
    max_dominance_pairs: int,
) -> tuple[tuple[ModelPolicyVectorEntry, ...], int, int]:
    by_costs: dict[tuple[Fraction, ...], ModelPolicyVectorEntry] = {}
    for entry in entries:
        incumbent = by_costs.get(entry.costs)
        if incumbent is None or _entry_tie_key(
            entry,
            candidates,
            sentinel,
        ) < _entry_tie_key(incumbent, candidates, sentinel):
            by_costs[entry.costs] = entry
    distinct = tuple(by_costs.values())
    if len(distinct) * max(0, len(distinct) - 1) > max_dominance_pairs:
        raise ValueError("model-frontier dominance search exceeds configured cap")
    retained = tuple(
        entry
        for entry in distinct
        if not any(
            _dominates(other.costs, entry.costs)
            for other in distinct
            if other is not entry
        )
    )
    ordered = tuple(
        sorted(
            retained,
            key=lambda entry: (
                entry.costs,
                _entry_tie_key(entry, candidates, sentinel),
            ),
        )
    )
    if len(ordered) > max_frontier_entries:
        raise ValueError("model-policy frontier exceeds configured cap")
    return ordered, len(distinct), len(distinct) - len(ordered)


@dataclass(frozen=True)
class InitialModelPolicyVector:
    costs: tuple[Fraction, ...]
    continuations: tuple[ModelContinuationChoice, ...]

    @property
    def worst_value(self) -> Fraction:
        return max(self.costs)


@dataclass(frozen=True)
class FixedModelAmbiguityCertificate:
    graph: ConfusionGraph
    family: FixedModelFamily
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    frontiers: tuple[ModelFrontierRecord, ...]
    initial_entries: tuple[InitialModelPolicyVector, ...]
    selected_initial_costs: tuple[Fraction, ...]
    fixed_model_value: Fraction
    rectangular_value: Fraction
    frontier_nodes_built: int
    policy_combinations_examined: int
    max_frontier_nodes: int
    max_policy_combinations: int
    max_frontier_entries: int

    @property
    def model_consistency_gap(self) -> Fraction:
        return self.rectangular_value - self.fixed_model_value

    @property
    def valid(self) -> bool:
        return (
            self.family.valid
            and self.graph.vertex_count == self.family.source_symbol_count
            and self.horizon >= 1
            and self.enumeration.candidates
            and self.frontiers
            and all(record.valid_shape for record in self.frontiers)
            and len(
                {
                    (record.period, record.state, record.previous_code)
                    for record in self.frontiers
                }
            )
            == len(self.frontiers)
            and self.initial_entries
            and self.selected_initial_costs
            in {entry.costs for entry in self.initial_entries}
            and self.fixed_model_value == max(self.selected_initial_costs)
            and self.fixed_model_value
            == min(entry.worst_value for entry in self.initial_entries)
            and self.rectangular_value >= self.fixed_model_value
            and self.frontier_nodes_built == len(self.frontiers)
            and self.frontier_nodes_built <= self.max_frontier_nodes
            and self.policy_combinations_examined <= self.max_policy_combinations
            and all(
                len(record.entries) <= self.max_frontier_entries
                for record in self.frontiers
            )
        )


def exact_fixed_model_ambiguity_game(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_code_dominance_pairs: int = 4_000_000,
    max_frontier_nodes: int = 100_000,
    max_policy_combinations: int = 2_000_000,
    max_frontier_entries: int = 100_000,
    max_frontier_dominance_pairs: int = 4_000_000,
) -> FixedModelAmbiguityCertificate:
    if not family.valid or graph.vertex_count != family.source_symbol_count:
        raise ValueError("graph and fixed-model family disagree")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    enumeration = _enumerate_candidates(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_code_dominance_pairs,
    )
    candidates = enumeration.candidates
    code_count = len(candidates)
    sentinel = code_count
    cache: dict[
        tuple[int, MultiModelBeliefState, int],
        ModelFrontierRecord,
    ] = {}
    combinations_examined = 0

    def build_frontier(
        period: int,
        state: MultiModelBeliefState,
        previous_code: int,
    ) -> ModelFrontierRecord:
        nonlocal combinations_examined
        key = (period, state, previous_code)
        if key in cache:
            return cache[key]
        if len(cache) >= max_frontier_nodes:
            raise ValueError("fixed-model frontier node count exceeds configured cap")
        raw: list[ModelPolicyVectorEntry] = []
        local_combinations = 0

        if period == periods - 1:
            for code_index, candidate in enumerate(candidates):
                switch = previous_code != sentinel and previous_code != code_index
                costs = tuple(
                    _scenario_stage_cost(
                        family.scenarios[model_index],
                        belief,
                        candidate,
                    )
                    + penalty * int(switch)
                    for model_index, belief in zip(
                        state.model_indices,
                        state.beliefs,
                    )
                )
                raw.append(
                    ModelPolicyVectorEntry(
                        period,
                        state,
                        previous_code,
                        costs,
                        code_index,
                        (),
                    )
                )
        else:
            branches = next_model_observation_branches(family, state)
            for code_index, candidate in enumerate(candidates):
                records = tuple(
                    build_frontier(period + 1, branch.next_state, code_index)
                    for branch in branches
                )
                combination_count = prod(len(record.entries) for record in records)
                if combinations_examined + combination_count > max_policy_combinations:
                    raise ValueError(
                        "fixed-model continuation combinations exceed configured cap"
                    )
                for selected_entries in product(
                    *(record.entries for record in records)
                ):
                    combinations_examined += 1
                    local_combinations += 1
                    switch = previous_code != sentinel and previous_code != code_index
                    costs: list[Fraction] = []
                    for model_index, belief in zip(
                        state.model_indices,
                        state.beliefs,
                    ):
                        value = _scenario_stage_cost(
                            family.scenarios[model_index],
                            belief,
                            candidate,
                        ) + penalty * int(switch)
                        for branch, entry in zip(branches, selected_entries):
                            probability = branch.probability_for_model(model_index)
                            if probability == 0:
                                continue
                            value += probability * _cost_for_model(
                                entry.state.model_indices,
                                entry.costs,
                                model_index,
                            )
                        costs.append(value)
                    raw.append(
                        ModelPolicyVectorEntry(
                            period,
                            state,
                            previous_code,
                            tuple(costs),
                            code_index,
                            tuple(
                                ModelContinuationChoice(
                                    branch.observation,
                                    branch.probabilities,
                                    branch.next_state,
                                    entry.costs,
                                )
                                for branch, entry in zip(branches, selected_entries)
                            ),
                        )
                    )

        entries, distinct, dominated = _prune_entries(
            raw,
            candidates,
            sentinel,
            max_frontier_entries=max_frontier_entries,
            max_dominance_pairs=max_frontier_dominance_pairs,
        )
        record = ModelFrontierRecord(
            period,
            state,
            previous_code,
            entries,
            len(raw),
            distinct,
            dominated,
            local_combinations,
        )
        if not record.valid_shape:
            raise AssertionError("fixed-model frontier record failed validation")
        cache[key] = record
        return record

    initial_branches = initial_model_observation_branches(family)
    initial_raw: list[InitialModelPolicyVector] = []
    initial_records = tuple(
        build_frontier(0, branch.next_state, sentinel)
        for branch in initial_branches
    )
    initial_combination_count = prod(
        len(record.entries) for record in initial_records
    )
    if combinations_examined + initial_combination_count > max_policy_combinations:
        raise ValueError("initial model-policy combinations exceed configured cap")
    for selected_entries in product(
        *(record.entries for record in initial_records)
    ):
        combinations_examined += 1
        costs: list[Fraction] = []
        for model_index in range(family.model_count):
            value = Fraction(0)
            for branch, entry in zip(initial_branches, selected_entries):
                probability = branch.probability_for_model(model_index)
                if probability == 0:
                    continue
                value += probability * _cost_for_model(
                    entry.state.model_indices,
                    entry.costs,
                    model_index,
                )
            costs.append(value)
        initial_raw.append(
            InitialModelPolicyVector(
                tuple(costs),
                tuple(
                    ModelContinuationChoice(
                        branch.observation,
                        branch.probabilities,
                        branch.next_state,
                        entry.costs,
                    )
                    for branch, entry in zip(initial_branches, selected_entries)
                ),
            )
        )

    by_costs: dict[tuple[Fraction, ...], InitialModelPolicyVector] = {}
    for entry in initial_raw:
        by_costs.setdefault(entry.costs, entry)
    distinct_initial = tuple(by_costs.values())
    if len(distinct_initial) * max(0, len(distinct_initial) - 1) > max_frontier_dominance_pairs:
        raise ValueError("initial model-frontier dominance search exceeds configured cap")
    initial_entries = tuple(
        sorted(
            (
                entry
                for entry in distinct_initial
                if not any(
                    _dominates(other.costs, entry.costs)
                    for other in distinct_initial
                    if other is not entry
                )
            ),
            key=lambda entry: entry.costs,
        )
    )
    if len(initial_entries) > max_frontier_entries:
        raise ValueError("initial fixed-model frontier exceeds configured cap")
    fixed_value = min(entry.worst_value for entry in initial_entries)
    selected = min(
        (entry for entry in initial_entries if entry.worst_value == fixed_value),
        key=lambda entry: entry.costs,
    )

    rectangular_cache: dict[
        tuple[int, MultiModelBeliefState, int], Fraction
    ] = {}

    def rectangular_value(
        period: int,
        state: MultiModelBeliefState,
        previous_code: int,
    ) -> Fraction:
        key = (period, state, previous_code)
        if key in rectangular_cache:
            return rectangular_cache[key]
        branches = (
            ()
            if period == periods - 1
            else next_model_observation_branches(family, state)
        )
        action_values: list[Fraction] = []
        for code_index, candidate in enumerate(candidates):
            switch = previous_code != sentinel and previous_code != code_index
            per_model: list[Fraction] = []
            for model_index, belief in zip(state.model_indices, state.beliefs):
                value = _scenario_stage_cost(
                    family.scenarios[model_index],
                    belief,
                    candidate,
                ) + penalty * int(switch)
                for branch in branches:
                    probability = branch.probability_for_model(model_index)
                    if probability:
                        value += probability * rectangular_value(
                            period + 1,
                            branch.next_state,
                            code_index,
                        )
                per_model.append(value)
            action_values.append(max(per_model))
        result = min(action_values)
        rectangular_cache[key] = result
        return result

    rectangular_initial_by_model: list[Fraction] = []
    for model_index in range(family.model_count):
        value = Fraction(0)
        for branch in initial_branches:
            probability = branch.probability_for_model(model_index)
            if probability:
                value += probability * rectangular_value(
                    0,
                    branch.next_state,
                    sentinel,
                )
        rectangular_initial_by_model.append(value)
    rectangular = max(rectangular_initial_by_model)

    result = FixedModelAmbiguityCertificate(
        graph,
        family,
        periods,
        penalty,
        enumeration,
        tuple(
            sorted(
                cache.values(),
                key=lambda record: (
                    record.period,
                    record.state.model_indices,
                    record.state.beliefs,
                    record.previous_code,
                ),
            )
        ),
        initial_entries,
        selected.costs,
        fixed_value,
        rectangular,
        len(cache),
        combinations_examined,
        int(max_frontier_nodes),
        int(max_policy_combinations),
        int(max_frontier_entries),
    )
    if not result.valid:
        raise AssertionError("fixed-model ambiguity certificate failed validation")
    return result
