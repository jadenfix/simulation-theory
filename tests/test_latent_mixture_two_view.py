from fractions import Fraction

from simtheory.latent_mixture_two_view import (
    exact_two_view_gauge_certificate,
    is_permutation_matrix,
    two_view_law,
)


def F(n, d=1):
    return Fraction(n, d)


def test_second_shared_latent_view_breaks_binary_continuous_gauge_exactly():
    prior = (F(1, 2), F(1, 2))
    channel = ((1, 0), (0, 1))
    gauge = ((F(3, 4), F(1, 4)), (0, 1))
    cert = exact_two_view_gauge_certificate(prior, channel, gauge)
    assert cert.valid
    assert cert.gauge.common_observed_law == (F(1, 2), F(1, 2))
    assert cert.original_two_view == ((F(1, 2), 0), (0, F(1, 2)))
    assert cert.transformed_two_view == ((F(3, 8), F(1, 8)), (F(1, 8), F(3, 8)))
    assert not cert.two_view_preserved
    assert cert.full_affine_rank and cert.transformed_prior_strictly_positive
    assert not cert.permutation_gauge


def test_permutation_label_switching_preserves_one_and_two_view_laws():
    prior = (F(1, 3), F(2, 3))
    channel = ((F(3, 4), F(1, 4)), (F(1, 5), F(4, 5)))
    swap = ((0, 1), (1, 0))
    cert = exact_two_view_gauge_certificate(prior, channel, swap)
    assert cert.valid
    assert cert.two_view_preserved
    assert cert.rigidity_hypotheses_hold
    assert cert.permutation_gauge
    assert cert.rigidity_conclusion_holds
    assert is_permutation_matrix(swap)


def test_three_component_nonpermutation_gauge_is_rejected_by_second_view():
    prior = (F(1, 3),) * 3
    channel = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    gauge = (
        (F(3, 4), F(1, 4), 0),
        (0, F(3, 4), F(1, 4)),
        (0, 0, 1),
    )
    cert = exact_two_view_gauge_certificate(prior, channel, gauge)
    assert cert.valid
    assert cert.full_affine_rank and cert.transformed_prior_strictly_positive
    assert not cert.permutation_gauge
    assert not cert.two_view_preserved


def test_affine_rank_assumption_is_necessary_for_rigidity():
    prior = (F(1, 2), F(1, 2))
    channel = ((1, 0), (1, 0))
    gauge = ((F(3, 4), F(1, 4)), (0, 1))
    cert = exact_two_view_gauge_certificate(prior, channel, gauge)
    assert cert.valid
    assert not cert.full_affine_rank
    assert cert.transformed_prior_strictly_positive
    assert not cert.permutation_gauge
    assert cert.two_view_preserved
    assert not cert.rigidity_hypotheses_hold


def test_strictly_positive_prior_assumption_is_necessary_for_rigidity():
    prior = (1, 0)
    channel = ((1, 0), (0, 1))
    gauge = ((1, 0), (F(1, 2), F(1, 2)))
    cert = exact_two_view_gauge_certificate(prior, channel, gauge)
    assert cert.valid
    assert cert.full_affine_rank
    assert not cert.transformed_prior_strictly_positive
    assert not cert.permutation_gauge
    assert cert.two_view_preserved
    assert not cert.rigidity_hypotheses_hold


def test_two_view_law_is_a_probability_matrix():
    law = two_view_law(
        (F(1, 4), F(3, 4)),
        ((F(2, 3), F(1, 3)), (F(1, 5), F(4, 5))),
    )
    assert all(v >= 0 for row in law for v in row)
    assert sum((v for row in law for v in row), Fraction(0)) == 1
    assert law[0][1] == law[1][0]
