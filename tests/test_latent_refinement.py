from fractions import Fraction

from simtheory.latent_refinement import (
    exact_latent_refinement,
    shared_latent_view_law,
    uniform_label_category_mass,
    weighted_category_mass,
)


def F(n, d=1):
    return Fraction(n, d)


def _base_problem():
    return (
        (F(1, 2), F(1, 2)),
        ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4))),
        ("base", "simulated"),
    )


def test_positive_weight_cloning_preserves_every_checked_shared_latent_view_law():
    prior, channel, categories = _base_problem()
    cert = exact_latent_refinement(
        prior,
        channel,
        categories,
        1,
        (F(1, 5),) * 5,
        max_views_checked=5,
    )
    assert cert.valid
    assert cert.original_view_laws == cert.refined_view_laws
    assert weighted_category_mass(prior, categories, "simulated") == F(1, 2)
    assert weighted_category_mass(
        cert.refined_prior, cert.refined_categories, "simulated"
    ) == F(1, 2)


def test_uniform_label_mass_can_be_driven_toward_one_without_changing_observations():
    prior, channel, categories = _base_problem()
    assert uniform_label_category_mass(categories, "simulated") == F(1, 2)
    for clones in (2, 5, 10, 50):
        cert = exact_latent_refinement(
            prior,
            channel,
            categories,
            1,
            (Fraction(1, clones),) * clones,
            max_views_checked=3,
        )
        assert cert.valid
        assert uniform_label_category_mass(
            cert.refined_categories, "simulated"
        ) == Fraction(clones, clones + 1)
        assert weighted_category_mass(
            cert.refined_prior, cert.refined_categories, "simulated"
        ) == F(1, 2)
        assert cert.original_view_laws == cert.refined_view_laws


def test_uniform_label_mass_can_also_be_driven_toward_zero_by_refining_other_category():
    prior, channel, categories = _base_problem()
    for clones in (2, 10, 50):
        cert = exact_latent_refinement(
            prior,
            channel,
            categories,
            0,
            (Fraction(1, clones),) * clones,
            max_views_checked=3,
        )
        assert uniform_label_category_mass(
            cert.refined_categories, "simulated"
        ) == Fraction(1, clones + 1)
        assert weighted_category_mass(
            cert.refined_prior, cert.refined_categories, "simulated"
        ) == F(1, 2)
        assert cert.original_view_laws == cert.refined_view_laws


def test_unequal_positive_split_weights_preserve_weighted_category_measure():
    prior, channel, categories = _base_problem()
    split = (F(1, 2), F(1, 3), F(1, 6))
    cert = exact_latent_refinement(
        prior, channel, categories, 1, split, max_views_checked=4
    )
    assert cert.valid
    assert cert.refined_prior[1:4] == (F(1, 4), F(1, 6), F(1, 12))
    assert weighted_category_mass(
        cert.refined_prior, cert.refined_categories, "simulated"
    ) == F(1, 2)


def test_shared_view_law_cap_fails_closed():
    prior, channel, _ = _base_problem()
    try:
        shared_latent_view_law(prior, channel, 10, max_outcomes=100)
    except ValueError as exc:
        assert "outcome space" in str(exc)
    else:
        raise AssertionError("expected bounded view enumeration to fail closed")
