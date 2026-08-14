"""Sink-specific linear predictive functions over finite causal networks.

A source holds x in F_p^h.  Sink t need not recover all of x; it may only need
specified linear functions B_t x and may already know side-information
functions S_t x.

If G_t contains the global encoding vectors of the network symbols arriving at
sink t, exact recovery is possible iff

    rowspace(B_t) subseteq rowspace(G_t union S_t).

Equivalently,

    rank([G_t; S_t; B_t]) = rank([G_t; S_t]).

The new information dimension required at one sink is

    rank([S_t; B_t]) - rank(S_t).

Every source-to-sink cut must carry at least that many independent field
symbols, but satisfying those receiver-wise cut inequalities is not sufficient
for several heterogeneous sinks sharing one bottleneck.

The module also solves a bounded common-summary problem.  It exhaustively
searches finite-field subspaces W in increasing dimension until

    rowspace(B_t) subseteq rowspace(W union S_t)

for every sink.  This yields an exact minimum common linear summary in the
declared bounded domain.

A two-receiver broadcast example separates three concepts:

* without side information, each sink individually needs one symbol but the
  shared summary needs dimension two;
* with complementary side information, one XOR symbol is sufficient;
* exhaustive F_2 search finds the XOR code and rules out every routing-only
  scalar assignment in the declared 16-assignment domain.

These are internal finite communication and predictive-function results.  They
are not evidence for simulation and do not turn field dimensions, messages,
side information, or cuts into parent-universe hardware, energy, mass, or
spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import prod
from typing import Hashable, Mapping, Sequence

from .network_coding import (
    FieldVector,
    LinearMulticastCertificate,
    ScalarLinearCode,
    UnitCapacityDAG,
    UnitEdge,
    certificate_is_routing,
    evaluate_scalar_linear_code,
    gf_rank,
    gf_solve,
)


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


def _validate_positive_integer(value: int, *, name: str) -> int:
    integer = int(value)
    if integer != value or integer < 1:
        raise ValueError(f"{name} must be a positive integer")
    return integer


def _canonical_row(
    row: Sequence[int],
    source_dimension: int,
    prime: int,
) -> FieldVector:
    values = tuple(int(value) % prime for value in row)
    if len(values) != source_dimension:
        raise ValueError("linear row has the wrong source dimension")
    return values


def _canonical_rows(
    rows: Sequence[Sequence[int]],
    source_dimension: int,
    prime: int,
    *,
    nonempty: bool,
) -> tuple[FieldVector, ...]:
    canonical = tuple(
        _canonical_row(row, source_dimension, prime)
        for row in rows
    )
    if nonempty and not canonical:
        raise ValueError("at least one target row is required")
    return canonical


def _basis_vector(length: int, index: int) -> FieldVector:
    if not 0 <= index < length:
        raise ValueError("basis index out of range")
    return tuple(1 if coordinate == index else 0 for coordinate in range(length))


def _zero_vector(length: int) -> FieldVector:
    return tuple(0 for _ in range(length))


def _dot(left: Sequence[int], right: Sequence[int], prime: int) -> int:
    if len(left) != len(right):
        raise ValueError("dot-product vectors must have equal length")
    return sum(int(a) * int(b) for a, b in zip(left, right)) % prime


def _linear_combination(
    coefficients: Sequence[int],
    vectors: Sequence[Sequence[int]],
    source_dimension: int,
    prime: int,
) -> FieldVector:
    supplied_coefficients = tuple(int(value) % prime for value in coefficients)
    supplied_vectors = tuple(
        _canonical_row(vector, source_dimension, prime)
        for vector in vectors
    )
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
        for coordinate in range(source_dimension)
    )


def gf_rref_basis(
    rows: Sequence[Sequence[int]],
    prime: int,
    *,
    width: int | None = None,
) -> tuple[FieldVector, ...]:
    """Canonical nonzero reduced-row-echelon basis over F_p."""

    modulus = _validate_prime(prime)
    supplied = tuple(tuple(int(value) % modulus for value in row) for row in rows)
    if width is None:
        if not supplied:
            raise ValueError("width is required for an empty row family")
        columns = len(supplied[0])
    else:
        columns = int(width)
        if columns != width or columns < 0:
            raise ValueError("width must be a nonnegative integer")
    if any(len(row) != columns for row in supplied):
        raise ValueError("matrix rows must have equal declared width")
    work = [list(row) for row in supplied if any(row)]
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(work))
                if work[row][column] % modulus != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], modulus - 2, modulus)
        work[pivot_row] = [
            (value * inverse) % modulus
            for value in work[pivot_row]
        ]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column] % modulus
            if factor:
                work[row] = [
                    (value - factor * pivot_value) % modulus
                    for value, pivot_value in zip(
                        work[row],
                        work[pivot_row],
                    )
                ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return tuple(
        tuple(row)
        for row in work[:pivot_row]
        if any(row)
    )


def rowspace_contains(
    spanning_rows: Sequence[Sequence[int]],
    target_rows: Sequence[Sequence[int]],
    source_dimension: int,
    prime: int,
) -> bool:
    """Whether every target row lies in the span of ``spanning_rows``."""

    modulus = _validate_prime(prime)
    width = _validate_positive_integer(
        source_dimension,
        name="source_dimension",
    )
    spanning = _canonical_rows(
        spanning_rows,
        width,
        modulus,
        nonempty=False,
    )
    targets = _canonical_rows(
        target_rows,
        width,
        modulus,
        nonempty=False,
    )
    return gf_rank(spanning, modulus) == gf_rank((*spanning, *targets), modulus)


def conditional_linear_rank(
    target_rows: Sequence[Sequence[int]],
    side_information_rows: Sequence[Sequence[int]],
    source_dimension: int,
    prime: int,
) -> int:
    """New linear dimensions in the target modulo local side information."""

    modulus = _validate_prime(prime)
    width = _validate_positive_integer(
        source_dimension,
        name="source_dimension",
    )
    targets = _canonical_rows(
        target_rows,
        width,
        modulus,
        nonempty=False,
    )
    side = _canonical_rows(
        side_information_rows,
        width,
        modulus,
        nonempty=False,
    )
    return gf_rank((*side, *targets), modulus) - gf_rank(side, modulus)


@dataclass(frozen=True)
class LinearSinkDemand:
    sink: str
    target_rows: tuple[FieldVector, ...]
    side_information_rows: tuple[FieldVector, ...] = ()

    def __post_init__(self) -> None:
        sink = str(self.sink)
        if not sink:
            raise ValueError("sink cannot be empty")
        if not self.target_rows:
            raise ValueError("at least one target row is required")
        object.__setattr__(self, "sink", sink)
        object.__setattr__(
            self,
            "target_rows",
            tuple(tuple(int(value) for value in row) for row in self.target_rows),
        )
        object.__setattr__(
            self,
            "side_information_rows",
            tuple(
                tuple(int(value) for value in row)
                for row in self.side_information_rows
            ),
        )


@dataclass(frozen=True)
class LinearFunctionProblem:
    field_prime: int
    source_dimension: int
    demands: tuple[LinearSinkDemand, ...]

    def __post_init__(self) -> None:
        prime = _validate_prime(self.field_prime)
        dimension = _validate_positive_integer(
            self.source_dimension,
            name="source_dimension",
        )
        supplied = tuple(self.demands)
        if not supplied or len({demand.sink for demand in supplied}) != len(supplied):
            raise ValueError("unique nonempty sink demands are required")
        canonical: list[LinearSinkDemand] = []
        for demand in supplied:
            canonical.append(
                LinearSinkDemand(
                    demand.sink,
                    _canonical_rows(
                        demand.target_rows,
                        dimension,
                        prime,
                        nonempty=True,
                    ),
                    _canonical_rows(
                        demand.side_information_rows,
                        dimension,
                        prime,
                        nonempty=False,
                    ),
                )
            )
        object.__setattr__(self, "field_prime", prime)
        object.__setattr__(self, "source_dimension", dimension)
        object.__setattr__(self, "demands", tuple(canonical))

    @property
    def sinks(self) -> tuple[str, ...]:
        return tuple(demand.sink for demand in self.demands)

    def demand(self, sink: str) -> LinearSinkDemand:
        target = str(sink)
        for demand in self.demands:
            if demand.sink == target:
                return demand
        raise ValueError("sink has no declared linear-function demand")

    def target_rank(self, sink: str) -> int:
        return gf_rank(self.demand(sink).target_rows, self.field_prime)

    def side_information_rank(self, sink: str) -> int:
        return gf_rank(
            self.demand(sink).side_information_rows,
            self.field_prime,
        )

    def conditional_rank(self, sink: str) -> int:
        demand = self.demand(sink)
        return conditional_linear_rank(
            demand.target_rows,
            demand.side_information_rows,
            self.source_dimension,
            self.field_prime,
        )

    def target_values(
        self,
        sink: str,
        source_vector: Sequence[int],
    ) -> tuple[int, ...]:
        source = _canonical_row(
            source_vector,
            self.source_dimension,
            self.field_prime,
        )
        return tuple(
            _dot(row, source, self.field_prime)
            for row in self.demand(sink).target_rows
        )

    def side_information_values(
        self,
        sink: str,
        source_vector: Sequence[int],
    ) -> tuple[int, ...]:
        source = _canonical_row(
            source_vector,
            self.source_dimension,
            self.field_prime,
        )
        return tuple(
            _dot(row, source, self.field_prime)
            for row in self.demand(sink).side_information_rows
        )


@dataclass(frozen=True)
class FunctionalSinkDecoder:
    sink: str
    incoming_edges: tuple[str, ...]
    incoming_vectors: tuple[FieldVector, ...]
    side_information_rows: tuple[FieldVector, ...]
    target_rows: tuple[FieldVector, ...]
    decoder_coefficients: tuple[FieldVector | None, ...]
    incoming_rank: int
    available_rank: int
    target_rank: int
    conditional_rank: int

    @property
    def recoverable(self) -> bool:
        return all(coefficients is not None for coefficients in self.decoder_coefficients)


@dataclass(frozen=True)
class LinearFunctionCodeCertificate:
    problem: LinearFunctionProblem
    propagation: LinearMulticastCertificate
    sink_decoders: tuple[FunctionalSinkDecoder, ...]

    @property
    def valid(self) -> bool:
        return all(decoder.recoverable for decoder in self.sink_decoders)

    def decoder(self, sink: str) -> FunctionalSinkDecoder:
        target = str(sink)
        for decoder in self.sink_decoders:
            if decoder.sink == target:
                return decoder
        raise ValueError("sink has no decoder certificate")

    def decode(
        self,
        sink: str,
        source_vector: Sequence[int],
    ) -> tuple[int, ...]:
        decoder = self.decoder(sink)
        if not decoder.recoverable:
            raise ValueError("sink demand is not recoverable by this code")
        source = _canonical_row(
            source_vector,
            self.problem.source_dimension,
            self.problem.field_prime,
        )
        global_vectors = self.propagation.global_vector_map()
        incoming_values = tuple(
            _dot(global_vectors[edge_id], source, self.problem.field_prime)
            for edge_id in decoder.incoming_edges
        )
        side_values = tuple(
            _dot(row, source, self.problem.field_prime)
            for row in decoder.side_information_rows
        )
        available_values = (*incoming_values, *side_values)
        outputs: list[int] = []
        for coefficients in decoder.decoder_coefficients:
            if coefficients is None:
                raise ValueError("sink demand is not recoverable by this code")
            outputs.append(
                sum(
                    coefficient * value
                    for coefficient, value in zip(coefficients, available_values)
                )
                % self.problem.field_prime
            )
        return tuple(outputs)


def _decoder_coefficients(
    available_vectors: Sequence[Sequence[int]],
    target_rows: Sequence[Sequence[int]],
    source_dimension: int,
    prime: int,
) -> tuple[FieldVector | None, ...]:
    available = tuple(
        _canonical_row(vector, source_dimension, prime)
        for vector in available_vectors
    )
    matrix = tuple(
        tuple(vector[coordinate] for vector in available)
        for coordinate in range(source_dimension)
    )
    return tuple(
        gf_solve(matrix, target, prime)
        for target in target_rows
    )


def evaluate_linear_function_code(
    network: UnitCapacityDAG,
    code: ScalarLinearCode,
    problem: LinearFunctionProblem,
) -> LinearFunctionCodeCertificate:
    if code.field_prime != problem.field_prime:
        raise ValueError("code and function problem use different fields")
    if code.source_dimension != problem.source_dimension:
        raise ValueError("code and function problem use different source dimensions")
    if set(code.sinks) != set(problem.sinks):
        raise ValueError("code sinks must match the declared function-demand sinks")
    propagation = evaluate_scalar_linear_code(network, code)
    vectors = propagation.global_vector_map()
    decoders: list[FunctionalSinkDecoder] = []
    for demand in problem.demands:
        incoming = network.incoming(demand.sink)
        incoming_vectors = tuple(vectors[edge.edge_id] for edge in incoming)
        available = (*incoming_vectors, *demand.side_information_rows)
        coefficients = _decoder_coefficients(
            available,
            demand.target_rows,
            problem.source_dimension,
            problem.field_prime,
        )
        decoder = FunctionalSinkDecoder(
            demand.sink,
            tuple(edge.edge_id for edge in incoming),
            incoming_vectors,
            demand.side_information_rows,
            demand.target_rows,
            coefficients,
            gf_rank(incoming_vectors, problem.field_prime),
            gf_rank(available, problem.field_prime),
            gf_rank(demand.target_rows, problem.field_prime),
            problem.conditional_rank(demand.sink),
        )
        rank_condition = rowspace_contains(
            available,
            demand.target_rows,
            problem.source_dimension,
            problem.field_prime,
        )
        if decoder.recoverable != rank_condition:
            raise AssertionError("decoder solve and row-space criterion disagree")
        decoders.append(decoder)
    return LinearFunctionCodeCertificate(
        problem,
        propagation,
        tuple(decoders),
    )


@dataclass(frozen=True)
class FunctionalCutCertificate:
    sink: str
    min_cut_symbols: int
    conditional_demand_rank: int

    @property
    def necessary_cut_holds(self) -> bool:
        return self.min_cut_symbols >= self.conditional_demand_rank


def functional_cut_certificates(
    network: UnitCapacityDAG,
    source: str,
    problem: LinearFunctionProblem,
) -> tuple[FunctionalCutCertificate, ...]:
    return tuple(
        FunctionalCutCertificate(
            sink,
            network.min_cut_capacity(source, sink),
            problem.conditional_rank(sink),
        )
        for sink in problem.sinks
    )


def _coefficient_domains(
    network: UnitCapacityDAG,
    source: str,
    source_dimension: int,
    prime: int,
) -> tuple[tuple[str, tuple[FieldVector, ...]], ...]:
    domains: list[tuple[str, tuple[FieldVector, ...]]] = []
    for node in network.topological_order():
        length = source_dimension if node == source else len(network.incoming(node))
        choices = tuple(product(range(prime), repeat=length))
        for edge in network.outgoing(node):
            domains.append((edge.edge_id, choices))
    return tuple(domains)


@dataclass(frozen=True)
class LinearFunctionCodeSearchResult:
    certificate: LinearFunctionCodeCertificate | None
    assignments_examined: int
    total_assignments: int
    exhausted: bool

    @property
    def found(self) -> bool:
        return self.certificate is not None


def search_scalar_linear_function_code(
    network: UnitCapacityDAG,
    source: str,
    problem: LinearFunctionProblem,
    *,
    routing_only: bool = False,
    max_assignments: int = 1_000_000,
) -> LinearFunctionCodeSearchResult:
    limit = _validate_positive_integer(
        max_assignments,
        name="max_assignments",
    )
    domains = _coefficient_domains(
        network,
        str(source),
        problem.source_dimension,
        problem.field_prime,
    )
    total = prod(len(choices) for _, choices in domains)
    examined = 0
    for selected in product(*(choices for _, choices in domains)):
        if examined >= limit:
            return LinearFunctionCodeSearchResult(None, examined, total, False)
        examined += 1
        code = ScalarLinearCode(
            problem.field_prime,
            str(source),
            problem.sinks,
            problem.source_dimension,
            tuple(
                (edge_id, coefficients)
                for (edge_id, _), coefficients in zip(domains, selected)
            ),
        )
        certificate = evaluate_linear_function_code(network, code, problem)
        if certificate.valid and (
            not routing_only
            or certificate_is_routing(certificate.propagation)
        ):
            return LinearFunctionCodeSearchResult(
                certificate,
                examined,
                total,
                False,
            )
    return LinearFunctionCodeSearchResult(None, examined, total, True)


def common_summary_satisfies(
    problem: LinearFunctionProblem,
    summary_basis: Sequence[Sequence[int]],
) -> bool:
    basis = _canonical_rows(
        summary_basis,
        problem.source_dimension,
        problem.field_prime,
        nonempty=False,
    )
    return all(
        rowspace_contains(
            (*basis, *demand.side_information_rows),
            demand.target_rows,
            problem.source_dimension,
            problem.field_prime,
        )
        for demand in problem.demands
    )


@dataclass(frozen=True)
class CommonLinearSummaryResult:
    basis: tuple[FieldVector, ...] | None
    dimension: int | None
    generator_sets_examined: int
    unique_subspaces_examined: int
    complete: bool

    @property
    def found(self) -> bool:
        return self.basis is not None


def minimum_common_linear_summary(
    problem: LinearFunctionProblem,
    *,
    max_generator_sets: int = 1_000_000,
) -> CommonLinearSummaryResult:
    """Exact bounded search for the minimum common linear message subspace.

    Search proceeds by subspace dimension.  Every r-dimensional subspace has a
    basis of r distinct nonzero vectors, so enumerating all such generator sets,
    canonicalizing them to RREF, and deduplicating covers every subspace.  A
    configured cap returns an explicitly incomplete result rather than a false
    optimum or impossibility claim.
    """

    limit = _validate_positive_integer(
        max_generator_sets,
        name="max_generator_sets",
    )
    if common_summary_satisfies(problem, ()):
        return CommonLinearSummaryResult((), 0, 0, 1, True)

    nonzero_vectors = tuple(
        vector
        for vector in product(
            range(problem.field_prime),
            repeat=problem.source_dimension,
        )
        if any(vector)
    )
    examined = 0
    unique = 1
    for dimension in range(1, problem.source_dimension + 1):
        seen: set[tuple[FieldVector, ...]] = set()
        for generators in combinations(nonzero_vectors, dimension):
            if examined >= limit:
                return CommonLinearSummaryResult(
                    None,
                    None,
                    examined,
                    unique,
                    False,
                )
            examined += 1
            if gf_rank(generators, problem.field_prime) != dimension:
                continue
            basis = gf_rref_basis(
                generators,
                problem.field_prime,
                width=problem.source_dimension,
            )
            if basis in seen:
                continue
            seen.add(basis)
            unique += 1
            if common_summary_satisfies(problem, basis):
                return CommonLinearSummaryResult(
                    basis,
                    dimension,
                    examined,
                    unique,
                    True,
                )
    raise AssertionError("the full source space must satisfy every linear demand")


def broadcast_network() -> UnitCapacityDAG:
    """One source symbol is copied by a relay to two receivers."""

    return UnitCapacityDAG(
        ("s", "b", "t1", "t2"),
        (
            UnitEdge("sb", "s", "b"),
            UnitEdge("bt1", "b", "t1"),
            UnitEdge("bt2", "b", "t2"),
        ),
    )


def heterogeneous_no_side_information_problem() -> LinearFunctionProblem:
    """t1 wants x1 and t2 wants x2, with no local side information."""

    return LinearFunctionProblem(
        2,
        2,
        (
            LinearSinkDemand("t1", ((1, 0),)),
            LinearSinkDemand("t2", ((0, 1),)),
        ),
    )


def complementary_side_information_problem() -> LinearFunctionProblem:
    """t1 knows x1 and wants x2; t2 knows x2 and wants x1."""

    return LinearFunctionProblem(
        2,
        2,
        (
            LinearSinkDemand("t1", ((0, 1),), ((1, 0),)),
            LinearSinkDemand("t2", ((1, 0),), ((0, 1),)),
        ),
    )


def xor_broadcast_code() -> ScalarLinearCode:
    return ScalarLinearCode(
        2,
        "s",
        ("t1", "t2"),
        2,
        (
            ("sb", (1, 1)),
            ("bt1", (1,)),
            ("bt2", (1,)),
        ),
    )


@dataclass(frozen=True)
class SideInformationBroadcastSeparation:
    no_side_summary: CommonLinearSummaryResult
    side_information_summary: CommonLinearSummaryResult
    side_information_linear_code: LinearFunctionCodeCertificate
    no_side_network_search: LinearFunctionCodeSearchResult
    side_information_routing_search: LinearFunctionCodeSearchResult
    side_information_linear_search: LinearFunctionCodeSearchResult
    per_sink_cuts: tuple[FunctionalCutCertificate, ...]

    @property
    def valid(self) -> bool:
        return (
            self.no_side_summary.complete
            and self.no_side_summary.dimension == 2
            and self.side_information_summary.complete
            and self.side_information_summary.dimension == 1
            and self.side_information_summary.basis == ((1, 1),)
            and self.side_information_linear_code.valid
            and not self.no_side_network_search.found
            and self.no_side_network_search.exhausted
            and not self.side_information_routing_search.found
            and self.side_information_routing_search.exhausted
            and self.side_information_linear_search.found
            and all(cut.necessary_cut_holds for cut in self.per_sink_cuts)
        )


def side_information_broadcast_separation() -> SideInformationBroadcastSeparation:
    network = broadcast_network()
    no_side = heterogeneous_no_side_information_problem()
    with_side = complementary_side_information_problem()
    certificate = SideInformationBroadcastSeparation(
        minimum_common_linear_summary(no_side),
        minimum_common_linear_summary(with_side),
        evaluate_linear_function_code(
            network,
            xor_broadcast_code(),
            with_side,
        ),
        search_scalar_linear_function_code(
            network,
            "s",
            no_side,
            max_assignments=100,
        ),
        search_scalar_linear_function_code(
            network,
            "s",
            with_side,
            routing_only=True,
            max_assignments=100,
        ),
        search_scalar_linear_function_code(
            network,
            "s",
            with_side,
            max_assignments=100,
        ),
        functional_cut_certificates(network, "s", with_side),
    )
    if not certificate.valid:
        raise AssertionError("side-information broadcast separation failed")
    return certificate


def linear_signature_map(
    records: Mapping[Hashable, Sequence[int]],
    rows: Sequence[Sequence[int]],
    source_dimension: int,
    prime: int,
) -> dict[Hashable, tuple[int, ...]]:
    """Map embedded predictive classes to one declared linear sink signature."""

    modulus = _validate_prime(prime)
    dimension = _validate_positive_integer(
        source_dimension,
        name="source_dimension",
    )
    target_rows = _canonical_rows(
        rows,
        dimension,
        modulus,
        nonempty=True,
    )
    return {
        record: tuple(
            _dot(row, _canonical_row(vector, dimension, modulus), modulus)
            for row in target_rows
        )
        for record, vector in records.items()
    }
