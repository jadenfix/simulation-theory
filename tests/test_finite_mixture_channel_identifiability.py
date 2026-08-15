from dataclasses import replace
from fractions import Fraction
from itertools import combinations

from simtheory.finite_mixture_channel_identifiability import (
    certified_latent_tv_radius,
    exact_finite_mixture_channel_certificate,
    mixture_law,
    reconstruct_latent_difference,
    total_variation,
)


def F(n, d=1):
    return Fraction(n, d)


def _simplex_grid(count: int, denominator: int):
    def rec(prefix, remaining, slots):
        if slots == 1:
            yield tuple(prefix + [Fraction(remaining, denominator)])
            return
        for value in range(remaining + 1):
            yield from rec(
                prefix + [Fraction(value, denominator)],
                remaining - value,
                slots - 1,
            )

    yield from rec([], denominator, count)


def _ternary_half_grid():
    return tuple(_simplex_grid(3, 2))


def test_binary_identity_channel_has_exact_unit_tv_inverse_constant():
    channel = ((1, 0), (0, 1))
    cert = exact_finite_mixture_channel_certificate(channel)
    assert cert.valid and cert.identifiable
    assert cert.affine_rank == 1
    assert cert.reconstruction is not None
    assert cert.reconstruction.tv_conditioning_constant == 1

    left = (F(3, 4), F(1, 4))
    right = (F(1, 4), F(3, 4))
    ql, qr = mixture_law(left, channel), mixture_law(right, channel)
    delta = tuple(a - b for a, b in zip(ql, qr))
    assert reconstruct_latent_difference(delta, cert) == tuple(
        a - b for a, b in zip(left, right)
    )
    assert total_variation(left, right) == total_variation(ql, qr)


def test_binary_noisy_channel_recovers_inverse_of_exact_row_separation():
    channel = ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)))
    cert = exact_finite_mixture_channel_certificate(channel)
    assert cert.valid and cert.identifiable
    assert cert.reconstruction is not None
    assert total_variation(channel[0], channel[1]) == F(1, 2)
    assert cert.reconstruction.tv_conditioning_constant == 2
    assert certified_latent_tv_radius(F(1, 10), cert) == F(1, 5)


def test_affine_dependence_returns_explicit_distinct_colliding_priors():
    channel = ((1, 0), (0, 1), (F(1, 2), F(1, 2)))
    cert = exact_finite_mixture_channel_certificate(channel)
    assert cert.valid and not cert.identifiable
    assert cert.affine_rank == 1
    assert cert.collision is not None
    witness = cert.collision
    assert witness.left_prior != witness.right_prior
    assert mixture_law(witness.left_prior, channel) == witness.common_observed_law
    assert mixture_law(witness.right_prior, channel) == witness.common_observed_law
    assert certified_latent_tv_radius(F(1, 100), cert) == 1


def test_identity_k3_is_identifiable_but_coordinate_minor_bound_is_conservative():
    channel = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    cert = exact_finite_mixture_channel_certificate(channel)
    assert cert.valid and cert.identifiable
    assert cert.affine_rank == 2
    assert cert.reconstruction is not None
    # The actual channel is the identity and therefore preserves TV exactly,
    # but the generic selected-coordinate L1 proof certifies the safe constant 2.
    assert cert.reconstruction.tv_conditioning_constant == 2
    left = (F(1, 2), F(1, 3), F(1, 6))
    right = (F(1, 6), F(1, 3), F(1, 2))
    ql, qr = mixture_law(left, channel), mixture_law(right, channel)
    assert total_variation(left, right) == total_variation(ql, qr)
    delta = tuple(a - b for a, b in zip(ql, qr))
    assert reconstruct_latent_difference(delta, cert) == tuple(
        a - b for a, b in zip(left, right)
    )


def test_exact_reconstruction_and_tv_bound_hold_on_small_ternary_channel_grid():
    rows = _ternary_half_grid()
    priors = tuple(_simplex_grid(3, 3))
    checked_identifiable = checked_collisions = 0
    for channel in combinations(rows, 3):
        cert = exact_finite_mixture_channel_certificate(channel)
        assert cert.valid
        if not cert.identifiable:
            checked_collisions += 1
            assert cert.collision is not None
            assert mixture_law(cert.collision.left_prior, channel) == mixture_law(
                cert.collision.right_prior, channel
            )
            continue
        checked_identifiable += 1
        assert cert.reconstruction is not None
        c = cert.reconstruction.tv_conditioning_constant
        for left in priors:
            for right in priors:
                ql, qr = mixture_law(left, channel), mixture_law(right, channel)
                observed_delta = tuple(a - b for a, b in zip(ql, qr))
                recovered = reconstruct_latent_difference(observed_delta, cert)
                assert recovered == tuple(a - b for a, b in zip(left, right))
                assert total_variation(left, right) <= c * total_variation(ql, qr)
    assert checked_identifiable > 0
    assert checked_collisions > 0


def test_certificate_validation_rejects_forged_collision_and_inverse_receipts():
    dependent = exact_finite_mixture_channel_certificate(
        ((1, 0), (0, 1), (F(1, 2), F(1, 2)))
    )
    assert dependent.collision is not None
    forged_collision = replace(
        dependent,
        collision=replace(dependent.collision, common_observed_law=(1, 0)),
    )
    assert not forged_collision.valid

    identifiable = exact_finite_mixture_channel_certificate(((1, 0), (0, 1)))
    assert identifiable.reconstruction is not None
    forged_inverse = replace(
        identifiable,
        reconstruction=replace(
            identifiable.reconstruction,
            full_reconstruction=((0, 0),),
        ),
    )
    assert not forged_inverse.valid


def test_minor_search_cap_fails_closed_before_uncertified_fallback():
    channel = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    try:
        exact_finite_mixture_channel_certificate(channel, max_minors=0)
    except ValueError as exc:
        assert "exceeded configured cap" in str(exc)
    else:
        raise AssertionError("expected bounded minor search to fail closed")
