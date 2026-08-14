"""Progressive query revelation and multiround causal-cut bounds.

A hidden binary record X=(X_1,...,X_m) is fixed before a future coordinate
query is fully known.  The receiver first obtains a shared message/state M_0.
A query hint then reveals one cell C_j of a partition of the coordinates.  A
cell-specific message/state M_j may cross after that hint but before the exact
coordinate I in C_j is revealed.

This separates three notions that are often collapsed:

* record uncertainty: which X occurred;
* query uncertainty: which coordinates may still be requested;
* communication timing: which information may depend on the query hint.

For exact classical messages with a shared budget ``a`` and branch budgets
``c_j``, feasibility is characterized by

    a >= sum_j max(0, |C_j|-c_j),

or equivalently

    a + sum_j min(c_j, |C_j|) >= m.

The lower bound follows because, after conditioning on one shared message, each
cell can retain at most 2**c_j distinct restrictions.  The upper bound stores
the uncovered bits of every cell in the shared message and sends the rest only
after the cell hint is known.

For independent uniform record bits and coordinate errors e_i, a bounded-error
converse replaces the exact cell size by

    R_j = sum_{i in C_j} [1-H_2(e_i)].

Any classical or unassisted-quantum progressive protocol obeys

    shared_capacity >= sum_j max(0, R_j-branch_capacity_j).

With receiver-side entanglement independent of X, one transmitted qubit can
increase receiver classical mutual information by at most two bits, so every
qubit budget is multiplied by two on the capacity side.

These are internal predictive and communication results for the declared
multiround interface.  They do not prove that reality is simulated and do not
turn bits or qubits in the model into parent-universe hardware or energy.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import ceil
from typing import Sequence

from .stabilizer_relations import binary_entropy

BitRecord = tuple[int, ...]
Cell = tuple[int, ...]


def _validate_nonnegative_integer(value: int, *, name: str) -> int:
    integer = int(value)
    if integer != value or integer < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return integer


def _validate_error(error: float) -> float:
    value = float(error)
    if not 0.0 <= value <= 0.5:
        raise ValueError("error must lie in [0,1/2]")
    return value


def _validate_binary_record(
    record: Sequence[int],
    *,
    expected_length: int | None = None,
) -> BitRecord:
    bits = tuple(int(bit) for bit in record)
    if expected_length is not None and len(bits) != expected_length:
        raise ValueError("record length mismatch")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("records must be binary")
    return bits


@dataclass(frozen=True)
class QueryPartition:
    """A partition of record coordinates into nonempty query-hint cells."""

    cells: tuple[Cell, ...]

    def __post_init__(self) -> None:
        canonical = tuple(
            tuple(sorted(int(coordinate) for coordinate in cell))
            for cell in self.cells
        )
        if not canonical:
            raise ValueError("partition must contain at least one cell")
        if any(not cell for cell in canonical):
            raise ValueError("partition cells must be nonempty")
        flattened = tuple(coordinate for cell in canonical for coordinate in cell)
        if any(coordinate < 0 for coordinate in flattened):
            raise ValueError("partition coordinates must be nonnegative")
        if len(set(flattened)) != len(flattened):
            raise ValueError("partition cells must be disjoint")
        if set(flattened) != set(range(len(flattened))):
            raise ValueError("partition must cover coordinates 0 through m-1")
        object.__setattr__(self, "cells", canonical)

    @classmethod
    def equal_cells(cls, record_bits: int, cell_size: int) -> "QueryPartition":
        bits = _validate_nonnegative_integer(record_bits, name="record_bits")
        size = _validate_nonnegative_integer(cell_size, name="cell_size")
        if bits < 1:
            raise ValueError("record_bits must be positive")
        if size < 1 or bits % size:
            raise ValueError("cell_size must be a positive divisor of record_bits")
        return cls(
            tuple(
                tuple(range(start, start + size))
                for start in range(0, bits, size)
            )
        )

    @classmethod
    def single_cell(cls, record_bits: int) -> "QueryPartition":
        bits = _validate_nonnegative_integer(record_bits, name="record_bits")
        if bits < 1:
            raise ValueError("record_bits must be positive")
        return cls((tuple(range(bits)),))

    @classmethod
    def singleton_cells(cls, record_bits: int) -> "QueryPartition":
        bits = _validate_nonnegative_integer(record_bits, name="record_bits")
        if bits < 1:
            raise ValueError("record_bits must be positive")
        return cls(tuple((coordinate,) for coordinate in range(bits)))

    @property
    def record_bits(self) -> int:
        return sum(len(cell) for cell in self.cells)

    @property
    def cell_sizes(self) -> tuple[int, ...]:
        return tuple(len(cell) for cell in self.cells)

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    def cell_of_coordinate(self, coordinate: int) -> int:
        index = int(coordinate)
        if not 0 <= index < self.record_bits:
            raise ValueError("coordinate out of range")
        return next(
            cell_index
            for cell_index, cell in enumerate(self.cells)
            if index in cell
        )


def _validate_branch_budgets(
    partition: QueryPartition,
    branch_budgets: Sequence[int],
) -> tuple[int, ...]:
    budgets = tuple(
        _validate_nonnegative_integer(value, name="branch budget")
        for value in branch_budgets
    )
    if len(budgets) != partition.cell_count:
        raise ValueError("one branch budget is required per partition cell")
    return budgets


def exact_shared_bits_required(
    partition: QueryPartition,
    branch_bits: Sequence[int],
) -> int:
    """Exact common-message bits needed after accounting for branch messages."""

    budgets = _validate_branch_budgets(partition, branch_bits)
    return sum(
        max(0, cell_size - budget)
        for cell_size, budget in zip(partition.cell_sizes, budgets)
    )


def exact_classical_progressive_feasible(
    partition: QueryPartition,
    shared_bits: int,
    branch_bits: Sequence[int],
) -> bool:
    shared = _validate_nonnegative_integer(shared_bits, name="shared_bits")
    return shared >= exact_shared_bits_required(partition, branch_bits)


def exact_classical_capacity_slack_bits(
    partition: QueryPartition,
    shared_bits: int,
    branch_bits: Sequence[int],
) -> int:
    shared = _validate_nonnegative_integer(shared_bits, name="shared_bits")
    return shared - exact_shared_bits_required(partition, branch_bits)


def equal_cell_exact_per_run_bits_lower_bound(
    record_bits: int,
    cell_size: int,
) -> int:
    """Exact per-execution communication after an equal-cell hint.

    With no pre-hint shared message, the sender transmits precisely the selected
    cell after its identity is known.  No protocol can use fewer than
    ``cell_size`` bits in the worst case.
    """

    partition = QueryPartition.equal_cells(record_bits, cell_size)
    return partition.cell_sizes[0]


@dataclass(frozen=True)
class ExactProgressiveAllocation:
    """A constructive exact bit allocation for one progressive protocol."""

    partition: QueryPartition
    shared_positions: tuple[Cell, ...]
    branch_positions: tuple[Cell, ...]

    def __post_init__(self) -> None:
        if (
            len(self.shared_positions) != self.partition.cell_count
            or len(self.branch_positions) != self.partition.cell_count
        ):
            raise ValueError("one shared and branch position set is required per cell")
        for cell, shared, branch in zip(
            self.partition.cells,
            self.shared_positions,
            self.branch_positions,
        ):
            if set(shared) & set(branch):
                raise ValueError("shared and branch positions must be disjoint")
            if set(shared) | set(branch) != set(cell):
                raise ValueError("allocation must cover every coordinate in its cell")

    @property
    def shared_bits_used(self) -> int:
        return sum(len(positions) for positions in self.shared_positions)

    @property
    def branch_bits_used(self) -> tuple[int, ...]:
        return tuple(len(positions) for positions in self.branch_positions)


def construct_exact_progressive_allocation(
    partition: QueryPartition,
    shared_bits: int,
    branch_bits: Sequence[int],
) -> ExactProgressiveAllocation:
    """Construct the canonical exact protocol whenever the capacity test passes."""

    shared_budget = _validate_nonnegative_integer(shared_bits, name="shared_bits")
    budgets = _validate_branch_budgets(partition, branch_bits)
    required = exact_shared_bits_required(partition, budgets)
    if shared_budget < required:
        raise ValueError(
            f"insufficient shared capacity: need at least {required} bits"
        )

    shared_positions: list[Cell] = []
    branch_positions: list[Cell] = []
    for cell, budget in zip(partition.cells, budgets):
        branch_count = min(len(cell), budget)
        shared_count = len(cell) - branch_count
        shared_positions.append(cell[:shared_count])
        branch_positions.append(cell[shared_count:])
    return ExactProgressiveAllocation(
        partition,
        tuple(shared_positions),
        tuple(branch_positions),
    )


def encode_shared_record(
    record: Sequence[int],
    allocation: ExactProgressiveAllocation,
) -> BitRecord:
    bits = _validate_binary_record(
        record,
        expected_length=allocation.partition.record_bits,
    )
    return tuple(
        bits[position]
        for positions in allocation.shared_positions
        for position in positions
    )


def encode_branch_record(
    record: Sequence[int],
    cell_index: int,
    allocation: ExactProgressiveAllocation,
) -> BitRecord:
    bits = _validate_binary_record(
        record,
        expected_length=allocation.partition.record_bits,
    )
    index = int(cell_index)
    if not 0 <= index < allocation.partition.cell_count:
        raise ValueError("cell_index out of range")
    return tuple(bits[position] for position in allocation.branch_positions[index])


def decode_progressive_coordinate(
    shared_message: Sequence[int],
    branch_message: Sequence[int],
    cell_index: int,
    coordinate: int,
    allocation: ExactProgressiveAllocation,
) -> int:
    shared = _validate_binary_record(
        shared_message,
        expected_length=allocation.shared_bits_used,
    )
    index = int(cell_index)
    if not 0 <= index < allocation.partition.cell_count:
        raise ValueError("cell_index out of range")
    branch = _validate_binary_record(
        branch_message,
        expected_length=len(allocation.branch_positions[index]),
    )
    target = int(coordinate)
    if target not in allocation.partition.cells[index]:
        raise ValueError("coordinate does not belong to the revealed cell")

    shared_offset = 0
    for positions in allocation.shared_positions:
        if target in positions:
            return shared[shared_offset + positions.index(target)]
        shared_offset += len(positions)
    branch_positions = allocation.branch_positions[index]
    return branch[branch_positions.index(target)]


def verify_exact_progressive_allocation(
    allocation: ExactProgressiveAllocation,
    *,
    max_record_bits: int = 16,
) -> bool:
    """Exhaustively verify all records and later coordinates for a small protocol."""

    bits = allocation.partition.record_bits
    if bits > max_record_bits:
        raise ValueError(
            f"exact protocol enumeration capped at {max_record_bits} record bits"
        )
    for record in product((0, 1), repeat=bits):
        shared = encode_shared_record(record, allocation)
        for cell_index, cell in enumerate(allocation.partition.cells):
            branch = encode_branch_record(record, cell_index, allocation)
            for coordinate in cell:
                if (
                    decode_progressive_coordinate(
                        shared,
                        branch,
                        cell_index,
                        coordinate,
                        allocation,
                    )
                    != record[coordinate]
                ):
                    return False
    return True


def cell_information_requirements_bits(
    partition: QueryPartition,
    coordinate_errors: Sequence[float],
) -> tuple[float, ...]:
    """Coordinatewise-Fano information requirement for each hint cell."""

    errors = tuple(_validate_error(error) for error in coordinate_errors)
    if len(errors) != partition.record_bits:
        raise ValueError("one coordinate error is required per record bit")
    return tuple(
        sum(1.0 - binary_entropy(errors[coordinate]) for coordinate in cell)
        for cell in partition.cells
    )


def shared_information_required_bits(
    cell_requirements: Sequence[float],
    branch_capacities: Sequence[float],
) -> float:
    """Shared capacity required after branch-specific capacities are credited."""

    requirements = tuple(float(value) for value in cell_requirements)
    capacities = tuple(float(value) for value in branch_capacities)
    if not requirements or len(requirements) != len(capacities):
        raise ValueError("requirements and capacities must have equal positive length")
    if any(value < 0.0 for value in requirements):
        raise ValueError("cell requirements must be nonnegative")
    if any(value < 0.0 for value in capacities):
        raise ValueError("branch capacities must be nonnegative")
    return sum(
        max(0.0, requirement - capacity)
        for requirement, capacity in zip(requirements, capacities)
    )


def classical_progressive_information_deficit_bits(
    partition: QueryPartition,
    shared_bits: float,
    branch_bits: Sequence[float],
    coordinate_errors: Sequence[float],
) -> float:
    """Positive deficit in the branch-aware classical information converse."""

    shared = float(shared_bits)
    branches = tuple(float(value) for value in branch_bits)
    if shared < 0.0 or any(value < 0.0 for value in branches):
        raise ValueError("capacities must be nonnegative")
    if len(branches) != partition.cell_count:
        raise ValueError("one branch capacity is required per cell")
    requirements = cell_information_requirements_bits(
        partition,
        coordinate_errors,
    )
    required_shared = shared_information_required_bits(requirements, branches)
    return max(0.0, required_shared - shared)


def uniform_error_progressive_total_capacity_lower_bound_bits(
    record_bits: int,
    error: float,
) -> float:
    bits = _validate_nonnegative_integer(record_bits, name="record_bits")
    if bits < 1:
        raise ValueError("record_bits must be positive")
    epsilon = _validate_error(error)
    return bits * (1.0 - binary_entropy(epsilon))


def equal_cell_bounded_error_per_run_lower_bound_bits(
    cell_size: int,
    error: float,
) -> float:
    """Best branch-aware converse for equal cells and uniform coordinate error.

    Optimizing shared plus one executed branch message puts all capacity after
    the cell hint, yielding the residual-cell bound s[1-H_2(error)].
    """

    size = _validate_nonnegative_integer(cell_size, name="cell_size")
    if size < 1:
        raise ValueError("cell_size must be positive")
    epsilon = _validate_error(error)
    return size * (1.0 - binary_entropy(epsilon))


def _capacity_multiplier(*, entanglement_assisted: bool) -> int:
    return 2 if entanglement_assisted else 1


def exact_quantum_progressive_feasible(
    partition: QueryPartition,
    shared_qubits: int,
    branch_qubits: Sequence[int],
    *,
    entanglement_assisted: bool = False,
) -> bool:
    """Exact qubit feasibility under the declared assistance model.

    Unassisted transmitted qubits carry at most one exactly recoverable
    classical bit each.  Receiver-side preshared entanglement raises the
    transmitted-qubit capacity to two bits by dense coding.
    """

    shared = _validate_nonnegative_integer(shared_qubits, name="shared_qubits")
    branches = _validate_branch_budgets(partition, branch_qubits)
    multiplier = _capacity_multiplier(
        entanglement_assisted=entanglement_assisted
    )
    effective_branch_bits = tuple(multiplier * value for value in branches)
    required_shared_bits = exact_shared_bits_required(
        partition,
        effective_branch_bits,
    )
    return multiplier * shared >= required_shared_bits


def exact_quantum_shared_qubits_required(
    partition: QueryPartition,
    branch_qubits: Sequence[int],
    *,
    entanglement_assisted: bool = False,
) -> int:
    branches = _validate_branch_budgets(partition, branch_qubits)
    multiplier = _capacity_multiplier(
        entanglement_assisted=entanglement_assisted
    )
    required_bits = exact_shared_bits_required(
        partition,
        tuple(multiplier * value for value in branches),
    )
    return ceil(required_bits / multiplier)


def equal_cell_exact_per_run_qubits_lower_bound(
    cell_size: int,
    *,
    entanglement_assisted: bool = False,
) -> int:
    size = _validate_nonnegative_integer(cell_size, name="cell_size")
    if size < 1:
        raise ValueError("cell_size must be positive")
    return ceil(
        size
        / _capacity_multiplier(
            entanglement_assisted=entanglement_assisted
        )
    )


def quantum_progressive_information_deficit_bits(
    partition: QueryPartition,
    shared_qubits: float,
    branch_qubits: Sequence[float],
    coordinate_errors: Sequence[float],
    *,
    entanglement_assisted: bool = False,
) -> float:
    """Positive classical-information deficit for progressive quantum messages."""

    shared = float(shared_qubits)
    branches = tuple(float(value) for value in branch_qubits)
    if shared < 0.0 or any(value < 0.0 for value in branches):
        raise ValueError("qubit capacities must be nonnegative")
    if len(branches) != partition.cell_count:
        raise ValueError("one branch qubit capacity is required per cell")
    multiplier = _capacity_multiplier(
        entanglement_assisted=entanglement_assisted
    )
    requirements = cell_information_requirements_bits(
        partition,
        coordinate_errors,
    )
    required_shared_information = shared_information_required_bits(
        requirements,
        tuple(multiplier * value for value in branches),
    )
    return max(0.0, required_shared_information - multiplier * shared)


def equal_cell_bounded_error_per_run_qubits_lower_bound(
    cell_size: int,
    error: float,
    *,
    entanglement_assisted: bool = False,
) -> float:
    bits = equal_cell_bounded_error_per_run_lower_bound_bits(cell_size, error)
    return bits / _capacity_multiplier(
        entanglement_assisted=entanglement_assisted
    )


def query_hint_reduction_factor(
    record_bits: int,
    cell_size: int,
) -> float:
    """Exact unresolved-coordinate reduction from an equal-cell query hint."""

    partition = QueryPartition.equal_cells(record_bits, cell_size)
    return partition.record_bits / partition.cell_sizes[0]


@dataclass(frozen=True)
class ProgressiveCutBudget:
    """Capacity bookkeeping for one shared stage and hint-specific branches."""

    partition: QueryPartition
    shared_units: int
    branch_units: tuple[int, ...]
    capacity_bits_per_unit: int = 1

    def __post_init__(self) -> None:
        _validate_nonnegative_integer(self.shared_units, name="shared_units")
        _validate_branch_budgets(self.partition, self.branch_units)
        multiplier = _validate_nonnegative_integer(
            self.capacity_bits_per_unit,
            name="capacity_bits_per_unit",
        )
        if multiplier < 1:
            raise ValueError("capacity_bits_per_unit must be positive")

    @property
    def exact_shared_units_required(self) -> int:
        effective_branch_bits = tuple(
            self.capacity_bits_per_unit * value
            for value in self.branch_units
        )
        required_bits = exact_shared_bits_required(
            self.partition,
            effective_branch_bits,
        )
        return ceil(required_bits / self.capacity_bits_per_unit)

    @property
    def exact_feasible(self) -> bool:
        return self.shared_units >= self.exact_shared_units_required

    def executed_units(self, cell_index: int) -> int:
        index = int(cell_index)
        if not 0 <= index < self.partition.cell_count:
            raise ValueError("cell_index out of range")
        return self.shared_units + self.branch_units[index]
