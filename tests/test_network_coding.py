import pytest

from simtheory.network_coding import (
    ScalarLinearCode,
    UnitCapacityDAG,
    UnitEdge,
    butterfly_linear_code,
    butterfly_network,
    butterfly_separation_certificate,
    certificate_is_routing,
    evaluate_scalar_linear_code,
    gf_rank,
    gf_solve,
    multicast_cut_certificate,
    predictive_multicast_certificate,
    search_scalar_linear_multicast_code,
)
from simtheory.predictive_networks import binary_coordinate_query_family


def test_gf_rank_and_solve_over_multiple_prime_fields():
    assert gf_rank(((1, 0), (0, 1)), 2) == 2
    assert gf_rank(((1, 1), (1, 1)), 2) == 1
    # Determinant is one modulo three, so this matrix is full rank over F_3.
    assert gf_rank(((1, 2, 0), (0, 1, 1), (1, 0, 2)), 3) == 3

    matrix = (
        (1, 0, 1),
        (0, 1, 1),
    )
    solution = gf_solve(matrix, (1, 1), 2)
    assert solution is not None
    assert tuple(
        sum(row[column] * solution[column] for column in range(3)) % 2
        for row in matrix
    ) == (1, 1)
    assert gf_solve(((1,), (0,)), (0, 1), 2) is None


def test_butterfly_mincuts_are_two_for_both_sinks():
    network = butterfly_network()
    cuts = multicast_cut_certificate(network, "s", ("t1", "t2"), 2)
    assert cuts.necessary_cuts_hold
    assert dict(cuts.sink_min_cuts) == {"t1": 2, "t2": 2}


def test_unit_edge_lookup_is_total_on_declared_ids_and_rejects_unknown_ids():
    network = butterfly_network()
    assert network.edge("cd") == UnitEdge("cd", "c", "d")
    with pytest.raises(ValueError, match="unknown unit edge"):
        network.edge("missing")


def test_explicit_butterfly_linear_code_decodes_at_both_sinks():
    network = butterfly_network()
    certificate = evaluate_scalar_linear_code(network, butterfly_linear_code())
    assert certificate.valid
    assert certificate.sink_ranks == {"t1": 2, "t2": 2}
    vectors = certificate.global_vector_map()
    assert vectors["sa"] == (1, 0)
    assert vectors["sb"] == (0, 1)
    assert vectors["cd"] == (1, 1)
    assert vectors["dt1"] == (1, 1)
    assert vectors["dt2"] == (1, 1)
    assert not certificate_is_routing(certificate)

    for decoder in certificate.decoders:
        assert decoder.decodes_all
        assert len(decoder.source_coordinate_coefficients) == 2


def test_exhaustive_search_finds_linear_code_and_rules_out_routing():
    network = butterfly_network()
    linear = search_scalar_linear_multicast_code(
        network,
        "s",
        ("t1", "t2"),
        2,
        2,
        max_assignments=10_000,
    )
    assert linear.found
    assert linear.certificate is not None
    assert linear.certificate.valid

    routing = search_scalar_linear_multicast_code(
        network,
        "s",
        ("t1", "t2"),
        2,
        2,
        routing_only=True,
        max_assignments=10_000,
    )
    assert not routing.found
    assert routing.exhausted
    assert routing.assignments_examined == routing.total_assignments == 4096


def test_butterfly_separation_certificate_combines_all_checks():
    certificate = butterfly_separation_certificate()
    assert certificate.valid
    assert certificate.linear_certificate.valid
    assert certificate.cut_certificate.necessary_cuts_hold
    assert certificate.exhaustive_routing_result.exhausted


def test_predictive_class_labels_multicast_over_butterfly():
    family = binary_coordinate_query_family(2)
    linear = evaluate_scalar_linear_code(
        butterfly_network(),
        butterfly_linear_code(),
    )
    certificate = predictive_multicast_certificate(family, linear)
    assert certificate.valid
    assert family.class_count == 4
    assert family.exact_predictive_bits == 2

    vectors = dict(certificate.record_symbol_vectors)
    labels = family.class_label_map()
    assert set(vectors) == set(family.records)
    assert set(vectors.values()) == {(0, 0), (1, 0), (0, 1), (1, 1)}

    # The field-vector naming is arbitrary. The invariant is that records in
    # one predictive class share a vector and distinct classes receive distinct
    # vectors; it need not equal the original record tuple coordinate-for-coordinate.
    for left in family.records:
        for right in family.records:
            assert (vectors[left] == vectors[right]) == (
                labels[left] == labels[right]
            )


def test_predictive_embedding_rejects_too_many_classes():
    family = binary_coordinate_query_family(3)
    linear = evaluate_scalar_linear_code(
        butterfly_network(),
        butterfly_linear_code(),
    )
    with pytest.raises(ValueError):
        predictive_multicast_certificate(family, linear)


def test_local_linearity_validation_rejects_wrong_coefficient_lengths():
    code = ScalarLinearCode(
        2,
        "s",
        ("t1", "t2"),
        2,
        tuple(
            (edge_id, (() if edge_id == "ac" else coefficients))
            for edge_id, coefficients in butterfly_linear_code().local_coefficients
        ),
    )
    with pytest.raises(ValueError):
        evaluate_scalar_linear_code(butterfly_network(), code)


def test_search_cap_reports_incomplete_instead_of_false_impossibility():
    result = search_scalar_linear_multicast_code(
        butterfly_network(),
        "s",
        ("t1", "t2"),
        2,
        2,
        routing_only=True,
        max_assignments=100,
    )
    assert not result.found
    assert not result.exhausted
    assert result.assignments_examined == 100
    assert result.total_assignments == 4096


def test_capacity_network_expansion_preserves_parallel_units():
    from simtheory.predictive_networks import CausalCapacityNetwork

    capacity = CausalCapacityNetwork(
        ("s", "m", "t"),
        (("s", "m", 3), ("m", "t", 2)),
    )
    unit = UnitCapacityDAG.from_capacity_network(capacity)
    assert len(unit.edges) == 5
    assert unit.min_cut_capacity("s", "t") == 2
    assert len(unit.outgoing("s")) == 3
    assert len(unit.incoming("t")) == 2


def test_validation_boundaries():
    with pytest.raises(ValueError):
        gf_rank(((1, 0),), 4)
    with pytest.raises(ValueError):
        UnitCapacityDAG(
            ("a", "b"),
            (UnitEdge("ab", "a", "b"), UnitEdge("ba", "b", "a")),
        )
    with pytest.raises(ValueError):
        ScalarLinearCode(4, "s", ("t",), 1, (("e", (1,)),))
    with pytest.raises(ValueError):
        search_scalar_linear_multicast_code(
            butterfly_network(),
            "s",
            ("t1", "t2"),
            2,
            2,
            max_assignments=0,
        )
