"""Exact arbitrary-center prediction for one-query ternary laws.

For probability vectors p and u in the three-outcome simplex, their coordinate
differences sum to zero.  For three zero-sum real numbers, half the L1 norm is
the largest absolute coordinate.  Therefore

    TV(p, u) = max_j |p_j-u_j|.

A set of ternary target laws has a common epsilon-accurate predictor exactly
when the coordinate intervals

    L_j = max(0, max_i p_ij - epsilon),
    U_j = min(1, min_i p_ij + epsilon)

satisfy L_j <= U_j and sum L_j <= 1 <= sum U_j.  Starting at L and
distributing the remaining mass within U constructs a center.

Enumerating all feasible target subsets and solving the resulting finite set
cover gives the exact minimum arbitrary-center predictive-state count.  This is
stronger than a target-centered cover: predictor centers may interpolate
between all supplied target laws.

The one-state minimax radius is also explicit.  It is the maximum of coordinate
half-ranges and two water-filling thresholds enforcing that the common box
intersects the simplex.

All results concern declared finite internal probability laws.  They are not
evidence for simulation and do not convert model bits, qubits, centers, or
network units into parent-universe hardware, energy, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from typing import Hashable, Mapping, Sequence

from .predictive_networks import CausalCapacityNetwork, RoutedPath
from .stochastic_predictive import (
    FiniteStochasticQueryFamily,
    maximum_stochastic_predictive_packing,
    minimum_target_centered_cover,
)

Record = Hashable
TernaryLaw = tuple[float, float, float]


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
    if not isfinite(value) or value < 0.0:
        raise ValueError("epsilon must be finite and nonnegative")
    return value


def _normalize_ternary_law(
    probabilities: Sequence[float],
    *,
    tolerance: float = 1e-12,
) -> TernaryLaw:
    values = tuple(float(probability) for probability in probabilities)
    if len(values) != 3:
        raise ValueError("ternary laws must contain exactly three probabilities")
    if any(not isfinite(value) or value < 0.0 for value in values):
        raise ValueError("ternary probabilities must be finite and nonnegative")
    total = sum(values)
    if abs(total - 1.0) > tolerance:
        raise ValueError("ternary probabilities must sum to one")
    normalized = tuple(value / total for value in values)
    return normalized  # type: ignore[return-value]


@dataclass(frozen=True)
class FiniteTernaryFamily:
    """Finite records carrying one three-outcome future probability law."""

    records: tuple[Record, ...]
    laws: tuple[TernaryLaw, ...]
    query_name: str = "ternary"

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("at least one record is required")
        try:
            unique_records = len(set(self.records))
        except TypeError as error:
            raise ValueError("records must be unique and hashable") from error
        if unique_records != len(self.records):
            raise ValueError("records must be unique and hashable")
        if len(self.laws) != len(self.records):
            raise ValueError("one ternary law is required per record")
        object.__setattr__(
            self,
            "laws",
            tuple(_normalize_ternary_law(law) for law in self.laws),
        )
        name = str(self.query_name)
        if not name:
            raise ValueError("query_name cannot be empty")
        object.__setattr__(self, "query_name", name)

    @classmethod
    def from_probabilities(
        cls,
        probabilities: Sequence[Sequence[float]],
        labels: Sequence[Record] | None = None,
        *,
        query_name: str = "ternary",
    ) -> "FiniteTernaryFamily":
        laws = tuple(_normalize_ternary_law(law) for law in probabilities)
        if not laws:
            raise ValueError("at least one ternary law is required")
        records: tuple[Record, ...] = (
            tuple(range(len(laws))) if labels is None else tuple(labels)
        )
        if len(records) != len(laws):
            raise ValueError("one label is required per ternary law")
        return cls(records, laws, query_name)

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def exact_class_count(self) -> int:
        return len(set(self.laws))

    @property
    def exact_predictive_bits(self) -> int:
        return _ceil_log2_integer(self.exact_class_count)

    def record_index(self, record: Record) -> int:
        try:
            return self.records.index(record)
        except ValueError as error:
            raise ValueError("record is not in the finite ternary family") from error

    def law(self, record: Record) -> TernaryLaw:
        return self.laws[self.record_index(record)]

    def to_stochastic_family(self) -> FiniteStochasticQueryFamily:
        return FiniteStochasticQueryFamily(
            self.records,
            (self.query_name,),
            ((0, 1, 2),),
            tuple((law,) for law in self.laws),
        )


def ternary_total_variation(
    left: Sequence[float],
    right: Sequence[float],
) -> float:
    """Exact three-outcome identity: TV is the maximum coordinate difference."""

    first = _normalize_ternary_law(left)
    second = _normalize_ternary_law(right)
    return max(abs(a - b) for a, b in zip(first, second))


def ternary_cover_bounds(
    laws: Sequence[Sequence[float]],
    epsilon: float,
) -> tuple[TernaryLaw, TernaryLaw] | None:
    """Return the box intersecting every epsilon-ball, or None if infeasible."""

    points = tuple(_normalize_ternary_law(law) for law in laws)
    if not points:
        raise ValueError("at least one target law is required")
    tolerance = _validate_epsilon(epsilon)
    maxima = tuple(max(point[index] for point in points) for index in range(3))
    minima = tuple(min(point[index] for point in points) for index in range(3))
    lower = tuple(max(0.0, maximum - tolerance) for maximum in maxima)
    upper = tuple(min(1.0, minimum + tolerance) for minimum in minima)
    if any(left > right + 1e-12 for left, right in zip(lower, upper)):
        return None
    if sum(lower) > 1.0 + 1e-12 or sum(upper) < 1.0 - 1e-12:
        return None
    return lower, upper  # type: ignore[return-value]


def _center_from_bounds(lower: TernaryLaw, upper: TernaryLaw) -> TernaryLaw:
    center = list(lower)
    remaining = 1.0 - sum(center)
    if remaining < -1e-10:
        raise ValueError("lower bounds exceed simplex mass")
    remaining = max(0.0, remaining)
    for index in range(3):
        addition = min(
            remaining,
            max(0.0, upper[index] - center[index]),
        )
        center[index] += addition
        remaining -= addition
    if remaining > 1e-10:
        raise ValueError("upper bounds cannot supply simplex mass")
    total = sum(center)
    if total <= 0.0:
        raise AssertionError("constructed center has zero mass")
    normalized = tuple(value / total for value in center)
    if any(
        value < lower[index] - 1e-9 or value > upper[index] + 1e-9
        for index, value in enumerate(normalized)
    ):
        raise AssertionError("normalization moved center outside feasible bounds")
    return normalized  # type: ignore[return-value]


def ternary_common_center(
    laws: Sequence[Sequence[float]],
    epsilon: float,
) -> TernaryLaw | None:
    """Construct one arbitrary ternary center covering every supplied law."""

    points = tuple(_normalize_ternary_law(law) for law in laws)
    bounds = ternary_cover_bounds(points, epsilon)
    if bounds is None:
        return None
    center = _center_from_bounds(*bounds)
    tolerance = _validate_epsilon(epsilon)
    if any(
        ternary_total_variation(point, center) > tolerance + 1e-9
        for point in points
    ):
        raise AssertionError("constructed center does not cover its target cluster")
    return center


def ternary_cluster_is_coverable(
    laws: Sequence[Sequence[float]],
    epsilon: float,
) -> bool:
    return ternary_common_center(laws, epsilon) is not None


def _water_filling_threshold(values: Sequence[float], budget: float) -> float:
    """Minimum r satisfying sum_j max(0, values_j-r) <= budget."""

    supplied = tuple(float(value) for value in values)
    if not supplied or any(not isfinite(value) or value < 0.0 for value in supplied):
        raise ValueError("water-filling values must be finite and nonnegative")
    limit = float(budget)
    if not isfinite(limit) or limit < 0.0:
        raise ValueError("water-filling budget must be finite and nonnegative")
    if sum(supplied) <= limit:
        return 0.0
    ordered = tuple(sorted(supplied, reverse=True))
    prefix = 0.0
    for count, value in enumerate(ordered, start=1):
        prefix += value
        next_value = ordered[count] if count < len(ordered) else 0.0
        candidate = (prefix - limit) / count
        if candidate >= next_value - 1e-15:
            return max(0.0, candidate)
    raise AssertionError("water-filling threshold was not found")


def ternary_minimax_center(
    laws: Sequence[Sequence[float]],
) -> tuple[TernaryLaw, float]:
    """Exact one-state minimax TV center and radius for finite ternary targets."""

    points = tuple(_normalize_ternary_law(law) for law in laws)
    if not points:
        raise ValueError("at least one target law is required")
    maxima = tuple(max(point[index] for point in points) for index in range(3))
    minima = tuple(min(point[index] for point in points) for index in range(3))
    range_radius = max(
        0.5 * (maximum - minimum)
        for maximum, minimum in zip(maxima, minima)
    )
    radius = max(
        range_radius,
        _water_filling_threshold(maxima, 1.0),
        _water_filling_threshold(
            tuple(1.0 - minimum for minimum in minima),
            2.0,
        ),
    )
    center = ternary_common_center(points, radius)
    if center is None:
        center = ternary_common_center(points, radius + 1e-12)
    if center is None:
        raise AssertionError("closed-form minimax radius is infeasible")
    achieved = max(ternary_total_variation(point, center) for point in points)
    if achieved > radius + 1e-9:
        raise AssertionError("constructed minimax center exceeds its radius")
    return center, radius


def _candidate_cover_masks_and_centers(
    family: FiniteTernaryFamily,
    epsilon: float,
    *,
    max_records: int,
) -> tuple[tuple[int, TernaryLaw], ...]:
    count = family.record_count
    if count > max_records:
        raise ValueError(
            f"exact ternary arbitrary-center search capped at {max_records} records"
        )
    tolerance = _validate_epsilon(epsilon)
    full = (1 << count) - 1
    by_coverage: dict[int, TernaryLaw] = {}
    for subset in range(1, full + 1):
        cluster = tuple(
            family.laws[index]
            for index in range(count)
            if (subset >> index) & 1
        )
        center = ternary_common_center(cluster, tolerance)
        if center is None:
            continue
        coverage = 0
        for index, law in enumerate(family.laws):
            if ternary_total_variation(law, center) <= tolerance + 1e-12:
                coverage |= 1 << index
        if coverage & subset != subset:
            raise AssertionError("canonical center failed to cover its defining subset")
        by_coverage.setdefault(coverage, center)

    # Remove every candidate whose covered set is a strict subset of another
    # candidate.  A superset center is never worse in an unweighted state-count
    # objective.  The SOS transform counts candidate supersets of every mask.
    present = [0] * (1 << count)
    for coverage in by_coverage:
        present[coverage] = 1
    superset_count = present.copy()
    for bit_index in range(count):
        bit = 1 << bit_index
        for mask in range(1 << count):
            if not mask & bit:
                superset_count[mask] += superset_count[mask | bit]
    maximal = tuple(
        (mask, by_coverage[mask])
        for mask in sorted(by_coverage)
        if superset_count[mask] == 1
    )
    if not maximal:
        raise AssertionError("singletons must yield ternary cover candidates")
    return maximal


def _minimum_cover_candidate_indices(
    point_count: int,
    coverage_masks: Sequence[int],
) -> tuple[int, ...]:
    full = (1 << point_count) - 1
    masks = tuple(int(mask) for mask in coverage_masks)
    if not masks or any(mask <= 0 or mask & ~full for mask in masks):
        raise ValueError("coverage masks must be nonempty subsets")
    if any(
        not any(mask & (1 << point) for mask in masks)
        for point in range(point_count)
    ):
        raise ValueError("candidate covers do not cover every point")

    uncovered = full
    greedy: list[int] = []
    while uncovered:
        index = max(
            range(len(masks)),
            key=lambda candidate: (masks[candidate] & uncovered).bit_count(),
        )
        if not masks[index] & uncovered:
            raise AssertionError("greedy cover stalled")
        greedy.append(index)
        uncovered &= ~masks[index]
    best = tuple(greedy)

    centers_for_point = [0] * point_count
    for index, mask in enumerate(masks):
        for point in range(point_count):
            if (mask >> point) & 1:
                centers_for_point[point] |= 1 << index

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
                (masks[index] & uncovered_mask).bit_count()
                for index in range(len(masks))
                if (available_mask >> index) & 1
            ),
            default=0,
        )
        if max_new == 0:
            return
        if len(chosen) + ceil(uncovered_mask.bit_count() / max_new) >= len(best):
            return
        uncovered_points = tuple(
            point
            for point in range(point_count)
            if (uncovered_mask >> point) & 1
        )
        point = min(
            uncovered_points,
            key=lambda candidate: (
                centers_for_point[candidate] & available_mask
            ).bit_count(),
        )
        options = centers_for_point[point] & available_mask
        if not options:
            return
        ordered_options = sorted(
            (
                index
                for index in range(len(masks))
                if (options >> index) & 1
            ),
            key=lambda index: (masks[index] & uncovered_mask).bit_count(),
            reverse=True,
        )
        removed = 0
        for index in ordered_options:
            removed |= 1 << index
            search(
                (*chosen, index),
                uncovered_mask & ~masks[index],
                available_mask & ~removed,
            )

    search((), full, (1 << len(masks)) - 1)
    return best


@dataclass(frozen=True)
class TernaryCoverCertificate:
    centers: tuple[TernaryLaw, ...]
    assignment: Mapping[Record, int]

    @property
    def state_count(self) -> int:
        return len(self.centers)

    @property
    def predictive_bits(self) -> int:
        return _ceil_log2_integer(self.state_count)


def minimum_ternary_arbitrary_cover(
    family: FiniteTernaryFamily,
    epsilon: float,
    *,
    max_records: int = 14,
) -> TernaryCoverCertificate:
    """Exact minimum arbitrary-center epsilon-cover for one ternary query."""

    candidates = _candidate_cover_masks_and_centers(
        family,
        epsilon,
        max_records=max_records,
    )
    chosen = _minimum_cover_candidate_indices(
        family.record_count,
        tuple(mask for mask, _ in candidates),
    )
    centers = tuple(candidates[index][1] for index in chosen)
    tolerance = _validate_epsilon(epsilon)
    assignment: dict[Record, int] = {}
    for record, law in zip(family.records, family.laws):
        for center_index, center in enumerate(centers):
            if ternary_total_variation(law, center) <= tolerance + 1e-12:
                assignment[record] = center_index
                break
        else:
            raise AssertionError("minimum-cover centers miss a target")
    return TernaryCoverCertificate(centers, assignment)


def target_centered_ternary_cover_size(
    family: FiniteTernaryFamily,
    epsilon: float,
    *,
    max_records: int = 14,
) -> int:
    return len(
        minimum_target_centered_cover(
            family.to_stochastic_family(),
            epsilon,
            max_records=max_records,
        )
    )


def ternary_packing_size_lower_bound(
    family: FiniteTernaryFamily,
    epsilon: float,
    *,
    max_records: int = 14,
) -> int:
    return len(
        maximum_stochastic_predictive_packing(
            family.to_stochastic_family(),
            epsilon,
            max_records=max_records,
        )
    )


def ternary_network_units_required(
    family: FiniteTernaryFamily,
    epsilon: float,
    *,
    capacity_bits_per_unit: int = 1,
    max_records: int = 14,
) -> int:
    multiplier = _validate_nonnegative_integer(
        capacity_bits_per_unit,
        name="capacity_bits_per_unit",
    )
    if multiplier < 1:
        raise ValueError("capacity_bits_per_unit must be positive")
    cover = minimum_ternary_arbitrary_cover(
        family,
        epsilon,
        max_records=max_records,
    )
    return ceil(cover.predictive_bits / multiplier)


@dataclass(frozen=True)
class TernaryNetworkCertificate:
    cover: TernaryCoverCertificate
    required_units: int
    min_cut_units: int
    routes: tuple[RoutedPath, ...]

    @property
    def feasible(self) -> bool:
        return self.min_cut_units >= self.required_units

    @property
    def routed_units(self) -> int:
        return sum(route.units for route in self.routes)


def ternary_network_certificate(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteTernaryFamily,
    epsilon: float,
    *,
    capacity_bits_per_unit: int = 1,
    max_records: int = 14,
) -> TernaryNetworkCertificate:
    multiplier = _validate_nonnegative_integer(
        capacity_bits_per_unit,
        name="capacity_bits_per_unit",
    )
    if multiplier < 1:
        raise ValueError("capacity_bits_per_unit must be positive")
    cover = minimum_ternary_arbitrary_cover(
        family,
        epsilon,
        max_records=max_records,
    )
    required = ceil(cover.predictive_bits / multiplier)
    minimum = network.min_cut_capacity(source, sink)
    routes = (
        network.route_units(source, sink, required)
        if minimum >= required
        else ()
    )
    return TernaryNetworkCertificate(cover, required, minimum, routes)
