from itertools import product

import pytest

from simtheory.functional_networks import (
    LinearFunctionProblem,
    LinearSinkDemand,
    broadcast_network,
    common_summary_satisfies,
    complementary_side_information_problem,
    conditional_linear_rank,
    evaluate_linear_function_code,
    functional_cut_certificates,
    gf_rref_basis,
    heterogeneous_no_side_information_problem,
    linear_signature_map,
    minimum_common_linear_summary,
    rowspace_contains,
    search_scalar_linear_function_code,
    side_information_broadcast_separation,
    xor_broadcast_code,
)
from simtheory.network_coding import ScalarLinearCode, certificate_is_routing


def test_rref_basis_is_canonical_over_prime_fields():
    assert gf_rref_basis(((0, 1), (1, 1)), 2) == ((1, 0), (0, 1))
    assert gf_rref_basis(((1, 2, 0), (2, 1, 0), (0, 0, 0)), 3) == (
        (1, 2, 0),
    )
    assert gf_rref_basis((), 2, width=3) == ()


def test_rowspace_recoverability_and_conditional_rank():
    assert rowspace_contains(((1, 1),), ((1, 1),), 2, 2)
    assert not rowspace_contains(((1, 1),), ((1, 0),), 2, 2)
    assert rowspace_contains(((1, 1), (1, 0)), ((0, 1),), 2, 2)

    assert conditional_linear_rank(((0, 1),), (), 2, 2) == 1
    assert conditional_linear_rank(((0, 1),), ((1, 0),), 2, 2) == 1
    assert conditional_linear_rank(((1, 0),), ((1, 0),), 2, 2) == 0
    assert conditional_linear_rank(
        ((1, 0, 0), (0, 1, 0)),
        ((1, 1, 0),),
        3,
        2,
    ) == 1


def test_problem_canonicalizes_rows_and_computes_target_values():
    problem = LinearFunctionProblem(
        3,
        2,
        (
            LinearSinkDemand("t", ((4, -1), (2, 2)), ((3, 0),)),
        ),
    )
    demand = problem.demand("t")
    assert demand.target_rows == ((1, 2), (2, 2))
    assert demand.side_information_rows == ((0, 0),)
    assert problem.target_rank("t") == 2
    assert problem.side_information_rank("t") == 0
    assert problem.conditional_rank("t") == 2
    assert problem.target_values("t", (2, 1)) == (1, 0)


def test_per_sink_cut_rank_is_necessary_but_not_jointly_sufficient():
    network = broadcast_network()
    problem = heterogeneous_no_side_information_problem()
    cuts = functional_cut_certificates(network, "s", problem)
    assert [(cut.sink, cut.min_cut_symbols, cut.conditional_demand_rank) for cut in cuts] == [
        ("t1", 1, 1),
        ("t2", 1, 1),
    ]
    assert all(cut.necessary_cut_holds for cut in cuts)

    # One common scalar cannot span both independent target rows even though
    # every receiver separately passes its one-symbol cut condition.
    summary = minimum_common_linear_summary(problem)
    assert summary.complete
    assert summary.dimension == 2
    assert summary.basis == ((1, 0), (0, 1))

    search = search_scalar_linear_function_code(
        network,
        "s",
        problem,
        max_assignments=100,
    )
    assert not search.found
    assert search.exhausted
    assert search.assignments_examined == search.total_assignments == 16


def test_complementary_side_information_reduces_common_summary_to_xor():
    problem = complementary_side_information_problem()
    assert problem.conditional_rank("t1") == 1
    assert problem.conditional_rank("t2") == 1
    assert not common_summary_satisfies(problem, ())
    assert not common_summary_satisfies(problem, ((1, 0),))
    assert not common_summary_satisfies(problem, ((0, 1),))
    assert common_summary_satisfies(problem, ((1, 1),))

    summary = minimum_common_linear_summary(problem)
    assert summary.complete
    assert summary.dimension == 1
    assert summary.basis == ((1, 1),)


def test_xor_broadcast_code_decodes_every_source_vector_at_both_sinks():
    problem = complementary_side_information_problem()
    code = xor_broadcast_code()
    certificate = evaluate_linear_function_code(
        broadcast_network(),
        code,
        problem,
    )
    assert certificate.valid
    assert not certificate.propagation.valid  # Neither sink receives full x.
    assert not certificate_is_routing(certificate.propagation)

    vectors = certificate.propagation.global_vector_map()
    assert vectors == {"sb": (1, 1), "bt1": (1, 1), "bt2": (1, 1)}

    for source in product((0, 1), repeat=2):
        assert certificate.decode("t1", source) == problem.target_values("t1", source)
        assert certificate.decode("t2", source) == problem.target_values("t2", source)
        assert certificate.decode("t1", source) == (source[1],)
        assert certificate.decode("t2", source) == (source[0],)


def test_exhaustive_side_information_search_separates_coding_from_routing():
    network = broadcast_network()
    problem = complementary_side_information_problem()

    linear = search_scalar_linear_function_code(
        network,
        "s",
        problem,
        max_assignments=100,
    )
    assert linear.found
    assert linear.certificate is not None
    assert linear.certificate.valid

    routing = search_scalar_linear_function_code(
        network,
        "s",
        problem,
        routing_only=True,
        max_assignments=100,
    )
    assert not routing.found
    assert routing.exhausted
    assert routing.assignments_examined == routing.total_assignments == 16


def test_combined_broadcast_separation_certificate():
    certificate = side_information_broadcast_separation()
    assert certificate.valid
    assert certificate.no_side_summary.dimension == 2
    assert certificate.side_information_summary.dimension == 1
    assert certificate.side_information_summary.basis == ((1, 1),)
    assert certificate.side_information_linear_code.valid
    assert certificate.no_side_network_search.exhausted
    assert certificate.side_information_routing_search.exhausted
    assert certificate.side_information_linear_search.found


def test_common_summary_search_reports_caps_as_incomplete():
    problem = heterogeneous_no_side_information_problem()
    result = minimum_common_linear_summary(problem, max_generator_sets=1)
    assert not result.found
    assert not result.complete
    assert result.generator_sets_examined == 1


def test_dependent_targets_decode_without_overcounting_rank():
    problem = LinearFunctionProblem(
        2,
        2,
        (
            LinearSinkDemand("t1", ((1, 1), (1, 1)), ()),
            LinearSinkDemand("t2", ((1, 1),), ()),
        ),
    )
    assert problem.target_rank("t1") == 1
    assert problem.conditional_rank("t1") == 1
    summary = minimum_common_linear_summary(problem)
    assert summary.dimension == 1
    assert summary.basis == ((1, 1),)


def test_linear_predictive_signature_map_respects_declared_embedding():
    embedded = {
        "a": (0, 0, 0),
        "b": (1, 0, 1),
        "c": (0, 1, 1),
        "d": (1, 1, 0),
    }
    signatures = linear_signature_map(
        embedded,
        ((1, 1, 0), (0, 1, 1)),
        3,
        2,
    )
    assert signatures == {
        "a": (0, 0),
        "b": (1, 1),
        "c": (1, 0),
        "d": (0, 1),
    }


def test_code_and_problem_interface_validation():
    problem = complementary_side_information_problem()
    wrong_field = ScalarLinearCode(
        3,
        "s",
        ("t1", "t2"),
        2,
        (("sb", (1, 1)), ("bt1", (1,)), ("bt2", (1,))),
    )
    with pytest.raises(ValueError):
        evaluate_linear_function_code(broadcast_network(), wrong_field, problem)

    wrong_sinks = ScalarLinearCode(
        2,
        "s",
        ("t1",),
        2,
        (("sb", (1, 1)), ("bt1", (1,)), ("bt2", (1,))),
    )
    with pytest.raises(ValueError):
        evaluate_linear_function_code(broadcast_network(), wrong_sinks, problem)


def test_validation_rejects_invalid_function_problems():
    with pytest.raises(ValueError):
        LinearFunctionProblem(4, 2, (LinearSinkDemand("t", ((1, 0),)),))
    with pytest.raises(ValueError):
        LinearFunctionProblem(2, 2, (LinearSinkDemand("t", ((1,),)),))
    with pytest.raises(ValueError):
        LinearFunctionProblem(
            2,
            2,
            (
                LinearSinkDemand("t", ((1, 0),)),
                LinearSinkDemand("t", ((0, 1),)),
            ),
        )
    with pytest.raises(ValueError):
        LinearSinkDemand("t", ())
    with pytest.raises(ValueError):
        search_scalar_linear_function_code(
            broadcast_network(),
            "s",
            complementary_side_information_problem(),
            max_assignments=0,
        )
