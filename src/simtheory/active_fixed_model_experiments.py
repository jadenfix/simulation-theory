"""Exact finite active sensing under one globally fixed probabilistic model.

This module extends the fixed-model ambiguity frontier by allowing the controller
to choose a public experiment before each period's observation.  Nature chooses
one model once for the whole horizon; it may not reselect a model after seeing
which experiment or observation occurred.

Timing in each period is:

1. choose an experiment from a finite declared menu;
2. observe its public signal;
3. choose a deterministic zero-error prefix code using that signal and history;
4. pay acquisition cost plus expected code length;
5. if another period remains, the hidden state transitions under the same model.

The exact policy object is a Pareto frontier of model-indexed expected costs.
Within one experiment, a separate public continuation is chosen for each signal.
This preserves fixed model identity while permitting genuinely adaptive future
experiment choices.

A key semantic point is that an uninformative public signal can still improve a
deterministic minimax policy by supplying source-independent public randomness.
Therefore raw improvement from an observation cannot automatically be called
"information value".  The tests and derivation separate no-signal value, public
randomization value, and model-informative sensing value.

All probabilities and costs are exact rational numbers and every combinatorial
search is bounded by explicit caps.  This is an internal finite decision model,
not empirical evidence for simulation or for any parent-universe resource bound.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .fixed_model_ambiguity import FixedModelFamily, MultiModelBeliefState
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)
from .stochastic_observation_beliefs import (
    Belief,
    ObservationKernel,
    _observe_belief,
    _predict_belief,
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


def _simplex_vertices(count: int) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(Fraction(1) if i == j else Fraction(0) for j in range(count))
        for i in range(count)
    )


@dataclass(frozen=True)
class ActiveExperiment:
    name: str
    kernels: tuple[ObservationKernel, ...]
    acquisition_cost: Fraction

    @property
    def observation_count(self) -> int:
        return self.kernels[0].observation_count

    @property
    def valid(self) -> bool:
        return (
            bool(self.name)
            and bool(self.kernels)
            and self.acquisition_cost >= 0
            and all(kernel.valid for kernel in self.kernels)
            and all(
                kernel.observation_count == self.observation_count
                for kernel in self.kernels
            )
        )


def active_experiment(
    name: str,
    kernels: Sequence[ObservationKernel],
    acquisition_cost: ExactInput = 0,
) -> ActiveExperiment:
    result = ActiveExperiment(
        str(name),
        tuple(kernels),
        _fraction(acquisition_cost, name="acquisition cost"),
    )
    if not result.valid:
        raise ValueError("invalid active experiment")
    return result


def experiment_is_source_independent(experiment: ActiveExperiment) -> bool:
    """Return whether every hidden state of every model emits one common law."""
    if not experiment.valid:
        return False
    reference = experiment.kernels[0].probabilities[0]
    return all(
        row == reference
        for kernel in experiment.kernels
        for row in kernel.probabilities
    )


@dataclass(frozen=True)
class ActiveObservationBranch:
    observation: int
    model_indices: tuple[int, ...]
    probabilities: tuple[Fraction, ...]
    posteriors: tuple[Belief, ...]
    next_state: MultiModelBeliefState | None

    @property
    def valid(self) -> bool:
        return (
            self.observation >= 0
            and self.model_indices
            and len(self.model_indices) == len(self.probabilities) == len(self.posteriors)
            and all(value > 0 for value in self.probabilities)
            and all(sum(belief, Fraction(0)) == 1 for belief in self.posteriors)
            and (
                self.next_state is None
                or (
                    self.next_state.valid
                    and self.next_state.model_indices == self.model_indices
                )
            )
        )


@dataclass(frozen=True)
class SignalDecision:
    observation: int
    model_indices: tuple[int, ...]
    conditional_costs: tuple[Fraction, ...]
    selected_code: int
    next_costs: tuple[Fraction, ...]


@dataclass(frozen=True)
class ActivePolicyEntry:
    period: int
    state: MultiModelBeliefState
    costs: tuple[Fraction, ...]
    selected_experiment: int
    signal_decisions: tuple[SignalDecision, ...]

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
            and tuple(sorted(d.observation for d in self.signal_decisions))
            == tuple(d.observation for d in self.signal_decisions)
        )


@dataclass(frozen=True)
class ActiveFrontierRecord:
    period: int
    state: MultiModelBeliefState
    entries: tuple[ActivePolicyEntry, ...]
    raw_count: int
    distinct_count: int
    dominated_count: int
    combinations_examined: int


@dataclass(frozen=True)
class ActiveExperimentCertificate:
    graph: ConfusionGraph
    family: FixedModelFamily
    experiments: tuple[ActiveExperiment, ...]
    horizon: int
    enumeration: RobustCandidateEnumeration
    frontiers: tuple[ActiveFrontierRecord, ...]
    initial_state: MultiModelBeliefState
    selected_costs: tuple[Fraction, ...]
    selected_experiment: int
    robust_value: Fraction
    nodes_built: int
    combinations_examined: int
    max_nodes: int
    max_combinations: int
    max_frontier_entries: int

    @property
    def valid(self) -> bool:
        if (
            not self.family.valid
            or self.graph.vertex_count != self.family.source_symbol_count
            or self.horizon < 1
            or not self.experiments
            or not self.enumeration.candidates
            or not self.initial_state.valid
            or self.nodes_built != len(self.frontiers)
            or self.nodes_built > self.max_nodes
            or self.combinations_examined > self.max_combinations
            or len(self.selected_costs) != self.family.model_count
            or self.robust_value != max(self.selected_costs)
            or not 0 <= self.selected_experiment < len(self.experiments)
        ):
            return False
        root = next(
            (
                record
                for record in self.frontiers
                if record.period == 0 and record.state == self.initial_state
            ),
            None,
        )
        if root is None or not root.entries:
            return False
        selected = min(
            root.entries,
            key=lambda entry: (
                entry.worst_value,
                entry.costs,
                self.experiments[entry.selected_experiment].name,
                entry.selected_experiment,
            ),
        )
        return (
            selected.costs == self.selected_costs
            and selected.selected_experiment == self.selected_experiment
            and selected.worst_value == self.robust_value
            and all(len(record.entries) <= self.max_frontier_entries for record in self.frontiers)
        )


def _scenario_stage_cost(
    family: FixedModelFamily,
    model_index: int,
    belief: Belief,
    candidate: RobustCodeCandidate,
) -> Fraction:
    scenario = family.scenarios[model_index]
    hidden_costs = tuple(
        _dot(source_law, candidate.scenario_costs)
        for source_law in scenario.model.laws
    )
    return _dot(belief, hidden_costs)


def _branches(
    family: FixedModelFamily,
    state: MultiModelBeliefState,
    experiment: ActiveExperiment,
    *,
    terminal: bool,
) -> tuple[ActiveObservationBranch, ...]:
    if len(experiment.kernels) != family.model_count:
        raise ValueError("experiment requires one kernel per fixed model")
    per_model: dict[int, dict[int, tuple[Fraction, Belief]]] = {}
    for model_index, belief in zip(state.model_indices, state.beliefs):
        kernel = experiment.kernels[model_index]
        scenario = family.scenarios[model_index]
        if kernel.hidden_state_count != scenario.model.hidden_state_count:
            raise ValueError("experiment kernel hidden-state dimension mismatch")
        per_model[model_index] = {
            branch.observation: (branch.probability, branch.posterior)
            for branch in _observe_belief(belief, kernel)
        }
    observations = tuple(
        sorted({obs for mapping in per_model.values() for obs in mapping})
    )
    results: list[ActiveObservationBranch] = []
    for obs in observations:
        active = tuple(
            model_index
            for model_index in state.model_indices
            if obs in per_model[model_index]
        )
        probabilities = tuple(per_model[m][obs][0] for m in active)
        posteriors = tuple(per_model[m][obs][1] for m in active)
        next_state = None
        if not terminal:
            next_state = MultiModelBeliefState(
                active,
                tuple(
                    _predict_belief(posterior, family.scenarios[m].model)
                    for m, posterior in zip(active, posteriors)
                ),
            )
        branch = ActiveObservationBranch(
            obs, active, probabilities, posteriors, next_state
        )
        if not branch.valid:
            raise AssertionError("active observation branch failed validation")
        results.append(branch)
    return tuple(results)


def _dominates(left: Sequence[Fraction], right: Sequence[Fraction]) -> bool:
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def _prune(
    entries: Sequence[ActivePolicyEntry],
    experiments: Sequence[ActiveExperiment],
    *,
    max_frontier_entries: int,
    max_dominance_pairs: int,
) -> tuple[tuple[ActivePolicyEntry, ...], int, int]:
    by_costs: dict[tuple[Fraction, ...], ActivePolicyEntry] = {}
    for entry in entries:
        key = (
            experiments[entry.selected_experiment].name,
            entry.selected_experiment,
            tuple((d.observation, d.selected_code, d.next_costs) for d in entry.signal_decisions),
        )
        incumbent = by_costs.get(entry.costs)
        if incumbent is None:
            by_costs[entry.costs] = entry
        else:
            incumbent_key = (
                experiments[incumbent.selected_experiment].name,
                incumbent.selected_experiment,
                tuple((d.observation, d.selected_code, d.next_costs) for d in incumbent.signal_decisions),
            )
            if key < incumbent_key:
                by_costs[entry.costs] = entry
    distinct = tuple(by_costs.values())
    if len(distinct) * max(0, len(distinct) - 1) > max_dominance_pairs:
        raise ValueError("active-experiment dominance search exceeds configured cap")
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
                experiments[entry.selected_experiment].name,
                entry.selected_experiment,
            ),
        )
    )
    if len(ordered) > max_frontier_entries:
        raise ValueError("active-experiment policy frontier exceeds configured cap")
    return ordered, len(distinct), len(distinct) - len(ordered)


def exact_active_fixed_model_experiment_design(
    graph: ConfusionGraph,
    family: FixedModelFamily,
    experiments: Sequence[ActiveExperiment],
    horizon: int,
    *,
    max_vertices: int = 8,
    max_partitions: int = 10000,
    max_candidates: int = 10000,
    max_prefix_assignments: int = 100000,
    max_prefix_shapes: int = 10000,
    max_dominance_pairs: int = 1000000,
    max_nodes: int = 10000,
    max_combinations: int = 1000000,
    max_frontier_entries: int = 10000,
) -> ActiveExperimentCertificate:
    """Solve the bounded finite-horizon deterministic active-sensing minimax game."""
    if not family.valid:
        raise ValueError("fixed model family must be valid")
    if graph.vertex_count != family.source_symbol_count:
        raise ValueError("graph and family source alphabets differ")
    if int(horizon) < 1:
        raise ValueError("horizon must be positive")
    exp_tuple = tuple(experiments)
    if not exp_tuple or any(not experiment.valid for experiment in exp_tuple):
        raise ValueError("at least one valid experiment is required")
    if len({experiment.name for experiment in exp_tuple}) != len(exp_tuple):
        raise ValueError("experiment names must be unique")
    for experiment in exp_tuple:
        if len(experiment.kernels) != family.model_count:
            raise ValueError("each experiment requires one kernel per fixed model")
        for model_index, kernel in enumerate(experiment.kernels):
            if kernel.hidden_state_count != family.scenarios[model_index].model.hidden_state_count:
                raise ValueError("experiment kernel hidden-state dimension mismatch")

    enumeration = enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    if not candidates:
        raise ValueError("zero-error code universe is empty")

    root_state = MultiModelBeliefState(
        tuple(range(family.model_count)),
        tuple(scenario.initial_prior for scenario in family.scenarios),
    )
    records: dict[tuple[int, MultiModelBeliefState], ActiveFrontierRecord] = {}
    combination_counter = 0

    def solve(period: int, state: MultiModelBeliefState) -> tuple[ActivePolicyEntry, ...]:
        nonlocal combination_counter
        key = (period, state)
        if key in records:
            return records[key].entries
        if len(records) >= max_nodes:
            raise ValueError("active-experiment frontier nodes exceed configured cap")
        terminal = period == int(horizon) - 1
        raw: list[ActivePolicyEntry] = []
        node_combinations = 0

        for experiment_index, experiment in enumerate(exp_tuple):
            branches = _branches(family, state, experiment, terminal=terminal)
            branch_options: list[tuple[SignalDecision, ...]] = []
            for branch in branches:
                options: list[SignalDecision] = []
                continuation_entries = (None,) if terminal else solve(period + 1, branch.next_state)  # type: ignore[arg-type]
                for code_index, candidate in enumerate(candidates):
                    for continuation in continuation_entries:
                        conditional: list[Fraction] = []
                        next_costs: tuple[Fraction, ...] = ()
                        if continuation is not None:
                            next_costs = continuation.costs
                        for model_index, posterior in zip(branch.model_indices, branch.posteriors):
                            stage = _scenario_stage_cost(
                                family, model_index, posterior, candidate
                            )
                            future = Fraction(0)
                            if continuation is not None:
                                position = continuation.state.model_indices.index(model_index)
                                future = continuation.costs[position]
                            conditional.append(stage + future)
                        options.append(
                            SignalDecision(
                                branch.observation,
                                branch.model_indices,
                                tuple(conditional),
                                code_index,
                                next_costs,
                            )
                        )
                branch_options.append(tuple(options))

            count = prod(len(options) for options in branch_options)
            node_combinations += count
            combination_counter += count
            if combination_counter > max_combinations:
                raise ValueError("active-experiment policy combinations exceed configured cap")

            for chosen in product(*branch_options):
                model_costs: list[Fraction] = []
                for model_index in state.model_indices:
                    total = experiment.acquisition_cost
                    for branch, decision in zip(branches, chosen):
                        if model_index not in branch.model_indices:
                            continue
                        pos = branch.model_indices.index(model_index)
                        total += branch.probabilities[pos] * decision.conditional_costs[pos]
                    model_costs.append(total)
                raw.append(
                    ActivePolicyEntry(
                        period,
                        state,
                        tuple(model_costs),
                        experiment_index,
                        tuple(chosen),
                    )
                )

        entries, distinct_count, dominated_count = _prune(
            raw,
            exp_tuple,
            max_frontier_entries=max_frontier_entries,
            max_dominance_pairs=max_dominance_pairs,
        )
        record = ActiveFrontierRecord(
            period,
            state,
            entries,
            len(raw),
            distinct_count,
            dominated_count,
            node_combinations,
        )
        records[key] = record
        return entries

    root_entries = solve(0, root_state)
    selected = min(
        root_entries,
        key=lambda entry: (
            entry.worst_value,
            entry.costs,
            exp_tuple[entry.selected_experiment].name,
            entry.selected_experiment,
        ),
    )
    certificate = ActiveExperimentCertificate(
        graph,
        family,
        exp_tuple,
        int(horizon),
        enumeration,
        tuple(
            sorted(
                records.values(),
                key=lambda record: (
                    record.period,
                    record.state.model_indices,
                    record.state.beliefs,
                ),
            )
        ),
        root_state,
        selected.costs,
        selected.selected_experiment,
        selected.worst_value,
        len(records),
        combination_counter,
        max_nodes,
        max_combinations,
        max_frontier_entries,
    )
    if not certificate.valid:
        raise AssertionError("active fixed-model experiment certificate failed validation")
    return certificate
