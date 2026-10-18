"""Regression tests: hand-built forged certificates must not validate.

Each test reproduces one forgery from the validator audit (docs/math-audit-
publication-readiness.md, "Validator audit") against the hardened ``valid``
properties. Before the fix every forged object below validated; the honest
builder output must still validate.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from fractions import Fraction as Q
from itertools import combinations

import pytest

from simtheory.confusion_graphs import (
    ChromaticCertificate,
    ConfusionGraph,
    ConfusionMonotonicityCertificate,
    exact_chromatic_certificate,
)

K3 = ConfusionGraph.from_edges((0, 1, 2), tuple(combinations((0, 1, 2), 2)))
E3 = ConfusionGraph.from_edges((0, 1, 2), ())
K4 = ConfusionGraph.from_edges((0, 1, 2, 3), tuple(combinations((0, 1, 2, 3), 2)))
POINT_LAWS = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


# ------------------------------------------------------------ TV transport


def test_tv_expectation_zero_radius_and_non_greedy_forgeries_fail():
    from simtheory.distributionally_robust_codes import TVTransfer, maximize_expectation_tv_ball

    p, v, r = (Q(1, 2), Q(1, 2)), (Q(0), Q(1)), Q(1, 2)
    real = maximize_expectation_tv_ball(p, v, r)
    assert real.valid and real.extremal_expectation == 1
    zero = replace(
        real,
        extremal_distribution=p,
        transfers=(),
        extremal_expectation=Q(1, 2),
        moved_mass=Q(0),
        saturation_radius=Q(0),
        full_range_tight_radius=Q(0),
    )
    assert not zero.valid

    p3, v3 = (Q(1, 3),) * 3, (Q(0), Q(1, 2), Q(1))
    real3 = maximize_expectation_tv_ball(p3, v3, Q(1, 3))
    wrong_donor = replace(
        real3,
        extremal_distribution=(Q(1, 3), Q(0), Q(2, 3)),
        transfers=(TVTransfer(1, 2, Q(1, 3), Q(1, 2), Q(1)),),
        extremal_expectation=Q(2, 3),
        full_range_tight_radius=Q(0),
    )
    assert real3.valid and real3.extremal_expectation == Q(5, 6)
    assert not wrong_donor.valid

    real4 = maximize_expectation_tv_ball(p3, v3, Q(1, 2))
    honest_scalars = replace(
        real4,
        extremal_distribution=(Q(1, 6), Q(0), Q(5, 6)),
        transfers=(TVTransfer(0, 2, Q(1, 6), Q(0), Q(1)), TVTransfer(1, 2, Q(1, 3), Q(1, 2), Q(1))),
        extremal_expectation=Q(5, 6),
    )
    assert real4.extremal_expectation == Q(11, 12)
    assert not honest_scalars.valid


def test_tv_knapsack_dual_gains_are_bound_to_the_transport():
    from simtheory.distributionally_robust_codes import maximize_expectation_tv_ball
    from simtheory.tv_transport_duals import tv_knapsack_dual_certificate

    transport = maximize_expectation_tv_ball((Q(1, 3),) * 3, (Q(0), Q(1, 2), Q(1)), Q(1, 2))
    dual = tv_knapsack_dual_certificate(transport)
    assert dual.valid
    assert not replace(dual, gain_vector=tuple(g * 2 for g in dual.gain_vector)).valid


def test_tv_robust_code_suboptimal_candidate_fails():
    from simtheory.distributionally_robust_codes import (
        exact_tv_robust_prefix_code,
        maximize_expectation_tv_ball,
        minimize_expectation_tv_ball,
    )

    prior = (Q(7, 10), Q(1, 10), Q(1, 10), Q(1, 10))
    cert = exact_tv_robust_prefix_code(K4, prior, Q(1, 10))
    assert cert.valid and cert.robust_value == Q(17, 10)
    fixed = exact_tv_robust_prefix_code(K4, (Q(1, 4),) * 4, Q(0)).optimal_candidate
    values = tuple(Q(x) for x in fixed.state_lengths)
    bad = replace(
        fixed,
        nominal_expectation=sum(a * b for a, b in zip(prior, values)),
        worst_case=maximize_expectation_tv_ball(prior, values, Q(1, 10)),
        best_case=minimize_expectation_tv_ball(prior, values, Q(1, 10)),
    )
    assert bad.valid
    assert not replace(cert, optimal_candidate=bad, nominal_optimum=Q(0)).valid


# ------------------------------------------------------- confidence radii


def test_zero_confidence_radii_fail():
    from simtheory.bayesian_boolean_prior_robustness import value_interval
    from simtheory.independent_latent_prior_confidence import (
        DataCalibratedBayesianValueBand,
        independent_latent_tv_confidence_radius,
    )
    from simtheory.statistical_prior_uncertainty import weissman_tv_confidence_radius

    real = independent_latent_tv_confidence_radius((3, 7))
    assert real.valid and real.radius == Q(707107, 1000000)
    forged = replace(real, radius=Q(0), clipped_at_one=True)
    assert not forged.valid
    band = DataCalibratedBayesianValueBand(forged, Q(1, 2), value_interval(Q(1, 2), Q(0)))
    assert not band.valid

    weissman = weissman_tv_confidence_radius((3, 7))
    assert weissman.valid and weissman.radius == Q(42947, 100000)
    assert not replace(weissman, radius=Q(0)).valid


# ------------------------------------------------------- chromatic numbers


def test_forged_chromatic_lower_bound_and_monotonicity_fail():
    path = ConfusionGraph.from_edges((0, 1, 2), ((0, 1), (1, 2)))
    real = exact_chromatic_certificate(path)
    assert real.valid and real.chromatic_number == 2
    forged = ChromaticCertificate(path, (0, 1, 2), 3, (0, 1, 2), (0,), 3, 1, 3, ())
    assert not forged.valid
    assert not ConfusionMonotonicityCertificate(K3, K3, "identity", 3, 1).valid
    assert ConfusionMonotonicityCertificate(K3, K3, "identity", 3, 3).valid


# ------------------------------------------- shared-randomness enumeration


def test_dropped_robust_candidate_fails():
    from simtheory.robust_prior_codes import k3_shared_randomness_example

    real = k3_shared_randomness_example()
    assert real.valid and real.mixed_minimax.value == Q(31, 20)
    enumeration = real.enumeration
    for drop in range(len(enumeration.candidates)):
        kept = tuple(c for i, c in enumerate(enumeration.candidates) if i != drop)
        forged = replace(enumeration, candidates=kept, dominated_count=enumeration.dominated_count + 1)
        assert not forged.valid


# ------------------------------------------------------- dynamic games


def test_swapped_enumeration_and_best_case_path_forgeries_fail():
    from simtheory.adaptive_drift_games import (
        exact_feedback_dynamic_code,
        exact_open_loop_dynamic_code,
        finite_law_transition_model,
    )

    model = finite_law_transition_model(POINT_LAWS, ((0, 1, 2),) * 3)
    real = exact_feedback_dynamic_code(K3, model, 0, 2)
    assert real.valid and real.initial_value == 2
    swapped = replace(exact_feedback_dynamic_code(E3, model, 0, 2), graph=K3)
    assert not swapped.valid

    open_loop = exact_open_loop_dynamic_code(K3, model, 0, 2)
    assert open_loop.valid and open_loop.selected_value == 3
    forged = replace(
        open_loop,
        selected_value=Q(2),
        sequence_values=(Q(2),) * open_loop.sequences_examined,
    )
    assert not forged.valid


def test_swapped_enumeration_bayesian_and_static_drift_fail():
    from simtheory.drifting_priors import exact_static_drift_robust_prefix_code
    from simtheory.stochastic_observation_beliefs import (
        bayesian_law_model,
        exact_bayesian_coding_game,
        full_information_kernel,
    )

    model = bayesian_law_model(POINT_LAWS, POINT_LAWS)
    kernel = full_information_kernel(3)
    real = exact_bayesian_coding_game(K3, model, kernel, (Q(1, 3),) * 3, 2)
    assert real.valid and real.initial_value == 2
    forged = replace(exact_bayesian_coding_game(E3, model, kernel, (Q(1, 3),) * 3, 2), graph=K3)
    assert not forged.valid

    static = exact_static_drift_robust_prefix_code(K3, (Q(1, 3),) * 3, Q(1, 6), 2)
    assert static.valid and static.robust_cumulative_value == Q(23, 6)
    swapped = replace(exact_static_drift_robust_prefix_code(E3, (Q(1, 3),) * 3, Q(1, 6), 2), graph=K3)
    assert not swapped.valid


def test_coarsened_benign_path_forgery_fails():
    import simtheory.coarsened_observation_games as cog
    from simtheory.adaptive_drift_games import finite_law_transition_model

    model = finite_law_transition_model(POINT_LAWS, ((0, 1, 2),) * 3)
    real = cog.exact_coarsened_observation_game(K3, model, cog.no_observation_partition(3), (0, 1, 2), 1)
    assert real.valid and real.initial_value == 2
    costs = real.entry_cost_path[0]
    record = [r for r in real.frontiers if r.period == 0][0]
    cheapest = min(range(len(costs)), key=lambda i: costs[i])
    forged = replace(
        real,
        adversarial_path=(record.states[cheapest],),
        initial_value=min(costs),
        initial_choices=tuple(replace(choice, value=min(costs)) for choice in real.initial_choices),
    )
    assert not forged.valid


def test_fixed_model_and_active_regret_forgeries_fail():
    from simtheory.active_fixed_model_experiments import active_experiment
    from simtheory.active_fixed_model_regret import exact_active_fixed_model_minimax_regret
    from simtheory.fixed_model_ambiguity import (
        exact_fixed_model_ambiguity_game,
        fixed_model_family,
        fixed_model_scenario,
    )
    from simtheory.stochastic_observation_beliefs import bayesian_law_model, no_information_kernel, observation_kernel

    scenarios = tuple(
        fixed_model_scenario(
            f"m{s}",
            bayesian_law_model((tuple(Q(int(i == s)) for i in range(3)),), ((1,),)),
            no_information_kernel(1),
            (1,),
        )
        for s in range(3)
    )
    family = fixed_model_family(scenarios)
    cert = exact_fixed_model_ambiguity_game(K3, family, 3)
    assert cert.valid and cert.fixed_model_value == 5
    entry = replace(cert.initial_entries[0], costs=(Q(0),) * len(cert.initial_entries[0].costs))
    forged = replace(cert, initial_entries=(entry,), selected_initial_costs=entry.costs, fixed_model_value=Q(0))
    assert not forged.valid

    no_signal = active_experiment("none", tuple(observation_kernel(((1,),)) for _ in scenarios))
    regret = exact_active_fixed_model_minimax_regret(K3, family, (no_signal,), 1)
    assert regret.valid and regret.minimax_regret == 1
    zero_oracles = replace(
        regret,
        oracles=tuple(replace(o, value=Q(0)) for o in regret.oracles),
        selected_regrets=regret.selected_costs,
        minimax_regret=max(regret.selected_costs),
        robust_cost_regrets=regret.base.selected_costs,
        regret_of_robust_cost_policy=max(regret.base.selected_costs),
    )
    assert not zero_oracles.valid
    raised = replace(regret, oracles=tuple(replace(o, value=Q(10)) for o in regret.oracles))
    assert raised.valid is False  # returns False instead of raising


# ------------------------------------------------- drift polytopes and grids


def test_drift_path_polytope_and_coupled_cost_forgeries_fail():
    from simtheory.coupled_drift_sequences import PathHalfspace, _objective_affine, _path_cost, exact_coupled_drift_cost

    costs = ((Q(0), Q(1)), (Q(0), Q(1)))
    real = exact_coupled_drift_cost((Q(1, 2), Q(1, 2)), costs, Q(1, 4))
    assert real.valid and real.optimum == Q(7, 4)
    kept = tuple(v for v in real.polytope.vertices if _path_cost(v.path, costs) < real.optimum)
    forged_opt = max(_path_cost(v.path, costs) for v in kept)
    constant, objective = _objective_affine(costs)
    polytope = replace(
        real.polytope,
        vertices=kept,
        constraints=real.polytope.constraints + (PathHalfspace(objective, forged_opt - constant, "spurious"),),
    )
    assert not polytope.valid
    index = [_path_cost(v.path, costs) for v in kept].index(forged_opt)
    multipliers = (Q(0),) * len(real.polytope.constraints) + (Q(1),)
    forged = replace(
        real,
        polytope=polytope,
        optimum=forged_opt,
        maximizing_path=kept[index].path,
        maximizing_vertex_index=index,
        vertex_values=tuple(_path_cost(v.path, costs) for v in kept),
        dual_multipliers=multipliers,
        dual_value=forged_opt,
        dual_support=(len(multipliers) - 1,),
    )
    assert not forged.valid


def test_pathwise_regret_dropped_vertices_and_comparators_fail():
    import simtheory.pathwise_regret as pr

    a = pr.affine_path_decision("A", ((0, 1), (0, 1)))
    b = pr.affine_path_decision("B", ((1, 0), (1, 0)))
    real = pr.exact_pathwise_regret_game((Q(1, 2), Q(1, 2)), Q(1, 4), (a, b))
    assert real.valid and real.deterministic_value == Q(3, 2) and real.shared_value == Q(3, 4)
    truncated = replace(real.polytope, vertices=real.polytope.vertices[:1])
    assert not truncated.valid
    assert not replace(real, polytope=truncated).valid

    sequence = pr.exact_code_sequence_regret(
        K3, (Q(1, 3),) * 3, Q(1, 3), 2, decision_max_switches=0, comparator_max_switches=1
    )
    assert sequence.valid and len(sequence.comparator_sequences) == 9
    assert not replace(sequence, comparator_sequences=sequence.decision_sequences).valid


def test_trimmed_simplex_grid_fails():
    import simtheory.adaptive_drift_policies as adp

    grid = adp.exact_simplex_grid(3, 2, Q(1, 2))
    assert grid.valid
    trimmed = replace(grid, transitions=tuple((i,) for i in range(grid.law_count)))
    assert not trimmed.valid


def test_precommitted_sequence_inflated_static_costs_fail():
    from simtheory.coupled_drift_sequences import exact_precommitted_code_sequence

    real = exact_precommitted_code_sequence(K3, (Q(1, 3),) * 3, Q(1, 6), 2)
    assert real.valid and real.sequence_gain_over_static == Q(1, 6)
    count = len(real.enumeration.candidates)
    statics = {(i,) * 2 for i in range(count)}
    selected = real.sequences.index(real.selected_sequence)
    paths = tuple(
        c + (Q(10) if (s in statics and i != selected) else 0)
        for i, (s, c) in enumerate(zip(real.sequences, real.sequence_path_costs))
    )
    totals = tuple(c + real.switching_penalty * k for c, k in zip(paths, real.sequence_switch_counts))
    forged = replace(real, sequence_path_costs=paths, sequence_total_costs=totals)
    assert not forged.valid


# --------------------------------------------------- polyhedral and TV balls


def test_polyhedral_dropped_vertex_dual_and_farkas_forgeries_fail():
    from simtheory.polyhedral_duals import FarkasInfeasibilityCertificate, exact_expectation_primal_dual
    from simtheory.polyhedral_priors import (
        PolyhedralExpectationCertificate,
        extremal_expectation,
        interval_prior_polytope,
    )

    polytope = interval_prior_polytope((Q(0),) * 3, (Q(1, 2),) * 3)
    values = (Q(0), Q(1), Q(2))
    real = extremal_expectation(polytope, values)
    assert real.valid and real.optimum == Q(3, 2)
    keep = tuple(v for v in polytope.vertices if sum(a * b for a, b in zip(v.distribution, values)) < real.optimum)
    dropped = replace(polytope, vertices=keep)
    assert not dropped.valid
    forged = PolyhedralExpectationCertificate(
        dropped, values, True, Q(1), keep[-1].distribution,
        tuple(sum(a * b for a, b in zip(v.distribution, values)) for v in keep),
    )
    assert not forged.valid

    dual = exact_expectation_primal_dual(polytope, values)
    assert dual.valid
    zero_objective = replace(
        dual,
        transformed_objective=(Q(0), Q(0)),
        transpose_product=(Q(0), Q(0)),
        multipliers=(Q(0),) * len(dual.multipliers),
        support=(),
        transformed_constant=Q(1),
        transformed_dual_value=Q(1),
        original_dual_value=Q(1),
    )
    assert not zero_objective.valid

    assert not replace(polytope, vertices=()).valid
    emptied = replace(
        polytope,
        vertices=(),
        transformed_constraints=polytope.transformed_constraints + (((Q(0), Q(0)), Q(-1), "fake"),),
    )
    weights = (Q(0),) * len(polytope.transformed_constraints) + (Q(1),)
    farkas = FarkasInfeasibilityCertificate(emptied, weights, (Q(0), Q(0)), Q(-1), Q(1), (len(weights) - 1,), 1, 1, 1)
    assert not farkas.valid


def test_polyhedral_robust_code_zero_costs_fail():
    from simtheory.polyhedral_priors import exact_polyhedral_robust_prefix_code, interval_prior_polytope
    from simtheory.robust_prior_codes import solve_exact_zero_sum_game

    polytope = interval_prior_polytope((Q(1, 5),) * 3, (Q(3, 5),) * 3)
    real = exact_polyhedral_robust_prefix_code(K3, polytope)
    assert real.valid and real.deterministic_value == Q(9, 5)
    zero = tuple(replace(c, scenario_costs=(Q(0),) * len(c.scenario_costs)) for c in real.enumeration.candidates[:1])
    forged = replace(
        real,
        enumeration=replace(real.enumeration, candidates=zero),
        deterministic_candidate=zero[0],
        deterministic_value=Q(0),
        oracle_costs=(Q(0),) * len(polytope.vertices),
        game=solve_exact_zero_sum_game(tuple((Q(0),) for _ in polytope.vertices)),
        shared_value=Q(0),
    )
    assert not forged.valid


def test_truncated_tv_ball_vertex_list_fails():
    from simtheory.shared_tv_robust_codes import enumerate_tv_ball_vertices

    ball = enumerate_tv_ball_vertices((Q(1, 3),) * 3, Q(1, 6))
    assert ball.valid and len(ball.vertices) == 6
    assert not replace(ball, vertices=ball.vertices[:1]).valid


# --------------------------------------------------------- network coding


def test_network_coding_empty_decoders_and_unexhausted_search_fail():
    from simtheory.network_coding import LinearCodeSearchResult, butterfly_separation_certificate

    real = butterfly_separation_certificate()
    assert real.valid
    assert not replace(real.linear_certificate, decoders=()).valid
    decoder = real.linear_certificate.decoders[0]
    forged_decoder = replace(decoder, rank=decoder.rank - 1)
    assert not replace(real.linear_certificate, decoders=(forged_decoder,) + real.linear_certificate.decoders[1:]).valid
    assert not replace(real, exhaustive_routing_result=LinearCodeSearchResult(None, 0, 0, True)).valid


def test_functional_code_empty_decoders_fail():
    from simtheory.functional_networks import side_information_broadcast_separation

    real = side_information_broadcast_separation()
    assert real.valid
    code = real.side_information_linear_code
    assert code.valid
    assert not replace(code, sink_decoders=()).valid


# ------------------------------------------------------------ prefix codes


def test_non_huffman_code_and_forged_entropy_fail():
    from simtheory.prior_weighted_codes import PrefixCodeCertificate, exact_prior_weighted_prefix_code

    probabilities = (Q(1, 2), Q(1, 4), Q(1, 4))
    words = ("00", "01", "1")
    expected = sum(a * len(b) for a, b in zip(probabilities, words))
    assert expected == Q(7, 4)
    assert not PrefixCodeCertificate(probabilities, words, (2, 2, 1), expected, expected, Q(1)).valid

    real = exact_prior_weighted_prefix_code(K3, probabilities)
    assert real.valid and real.minimum_coloring_entropy_bits == 1.5
    assert not replace(real, minimum_coloring_entropy_bits=0.6).valid


# -------------------------------------------------------- observation value


def test_blackwell_values_are_bound_to_their_channels():
    from simtheory.observation_channel_value import (
        RationalObservationChannel,
        exact_blackwell_comparison,
        exact_observation_channel_value,
    )

    perfect = RationalObservationChannel(((Q(1), Q(0)), (Q(0), Q(1))))
    no_info = RationalObservationChannel(((Q(1),), (Q(1),)))
    scenarios = ((Q(1), Q(0), Q(0)), (Q(0), Q(1), Q(0)))
    real = exact_blackwell_comparison(K3, scenarios, no_info, ((Q(1),),))
    assert real.valid and real.informative_value.shared_observation_value == Q(3, 2)
    perfect_value = exact_observation_channel_value(K3, scenarios, perfect)
    assert not replace(real, informative_value=perfect_value, garbled_value=perfect_value).valid


# --------------------------------------------------------- Boolean queries


def test_boolean_query_values_are_recomputed():
    from simtheory.bayesian_adaptive_boolean_queries import exact_adaptive_boolean_query_design
    from simtheory.bayesian_boolean_experiments import exact_bayesian_boolean_geometry
    from simtheory.bayesian_cost_sensitive_queries import exact_cost_sensitive_boolean_query_design

    adaptive = exact_adaptive_boolean_query_design((0, 1, 1, 0), 1)
    assert adaptive.valid and adaptive.adaptive_value == Q(1, 2)
    forged = replace(
        adaptive,
        adaptive_value=Q(0),
        adaptivity_gain=adaptive.nonadaptive_value,
        nodes=(replace(adaptive.nodes[0], value=Q(0)),) + adaptive.nodes[1:],
    )
    assert not forged.valid

    cost = exact_cost_sensitive_boolean_query_design((0, 1, 1, 0), (Q(1, 10), Q(1, 10)), 2)
    assert cost.valid
    assert not replace(cost, value=Q(0), nodes=(replace(cost.nodes[0], value=Q(0)),) + cost.nodes[1:]).valid

    geometry = exact_bayesian_boolean_geometry((0, 1, 1, 0))
    assert geometry.valid
    values = tuple((subset, Q(0)) for subset, _ in geometry.subset_values)
    mobius = tuple((subset, Q(0)) for subset, _ in geometry.mobius)
    assert not replace(geometry, subset_values=values, mobius=mobius).valid


# --------------------------------------------------------------- real data


def test_self_referential_real_data_receipts_are_rejected(tmp_path):
    from simtheory.real_data import (
        DELFT_SUMMARY_PATH,
        BellTrial,
        load_beacon_summary,
        load_delft_summary,
        trial_digest,
    )

    payload = json.loads(DELFT_SUMMARY_PATH.read_text(encoding="utf-8"))
    rows = [list(row) for row in payload["trials"]]
    flips = 0
    for row in rows:
        trial = BellTrial(*row)
        if flips < 30 and not trial.chsh_win:
            row[4] = -row[4]
            flips += 1
    payload["trials"] = rows
    payload["trials_sha256"] = trial_digest([BellTrial(*row) for row in rows])
    forged = tmp_path / "delft.json"
    forged.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="pinned"):
        load_delft_summary(forged)
    load_delft_summary()  # the committed file still passes

    zero, ones = "00" * 64, "11" * 64
    values = [zero, zero, ones]
    pulses = []
    for index, value in enumerate(values):
        later = values[index + 1] if index + 1 < len(values) else zero
        pulses.append(
            {
                "pulseIndex": 1 + index,
                "timeStamp": "x",
                "localRandomValue": value,
                "precommitmentValue": hashlib.sha512(bytes.fromhex(later)).hexdigest().upper(),
            }
        )
    fabricated = tmp_path / "beacon.json"
    fabricated.write_text(
        json.dumps({"schema": "simulation-theory.real-data.nist-beacon/v1", "pulses": pulses}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="pinned"):
        load_beacon_summary(fabricated)
    load_beacon_summary()


def test_evidence_paths_must_stay_inside_the_repository(tmp_path):
    from simtheory.claims import validate_local_evidence_paths

    manifest = {
        "schema": "simulation-theory.claims/v1",
        "claims": [
            {
                "id": "ST-X0",
                "title": "t",
                "kind": "THEOREM",
                "scope": "s",
                "assumptions": [],
                "evidence": ["/etc/hosts"],
                "nonclaims": ["n"],
            }
        ],
    }
    with pytest.raises(ValueError, match="escapes"):
        validate_local_evidence_paths(manifest, tmp_path)
    manifest["claims"][0]["evidence"] = ["../outside.txt"]
    (tmp_path.parent / "outside.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        validate_local_evidence_paths(manifest, tmp_path)
