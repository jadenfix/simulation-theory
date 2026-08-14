"""Exact pathwise regret under bounded source-law drift.

Robust absolute cost and regret are different decision criteria.  For one
precommitted decision ``a`` and one feasible source-law path ``q``, let

    C_a(q) = constant_a + sum_t q_t . g_{a,t}.

Given a finite comparator class B, the pathwise oracle is

    O_B(q) = min_{b in B} C_b(q),

and the regret of ``a`` is

    R_a(q) = C_a(q) - O_B(q)
           = max_{b in B} [C_a(q) - C_b(q)].

For a fixed decision, regret is therefore a convex piecewise-linear function of
the complete path.  Its maximum over the exact bounded-TV path polytope occurs
at a path vertex.  The same remains true for a source-independent shared
mixture of decisions because the mixture changes only the affine decision cost.
Consequently deterministic and shared-randomness minimax regret reduce exactly
to finite rational games over path vertices.

A coding wrapper builds the decision and comparator classes from complete
bounded deterministic zero-error prefix-code sequences.  Candidate and
comparator switch budgets are separated, but the candidate class must be a
subset of the comparator class so regret is nonnegative path by path.  One
common rational switching penalty is charged to both classes.

All results are finite, exact-rational, open-loop, and internal to the declared
source/cost model.  They do not optimize a causal feedback policy, do not infer
a physical reconfiguration cost, and are not evidence that reality is
simulated.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence

from .confusion_graphs import ConfusionGraph
from .coupled_drift_sequences import (
    CostVector,
    Distribution,
    DriftPathPolytope,
    ExactInput,
    Path,
    _fraction,
    _validate_eta,
    _validate_prior,
    enumerate_drift_path_polytope,
)
from .robust_prior_codes import (
    ExactZeroSumGameCertificate,
    RobustCandidateEnumeration,
    RobustCodeCandidate,
    enumerate_robust_code_candidates,
    solve_exact_zero_sum_game,
)


@dataclass(frozen=True)
class AffinePathDecision:
    """One precommitted affine cost functional on a source-law path."""

    label: str
    period_costs: tuple[CostVector, ...]
    constant_cost: Fraction = Fraction(0)

    @property
    def horizon(self) -> int:
        return len(self.period_costs)

    @property
    def state_count(self) -> int:
        return len(self.period_costs[0]) if self.period_costs else 0

    def valid_for(self, state_count: int, horizon: int) -> bool:
        return (
            bool(self.label)
            and self.horizon == horizon
            and horizon >= 1
            and self.state_count == state_count
            and all(len(cost) == state_count for cost in self.period_costs)
        )


def affine_path_decision(
    label: str,
    period_costs: Sequence[Sequence[ExactInput]],
    *,
    constant_cost: ExactInput = 0,
) -> AffinePathDecision:
    """Construct one exact-rational affine path decision."""

    costs = tuple(
        tuple(_fraction(value, name="period state cost") for value in period)
        for period in period_costs
    )
    if not costs:
        raise ValueError("at least one period cost vector is required")
    state_count = len(costs[0])
    if state_count < 1 or any(len(cost) != state_count for cost in costs):
        raise ValueError("period cost vectors must have one common positive size")
    decision = AffinePathDecision(
        str(label),
        costs,
        _fraction(constant_cost, name="constant decision cost"),
    )
    if not decision.valid_for(state_count, len(costs)):
        raise ValueError("invalid affine path decision")
    return decision


def path_decision_cost(decision: AffinePathDecision, path: Path) -> Fraction:
    """Evaluate one affine decision on one complete path."""

    if not decision.valid_for(
        len(path[0]) if path else 0,
        len(path),
    ):
        raise ValueError("decision and path dimensions differ")
    return decision.constant_cost + sum(
        (
            sum(
                (
                    probability * cost
                    for probability, cost in zip(distribution, period_cost)
                ),
                Fraction(0),
            )
            for distribution, period_cost in zip(path, decision.period_costs)
        ),
        Fraction(0),
    )


def _decision_identity(decision: AffinePathDecision) -> tuple[object, ...]:
    return decision.period_costs, decision.constant_cost


def _validate_decision_family(
    decisions: Sequence[AffinePathDecision],
    *,
    state_count: int,
    horizon: int,
    family_name: str,
) -> tuple[AffinePathDecision, ...]:
    supplied = tuple(decisions)
    if not supplied:
        raise ValueError(f"{family_name} cannot be empty")
    if any(not decision.valid_for(state_count, horizon) for decision in supplied):
        raise ValueError(f"{family_name} contains a dimensionally invalid decision")
    if len({decision.label for decision in supplied}) != len(supplied):
        raise ValueError(f"{family_name} decision labels must be unique")
    if len({_decision_identity(decision) for decision in supplied}) != len(supplied):
        raise ValueError(f"{family_name} contains duplicate affine decisions")
    return supplied


@dataclass(frozen=True)
class PathwiseRegretCertificate:
    """Exact deterministic and shared minimax regret over one path polytope."""

    polytope: DriftPathPolytope
    decisions: tuple[AffinePathDecision, ...]
    comparators: tuple[AffinePathDecision, ...]
    decision_cost_matrix: tuple[tuple[Fraction, ...], ...]
    comparator_cost_matrix: tuple[tuple[Fraction, ...], ...]
    oracle_costs: tuple[Fraction, ...]
    oracle_comparator_indices: tuple[int, ...]
    regret_matrix: tuple[tuple[Fraction, ...], ...]
    deterministic_decision_index: int
    deterministic_value: Fraction
    deterministic_worst_vertex_indices: tuple[int, ...]
    shared_game: ExactZeroSumGameCertificate

    @property
    def deterministic_decision(self) -> AffinePathDecision:
        return self.decisions[self.deterministic_decision_index]

    @property
    def shared_value(self) -> Fraction:
        return self.shared_game.value

    @property
    def randomization_gain(self) -> Fraction:
        return self.deterministic_value - self.shared_value

    @property
    def shared_decision_support(self) -> tuple[int, ...]:
        return self.shared_game.code_support

    @property
    def least_favorable_vertex_support(self) -> tuple[int, ...]:
        return self.shared_game.scenario_support

    @property
    def comparator_contains_decisions(self) -> bool:
        comparator_identities = {
            _decision_identity(comparator) for comparator in self.comparators
        }
        return all(
            _decision_identity(decision) in comparator_identities
            for decision in self.decisions
        )

    @property
    def valid(self) -> bool:
        if (
            not self.polytope.valid
            or not self.decisions
            or not self.comparators
            or not self.comparator_contains_decisions
            or not 0 <= self.deterministic_decision_index < len(self.decisions)
            or not self.shared_game.valid
            or self.shared_game.cost_matrix != self.regret_matrix
        ):
            return False

        vertices = self.polytope.paths
        expected_decision_costs = tuple(
            tuple(path_decision_cost(decision, path) for decision in self.decisions)
            for path in vertices
        )
        expected_comparator_costs = tuple(
            tuple(
                path_decision_cost(comparator, path)
                for comparator in self.comparators
            )
            for path in vertices
        )
        expected_oracle_indices = tuple(
            min(
                range(len(self.comparators)),
                key=lambda index: (
                    expected_comparator_costs[vertex][index],
                    self.comparators[index].constant_cost,
                    self.comparators[index].label,
                ),
            )
            for vertex in range(len(vertices))
        )
        expected_oracle_costs = tuple(
            expected_comparator_costs[vertex][index]
            for vertex, index in enumerate(expected_oracle_indices)
        )
        expected_regrets = tuple(
            tuple(
                expected_decision_costs[vertex][decision]
                - expected_oracle_costs[vertex]
                for decision in range(len(self.decisions))
            )
            for vertex in range(len(vertices))
        )
        if any(value < 0 for row in expected_regrets for value in row):
            return False

        worst_by_decision = tuple(
            max(expected_regrets[vertex][decision] for vertex in range(len(vertices)))
            for decision in range(len(self.decisions))
        )
        deterministic_index = min(
            range(len(self.decisions)),
            key=lambda index: (
                worst_by_decision[index],
                self.decisions[index].constant_cost,
                self.decisions[index].label,
            ),
        )
        worst_vertices = tuple(
            vertex
            for vertex in range(len(vertices))
            if expected_regrets[vertex][deterministic_index]
            == worst_by_decision[deterministic_index]
        )
        return (
            self.decision_cost_matrix == expected_decision_costs
            and self.comparator_cost_matrix == expected_comparator_costs
            and self.oracle_comparator_indices == expected_oracle_indices
            and self.oracle_costs == expected_oracle_costs
            and self.regret_matrix == expected_regrets
            and self.deterministic_decision_index == deterministic_index
            and self.deterministic_value == worst_by_decision[deterministic_index]
            and self.deterministic_worst_vertex_indices == worst_vertices
            and self.shared_value <= self.deterministic_value
            and self.randomization_gain >= 0
        )


def exact_pathwise_regret_game(
    nominal_prior: Sequence[ExactInput],
    drift_per_step: ExactInput,
    decisions: Sequence[AffinePathDecision],
    comparators: Sequence[AffinePathDecision] | None = None,
    *,
    max_path_bases: int = 2_000_000,
    max_game_bases: int = 2_000_000,
) -> PathwiseRegretCertificate:
    """Solve deterministic and shared minimax regret over a continuous path set.

    The comparator family defaults to the decision family.  Every decision must
    also be present in the comparator family, ensuring pathwise regret is
    nonnegative.  The source-law path is selected after the deterministic
    decision or source-independent shared mixture is committed.
    """

    prior = _validate_prior(nominal_prior)
    supplied_decisions = tuple(decisions)
    if not supplied_decisions:
        raise ValueError("at least one decision is required")
    horizon = supplied_decisions[0].horizon
    decision_family = _validate_decision_family(
        supplied_decisions,
        state_count=len(prior),
        horizon=horizon,
        family_name="decision family",
    )
    comparator_family = _validate_decision_family(
        decision_family if comparators is None else comparators,
        state_count=len(prior),
        horizon=horizon,
        family_name="comparator family",
    )
    comparator_identities = {
        _decision_identity(comparator) for comparator in comparator_family
    }
    if any(
        _decision_identity(decision) not in comparator_identities
        for decision in decision_family
    ):
        raise ValueError("the comparator family must contain every decision")

    polytope = enumerate_drift_path_polytope(
        prior,
        drift_per_step,
        horizon,
        max_bases=max_path_bases,
    )
    decision_costs = tuple(
        tuple(path_decision_cost(decision, path) for decision in decision_family)
        for path in polytope.paths
    )
    comparator_costs = tuple(
        tuple(
            path_decision_cost(comparator, path)
            for comparator in comparator_family
        )
        for path in polytope.paths
    )
    oracle_indices = tuple(
        min(
            range(len(comparator_family)),
            key=lambda index: (
                comparator_costs[vertex][index],
                comparator_family[index].constant_cost,
                comparator_family[index].label,
            ),
        )
        for vertex in range(len(polytope.vertices))
    )
    oracle_costs = tuple(
        comparator_costs[vertex][index]
        for vertex, index in enumerate(oracle_indices)
    )
    regret_matrix = tuple(
        tuple(
            decision_costs[vertex][decision] - oracle_costs[vertex]
            for decision in range(len(decision_family))
        )
        for vertex in range(len(polytope.vertices))
    )
    if any(value < 0 for row in regret_matrix for value in row):
        raise AssertionError("comparator containment did not imply nonnegative regret")

    worst_by_decision = tuple(
        max(regret_matrix[vertex][decision] for vertex in range(len(polytope.vertices)))
        for decision in range(len(decision_family))
    )
    deterministic_index = min(
        range(len(decision_family)),
        key=lambda index: (
            worst_by_decision[index],
            decision_family[index].constant_cost,
            decision_family[index].label,
        ),
    )
    worst_vertices = tuple(
        vertex
        for vertex in range(len(polytope.vertices))
        if regret_matrix[vertex][deterministic_index]
        == worst_by_decision[deterministic_index]
    )
    game = solve_exact_zero_sum_game(
        regret_matrix,
        max_bases=max_game_bases,
    )
    result = PathwiseRegretCertificate(
        polytope,
        decision_family,
        comparator_family,
        decision_costs,
        comparator_costs,
        oracle_costs,
        oracle_indices,
        regret_matrix,
        deterministic_index,
        worst_by_decision[deterministic_index],
        worst_vertices,
        game,
    )
    if not result.valid:
        raise AssertionError("pathwise regret certificate failed validation")
    return result


def _simplex_vertices(state_count: int) -> tuple[Distribution, ...]:
    return tuple(
        tuple(
            Fraction(1) if state == vertex else Fraction(0)
            for state in range(state_count)
        )
        for vertex in range(state_count)
    )


def sequence_switch_count(sequence: Sequence[int]) -> int:
    supplied = tuple(int(index) for index in sequence)
    return sum(left != right for left, right in zip(supplied, supplied[1:]))


def bounded_code_sequences(
    candidate_count: int,
    horizon: int,
    max_switches: int,
    *,
    max_sequences: int = 500_000,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate every sequence below an exact switch-count budget."""

    count = int(candidate_count)
    periods = int(horizon)
    budget = int(max_switches)
    cap = int(max_sequences)
    if count < 1 or periods < 1 or cap < 1:
        raise ValueError("candidate count, horizon, and cap must be positive")
    if not 0 <= budget <= periods - 1:
        raise ValueError("max_switches must lie in [0,horizon-1]")
    accepted: list[tuple[int, ...]] = []
    examined = 0
    for sequence in product(range(count), repeat=periods):
        examined += 1
        if sequence_switch_count(sequence) > budget:
            continue
        accepted.append(sequence)
        if len(accepted) > cap:
            raise ValueError("bounded code-sequence family exceeds configured cap")
    if not accepted:
        raise AssertionError("every positive candidate family has a static sequence")
    return tuple(accepted)


def _candidate_period_cost(candidate: RobustCodeCandidate) -> CostVector:
    return tuple(Fraction(value) for value in candidate.scenario_costs)


def _sequence_decision(
    sequence: tuple[int, ...],
    candidates: tuple[RobustCodeCandidate, ...],
    switching_penalty: Fraction,
    *,
    prefix: str,
) -> AffinePathDecision:
    return AffinePathDecision(
        f"{prefix}[{','.join(str(index) for index in sequence)}]",
        tuple(_candidate_period_cost(candidates[index]) for index in sequence),
        switching_penalty * sequence_switch_count(sequence),
    )


@dataclass(frozen=True)
class CodeSequenceRegretCertificate:
    graph: ConfusionGraph
    nominal_prior: Distribution
    drift_per_step: Fraction
    horizon: int
    switching_penalty: Fraction
    decision_max_switches: int
    comparator_max_switches: int
    enumeration: RobustCandidateEnumeration
    decision_sequences: tuple[tuple[int, ...], ...]
    comparator_sequences: tuple[tuple[int, ...], ...]
    regret: PathwiseRegretCertificate

    @property
    def deterministic_sequence(self) -> tuple[int, ...]:
        return self.decision_sequences[self.regret.deterministic_decision_index]

    @property
    def deterministic_regret(self) -> Fraction:
        return self.regret.deterministic_value

    @property
    def shared_regret(self) -> Fraction:
        return self.regret.shared_value

    @property
    def randomization_gain(self) -> Fraction:
        return self.regret.randomization_gain

    @property
    def valid(self) -> bool:
        candidates = self.enumeration.candidates
        expected_decisions = tuple(
            _sequence_decision(
                sequence,
                candidates,
                self.switching_penalty,
                prefix="decision",
            )
            for sequence in self.decision_sequences
        )
        expected_comparators = tuple(
            _sequence_decision(
                sequence,
                candidates,
                self.switching_penalty,
                prefix="comparator",
            )
            for sequence in self.comparator_sequences
        )
        return (
            self.graph.vertex_count == len(self.nominal_prior)
            and self.horizon >= 1
            and self.switching_penalty >= 0
            and 0 <= self.decision_max_switches <= self.comparator_max_switches
            <= self.horizon - 1
            and bool(candidates)
            and set(self.decision_sequences).issubset(self.comparator_sequences)
            and all(len(sequence) == self.horizon for sequence in self.decision_sequences)
            and all(len(sequence) == self.horizon for sequence in self.comparator_sequences)
            and all(
                sequence_switch_count(sequence) <= self.decision_max_switches
                for sequence in self.decision_sequences
            )
            and all(
                sequence_switch_count(sequence) <= self.comparator_max_switches
                for sequence in self.comparator_sequences
            )
            and self.regret.valid
            and self.regret.polytope.nominal_prior == self.nominal_prior
            and self.regret.polytope.drift_per_step == self.drift_per_step
            and self.regret.polytope.horizon == self.horizon
            and tuple(
                decision.period_costs for decision in self.regret.decisions
            )
            == tuple(decision.period_costs for decision in expected_decisions)
            and tuple(
                decision.constant_cost for decision in self.regret.decisions
            )
            == tuple(decision.constant_cost for decision in expected_decisions)
            and tuple(
                comparator.period_costs for comparator in self.regret.comparators
            )
            == tuple(comparator.period_costs for comparator in expected_comparators)
            and tuple(
                comparator.constant_cost for comparator in self.regret.comparators
            )
            == tuple(comparator.constant_cost for comparator in expected_comparators)
        )


def exact_code_sequence_regret(
    graph: ConfusionGraph,
    nominal_prior: Sequence[ExactInput],
    drift_per_step: ExactInput,
    horizon: int,
    *,
    switching_penalty: ExactInput = 0,
    decision_max_switches: int = 0,
    comparator_max_switches: int | None = None,
    max_sequences: int = 500_000,
    max_path_bases: int = 2_000_000,
    max_game_bases: int = 2_000_000,
    max_vertices: int = 8,
    max_partitions: int = 250_000,
    max_candidates: int = 500_000,
    max_prefix_assignments: int = 10_000_000,
    max_prefix_shapes: int = 100_000,
    max_dominance_pairs: int = 4_000_000,
) -> CodeSequenceRegretCertificate:
    """Solve exact pathwise regret for bounded zero-error code sequences.

    ``decision_max_switches`` controls the sequence selected before the source
    path.  ``comparator_max_switches`` controls the clairvoyant path-specific
    oracle and defaults to the decision budget.  The decision budget may not
    exceed the comparator budget.
    """

    prior = _validate_prior(nominal_prior)
    if len(prior) != graph.vertex_count:
        raise ValueError("graph and prior dimensions differ")
    eta = _validate_eta(drift_per_step)
    periods = int(horizon)
    if periods != horizon or periods < 1:
        raise ValueError("horizon must be a positive integer")
    penalty = _fraction(switching_penalty, name="switching_penalty")
    if penalty < 0:
        raise ValueError("switching_penalty must be nonnegative")
    decision_budget = int(decision_max_switches)
    comparator_budget = (
        decision_budget
        if comparator_max_switches is None
        else int(comparator_max_switches)
    )
    if not 0 <= decision_budget <= comparator_budget <= periods - 1:
        raise ValueError(
            "switch budgets must satisfy 0 <= decision <= comparator <= horizon-1"
        )

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
    decision_sequences = bounded_code_sequences(
        len(candidates),
        periods,
        decision_budget,
        max_sequences=max_sequences,
    )
    comparator_sequences = bounded_code_sequences(
        len(candidates),
        periods,
        comparator_budget,
        max_sequences=max_sequences,
    )
    decision_family = tuple(
        _sequence_decision(
            sequence,
            candidates,
            penalty,
            prefix="decision",
        )
        for sequence in decision_sequences
    )
    comparator_family = tuple(
        _sequence_decision(
            sequence,
            candidates,
            penalty,
            prefix="comparator",
        )
        for sequence in comparator_sequences
    )
    regret = exact_pathwise_regret_game(
        prior,
        eta,
        decision_family,
        comparator_family,
        max_path_bases=max_path_bases,
        max_game_bases=max_game_bases,
    )
    result = CodeSequenceRegretCertificate(
        graph,
        prior,
        eta,
        periods,
        penalty,
        decision_budget,
        comparator_budget,
        enumeration,
        decision_sequences,
        comparator_sequences,
        regret,
    )
    if not result.valid:
        raise AssertionError("code-sequence pathwise regret certificate failed")
    return result
