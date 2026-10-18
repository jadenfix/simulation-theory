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


def test_affine_and_linear_row_rank_coincide_for_probability_rows():
    # ST-T260: rows summing to one make affine rank equal linear rank minus one.
    from simtheory.latent_mixture_gauge import _rank, affine_row_rank

    channels = (
        ((1, 0), (1, 0)),
        ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ((F(1, 2), F(1, 2), 0), (0, F(1, 2), F(1, 2)), (F(1, 2), 0, F(1, 2))),
        ((F(1, 2), F(1, 2)), (1, 0), (0, 1)),
    )
    for channel in channels:
        k = tuple(tuple(F(v) for v in row) for row in channel)
        assert _rank(k) == affine_row_rank(k) + 1


def test_independently_redrawn_pairs_have_product_law_unchanged_by_the_gauge():
    # ST-T262: with redrawn latents the pair law is q q^T before and after the gauge.
    prior = (F(1, 2), F(1, 2))
    channel = ((1, 0), (0, 1))
    gauge = ((F(3, 4), F(1, 4)), (0, 1))
    cert = exact_two_view_gauge_certificate(prior, channel, gauge)
    q = cert.gauge.common_observed_law
    product_law = tuple(tuple(a * b for b in q) for a in q)
    transformed_q = tuple(
        sum((p * row[y] for p, row in zip(cert.gauge.transformed_prior, cert.gauge.transformed_channel)), F(0))
        for y in range(2)
    )
    assert tuple(tuple(a * b for b in transformed_q) for a in transformed_q) == product_law
    assert cert.transformed_two_view != product_law


def test_two_views_do_not_identify_outside_the_nonnegative_gauge_class():
    # Full-rank, strictly positive factorizations with equal one- and two-view laws,
    # related by a unit-row-sum gauge with a negative entry.
    first = ((F(1, 2), F(1, 2)), ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4))))
    second = ((F(1, 5), F(4, 5)), ((F(1), F(0)), (F(3, 8), F(5, 8))))
    assert two_view_law(*first) == two_view_law(*second) == (
        (F(5, 16), F(3, 16)),
        (F(3, 16), F(5, 16)),
    )
    three_view = [
        tuple(
            sum(p * row[a] * row[b] * row[c] for p, row in zip(*model))
            for a in range(2) for b in range(2) for c in range(2)
        )
        for model in (first, second)
    ]
    assert three_view[0] != three_view[1]
