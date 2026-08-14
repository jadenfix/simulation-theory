from fractions import Fraction
from itertools import product
from random import Random

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.distributionally_robust_codes import (
    exact_tv_robust_prefix_code,
    maximize_expectation_tv_ball,
)
from simtheory.shared_tv_robust_codes import (
    enumerate_tv_ball_vertices,
    exact_shared_tv_robust_prefix_code,
    full_tv_k3_shared_randomness_example,
    tv_ball_event_inequalities,
)


def _compositions(total, count):
    if count == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, count - 1):
            yield (first, *rest)


def _graph_from_edge_mask(vertex_count, edge_mask):
    edges = []
    bit = 0
    for left in range(vertex_count):
        for right in range(left + 1, vertex_count):
            if (edge_mask >> bit) & 1:
                edges.append((left, right))
            bit += 1
    return ConfusionGraph.from_edges(tuple(range(vertex_count)), tuple(edges))


def test_tv_ball_vertex_endpoints_are_nominal_and_simplex_vertices():
    nominal = (Fraction(3, 5), Fraction(3, 10), Fraction(1, 10))
    zero = enumerate_tv_ball_vertices(nominal, 0)
    full = enumerate_tv_ball_vertices(nominal, 1)
    assert zero.valid and full.valid
    assert zero.vertex_distributions == (nominal,)
    assert set(full.vertex_distributions) == {
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
    }
    assert len(tv_ball_event_inequalities(nominal, Fraction(1, 5))) == 9


def test_vertex_maximum_matches_transport_on_seeded_three_state_instances():
    rng = Random(271828)
    denominator = 10
    compositions = tuple(_compositions(denominator, 3))
    for _ in range(80):
        counts = rng.choice(compositions)
        nominal = tuple(Fraction(count, denominator) for count in counts)
        radius = Fraction(rng.randrange(denominator + 1), denominator)
        values = tuple(Fraction(rng.randrange(-4, 7)) for _ in range(3))
        vertices = enumerate_tv_ball_vertices(nominal, radius)
        vertex_max = max(
            sum(probability * value for probability, value in zip(vertex, values))
            for vertex in vertices.vertex_distributions
        )
        transport = maximize_expectation_tv_ball(nominal, values, radius)
        assert vertex_max == transport.extremal_expectation


def test_full_tv_k3_shared_randomness_strictly_beats_deterministic_mean():
    certificate = full_tv_k3_shared_randomness_example()
    assert certificate.valid
    assert certificate.deterministic_value == 2
    assert certificate.mixed_value == Fraction(5, 3)
    assert certificate.randomization_gain == Fraction(1, 3)
    assert certificate.mixed_state_lengths == (
        Fraction(5, 3),
        Fraction(5, 3),
        Fraction(5, 3),
    )
    assert certificate.mixed_game.code_mixture == (
        Fraction(1, 3),
        Fraction(1, 3),
        Fraction(1, 3),
    )
    assert certificate.least_favorable_prior == (
        Fraction(1, 3),
        Fraction(1, 3),
        Fraction(1, 3),
    )
    assert certificate.least_favorable_oracle_value == Fraction(5, 3)
    assert certificate.selected_mixture_seed_observing_cost == 2
    assert certificate.optimal_seed_observing_value == 2
    assert len(certificate.code_support) == 3


def test_skew_k3_has_exact_shared_randomness_radius_phase_change():
    graph = ConfusionGraph.from_edges(
        (0, 1, 2),
        ((0, 1), (0, 2), (1, 2)),
    )
    nominal = (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10))

    before = exact_shared_tv_robust_prefix_code(
        graph,
        nominal,
        Fraction(2, 5),
    )
    threshold = exact_shared_tv_robust_prefix_code(
        graph,
        nominal,
        Fraction(7, 15),
    )
    after = exact_shared_tv_robust_prefix_code(
        graph,
        nominal,
        Fraction(1, 2),
    )

    assert before.valid and threshold.valid and after.valid
    assert before.mixed_value == Fraction(8, 5)
    assert before.mixed_value == before.deterministic_value
    assert len(before.code_support) == 1

    assert threshold.mixed_value == Fraction(5, 3)
    # The game solver's deterministic-support tie-break retains one code at the
    # exact crossing even though the uniform mixture has the same value.
    assert len(threshold.code_support) == 1

    assert after.mixed_value == Fraction(5, 3)
    assert after.deterministic_value == Fraction(17, 10)
    assert after.randomization_gain == Fraction(1, 30)
    assert after.mixed_state_lengths == (
        Fraction(5, 3),
        Fraction(5, 3),
        Fraction(5, 3),
    )
    assert after.mixed_game.code_mixture == (
        Fraction(1, 3),
        Fraction(1, 3),
        Fraction(1, 3),
    )


def test_radius_zero_reduces_to_nominal_and_has_no_randomization_gain():
    graph = ConfusionGraph.from_edges(
        (0, 1, 2),
        ((0, 1), (1, 2)),
    )
    nominal = (Fraction(3, 5), Fraction(3, 10), Fraction(1, 10))
    certificate = exact_shared_tv_robust_prefix_code(graph, nominal, 0)
    deterministic = exact_tv_robust_prefix_code(graph, nominal, 0)
    assert certificate.valid
    assert certificate.mixed_value == deterministic.robust_value
    assert certificate.deterministic_value == deterministic.robust_value
    assert certificate.randomization_gain == 0
    assert certificate.least_favorable_prior == nominal


def test_all_labeled_three_vertex_graphs_have_continuous_replay_and_oracle_gap_zero():
    nominal = (Fraction(3, 5), Fraction(3, 10), Fraction(1, 10))
    radius = Fraction(1, 5)
    for edge_mask in range(1 << 3):
        graph = _graph_from_edge_mask(3, edge_mask)
        certificate = exact_shared_tv_robust_prefix_code(
            graph,
            nominal,
            radius,
            max_states=4,
            max_vertices=5,
            max_partitions=10_000,
            max_candidates=20_000,
            max_dominance_pairs=100_000,
            max_game_bases=500_000,
        )
        assert certificate.valid
        assert certificate.mixed_continuous_worst_case.extremal_expectation == certificate.mixed_value
        assert certificate.least_favorable_oracle_value == certificate.mixed_value
        assert certificate.mixed_value <= certificate.deterministic_value


def test_tv_vertex_enumeration_matches_denominator_grid_polytope():
    nominal_counts = (6, 3, 1)
    nominal = tuple(Fraction(count, 10) for count in nominal_counts)
    radius_counts = 2
    vertices = enumerate_tv_ball_vertices(nominal, Fraction(1, 5))
    grid = tuple(
        tuple(Fraction(count, 10) for count in counts)
        for counts in _compositions(10, 3)
        if sum(abs(left - right) for left, right in zip(counts, nominal_counts))
        <= 2 * radius_counts
    )
    # Every grid point must satisfy every exact event inequality, and each
    # linear objective attains its grid maximum no above the exact vertex max.
    inequalities = vertices.inequalities
    assert all(
        all(inequality.satisfied(point[:-1]) for inequality in inequalities)
        for point in grid
    )
    objectives = (
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(-2), Fraction(1), Fraction(4)),
        (Fraction(3), Fraction(-5), Fraction(2)),
    )
    for values in objectives:
        grid_max = max(
            sum(probability * value for probability, value in zip(point, values))
            for point in grid
        )
        vertex_max = max(
            sum(probability * value for probability, value in zip(point, values))
            for point in vertices.vertex_distributions
        )
        assert grid_max <= vertex_max


def test_adversary_timing_is_not_silently_interchanged():
    certificate = full_tv_k3_shared_randomness_example()
    assert certificate.mixed_value == Fraction(5, 3)
    # Oblivious source law: one distribution is selected independently of seed.
    # Seed-observing source law: a different worst state may be selected for each
    # realized tree, eliminating the expected-length gain.
    assert certificate.selected_mixture_seed_observing_cost == 2
    assert certificate.optimal_seed_observing_value == certificate.deterministic_value == 2


def test_vertex_and_game_caps_fail_closed():
    nominal = (Fraction(1, 4),) * 4
    with pytest.raises(ValueError):
        enumerate_tv_ball_vertices(nominal, Fraction(1, 5), max_states=3)
    with pytest.raises(ValueError):
        enumerate_tv_ball_vertices(nominal, Fraction(1, 5), max_bases=1)
    with pytest.raises(ValueError):
        enumerate_tv_ball_vertices((0.2, 0.3, 0.5), Fraction(1, 5))

    graph = ConfusionGraph.from_edges(
        (0, 1, 2),
        ((0, 1), (0, 2), (1, 2)),
    )
    with pytest.raises(ValueError):
        exact_shared_tv_robust_prefix_code(
            graph,
            (Fraction(1, 3),) * 3,
            Fraction(1),
            max_game_bases=1,
        )
