"""Tests for the random-bit price of shared codebook randomness (ST-T310 to ST-T313, ST-M90 to ST-M93, ST-F61)."""

from __future__ import annotations

import math
from fractions import Fraction
from pathlib import Path
from random import Random

import pytest

from simtheory import random_bit_price
from simtheory.random_bit_price import (
    EXPECTED_VALUES,
    INSTANCES,
    K3,
    common_denominator,
    ddg_undecided,
    entropy_bits,
    grid_value,
    in_ring,
    k3_grid_value_fast,
    ky_expected_bits,
    largest_remainder_round,
    nu_partial,
    optimal_set_vertices,
    payoff,
    polytope_meets_ring,
    rounding_gap_bound,
    sampler_lower_bound_tail,
    solve_game,
)

F = Fraction
THIRD = (F(1, 3), F(1, 3), F(1, 3))


def test_k3_game_has_unique_nondyadic_optimum():
    value, mixture = solve_game(K3)
    assert value == F(5, 3)
    assert mixture == THIRD
    assert optimal_set_vertices(K3, value) == [THIRD]
    assert not polytope_meets_ring([THIRD], 2)


def test_k3_b_bit_value_curve_is_exact():
    for b in range(11):
        n = 2 ** b
        value = k3_grid_value_fast(n)
        assert value == 2 - F(n // 3, n)
        assert value - F(5, 3) == F(n % 3, 3 * n)
        assert value == F(5, 3) + F(1, 3 * 4 ** (b // 2))
        if b <= 6:
            assert grid_value(K3, n)[0] == value
    assert [k3_grid_value_fast(2 ** b) for b in range(7)] == [
        F(2), F(2), F(7, 4), F(7, 4), F(27, 16), F(27, 16), F(107, 64)
    ]


def test_k3_odd_bits_are_worthless_and_even_bits_pay_one_over_four_to_the_k():
    for k in range(1, 6):
        assert k3_grid_value_fast(2 ** (2 * k)) == k3_grid_value_fast(2 ** (2 * k + 1))
        drop = k3_grid_value_fast(2 ** (2 * k - 1)) - k3_grid_value_fast(2 ** (2 * k))
        assert drop == F(1, 4 ** k)


def test_skew_half_radius_curve_is_one_tenth_of_k3_curve():
    matrix = INSTANCES["ST-M27 radius 1/2"]
    assert solve_game(matrix) == (F(5, 3), THIRD)
    assert optimal_set_vertices(matrix, F(5, 3)) == [THIRD]
    for b in range(9):
        n = 2 ** b
        assert grid_value(matrix, n)[0] - F(5, 3) == F(n % 3, 30 * n)


@pytest.mark.parametrize("name", sorted(INSTANCES))
def test_dyadic_dichotomy_and_two_sided_gap_on_committed_instances(name):
    matrix = INSTANCES[name]
    value, mixture = solve_game(matrix)
    assert value == EXPECTED_VALUES[name]
    dyadic = polytope_meets_ring(optimal_set_vertices(matrix, value), 2)
    lower_denominator = common_denominator(matrix) * value.denominator
    exact = []
    previous = None
    for b in range(9):
        n = 2 ** b
        grid, _ = grid_value(matrix, n)
        gap = grid - value
        assert gap >= 0
        if previous is not None:
            assert grid <= previous
        previous = grid
        if gap == 0:
            exact.append(b)
        else:
            assert gap >= F(1, lower_denominator * n)
        assert gap <= rounding_gap_bound(matrix, mixture, n)
        rounded = largest_remainder_round(mixture, n)
        assert payoff(matrix, rounded) - value <= rounding_gap_bound(matrix, mixture, n)
    assert bool(exact) == dyadic
    if exact:
        assert exact == list(range(exact[0], 9))


def test_two_sided_gap_on_seeded_random_integer_games():
    rng = Random(17)
    for _ in range(80):
        rows, columns = rng.randint(2, 4), rng.randint(2, 3)
        matrix = tuple(
            tuple(F(rng.randint(0, 5)) for _ in range(columns))
            for _ in range(rows)
        )
        value, mixture = solve_game(matrix)
        dyadic = polytope_meets_ring(optimal_set_vertices(matrix, value), 2)
        hit = False
        for b in range(6):
            n = 2 ** b
            gap = grid_value(matrix, n)[0] - value
            hit = hit or gap == 0
            if gap:
                assert gap >= F(1, common_denominator(matrix) * value.denominator * n)
            assert gap <= rounding_gap_bound(matrix, mixture, n)
        if not dyadic:
            assert not hit


def test_ring_membership_decision_uses_affine_hull_not_vertices():
    # Segment between two non-dyadic vertices that contains the dyadic 1/2.
    assert polytope_meets_ring([(F(1, 3), F(2, 3)), (F(2, 3), F(1, 3))], 2)
    # Segment on the line w_0 = 1/3 contains no dyadic point.
    assert not polytope_meets_ring(
        [(F(1, 3), F(0), F(2, 3)), (F(1, 3), F(2, 3), F(0))], 2
    )
    # Ternary coins do realize thirds.
    assert polytope_meets_ring([THIRD], 3)
    assert polytope_meets_ring([THIRD], 6)
    assert not polytope_meets_ring([THIRD], 10)


def test_knuth_yao_k3_costs_exactly_eight_thirds_bits():
    assert ky_expected_bits(THIRD) == F(8, 3)
    undecided = ddg_undecided(THIRD, 30)
    for t, count in enumerate(undecided):
        assert F(count, 2 ** t) == F(2 ** t % 3, 2 ** t)
        assert F(count, 2 ** t) == sampler_lower_bound_tail(THIRD, t)
    entropy = math.log2(3)
    assert entropy <= float(F(8, 3)) < entropy + 2


def test_knuth_yao_closed_form_matches_digit_series_and_ddg_tail():
    rng = Random(5)
    depth = 60
    for _ in range(60):
        parts = rng.randint(2, 5)
        denominator = rng.randint(2, 30)
        cuts = sorted(rng.randint(0, denominator) for _ in range(parts - 1))
        weights = tuple(
            F(right - left, denominator)
            for left, right in zip([0] + cuts, cuts + [denominator])
        )
        expected = ky_expected_bits(weights)
        digits = sum((nu_partial(x, depth) for x in weights), F(0))
        assert digits <= expected <= digits + parts * F(depth + 2, 2 ** depth)
        undecided = ddg_undecided(weights, depth)
        tail = sum((F(u, 2 ** t) for t, u in enumerate(undecided)), F(0))
        assert tail <= expected <= tail + F(parts, 2 ** depth)
        assert entropy_bits(weights) - 1e-12 <= float(expected) < entropy_bits(weights) + 2
        all_dyadic = all(in_ring(x, 2) for x in weights)
        assert all_dyadic == (undecided[-1] == 0)


def test_one_lary_toss_attains_k3_value_iff_three_divides_l():
    for coin in range(1, 13):
        value = grid_value(K3, coin)[0]
        assert value == 2 - F(coin // 3, coin)
        assert (value == F(5, 3)) == (coin % 3 == 0)
    for coin in (2, 4, 5, 7):
        tosses = 1
        while coin ** tosses <= 500:
            assert k3_grid_value_fast(coin ** tosses) > F(5, 3)
            tosses += 1


def test_repository_instances_match_committed_certificates():
    from simtheory.confusion_graphs import ConfusionGraph
    from simtheory.robust_prior_codes import (
        k3_shared_randomness_example,
        k4_nonoracle_minimax_example,
    )
    from simtheory.shared_tv_robust_codes import (
        exact_shared_tv_robust_prefix_code,
        full_tv_k3_shared_randomness_example,
    )

    graph = ConfusionGraph.from_edges((0, 1, 2), ((0, 1), (0, 2), (1, 2)))
    games = {
        "ST-M21 minimax": k3_shared_randomness_example().mixed_minimax,
        "K4 nonoracle minimax": k4_nonoracle_minimax_example().mixed_minimax,
        "ST-M26 full-TV K3": full_tv_k3_shared_randomness_example().mixed_game,
        "ST-M27 radius 1/2": exact_shared_tv_robust_prefix_code(
            graph, (F(4, 5), F(1, 10), F(1, 10)), F(1, 2)
        ).mixed_game,
    }
    for name, game in games.items():
        assert game.valid
        assert tuple(tuple(row) for row in game.cost_matrix) == INSTANCES[name]
        assert game.value == EXPECTED_VALUES[name]


def test_ring_decision_requires_l_at_least_two_for_segments():
    segment = [(F(1, 3), F(2, 3)), (F(2, 3), F(1, 3))]
    with pytest.raises(ValueError):
        polytope_meets_ring(segment, 1)
    assert polytope_meets_ring([(F(1), F(0))], 1)
    assert not polytope_meets_ring([THIRD], 1)
    assert polytope_meets_ring(segment, 2)  # contains (1/2, 1/2)


@pytest.mark.slow
def test_receipt_matches_committed_receipt():
    root = Path(__file__).resolve().parents[1]
    committed = (root / "receipts" / "random-bit-price-shared-randomness.txt").read_text(encoding="utf-8")
    assert random_bit_price.receipt_text() == committed
