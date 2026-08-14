from math import isclose

import pytest

from simtheory.predictive_networks import (
    CausalCapacityNetwork,
    binary_coordinate_query_family,
    deterministic_query_total_variation,
)
from simtheory.stochastic_predictive import (
    FiniteStochasticQueryFamily,
    approximate_stochastic_network_certificate,
    bernoulli_minimax_center,
    categorical_kl_nats,
    categorical_total_variation,
    exact_stochastic_network_feasible,
    maximum_stochastic_predictive_packing,
    minimum_target_centered_cover,
    optimal_bernoulli_cover_assignment,
    optimal_bernoulli_cover_centers,
    optimal_bernoulli_network_feasible,
    optimal_bernoulli_network_units_required,
    optimal_bernoulli_state_count,
    pinsker_tv_upper_bound_from_weighted_kl,
    single_bernoulli_query_family,
    stochastic_predictive_state_bracket,
    target_centered_cover_assignment,
    weighted_query_kl_nats,
    weighted_query_total_variation,
    worst_query_total_variation,
)


def test_exact_stochastic_equivalence_classes():
    family = single_bernoulli_query_family(
        (0.2, 0.2, 0.8),
        ("a", "b", "c"),
    )
    assert family.exact_class_count == 2
    assert family.exact_predictive_bits == 1
    assert sorted(map(len, family.exact_equivalence_classes)) == [1, 2]
    labels = family.exact_class_label_map()
    assert labels["a"] == labels["b"]
    assert labels["a"] != labels["c"]


def test_deterministic_embedding_preserves_tv_geometry():
    deterministic = binary_coordinate_query_family(3)
    stochastic = FiniteStochasticQueryFamily.from_deterministic(deterministic)
    left = (0, 1, 0)
    right = (1, 1, 1)
    weights = (0.2, 0.3, 0.5)
    assert isclose(
        weighted_query_total_variation(
            stochastic,
            left,
            right,
            weights,
        ),
        deterministic_query_total_variation(
            deterministic,
            left,
            right,
            weights,
        ),
    )
    assert stochastic.exact_class_count == deterministic.class_count


def test_weighted_stochastic_tv_and_worst_query_geometry():
    family = FiniteStochasticQueryFamily(
        ("a", "b"),
        ("q1", "q2"),
        ((0, 1), (0, 1)),
        (
            ((0.9, 0.1), (0.2, 0.8)),
            ((0.6, 0.4), (0.8, 0.2)),
        ),
    )
    assert isclose(
        weighted_query_total_variation(
            family,
            "a",
            "b",
            (0.25, 0.75),
        ),
        0.525,
    )
    assert isclose(worst_query_total_variation(family, "a", "b"), 0.6)
    joint = family.joint_law("a", (0.25, 0.75))
    assert isclose(sum(joint.values()), 1.0)


def test_weighted_kl_chain_and_pinsker():
    family = FiniteStochasticQueryFamily(
        ("a", "b"),
        ("q1", "q2"),
        ((0, 1), (0, 1)),
        (
            ((0.8, 0.2), (0.3, 0.7)),
            ((0.5, 0.5), (0.6, 0.4)),
        ),
    )
    expected = 0.4 * categorical_kl_nats((0.8, 0.2), (0.5, 0.5))
    expected += 0.6 * categorical_kl_nats((0.3, 0.7), (0.6, 0.4))
    assert isclose(
        weighted_query_kl_nats(
            family,
            "a",
            "b",
            (0.4, 0.6),
        ),
        expected,
    )
    tv = weighted_query_total_variation(
        family,
        "a",
        "b",
        (0.4, 0.6),
    )
    assert tv <= pinsker_tv_upper_bound_from_weighted_kl(
        family,
        "a",
        "b",
        (0.4, 0.6),
    ) + 1e-12


def test_target_cover_and_packing_match_on_even_bernoulli_grid():
    family = single_bernoulli_query_family(
        (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    )
    packing = maximum_stochastic_predictive_packing(
        family,
        0.2,
        max_records=10,
    )
    cover = minimum_target_centered_cover(
        family,
        0.2,
        max_records=10,
    )
    assert len(packing) == 2
    assert len(cover) == 2
    assignment = target_centered_cover_assignment(family, cover, 0.2)
    assert set(assignment) == set(family.records)

    bracket = stochastic_predictive_state_bracket(
        family,
        0.2,
        max_records=10,
    )
    assert bracket.packing_size == 2
    assert bracket.target_cover_size == 2
    assert bracket.lower_bits == 1
    assert bracket.target_cover_upper_bits == 1


def test_target_centered_cover_can_be_conservative():
    family = single_bernoulli_query_family((0.0, 1.0))
    bracket = stochastic_predictive_state_bracket(
        family,
        0.5,
        max_records=4,
    )
    assert bracket.packing_size == 1
    assert bracket.target_cover_size == 2

    assert optimal_bernoulli_state_count((0.0, 1.0), 0.5) == 1
    assert optimal_bernoulli_cover_centers((0.0, 1.0), 0.5) == (0.5,)
    assert optimal_bernoulli_cover_assignment(
        (0.0, 1.0),
        (0.5,),
        0.5,
    ) == (0, 0)


def test_bernoulli_minimax_center_and_exact_interval_cover():
    center, radius = bernoulli_minimax_center((0.1, 0.4, 0.9))
    assert isclose(center, 0.5)
    assert isclose(radius, 0.4)

    parameters = (0.0, 0.1, 0.4, 0.5, 0.9, 1.0)
    centers = optimal_bernoulli_cover_centers(parameters, 0.1)
    assert len(centers) == 3
    assert optimal_bernoulli_cover_assignment(
        parameters,
        centers,
        0.1,
    ) == (0, 0, 1, 1, 2, 2)


def test_approximate_network_certificate_impossible_feasible_and_unresolved():
    family = single_bernoulli_query_family(
        (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    )
    disconnected = CausalCapacityNetwork(("s", "t"), ())
    impossible = approximate_stochastic_network_certificate(
        disconnected,
        "s",
        "t",
        family,
        0.2,
        max_records=10,
    )
    assert impossible.status == "impossible"
    assert impossible.lower_units == 1
    assert impossible.target_cover_upper_units == 1

    one_bit = CausalCapacityNetwork(
        ("s", "t"),
        (("s", "t", 1),),
    )
    feasible = approximate_stochastic_network_certificate(
        one_bit,
        "s",
        "t",
        family,
        0.2,
        max_records=10,
    )
    assert feasible.status == "constructively-feasible"
    assert feasible.routed_units == 1
    assert len(feasible.assignment) == family.record_count

    extreme = single_bernoulli_query_family((0.0, 1.0))
    unresolved = approximate_stochastic_network_certificate(
        disconnected,
        "s",
        "t",
        extreme,
        0.5,
        max_records=4,
    )
    assert unresolved.status == "unresolved"
    assert optimal_bernoulli_network_units_required(
        (0.0, 1.0),
        0.5,
    ) == 0
    assert optimal_bernoulli_network_feasible(
        disconnected,
        "s",
        "t",
        (0.0, 1.0),
        0.5,
    )


def test_exact_stochastic_network_uses_law_classes_not_record_count():
    family = single_bernoulli_query_family(
        (0.2, 0.2, 0.8),
        ("a", "b", "c"),
    )
    one_bit = CausalCapacityNetwork(
        ("s", "t"),
        (("s", "t", 1),),
    )
    assert exact_stochastic_network_feasible(
        one_bit,
        "s",
        "t",
        family,
    )

    one_class = single_bernoulli_query_family(
        (0.2, 0.2),
        ("a", "b"),
    )
    disconnected = CausalCapacityNetwork(("s", "t"), ())
    assert exact_stochastic_network_feasible(
        disconnected,
        "s",
        "t",
        one_class,
    )


def test_categorical_boundary_values():
    assert isclose(categorical_total_variation((1, 0), (0, 1)), 1.0)
    assert categorical_kl_nats((1, 0), (0, 1)) == float("inf")


def test_validation_boundaries():
    with pytest.raises(ValueError):
        single_bernoulli_query_family(())
    with pytest.raises(ValueError):
        single_bernoulli_query_family((1.1,))
    with pytest.raises(ValueError):
        FiniteStochasticQueryFamily(
            ("a",),
            ("q",),
            ((0, 1),),
            (((0.2, 0.2),),),
        )
    with pytest.raises(ValueError):
        minimum_target_centered_cover(
            single_bernoulli_query_family(
                tuple(index / 30 for index in range(30))
            ),
            0.1,
            max_records=26,
        )
    with pytest.raises(ValueError):
        target_centered_cover_assignment(
            single_bernoulli_query_family((0.0, 1.0)),
            (0,),
            0.2,
        )
