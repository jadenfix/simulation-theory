from functools import lru_cache
from math import isclose
from random import Random

import pytest

from simtheory.predictive_networks import CausalCapacityNetwork
from simtheory.stochastic_predictive import categorical_total_variation
from simtheory.ternary_predictive import (
    FiniteTernaryFamily,
    minimum_ternary_arbitrary_cover,
    target_centered_ternary_cover_size,
    ternary_cluster_is_coverable,
    ternary_common_center,
    ternary_cover_bounds,
    ternary_minimax_center,
    ternary_network_certificate,
    ternary_network_units_required,
    ternary_packing_size_lower_bound,
    ternary_total_variation,
)

VERTICES = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)


def _independent_partition_optimum(laws, epsilon):
    """Exact subset-DP checker independent of the set-cover implementation."""

    count = len(laws)
    full = (1 << count) - 1
    feasible = [False] * (1 << count)
    for mask in range(1, full + 1):
        feasible[mask] = ternary_cluster_is_coverable(
            tuple(laws[index] for index in range(count) if (mask >> index) & 1),
            epsilon,
        )

    @lru_cache(maxsize=None)
    def solve(mask):
        if mask == 0:
            return 0
        first = mask & -mask
        best = count
        subset = mask
        while subset:
            if subset & first and feasible[subset]:
                best = min(best, 1 + solve(mask ^ subset))
            subset = (subset - 1) & mask
        return best

    return solve(full)


def _random_simplex_law(rng, denominator=12):
    first = rng.randrange(denominator + 1)
    second = rng.randrange(denominator - first + 1)
    third = denominator - first - second
    return (
        first / denominator,
        second / denominator,
        third / denominator,
    )


def test_ternary_tv_is_max_coordinate_difference():
    examples = (
        ((1, 0, 0), (0, 1, 0)),
        ((0.2, 0.3, 0.5), (0.4, 0.1, 0.5)),
        ((0.1, 0.8, 0.1), (0.2, 0.2, 0.6)),
        ((1 / 3, 1 / 3, 1 / 3), (0.0, 0.5, 0.5)),
    )
    for left, right in examples:
        expected = categorical_total_variation(left, right)
        assert isclose(ternary_total_variation(left, right), expected, abs_tol=1e-12)
        assert isclose(
            expected,
            max(abs(a - b) for a, b in zip(left, right)),
            abs_tol=1e-12,
        )


def test_common_center_feasibility_is_box_simplex_intersection():
    center = ternary_common_center(VERTICES, 2.0 / 3.0)
    assert center is not None
    assert all(isclose(value, 1.0 / 3.0, abs_tol=1e-12) for value in center)
    assert all(
        ternary_total_variation(vertex, center) <= 2.0 / 3.0 + 1e-12
        for vertex in VERTICES
    )
    assert ternary_common_center(VERTICES, 2.0 / 3.0 - 1e-8) is None

    bounds = ternary_cover_bounds(
        ((0.6, 0.3, 0.1), (0.5, 0.1, 0.4)),
        0.2,
    )
    assert bounds is not None
    lower, upper = bounds
    assert all(a <= b for a, b in zip(lower, upper))
    assert sum(lower) <= 1.0 <= sum(upper)


def test_closed_form_minimax_center_on_simplex_vertices():
    center, radius = ternary_minimax_center(VERTICES)
    assert isclose(radius, 2.0 / 3.0, abs_tol=1e-12)
    assert all(isclose(value, 1.0 / 3.0, abs_tol=1e-12) for value in center)

    edge_center, edge_radius = ternary_minimax_center(VERTICES[:2])
    assert isclose(edge_radius, 0.5, abs_tol=1e-12)
    assert all(
        isclose(value, expected, abs_tol=1e-12)
        for value, expected in zip(edge_center, (0.5, 0.5, 0.0))
    )

    point = (0.2, 0.3, 0.5)
    same_center, same_radius = ternary_minimax_center((point, point))
    assert same_center == point
    assert same_radius == 0.0


def test_exact_arbitrary_center_cover_beats_target_centering():
    family = FiniteTernaryFamily.from_probabilities(VERTICES, ("x", "y", "z"))
    cover = minimum_ternary_arbitrary_cover(family, 2.0 / 3.0)
    assert cover.state_count == 1
    assert cover.predictive_bits == 0
    assert all(record in cover.assignment for record in family.records)
    assert target_centered_ternary_cover_size(family, 2.0 / 3.0) == 3
    assert ternary_packing_size_lower_bound(family, 2.0 / 3.0) == 1


def test_ternary_cover_phase_changes_at_half_and_two_thirds():
    family = FiniteTernaryFamily.from_probabilities(VERTICES)
    assert minimum_ternary_arbitrary_cover(family, 0.49).state_count == 3
    assert minimum_ternary_arbitrary_cover(family, 0.5).state_count == 2
    assert minimum_ternary_arbitrary_cover(family, 2.0 / 3.0).state_count == 1


def test_exact_cover_matches_independent_subset_partition_dp():
    rng = Random(6117)
    tolerances = (0.0, 0.08, 0.15, 0.25, 0.4)
    for count in range(1, 8):
        for _ in range(20):
            laws = tuple(_random_simplex_law(rng) for _ in range(count))
            epsilon = rng.choice(tolerances)
            family = FiniteTernaryFamily.from_probabilities(laws)
            certificate = minimum_ternary_arbitrary_cover(
                family,
                epsilon,
                max_records=8,
            )
            assert certificate.state_count == _independent_partition_optimum(
                laws,
                epsilon,
            )
            for record, law in zip(family.records, family.laws):
                center = certificate.centers[certificate.assignment[record]]
                assert ternary_total_variation(law, center) <= epsilon + 1e-12


def test_stochastic_embedding_and_exact_classes():
    family = FiniteTernaryFamily.from_probabilities(
        ((0.2, 0.3, 0.5), (0.2, 0.3, 0.5), (0.7, 0.2, 0.1)),
        ("a", "b", "c"),
    )
    stochastic = family.to_stochastic_family()
    assert stochastic.exact_class_count == 2
    assert stochastic.exact_predictive_bits == 1
    assert stochastic.conditional_laws[0][0] == family.laws[0]


def test_exact_ternary_network_capacity_and_routing():
    family = FiniteTernaryFamily.from_probabilities(VERTICES)
    disconnected = CausalCapacityNetwork(("s", "t"), ())
    one_bit = CausalCapacityNetwork(("s", "t"), (("s", "t", 1),))
    two_bits = CausalCapacityNetwork(("s", "t"), (("s", "t", 2),))

    assert ternary_network_units_required(family, 2.0 / 3.0) == 0
    zero_certificate = ternary_network_certificate(
        disconnected,
        "s",
        "t",
        family,
        2.0 / 3.0,
    )
    assert zero_certificate.feasible
    assert zero_certificate.required_units == 0
    assert zero_certificate.routed_units == 0

    assert ternary_network_units_required(family, 0.5) == 1
    one_certificate = ternary_network_certificate(
        one_bit,
        "s",
        "t",
        family,
        0.5,
    )
    assert one_certificate.feasible
    assert one_certificate.routed_units == 1

    assert ternary_network_units_required(family, 0.49) == 2
    assert not ternary_network_certificate(
        one_bit,
        "s",
        "t",
        family,
        0.49,
    ).feasible
    assert ternary_network_certificate(
        two_bits,
        "s",
        "t",
        family,
        0.49,
    ).feasible


def test_declared_two_bit_capacity_multiplier():
    family = FiniteTernaryFamily.from_probabilities(VERTICES)
    assert ternary_network_units_required(
        family,
        0.49,
        capacity_bits_per_unit=2,
    ) == 1
    one_unit = CausalCapacityNetwork(("s", "t"), (("s", "t", 1),))
    certificate = ternary_network_certificate(
        one_unit,
        "s",
        "t",
        family,
        0.49,
        capacity_bits_per_unit=2,
    )
    assert certificate.feasible
    assert certificate.routed_units == 1


def test_validation_boundaries():
    with pytest.raises(ValueError):
        FiniteTernaryFamily.from_probabilities(())
    with pytest.raises(ValueError):
        FiniteTernaryFamily.from_probabilities(((0.5, 0.5),))
    with pytest.raises(ValueError):
        FiniteTernaryFamily.from_probabilities(((0.5, 0.5, 0.5),))
    with pytest.raises(ValueError):
        ternary_common_center(VERTICES, -0.1)
    with pytest.raises(ValueError):
        minimum_ternary_arbitrary_cover(
            FiniteTernaryFamily.from_probabilities(VERTICES * 5),
            0.2,
            max_records=14,
        )
