from fractions import Fraction
from itertools import combinations

from simtheory.finite_mixture_channel_identifiability import total_variation
from simtheory.finite_mixture_global_tv import exact_global_tv_modulus


def F(n, d=1):
    return Fraction(n, d)


def test_identity_k3_recovers_true_global_constant_and_beats_coordinate_bound():
    channel = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    result = exact_global_tv_modulus(channel)
    assert result.valid
    assert result.alpha == 1
    assert result.optimal_inverse_constant == 1
    assert result.affine.reconstruction is not None
    assert result.affine.reconstruction.tv_conditioning_constant == 2
    assert all(face.game.gap == 0 for face in result.face_certificates)


def test_binary_noisy_channel_matches_exact_row_tv_coefficient():
    channel = ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)))
    result = exact_global_tv_modulus(channel)
    assert result.valid
    assert result.alpha == total_variation(channel[0], channel[1]) == F(1, 2)
    assert result.optimal_inverse_constant == 2
    assert result.face_pair_count == 1


def test_pairwise_separation_can_miss_near_collision_between_convex_mixtures():
    epsilon = F(1, 10)
    channel = (
        (1, 0, 0),
        (0, 1, 0),
        (F(1, 2), F(1, 2) - epsilon, epsilon),
    )
    pairwise = min(total_variation(a, b) for a, b in combinations(channel, 2))
    result = exact_global_tv_modulus(channel)
    assert result.valid and result.affine.identifiable
    assert pairwise == F(1, 2)
    assert result.alpha == epsilon
    assert result.optimal_inverse_constant == 10
    best = result.face_certificates[result.minimizing_face_index]
    assert set(best.positive_indices) | set(best.negative_indices) == {0, 1, 2}
    assert sorted((len(best.positive_indices), len(best.negative_indices))) == [1, 2]


def test_exact_midpoint_is_zero_separation_and_nonidentifiable():
    channel = ((1, 0), (0, 1), (F(1, 2), F(1, 2)))
    result = exact_global_tv_modulus(channel)
    assert result.valid
    assert not result.affine.identifiable
    assert result.alpha == 0
    assert result.optimal_inverse_constant is None
    best = result.face_certificates[result.minimizing_face_index]
    assert best.separation == 0
    assert best.positive_observed_law == best.negative_observed_law


def test_alpha_scales_linearly_toward_affine_dependence():
    for denominator in (4, 5, 8, 10):
        epsilon = F(1, denominator)
        channel = (
            (1, 0, 0),
            (0, 1, 0),
            (F(1, 2), F(1, 2) - epsilon, epsilon),
        )
        result = exact_global_tv_modulus(channel)
        assert result.alpha == epsilon
        assert result.optimal_inverse_constant == denominator


def test_event_and_face_caps_fail_closed():
    channel = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    try:
        exact_global_tv_modulus(channel, max_events=5)
    except ValueError as exc:
        assert "event enumeration" in str(exc)
    else:
        raise AssertionError("expected event cap to fail closed")

    try:
        exact_global_tv_modulus(channel, max_face_pairs=1)
    except ValueError as exc:
        assert "face-pair enumeration" in str(exc)
    else:
        raise AssertionError("expected face-pair cap to fail closed")
