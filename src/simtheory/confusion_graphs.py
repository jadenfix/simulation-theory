"""One-shot nonlinear predictive function computation via confusion graphs.

A finite hidden state x is encoded into one common deterministic message before
several sinks decode. Sink t already knows side information s_t(x) and only
needs the finite target value f_t(x).

Two states x and y are confusable when some sink has the same side information
under both states but requires different target outputs:

    s_t(x) = s_t(y) and f_t(x) != f_t(y).

The confusion graph joins exactly those pairs. A zero-error common-message
encoder is valid iff its message labels form a proper coloring of this graph.
Consequently the exact minimum one-shot message alphabet is the chromatic
number chi(G), and the minimum fixed-length classical message is
ceil(log2 chi(G)) bits.

The module includes exact bounded graph construction, decoder synthesis,
maximum clique and independent-set bounds, deterministic DSATUR coloring,
exact bounded chromatic search, arbitrary-graph realization, side-information
and target-coarsening monotonicity, zero-error randomized-support
determinization, and a bridge from colors to an already certified finite-field
multicast code.

These are finite one-shot zero-error internal communication results. They are
not evidence for simulation. Color labels, graph vertices, messages, side
information, field symbols, and bit counts are not parent-universe hardware,
energy, mass, or spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import ceil, log2
from typing import Callable, Hashable, Mapping, Sequence

from .network_coding import FieldVector, LinearMulticastCertificate

State = Hashable
Value = Hashable
Message = Hashable


def _ceil_log2_integer(value: int) -> int:
    integer = int(value)
    if integer != value or integer < 1:
        raise ValueError("value must be a positive integer")
    return 0 if integer == 1 else (integer - 1).bit_length()


def _validate_hashable_sequence(
    values: Sequence[Hashable],
    *,
    name: str,
    unique: bool,
    nonempty: bool,
) -> tuple[Hashable, ...]:
    supplied = tuple(values)
    if nonempty and not supplied:
        raise ValueError(f"{name} cannot be empty")
    try:
        distinct = len(set(supplied))
    except TypeError as error:
        raise ValueError(f"{name} must be hashable") from error
    if unique and distinct != len(supplied):
        raise ValueError(f"{name} must be unique")
    return supplied


@dataclass(frozen=True)
class FiniteFunctionDemand:
    """One sink's target and side-information values aligned with source states."""

    sink: str
    target_values: tuple[Value, ...]
    side_information_values: tuple[Value, ...]

    def __post_init__(self) -> None:
        sink = str(self.sink)
        if not sink:
            raise ValueError("sink cannot be empty")
        targets = _validate_hashable_sequence(
            self.target_values,
            name="target values",
            unique=False,
            nonempty=True,
        )
        side = _validate_hashable_sequence(
            self.side_information_values,
            name="side-information values",
            unique=False,
            nonempty=True,
        )
        if len(targets) != len(side):
            raise ValueError("target and side-information tables must align")
        object.__setattr__(self, "sink", sink)
        object.__setattr__(self, "target_values", targets)
        object.__setattr__(self, "side_information_values", side)


@dataclass(frozen=True)
class FiniteFunctionProblem:
    """Finite one-shot common-message function-computation problem."""

    states: tuple[State, ...]
    demands: tuple[FiniteFunctionDemand, ...]

    def __post_init__(self) -> None:
        states = _validate_hashable_sequence(
            self.states,
            name="states",
            unique=True,
            nonempty=True,
        )
        demands = tuple(self.demands)
        if not demands or len({demand.sink for demand in demands}) != len(demands):
            raise ValueError("unique nonempty sink demands are required")
        if any(len(demand.target_values) != len(states) for demand in demands):
            raise ValueError("every demand table must align with all source states")
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "demands", demands)

    @classmethod
    def from_functions(
        cls,
        states: Sequence[State],
        demands: Sequence[
            tuple[
                str,
                Callable[[State], Value],
                Callable[[State], Value],
            ]
        ],
    ) -> "FiniteFunctionProblem":
        supplied_states = tuple(states)
        return cls(
            supplied_states,
            tuple(
                FiniteFunctionDemand(
                    sink,
                    tuple(target(state) for state in supplied_states),
                    tuple(side_information(state) for state in supplied_states),
                )
                for sink, target, side_information in demands
            ),
        )

    @classmethod
    def from_mappings(
        cls,
        states: Sequence[State],
        demands: Sequence[
            tuple[
                str,
                Mapping[State, Value],
                Mapping[State, Value],
            ]
        ],
    ) -> "FiniteFunctionProblem":
        supplied_states = tuple(states)
        expected = set(supplied_states)
        canonical: list[FiniteFunctionDemand] = []
        for sink, target_mapping, side_mapping in demands:
            if set(target_mapping) != expected or set(side_mapping) != expected:
                raise ValueError("demand mappings must define exactly every state")
            canonical.append(
                FiniteFunctionDemand(
                    sink,
                    tuple(target_mapping[state] for state in supplied_states),
                    tuple(side_mapping[state] for state in supplied_states),
                )
            )
        return cls(supplied_states, tuple(canonical))

    @property
    def sink_names(self) -> tuple[str, ...]:
        return tuple(demand.sink for demand in self.demands)

    @property
    def state_count(self) -> int:
        return len(self.states)

    def state_index(self, state: State) -> int:
        try:
            return self.states.index(state)
        except ValueError as error:
            raise ValueError("state is not in this finite problem") from error

    def demand(self, sink: str) -> FiniteFunctionDemand:
        target = str(sink)
        for demand in self.demands:
            if demand.sink == target:
                return demand
        raise ValueError("sink has no declared demand")

    def target(self, sink: str, state: State) -> Value:
        return self.demand(sink).target_values[self.state_index(state)]

    def side_information(self, sink: str, state: State) -> Value:
        return self.demand(sink).side_information_values[self.state_index(state)]


@dataclass(frozen=True)
class ConfusionWitness:
    left: State
    right: State
    sink: str
    common_side_information: Value
    left_target: Value
    right_target: Value


@dataclass(frozen=True)
class ConfusionGraph:
    """Finite simple graph represented by symmetric integer adjacency masks."""

    vertices: tuple[State, ...]
    adjacency_masks: tuple[int, ...]

    def __post_init__(self) -> None:
        vertices = _validate_hashable_sequence(
            self.vertices,
            name="vertices",
            unique=True,
            nonempty=True,
        )
        masks = tuple(int(mask) for mask in self.adjacency_masks)
        if len(masks) != len(vertices):
            raise ValueError("one adjacency mask is required per vertex")
        full = (1 << len(vertices)) - 1
        for index, mask in enumerate(masks):
            if mask < 0 or mask & ~full:
                raise ValueError("adjacency mask contains an unknown vertex")
            if (mask >> index) & 1:
                raise ValueError("confusion graph cannot contain self loops")
        for left in range(len(vertices)):
            for right in range(left + 1, len(vertices)):
                if ((masks[left] >> right) & 1) != ((masks[right] >> left) & 1):
                    raise ValueError("adjacency masks must be symmetric")
        object.__setattr__(self, "vertices", vertices)
        object.__setattr__(self, "adjacency_masks", masks)

    @classmethod
    def from_edges(
        cls,
        vertices: Sequence[State],
        edges: Sequence[tuple[State, State]],
    ) -> "ConfusionGraph":
        supplied_vertices = tuple(vertices)
        index = {vertex: position for position, vertex in enumerate(supplied_vertices)}
        if len(index) != len(supplied_vertices):
            raise ValueError("vertices must be unique and hashable")
        masks = [0] * len(supplied_vertices)
        for left_vertex, right_vertex in edges:
            if left_vertex not in index or right_vertex not in index:
                raise ValueError("edge endpoint is not a declared vertex")
            left = index[left_vertex]
            right = index[right_vertex]
            if left == right:
                raise ValueError("self loops are not allowed")
            masks[left] |= 1 << right
            masks[right] |= 1 << left
        return cls(supplied_vertices, tuple(masks))

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def edge_count(self) -> int:
        return sum(mask.bit_count() for mask in self.adjacency_masks) // 2

    def vertex_index(self, vertex: State) -> int:
        try:
            return self.vertices.index(vertex)
        except ValueError as error:
            raise ValueError("vertex is not in this graph") from error

    def adjacent(self, left: State, right: State) -> bool:
        left_index = self.vertex_index(left)
        right_index = self.vertex_index(right)
        return bool((self.adjacency_masks[left_index] >> right_index) & 1)

    def neighbors(self, vertex: State) -> tuple[State, ...]:
        index = self.vertex_index(vertex)
        mask = self.adjacency_masks[index]
        return tuple(
            self.vertices[neighbor]
            for neighbor in range(self.vertex_count)
            if (mask >> neighbor) & 1
        )

    def degree(self, vertex: State) -> int:
        return self.adjacency_masks[self.vertex_index(vertex)].bit_count()

    def edges(self) -> tuple[tuple[State, State], ...]:
        return tuple(
            (self.vertices[left], self.vertices[right])
            for left in range(self.vertex_count)
            for right in range(left + 1, self.vertex_count)
            if (self.adjacency_masks[left] >> right) & 1
        )

    def complement(self) -> "ConfusionGraph":
        full = (1 << self.vertex_count) - 1
        masks = tuple(
            full & ~(mask | (1 << index))
            for index, mask in enumerate(self.adjacency_masks)
        )
        return ConfusionGraph(self.vertices, masks)


@dataclass(frozen=True)
class ConfusionGraphCertificate:
    problem: FiniteFunctionProblem
    graph: ConfusionGraph
    witnesses: tuple[tuple[tuple[int, int], ConfusionWitness], ...]

    def witness(self, left: State, right: State) -> ConfusionWitness | None:
        left_index = self.problem.state_index(left)
        right_index = self.problem.state_index(right)
        key = tuple(sorted((left_index, right_index)))
        return dict(self.witnesses).get(key)

    @property
    def valid(self) -> bool:
        witness_map = dict(self.witnesses)
        for left in range(self.problem.state_count):
            for right in range(left + 1, self.problem.state_count):
                expected = first_confusion_witness_by_index(
                    self.problem,
                    left,
                    right,
                )
                edge = bool((self.graph.adjacency_masks[left] >> right) & 1)
                if edge != (expected is not None):
                    return False
                if edge and witness_map.get((left, right)) != expected:
                    return False
        return True


def first_confusion_witness_by_index(
    problem: FiniteFunctionProblem,
    left_index: int,
    right_index: int,
) -> ConfusionWitness | None:
    if not 0 <= left_index < problem.state_count or not 0 <= right_index < problem.state_count:
        raise ValueError("state index out of range")
    if left_index == right_index:
        return None
    left = problem.states[left_index]
    right = problem.states[right_index]
    for demand in problem.demands:
        left_side = demand.side_information_values[left_index]
        right_side = demand.side_information_values[right_index]
        left_target = demand.target_values[left_index]
        right_target = demand.target_values[right_index]
        if left_side == right_side and left_target != right_target:
            return ConfusionWitness(
                left,
                right,
                demand.sink,
                left_side,
                left_target,
                right_target,
            )
    return None


def confusion_graph_certificate(
    problem: FiniteFunctionProblem,
) -> ConfusionGraphCertificate:
    masks = [0] * problem.state_count
    witnesses: list[tuple[tuple[int, int], ConfusionWitness]] = []
    for left in range(problem.state_count):
        for right in range(left + 1, problem.state_count):
            witness = first_confusion_witness_by_index(problem, left, right)
            if witness is None:
                continue
            masks[left] |= 1 << right
            masks[right] |= 1 << left
            witnesses.append(((left, right), witness))
    certificate = ConfusionGraphCertificate(
        problem,
        ConfusionGraph(problem.states, tuple(masks)),
        tuple(witnesses),
    )
    if not certificate.valid:
        raise AssertionError("constructed confusion graph failed its witness audit")
    return certificate


def confusion_graph(problem: FiniteFunctionProblem) -> ConfusionGraph:
    return confusion_graph_certificate(problem).graph


def canonicalize_coloring(colors: Sequence[int]) -> tuple[int, ...]:
    supplied = tuple(int(color) for color in colors)
    if not supplied:
        raise ValueError("coloring cannot be empty")
    if any(color < 0 for color in supplied):
        raise ValueError("colors must be nonnegative integers")
    renaming: dict[int, int] = {}
    result: list[int] = []
    for color in supplied:
        renamed = renaming.setdefault(color, len(renaming))
        result.append(renamed)
    return tuple(result)


def coloring_color_count(colors: Sequence[int]) -> int:
    return len(set(canonicalize_coloring(colors)))


def coloring_is_proper(graph: ConfusionGraph, colors: Sequence[int]) -> bool:
    canonical = canonicalize_coloring(colors)
    if len(canonical) != graph.vertex_count:
        raise ValueError("one color is required per graph vertex")
    return all(
        canonical[left] != canonical[right]
        for left in range(graph.vertex_count)
        for right in range(left + 1, graph.vertex_count)
        if (graph.adjacency_masks[left] >> right) & 1
    )


@dataclass(frozen=True)
class DecoderEntry:
    sink: str
    message: int
    side_information: Value
    target: Value


@dataclass(frozen=True)
class DeterministicFunctionCode:
    problem: FiniteFunctionProblem
    coloring: tuple[int, ...]
    decoder_entries: tuple[DecoderEntry, ...]

    def __post_init__(self) -> None:
        canonical = canonicalize_coloring(self.coloring)
        if len(canonical) != self.problem.state_count:
            raise ValueError("one encoder color is required per source state")
        object.__setattr__(self, "coloring", canonical)
        if not coloring_is_proper(confusion_graph(self.problem), canonical):
            raise ValueError("encoder labels are not a proper confusion-graph coloring")

    @property
    def message_states(self) -> int:
        return coloring_color_count(self.coloring)

    @property
    def fixed_length_bits(self) -> int:
        return _ceil_log2_integer(self.message_states)

    def encode(self, state: State) -> int:
        return self.coloring[self.problem.state_index(state)]

    def decode(self, sink: str, message: int, side_information: Value) -> Value:
        candidates = [
            entry.target
            for entry in self.decoder_entries
            if entry.sink == sink
            and entry.message == int(message)
            and entry.side_information == side_information
        ]
        if len(candidates) != 1:
            raise ValueError("decoder input is absent or ambiguous")
        return candidates[0]

    def answer(self, sink: str, state: State) -> Value:
        return self.decode(
            sink,
            self.encode(state),
            self.problem.side_information(sink, state),
        )

    @property
    def valid(self) -> bool:
        return all(
            self.answer(demand.sink, state)
            == self.problem.target(demand.sink, state)
            for demand in self.problem.demands
            for state in self.problem.states
        )


def deterministic_code_from_coloring(
    problem: FiniteFunctionProblem,
    colors: Sequence[int],
) -> DeterministicFunctionCode:
    canonical = canonicalize_coloring(colors)
    graph = confusion_graph(problem)
    if len(canonical) != problem.state_count:
        raise ValueError("one color is required per source state")
    if not coloring_is_proper(graph, canonical):
        raise ValueError("coloring is not proper")
    table: dict[tuple[str, int, Value], Value] = {}
    for state_index, state in enumerate(problem.states):
        message = canonical[state_index]
        for demand in problem.demands:
            key = (
                demand.sink,
                message,
                demand.side_information_values[state_index],
            )
            target = demand.target_values[state_index]
            existing = table.get(key, target)
            if existing != target:
                raise AssertionError("proper coloring unexpectedly produced decoder ambiguity")
            table[key] = target
    entries = tuple(
        DecoderEntry(sink, message, side, target)
        for (sink, message, side), target in table.items()
    )
    code = DeterministicFunctionCode(problem, canonical, entries)
    if not code.valid:
        raise AssertionError("synthesized deterministic decoder failed")
    return code


def encoder_is_zero_error(
    problem: FiniteFunctionProblem,
    messages: Sequence[Hashable],
) -> bool:
    supplied = _validate_hashable_sequence(
        messages,
        name="messages",
        unique=False,
        nonempty=True,
    )
    if len(supplied) != problem.state_count:
        raise ValueError("one message is required per source state")
    graph = confusion_graph(problem)
    return all(
        supplied[left] != supplied[right]
        for left in range(problem.state_count)
        for right in range(left + 1, problem.state_count)
        if (graph.adjacency_masks[left] >> right) & 1
    )


@dataclass(frozen=True)
class ColoringEquivalenceCertificate:
    graph_proper: bool
    encoder_zero_error: bool
    decoder_constructed: bool

    @property
    def valid(self) -> bool:
        return self.graph_proper == self.encoder_zero_error and (
            not self.graph_proper or self.decoder_constructed
        )


def coloring_equivalence_certificate(
    problem: FiniteFunctionProblem,
    colors: Sequence[int],
) -> ColoringEquivalenceCertificate:
    canonical = canonicalize_coloring(colors)
    if len(canonical) != problem.state_count:
        raise ValueError("one color is required per state")
    proper = coloring_is_proper(confusion_graph(problem), canonical)
    zero_error = encoder_is_zero_error(problem, canonical)
    decoder_constructed = False
    if proper:
        decoder_constructed = deterministic_code_from_coloring(
            problem,
            canonical,
        ).valid
    certificate = ColoringEquivalenceCertificate(
        proper,
        zero_error,
        decoder_constructed,
    )
    if not certificate.valid:
        raise AssertionError("coloring and zero-error encoder conditions disagree")
    return certificate


def greedy_dsatur_coloring(graph: ConfusionGraph) -> tuple[int, ...]:
    """Deterministic DSATUR coloring used as a constructive upper bound."""

    count = graph.vertex_count
    colors = [-1] * count
    uncolored = set(range(count))
    while uncolored:
        def priority(vertex: int) -> tuple[int, int, int]:
            neighbor_colors = {
                colors[neighbor]
                for neighbor in range(count)
                if (graph.adjacency_masks[vertex] >> neighbor) & 1
                and colors[neighbor] >= 0
            }
            return (
                len(neighbor_colors),
                graph.adjacency_masks[vertex].bit_count(),
                -vertex,
            )

        vertex = max(uncolored, key=priority)
        forbidden = {
            colors[neighbor]
            for neighbor in range(count)
            if (graph.adjacency_masks[vertex] >> neighbor) & 1
            and colors[neighbor] >= 0
        }
        color = 0
        while color in forbidden:
            color += 1
        colors[vertex] = color
        uncolored.remove(vertex)
    canonical = canonicalize_coloring(colors)
    if not coloring_is_proper(graph, canonical):
        raise AssertionError("DSATUR produced an improper coloring")
    return canonical


def _maximum_clique_indices(
    graph: ConfusionGraph,
    *,
    max_vertices: int,
) -> tuple[int, ...]:
    if graph.vertex_count > max_vertices:
        raise ValueError(f"exact clique search capped at {max_vertices} vertices")
    best_mask = 0

    def expand(clique_mask: int, candidates: int) -> None:
        nonlocal best_mask
        if clique_mask.bit_count() + candidates.bit_count() <= best_mask.bit_count():
            return
        if not candidates:
            if clique_mask.bit_count() > best_mask.bit_count():
                best_mask = clique_mask
            return
        remaining = candidates
        while remaining:
            if clique_mask.bit_count() + remaining.bit_count() <= best_mask.bit_count():
                return
            candidate_indices = [
                index
                for index in range(graph.vertex_count)
                if (remaining >> index) & 1
            ]
            vertex = max(
                candidate_indices,
                key=lambda index: (
                    (graph.adjacency_masks[index] & remaining).bit_count(),
                    -index,
                ),
            )
            bit = 1 << vertex
            remaining &= ~bit
            expand(
                clique_mask | bit,
                remaining & graph.adjacency_masks[vertex],
            )
        if clique_mask.bit_count() > best_mask.bit_count():
            best_mask = clique_mask

    expand(0, (1 << graph.vertex_count) - 1)
    return tuple(
        index
        for index in range(graph.vertex_count)
        if (best_mask >> index) & 1
    )


def maximum_clique(
    graph: ConfusionGraph,
    *,
    max_vertices: int = 60,
) -> tuple[State, ...]:
    return tuple(
        graph.vertices[index]
        for index in _maximum_clique_indices(graph, max_vertices=max_vertices)
    )


def maximum_independent_set(
    graph: ConfusionGraph,
    *,
    max_vertices: int = 60,
) -> tuple[State, ...]:
    return maximum_clique(graph.complement(), max_vertices=max_vertices)


def _k_coloring(
    graph: ConfusionGraph,
    color_limit: int,
) -> tuple[int, ...] | None:
    if color_limit < 1:
        return None
    count = graph.vertex_count
    colors = [-1] * count

    def choose_vertex() -> int:
        uncolored = [index for index, color in enumerate(colors) if color < 0]
        return max(
            uncolored,
            key=lambda vertex: (
                len({
                    colors[neighbor]
                    for neighbor in range(count)
                    if (graph.adjacency_masks[vertex] >> neighbor) & 1
                    and colors[neighbor] >= 0
                }),
                sum(
                    1
                    for neighbor in range(count)
                    if (graph.adjacency_masks[vertex] >> neighbor) & 1
                    and colors[neighbor] < 0
                ),
                graph.adjacency_masks[vertex].bit_count(),
                -vertex,
            ),
        )

    def search(colored_count: int, used_colors: int) -> bool:
        if colored_count == count:
            return True
        vertex = choose_vertex()
        forbidden = {
            colors[neighbor]
            for neighbor in range(count)
            if (graph.adjacency_masks[vertex] >> neighbor) & 1
            and colors[neighbor] >= 0
        }
        maximum_candidate = min(used_colors, color_limit - 1)
        for color in range(maximum_candidate + 1):
            if color in forbidden:
                continue
            is_new = color == used_colors
            if is_new and used_colors >= color_limit:
                continue
            colors[vertex] = color
            if search(colored_count + 1, used_colors + int(is_new)):
                return True
            colors[vertex] = -1
        return False

    # Fix one color label to remove global color-permutation symmetry.
    first = max(
        range(count),
        key=lambda index: (graph.adjacency_masks[index].bit_count(), -index),
    )
    colors[first] = 0
    if search(1, 1):
        result = canonicalize_coloring(colors)
        if not coloring_is_proper(graph, result):
            raise AssertionError("exact k-color search returned an improper coloring")
        return result
    return None


@dataclass(frozen=True)
class ChromaticCertificate:
    graph: ConfusionGraph
    coloring: tuple[int, ...]
    chromatic_number: int
    maximum_clique_vertices: tuple[State, ...]
    maximum_independent_vertices: tuple[State, ...]
    clique_lower_bound: int
    independence_lower_bound: int
    greedy_upper_bound: int
    searched_color_limits: tuple[int, ...]

    @property
    def lower_bound(self) -> int:
        return max(self.clique_lower_bound, self.independence_lower_bound)

    @property
    def fixed_length_bits(self) -> int:
        return _ceil_log2_integer(self.chromatic_number)

    @property
    def valid(self) -> bool:
        return (
            coloring_is_proper(self.graph, self.coloring)
            and coloring_color_count(self.coloring) == self.chromatic_number
            and self.lower_bound <= self.chromatic_number <= self.greedy_upper_bound
            and len(self.maximum_clique_vertices) == self.clique_lower_bound
            and len(self.maximum_independent_vertices) > 0
        )


def exact_chromatic_certificate(
    graph: ConfusionGraph,
    *,
    max_vertices: int = 36,
) -> ChromaticCertificate:
    if graph.vertex_count > max_vertices:
        raise ValueError(f"exact chromatic search capped at {max_vertices} vertices")
    greedy = greedy_dsatur_coloring(graph)
    greedy_upper = coloring_color_count(greedy)
    clique = maximum_clique(graph, max_vertices=max_vertices)
    independent = maximum_independent_set(graph, max_vertices=max_vertices)
    clique_lower = len(clique)
    independence_lower = ceil(graph.vertex_count / len(independent))
    lower = max(clique_lower, independence_lower)
    coloring = greedy
    chromatic = greedy_upper
    searched: list[int] = []
    for color_limit in range(lower, greedy_upper):
        searched.append(color_limit)
        candidate = _k_coloring(graph, color_limit)
        if candidate is not None:
            coloring = candidate
            chromatic = color_limit
            break
    certificate = ChromaticCertificate(
        graph,
        coloring,
        chromatic,
        clique,
        independent,
        clique_lower,
        independence_lower,
        greedy_upper,
        tuple(searched),
    )
    if not certificate.valid:
        raise AssertionError("chromatic certificate failed internal validation")
    return certificate


@dataclass(frozen=True)
class OptimalFunctionCodeCertificate:
    graph_certificate: ConfusionGraphCertificate
    chromatic_certificate: ChromaticCertificate
    code: DeterministicFunctionCode

    @property
    def message_states(self) -> int:
        return self.chromatic_certificate.chromatic_number

    @property
    def fixed_length_bits(self) -> int:
        return self.chromatic_certificate.fixed_length_bits

    @property
    def valid(self) -> bool:
        return (
            self.graph_certificate.valid
            and self.chromatic_certificate.valid
            and self.code.valid
            and self.code.message_states == self.message_states
        )


def optimal_function_code(
    problem: FiniteFunctionProblem,
    *,
    max_vertices: int = 36,
) -> OptimalFunctionCodeCertificate:
    graph_certificate = confusion_graph_certificate(problem)
    chromatic = exact_chromatic_certificate(
        graph_certificate.graph,
        max_vertices=max_vertices,
    )
    code = deterministic_code_from_coloring(problem, chromatic.coloring)
    certificate = OptimalFunctionCodeCertificate(
        graph_certificate,
        chromatic,
        code,
    )
    if not certificate.valid:
        raise AssertionError("optimal finite function code failed validation")
    return certificate


@dataclass(frozen=True)
class RandomizedSupportEncoder:
    """One-shot randomized encoder represented by nonempty message supports."""

    graph: ConfusionGraph
    message_alphabet: tuple[Message, ...]
    state_supports: tuple[frozenset[int], ...]

    def __post_init__(self) -> None:
        alphabet = _validate_hashable_sequence(
            self.message_alphabet,
            name="message alphabet",
            unique=True,
            nonempty=True,
        )
        supports = tuple(frozenset(int(index) for index in support) for support in self.state_supports)
        if len(supports) != self.graph.vertex_count:
            raise ValueError("one randomized support is required per state")
        if any(not support for support in supports):
            raise ValueError("randomized supports must be nonempty")
        if any(
            index < 0 or index >= len(alphabet)
            for support in supports
            for index in support
        ):
            raise ValueError("randomized support references an unknown message")
        object.__setattr__(self, "message_alphabet", alphabet)
        object.__setattr__(self, "state_supports", supports)

    @property
    def zero_error(self) -> bool:
        return all(
            self.state_supports[left].isdisjoint(self.state_supports[right])
            for left in range(self.graph.vertex_count)
            for right in range(left + 1, self.graph.vertex_count)
            if (self.graph.adjacency_masks[left] >> right) & 1
        )

    def determinize(self) -> tuple[int, ...]:
        """Select one support message per state; zero error guarantees a coloring."""

        coloring = tuple(min(support) for support in self.state_supports)
        if self.zero_error and not coloring_is_proper(self.graph, coloring):
            raise AssertionError("zero-error randomized supports failed to determinize")
        return canonicalize_coloring(coloring)


@dataclass(frozen=True)
class RandomizationNoBenefitCertificate:
    randomized: RandomizedSupportEncoder
    deterministic_coloring: tuple[int, ...]

    @property
    def valid(self) -> bool:
        return (
            self.randomized.zero_error
            and coloring_is_proper(
                self.randomized.graph,
                self.deterministic_coloring,
            )
            and coloring_color_count(self.deterministic_coloring)
            <= len(self.randomized.message_alphabet)
        )


def randomization_no_benefit_certificate(
    randomized: RandomizedSupportEncoder,
) -> RandomizationNoBenefitCertificate:
    if not randomized.zero_error:
        raise ValueError("randomized supports are not zero error")
    certificate = RandomizationNoBenefitCertificate(
        randomized,
        randomized.determinize(),
    )
    if not certificate.valid:
        raise AssertionError("randomized encoder did not yield a deterministic coloring")
    return certificate


def problem_from_graph(graph: ConfusionGraph) -> FiniteFunctionProblem:
    """Realize any finite simple graph as a finite side-information problem.

    One sink is created per edge. Its two edge endpoints share one side value
    and require opposite targets. Every other vertex receives a unique side
    value for that sink, so no unintended edge is introduced.
    """

    demands: list[FiniteFunctionDemand] = []
    for edge_index, (left_vertex, right_vertex) in enumerate(graph.edges()):
        targets: list[Value] = []
        sides: list[Value] = []
        for vertex in graph.vertices:
            if vertex == left_vertex:
                targets.append(0)
                sides.append(("edge", edge_index))
            elif vertex == right_vertex:
                targets.append(1)
                sides.append(("edge", edge_index))
            else:
                targets.append(0)
                sides.append(("other", edge_index, graph.vertex_index(vertex)))
        demands.append(
            FiniteFunctionDemand(
                f"edge-{edge_index}",
                tuple(targets),
                tuple(sides),
            )
        )
    if not demands:
        # An edgeless graph is realized by one constant target with unique side
        # information, preventing every pair from becoming confusable.
        demands.append(
            FiniteFunctionDemand(
                "edgeless",
                tuple(0 for _ in graph.vertices),
                tuple(("state", index) for index in range(graph.vertex_count)),
            )
        )
    problem = FiniteFunctionProblem(graph.vertices, tuple(demands))
    realized = confusion_graph(problem)
    if realized.adjacency_masks != graph.adjacency_masks:
        raise AssertionError("finite function construction failed to realize the graph")
    return problem


def binary_pair_problem(
    *,
    complementary_side_information: bool,
) -> FiniteFunctionProblem:
    """Two sinks respectively demand x1 and x2 from a two-bit source."""

    states = tuple(product((0, 1), repeat=2))
    if complementary_side_information:
        return FiniteFunctionProblem.from_functions(
            states,
            (
                ("t1", lambda state: state[0], lambda state: state[1]),
                ("t2", lambda state: state[1], lambda state: state[0]),
            ),
        )
    return FiniteFunctionProblem.from_functions(
        states,
        (
            ("t1", lambda state: state[0], lambda _state: None),
            ("t2", lambda state: state[1], lambda _state: None),
        ),
    )


def parity_coloring_for_binary_pair(problem: FiniteFunctionProblem) -> tuple[int, ...]:
    if set(problem.states) != set(product((0, 1), repeat=2)):
        raise ValueError("parity coloring requires every two-bit source state")
    return tuple((int(state[0]) ^ int(state[1])) for state in problem.states)  # type: ignore[index]


def side_information_refines(
    refined: FiniteFunctionProblem,
    coarse: FiniteFunctionProblem,
) -> bool:
    """Whether refined side information distinguishes at least what coarse does.

    Targets, states, and sinks must agree. For every sink, equality of refined
    side values must imply equality of coarse side values.
    """

    if refined.states != coarse.states or refined.sink_names != coarse.sink_names:
        return False
    for refined_demand, coarse_demand in zip(refined.demands, coarse.demands):
        if refined_demand.target_values != coarse_demand.target_values:
            return False
        for left in range(refined.state_count):
            for right in range(left + 1, refined.state_count):
                if (
                    refined_demand.side_information_values[left]
                    == refined_demand.side_information_values[right]
                    and coarse_demand.side_information_values[left]
                    != coarse_demand.side_information_values[right]
                ):
                    return False
    return True


def targets_are_coarsened(
    coarsened: FiniteFunctionProblem,
    original: FiniteFunctionProblem,
) -> bool:
    """Whether each new target is a function of the corresponding old target."""

    if coarsened.states != original.states or coarsened.sink_names != original.sink_names:
        return False
    for new_demand, old_demand in zip(coarsened.demands, original.demands):
        if new_demand.side_information_values != old_demand.side_information_values:
            return False
        for left in range(coarsened.state_count):
            for right in range(left + 1, coarsened.state_count):
                if (
                    old_demand.target_values[left]
                    == old_demand.target_values[right]
                    and new_demand.target_values[left]
                    != new_demand.target_values[right]
                ):
                    return False
    return True


@dataclass(frozen=True)
class ConfusionMonotonicityCertificate:
    original_graph: ConfusionGraph
    transformed_graph: ConfusionGraph
    transformation: str
    original_chromatic_number: int
    transformed_chromatic_number: int

    @property
    def edges_contract(self) -> bool:
        return all(
            transformed & ~original == 0
            for original, transformed in zip(
                self.original_graph.adjacency_masks,
                self.transformed_graph.adjacency_masks,
            )
        )

    @property
    def valid(self) -> bool:
        return (
            self.edges_contract
            and self.transformed_chromatic_number
            <= self.original_chromatic_number
        )


def side_information_refinement_certificate(
    refined: FiniteFunctionProblem,
    coarse: FiniteFunctionProblem,
    *,
    max_vertices: int = 36,
) -> ConfusionMonotonicityCertificate:
    if not side_information_refines(refined, coarse):
        raise ValueError("refined problem is not a side-information refinement")
    original_graph = confusion_graph(coarse)
    transformed_graph = confusion_graph(refined)
    certificate = ConfusionMonotonicityCertificate(
        original_graph,
        transformed_graph,
        "side-information refinement",
        exact_chromatic_certificate(original_graph, max_vertices=max_vertices).chromatic_number,
        exact_chromatic_certificate(transformed_graph, max_vertices=max_vertices).chromatic_number,
    )
    if not certificate.valid:
        raise AssertionError("side-information refinement increased confusion")
    return certificate


def target_coarsening_certificate(
    coarsened: FiniteFunctionProblem,
    original: FiniteFunctionProblem,
    *,
    max_vertices: int = 36,
) -> ConfusionMonotonicityCertificate:
    if not targets_are_coarsened(coarsened, original):
        raise ValueError("new targets are not a coarsening of the original targets")
    original_graph = confusion_graph(original)
    transformed_graph = confusion_graph(coarsened)
    certificate = ConfusionMonotonicityCertificate(
        original_graph,
        transformed_graph,
        "target coarsening",
        exact_chromatic_certificate(original_graph, max_vertices=max_vertices).chromatic_number,
        exact_chromatic_certificate(transformed_graph, max_vertices=max_vertices).chromatic_number,
    )
    if not certificate.valid:
        raise AssertionError("target coarsening increased confusion")
    return certificate


def _integer_to_base_p_vector(value: int, length: int, prime: int) -> FieldVector:
    if value < 0 or length < 1 or prime < 2:
        raise ValueError("invalid finite-field label dimensions")
    digits: list[int] = []
    remaining = value
    for _ in range(length):
        digits.append(remaining % prime)
        remaining //= prime
    if remaining:
        raise ValueError("value does not fit in the finite-field vector")
    return tuple(digits)


@dataclass(frozen=True)
class ConfusionGraphMulticastCertificate:
    optimal_code: OptimalFunctionCodeCertificate
    multicast: LinearMulticastCertificate
    color_vectors: tuple[tuple[int, FieldVector], ...]

    @property
    def valid(self) -> bool:
        code = self.multicast.code
        if not self.optimal_code.valid or not self.multicast.valid:
            return False
        if set(code.sinks) != set(self.optimal_code.code.problem.sink_names):
            return False
        mapping = dict(self.color_vectors)
        if set(mapping) != set(range(self.optimal_code.message_states)):
            return False
        if len(set(mapping.values())) != self.optimal_code.message_states:
            return False
        return all(
            len(vector) == code.source_dimension
            and all(0 <= coordinate < code.field_prime for coordinate in vector)
            for vector in mapping.values()
        )

    def source_vector(self, state: State) -> FieldVector:
        return dict(self.color_vectors)[self.optimal_code.code.encode(state)]


def confusion_graph_multicast_certificate(
    problem: FiniteFunctionProblem,
    multicast: LinearMulticastCertificate,
    *,
    max_vertices: int = 36,
) -> ConfusionGraphMulticastCertificate:
    optimal = optimal_function_code(problem, max_vertices=max_vertices)
    code = multicast.code
    capacity = code.field_prime ** code.source_dimension
    if optimal.message_states > capacity:
        raise ValueError("multicast source vector has too few values for all colors")
    if set(code.sinks) != set(problem.sink_names):
        raise ValueError("multicast sinks must match the function-demand sinks")
    certificate = ConfusionGraphMulticastCertificate(
        optimal,
        multicast,
        tuple(
            (
                color,
                _integer_to_base_p_vector(
                    color,
                    code.source_dimension,
                    code.field_prime,
                ),
            )
            for color in range(optimal.message_states)
        ),
    )
    if not certificate.valid:
        raise AssertionError("color multicast certificate failed")
    return certificate
