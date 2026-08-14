"""Exact finite dynamic games for observed source-law drift and code switching.

The coupled open-loop lane chooses a complete code sequence before the source
path.  This module changes the information pattern: at each period the current
source law is assumed to be observed exactly before a deterministic zero-error
prefix code is chosen.  After the stage cost is paid, an adversary chooses the
next law from a declared finite transition relation.

For finite law states Q, code actions C, horizon T, and switching penalty kappa,
backward induction gives

    V_t(q,c_prev) = min_c [
        q . ell_c + kappa 1{c != c_prev}
        + max_{q' in Gamma(q)} V_{t+1}(q',c)
    ].

The first code incurs no switching penalty.  A separate open-loop solver
chooses the entire code sequence before the adversarial path.  Because a
feedback policy can ignore observations and emulate any open-loop sequence,
the fully observed value cannot exceed the open-loop value.

All arithmetic is exact rational and all finite action, path, and policy spaces
are bounded by explicit caps.  The current law is an *assumed observed state*;
this module does not infer it from samples.  It does not solve partial
observation, belief-state filtering, stochastic control, or continuous-law
feedback.  The results are internal source-coding theorems, not evidence for
simulation or parent-substrate resource claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Sequence

from .confusion_graphs import ConfusionGraph
from .distributionally_robust_codes import total_variation_distance
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


def _validate_law(values: Sequence[ExactInput], *, state_count: int | None = None) -> tuple[Fraction, ...]:
    law = tuple(_fraction(value, name="law probability") for value in values)
    if not law or (state_count is not None and len(law) != state_count):
        raise ValueError("law dimension is empty or inconsistent")
    if any(value < 0 for value in law):
        raise ValueError("law probabilities must be nonnegative")
    if sum(law, Fraction(0)) != 1:
        raise ValueError("law probabilities must sum exactly to one")
    return law


def _dot(law: Sequence[Fraction], lengths: Sequence[Fraction]) -> Fraction:
    return sum((probability * length for probability, length in zip(law, lengths)), Fraction(0))


def _simplex_vertices(state_count: int) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(Fraction(1) if row == column else Fraction(0) for column in range(state_count))
        for row in range(state_count)
    )


@dataclass(frozen=True)
class FiniteLawTransitionModel:
    laws: tuple[tuple[Fraction, ...], ...]
    successors: tuple[tuple[int, ...], ...]

    @property
    def law_count(self) -> int:
        return len(self.laws)

    @property
    def source_state_count(self) -> int:
        return len(self.laws[0])

    @property
    def valid(self) -> bool:
        return (
            bool(self.laws)
            and len(self.successors) == self.law_count
            and all(
                len(law) == self.source_state_count
                and all(value >= 0 for value in law)
                and sum(law, Fraction(0)) == 1
                for law in self.laws
            )
            and all(
                bool(indices)
                and tuple(sorted(set(indices))) == indices
                and all(0 <= index < self.law_count for index in indices)
                for indices in self.successors
            )
        )


def finite_law_transition_model(
    laws: Sequence[Sequence[ExactInput]],
    successors: Sequence[Sequence[int]],
) -> FiniteLawTransitionModel:
    supplied = tuple(tuple(values) for values in laws)
    if not supplied:
        raise ValueError("at least one law state is required")
    first = _validate_law(supplied[0])
    validated = (first,) + tuple(
        _validate_law(values, state_count=len(first)) for values in supplied[1:]
    )
    if len(successors) != len(validated):
        raise ValueError("one successor set is required per law state")
    normalized = tuple(tuple(sorted(set(int(index) for index in row))) for row in successors)
    result = FiniteLawTransitionModel(validated, normalized)
    if not result.valid:
        raise ValueError("invalid finite law transition relation")
    return result


def tv_law_transition_model(
    laws: Sequence[Sequence[ExactInput]],
    drift_per_step: ExactInput,
) -> FiniteLawTransitionModel:
    supplied = tuple(tuple(values) for values in laws)
    if not supplied:
        raise ValueError("at least one law state is required")
    first = _validate_law(supplied[0])
    validated = (first,) + tuple(
        _validate_law(values, state_count=len(first)) for values in supplied[1:]
    )
    eta = _fraction(drift_per_step, name="drift_per_step")
    if not 0 <= eta <= 1:
        raise ValueError("drift_per_step must lie in [0,1]")
    successors = tuple(
        tuple(
            right
            for right, target in enumerate(validated)
            if total_variation_distance(source, target) <= eta
        )
        for source in validated
    )
    return finite_law_transition_model(validated, successors)


def transition_relation_is_subset(
    smaller: FiniteLawTransitionModel,
    larger: FiniteLawTransitionModel,
) -> bool:
    return (
        smaller.laws == larger.laws
        and all(set(left) <= set(right) for left, right in zip(smaller.successors, larger.successors))
    )


def _enumerate_code_actions(
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


def _stage_cost(
    law: Sequence[Fraction],
    candidate: RobustCodeCandidate,
    previous_code: int,
    code_index: int,
    switching_penalty: Fraction,
    sentinel: int,
) -> Fraction:
    switch = previous_code != sentinel and previous_code != code_index
    return _dot(law, candidate.scenario_costs) + switching_penalty * int(switch)


@dataclass(frozen=True)
class OpenLoopDynamicCodeCertificate:
    graph: ConfusionGraph
    transition_model: FiniteLawTransitionModel
    initial_law_index: int
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    selected_sequence: tuple[int, ...]
    selected_candidates: tuple[RobustCodeCandidate, ...]
    selected_value: Fraction
    worst_path: tuple[int, ...]
    sequence_values: tuple[Fraction, ...]
    sequences_examined: int
    max_sequences: int

    @property
    def valid(self) -> bool:
        candidates = self.enumeration.candidates
        code_count = len(candidates)
        if (
            not self.transition_model.valid
            or self.graph.vertex_count != self.transition_model.source_state_count
            or self.horizon < 1
            or not 0 <= self.initial_law_index < self.transition_model.law_count
            or len(self.selected_sequence) != self.horizon
            or len(self.selected_candidates) != self.horizon
            or any(not 0 <= index < code_count for index in self.selected_sequence)
            or self.selected_candidates != tuple(candidates[index] for index in self.selected_sequence)
            or len(self.worst_path) != self.horizon
            or self.worst_path[0] != self.initial_law_index
            or any(
                right not in self.transition_model.successors[left]
                for left, right in zip(self.worst_path, self.worst_path[1:])
            )
            or self.sequences_examined != code_count ** self.horizon
            or len(self.sequence_values) != self.sequences_examined
            or self.selected_value != min(self.sequence_values)
        ):
            return False
        value = Fraction(0)
        sentinel = code_count
        previous = sentinel
        for law_index, code_index in zip(self.worst_path, self.selected_sequence):
            value += _stage_cost(
                self.transition_model.laws[law_index],
                candidates[code_index],
                previous,
                code_index,
                self.switching_penalty,
                sentinel,
            )
            previous = code_index
        return value == self.selected_value


def _open_loop_sequence_value(
    model: FiniteLawTransitionModel,
    candidates: Sequence[RobustCodeCandidate],
    sequence: Sequence[int],
    initial_law_index: int,
    switching_penalty: Fraction,
) -> tuple[Fraction, tuple[int, ...]]:
    horizon = len(sequence)
    law_count = model.law_count
    code_count = len(candidates)
    sentinel = code_count
    values: list[tuple[Fraction, ...]] = [tuple() for _ in range(horizon)]
    successor_witnesses: list[tuple[int, ...]] = [tuple() for _ in range(max(0, horizon - 1))]

    for period in range(horizon - 1, -1, -1):
        code = sequence[period]
        previous = sentinel if period == 0 else sequence[period - 1]
        current_values: list[Fraction] = []
        current_successors: list[int] = []
        for law_index, law in enumerate(model.laws):
            stage = _stage_cost(
                law,
                candidates[code],
                previous,
                code,
                switching_penalty,
                sentinel,
            )
            if period == horizon - 1:
                current_values.append(stage)
                continue
            options = tuple(
                (values[period + 1][successor], successor)
                for successor in model.successors[law_index]
            )
            worst_value = max(value for value, _ in options)
            worst_successor = min(
                successor for value, successor in options if value == worst_value
            )
            current_values.append(stage + worst_value)
            current_successors.append(worst_successor)
        values[period] = tuple(current_values)
        if period < horizon - 1:
            successor_witnesses[period] = tuple(current_successors)

    path = [initial_law_index]
    for period in range(horizon - 1):
        path.append(successor_witnesses[period][path[-1]])
    return values[0][initial_law_index], tuple(path)


def exact_open_loop_dynamic_code(
    graph: ConfusionGraph,
    transition_model: FiniteLawTransitionModel,
    initial_law_index: int,
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_sequences: int = 100_000,
) -> OpenLoopDynamicCodeCertificate:
    if graph.vertex_count != transition_model.source_state_count:
        raise ValueError("graph and law-state dimensions differ")
    if not transition_model.valid:
        raise ValueError("transition model must be valid")
    initial = int(initial_law_index)
    if not 0 <= initial < transition_model.law_count:
        raise ValueError("initial_law_index is out of range")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    enumeration = _enumerate_code_actions(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    count = len(candidates) ** periods
    if count > max_sequences:
        raise ValueError("open-loop code-sequence space exceeds configured cap")

    values: list[Fraction] = []
    paths: list[tuple[int, ...]] = []
    sequences: list[tuple[int, ...]] = []
    for sequence in product(range(len(candidates)), repeat=periods):
        value, path = _open_loop_sequence_value(
            transition_model,
            candidates,
            sequence,
            initial,
            penalty,
        )
        sequences.append(tuple(sequence))
        values.append(value)
        paths.append(path)
    best = min(values)
    best_positions = [index for index, value in enumerate(values) if value == best]
    selected_position = min(
        best_positions,
        key=lambda index: (
            sum(
                left != right
                for left, right in zip(sequences[index], sequences[index][1:])
            ),
            tuple(candidates[code].scenario_costs for code in sequences[index]),
            sequences[index],
        ),
    )
    selected_sequence = sequences[selected_position]
    result = OpenLoopDynamicCodeCertificate(
        graph,
        transition_model,
        initial,
        periods,
        penalty,
        enumeration,
        selected_sequence,
        tuple(candidates[index] for index in selected_sequence),
        best,
        paths[selected_position],
        tuple(values),
        count,
        max_sequences,
    )
    if not result.valid:
        raise AssertionError("open-loop dynamic code certificate failed validation")
    return result


@dataclass(frozen=True)
class FeedbackDynamicCodeCertificate:
    graph: ConfusionGraph
    transition_model: FiniteLawTransitionModel
    initial_law_index: int
    horizon: int
    switching_penalty: Fraction
    enumeration: RobustCandidateEnumeration
    value_tables: tuple[tuple[tuple[Fraction, ...], ...], ...]
    policy_tables: tuple[tuple[tuple[int, ...], ...], ...]
    successor_tables: tuple[tuple[tuple[int, ...], ...], ...]
    initial_value: Fraction
    adversarial_path: tuple[int, ...]
    selected_codes: tuple[int, ...]

    @property
    def valid(self) -> bool:
        model = self.transition_model
        candidates = self.enumeration.candidates
        code_count = len(candidates)
        sentinel = code_count
        if (
            not model.valid
            or self.graph.vertex_count != model.source_state_count
            or self.horizon < 1
            or not 0 <= self.initial_law_index < model.law_count
            or len(self.value_tables) != self.horizon
            or len(self.policy_tables) != self.horizon
            or len(self.successor_tables) != self.horizon
            or len(self.adversarial_path) != self.horizon
            or len(self.selected_codes) != self.horizon
            or self.adversarial_path[0] != self.initial_law_index
        ):
            return False
        for period in range(self.horizon):
            if (
                len(self.value_tables[period]) != model.law_count
                or len(self.policy_tables[period]) != model.law_count
                or len(self.successor_tables[period]) != model.law_count
            ):
                return False
            for law_index in range(model.law_count):
                if (
                    len(self.value_tables[period][law_index]) != code_count + 1
                    or len(self.policy_tables[period][law_index]) != code_count + 1
                    or len(self.successor_tables[period][law_index]) != code_count + 1
                ):
                    return False
                for previous in range(code_count + 1):
                    chosen = self.policy_tables[period][law_index][previous]
                    if not 0 <= chosen < code_count:
                        return False
                    stage = _stage_cost(
                        model.laws[law_index],
                        candidates[chosen],
                        previous,
                        chosen,
                        self.switching_penalty,
                        sentinel,
                    )
                    if period == self.horizon - 1:
                        expected = stage
                        if self.successor_tables[period][law_index][previous] != -1:
                            return False
                    else:
                        successor = self.successor_tables[period][law_index][previous]
                        if successor not in model.successors[law_index]:
                            return False
                        continuation = self.value_tables[period + 1][successor][chosen]
                        expected = stage + continuation
                        if continuation != max(
                            self.value_tables[period + 1][candidate_successor][chosen]
                            for candidate_successor in model.successors[law_index]
                        ):
                            return False
                    if self.value_tables[period][law_index][previous] != expected:
                        return False
                    alternatives = []
                    for code_index, candidate in enumerate(candidates):
                        alternative_stage = _stage_cost(
                            model.laws[law_index],
                            candidate,
                            previous,
                            code_index,
                            self.switching_penalty,
                            sentinel,
                        )
                        if period == self.horizon - 1:
                            alternatives.append(alternative_stage)
                        else:
                            alternatives.append(
                                alternative_stage
                                + max(
                                    self.value_tables[period + 1][successor][code_index]
                                    for successor in model.successors[law_index]
                                )
                            )
                    if expected != min(alternatives):
                        return False
        if self.initial_value != self.value_tables[0][self.initial_law_index][sentinel]:
            return False
        law = self.initial_law_index
        previous = sentinel
        path = [law]
        codes = []
        for period in range(self.horizon):
            code = self.policy_tables[period][law][previous]
            codes.append(code)
            if period < self.horizon - 1:
                law = self.successor_tables[period][law][previous]
                path.append(law)
            previous = code
        return tuple(path) == self.adversarial_path and tuple(codes) == self.selected_codes


def exact_feedback_dynamic_code(
    graph: ConfusionGraph,
    transition_model: FiniteLawTransitionModel,
    initial_law_index: int,
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> FeedbackDynamicCodeCertificate:
    if graph.vertex_count != transition_model.source_state_count:
        raise ValueError("graph and law-state dimensions differ")
    if not transition_model.valid:
        raise ValueError("transition model must be valid")
    initial = int(initial_law_index)
    if not 0 <= initial < transition_model.law_count:
        raise ValueError("initial_law_index is out of range")
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")

    enumeration = _enumerate_code_actions(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    code_count = len(candidates)
    sentinel = code_count
    values: list[tuple[tuple[Fraction, ...], ...]] = [tuple() for _ in range(periods)]
    policies: list[tuple[tuple[int, ...], ...]] = [tuple() for _ in range(periods)]
    successors: list[tuple[tuple[int, ...], ...]] = [tuple() for _ in range(periods)]

    for period in range(periods - 1, -1, -1):
        period_values: list[tuple[Fraction, ...]] = []
        period_policies: list[tuple[int, ...]] = []
        period_successors: list[tuple[int, ...]] = []
        for law_index, law in enumerate(transition_model.laws):
            law_values: list[Fraction] = []
            law_policies: list[int] = []
            law_successors: list[int] = []
            for previous in range(code_count + 1):
                options: list[tuple[Fraction, int, int]] = []
                for code_index, candidate in enumerate(candidates):
                    stage = _stage_cost(
                        law,
                        candidate,
                        previous,
                        code_index,
                        penalty,
                        sentinel,
                    )
                    if period == periods - 1:
                        options.append((stage, code_index, -1))
                    else:
                        successor_values = tuple(
                            (values[period + 1][successor][code_index], successor)
                            for successor in transition_model.successors[law_index]
                        )
                        worst = max(value for value, _ in successor_values)
                        witness = min(
                            successor
                            for value, successor in successor_values
                            if value == worst
                        )
                        options.append((stage + worst, code_index, witness))
                best_value = min(value for value, _, _ in options)
                best_options = tuple(option for option in options if option[0] == best_value)
                selected = min(
                    best_options,
                    key=lambda option: (
                        previous != sentinel and previous != option[1],
                        candidates[option[1]].scenario_costs,
                        option[1],
                        option[2],
                    ),
                )
                law_values.append(selected[0])
                law_policies.append(selected[1])
                law_successors.append(selected[2])
            period_values.append(tuple(law_values))
            period_policies.append(tuple(law_policies))
            period_successors.append(tuple(law_successors))
        values[period] = tuple(period_values)
        policies[period] = tuple(period_policies)
        successors[period] = tuple(period_successors)

    law = initial
    previous = sentinel
    path = [law]
    selected_codes = []
    for period in range(periods):
        code = policies[period][law][previous]
        selected_codes.append(code)
        if period < periods - 1:
            law = successors[period][law][previous]
            path.append(law)
        previous = code

    result = FeedbackDynamicCodeCertificate(
        graph,
        transition_model,
        initial,
        periods,
        penalty,
        enumeration,
        tuple(values),
        tuple(policies),
        tuple(successors),
        values[0][initial][sentinel],
        tuple(path),
        tuple(selected_codes),
    )
    if not result.valid:
        raise AssertionError("feedback dynamic code certificate failed validation")
    return result


@dataclass(frozen=True)
class ObservationValueCertificate:
    open_loop: OpenLoopDynamicCodeCertificate
    feedback: FeedbackDynamicCodeCertificate

    @property
    def feedback_gain(self) -> Fraction:
        return self.open_loop.selected_value - self.feedback.initial_value

    @property
    def valid(self) -> bool:
        return (
            self.open_loop.valid
            and self.feedback.valid
            and self.open_loop.graph == self.feedback.graph
            and self.open_loop.transition_model == self.feedback.transition_model
            and self.open_loop.initial_law_index == self.feedback.initial_law_index
            and self.open_loop.horizon == self.feedback.horizon
            and self.open_loop.switching_penalty == self.feedback.switching_penalty
            and self.feedback_gain >= 0
        )


def exact_observation_value(
    graph: ConfusionGraph,
    transition_model: FiniteLawTransitionModel,
    initial_law_index: int,
    horizon: int,
    *,
    switching_penalty: RationalInput = 0,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
    max_sequences: int = 100_000,
) -> ObservationValueCertificate:
    common = dict(
        switching_penalty=switching_penalty,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    open_loop = exact_open_loop_dynamic_code(
        graph,
        transition_model,
        initial_law_index,
        horizon,
        max_sequences=max_sequences,
        **common,
    )
    feedback = exact_feedback_dynamic_code(
        graph,
        transition_model,
        initial_law_index,
        horizon,
        **common,
    )
    result = ObservationValueCertificate(open_loop, feedback)
    if not result.valid:
        raise AssertionError("observation-value certificate failed validation")
    return result
