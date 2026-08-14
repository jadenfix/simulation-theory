"""Finite stochastic future laws, predictive covers, and network bounds.

This module closes a gap left by packing-only lower bounds.

A hidden record x and a future query q induce a categorical law P(.|x,q).
Two records are exactly predictively equivalent when all of those conditional
laws agree.  Under an exogenous query schedule w, their joint future-law total
variation is

    TV(P_x, P_u) = sum_q w_q TV(P(.|x,q), P(.|u,q)).

For epsilon-approximate prediction, two finite metric quantities bracket the
number M_epsilon of predictive states:

    packing_{>2 epsilon} <= M_epsilon <= target_center_cover_epsilon.

The lower bound permits arbitrary predictor laws.  The upper bound is
constructive but restricts centers to target laws already present in the
family.  Sending the selected cover-center index through a one-sink causal
network gives an explicit approximate renderer whenever the min-cut can carry
that index.

For a one-query Bernoulli family, arbitrary centers can be optimized exactly.
The TV metric is |p-u|, and greedy interval covering gives the exact minimum
number of epsilon-accurate predictor states.  This exposes why a target-centered
cover can be conservative: p=0 and p=1 need two target centers at epsilon=1/2,
but the arbitrary center p=1/2 covers both.

These are internal predictive-representation and communication results for
declared finite stochastic laws.  They are not evidence for simulation and do
not turn model bits, qubits, or network capacities into parent-universe
hardware, energy, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf, isfinite, log, sqrt
from typing import Hashable, Mapping, Sequence

from .predictive_networks import (
    CausalCapacityNetwork,
    FiniteQueryFamily,
    RoutedPath,
)

Record = Hashable
Outcome = Hashable
CategoricalLaw = tuple[float, ...]
QueryLawTable = tuple[CategoricalLaw, ...]


def _ceil_log2_integer(value: int) -> int:
    integer = int(value)
    if integer != value or integer < 1:
        raise ValueError("value must be a positive integer")
    return 0 if integer == 1 else (integer - 1).bit_length()


def _validate_nonnegative_integer(value: int, *, name: str) -> int:
    integer = int(value)
    if integer != value or integer < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return integer


def _validate_epsilon(epsilon: float) -> float:
    value = float(epsilon)
    if value < 0.0:
        raise ValueError("epsilon must be nonnegative")
    return value


def _validate_query_weights(
    query_count: int,
    weights: Sequence[float] | None,
) -> tuple[float, ...]:
    if weights is None:
        return tuple(1.0 / query_count for _ in range(query_count))
    values = tuple(float(weight) for weight in weights)
    if len(values) != query_count:
        raise ValueError("one query weight is required per query")
    if any(not isfinite(weight) or weight < 0.0 for weight in values):
        raise ValueError("query weights must be finite and nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("query weights must sum to one")
    return values


def _normalize_law(
    probabilities: Sequence[float],
    expected_outcomes: int,
    *,
    tolerance: float = 1e-12,
) -> CategoricalLaw:
    values = tuple(float(probability) for probability in probabilities)
    if len(values) != expected_outcomes:
        raise ValueError("categorical law length does not match outcome space")
    if any(not isfinite(value) or value < 0.0 for value in values):
        raise ValueError("categorical probabilities must be finite and nonnegative")
    total = sum(values)
    if abs(total - 1.0) > tolerance:
        raise ValueError("categorical probabilities must sum to one")
    return tuple(value / total for value in values)


@dataclass(frozen=True)
class FiniteStochasticQueryFamily:
    """Finite records and categorical future laws for every query."""

    records: tuple[Record, ...]
    query_names: tuple[str, ...]
    outcome_spaces: tuple[tuple[Outcome, ...], ...]
    conditional_laws: tuple[QueryLawTable, ...]

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("at least one record is required")
        try:
            unique_records = len(set(self.records))
        except TypeError as error:
            raise ValueError("records must be unique and hashable") from error
        if unique_records != len(self.records):
            raise ValueError("records must be unique and hashable")
        if not self.query_names or len(set(self.query_names)) != len(self.query_names):
            raise ValueError("query names must be nonempty and unique")
        if len(self.outcome_spaces) != len(self.query_names):
            raise ValueError("one outcome space is required per query")
        canonical_outcomes: list[tuple[Outcome, ...]] = []
        for outcomes in self.outcome_spaces:
            supplied = tuple(outcomes)
            if not supplied:
                raise ValueError("outcome spaces must be nonempty")
            try:
                if len(set(supplied)) != len(supplied):
                    raise ValueError("outcomes must be unique and hashable")
            except TypeError as error:
                raise ValueError("outcomes must be unique and hashable") from error
            canonical_outcomes.append(supplied)
        if len(self.conditional_laws) != len(self.records):
            raise ValueError("one query-law table is required per record")

        canonical_tables: list[QueryLawTable] = []
        for table in self.conditional_laws:
            if len(table) != len(self.query_names):
                raise ValueError("one categorical law is required per query")
            canonical_tables.append(
                tuple(
                    _normalize_law(law, len(outcomes))
                    for law, outcomes in zip(table, canonical_outcomes)
                )
            )
        object.__setattr__(self, "outcome_spaces", tuple(canonical_outcomes))
        object.__setattr__(self, "conditional_laws", tuple(canonical_tables))

    @classmethod
    def from_deterministic(
        cls,
        family: FiniteQueryFamily,
    ) -> "FiniteStochasticQueryFamily":
        outcome_spaces: list[tuple[Outcome, ...]] = []
        for query_index in range(family.query_count):
            seen: list[Outcome] = []
            for signature in family.signatures:
                outcome = signature[query_index]
                if outcome not in seen:
                    seen.append(outcome)
            outcome_spaces.append(tuple(seen))

        tables: list[QueryLawTable] = []
        for signature in family.signatures:
            query_laws: list[CategoricalLaw] = []
            for outcome, space in zip(signature, outcome_spaces):
                query_laws.append(
                    tuple(1.0 if candidate == outcome else 0.0 for candidate in space)
                )
            tables.append(tuple(query_laws))
        return cls(
            family.records,
            family.query_names,
            tuple(outcome_spaces),
            tuple(tables),
        )

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def query_count(self) -> int:
        return len(self.query_names)

    def record_index(self, record: Record) -> int:
        try:
            return self.records.index(record)
        except ValueError as error:
            raise ValueError("record is not in the finite family") from error

    def laws(self, record: Record) -> QueryLawTable:
        return self.conditional_laws[self.record_index(record)]

    @property
    def exact_equivalence_classes(self) -> tuple[tuple[Record, ...], ...]:
        groups: dict[QueryLawTable, list[Record]] = {}
        for record, table in zip(self.records, self.conditional_laws):
            groups.setdefault(table, []).append(record)
        return tuple(tuple(group) for group in groups.values())

    @property
    def exact_class_count(self) -> int:
        return len(set(self.conditional_laws))

    @property
    def exact_predictive_bits(self) -> int:
        return _ceil_log2_integer(self.exact_class_count)

    def exact_class_label_map(self) -> dict[Record, int]:
        labels: dict[QueryLawTable, int] = {}
        result: dict[Record, int] = {}
        for record, table in zip(self.records, self.conditional_laws):
            result[record] = labels.setdefault(table, len(labels))
        return result

    def joint_law(
        self,
        record: Record,
        weights: Sequence[float] | None = None,
    ) -> dict[tuple[str, Outcome], float]:
        query_weights = _validate_query_weights(self.query_count, weights)
        result: dict[tuple[str, Outcome], float] = {}
        for name, outcomes, law, query_weight in zip(
            self.query_names,
            self.outcome_spaces,
            self.laws(record),
            query_weights,
        ):
            for outcome, probability in zip(outcomes, law):
                result[(name, outcome)] = query_weight * probability
        return result


def single_bernoulli_query_family(
    parameters: Sequence[float],
    labels: Sequence[Record] | None = None,
) -> FiniteStochasticQueryFamily:
    probabilities = tuple(float(parameter) for parameter in parameters)
    if not probabilities:
        raise ValueError("at least one Bernoulli parameter is required")
    if any(not isfinite(parameter) or not 0.0 <= parameter <= 1.0 for parameter in probabilities):
        raise ValueError("Bernoulli parameters must lie in [0,1]")
    records: tuple[Record, ...]
    if labels is None:
        records = tuple(range(len(probabilities)))
    else:
        records = tuple(labels)
        if len(records) != len(probabilities):
            raise ValueError("one label is required per Bernoulli parameter")
    tables = tuple(
        (((1.0 - parameter, parameter),))
        for parameter in probabilities
    )
    return FiniteStochasticQueryFamily(
        records,
        ("bernoulli",),
        ((0, 1),),
        tables,
    )


def categorical_total_variation(
    left: Sequence[float],
    right: Sequence[float],
) -> float:
    first = tuple(float(value) for value in left)
    second = tuple(float(value) for value in right)
    if len(first) != len(second) or not first:
        raise ValueError("categorical laws must have equal positive length")
    if any(value < 0.0 or not isfinite(value) for value in (*first, *second)):
        raise ValueError("categorical probabilities must be finite and nonnegative")
    if abs(sum(first) - 1.0) > 1e-12 or abs(sum(second) - 1.0) > 1e-12:
        raise ValueError("categorical probabilities must sum to one")
    return 0.5 * sum(abs(a - b) for a, b in zip(first, second))


def categorical_kl_nats(
    left: Sequence[float],
    right: Sequence[float],
) -> float:
    first = tuple(float(value) for value in left)
    second = tuple(float(value) for value in right)
    if len(first) != len(second) or not first:
        raise ValueError("categorical laws must have equal positive length")
    if any(value < 0.0 or not isfinite(value) for value in (*first, *second)):
        raise ValueError("categorical probabilities must be finite and nonnegative")
    if abs(sum(first) - 1.0) > 1e-12 or abs(sum(second) - 1.0) > 1e-12:
        raise ValueError("categorical probabilities must sum to one")
    divergence = 0.0
    for probability, reference in zip(first, second):
        if probability == 0.0:
            continue
        if reference == 0.0:
            return inf
        divergence += probability * log(probability / reference)
    return divergence


def weighted_query_total_variation(
    family: FiniteStochasticQueryFamily,
    left: Record,
    right: Record,
    weights: Sequence[float] | None = None,
) -> float:
    query_weights = _validate_query_weights(family.query_count, weights)
    return sum(
        query_weight * categorical_total_variation(first, second)
        for query_weight, first, second in zip(
            query_weights,
            family.laws(left),
            family.laws(right),
        )
    )


def worst_query_total_variation(
    family: FiniteStochasticQueryFamily,
    left: Record,
    right: Record,
) -> float:
    return max(
        categorical_total_variation(first, second)
        for first, second in zip(family.laws(left), family.laws(right))
    )


def weighted_query_kl_nats(
    family: FiniteStochasticQueryFamily,
    left: Record,
    right: Record,
    weights: Sequence[float] | None = None,
) -> float:
    query_weights = _validate_query_weights(family.query_count, weights)
    total = 0.0
    for query_weight, first, second in zip(
        query_weights,
        family.laws(left),
        family.laws(right),
    ):
        divergence = categorical_kl_nats(first, second)
        if divergence == inf and query_weight > 0.0:
            return inf
        total += query_weight * divergence
    return total


def pinsker_tv_upper_bound_from_weighted_kl(
    family: FiniteStochasticQueryFamily,
    left: Record,
    right: Record,
    weights: Sequence[float] | None = None,
) -> float:
    divergence = weighted_query_kl_nats(family, left, right, weights)
    return 1.0 if divergence == inf else min(1.0, sqrt(0.5 * divergence))


def _distance_matrix(
    family: FiniteStochasticQueryFamily,
    weights: Sequence[float] | None,
    *,
    worst_query: bool,
) -> tuple[tuple[float, ...], ...]:
    if not worst_query:
        _validate_query_weights(family.query_count, weights)
    elif weights is not None:
        raise ValueError("weights are not used with worst_query=True")
    matrix = [[0.0] * family.record_count for _ in range(family.record_count)]
    for left in range(family.record_count):
        for right in range(left + 1, family.record_count):
            distance = (
                worst_query_total_variation(
                    family,
                    family.records[left],
                    family.records[right],
                )
                if worst_query
                else weighted_query_total_variation(
                    family,
                    family.records[left],
                    family.records[right],
                    weights,
                )
            )
            matrix[left][right] = distance
            matrix[right][left] = distance
    return tuple(tuple(row) for row in matrix)


def maximum_stochastic_predictive_packing(
    family: FiniteStochasticQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    worst_query: bool = False,
    max_records: int = 28,
) -> tuple[Record, ...]:
    """Exact bounded maximum packing with pairwise distance > 2 epsilon."""

    tolerance = _validate_epsilon(epsilon)
    if family.record_count > max_records:
        raise ValueError(f"exact packing search capped at {max_records} records")
    distances = _distance_matrix(family, weights, worst_query=worst_query)
    adjacency = [0] * family.record_count
    for left in range(family.record_count):
        for right in range(left + 1, family.record_count):
            if distances[left][right] > 2.0 * tolerance:
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left

    best: tuple[int, ...] = ()

    def expand(chosen: tuple[int, ...], candidates: int) -> None:
        nonlocal best
        if len(chosen) + candidates.bit_count() <= len(best):
            return
        if not candidates:
            if len(chosen) > len(best):
                best = chosen
            return
        remaining = candidates
        while remaining:
            if len(chosen) + remaining.bit_count() <= len(best):
                return
            bit = remaining & -remaining
            vertex = bit.bit_length() - 1
            remaining ^= bit
            expand((*chosen, vertex), remaining & adjacency[vertex])
        if len(chosen) > len(best):
            best = chosen

    expand((), (1 << family.record_count) - 1)
    return tuple(family.records[index] for index in best)


def minimum_target_centered_cover(
    family: FiniteStochasticQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    worst_query: bool = False,
    max_records: int = 26,
) -> tuple[Record, ...]:
    """Exact minimum epsilon-cover whose centers are target laws in the family."""

    tolerance = _validate_epsilon(epsilon)
    count = family.record_count
    if count > max_records:
        raise ValueError(f"exact cover search capped at {max_records} records")
    distances = _distance_matrix(family, weights, worst_query=worst_query)
    coverage = []
    centers_for_point = [0] * count
    for center in range(count):
        mask = 0
        for point in range(count):
            if distances[center][point] <= tolerance + 1e-12:
                mask |= 1 << point
                centers_for_point[point] |= 1 << center
        coverage.append(mask)

    full = (1 << count) - 1

    uncovered = full
    greedy: list[int] = []
    while uncovered:
        center = max(
            range(count),
            key=lambda index: (coverage[index] & uncovered).bit_count(),
        )
        if not (coverage[center] & uncovered):
            raise AssertionError("every target must cover itself")
        greedy.append(center)
        uncovered &= ~coverage[center]
    best = tuple(greedy)

    def search(
        chosen: tuple[int, ...],
        uncovered_mask: int,
        available_mask: int,
    ) -> None:
        nonlocal best
        if not uncovered_mask:
            if len(chosen) < len(best):
                best = chosen
            return
        if len(chosen) >= len(best):
            return

        max_new = max(
            (
                (coverage[index] & uncovered_mask).bit_count()
                for index in range(count)
                if (available_mask >> index) & 1
            ),
            default=0,
        )
        if max_new == 0:
            return
        optimistic = ceil(uncovered_mask.bit_count() / max_new)
        if len(chosen) + optimistic >= len(best):
            return

        uncovered_points = [
            index for index in range(count) if (uncovered_mask >> index) & 1
        ]
        point = min(
            uncovered_points,
            key=lambda index: (
                centers_for_point[index] & available_mask
            ).bit_count(),
        )
        options = centers_for_point[point] & available_mask
        if not options:
            return

        tried = 0
        while options:
            bit = options & -options
            center = bit.bit_length() - 1
            options ^= bit
            tried |= bit
            search(
                (*chosen, center),
                uncovered_mask & ~coverage[center],
                available_mask & ~tried,
            )

    search((), full, full)
    return tuple(family.records[index] for index in best)


def target_centered_cover_assignment(
    family: FiniteStochasticQueryFamily,
    centers: Sequence[Record],
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    worst_query: bool = False,
) -> dict[Record, Record]:
    tolerance = _validate_epsilon(epsilon)
    supplied_centers = tuple(centers)
    if not supplied_centers:
        raise ValueError("at least one center is required")
    for center in supplied_centers:
        family.record_index(center)
    result: dict[Record, Record] = {}
    for record in family.records:
        for center in supplied_centers:
            distance = (
                worst_query_total_variation(family, record, center)
                if worst_query
                else weighted_query_total_variation(
                    family,
                    record,
                    center,
                    weights,
                )
            )
            if distance <= tolerance + 1e-12:
                result[record] = center
                break
        else:
            raise ValueError("supplied centers do not form an epsilon-cover")
    return result


@dataclass(frozen=True)
class PredictiveStateBracket:
    packing_size: int
    target_cover_size: int

    @property
    def lower_bits(self) -> int:
        return _ceil_log2_integer(self.packing_size)

    @property
    def target_cover_upper_bits(self) -> int:
        return _ceil_log2_integer(self.target_cover_size)


def stochastic_predictive_state_bracket(
    family: FiniteStochasticQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    worst_query: bool = False,
    max_records: int = 26,
) -> PredictiveStateBracket:
    packing = maximum_stochastic_predictive_packing(
        family,
        epsilon,
        weights,
        worst_query=worst_query,
        max_records=max_records,
    )
    cover = minimum_target_centered_cover(
        family,
        epsilon,
        weights,
        worst_query=worst_query,
        max_records=max_records,
    )
    if len(packing) > len(cover):
        raise AssertionError("packing lower bound exceeds constructive cover")
    return PredictiveStateBracket(len(packing), len(cover))


def exact_stochastic_network_units_required(
    family: FiniteStochasticQueryFamily,
    *,
    capacity_bits_per_unit: int = 1,
) -> int:
    multiplier = _validate_nonnegative_integer(
        capacity_bits_per_unit,
        name="capacity_bits_per_unit",
    )
    if multiplier < 1:
        raise ValueError("capacity_bits_per_unit must be positive")
    return ceil(family.exact_predictive_bits / multiplier)


def exact_stochastic_network_feasible(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteStochasticQueryFamily,
    *,
    capacity_bits_per_unit: int = 1,
) -> bool:
    required = exact_stochastic_network_units_required(
        family,
        capacity_bits_per_unit=capacity_bits_per_unit,
    )
    return network.min_cut_capacity(source, sink) >= required


@dataclass(frozen=True)
class ApproximateStochasticNetworkCertificate:
    packing: tuple[Record, ...]
    target_centers: tuple[Record, ...]
    assignment: Mapping[Record, Record]
    lower_units: int
    target_cover_upper_units: int
    min_cut_units: int
    status: str
    routes: tuple[RoutedPath, ...]

    @property
    def routed_units(self) -> int:
        return sum(route.units for route in self.routes)


def approximate_stochastic_network_certificate(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteStochasticQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    worst_query: bool = False,
    capacity_bits_per_unit: int = 1,
    max_records: int = 26,
) -> ApproximateStochasticNetworkCertificate:
    multiplier = _validate_nonnegative_integer(
        capacity_bits_per_unit,
        name="capacity_bits_per_unit",
    )
    if multiplier < 1:
        raise ValueError("capacity_bits_per_unit must be positive")
    packing = maximum_stochastic_predictive_packing(
        family,
        epsilon,
        weights,
        worst_query=worst_query,
        max_records=max_records,
    )
    centers = minimum_target_centered_cover(
        family,
        epsilon,
        weights,
        worst_query=worst_query,
        max_records=max_records,
    )
    assignment = target_centered_cover_assignment(
        family,
        centers,
        epsilon,
        weights,
        worst_query=worst_query,
    )
    lower_units = ceil(_ceil_log2_integer(len(packing)) / multiplier)
    upper_units = ceil(_ceil_log2_integer(len(centers)) / multiplier)
    minimum = network.min_cut_capacity(source, sink)
    if minimum < lower_units:
        status = "impossible"
        routes: tuple[RoutedPath, ...] = ()
    elif minimum >= upper_units:
        status = "constructively-feasible"
        routes = network.route_units(source, sink, upper_units)
    else:
        status = "unresolved"
        routes = ()
    return ApproximateStochasticNetworkCertificate(
        packing,
        centers,
        assignment,
        lower_units,
        upper_units,
        minimum,
        status,
        routes,
    )


def _validate_bernoulli_parameters(
    parameters: Sequence[float],
) -> tuple[float, ...]:
    values = tuple(float(parameter) for parameter in parameters)
    if not values:
        raise ValueError("at least one Bernoulli parameter is required")
    if any(not isfinite(value) or not 0.0 <= value <= 1.0 for value in values):
        raise ValueError("Bernoulli parameters must lie in [0,1]")
    return values


def bernoulli_minimax_center(
    parameters: Sequence[float],
) -> tuple[float, float]:
    values = _validate_bernoulli_parameters(parameters)
    lower = min(values)
    upper = max(values)
    center = 0.5 * (lower + upper)
    radius = 0.5 * (upper - lower)
    return center, radius


def optimal_bernoulli_cover_centers(
    parameters: Sequence[float],
    epsilon: float,
) -> tuple[float, ...]:
    """Exact minimum arbitrary-center TV cover for finite Bernoulli parameters."""

    values = tuple(sorted(_validate_bernoulli_parameters(parameters)))
    tolerance = _validate_epsilon(epsilon)
    centers: list[float] = []
    index = 0
    while index < len(values):
        leftmost = values[index]
        center = min(1.0, leftmost + tolerance)
        centers.append(center)
        right_edge = center + tolerance + 1e-12
        index += 1
        while index < len(values) and values[index] <= right_edge:
            index += 1
    return tuple(centers)


def optimal_bernoulli_cover_assignment(
    parameters: Sequence[float],
    centers: Sequence[float],
    epsilon: float,
) -> tuple[int, ...]:
    values = _validate_bernoulli_parameters(parameters)
    supplied = _validate_bernoulli_parameters(centers)
    tolerance = _validate_epsilon(epsilon)
    assignment: list[int] = []
    for value in values:
        for index, center in enumerate(supplied):
            if abs(value - center) <= tolerance + 1e-12:
                assignment.append(index)
                break
        else:
            raise ValueError("supplied Bernoulli centers do not cover all parameters")
    return tuple(assignment)


def optimal_bernoulli_state_count(
    parameters: Sequence[float],
    epsilon: float,
) -> int:
    return len(optimal_bernoulli_cover_centers(parameters, epsilon))


def optimal_bernoulli_network_units_required(
    parameters: Sequence[float],
    epsilon: float,
    *,
    capacity_bits_per_unit: int = 1,
) -> int:
    multiplier = _validate_nonnegative_integer(
        capacity_bits_per_unit,
        name="capacity_bits_per_unit",
    )
    if multiplier < 1:
        raise ValueError("capacity_bits_per_unit must be positive")
    states = optimal_bernoulli_state_count(parameters, epsilon)
    return ceil(_ceil_log2_integer(states) / multiplier)


def optimal_bernoulli_network_feasible(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    parameters: Sequence[float],
    epsilon: float,
    *,
    capacity_bits_per_unit: int = 1,
) -> bool:
    required = optimal_bernoulli_network_units_required(
        parameters,
        epsilon,
        capacity_bits_per_unit=capacity_bits_per_unit,
    )
    return network.min_cut_capacity(source, sink) >= required
