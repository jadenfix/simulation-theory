from fractions import Fraction

from simtheory.latent_mixture_gauge import (
    affine_row_rank,
    exact_latent_mixture_gauge_transform,
    observed_law,
)


def F(n, d=1):
    return Fraction(n, d)


def test_binary_nonpermutation_gauge_changes_prior_and_channel_but_not_observations():
    prior = (F(1, 2), F(1, 2))
    channel = ((1, 0), (0, 1))
    gauge = ((F(3, 4), F(1, 4)), (0, 1))
    cert = exact_latent_mixture_gauge_transform(prior, channel, gauge)
    assert cert.valid and cert.nontrivial
    assert cert.transformed_prior == (F(2, 3), F(1, 3))
    assert cert.transformed_channel == gauge
    assert cert.common_observed_law == (F(1, 2), F(1, 2))
    assert cert.original_affine_rank == cert.transformed_affine_rank == 1


def test_rational_continuum_approaches_identity_while_remaining_observationally_equivalent():
    prior = (F(1, 2), F(1, 2))
    channel = ((1, 0), (0, 1))
    for t in (F(1, 100), F(1, 20), F(1, 10), F(1, 4), F(2, 5)):
        gauge = ((1 - t, t), (0, 1))
        cert = exact_latent_mixture_gauge_transform(prior, channel, gauge)
        assert cert.valid and cert.nontrivial
        assert cert.common_observed_law == observed_law(prior, channel)
        assert cert.transformed_prior != prior
        assert cert.transformed_channel != channel
        assert cert.original_affine_rank == cert.transformed_affine_rank == 1


def test_three_component_full_affine_rank_is_preserved_by_invertible_stochastic_gauge():
    prior = (F(1, 3),) * 3
    channel = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    gauge = (
        (F(3, 4), F(1, 4), 0),
        (0, F(3, 4), F(1, 4)),
        (0, 0, 1),
    )
    cert = exact_latent_mixture_gauge_transform(prior, channel, gauge)
    assert cert.valid and cert.nontrivial
    assert cert.transformed_prior == (F(4, 9), F(8, 27), F(7, 27))
    assert cert.common_observed_law == prior
    assert affine_row_rank(channel) == affine_row_rank(cert.transformed_channel) == 2


def test_joint_unknown_factorization_is_not_fixed_by_infinite_one_view_data():
    # Both factorizations below have distinct, affinely independent binary rows
    # and different mixing weights, yet exactly the same observed law.
    p1 = (F(1, 2), F(1, 2))
    k1 = ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)))
    p2 = (F(1, 4), F(3, 4))
    k2 = ((1, 0), (F(1, 3), F(2, 3)))
    assert p1 != p2 and k1 != k2
    assert affine_row_rank(k1) == affine_row_rank(k2) == 1
    assert observed_law(p1, k1) == observed_law(p2, k2) == (F(1, 2), F(1, 2))


def test_invalid_or_noninvertible_gauges_fail_closed():
    prior = (F(1, 2), F(1, 2))
    channel = ((1, 0), (0, 1))
    bad = (
        ((F(1, 2), F(1, 2)), (F(1, 2), F(1, 2))),
        ((1, 1), (0, 1)),
        ((F(1, 4), F(3, 4)), (0, 1)),
    )
    for gauge in bad:
        try:
            exact_latent_mixture_gauge_transform(prior, channel, gauge)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid gauge should be rejected")


def test_iid_one_view_samples_of_any_length_have_identical_laws():
    # ST-T258: with the latent redrawn for each draw, every finite sample law is a
    # product of the common one-view law, so no sample size separates the pair.
    from itertools import product

    p1, k1 = (F(1, 2), F(1, 2)), ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)))
    p2, k2 = (F(1, 4), F(3, 4)), ((1, 0), (F(1, 3), F(2, 3)))
    q1, q2 = observed_law(p1, k1), observed_law(p2, k2)
    for n in range(1, 5):
        for ys in product(range(2), repeat=n):
            left = right = F(1)
            for y in ys:
                left *= q1[y]
                right *= q2[y]
            assert left == right


def test_gauge_perturbation_must_move_the_channel():
    # ST-T256: a B with (B - I) K = 0 and pi B = pi gives a trivial family.
    prior = (F(1, 4), F(1, 4), F(1, 2))
    channel = ((1, 0), (1, 0), (0, 1))
    t = F(1, 5)
    averaging = ((F(1, 2), F(1, 2), 0), (F(1, 2), F(1, 2), 0), (0, 0, 1))
    gauge = tuple(
        tuple((1 - t) * (1 if r == c else 0) + t * averaging[r][c] for c in range(3))
        for r in range(3)
    )
    cert = exact_latent_mixture_gauge_transform(prior, channel, gauge)
    assert cert.transformed_prior == prior
    assert cert.transformed_channel == tuple(tuple(F(x) for x in row) for row in channel)
