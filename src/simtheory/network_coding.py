"""Finite-field multicast network-coding certificates.

The single-sink predictive min-cut theorem does not automatically solve a
simultaneous multi-sink problem. Different sinks can compete for one shared
bottleneck. Routing and replication may fail even when every sink separately
has a large enough min-cut.

This module builds a bounded, auditable bridge from predictive class labels to
scalar linear network coding over a prime field.

A source holds h symbols x in F_p^h. Every unit-capacity edge carries one
linear combination g_e dot x, where g_e is its global encoding vector. At a
non-source node, every outgoing global vector must lie in the span of the
incoming vectors. A sink recovers all source symbols exactly iff its incoming
global vectors have rank h.

The canonical butterfly network supplies a sharp finite separation:

* both sinks have source min-cut two;
* no routing-only scalar assignment can deliver both symbols to both sinks;
* over F_2, sending x_1+x_2 through the shared bottleneck lets both sinks
  decode.

The implementation includes exact GF(p) rank/solve routines, local coefficient
validation, sink decoders, exhaustive bounded code search, exhaustive routing
search, min-cut checks, and a predictive-class bridge.

These are internal finite communication results for declared networks. They
are not evidence for simulation and do not convert field symbols or edge units
into parent-universe hardware, energy, mass, or spacetime.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product
from math import prod
from typing import Hashable, Mapping, Sequence

from .predictive_networks import CausalCapacityNetwork, FiniteQueryFamily

FieldVector = tuple[int, ...]
CoefficientMap = tuple[tuple[str, tuple[int, ...]], ...]


def _validate_nonnegative_integer(value: int, *, name: str) -> int:
    integer = int(value)
    if integer != value or integer < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return integer


def _is_prime(value: int) -> bool:
    integer = int(value)
    if integer != value or integer < 2:
        return False
    if integer == 2:
        return True
    if integer % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= integer:
        if integer % divisor == 0:
            return False
        divisor += 2
    return True


def _validate_prime(value: int) -> int:
    prime = int(value)
    if not _is_prime(prime):
        raise ValueError("field modulus must be prime")
    return prime


def _canonical_vector(
    vector: Sequence[int],
    length: int,
    prime: int,
) -> FieldVector:
    values = tuple(int(value) % prime for value in vector)
    if len(values) != length:
        raise ValueError("field vector has the wrong length")
    return values


def _zero_vector(length: int) -> FieldVector:
    return tuple(0 for _ in range(length))


def _basis_vector(length: int, index: int) -> FieldVector:
    if not 0 <= index < length:
        raise ValueError("basis index out of range")
    return tuple(1 if coordinate == index else 0 for coordinate in range(length))


def _linear_combination(
    coefficients: Sequence[int],
    vectors: Sequence[Sequence[int]],
    length: int,
    prime: int,
) -> FieldVector:
    supplied_vectors = tuple(
        _canonical_vector(vector, length, prime) for vector in vectors
    )
    supplied_coefficients = tuple(int(value) % prime for value in coefficients)
    if len(supplied_coefficients) != len(supplied_vectors):
        raise ValueError("one coefficient is required per vector")
    return tuple(
        sum(
            coefficient * vector[coordinate]
            for coefficient, vector in zip(
                supplied_coefficients,
                supplied_vectors,
            )
        )
        % prime
        for coordinate in range(length)
    )


def gf_rank(matrix: Sequence[Sequence[int]], prime: int) -> int:
    """Exact row rank over the prime field F_p."""

    modulus = _validate_prime(prime)
    rows = [tuple(int(value) % modulus for value in row) for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("matrix rows must have equal length")
    work = [list(row) for row in rows]
    rank = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column] % modulus != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], modulus - 2, modulus)
        work[rank] = [(value * inverse) % modulus for value in work[rank]]
        for row in range(len(work)):
            if row == rank:
                continue
            factor = work[row][column] % modulus
            if factor:
                work[row] = [
                    (value - factor * pivot_value) % modulus
                    for value, pivot_value in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == len(work):
            break
    return rank


def gf_solve(
    matrix: Sequence[Sequence[int]],
    target: Sequence[int],
    prime: int,
) -> FieldVector | None:
    """Return one solution to A x=b over F_p, with free variables set to zero."""

    modulus = _validate_prime(prime)
    rows = [tuple(int(value) % modulus for value in row) for row in matrix]
    right = tuple(int(value) % modulus for value in target)
    if len(rows) != len(right):
        raise ValueError("target length must match the number of matrix rows")
    if not rows:
        return () if not right else None
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("matrix rows must have equal length")
    augmented = [list(row) + [value] for row, value in zip(rows, right)]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(augmented))
                if augmented[row][column] % modulus != 0
            ),
            None,
        )
        if pivot is None:
            continue
        augmented[pivot_row], augmented[pivot] = (
            augmented[pivot],
            augmented[pivot_row],
        )
        inverse = pow(augmented[pivot_row][column], modulus - 2, modulus)
        augmented[pivot_row] = [
            (value * inverse) % modulus
            for value in augmented[pivot_row]
        ]
        for row in range(len(augmented)):
            if row == pivot_row:
                continue
            factor = augmented[row][column] % modulus
            if factor:
                augmented[row] = [
                    (value - factor * pivot_value) % modulus
                    for value, pivot_value in zip(
                        augmented[row],
                        augmented[pivot_row],
                    )
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(augmented):
            break

    for row in augmented:
        if all(value % modulus == 0 for value in row[:width]) and row[width] % modulus:
            return None

    solution = [0] * width
    for row, column in enumerate(pivot_columns):
        solution[column] = augmented[row][width] % modulus
    return tuple(solution)


@dataclass(frozen=True)
class UnitEdge:
    edge_id: str
    tail: str
    head: str

    def __post_init__(self) -> None:
        edge_id = str(self.edge_id)
        tail = str(self.tail)
        head = str(self.head)
        if not edge_id:
            raise ValueError("edge_id cannot be empty")
        if not tail or not head or tail == head:
            raise ValueError("unit edge needs distinct nonempty endpoints")
        object.__setattr__(self, "edge_id", edge_id)
        object.__setattr__(self, "tail", tail)
        object.__setattr__(self, "head", head)


@dataclass(frozen=True)
class UnitCapacityDAG:
    nodes: tuple[str, ...]
    edges: tuple[UnitEdge, ...]

    def __post_init__(self) -> None:
        nodes = tuple(str(node) for node in self.nodes)
        if not nodes or len(set(nodes)) != len(nodes):
            raise ValueError("network nodes must be nonempty and unique")
        supplied_edges = tuple(self.edges)
        if len({edge.edge_id for edge in supplied_edges}) != len(supplied_edges):
            raise ValueError("unit edge identifiers must be unique")
        node_set = set(nodes)
        if any(edge.tail not in node_set or edge.head not in node_set for edge in supplied_edges):
            raise ValueError("edge endpoint is not a network node")
        canonical_edges = tuple(
            sorted(
                supplied_edges,
                key=lambda edge: (edge.tail, edge.head, edge.edge_id),
            )
        )
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", canonical_edges)
        self.topological_order()

    @classmethod
    def from_capacity_network(
        cls,
        network: CausalCapacityNetwork,
    ) -> "UnitCapacityDAG":
        edges: list[UnitEdge] = []
        for tail, head, capacity in network.edges:
            for index in range(capacity):
                edges.append(UnitEdge(f"{tail}->{head}#{index}", tail, head))
        return cls(network.nodes, tuple(edges))

    def topological_order(self) -> tuple[str, ...]:
        indegree = {node: 0 for node in self.nodes}
        outgoing = {node: [] for node in self.nodes}
        for edge in self.edges:
            indegree[edge.head] += 1
            outgoing[edge.tail].append(edge.head)
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
            raise ValueError("linear multicast network must be acyclic")
        return tuple(order)

    def incoming(self, node: str) -> tuple[UnitEdge, ...]:
        target = str(node)
        if target not in self.nodes:
            raise ValueError("node is not in the network")
        return tuple(
            sorted(
                (edge for edge in self.edges if edge.head == target),
                key=lambda edge: edge.edge_id,
            )
        )

    def outgoing(self, node: str) -> tuple[UnitEdge, ...]:
        source = str(node)
        if source not in self.nodes:
            raise ValueError("node is not in the network")
        return tuple(
            sorted(
                (edge for edge in self.edges if edge.tail == source),
                key=lambda edge: edge.edge_id,
            )
        )

    def edge(self, edge_id: str) -> UnitEdge:
        identifier = str(edge_id)
        for edge in self.edges:
            if edge.edge_id == identifier:
                return edge
        raise ValueError(f"unknown unit edge: {identifier}")

    def to_capacity_network(self) -> CausalCapacityNetwork:
        counts: dict[tuple[str, str], int] = {}
        for edge in self.edges:
            counts[(edge.tail, edge.head)] = counts.get((edge.tail, edge.head), 0) + 1
        return CausalCapacityNetwork(
            self.nodes,
            tuple(
                (tail, head, capacity)
                for (tail, head), capacity in sorted(counts.items())
            ),
        )

    def min_cut_capacity(self, source: str, sink: str) -> int:
        return self.to_capacity_network().min_cut_capacity(source, sink)


@dataclass(frozen=True)
class ScalarLinearCode:
    field_prime: int
    source: str
    sinks: tuple[str, ...]
    source_dimension: int
    local_coefficients: CoefficientMap

    def __post_init__(self) -> None:
        prime = _validate_prime(self.field_prime)
        source = str(self.source)
        sinks = tuple(str(sink) for sink in self.sinks)
        if not source or not sinks or len(set(sinks)) != len(sinks):
            raise ValueError("source and unique nonempty sinks are required")
        dimension = _validate_nonnegative_integer(
            self.source_dimension,
            name="source_dimension",
        )
        if dimension < 1:
            raise ValueError("source_dimension must be positive")
        coefficients = tuple(
            (str(edge_id), tuple(int(value) % prime for value in values))
            for edge_id, values in self.local_coefficients
        )
        if len({edge_id for edge_id, _ in coefficients}) != len(coefficients):
            raise ValueError("one local coefficient vector is allowed per edge")
        object.__setattr__(self, "field_prime", prime)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "sinks", sinks)
        object.__setattr__(self, "source_dimension", dimension)
        object.__setattr__(self, "local_coefficients", coefficients)

    def coefficient_map(self) -> dict[str, tuple[int, ...]]:
        return dict(self.local_coefficients)


@dataclass(frozen=True)
class SinkDecoder:
    sink: str
    incoming_edges: tuple[str, ...]
    rank: int
    source_coordinate_coefficients: tuple[FieldVector, ...]

    @property
    def decodes_all(self) -> bool:
        return self.rank == len(self.source_coordinate_coefficients)


@dataclass(frozen=True)
class LinearMulticastCertificate:
    network: UnitCapacityDAG
    code: ScalarLinearCode
    global_vectors: tuple[tuple[str, FieldVector], ...]
    decoders: tuple[SinkDecoder, ...]

    def global_vector_map(self) -> dict[str, FieldVector]:
        return dict(self.global_vectors)

    @property
    def valid(self) -> bool:
        return all(decoder.decodes_all for decoder in self.decoders)

    @property
    def sink_ranks(self) -> dict[str, int]:
        return {decoder.sink: decoder.rank for decoder in self.decoders}


def evaluate_scalar_linear_code(
    network: UnitCapacityDAG,
    code: ScalarLinearCode,
) -> LinearMulticastCertificate:
    if code.source not in network.nodes:
        raise ValueError("code source is not a network node")
    if any(sink not in network.nodes or sink == code.source for sink in code.sinks):
        raise ValueError("every sink must be a distinct network node")
    coefficient_map = code.coefficient_map()
    edge_ids = {edge.edge_id for edge in network.edges}
    if set(coefficient_map) != edge_ids:
        raise ValueError("local coefficients must be supplied for every unit edge exactly once")

    global_vectors: dict[str, FieldVector] = {}
    for node in network.topological_order():
        incoming = network.incoming(node)
        incoming_vectors = tuple(global_vectors[edge.edge_id] for edge in incoming)
        for edge in network.outgoing(node):
            coefficients = coefficient_map[edge.edge_id]
            expected = code.source_dimension if node == code.source else len(incoming)
            if len(coefficients) != expected:
                raise ValueError(
                    f"edge {edge.edge_id} needs {expected} local coefficients"
                )
            if node == code.source:
                vector = _canonical_vector(
                    coefficients,
                    code.source_dimension,
                    code.field_prime,
                )
            else:
                vector = _linear_combination(
                    coefficients,
                    incoming_vectors,
                    code.source_dimension,
                    code.field_prime,
                )
            global_vectors[edge.edge_id] = vector

    decoders: list[SinkDecoder] = []
    for sink in code.sinks:
        incoming = network.incoming(sink)
        vectors = tuple(global_vectors[edge.edge_id] for edge in incoming)
        rank = gf_rank(vectors, code.field_prime)
        matrix = tuple(
            tuple(vector[coordinate] for vector in vectors)
            for coordinate in range(code.source_dimension)
        )
        decoder_rows: list[FieldVector] = []
        for coordinate in range(code.source_dimension):
            solution = gf_solve(
                matrix,
                _basis_vector(code.source_dimension, coordinate),
                code.field_prime,
            )
            decoder_rows.append(
                solution if solution is not None else _zero_vector(len(vectors))
            )
        decoders.append(
            SinkDecoder(
                sink,
                tuple(edge.edge_id for edge in incoming),
                rank,
                tuple(decoder_rows),
            )
        )

    certificate = LinearMulticastCertificate(
        network,
        code,
        tuple(sorted(global_vectors.items())),
        tuple(decoders),
    )
    _verify_decoder_equations(certificate)
    return certificate


def _verify_decoder_equations(certificate: LinearMulticastCertificate) -> None:
    vectors = certificate.global_vector_map()
    code = certificate.code
    for decoder in certificate.decoders:
        incoming_vectors = tuple(
            vectors[edge_id] for edge_id in decoder.incoming_edges
        )
        if decoder.rank < code.source_dimension:
            continue
        for coordinate, coefficients in enumerate(
            decoder.source_coordinate_coefficients
        ):
            recovered = _linear_combination(
                coefficients,
                incoming_vectors,
                code.source_dimension,
                code.field_prime,
            )
            if recovered != _basis_vector(code.source_dimension, coordinate):
                raise AssertionError("sink decoder does not recover a source basis symbol")


def certificate_is_routing(certificate: LinearMulticastCertificate) -> bool:
    """Whether every edge carries zero or an unchanged locally available symbol."""

    vectors = certificate.global_vector_map()
    code = certificate.code
    basis = {
        _basis_vector(code.source_dimension, index)
        for index in range(code.source_dimension)
    }
    zero = _zero_vector(code.source_dimension)
    for node in certificate.network.topological_order():
        incoming_vectors = {
            vectors[edge.edge_id]
            for edge in certificate.network.incoming(node)
        }
        for edge in certificate.network.outgoing(node):
            vector = vectors[edge.edge_id]
            allowed = (
                ({zero} | basis)
                if node == code.source
                else ({zero} | incoming_vectors)
            )
            if vector not in allowed:
                return False
    return True


def _coefficient_domains(
    network: UnitCapacityDAG,
    source: str,
    source_dimension: int,
    prime: int,
) -> tuple[tuple[str, tuple[tuple[int, ...], ...]], ...]:
    domains: list[tuple[str, tuple[tuple[int, ...], ...]]] = []
    for node in network.topological_order():
        length = source_dimension if node == source else len(network.incoming(node))
        choices = tuple(product(range(prime), repeat=length))
        for edge in network.outgoing(node):
            domains.append((edge.edge_id, choices))
    return tuple(domains)


@dataclass(frozen=True)
class LinearCodeSearchResult:
    certificate: LinearMulticastCertificate | None
    assignments_examined: int
    total_assignments: int
    exhausted: bool

    @property
    def found(self) -> bool:
        return self.certificate is not None


def search_scalar_linear_multicast_code(
    network: UnitCapacityDAG,
    source: str,
    sinks: Sequence[str],
    source_dimension: int,
    field_prime: int,
    *,
    routing_only: bool = False,
    max_assignments: int = 1_000_000,
) -> LinearCodeSearchResult:
    prime = _validate_prime(field_prime)
    dimension = _validate_nonnegative_integer(
        source_dimension,
        name="source_dimension",
    )
    if dimension < 1:
        raise ValueError("source_dimension must be positive")
    limit = _validate_nonnegative_integer(
        max_assignments,
        name="max_assignments",
    )
    if limit < 1:
        raise ValueError("max_assignments must be positive")
    domains = _coefficient_domains(network, str(source), dimension, prime)
    total = prod(len(choices) for _, choices in domains)
    examined = 0
    for selected in product(*(choices for _, choices in domains)):
        if examined >= limit:
            return LinearCodeSearchResult(None, examined, total, False)
        examined += 1
        code = ScalarLinearCode(
            prime,
            str(source),
            tuple(str(sink) for sink in sinks),
            dimension,
            tuple(
                (edge_id, coefficients)
                for (edge_id, _), coefficients in zip(domains, selected)
            ),
        )
        certificate = evaluate_scalar_linear_code(network, code)
        if certificate.valid and (
            not routing_only or certificate_is_routing(certificate)
        ):
            return LinearCodeSearchResult(certificate, examined, total, False)
    return LinearCodeSearchResult(None, examined, total, True)


def butterfly_network() -> UnitCapacityDAG:
    return UnitCapacityDAG(
        ("s", "a", "b", "c", "d", "t1", "t2"),
        (
            UnitEdge("sa", "s", "a"),
            UnitEdge("sb", "s", "b"),
            UnitEdge("at1", "a", "t1"),
            UnitEdge("ac", "a", "c"),
            UnitEdge("bt2", "b", "t2"),
            UnitEdge("bc", "b", "c"),
            UnitEdge("cd", "c", "d"),
            UnitEdge("dt1", "d", "t1"),
            UnitEdge("dt2", "d", "t2"),
        ),
    )


def butterfly_linear_code() -> ScalarLinearCode:
    return ScalarLinearCode(
        2,
        "s",
        ("t1", "t2"),
        2,
        (
            ("sa", (1, 0)),
            ("sb", (0, 1)),
            ("ac", (1,)),
            ("at1", (1,)),
            ("bc", (1,)),
            ("bt2", (1,)),
            ("cd", (1, 1)),
            ("dt1", (1,)),
            ("dt2", (1,)),
        ),
    )


@dataclass(frozen=True)
class MulticastCutCertificate:
    source: str
    sinks: tuple[str, ...]
    required_symbols: int
    sink_min_cuts: tuple[tuple[str, int], ...]

    @property
    def necessary_cuts_hold(self) -> bool:
        return all(
            capacity >= self.required_symbols
            for _, capacity in self.sink_min_cuts
        )


def multicast_cut_certificate(
    network: UnitCapacityDAG,
    source: str,
    sinks: Sequence[str],
    required_symbols: int,
) -> MulticastCutCertificate:
    required = _validate_nonnegative_integer(
        required_symbols,
        name="required_symbols",
    )
    if required < 1:
        raise ValueError("required_symbols must be positive")
    supplied_sinks = tuple(str(sink) for sink in sinks)
    if not supplied_sinks or len(set(supplied_sinks)) != len(supplied_sinks):
        raise ValueError("unique sinks are required")
    return MulticastCutCertificate(
        str(source),
        supplied_sinks,
        required,
        tuple(
            (sink, network.min_cut_capacity(str(source), sink))
            for sink in supplied_sinks
        ),
    )


@dataclass(frozen=True)
class ButterflySeparationCertificate:
    cut_certificate: MulticastCutCertificate
    linear_certificate: LinearMulticastCertificate
    exhaustive_routing_result: LinearCodeSearchResult

    @property
    def valid(self) -> bool:
        return (
            self.cut_certificate.necessary_cuts_hold
            and self.linear_certificate.valid
            and not self.exhaustive_routing_result.found
            and self.exhaustive_routing_result.exhausted
        )


def butterfly_separation_certificate() -> ButterflySeparationCertificate:
    network = butterfly_network()
    linear = evaluate_scalar_linear_code(network, butterfly_linear_code())
    routing = search_scalar_linear_multicast_code(
        network,
        "s",
        ("t1", "t2"),
        2,
        2,
        routing_only=True,
        max_assignments=10_000,
    )
    certificate = ButterflySeparationCertificate(
        multicast_cut_certificate(network, "s", ("t1", "t2"), 2),
        linear,
        routing,
    )
    if not certificate.valid:
        raise AssertionError("butterfly routing/coding separation certificate failed")
    return certificate


def _integer_to_base_p_vector(value: int, length: int, prime: int) -> FieldVector:
    if value < 0 or length < 1:
        raise ValueError("value must be nonnegative and length positive")
    digits: list[int] = []
    remaining = value
    for _ in range(length):
        digits.append(remaining % prime)
        remaining //= prime
    if remaining:
        raise ValueError("value does not fit in the supplied field-vector length")
    return tuple(digits)


@dataclass(frozen=True)
class PredictiveMulticastCertificate:
    family: FiniteQueryFamily
    linear_certificate: LinearMulticastCertificate
    record_symbol_vectors: tuple[tuple[Hashable, FieldVector], ...]

    @property
    def valid(self) -> bool:
        return self.linear_certificate.valid and len(
            {vector for _, vector in self.record_symbol_vectors}
        ) == self.family.class_count


def predictive_multicast_certificate(
    family: FiniteQueryFamily,
    linear_certificate: LinearMulticastCertificate,
) -> PredictiveMulticastCertificate:
    code = linear_certificate.code
    capacity = code.field_prime ** code.source_dimension
    if family.class_count > capacity:
        raise ValueError("linear source vector has too few values for predictive classes")
    labels = family.class_label_map()
    class_vectors = {
        label: _integer_to_base_p_vector(
            label,
            code.source_dimension,
            code.field_prime,
        )
        for label in set(labels.values())
    }
    certificate = PredictiveMulticastCertificate(
        family,
        linear_certificate,
        tuple(
            (record, class_vectors[labels[record]])
            for record in family.records
        ),
    )
    if not certificate.valid:
        raise AssertionError("predictive class embedding into multicast symbols failed")
    return certificate
