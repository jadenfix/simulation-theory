from fractions import Fraction

from simtheory.finite_mixture_global_tv import exact_global_tv_modulus
from simtheory.finite_mixture_row_uncertainty import (
    certified_latent_radius_with_channel_uncertainty,
    exact_row_uncertain_global_tv,
)


def F(n, d=1):
    return Fraction(n, d)


def test_uniform_binary_row_uncertainty_attains_two_epsilon_lipschitz_loss():
    nominal = ((1, 0), (0, 1))
    for epsilon in (F(1, 10), F(1, 4), F(2, 5)):
        cert = exact_row_uncertain_global_tv(nominal, (epsilon, epsilon))
        actual = (
            (1 - epsilon, epsilon),
            (epsilon, 1 - epsilon),
        )
        actual_modulus = exact_global_tv_modulus(actual)
        assert cert.valid
        assert cert.nominal.alpha == 1
        assert cert.simple_lower_bound == 1 - 2 * epsilon
        assert cert.facewise_lower_bound == 1 - 2 * epsilon
        assert actual_modulus.alpha == 1 - 2 * epsilon
        assert cert.robust_inverse_upper_bound == 1 / (1 - 2 * epsilon)


def test_half_tv_row_uncertainty_can_destroy_binary_identifiability_exactly():
    nominal = ((1, 0), (0, 1))
    cert = exact_row_uncertain_global_tv(nominal, (F(1, 2), F(1, 2)))
    collapsed = ((F(1, 2), F(1, 2)), (F(1, 2), F(1, 2)))
    actual = exact_global_tv_modulus(collapsed)
    assert cert.facewise_lower_bound == 0
    assert cert.robust_inverse_upper_bound is None
    assert actual.alpha == 0
    assert certified_latent_radius_with_channel_uncertainty(F(1, 100), cert) == 1


def test_face_specific_radii_improve_over_two_max_radius_bound():
    nominal = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    cert = exact_row_uncertain_global_tv(nominal, (0, 0, F(1, 4)))
    assert cert.valid
    assert cert.nominal.alpha == 1
    assert cert.simple_lower_bound == F(1, 2)
    assert cert.facewise_lower_bound == F(3, 4)
    assert cert.robust_inverse_upper_bound == F(4, 3)


def test_uniform_row_radii_reduce_every_face_by_same_two_rho_penalty():
    epsilon = F(1, 100)
    channel = (
        (1, 0, 0),
        (0, 1, 0),
        (F(1, 2), F(2, 5), F(1, 10)),
    )
    cert = exact_row_uncertain_global_tv(channel, (epsilon,) * 3)
    assert cert.nominal.alpha == F(1, 10)
    assert cert.simple_lower_bound == F(2, 25)
    assert cert.facewise_lower_bound == F(2, 25)
    assert cert.robust_inverse_upper_bound == F(25, 2)


def test_positive_robust_modulus_transfers_observed_confidence_to_latent_radius():
    nominal = ((1, 0), (0, 1))
    cert = exact_row_uncertain_global_tv(nominal, (F(1, 10), F(1, 10)))
    assert cert.facewise_lower_bound == F(4, 5)
    assert certified_latent_radius_with_channel_uncertainty(F(1, 20), cert) == F(1, 16)


def test_invalid_row_radius_vector_is_rejected():
    nominal = ((1, 0), (0, 1))
    for radii in ((F(1, 10),), (F(-1, 10), F(1, 10)), (2, 0)):
        try:
            exact_row_uncertain_global_tv(nominal, radii)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid rowwise uncertainty must fail closed")
