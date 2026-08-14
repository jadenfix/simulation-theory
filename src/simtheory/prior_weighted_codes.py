"""Exact prior-weighted zero-error prefix coding for finite confusion graphs.

The chromatic number of a confusion graph answers a worst-case one-shot
question: how many distinct message labels are required when every declared
source state must be decoded with zero error?  It does not by itself answer how
many bits are used on average when source states have a declared prior and the
message is sent with a binary prefix code.

A deterministic zero-error encoder partitions the graph vertices into
independent color classes.  Under a rational source prior, every class has an
exact rational probability.  For one fixed partition, Huffman's algorithm gives
an exact minimum expected binary prefix length.  Enumerating every canonical
proper partition below explicit finite caps therefore gives the exact global
one-shot optimum.

The implementation keeps several commonly conflated resources separate:

* chromatic number: minimum message alphabet size;
* fixed-length bits: ceil(log2(chi));
* expected prefix length under one prior;
* maximum prefix length of the selected variable-length code;
* declared-state zero error versus positive-support-only zero error;
* the number of color classes in an average-optimal code versus chi.

All arithmetic that determines feasibility or expected length is rational.
Floating point is used only to display Shannon entropy after the exact ordering
of rational color distributions has already been established.

These are finite internal source-coding results.  They are not evidence for
simulation and do not identify messages, codewords, or average bit lengths with
parent-universe hardware, energy, mass, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from math import lcm, log2
from typing import Iterable, Mapping, Sequence

from .confusion_graphs import (
    ChromaticCertificate,
    ConfusionGraph,
    FiniteFunctionProblem,
    coloring_is_proper,
    deterministic_code_from_coloring,
    exact_chromatic_certificate,
)

RationalInput = int | str | Fraction
Partition = tuple[tuple[int, ...], ...]


def _ceil_log2_integer(value: int) -> int:
    integer = int(value)
    if integer != value or integer < 1:
        raise ValueError("value must be a positive integer")
    return 0 if integer == 1 else (integer - 1).bit_length()


def _as_fraction(value: RationalInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(
            f"{name} must be supplied as int, str, or Fraction for exact arithmetic"
        )
    try:
        result = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{name} is not an exact rational value") from error
    return result


def validate_rational_prior(
    graph: ConfusionGraph,
    probabilities: Sequence[RationalInput] | Mapping[object, RationalInput],
) -> tuple[Fraction, ...]:
    """Validate an exact prior aligned with the graph's vertex order."""

    if isinstance(probabilities, Mapping):
        if set(probabilities) != set(graph.vertices):
            raise ValueError("prior mapping must define exactly every graph vertex")
        supplied = tuple(probabilities[vertex] for vertex in graph.vertices)
    else:
        supplied = tuple(probabilities)
    if len(supplied) != graph.vertex_count:
        raise ValueError("one prior probability is required per graph vertex")
    prior = tuple(
        _as_fraction(value, name="prior probability")
        for value in supplied
    )
    if any(probability < 0 for probability in prior):
        raise ValueError("prior probabilities must be nonnegative")
    if sum(prior, Fraction(0)) != 1:
        raise ValueError("prior probabilities must sum exactly to one")
    return prior


def canonicalize_partition(partition: Sequence[Sequence[int]]) -> Partition:
    """Return an unlabeled partition in increasing first-vertex order."""

    blocks = tuple(tuple(sorted(int(vertex) for vertex in block)) for block in partition)
    if not blocks or any(not block for block in blocks):
        raise ValueError("a partition must contain nonempty blocks")
    if any(len(set(block)) != len(block) for block in blocks):
        raise ValueError("a partition block contains a duplicate vertex")
    return tuple(sorted(blocks, key=lambda block: (block[0], block)))


def partition_is_proper(graph: ConfusionGraph, partition: Sequence[Sequence[int]]) -> bool:
    """Whether the blocks form an exact independent-set partition of the graph."""

    try:
        canonical = canonicalize_partition(partition)
    except ValueError:
        return False
    seen = 0
    for block in canonical:
        block_mask = 0
        for vertex in block:
            if not 0 <= vertex < graph.vertex_count:
                return False
            bit = 1 << vertex
            if seen & bit or block_mask & bit:
                return False
            if graph.adjacency_masks[vertex] & block_mask:
                return False
            block_mask |= bit
        seen |= block_mask
    return seen == (1 << graph.vertex_count) - 1


def coloring_from_partition(graph: ConfusionGraph, partition: Sequence[Sequence[int]]) -> tuple[int, ...]:
    canonical = canonicalize_partition(partition)
    if not partition_is_proper(graph, canonical):
        raise ValueError("partition is not a proper graph coloring")
    colors = [-1] * graph.vertex_count
    for color, block in enumerate(canonical):
        for vertex in block:
            colors[vertex] = color
    result = tuple(colors)
    if not coloring_is_proper(graph, result):
        raise AssertionError("proper partition unexpectedly produced an improper coloring")
    return result


def iter_proper_partitions(
    graph: ConfusionGraph,
    *,
    max_vertices: int = 11,
    max_partitions: int = 2_000_000,
) -> Iterable[Partition]:
    """Enumerate every unlabeled proper color partition below explicit caps.

    Restricted-growth order removes color-label permutations: vertex ``v`` may
    join an existing independent block or open exactly one new final block.
    If the partition cap is exceeded, the function raises instead of returning
    a partial search that could be mistaken for an optimum certificate.
    """

    vertex_cap = int(max_vertices)
    partition_cap = int(max_partitions)
    if vertex_cap < 1 or partition_cap < 1:
        raise ValueError("search caps must be positive integers")
    if graph.vertex_count > vertex_cap:
        raise ValueError(
            f"exact proper-partition search capped at {vertex_cap} vertices"
        )

    blocks: list[list[int]] = []
    emitted = 0

    def search(vertex: int) -> Iterable[Partition]:
        nonlocal emitted
        if vertex == graph.vertex_count:
            emitted += 1
            if emitted > partition_cap:
                raise ValueError(
                    "proper-partition enumeration exceeded the configured cap; "
                    "no exact optimum was certified"
                )
            yield tuple(tuple(block) for block in blocks)
            return

        adjacency = graph.adjacency_masks[vertex]
        for block in blocks:
            block_mask = sum(1 << member for member in block)
            if adjacency & block_mask:
                continue
            block.append(vertex)
            yield from search(vertex + 1)
            block.pop()

        blocks.append([vertex])
        yield from search(vertex + 1)
        blocks.pop()

    yield from search(0)


def class_probabilities(
    partition: Sequence[Sequence[int]],
    prior: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    canonical = canonicalize_partition(partition)
    return tuple(
        sum((prior[vertex] for vertex in block), Fraction(0))
        for block in canonical
    )


def prefix_free(codewords: Sequence[str]) -> bool:
    supplied = tuple(str(codeword) for codeword in codewords)
    if any(set(codeword) - {"0", "1"} for codeword in supplied):
        return False
    if len(set(supplied)) != len(supplied):
        return False
    return all(
        not right.startswith(left)
        for left_index, left in enumerate(supplied)
        for right_index, right in enumerate(supplied)
        if left_index != right_index
    )


@dataclass(frozen=True)
class _HuffmanNode:
    weight: Fraction
    minimum_symbol: int
    serial: int
    symbol: int | None = None
    left: _HuffmanNode | None = None
    right: _HuffmanNode | None = None


@dataclass(frozen=True)
class PrefixCodeCertificate:
    probabilities: tuple[Fraction, ...]
    codewords: tuple[str, ...]
    lengths: tuple[int, ...]
    expected_length: Fraction
    merge_cost: Fraction
    kraft_sum: Fraction

    @property
    def maximum_length(self) -> int:
        return max(self.lengths)

    @property
    def message_count(self) -> int:
        return len(self.probabilities)

    @property
    def valid(self) -> bool:
        return (
            bool(self.probabilities)
            and all(probability >= 0 for probability in self.probabilities)
            and sum(self.probabilities, Fraction(0)) == 1
            and len(self.codewords) == len(self.probabilities)
            and self.lengths == tuple(len(codeword) for codeword in self.codewords)
            and prefix_free(self.codewords)
            and self.kraft_sum
            == sum(
                (Fraction(1, 1 << length) for length in self.lengths),
                Fraction(0),
            )
            and self.kraft_sum <= 1
            and self.expected_length
            == sum(
                (
                    probability * length
                    for probability, length in zip(
                        self.probabilities,
                        self.lengths,
                    )
                ),
                Fraction(0),
            )
            and self.expected_length == self.merge_cost
        )


def optimal_binary_prefix_code(
    probabilities: Sequence[RationalInput | Fraction],
) -> PrefixCodeCertificate:
    """Exact Huffman-optimal binary prefix code for a rational distribution."""

    supplied = tuple(
        _as_fraction(probability, name="message probability")
        if not isinstance(probability, Fraction)
        else probability
        for probability in probabilities
    )
    if not supplied:
        raise ValueError("at least one message probability is required")
    if any(probability < 0 for probability in supplied):
        raise ValueError("message probabilities must be nonnegative")
    if sum(supplied, Fraction(0)) != 1:
        raise ValueError("message probabilities must sum exactly to one")

    if len(supplied) == 1:
        certificate = PrefixCodeCertificate(
            supplied,
            ("",),
            (0,),
            Fraction(0),
            Fraction(0),
            Fraction(1),
        )
        if not certificate.valid:
            raise AssertionError("one-symbol prefix certificate failed")
        return certificate

    heap: list[tuple[Fraction, int, int, _HuffmanNode]] = []
    serial = 0
    for symbol, probability in enumerate(supplied):
        node = _HuffmanNode(
            probability,
            symbol,
            serial,
            symbol=symbol,
        )
        heappush(
            heap,
            (node.weight, node.minimum_symbol, node.serial, node),
        )
        serial += 1

    merge_cost = Fraction(0)
    while len(heap) > 1:
        _, _, _, left = heappop(heap)
        _, _, _, right = heappop(heap)
        weight = left.weight + right.weight
        merge_cost += weight
        parent = _HuffmanNode(
            weight,
            min(left.minimum_symbol, right.minimum_symbol),
            serial,
            left=left,
            right=right,
        )
        heappush(
            heap,
            (parent.weight, parent.minimum_symbol, parent.serial, parent),
        )
        serial += 1

    root = heap[0][3]
    words = [""] * len(supplied)

    def assign(node: _HuffmanNode, prefix: str) -> None:
        if node.symbol is not None:
            words[node.symbol] = prefix
            return
        if node.left is None or node.right is None:
            raise AssertionError("internal Huffman node is missing a child")
        assign(node.left, prefix + "0")
        assign(node.right, prefix + "1")

    assign(root, "")
    codewords = tuple(words)
    lengths = tuple(len(codeword) for codeword in codewords)
    expected = sum(
        (
            probability * length
            for probability, length in zip(supplied, lengths)
        ),
        Fraction(0),
    )
    certificate = PrefixCodeCertificate(
        supplied,
        codewords,
        lengths,
        expected,
        merge_cost,
        sum(
            (Fraction(1, 1 << length) for length in lengths),
            Fraction(0),
        ),
    )
    if not certificate.valid:
        raise AssertionError("Huffman prefix certificate failed validation")
    return certificate


def entropy_bits(probabilities: Sequence[Fraction]) -> float:
    return -sum(
        float(probability) * log2(float(probability))
        for probability in probabilities
        if probability > 0
    )


def common_prior_denominator(prior: Sequence[Fraction]) -> int:
    denominator = 1
    for probability in prior:
        denominator = lcm(denominator, probability.denominator)
    return denominator


def exact_entropy_order_product(
    probabilities: Sequence[Fraction],
    denominator: int,
) -> Fraction:
    """Exact monotone key for entropy comparison under rational probabilities.

    If ``D * p_i`` is integral for every probability, then

        product_i p_i ** (D p_i) = 2 ** (-D H_2(p)).

    Larger products therefore mean smaller Shannon entropy.  Zero-mass terms
    contribute the usual ``0 log 0 = 0`` and are skipped.
    """

    scale = int(denominator)
    if scale < 1:
        raise ValueError("entropy denominator must be positive")
    if any(probability < 0 for probability in probabilities):
        raise ValueError("entropy probabilities must be nonnegative")
    if sum(probabilities, Fraction(0)) != 1:
        raise ValueError("entropy probabilities must sum to one")
    product_value = Fraction(1)
    for probability in probabilities:
        exponent = probability * scale
        if exponent.denominator != 1:
            raise ValueError("entropy denominator does not clear all probabilities")
        if probability > 0 and exponent.numerator:
            product_value *= probability ** exponent.numerator
    return product_value


@dataclass(frozen=True)
class PartitionPrefixCode:
    graph: ConfusionGraph
    prior: tuple[Fraction, ...]
    partition: Partition
    coloring: tuple[int, ...]
    class_probabilities: tuple[Fraction, ...]
    prefix_code: PrefixCodeCertificate

    @property
    def message_count(self) -> int:
        return len(self.partition)

    @property
    def expected_length(self) -> Fraction:
        return self.prefix_code.expected_length

    @property
    def maximum_length(self) -> int:
        return self.prefix_code.maximum_length

    def message_for_vertex_index(self, vertex_index: int) -> int:
        if not 0 <= vertex_index < self.graph.vertex_count:
            raise ValueError("vertex index out of range")
        return self.coloring[vertex_index]

    def codeword_for_vertex_index(self, vertex_index: int) -> str:
        return self.prefix_code.codewords[
            self.message_for_vertex_index(vertex_index)
        ]

    @property
    def state_codewords(self) -> tuple[str, ...]:
        return tuple(
            self.codeword_for_vertex_index(index)
            for index in range(self.graph.vertex_count)
        )

    @property
    def valid(self) -> bool:
        return (
            len(self.prior) == self.graph.vertex_count
            and sum(self.prior, Fraction(0)) == 1
            and partition_is_proper(self.graph, self.partition)
            and self.coloring
            == coloring_from_partition(self.graph, self.partition)
            and self.class_probabilities
            == class_probabilities(self.partition, self.prior)
            and self.prefix_code.valid
            and self.prefix_code.probabilities == self.class_probabilities
        )


def partition_prefix_code(
    graph: ConfusionGraph,
    prior: Sequence[Fraction],
    partition: Sequence[Sequence[int]],
) -> PartitionPrefixCode:
    canonical = canonicalize_partition(partition)
    if not partition_is_proper(graph, canonical):
        raise ValueError("partition is not a proper zero-error coloring")
    probabilities = class_probabilities(canonical, prior)
    certificate = PartitionPrefixCode(
        graph,
        tuple(prior),
        canonical,
        coloring_from_partition(graph, canonical),
        probabilities,
        optimal_binary_prefix_code(probabilities),
    )
    if not certificate.valid:
        raise AssertionError("partition prefix code failed validation")
    return certificate


@dataclass(frozen=True)
class MessageCountPoint:
    message_count: int
    exact_best_expected_length: Fraction
    at_most_expected_length: Fraction
    exact_best_partition: Partition


@dataclass(frozen=True)
class PriorWeightedCodeCertificate:
    graph: ConfusionGraph
    prior: tuple[Fraction, ...]
    expected_optimal_code: PartitionPrefixCode
    entropy_optimal_partition: Partition
    entropy_optimal_probabilities: tuple[Fraction, ...]
    entropy_order_denominator: int
    entropy_order_product: Fraction
    minimum_coloring_entropy_bits: float
    chromatic_certificate: ChromaticCertificate
    message_count_frontier: tuple[MessageCountPoint, ...]
    partitions_examined: int
    max_vertices: int
    max_partitions: int

    @property
    def expected_length(self) -> Fraction:
        return self.expected_optimal_code.expected_length

    @property
    def expected_optimal_message_count(self) -> int:
        return self.expected_optimal_code.message_count

    @property
    def maximum_codeword_length(self) -> int:
        return self.expected_optimal_code.maximum_length

    @property
    def chromatic_number(self) -> int:
        return self.chromatic_certificate.chromatic_number

    @property
    def fixed_length_bits(self) -> int:
        return self.chromatic_certificate.fixed_length_bits

    @property
    def entropy_redundancy(self) -> float:
        return float(self.expected_length) - self.minimum_coloring_entropy_bits

    @property
    def valid(self) -> bool:
        expected = float(self.expected_length)
        entropy = self.minimum_coloring_entropy_bits
        frontier_counts = tuple(
            point.message_count for point in self.message_count_frontier
        )
        return (
            self.expected_optimal_code.valid
            and self.chromatic_certificate.valid
            and self.prior == self.expected_optimal_code.prior
            and partition_is_proper(
                self.graph,
                self.entropy_optimal_partition,
            )
            and self.entropy_optimal_probabilities
            == class_probabilities(
                self.entropy_optimal_partition,
                self.prior,
            )
            and self.entropy_order_product
            == exact_entropy_order_product(
                self.entropy_optimal_probabilities,
                self.entropy_order_denominator,
            )
            and self.partitions_examined >= 1
            and frontier_counts
            == tuple(
                range(
                    self.chromatic_number,
                    self.graph.vertex_count + 1,
                )
            )
            and entropy <= expected + 1e-12
            and expected < entropy + 1.0 + 1e-12
            and self.expected_length <= self.fixed_length_bits
        )


def exact_prior_weighted_prefix_code(
    graph: ConfusionGraph,
    probabilities: Sequence[RationalInput] | Mapping[object, RationalInput],
    *,
    max_vertices: int = 11,
    max_partitions: int = 2_000_000,
) -> PriorWeightedCodeCertificate:
    """Exact bounded minimum expected zero-error binary prefix code."""

    prior = validate_rational_prior(graph, probabilities)
    denominator = common_prior_denominator(prior)
    chromatic = exact_chromatic_certificate(
        graph,
        max_vertices=max_vertices,
    )

    expected_best: PartitionPrefixCode | None = None
    entropy_best_partition: Partition | None = None
    entropy_best_probabilities: tuple[Fraction, ...] | None = None
    entropy_best_product: Fraction | None = None
    exact_by_messages: dict[int, PartitionPrefixCode] = {}
    partitions_examined = 0

    for partition in iter_proper_partitions(
        graph,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    ):
        partitions_examined += 1
        candidate = partition_prefix_code(graph, prior, partition)
        message_count = candidate.message_count
        incumbent = exact_by_messages.get(message_count)
        candidate_key = (
            candidate.expected_length,
            candidate.maximum_length,
            candidate.partition,
        )
        if incumbent is None or candidate_key < (
            incumbent.expected_length,
            incumbent.maximum_length,
            incumbent.partition,
        ):
            exact_by_messages[message_count] = candidate

        if expected_best is None or candidate_key < (
            expected_best.expected_length,
            expected_best.maximum_length,
            expected_best.partition,
        ):
            expected_best = candidate

        entropy_product_value = exact_entropy_order_product(
            candidate.class_probabilities,
            denominator,
        )
        if (
            entropy_best_product is None
            or entropy_product_value > entropy_best_product
            or (
                entropy_product_value == entropy_best_product
                and (
                    candidate.message_count,
                    candidate.partition,
                )
                < (
                    len(entropy_best_partition or ()),
                    entropy_best_partition or (),
                )
            )
        ):
            entropy_best_partition = candidate.partition
            entropy_best_probabilities = candidate.class_probabilities
            entropy_best_product = entropy_product_value

    if (
        expected_best is None
        or entropy_best_partition is None
        or entropy_best_probabilities is None
        or entropy_best_product is None
    ):
        raise AssertionError("finite graph must have at least one proper partition")

    missing_counts = tuple(
        count
        for count in range(chromatic.chromatic_number, graph.vertex_count + 1)
        if count not in exact_by_messages
    )
    if missing_counts:
        raise AssertionError(
            f"proper partition enumeration missed message counts {missing_counts}"
        )

    frontier: list[MessageCountPoint] = []
    at_most = None
    for message_count in range(
        chromatic.chromatic_number,
        graph.vertex_count + 1,
    ):
        exact = exact_by_messages[message_count]
        at_most = (
            exact.expected_length
            if at_most is None
            else min(at_most, exact.expected_length)
        )
        frontier.append(
            MessageCountPoint(
                message_count,
                exact.expected_length,
                at_most,
                exact.partition,
            )
        )

    certificate = PriorWeightedCodeCertificate(
        graph,
        prior,
        expected_best,
        entropy_best_partition,
        entropy_best_probabilities,
        denominator,
        entropy_best_product,
        entropy_bits(entropy_best_probabilities),
        chromatic,
        tuple(frontier),
        partitions_examined,
        int(max_vertices),
        int(max_partitions),
    )
    if not certificate.valid:
        raise AssertionError("prior-weighted code certificate failed validation")
    return certificate


@dataclass(frozen=True)
class PriorWeightedFunctionCodeCertificate:
    problem: FiniteFunctionProblem
    weighted_code: PriorWeightedCodeCertificate

    @property
    def deterministic_message_code_valid(self) -> bool:
        return deterministic_code_from_coloring(
            self.problem,
            self.weighted_code.expected_optimal_code.coloring,
        ).valid

    @property
    def valid(self) -> bool:
        return (
            self.weighted_code.valid
            and self.problem.states == self.weighted_code.graph.vertices
            and self.deterministic_message_code_valid
        )


def exact_prior_weighted_function_code(
    problem: FiniteFunctionProblem,
    probabilities: Sequence[RationalInput] | Mapping[object, RationalInput],
    *,
    max_vertices: int = 11,
    max_partitions: int = 2_000_000,
) -> PriorWeightedFunctionCodeCertificate:
    from .confusion_graphs import confusion_graph

    certificate = PriorWeightedFunctionCodeCertificate(
        problem,
        exact_prior_weighted_prefix_code(
            confusion_graph(problem),
            probabilities,
            max_vertices=max_vertices,
            max_partitions=max_partitions,
        ),
    )
    if not certificate.valid:
        raise AssertionError("prior-weighted function code failed validation")
    return certificate


def graph_is_spanning_subgraph(
    reduced: ConfusionGraph,
    original: ConfusionGraph,
) -> bool:
    return (
        reduced.vertices == original.vertices
        and all(
            reduced_mask & ~original_mask == 0
            for reduced_mask, original_mask in zip(
                reduced.adjacency_masks,
                original.adjacency_masks,
            )
        )
    )


@dataclass(frozen=True)
class PriorWeightedMonotonicityCertificate:
    original: PriorWeightedCodeCertificate
    reduced: PriorWeightedCodeCertificate

    @property
    def valid(self) -> bool:
        return (
            graph_is_spanning_subgraph(
                self.reduced.graph,
                self.original.graph,
            )
            and self.reduced.prior == self.original.prior
            and self.reduced.expected_length <= self.original.expected_length
            and self.reduced.chromatic_number <= self.original.chromatic_number
        )


def prior_weighted_edge_deletion_certificate(
    original: ConfusionGraph,
    reduced: ConfusionGraph,
    probabilities: Sequence[RationalInput] | Mapping[object, RationalInput],
    *,
    max_vertices: int = 11,
    max_partitions: int = 2_000_000,
) -> PriorWeightedMonotonicityCertificate:
    if not graph_is_spanning_subgraph(reduced, original):
        raise ValueError("reduced graph is not a spanning edge-deletion subgraph")
    original_certificate = exact_prior_weighted_prefix_code(
        original,
        probabilities,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    )
    reduced_certificate = exact_prior_weighted_prefix_code(
        reduced,
        probabilities,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    )
    certificate = PriorWeightedMonotonicityCertificate(
        original_certificate,
        reduced_certificate,
    )
    if not certificate.valid:
        raise AssertionError("edge deletion increased prior-weighted coding cost")
    return certificate


def induced_subgraph(
    graph: ConfusionGraph,
    vertex_indices: Sequence[int],
) -> ConfusionGraph:
    indices = tuple(int(index) for index in vertex_indices)
    if not indices or len(set(indices)) != len(indices):
        raise ValueError("induced subgraph requires unique nonempty vertex indices")
    if any(not 0 <= index < graph.vertex_count for index in indices):
        raise ValueError("induced-subgraph vertex index out of range")
    old_to_new = {old: new for new, old in enumerate(indices)}
    masks: list[int] = []
    for old in indices:
        new_mask = 0
        for old_neighbor in indices:
            if (graph.adjacency_masks[old] >> old_neighbor) & 1:
                new_mask |= 1 << old_to_new[old_neighbor]
        masks.append(new_mask)
    return ConfusionGraph(
        tuple(graph.vertices[index] for index in indices),
        tuple(masks),
    )


@dataclass(frozen=True)
class PositiveSupportCodeCertificate:
    declared_state_code: PriorWeightedCodeCertificate
    support_indices: tuple[int, ...]
    support_graph: ConfusionGraph
    support_prior: tuple[Fraction, ...]
    support_only_code: PriorWeightedCodeCertificate

    @property
    def valid(self) -> bool:
        return (
            self.support_indices
            == tuple(
                index
                for index, probability in enumerate(
                    self.declared_state_code.prior
                )
                if probability > 0
            )
            and self.support_graph
            == induced_subgraph(
                self.declared_state_code.graph,
                self.support_indices,
            )
            and self.support_prior
            == tuple(
                self.declared_state_code.prior[index]
                for index in self.support_indices
            )
            and sum(self.support_prior, Fraction(0)) == 1
            and self.support_only_code.valid
            and self.support_only_code.expected_length
            <= self.declared_state_code.expected_length
        )


def positive_support_code_certificate(
    graph: ConfusionGraph,
    probabilities: Sequence[RationalInput] | Mapping[object, RationalInput],
    *,
    max_vertices: int = 11,
    max_partitions: int = 2_000_000,
) -> PositiveSupportCodeCertificate:
    declared = exact_prior_weighted_prefix_code(
        graph,
        probabilities,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    )
    support_indices = tuple(
        index
        for index, probability in enumerate(declared.prior)
        if probability > 0
    )
    support_graph = induced_subgraph(graph, support_indices)
    support_prior = tuple(declared.prior[index] for index in support_indices)
    support_code = exact_prior_weighted_prefix_code(
        support_graph,
        support_prior,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
    )
    certificate = PositiveSupportCodeCertificate(
        declared,
        support_indices,
        support_graph,
        support_prior,
        support_code,
    )
    if not certificate.valid:
        raise AssertionError("positive-support coding certificate failed")
    return certificate


def richer_than_chromatic_example() -> tuple[ConfusionGraph, tuple[Fraction, ...]]:
    """Five-vertex example where expected-optimal coding uses four colors.

    Vertex 0 is universal and vertices 1-2-3-4 form a path.  The graph is
    3-chromatic.  Under the returned prior, every 3-color code costs at least
    38/25 expected bits, while the 4-color partition

        {0}, {1,4}, {2}, {3}

    has class masses 6/25, 16/25, 1/50, 1/10 and Huffman cost 37/25.
    """

    graph = ConfusionGraph.from_edges(
        tuple(range(5)),
        (
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
            (3, 4),
        ),
    )
    prior = (
        Fraction(12, 50),
        Fraction(19, 50),
        Fraction(1, 50),
        Fraction(5, 50),
        Fraction(13, 50),
    )
    return graph, prior
