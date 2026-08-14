"""Certified bounds separating robust absolute cost from pathwise regret.

For a decision mixture x and path q, write C_x(q) for its expected cost and
O(q) for the path-specific comparator oracle. Pathwise regret is

    max_q [C_x(q) - O(q)],

not generally

    max_q C_x(q) - max_q O(q).

The two maxima may occur at different paths. More subtly, O(q) is a minimum of
affine comparator costs and is therefore concave piecewise linear. Its maximum
over a path polytope need not occur at a path vertex.

If the path polytope has vertices v_j, every feasible path is a convex
combination of them. Because every comparator cost is affine,

    max_q min_b C_b(q)
      = max_{lambda in simplex} min_b sum_j lambda_j C_b(v_j).

This is exactly the dual side of the finite rational zero-sum game whose rows
are path vertices and whose columns are comparators. The repository therefore
certifies the oracle maximum with a full primal-dual game receipt rather than
incorrectly taking the largest vertex oracle value.

If

    V_abs = min_x max_q C_x(q),
    O_min = min_q O(q),
    O_max = max_q O(q),

then deterministic and shared-randomness minimax regret satisfy

    V_abs - O_max <= R <= V_abs - O_min.

The module constructs exact rational absolute-cost and oracle-maximin games from
an already validated pathwise-regret certificate and checks both bounds. It
exists to prevent either a robust value gap or a vertex-only oracle calculation
from being misreported as dynamic regret.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .pathwise_regret import PathwiseRegretCertificate
from .robust_prior_codes import ExactZeroSumGameCertificate, solve_exact_zero_sum_game


@dataclass(frozen=True)
class RegretValueBoundsCertificate:
    regret: PathwiseRegretCertificate
    deterministic_absolute_decision_index: int
    deterministic_absolute_value: Fraction
    shared_absolute_game: ExactZeroSumGameCertificate
    oracle_minimum: Fraction
    oracle_max_game: ExactZeroSumGameCertificate

    @property
    def oracle_maximum(self) -> Fraction:
        return self.oracle_max_game.value

    @property
    def oracle_vertex_maximum(self) -> Fraction:
        return max(self.regret.oracle_costs)

    @property
    def oracle_interior_gain(self) -> Fraction:
        return self.oracle_maximum - self.oracle_vertex_maximum

    @property
    def deterministic_lower_bound(self) -> Fraction:
        return self.deterministic_absolute_value - self.oracle_maximum

    @property
    def deterministic_upper_bound(self) -> Fraction:
        return self.deterministic_absolute_value - self.oracle_minimum

    @property
    def shared_lower_bound(self) -> Fraction:
        return self.shared_absolute_game.value - self.oracle_maximum

    @property
    def shared_upper_bound(self) -> Fraction:
        return self.shared_absolute_game.value - self.oracle_minimum

    @property
    def deterministic_slack_above_value_gap(self) -> Fraction:
        return self.regret.deterministic_value - self.deterministic_lower_bound

    @property
    def shared_slack_above_value_gap(self) -> Fraction:
        return self.regret.shared_value - self.shared_lower_bound

    @property
    def valid(self) -> bool:
        if (
            not self.regret.valid
            or not self.shared_absolute_game.valid
            or not self.oracle_max_game.valid
            or self.shared_absolute_game.cost_matrix
            != self.regret.decision_cost_matrix
            or self.oracle_max_game.cost_matrix
            != self.regret.comparator_cost_matrix
            or not 0
            <= self.deterministic_absolute_decision_index
            < len(self.regret.decisions)
        ):
            return False
        worst_absolute = tuple(
            max(
                self.regret.decision_cost_matrix[vertex][decision]
                for vertex in range(len(self.regret.polytope.vertices))
            )
            for decision in range(len(self.regret.decisions))
        )
        expected_index = min(
            range(len(self.regret.decisions)),
            key=lambda index: (
                worst_absolute[index],
                self.regret.decisions[index].constant_cost,
                self.regret.decisions[index].label,
            ),
        )
        expected_oracle_minimum = min(
            value
            for row in self.regret.comparator_cost_matrix
            for value in row
        )
        return (
            self.deterministic_absolute_decision_index == expected_index
            and self.deterministic_absolute_value == worst_absolute[expected_index]
            and self.oracle_minimum == expected_oracle_minimum
            and self.oracle_maximum >= self.oracle_vertex_maximum
            and self.oracle_interior_gain >= 0
            and self.deterministic_lower_bound
            <= self.regret.deterministic_value
            <= self.deterministic_upper_bound
            and self.shared_lower_bound
            <= self.regret.shared_value
            <= self.shared_upper_bound
            and self.deterministic_slack_above_value_gap >= 0
            and self.shared_slack_above_value_gap >= 0
        )


def exact_regret_value_bounds(
    regret: PathwiseRegretCertificate,
    *,
    max_game_bases: int = 2_000_000,
) -> RegretValueBoundsCertificate:
    """Return exact absolute-cost and oracle-maximin bounds on regret."""

    if not regret.valid:
        raise ValueError("pathwise regret certificate must be valid")
    worst_absolute = tuple(
        max(
            regret.decision_cost_matrix[vertex][decision]
            for vertex in range(len(regret.polytope.vertices))
        )
        for decision in range(len(regret.decisions))
    )
    index = min(
        range(len(regret.decisions)),
        key=lambda decision: (
            worst_absolute[decision],
            regret.decisions[decision].constant_cost,
            regret.decisions[decision].label,
        ),
    )
    shared_absolute = solve_exact_zero_sum_game(
        regret.decision_cost_matrix,
        max_bases=max_game_bases,
    )
    oracle_max_game = solve_exact_zero_sum_game(
        regret.comparator_cost_matrix,
        max_bases=max_game_bases,
    )
    oracle_minimum = min(
        value
        for row in regret.comparator_cost_matrix
        for value in row
    )
    result = RegretValueBoundsCertificate(
        regret,
        index,
        worst_absolute[index],
        shared_absolute,
        oracle_minimum,
        oracle_max_game,
    )
    if not result.valid:
        raise AssertionError("regret-versus-value bound certificate failed")
    return result
