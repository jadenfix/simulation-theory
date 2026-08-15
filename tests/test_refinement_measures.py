from fractions import Fraction

from simtheory.refinement_measures import (
    equal_clone_score_scaling,
    escort_category_mass,
    forced_refinement_mass,
    rational_refinement_uniqueness_certificate,
)


def F(n, d=1):
    return Fraction(n, d)


def test_normalized_rational_refinement_additivity_forces_identity_mass():
    for denominator in range(1, 21):
        for numerator in range(denominator + 1):
            weight = Fraction(numerator, denominator)
            cert = rational_refinement_uniqueness_certificate(weight)
            assert cert.valid
            assert cert.forced_mass == weight == forced_refinement_mass(weight)


def test_equal_clone_escort_score_scaling_is_r_to_one_minus_gamma():
    weight = F(3, 7)
    for clones in (2, 3, 5, 10):
        assert equal_clone_score_scaling(weight, clones, 0) == clones
        assert equal_clone_score_scaling(weight, clones, 1) == 1
        assert equal_clone_score_scaling(weight, clones, 2) == F(1, clones)
        assert equal_clone_score_scaling(weight, clones, 3) == F(1, clones * clones)


def test_only_linear_escort_mass_survives_equal_positive_clone_refinement():
    original_prior = (F(1, 2), F(1, 2))
    original_categories = ("base", "simulated")
    for clones in (2, 5, 10, 50):
        refined_prior = (F(1, 2),) + (F(1, 2 * clones),) * clones
        refined_categories = ("base",) + ("simulated",) * clones

        assert escort_category_mass(
            original_prior, original_categories, "simulated", 1
        ) == F(1, 2)
        assert escort_category_mass(
            refined_prior, refined_categories, "simulated", 1
        ) == F(1, 2)

        assert escort_category_mass(
            refined_prior, refined_categories, "simulated", 0
        ) == F(clones, clones + 1)
        assert escort_category_mass(
            refined_prior, refined_categories, "simulated", 2
        ) == F(1, clones + 1)


def test_counting_and_quadratic_escort_move_in_opposite_directions_under_same_refinement():
    clones = 20
    prior = (F(1, 2),) + (F(1, 2 * clones),) * clones
    categories = ("base",) + ("simulated",) * clones
    count_mass = escort_category_mass(prior, categories, "simulated", 0)
    linear_mass = escort_category_mass(prior, categories, "simulated", 1)
    quadratic_mass = escort_category_mass(prior, categories, "simulated", 2)
    assert count_mass == F(20, 21)
    assert linear_mass == F(1, 2)
    assert quadratic_mass == F(1, 21)
    assert count_mass > linear_mass > quadratic_mass


def test_invalid_measure_inputs_fail_closed():
    for weight in (F(-1, 10), F(11, 10)):
        try:
            rational_refinement_uniqueness_certificate(weight)
        except ValueError:
            pass
        else:
            raise AssertionError("out-of-simplex weight should be rejected")
