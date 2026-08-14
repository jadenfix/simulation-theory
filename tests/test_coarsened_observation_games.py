from fractions import Fraction

import pytest

from simtheory.adaptive_drift_games import (
    finite_law_transition_model,
    tv_law_transition_model,
)
from simtheory.coarsened_observation_games import (
    exact_coarsened_observation_game,
    exact_endpoint_equivalence,
    exact_partition_refinement_value,
    full_observation_partition,
    no_observation_partition,
    observation_partition,
    partition_refines,
)
from simtheory.confusion_graphs import complete_graph


def _point_masses(count: int):
    return tuple(
        tuple(Fraction(1) if row == column else Fraction(0) for column in range(count))
        for row in range(count)
    )


def test_observation_partitions_are_canonical_and_refinement_is_ordered():
    coarse = observation_partition(("same", "same", "same"))
    middle = observation_partition(("a", "b", "b"))
    fine = observation_partition((10, 20, 30))

    assert coarse.valid and middle.valid and fine.valid
    assert coarse.labels == (0, 0, 0)
    assert middle.labels == (0, 1, 1)
    assert fine.labels == (0, 1, 2)
    assert partition_refines(middle, coarse)
    assert partition_refines(fine, middle)
    assert partition_refines(fine, coarse)
    assert not partition_refines(coarse, middle)


def test_no_and_full_observation_match_independent_endpoint_solvers():
    graph = complete_graph(3)
    model = tv_law_transition_model(_point_masses(3), 1)
    certificate = exact_endpoint_equivalence(graph, model, 0, 2)

    assert certificate.valid
    assert certificate.no_observation.initial_value == 3
    assert certificate.open_loop.selected_value == 3
    assert certificate.full_observation.initial_value == 2
    assert certificate.feedback.initial_value == 2


def test_strict_three_level_information_refinement_chain():
    graph = complete_graph(3)
    laws = _point_masses(3)
    identity = finite_law_transition_model(laws, ((0,), (1,), (2,)))
    coarse = no_observation_partition(3)
    middle = observation_partition((0, 1, 1))
    fine = full_observation_partition(3)

    coarse_to_middle = exact_partition_refinement_value(
        graph,
        identity,
        coarse,
        middle,
        (0, 1, 2),
        2,
    )
    middle_to_fine = exact_partition_refinement_value(
        graph,
        identity,
        middle,
        fine,
        (0, 1, 2),
        2,
    )

    assert coarse_to_middle.valid and middle_to_fine.valid
    assert coarse_to_middle.coarser.initial_value == 4
    assert coarse_to_middle.finer.initial_value == 3
    assert coarse_to_middle.information_gain == 1
    assert middle_to_fine.coarser.initial_value == 3
    assert middle_to_fine.finer.initial_value == 2
    assert middle_to_fine.information_gain == 1


def test_vector_frontier_prevents_hidden_state_reselection_across_time():
    graph = complete_graph(3)
    laws = _point_masses(3)
    identity = finite_law_transition_model(laws, ((0,), (1,), (2,)))
    certificate = exact_coarsened_observation_game(
        graph,
        identity,
        no_observation_partition(3),
        (0, 1, 2),
        3,
    )

    assert certificate.valid
    assert certificate.initial_value == 5
    # A scalar rectangular relaxation that lets nature reselect a hidden state
    # inside the information set every period would charge the per-period worst
    # length 2 three times.  The exact path-consistent value is strictly lower.
    assert certificate.initial_value < 6
    assert len(set(certificate.selected_codes)) == 3
    assert certificate.adversarial_path[0] == certificate.adversarial_path[1]
    assert certificate.adversarial_path[1] == certificate.adversarial_path[2]


def test_initial_observation_can_have_value_before_the_first_code_choice():
    graph = complete_graph(3)
    laws = _point_masses(3)
    identity = finite_law_transition_model(laws, ((0,), (1,), (2,)))

    none = exact_coarsened_observation_game(
        graph,
        identity,
        no_observation_partition(3),
        (0, 1, 2),
        1,
    )
    full = exact_coarsened_observation_game(
        graph,
        identity,
        full_observation_partition(3),
        (0, 1, 2),
        1,
    )

    assert none.valid and full.valid
    assert none.initial_value == 2
    assert full.initial_value == 1


def test_switching_penalty_is_replayed_on_information_set_policy_paths():
    graph = complete_graph(3)
    laws = _point_masses(3)
    identity = finite_law_transition_model(laws, ((0,), (1,), (2,)))
    result = exact_coarsened_observation_game(
        graph,
        identity,
        no_observation_partition(3),
        (0, 1, 2),
        2,
        switching_penalty=Fraction(2),
    )

    assert result.valid
    assert result.initial_value == 4
    assert result.selected_codes[0] == result.selected_codes[1]


def test_directed_transition_paths_remain_actual_state_consistent():
    graph = complete_graph(3)
    model = finite_law_transition_model(
        _point_masses(3),
        (
            (0, 1),
            (1, 2),
            (2,),
        ),
    )
    result = exact_coarsened_observation_game(
        graph,
        model,
        observation_partition((0, 0, 1)),
        (0,),
        3,
    )

    assert result.valid
    assert all(
        right in model.successors[left]
        for left, right in zip(result.adversarial_path, result.adversarial_path[1:])
    )
    assert all(
        mask & (1 << state)
        for mask, state in zip(result.information_path, result.adversarial_path)
    )


def test_invalid_partitions_initial_sets_and_caps_are_rejected():
    graph = complete_graph(3)
    model = tv_law_transition_model(_point_masses(3), 1)

    with pytest.raises(ValueError):
        observation_partition(())
    with pytest.raises(ValueError):
        exact_coarsened_observation_game(
            graph,
            model,
            observation_partition((0, 0)),
            (0,),
            2,
        )
    with pytest.raises(ValueError):
        exact_coarsened_observation_game(
            graph,
            model,
            no_observation_partition(3),
            (),
            2,
        )
    with pytest.raises(ValueError):
        exact_coarsened_observation_game(
            graph,
            model,
            no_observation_partition(3),
            (0, 1, 2),
            3,
            max_frontier_entries=1,
        )
