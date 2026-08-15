from fractions import Fraction

import pytest

from simtheory.binary_latent_mixture_identifiability import (
    bernoulli_emission_second_moment_theta_radius,
    binary_bernoulli_emission_theta,
    binary_mixture_identifiability_certificate,
    binary_mixture_law,
    latent_radius_from_emission_radius,
    total_variation,
)


def test_binary_mixture_tv_identity_is_exact_for_multicategory_emissions():
    row0 = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    row1 = (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2))
    cert = binary_mixture_identifiability_certificate(Fraction(4, 5), Fraction(1, 5), row0, row1)
    assert cert.valid
    assert cert.row_separation == Fraction(1, 3)
    assert cert.latent_tv == Fraction(3, 5)
    assert cert.emission_tv == Fraction(1, 5)


def test_identical_rows_destroy_mixing_weight_identifiability():
    row = (Fraction(2, 5), Fraction(3, 5))
    assert binary_mixture_law(Fraction(1, 10), row, row) == binary_mixture_law(Fraction(9, 10), row, row)
    assert total_variation(row, row) == 0
    assert latent_radius_from_emission_radius(Fraction(1, 100), row, row) == 1


def test_observed_law_uncertainty_is_amplified_by_inverse_row_separation():
    row0 = (Fraction(9, 10), Fraction(1, 10))
    row1 = (Fraction(1, 10), Fraction(9, 10))
    assert total_variation(row0, row1) == Fraction(4, 5)
    assert latent_radius_from_emission_radius(Fraction(1, 10), row0, row1) == Fraction(1, 8)


def test_binary_bernoulli_mixture_inversion_is_exact():
    assert binary_bernoulli_emission_theta(Fraction(1, 2), Fraction(1, 5), Fraction(4, 5)) == Fraction(1, 2)
    assert binary_bernoulli_emission_theta(Fraction(7, 20), Fraction(1, 5), Fraction(4, 5)) == Fraction(1, 4)
    with pytest.raises(ValueError):
        binary_bernoulli_emission_theta(Fraction(1, 2), Fraction(1, 3), Fraction(1, 3))


def test_emission_noise_inflates_latent_squared_confidence_radius_quadratically():
    # q_hat=1/2 maps to theta_hat=1/2 in both channels.
    clean = bernoulli_emission_second_moment_theta_radius(
        500, 500, 0, 1, Fraction(1, 10)
    )
    noisy = bernoulli_emission_second_moment_theta_radius(
        500, 500, Fraction(1, 4), Fraction(3, 4), Fraction(1, 10)
    )
    assert clean[0] == noisy[0] == Fraction(1, 2)
    assert clean[1] == noisy[1]
    assert noisy[2] == 4 * clean[2]


def test_required_sample_size_scaling_is_inverse_square_in_row_separation():
    # The squared theta radius is [1/(4N alpha)] / d^2.
    _, _, r2_d1 = bernoulli_emission_second_moment_theta_radius(500, 500, 0, 1, Fraction(1, 10))
    _, _, r2_dhalf = bernoulli_emission_second_moment_theta_radius(500, 500, Fraction(1, 4), Fraction(3, 4), Fraction(1, 10))
    assert r2_dhalf / r2_d1 == 4
