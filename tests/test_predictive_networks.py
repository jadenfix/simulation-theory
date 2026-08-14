from math import isclose

import pytest

from simtheory.predictive_networks import (
    CausalCapacityNetwork,
    FiniteQueryFamily,
    approximate_predictive_cut_deficit_units,
    binary_coordinate_query_family,
    binary_parity_query_family,
    deterministic_query_total_variation,
    exact_predictive_network_certificate,
    exact_predictive_network_deficit_units,
    exact_predictive_network_units_required,
    exact_single_sink_network_feasible,
    maximum_predictive_packing,
    multisink_exact_cut_deficits_units,
    predictive_packing_bits_lower_bound,
    route_exact_predictive_class,
)


def _three_unit_network() -> CausalCapacityNetwork:
    return CausalCapacityNetwork(
        ("s", "a", "b", "t"),
        (
            ("s", "a", 2),
            ("s", "b", 1),
            ("a", "t", 1),
            ("a", "b", 1),
            ("b", "t", 2),
        ),
    )


def test_coordinate_and_parity_equivalence_classes():
    coordinate = binary_coordinate_query_family(4)
    assert coordinate.record_count == 16
    assert coordinate.class_count == 16
    assert coordinate.exact_predictive_bits == 4
    assert all(len(group) == 1 for group in coordinate.equivalence_classes)

    total_parity = binary_parity_query_family(4, (0b1111,))
    assert total_parity.class_count == 2
    assert total_parity.exact_predictive_bits == 1
    assert sorted(map(len, total_parity.equivalence_classes)) == [8, 8]

    two_parities = binary_parity_query_family(4, (0b0011, 0b1100))
    assert two_parities.class_count == 4
    assert two_parities.exact_predictive_bits == 2
    assert sorted(map(len, two_parities.equivalence_classes)) == [4, 4, 4, 4]


def test_function_family_can_collapse_many_records_to_one_predictive_class():
    family = FiniteQueryFamily.from_functions(
        tuple(range(8)),
        (("mod2", lambda value: value % 2),),
    )
    assert family.class_count == 2
    assert family.exact_predictive_bits == 1
    labels = family.class_label_map()
    assert labels[0] == labels[2]
    assert labels[0] != labels[1]


def test_weighted_deterministic_query_tv_is_disagreement_mass():
    family = binary_coordinate_query_family(4)
    left = (0, 0, 1, 1)
    right = (1, 0, 0, 1)
    weights = (0.1, 0.2, 0.3, 0.4)
    assert isclose(
        deterministic_query_total_variation(family, left, right, weights),
        0.4,
    )
    assert isclose(
        deterministic_query_total_variation(family, left, right),
        0.5,
    )


def test_exact_maximum_predictive_packings():
    family = binary_coordinate_query_family(4)
    all_records = maximum_predictive_packing(
        family,
        0.1,
        max_records=16,
    )
    assert len(all_records) == 16

    distance_two_code = maximum_predictive_packing(
        family,
        0.2,
        max_records=16,
    )
    assert len(distance_two_code) == 8
    assert (
        predictive_packing_bits_lower_bound(
            family,
            0.2,
            max_records=16,
        )
        == 3
    )


def test_max_flow_equals_min_cut_and_route_decomposition_respects_edges():
    network = _three_unit_network()
    result = network.max_flow("s", "t")
    assert result.value == 3
    assert result.cut_capacity == 3

    routes = network.route_units("s", "t", 3)
    assert sum(route.units for route in routes) == 3

    used: dict[tuple[str, str], int] = {}
    for route in routes:
        assert route.nodes[0] == "s"
        assert route.nodes[-1] == "t"
        for edge in zip(route.nodes, route.nodes[1:]):
            used[edge] = used.get(edge, 0) + route.units
    for (left, right), units in used.items():
        assert units <= network.edge_capacity(left, right)


def test_exact_single_sink_predictive_network_feasibility():
    network = _three_unit_network()
    coordinate_three = binary_coordinate_query_family(3)
    coordinate_four = binary_coordinate_query_family(4)
    total_parity = binary_parity_query_family(4, (0b1111,))

    assert exact_predictive_network_units_required(coordinate_three) == 3
    assert exact_single_sink_network_feasible(
        network,
        "s",
        "t",
        coordinate_three,
    )
    assert not exact_single_sink_network_feasible(
        network,
        "s",
        "t",
        coordinate_four,
    )
    assert (
        exact_predictive_network_deficit_units(
            network,
            "s",
            "t",
            coordinate_four,
        )
        == 1
    )
    assert exact_single_sink_network_feasible(
        network,
        "s",
        "t",
        total_parity,
    )
    assert (
        sum(
            route.units
            for route in route_exact_predictive_class(
                network,
                "s",
                "t",
                coordinate_three,
            )
        )
        == 3
    )


def test_capacity_multiplier_models_entanglement_assisted_payload():
    network = CausalCapacityNetwork(
        ("s", "t"),
        (("s", "t", 2),),
    )
    family = binary_coordinate_query_family(3)
    assert not exact_single_sink_network_feasible(
        network,
        "s",
        "t",
        family,
    )
    assert exact_single_sink_network_feasible(
        network,
        "s",
        "t",
        family,
        capacity_bits_per_unit=2,
    )
    assert (
        exact_predictive_network_units_required(
            family,
            capacity_bits_per_unit=2,
        )
        == 2
    )


def test_approximate_packing_cut_deficit():
    family = binary_coordinate_query_family(4)
    network = CausalCapacityNetwork(
        ("s", "t"),
        (("s", "t", 2),),
    )
    assert (
        approximate_predictive_cut_deficit_units(
            network,
            "s",
            "t",
            family,
            0.2,
            max_records=16,
        )
        == 1
    )
    assert (
        approximate_predictive_cut_deficit_units(
            network,
            "s",
            "t",
            family,
            0.2,
            max_records=16,
            capacity_bits_per_unit=2,
        )
        == 0
    )


def test_multisink_cut_deficits_are_per_sink_necessary_conditions():
    network = CausalCapacityNetwork(
        ("s", "a", "t1", "t2"),
        (
            ("s", "a", 3),
            ("a", "t1", 3),
            ("a", "t2", 1),
        ),
    )
    deficits = multisink_exact_cut_deficits_units(
        network,
        "s",
        {
            "t1": binary_coordinate_query_family(3),
            "t2": binary_coordinate_query_family(2),
        },
    )
    assert deficits == {"t1": 0, "t2": 1}


def test_certificate_matches_required_route_and_min_cut():
    network = _three_unit_network()
    family = binary_coordinate_query_family(3)
    certificate = exact_predictive_network_certificate(
        network,
        "s",
        "t",
        family,
    )
    assert certificate.required_units == 3
    assert certificate.min_cut_units == 3
    assert certificate.feasible
    assert certificate.routed_units == 3


def test_validation_boundaries():
    with pytest.raises(ValueError):
        FiniteQueryFamily((), ("q",), ())
    with pytest.raises(ValueError):
        FiniteQueryFamily(((0,), [1]), ("q",), ((0,), (1,)))
    with pytest.raises(ValueError):
        binary_coordinate_query_family(17, max_record_bits=16)
    with pytest.raises(ValueError):
        binary_parity_query_family(4, (0,))
    with pytest.raises(ValueError):
        maximum_predictive_packing(
            binary_coordinate_query_family(5),
            0.1,
            max_records=28,
        )
    with pytest.raises(ValueError):
        CausalCapacityNetwork(
            ("a", "b"),
            (("a", "b", 1), ("b", "a", 1)),
        )
    with pytest.raises(ValueError):
        CausalCapacityNetwork(("a", "a"), ())
    with pytest.raises(ValueError):
        CausalCapacityNetwork(("a", "b"), (("a", "b", 0),))
    with pytest.raises(ValueError):
        _three_unit_network().route_units("s", "t", 4)
