from math import isclose

import pytest

from simtheory.progressive_queries import (
    ProgressiveCutBudget,
    QueryPartition,
    cell_information_requirements_bits,
    classical_progressive_information_deficit_bits,
    construct_exact_progressive_allocation,
    decode_progressive_coordinate,
    encode_branch_record,
    encode_shared_record,
    equal_cell_bounded_error_per_run_lower_bound_bits,
    equal_cell_bounded_error_per_run_qubits_lower_bound,
    equal_cell_exact_per_run_bits_lower_bound,
    equal_cell_exact_per_run_qubits_lower_bound,
    exact_classical_capacity_slack_bits,
    exact_classical_progressive_feasible,
    exact_quantum_progressive_feasible,
    exact_quantum_shared_qubits_required,
    exact_shared_bits_required,
    query_hint_reduction_factor,
    shared_information_required_bits,
    uniform_error_progressive_total_capacity_lower_bound_bits,
    verify_exact_progressive_allocation,
)


def test_query_partition_canonicalization_and_coordinate_lookup():
    partition = QueryPartition(((3, 2), (0, 1), (5, 4)))
    assert partition.cells == ((2, 3), (0, 1), (4, 5))
    assert partition.record_bits == 6
    assert partition.cell_sizes == (2, 2, 2)
    assert partition.cell_of_coordinate(0) == 1
    assert partition.cell_of_coordinate(5) == 2


def test_exact_classical_progressive_tradeoff_is_sharp():
    partition = QueryPartition.equal_cells(12, 3)
    branch = (1, 1, 1, 1)
    assert exact_shared_bits_required(partition, branch) == 8
    assert exact_classical_progressive_feasible(partition, 8, branch)
    assert not exact_classical_progressive_feasible(partition, 7, branch)
    assert exact_classical_capacity_slack_bits(partition, 10, branch) == 2
    assert exact_classical_capacity_slack_bits(partition, 7, branch) == -1

    # No pre-hint message means the selected residual cell must be sent.
    assert equal_cell_exact_per_run_bits_lower_bound(12, 3) == 3
    assert query_hint_reduction_factor(12, 3) == 4.0


def test_nonuniform_cells_obey_sum_of_uncovered_bits():
    partition = QueryPartition(((0,), (1, 2, 3), (4, 5, 6, 7)))
    branch = (0, 2, 1)
    # uncovered = 1 + 1 + 3
    assert exact_shared_bits_required(partition, branch) == 5
    assert exact_classical_progressive_feasible(partition, 5, branch)
    assert not exact_classical_progressive_feasible(partition, 4, branch)


def test_constructed_exact_protocol_is_exhaustively_correct():
    partition = QueryPartition(((0, 3), (1, 4, 6), (2, 5, 7)))
    allocation = construct_exact_progressive_allocation(
        partition,
        shared_bits=5,
        branch_bits=(1, 1, 1),
    )
    assert allocation.shared_bits_used == 5
    assert allocation.branch_bits_used == (1, 1, 1)
    assert verify_exact_progressive_allocation(allocation)

    record = (1, 0, 1, 1, 0, 0, 1, 1)
    shared = encode_shared_record(record, allocation)
    for cell_index, cell in enumerate(partition.cells):
        branch = encode_branch_record(record, cell_index, allocation)
        for coordinate in cell:
            assert (
                decode_progressive_coordinate(
                    shared,
                    branch,
                    cell_index,
                    coordinate,
                    allocation,
                )
                == record[coordinate]
            )


def test_bounded_error_branch_aware_converse():
    partition = QueryPartition.equal_cells(8, 2)
    errors = (0.0,) * 8
    requirements = cell_information_requirements_bits(partition, errors)
    assert requirements == (2.0, 2.0, 2.0, 2.0)
    assert shared_information_required_bits(requirements, (1.0,) * 4) == 4.0
    assert (
        classical_progressive_information_deficit_bits(
            partition,
            shared_bits=4,
            branch_bits=(1, 1, 1, 1),
            coordinate_errors=errors,
        )
        == 0.0
    )
    assert (
        classical_progressive_information_deficit_bits(
            partition,
            shared_bits=3,
            branch_bits=(1, 1, 1, 1),
            coordinate_errors=errors,
        )
        == 1.0
    )


def test_uniform_error_converse_reduces_to_residual_cell_size():
    error = 0.1
    total = uniform_error_progressive_total_capacity_lower_bound_bits(100, error)
    residual = equal_cell_bounded_error_per_run_lower_bound_bits(10, error)
    assert isclose(total, 10.0 * residual, abs_tol=1e-12)
    assert 5.0 < residual < 6.0


def test_quantum_exact_tradeoff_and_entanglement_factor_two():
    partition = QueryPartition.equal_cells(12, 3)

    # Unassisted: one branch qubit leaves two bits per cell for the shared stage.
    assert exact_quantum_shared_qubits_required(
        partition,
        (1, 1, 1, 1),
    ) == 8
    assert exact_quantum_progressive_feasible(
        partition,
        8,
        (1, 1, 1, 1),
    )
    assert not exact_quantum_progressive_feasible(
        partition,
        7,
        (1, 1, 1, 1),
    )

    # Assisted: one branch qubit can dense-code two bits, leaving one bit/cell.
    assert exact_quantum_shared_qubits_required(
        partition,
        (1, 1, 1, 1),
        entanglement_assisted=True,
    ) == 2
    assert exact_quantum_progressive_feasible(
        partition,
        2,
        (1, 1, 1, 1),
        entanglement_assisted=True,
    )
    assert not exact_quantum_progressive_feasible(
        partition,
        1,
        (1, 1, 1, 1),
        entanglement_assisted=True,
    )

    assert equal_cell_exact_per_run_qubits_lower_bound(3) == 3
    assert (
        equal_cell_exact_per_run_qubits_lower_bound(
            3,
            entanglement_assisted=True,
        )
        == 2
    )


def test_quantum_bounded_error_converse_scales_by_capacity_multiplier():
    error = 0.1
    unassisted = equal_cell_bounded_error_per_run_qubits_lower_bound(20, error)
    assisted = equal_cell_bounded_error_per_run_qubits_lower_bound(
        20,
        error,
        entanglement_assisted=True,
    )
    assert isclose(assisted, 0.5 * unassisted, abs_tol=1e-12)


def test_progressive_cut_budget_wrapper():
    partition = QueryPartition.equal_cells(8, 2)
    classical = ProgressiveCutBudget(partition, 4, (1, 1, 1, 1))
    assert classical.exact_shared_units_required == 4
    assert classical.exact_feasible
    assert classical.executed_units(2) == 5

    assisted = ProgressiveCutBudget(
        partition,
        0,
        (1, 1, 1, 1),
        capacity_bits_per_unit=2,
    )
    assert assisted.exact_shared_units_required == 0
    assert assisted.exact_feasible
    assert assisted.executed_units(0) == 1


def test_validation_rejects_invalid_partitions_and_budgets():
    with pytest.raises(ValueError):
        QueryPartition(())
    with pytest.raises(ValueError):
        QueryPartition(((0, 1), (1, 2)))
    with pytest.raises(ValueError):
        QueryPartition(((0, 2),))
    with pytest.raises(ValueError):
        QueryPartition.equal_cells(10, 3)
    with pytest.raises(ValueError):
        exact_shared_bits_required(QueryPartition.equal_cells(4, 2), (1,))
    with pytest.raises(ValueError):
        construct_exact_progressive_allocation(
            QueryPartition.equal_cells(4, 2),
            shared_bits=1,
            branch_bits=(1, 1),
        )
    with pytest.raises(ValueError):
        verify_exact_progressive_allocation(
            construct_exact_progressive_allocation(
                QueryPartition.single_cell(17),
                shared_bits=17,
                branch_bits=(0,),
            )
        )
