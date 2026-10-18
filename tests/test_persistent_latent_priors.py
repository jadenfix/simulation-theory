from fractions import Fraction

from simtheory.persistent_latent_priors import (
    fresh_unit_likelihood_ratio,
    mixture_outcome_law,
    misspecified_iid_binary_likelihood,
    noiseless_persistent_binary_likelihood,
    persistent_evidence_certificate,
    prior_ratio_bounds,
)


def test_mixture_likelihood_ratio_is_convex_average_of_prior_weight_ratios():
    a = (Fraction(3, 4), Fraction(1, 4))
    b = (Fraction(1, 4), Fraction(3, 4))
    channel = (
        (Fraction(9, 10), Fraction(1, 10)),
        (Fraction(1, 5), Fraction(4, 5)),
    )
    for outcome in (0, 1):
        cert = persistent_evidence_certificate(a, b, channel, outcome)
        assert cert.valid
        assert cert.lower_bound == Fraction(1, 3)
        assert cert.upper_bound == 3
        assert cert.lower_bound <= cert.likelihood_ratio <= cert.upper_bound


def test_mutually_singular_components_attain_prior_ratio_ceiling():
    a = (Fraction(3, 4), Fraction(1, 4))
    b = (Fraction(1, 4), Fraction(3, 4))
    channel = ((1, 0), (0, 1))
    assert persistent_evidence_certificate(a, b, channel, 0).likelihood_ratio == 3
    assert persistent_evidence_certificate(a, b, channel, 1).likelihood_ratio == Fraction(1, 3)


def test_noiseless_repetition_from_one_persistent_model_does_not_exponentiate_prior_evidence():
    theta_a = Fraction(3, 4)
    theta_b = Fraction(1, 4)
    for repeats in (1, 2, 10, 100):
        la = noiseless_persistent_binary_likelihood(theta_a, 1, repeats)
        lb = noiseless_persistent_binary_likelihood(theta_b, 1, repeats)
        assert la / lb == 3
    assert misspecified_iid_binary_likelihood(theta_a, 1, 100) / misspecified_iid_binary_likelihood(theta_b, 1, 100) == 3**100


def test_fresh_independent_latent_units_multiply_evidence():
    assert fresh_unit_likelihood_ratio((3, 3, 3, 3)) == 81
    assert fresh_unit_likelihood_ratio((Fraction(1, 3), Fraction(1, 3))) == Fraction(1, 9)


def test_general_outcome_law_and_ratio_bounds_are_exact():
    weights = (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2))
    channel = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    )
    assert mixture_outcome_law(weights, channel) == weights
    lower, upper = prior_ratio_bounds(
        (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
        (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
    )
    assert lower == Fraction(1, 2)
    assert upper == 2
