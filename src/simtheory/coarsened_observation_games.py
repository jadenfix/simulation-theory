"""Exact finite minimax coding with deterministic coarsened law observations.

The fully observed dynamic-game lane assumes that the exact current source law
is revealed before every code choice.  This module inserts a deterministic
observation partition between open-loop commitment and full law observation.
The controller sees only the observation cell containing the current law state.

A scalar Bellman value on an information set is generally *not* exact for this
imperfect-information game: replacing the actual hidden state by an arbitrary
state in the next information set can let nature switch between incompatible
hidden paths.  The exact finite recursion therefore propagates a Pareto frontier
of achievable continuation-cost vectors, one coordinate for every possible
actual law state in the current information set.

For an information set B and previous code c-, each frontier entry represents
one deterministic continuation policy.  Its coordinate v_i is the worst future
cost when the actual current state is i in B.  At a nonterminal period, one
current code is chosen and one continuation-frontier entry is selected for each
possible next observation cell.  Nature then selects a transition consistent
with its actual hidden state.  Componentwise dominated cost vectors are safely
removed because every parent operation is coordinatewise monotone.

The construction is finite, exact-rational, deterministic, and bounded by
explicit node, combination, frontier, and dominance caps.  It is a robust
set-membership game, not Bayesian filtering.  It does not infer the hidden law
from samples, price observation acquisition, solve continuous-law feedback, or
provide evidence for simulation or parent-substrate resource claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import prod
from typing import Mapping, Sequence

from .adaptive_drift_games import (
    FeedbackDynamicCodeCertificate,
    FiniteLawTransitionModel,
    OpenLoopDynamicCodeCertificate,
    exact_feedback_dynamic_code,
    exact_open_loop_dynamic_code,
)
from .confusion_graphs import ConfusionGraph
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
)


ExactInput = int | str | Fraction


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be supplied as exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _states_from_mask(mask: int, state_count: int) -> tuple[int, ...]:
    if mask <= 0 or mask >= 1 << state_count:
        raise ValueError("information mask must be a nonempty subset of law states")
    return tuple(index for index in range(state_count) if mask & (1 << index))


def _mask_from_states(states: Sequence[int], state_count: int) -> int:
    normalized = tuple(sorted(set(int(state) for state in states)))
    if not normalized or any(not 0 <= state < state_count for state in normalized):
        raise ValueError("initial possible states are empty or out of range")
    return sum(1 << state for state in normalized)


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
class ObservationPartition:
    """A canonical deterministic observation map on finite law states."""

    labels: tuple[int, ...]
    cells: tuple[tuple[int, ...], ...]
    cell_masks: tuple[int, ...]

    @property
    def state_count(self) -> int:
        return len(self.labels)

    @property
    def class_count(self) -> int:
        return len(self.cells)

    @property
    def valid(self) -> bool:
        if (
            self.state_count < 1
            or self.class_count < 1
            or len(self.cell_masks) != self.class_count
            or set(self.labels) != set(range(self.class_count))
        ):
            return False
        reconstructed = tuple(
            tuple(index for index, label in enumerate(self.labels) if label == cls)
            for cls in range(self.class_count)
        )
        return (
            reconstructed == self.cells
            and all(cell for cell in self.cells)
            and self.cell_masks
            == tuple(sum(1 << state for state in cell) for cell in self.cells)
        )


def observation_partition(labels: Sequence[object]) -> ObservationPartition:
    supplied = tuple(labels)
    if not supplied:
        raise ValueError("observation partition requires at least one law state")
    canonical_map: dict[object, int] = {}
    canonical: list[int] = []
    for label in supplied:
        try:
            if label not in canonical_map:
                canonical_map[label] = len(canonical_map)
            canonical.append(canonical_map[label])
        except TypeError as error:
            raise ValueError("observation labels must be hashable") from error
    labels_tuple = tuple(canonical)
    cells = tuple(
        tuple(index for index, value in enumerate(labels_tuple) if value == cls)
        for cls in range(len(canonical_map))
    )
    result = ObservationPartition(
        labels_tuple,
        cells,
        tuple(sum(1 << state for state in cell) for cell in cells),
    )
    if not result.valid:
        raise AssertionError("canonical observation partition failed validation")
    return result


def no_observation_partition(state_count: int) -> ObservationPartition:
    count = int(state_count)
    if count < 1:
        raise ValueError("state_count must be positive")
    return observation_partition((0,) * count)


def full_observation_partition(state_count: int) -> ObservationPartition:
    count = int(state_count)
    if count < 1:
        raise ValueError("state_count must be positive")
    return observation_partition(tuple(range(count)))


def partition_refines(
    finer: ObservationPartition,
    coarser: ObservationPartition,
) -> bool:
    if (
        not finer.valid
        or not coarser.valid
        or finer.state_count != coarser.state_count
    ):
        return False
    return all(
        len({coarser.labels[state] for state in fine_cell}) == 1
        for fine_cell in finer.cells
    )


def _post_mask(model: FiniteLawTransitionModel, information_mask: int) -> int:
    result = 0
    for state in _states_from_mask(information_mask, model.law_count):
        for successor in model.successors[state]:
            result |= 1 << successor
    return result


def _mask_has_one_observation_class(
    mask: int,
    partition: ObservationPartition,
) -> bool:
    states = _states_from_mask(mask, partition.state_count)
    return len({partition.labels[state] for state in states}) == 1


def _cost_for_state(
    states: Sequence[int],
    costs: Sequence[Fraction],
    state: int,
) -> Fraction:
    try:
        return costs[tuple(states).index(state)]
    except ValueError as error:
        raise AssertionError("state is absent from its continuation information set") from error


@dataclass(frozen=True)
class ContinuationChoice:
    observation_class: int
    next_information_mask: int
    next_costs: tuple[Fraction, ...]


@dataclass(frozen=True)
class PolicyVectorEntry:
    period: int
    information_mask: int
    previous_code: int
    states: tuple[int, ...]
    costs: tuple[Fraction, ...]
    selected_code: int
    continuations: tuple[ContinuationChoice, ...]
    worst_successors: tuple[int, ...]

    @property
    def worst_value(self) -> Fraction:
        return max(self.costs)

    @property
    def valid_shape(self) -> bool:
        return (
            self.period >= 0
            and self.information_mask > 0
            and self.states
            and len(self.states) == len(self.costs) == len(self.worst_successors)
            and all(cost >= 0 for cost in self.costs)
            and tuple(sorted(self.continuations, key=lambda item: item.observation_class))
            == self.continuations
            and len({item.observation_class for item in self.continuations})
            == len(self.continuations)
        )


@dataclass(frozen=True)
class FrontierRecord:
    period: int
    information_mask: int
    previous_code: int
    states: tuple[int, ...]
    entries: tuple[PolicyVectorEntry, ...]
    raw_entry_count: int
    distinct_entry_count: int
    dominated_entry_count: int
    continuation_combinations_examined: int

    @property
    def valid_shape(self) -> bool:
        return (
            self.states
            and self.entries
            and all(
                entry.valid_shape
                and entry.period == self.period
                and entry.information_mask == self.information_mask
                and entry.previous_code == self.previous_code
                and entry.states == self.states
                for entry in self.entries
            )
            and len({entry.costs for entry in self.entries}) == len(self.entries)
            and self.raw_entry_count >= self.distinct_entry_count
            and self.distinct_entry_count
            == len(self.entries) + self.dominated_entry_count
            and not any(
                _cost_vector_dominates(left.costs, right.costs)
                for left_index, left in enumerate(self.entries)
                for right_index, right in enumerate(self.entries)
                if left_index != right_index
            )
        )


@dataclass(frozen=True)
class InitialObservationChoice:
    observation_class: int
    information_mask: int
    entry_costs: tuple[Fraction, ...]
    value: Fraction


@dataclass(frozen=True)
class CoarsenedObservationGameCertificate:
    graph: ConfusionGraph
    transition_model: FiniteLawTransitionModel
    partition: ObservationPartition
    initial_possible_mask: int
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    frontiers: tuple[FrontierRecord, ...]
    initial_choices: tuple[InitialObservationChoice, ...]
    initial_value: Fraction
    worst_initial_observation: int
    adversarial_path: tuple[int, ...]
    observation_path: tuple[int, ...]
    information_path: tuple[int, ...]
    selected_codes: tuple[int, ...]
    entry_cost_path: tuple[tuple[Fraction, ...], ...]
    nodes_built: int
    continuation_combinations_examined: int
    max_nodes: int
    max_policy_combinations: int
    max_frontier_entries: int
    max_dominance_pairs: int

    @property
    def valid(self) -> bool:
        model = self.transition_model
        candidates = self.enumeration.candidates
        code_count = len(candidates)
        sentinel = code_count
        if (
            not model.valid
            or not self.partition.valid
            or self.partition.state_count != model.law_count
            or self.graph.vertex_count != model.source_state_count
            or self.horizon < 1
            or not candidates
            or not self.frontiers
            or any(not record.valid_shape for record in self.frontiers)
            or len(
                {
                    (record.period, record.information_mask, record.previous_code)
                    for record in self.frontiers
                }
            )
            != len(self.frontiers)
            or self.nodes_built != len(self.frontiers)
            or self.nodes_built > self.max_nodes
            or self.continuation_combinations_examined
            > self.max_policy_combinations
            or any(len(record.entries) > self.max_frontier_entries for record in self.frontiers)
            or len(self.adversarial_path) != self.horizon
            or len(self.observation_path) != self.horizon
            or len(self.information_path) != self.horizon
            or len(self.selected_codes) != self.horizon
            or len(self.entry_cost_path) != self.horizon
            or any(not 0 <= code < code_count for code in self.selected_codes)
            or self.adversarial_path[0] not in _states_from_mask(
                self.initial_possible_mask,
                model.law_count,
            )
        ):
            return False

        frontier_map = {
            (record.period, record.information_mask, record.previous_code): record
            for record in self.frontiers
        }
        expected_initial_cells = tuple(
            cls
            for cls, cell_mask in enumerate(self.partition.cell_masks)
            if cell_mask & self.initial_possible_mask
        )
        if tuple(choice.observation_class for choice in self.initial_choices) != expected_initial_cells:
            return False
        if self.initial_value != max(choice.value for choice in self.initial_choices):
            return False
        if self.worst_initial_observation not in expected_initial_cells:
            return False
        worst_choice = next(
            choice
            for choice in self.initial_choices
            if choice.observation_class == self.worst_initial_observation
        )
        if worst_choice.value != self.initial_value:
            return False

        previous_code = sentinel
        cumulative = Fraction(0)
        for period in range(self.horizon):
            actual = self.adversarial_path[period]
            observation = self.observation_path[period]
            information_mask = self.information_path[period]
            if (
                observation != self.partition.labels[actual]
                or not information_mask & (1 << actual)
                or not _mask_has_one_observation_class(information_mask, self.partition)
            ):
                return False
            record = frontier_map.get((period, information_mask, previous_code))
            if record is None:
                return False
            entry = next(
                (
                    candidate
                    for candidate in record.entries
                    if candidate.costs == self.entry_cost_path[period]
                ),
                None,
            )
            if entry is None or entry.selected_code != self.selected_codes[period]:
                return False
            state_position = entry.states.index(actual)
            code = self.selected_codes[period]
            switch = previous_code != sentinel and previous_code != code
            cumulative += _dot(
                model.laws[actual],
                candidates[code].scenario_costs,
            ) + self.switching_penalty * int(switch)
            if period < self.horizon - 1:
                successor = entry.worst_successors[state_position]
                if successor != self.adversarial_path[period + 1]:
                    return False
                if successor not in model.successors[actual]:
                    return False
                next_observation = self.partition.labels[successor]
                post = _post_mask(model, information_mask)
                next_mask = post & self.partition.cell_masks[next_observation]
                if next_mask != self.information_path[period + 1]:
                    return False
                continuation = next(
                    (
                        item
                        for item in entry.continuations
                        if item.observation_class == next_observation
                    ),
                    None,
                )
                if (
                    continuation is None
                    or continuation.next_information_mask != next_mask
                    or continuation.next_costs != self.entry_cost_path[period + 1]
                ):
                    return False
            previous_code = code
        return cumulative == self.initial_value


def _cost_vector_dominates(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> bool:
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def _entry_tie_key(
    entry: PolicyVectorEntry,
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
                item.observation_class,
                item.next_information_mask,
                item.next_costs,
            )
            for item in entry.continuations
        ),
        entry.worst_successors,
    )


def _deduplicate_and_prune_entries(
    entries: Sequence[PolicyVectorEntry],
    candidates: Sequence[RobustCodeCandidate],
    sentinel: int,
    *,
    max_frontier_entries: int,
    max_dominance_pairs: int,
) -> tuple[tuple[PolicyVectorEntry, ...], int, int]:
    by_costs: dict[tuple[Fraction, ...], PolicyVectorEntry] = {}
    for entry in entries:
        incumbent = by_costs.get(entry.costs)
        if incumbent is None or _entry_tie_key(
            entry,
            candidates,
            sentinel,
        ) < _entry_tie_key(incumbent, candidates, sentinel):
            by_costs[entry.costs] = entry
    distinct = tuple(by_costs.values())
    pair_count = len(distinct) * max(0, len(distinct) - 1)
    if pair_count > max_dominance_pairs:
        raise ValueError("frontier dominance search exceeds configured cap")
    retained = tuple(
        entry
        for entry in distinct
        if not any(
            _cost_vector_dominates(other.costs, entry.costs)
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
        raise ValueError("Pareto frontier exceeds configured entry cap")
    return ordered, len(distinct), len(distinct) - len(ordered)


def _enumerate_candidates(
    graph: ConfusionGraph,
    *,
    max_vertices: int,
    max_partitions: int,
    max_candidates: int,
    max_prefix_assignments: int,
    max_prefix_shapes: int,
    max_code_dominance_pairs: int,
) -> RobustCandidateEnumeration:
    return enumerate_robust_code_candidates(
        graph,
        _simplex_vertices(graph.vertex_count),
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_code_dominance_pairs,
    )


def exact_coarsened_observation_game(
    graph: ConfusionGraph,
    transition_model: FiniteLawTransitionModel,
    partition: ObservationPartition,
    initial_possible_states: Sequence[int],
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_code_dominance_pairs: int = 4_000_000,
    max_nodes: int = 10_000,
    max_policy_combinations: int = 2_000_000,
    max_frontier_entries: int = 100_000,
    max_frontier_dominance_pairs: int = 4_000_000,
) -> CoarsenedObservationGameCertificate:
    if (
        not transition_model.valid
        or not partition.valid
        or partition.state_count != transition_model.law_count
        or graph.vertex_count != transition_model.source_state_count
    ):
        raise ValueError("graph, transition model, and observation partition disagree")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")
    initial_mask = _mask_from_states(
        initial_possible_states,
        transition_model.law_count,
    )
    if any(
        int(cap) != cap or int(cap) < 1
        for cap in (
            max_nodes,
            max_policy_combinations,
            max_frontier_entries,
            max_frontier_dominance_pairs,
        )
    ):
        raise ValueError("all coarsened-observation search caps must be positive integers")

    enumeration = _enumerate_candidates(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_code_dominance_pairs=max_code_dominance_pairs,
    )
    candidates = enumeration.candidates
    code_count = len(candidates)
    sentinel = code_count
    cache: dict[tuple[int, int, int], FrontierRecord] = {}
    total_combinations = 0

    def build_frontier(
        period: int,
        information_mask: int,
        previous_code: int,
    ) -> FrontierRecord:
        nonlocal total_combinations
        key = (period, information_mask, previous_code)
        if key in cache:
            return cache[key]
        if len(cache) >= max_nodes:
            raise ValueError("coarsened-observation node count exceeds configured cap")
        if not _mask_has_one_observation_class(information_mask, partition):
            raise AssertionError("decision information set crosses observation cells")
        states = _states_from_mask(information_mask, transition_model.law_count)
        raw_entries: list[PolicyVectorEntry] = []
        combinations_examined = 0

        if period == periods - 1:
            for code_index, candidate in enumerate(candidates):
                switch = previous_code != sentinel and previous_code != code_index
                costs = tuple(
                    _dot(transition_model.laws[state], candidate.scenario_costs)
                    + penalty * int(switch)
                    for state in states
                )
                raw_entries.append(
                    PolicyVectorEntry(
                        period,
                        information_mask,
                        previous_code,
                        states,
                        costs,
                        code_index,
                        (),
                        tuple(-1 for _ in states),
                    )
                )
        else:
            post_mask = _post_mask(transition_model, information_mask)
            reachable_classes = tuple(
                cls
                for cls, cell_mask in enumerate(partition.cell_masks)
                if post_mask & cell_mask
            )
            for code_index, candidate in enumerate(candidates):
                next_records = tuple(
                    build_frontier(
                        period + 1,
                        post_mask & partition.cell_masks[cls],
                        code_index,
                    )
                    for cls in reachable_classes
                )
                combination_count = prod(len(record.entries) for record in next_records)
                if total_combinations + combination_count > max_policy_combinations:
                    raise ValueError(
                        "continuation-policy combination count exceeds configured cap"
                    )
                for chosen_entries in product(
                    *(record.entries for record in next_records)
                ):
                    total_combinations += 1
                    combinations_examined += 1
                    continuation_by_class = {
                        cls: (record, entry)
                        for cls, record, entry in zip(
                            reachable_classes,
                            next_records,
                            chosen_entries,
                        )
                    }
                    switch = previous_code != sentinel and previous_code != code_index
                    costs: list[Fraction] = []
                    worst_successors: list[int] = []
                    for state in states:
                        successor_options: list[tuple[Fraction, int]] = []
                        for successor in transition_model.successors[state]:
                            cls = partition.labels[successor]
                            record, continuation = continuation_by_class[cls]
                            successor_options.append(
                                (
                                    _cost_for_state(
                                        record.states,
                                        continuation.costs,
                                        successor,
                                    ),
                                    successor,
                                )
                            )
                        worst = max(value for value, _ in successor_options)
                        witness = min(
                            successor
                            for value, successor in successor_options
                            if value == worst
                        )
                        costs.append(
                            _dot(
                                transition_model.laws[state],
                                candidate.scenario_costs,
                            )
                            + penalty * int(switch)
                            + worst
                        )
                        worst_successors.append(witness)
                    raw_entries.append(
                        PolicyVectorEntry(
                            period,
                            information_mask,
                            previous_code,
                            states,
                            tuple(costs),
                            code_index,
                            tuple(
                                ContinuationChoice(
                                    cls,
                                    record.information_mask,
                                    entry.costs,
                                )
                                for cls, record, entry in zip(
                                    reachable_classes,
                                    next_records,
                                    chosen_entries,
                                )
                            ),
                            tuple(worst_successors),
                        )
                    )

        entries, distinct_count, dominated_count = _deduplicate_and_prune_entries(
            raw_entries,
            candidates,
            sentinel,
            max_frontier_entries=max_frontier_entries,
            max_dominance_pairs=max_frontier_dominance_pairs,
        )
        record = FrontierRecord(
            period,
            information_mask,
            previous_code,
            states,
            entries,
            len(raw_entries),
            distinct_count,
            dominated_count,
            combinations_examined,
        )
        if not record.valid_shape:
            raise AssertionError("constructed Pareto frontier failed validation")
        cache[key] = record
        return record

    initial_choices: list[InitialObservationChoice] = []
    initial_entry_by_class: dict[int, PolicyVectorEntry] = {}
    for cls, cell_mask in enumerate(partition.cell_masks):
        information_mask = initial_mask & cell_mask
        if not information_mask:
            continue
        record = build_frontier(0, information_mask, sentinel)
        best_value = min(entry.worst_value for entry in record.entries)
        best_entries = tuple(
            entry for entry in record.entries if entry.worst_value == best_value
        )
        selected = min(
            best_entries,
            key=lambda entry: (
                entry.costs,
                _entry_tie_key(entry, candidates, sentinel),
            ),
        )
        initial_choices.append(
            InitialObservationChoice(
                cls,
                information_mask,
                selected.costs,
                best_value,
            )
        )
        initial_entry_by_class[cls] = selected

    initial_value = max(choice.value for choice in initial_choices)
    worst_initial_class = min(
        choice.observation_class
        for choice in initial_choices
        if choice.value == initial_value
    )
    current_entry = initial_entry_by_class[worst_initial_class]
    actual_state = min(
        state
        for state, cost in zip(current_entry.states, current_entry.costs)
        if cost == current_entry.worst_value
    )
    adversarial_path: list[int] = []
    observation_path: list[int] = []
    information_path: list[int] = []
    selected_codes: list[int] = []
    entry_cost_path: list[tuple[Fraction, ...]] = []
    previous_code = sentinel

    for period in range(periods):
        adversarial_path.append(actual_state)
        observation_path.append(partition.labels[actual_state])
        information_path.append(current_entry.information_mask)
        selected_codes.append(current_entry.selected_code)
        entry_cost_path.append(current_entry.costs)
        if period == periods - 1:
            break
        position = current_entry.states.index(actual_state)
        successor = current_entry.worst_successors[position]
        next_class = partition.labels[successor]
        continuation = next(
            item
            for item in current_entry.continuations
            if item.observation_class == next_class
        )
        next_record = cache[
            (
                period + 1,
                continuation.next_information_mask,
                current_entry.selected_code,
            )
        ]
        current_entry = next(
            entry
            for entry in next_record.entries
            if entry.costs == continuation.next_costs
        )
        actual_state = successor
        previous_code = selected_codes[-1]

    result = CoarsenedObservationGameCertificate(
        graph,
        transition_model,
        partition,
        initial_mask,
        periods,
        penalty,
        enumeration,
        tuple(sorted(cache.values(), key=lambda row: (row.period, row.information_mask, row.previous_code))),
        tuple(initial_choices),
        initial_value,
        worst_initial_class,
        tuple(adversarial_path),
        tuple(observation_path),
        tuple(information_path),
        tuple(selected_codes),
        tuple(entry_cost_path),
        len(cache),
        total_combinations,
        int(max_nodes),
        int(max_policy_combinations),
        int(max_frontier_entries),
        int(max_frontier_dominance_pairs),
    )
    if not result.valid:
        raise AssertionError("coarsened-observation game certificate failed validation")
    return result


@dataclass(frozen=True)
class PartitionRefinementCertificate:
    coarser: CoarsenedObservationGameCertificate
    finer: CoarsenedObservationGameCertificate

    @property
    def information_gain(self) -> Fraction:
        return self.coarser.initial_value - self.finer.initial_value

    @property
    def valid(self) -> bool:
        return (
            self.coarser.valid
            and self.finer.valid
            and self.coarser.graph == self.finer.graph
            and self.coarser.transition_model == self.finer.transition_model
            and self.coarser.initial_possible_mask == self.finer.initial_possible_mask
            and self.coarser.horizon == self.finer.horizon
            and self.coarser.switching_penalty == self.finer.switching_penalty
            and partition_refines(self.finer.partition, self.coarser.partition)
            and self.information_gain >= 0
        )


def exact_partition_refinement_value(
    graph: ConfusionGraph,
    transition_model: FiniteLawTransitionModel,
    coarser: ObservationPartition,
    finer: ObservationPartition,
    initial_possible_states: Sequence[int],
    horizon: int,
    **kwargs: object,
) -> PartitionRefinementCertificate:
    if not partition_refines(finer, coarser):
        raise ValueError("the supplied finer partition does not refine the coarser one")
    coarse_result = exact_coarsened_observation_game(
        graph,
        transition_model,
        coarser,
        initial_possible_states,
        horizon,
        **kwargs,
    )
    fine_result = exact_coarsened_observation_game(
        graph,
        transition_model,
        finer,
        initial_possible_states,
        horizon,
        **kwargs,
    )
    result = PartitionRefinementCertificate(coarse_result, fine_result)
    if not result.valid:
        raise AssertionError("observation-partition refinement certificate failed")
    return result


@dataclass(frozen=True)
class EndpointEquivalenceCertificate:
    no_observation: CoarsenedObservationGameCertificate
    full_observation: CoarsenedObservationGameCertificate
    open_loop: OpenLoopDynamicCodeCertificate
    feedback: FeedbackDynamicCodeCertificate

    @property
    def valid(self) -> bool:
        initial_states = _states_from_mask(
            self.no_observation.initial_possible_mask,
            self.no_observation.transition_model.law_count,
        )
        return (
            self.no_observation.valid
            and self.full_observation.valid
            and self.open_loop.valid
            and self.feedback.valid
            and len(initial_states) == 1
            and self.no_observation.initial_value == self.open_loop.selected_value
            and self.full_observation.initial_value == self.feedback.initial_value
            and self.no_observation.transition_model
            == self.full_observation.transition_model
            == self.open_loop.transition_model
            == self.feedback.transition_model
            and self.no_observation.horizon
            == self.full_observation.horizon
            == self.open_loop.horizon
            == self.feedback.horizon
        )


def exact_endpoint_equivalence(
    graph: ConfusionGraph,
    transition_model: FiniteLawTransitionModel,
    initial_law_index: int,
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_sequences: int = 100_000,
    **kwargs: object,
) -> EndpointEquivalenceCertificate:
    initial = int(initial_law_index)
    if not 0 <= initial < transition_model.law_count:
        raise ValueError("initial_law_index is out of range")
    coarsened_kwargs = dict(kwargs)
    common_adaptive = {
        key: value
        for key, value in kwargs.items()
        if key
        in {
            "max_vertices",
            "max_partitions",
            "max_candidates",
            "max_prefix_assignments",
            "max_prefix_shapes",
            "max_code_dominance_pairs",
        }
    }
    if "max_code_dominance_pairs" in common_adaptive:
        common_adaptive["max_dominance_pairs"] = common_adaptive.pop(
            "max_code_dominance_pairs"
        )
    no_observation = exact_coarsened_observation_game(
        graph,
        transition_model,
        no_observation_partition(transition_model.law_count),
        (initial,),
        horizon,
        switching_penalty=switching_penalty,
        **coarsened_kwargs,
    )
    full_observation = exact_coarsened_observation_game(
        graph,
        transition_model,
        full_observation_partition(transition_model.law_count),
        (initial,),
        horizon,
        switching_penalty=switching_penalty,
        **coarsened_kwargs,
    )
    open_loop = exact_open_loop_dynamic_code(
        graph,
        transition_model,
        initial,
        horizon,
        switching_penalty=switching_penalty,
        max_sequences=max_sequences,
        **common_adaptive,
    )
    feedback = exact_feedback_dynamic_code(
        graph,
        transition_model,
        initial,
        horizon,
        switching_penalty=switching_penalty,
        **common_adaptive,
    )
    result = EndpointEquivalenceCertificate(
        no_observation,
        full_observation,
        open_loop,
        feedback,
    )
    if not result.valid:
        raise AssertionError("observation endpoint equivalence failed")
    return result
