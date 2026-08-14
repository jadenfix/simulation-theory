"""Predictive-equivalence classes and causal-network min-cut bounds.

This module generalizes coordinate INDEX to an arbitrary finite deterministic
future-query family.

Two hidden records are exactly predictively equivalent when every allowed
future query returns the same outcome.  If the query family induces K
equivalence classes, any state crossing a causal cut before the query is chosen
must distinguish at least K possibilities.  The exact classical requirement is

    ceil(log2 K) bits.

For a directed acyclic capacity network with one source and one sink, every
source-sink cut must carry that many bits.  Integer max-flow/min-cut also gives a
matching routing construction: transmit the predictive-class label rather than
the full hidden record.

A capacity unit may be interpreted as

* one classical bit;
* one unassisted transmitted qubit, for exact classical payload;
* one entanglement-assisted transmitted qubit, with two exact classical bits
  under an explicit dense-coding assumption.

For deterministic responses under an exogenous query distribution, the total
variation distance between two records is exactly the total query weight on
which their signatures disagree.  Finite maximum packings therefore give
approximate cut lower bounds.

These are internal communication and predictive-state results for declared
finite interfaces.  They do not prove that reality is simulated and do not
convert model bits, qubits, or edge capacities into parent-universe hardware,
energy, or spacetime.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product
from math import ceil
from typing import Callable, Hashable, Mapping, Sequence

Record = Hashable
Outcome = Hashable
QueryFunction = Callable[[Record], Outcome]
Edge = tuple[str, str, int]


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


def _validate_query_weights(
    query_count: int,
    weights: Sequence[float] | None,
) -> tuple[float, ...]:
    if weights is None:
        return tuple(1.0 / query_count for _ in range(query_count))
    values = tuple(float(weight) for weight in weights)
    if len(values) != query_count:
        raise ValueError("one query weight is required per query")
    if any(weight < 0.0 for weight in values):
        raise ValueError("query weights must be nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("query weights must sum to one")
    return values


@dataclass(frozen=True)
class FiniteQueryFamily:
    """Finite records and their deterministic future-query signatures."""

    records: tuple[Record, ...]
    query_names: tuple[str, ...]
    signatures: tuple[tuple[Outcome, ...], ...]

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("at least one record is required")
        try:
            unique_record_count = len(set(self.records))
        except TypeError as error:
            raise ValueError("records must be unique and hashable") from error
        if unique_record_count != len(self.records):
            raise ValueError("records must be unique and hashable")
        if not self.query_names:
            raise ValueError("at least one query is required")
        if len(set(self.query_names)) != len(self.query_names):
            raise ValueError("query names must be unique")
        if len(self.signatures) != len(self.records):
            raise ValueError("one signature is required per record")
        for signature in self.signatures:
            if len(signature) != len(self.query_names):
                raise ValueError("signature length must match query count")
            try:
                hash(signature)
            except TypeError as error:
                raise ValueError("query outcomes must be hashable") from error

    @classmethod
    def from_functions(
        cls,
        records: Sequence[Record],
        queries: Sequence[tuple[str, QueryFunction]],
    ) -> "FiniteQueryFamily":
        supplied_records = tuple(records)
        supplied_queries = tuple(queries)
        if not supplied_queries:
            raise ValueError("at least one query is required")
        names = tuple(str(name) for name, _ in supplied_queries)
        signatures = tuple(
            tuple(query(record) for _, query in supplied_queries)
            for record in supplied_records
        )
        return cls(supplied_records, names, signatures)

    @property
    def query_count(self) -> int:
        return len(self.query_names)

    @property
    def record_count(self) -> int:
        return len(self.records)

    def record_index(self, record: Record) -> int:
        try:
            return self.records.index(record)
        except ValueError as error:
            raise ValueError("record is not in the finite family") from error

    def signature(self, record: Record) -> tuple[Outcome, ...]:
        return self.signatures[self.record_index(record)]

    @property
    def equivalence_classes(self) -> tuple[tuple[Record, ...], ...]:
        groups: dict[tuple[Outcome, ...], list[Record]] = {}
        for record, signature in zip(self.records, self.signatures):
            groups.setdefault(signature, []).append(record)
        return tuple(tuple(group) for group in groups.values())

    @property
    def class_count(self) -> int:
        return len(set(self.signatures))

    @property
    def exact_predictive_bits(self) -> int:
        return _ceil_log2_integer(self.class_count)

    def class_label_map(self) -> dict[Record, int]:
        label_by_signature: dict[tuple[Outcome, ...], int] = {}
        result: dict[Record, int] = {}
        for record, signature in zip(self.records, self.signatures):
            label = label_by_signature.setdefault(
                signature,
                len(label_by_signature),
            )
            result[record] = label
        return result


def binary_coordinate_query_family(
    record_bits: int,
    coordinates: Sequence[int] | None = None,
    *,
    max_record_bits: int = 16,
) -> FiniteQueryFamily:
    bits = _validate_nonnegative_integer(record_bits, name="record_bits")
    if bits < 1:
        raise ValueError("record_bits must be positive")
    if bits > max_record_bits:
        raise ValueError(
            f"explicit binary record enumeration capped at {max_record_bits} bits"
        )
    selected = (
        tuple(range(bits))
        if coordinates is None
        else tuple(int(coordinate) for coordinate in coordinates)
    )
    if not selected or len(set(selected)) != len(selected):
        raise ValueError("coordinates must be nonempty and unique")
    if any(not 0 <= coordinate < bits for coordinate in selected):
        raise ValueError("coordinate out of range")
    records = tuple(product((0, 1), repeat=bits))
    queries = tuple(
        (
            f"x[{coordinate}]",
            lambda record, coordinate=coordinate: record[coordinate],
        )
        for coordinate in selected
    )
    return FiniteQueryFamily.from_functions(records, queries)


def binary_parity_query_family(
    record_bits: int,
    masks: Sequence[int],
    *,
    max_record_bits: int = 16,
) -> FiniteQueryFamily:
    bits = _validate_nonnegative_integer(record_bits, name="record_bits")
    if bits < 1:
        raise ValueError("record_bits must be positive")
    if bits > max_record_bits:
        raise ValueError(
            f"explicit binary record enumeration capped at {max_record_bits} bits"
        )
    supplied_masks = tuple(int(mask) for mask in masks)
    if not supplied_masks or len(set(supplied_masks)) != len(supplied_masks):
        raise ValueError("parity masks must be nonempty and unique")
    if any(not 0 < mask < 1 << bits for mask in supplied_masks):
        raise ValueError("parity mask out of range")
    records = tuple(product((0, 1), repeat=bits))

    def parity(record: tuple[int, ...], mask: int) -> int:
        return sum(
            bit
            for coordinate, bit in enumerate(record)
            if (mask >> coordinate) & 1
        ) & 1

    queries = tuple(
        (
            f"parity[{mask:#0{bits + 2}b}]",
            lambda record, mask=mask: parity(record, mask),
        )
        for mask in supplied_masks
    )
    return FiniteQueryFamily.from_functions(records, queries)


def deterministic_query_total_variation(
    family: FiniteQueryFamily,
    left: Record,
    right: Record,
    weights: Sequence[float] | None = None,
) -> float:
    """Exact TV of the joint law over query index and deterministic outcome."""

    query_weights = _validate_query_weights(family.query_count, weights)
    first = family.signature(left)
    second = family.signature(right)
    return sum(
        weight
        for outcome_left, outcome_right, weight in zip(
            first,
            second,
            query_weights,
        )
        if outcome_left != outcome_right
    )


def maximum_predictive_packing(
    family: FiniteQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    max_records: int = 28,
) -> tuple[Record, ...]:
    """Exact maximum 2-epsilon packing by a bounded maximum-clique search."""

    tolerance = float(epsilon)
    if tolerance < 0.0:
        raise ValueError("epsilon must be nonnegative")
    if family.record_count > max_records:
        raise ValueError(
            f"exact packing search capped at {max_records} records"
        )
    query_weights = _validate_query_weights(family.query_count, weights)
    adjacency: list[int] = [0] * family.record_count
    for left in range(family.record_count):
        for right in range(left + 1, family.record_count):
            distance = sum(
                weight
                for a, b, weight in zip(
                    family.signatures[left],
                    family.signatures[right],
                    query_weights,
                )
                if a != b
            )
            if distance > 2.0 * tolerance:
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
            lowest_bit = remaining & -remaining
            vertex = lowest_bit.bit_length() - 1
            remaining ^= lowest_bit
            expand(
                (*chosen, vertex),
                remaining & adjacency[vertex],
            )
        if len(chosen) > len(best):
            best = chosen

    expand((), (1 << family.record_count) - 1)
    return tuple(family.records[index] for index in best)


def predictive_packing_bits_lower_bound(
    family: FiniteQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    max_records: int = 28,
) -> int:
    packing = maximum_predictive_packing(
        family,
        epsilon,
        weights,
        max_records=max_records,
    )
    return _ceil_log2_integer(len(packing))


@dataclass(frozen=True)
class RoutedPath:
    nodes: tuple[str, ...]
    units: int

    def __post_init__(self) -> None:
        if len(self.nodes) < 2:
            raise ValueError("a routed path needs at least two nodes")
        if self.units < 1:
            raise ValueError("routed path units must be positive")


@dataclass(frozen=True)
class FlowResult:
    value: int
    edge_flows: tuple[Edge, ...]
    source_side: tuple[str, ...]
    cut_capacity: int

    def flow_map(self) -> dict[tuple[str, str], int]:
        return {
            (left, right): units
            for left, right, units in self.edge_flows
        }


@dataclass(frozen=True)
class CausalCapacityNetwork:
    """Finite directed acyclic network with positive integer edge capacities."""

    nodes: tuple[str, ...]
    edges: tuple[Edge, ...]

    def __post_init__(self) -> None:
        canonical_nodes = tuple(str(node) for node in self.nodes)
        if not canonical_nodes or len(set(canonical_nodes)) != len(canonical_nodes):
            raise ValueError("network nodes must be nonempty and unique")
        node_set = set(canonical_nodes)
        combined: dict[tuple[str, str], int] = {}
        for supplied_left, supplied_right, supplied_capacity in self.edges:
            left = str(supplied_left)
            right = str(supplied_right)
            capacity = _validate_nonnegative_integer(
                supplied_capacity,
                name="edge capacity",
            )
            if left not in node_set or right not in node_set:
                raise ValueError("edge endpoint is not a network node")
            if left == right:
                raise ValueError("self-loops are not causal edges")
            if capacity < 1:
                raise ValueError("edge capacities must be positive")
            combined[(left, right)] = combined.get((left, right), 0) + capacity
        canonical_edges = tuple(
            (left, right, capacity)
            for (left, right), capacity in sorted(combined.items())
        )
        object.__setattr__(self, "nodes", canonical_nodes)
        object.__setattr__(self, "edges", canonical_edges)
        self.topological_order()

    def topological_order(self) -> tuple[str, ...]:
        indegree = {node: 0 for node in self.nodes}
        outgoing: dict[str, list[str]] = {node: [] for node in self.nodes}
        for left, right, _ in self.edges:
            indegree[right] += 1
            outgoing[left].append(right)
        ready = deque(node for node in self.nodes if indegree[node] == 0)
        order: list[str] = []
        while ready:
            node = ready.popleft()
            order.append(node)
            for neighbor in outgoing[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    ready.append(neighbor)
        if len(order) != len(self.nodes):
            raise ValueError("causal capacity network must be acyclic")
        return tuple(order)

    def edge_capacity(self, left: str, right: str) -> int:
        source = str(left)
        target = str(right)
        return next(
            (
                capacity
                for edge_left, edge_right, capacity in self.edges
                if edge_left == source and edge_right == target
            ),
            0,
        )

    def max_flow(self, source: str, sink: str) -> FlowResult:
        start = str(source)
        target = str(sink)
        if start not in self.nodes or target not in self.nodes:
            raise ValueError("source and sink must be network nodes")
        if start == target:
            raise ValueError("source and sink must be distinct")

        residual: dict[str, dict[str, int]] = {
            node: {} for node in self.nodes
        }
        for left, right, capacity in self.edges:
            residual[left][right] = capacity
            residual[right].setdefault(left, 0)

        total = 0
        while True:
            parent: dict[str, str | None] = {start: None}
            queue = deque([start])
            while queue and target not in parent:
                node = queue.popleft()
                for neighbor in self.nodes:
                    if (
                        neighbor not in parent
                        and residual[node].get(neighbor, 0) > 0
                    ):
                        parent[neighbor] = node
                        queue.append(neighbor)
            if target not in parent:
                break
            bottleneck = min(
                residual[parent_node][node]
                for parent_node, node in _path_edges(parent, start, target)
            )
            for left, right in _path_edges(parent, start, target):
                residual[left][right] -= bottleneck
                residual[right][left] = (
                    residual[right].get(left, 0) + bottleneck
                )
            total += bottleneck

        source_side = _residual_reachable(residual, start, self.nodes)
        cut_capacity = sum(
            capacity
            for left, right, capacity in self.edges
            if left in source_side and right not in source_side
        )
        edge_flows = tuple(
            (
                left,
                right,
                capacity - residual[left].get(right, 0),
            )
            for left, right, capacity in self.edges
            if capacity - residual[left].get(right, 0) > 0
        )
        if total != cut_capacity:
            raise AssertionError("max-flow and min-cut values disagree")
        return FlowResult(
            total,
            edge_flows,
            tuple(node for node in self.nodes if node in source_side),
            cut_capacity,
        )

    def min_cut_capacity(self, source: str, sink: str) -> int:
        return self.max_flow(source, sink).cut_capacity

    def route_units(
        self,
        source: str,
        sink: str,
        required_units: int,
    ) -> tuple[RoutedPath, ...]:
        required = _validate_nonnegative_integer(
            required_units,
            name="required_units",
        )
        if required == 0:
            return ()
        result = self.max_flow(source, sink)
        if result.value < required:
            raise ValueError(
                f"network can route only {result.value} of {required} units"
            )
        remaining_flow = result.flow_map()
        routes: list[RoutedPath] = []
        routed = 0
        while routed < required:
            path = _positive_flow_path(
                remaining_flow,
                str(source),
                str(sink),
                self.nodes,
            )
            if path is None:
                raise AssertionError("flow decomposition ended too early")
            path_edges = tuple(zip(path, path[1:]))
            available = min(remaining_flow[edge] for edge in path_edges)
            amount = min(available, required - routed)
            for edge in path_edges:
                remaining_flow[edge] -= amount
            routes.append(RoutedPath(path, amount))
            routed += amount
        return tuple(routes)


def _path_edges(
    parent: Mapping[str, str | None],
    source: str,
    sink: str,
) -> tuple[tuple[str, str], ...]:
    reversed_edges: list[tuple[str, str]] = []
    node = sink
    while node != source:
        predecessor = parent[node]
        if predecessor is None:
            raise AssertionError("broken augmenting path")
        reversed_edges.append((predecessor, node))
        node = predecessor
    return tuple(reversed(reversed_edges))


def _residual_reachable(
    residual: Mapping[str, Mapping[str, int]],
    source: str,
    node_order: Sequence[str],
) -> set[str]:
    reachable = {source}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for neighbor in node_order:
            if (
                neighbor not in reachable
                and residual[node].get(neighbor, 0) > 0
            ):
                reachable.add(neighbor)
                queue.append(neighbor)
    return reachable


def _positive_flow_path(
    flow: Mapping[tuple[str, str], int],
    source: str,
    sink: str,
    node_order: Sequence[str],
) -> tuple[str, ...] | None:
    parent: dict[str, str | None] = {source: None}
    queue = deque([source])
    while queue and sink not in parent:
        node = queue.popleft()
        for neighbor in node_order:
            if (
                neighbor not in parent
                and flow.get((node, neighbor), 0) > 0
            ):
                parent[neighbor] = node
                queue.append(neighbor)
    if sink not in parent:
        return None
    nodes: list[str] = []
    node = sink
    while node is not None:
        nodes.append(node)
        node = parent[node]
    return tuple(reversed(nodes))


def exact_predictive_network_units_required(
    family: FiniteQueryFamily,
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


def exact_predictive_network_deficit_units(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteQueryFamily,
    *,
    capacity_bits_per_unit: int = 1,
) -> int:
    required = exact_predictive_network_units_required(
        family,
        capacity_bits_per_unit=capacity_bits_per_unit,
    )
    available = network.min_cut_capacity(source, sink)
    return max(0, required - available)


def exact_single_sink_network_feasible(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteQueryFamily,
    *,
    capacity_bits_per_unit: int = 1,
) -> bool:
    """Exact single-sink iff result under the declared capacity interpretation."""

    return (
        exact_predictive_network_deficit_units(
            network,
            source,
            sink,
            family,
            capacity_bits_per_unit=capacity_bits_per_unit,
        )
        == 0
    )


def route_exact_predictive_class(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteQueryFamily,
    *,
    capacity_bits_per_unit: int = 1,
) -> tuple[RoutedPath, ...]:
    required = exact_predictive_network_units_required(
        family,
        capacity_bits_per_unit=capacity_bits_per_unit,
    )
    return network.route_units(source, sink, required)


def approximate_predictive_cut_deficit_units(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteQueryFamily,
    epsilon: float,
    weights: Sequence[float] | None = None,
    *,
    capacity_bits_per_unit: int = 1,
    max_records: int = 28,
) -> int:
    """Necessary cut deficit from an exact finite predictive packing."""

    packing_bits = predictive_packing_bits_lower_bound(
        family,
        epsilon,
        weights,
        max_records=max_records,
    )
    multiplier = _validate_nonnegative_integer(
        capacity_bits_per_unit,
        name="capacity_bits_per_unit",
    )
    if multiplier < 1:
        raise ValueError("capacity_bits_per_unit must be positive")
    required_units = ceil(packing_bits / multiplier)
    return max(
        0,
        required_units - network.min_cut_capacity(source, sink),
    )


def multisink_exact_cut_deficits_units(
    network: CausalCapacityNetwork,
    source: str,
    sink_families: Mapping[str, FiniteQueryFamily],
    *,
    capacity_bits_per_unit: int = 1,
) -> dict[str, int]:
    """Per-sink necessary deficits; no general multicast sufficiency is claimed."""

    if not sink_families:
        raise ValueError("at least one sink family is required")
    return {
        str(sink): exact_predictive_network_deficit_units(
            network,
            source,
            str(sink),
            family,
            capacity_bits_per_unit=capacity_bits_per_unit,
        )
        for sink, family in sink_families.items()
    }


@dataclass(frozen=True)
class PredictiveNetworkCertificate:
    """Single-sink exact cut and routing certificate."""

    required_units: int
    min_cut_units: int
    routes: tuple[RoutedPath, ...]

    @property
    def feasible(self) -> bool:
        return self.min_cut_units >= self.required_units

    @property
    def routed_units(self) -> int:
        return sum(route.units for route in self.routes)


def exact_predictive_network_certificate(
    network: CausalCapacityNetwork,
    source: str,
    sink: str,
    family: FiniteQueryFamily,
    *,
    capacity_bits_per_unit: int = 1,
) -> PredictiveNetworkCertificate:
    required = exact_predictive_network_units_required(
        family,
        capacity_bits_per_unit=capacity_bits_per_unit,
    )
    minimum = network.min_cut_capacity(source, sink)
    routes = (
        network.route_units(source, sink, required)
        if minimum >= required
        else ()
    )
    return PredictiveNetworkCertificate(required, minimum, routes)
