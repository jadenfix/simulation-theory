from fractions import Fraction

from simtheory.independent_latent_prior_confidence import (
    _ceil_sqrt_fraction_on_grid,
    data_calibrated_gain_interval,
    data_calibrated_value_band,
    data_certifies_gain_ranking,
    data_certifies_value_ranking,
    empirical_latent_prior,
    independent_latent_tv_confidence_radius,
)


def test_outward_rational_square_root_is_minimal_on_declared_grid():
    target = Fraction(2, 9)
    radius = _ceil_sqrt_fraction_on_grid(target, 100)
    assert radius == Fraction(48, 100)
    assert radius**2 >= target
    assert Fraction(47, 100) ** 2 < target


def test_confidence_radius_satisfies_exact_second_moment_markov_requirement():
    result = independent_latent_tv_confidence_radius((40, 35, 25), Fraction(1, 10), grid_denominator=10_000)
    assert result.valid
    assert result.empirical_prior == (Fraction(2, 5), Fraction(7, 20), Fraction(1, 4))
    assert result.raw_squared_radius == Fraction(1, 20)
    assert result.radius**2 >= result.raw_squared_radius


def test_more_independent_latent_units_shrink_unclipped_radius():
    small = independent_latent_tv_confidence_radius((500, 500), Fraction(1, 10), grid_denominator=1_000_000)
    large = independent_latent_tv_confidence_radius((2000, 2000), Fraction(1, 10), grid_denominator=1_000_000)
    assert large.radius < small.radius
    # Quadrupling N halves the ideal radius; outward grid rounding allows only one-grid-cell slack.
    assert abs(2 * large.radius - small.radius) <= Fraction(2, 1_000_000)


def test_small_sample_can_correctly_collapse_to_full_simplex_radius():
    result = independent_latent_tv_confidence_radius((1, 0, 0, 0), Fraction(1, 20))
    assert result.valid
    assert result.clipped_at_one
    assert result.radius == 1


def test_data_calibration_composes_with_bayesian_value_and_gain_robustness():
    counts = (5000, 5000)
    band = data_calibrated_value_band(counts, Fraction(1, 4), Fraction(1, 5))
    assert band.valid
    assert band.interval[0] <= Fraction(1, 4) <= band.interval[1]
    conf, gain_band = data_calibrated_gain_interval(counts, Fraction(1, 3), Fraction(1, 5))
    assert conf.valid
    assert gain_band[0] <= Fraction(1, 3) <= gain_band[1]


def test_ranking_certification_requires_margin_larger_than_calibrated_uncertainty():
    counts = (10000, 10000)
    conf = independent_latent_tv_confidence_radius(counts, Fraction(1, 10))
    assert data_certifies_value_ranking(counts, 3 * conf.radius, Fraction(1, 10))
    assert not data_certifies_value_ranking(counts, 2 * conf.radius, Fraction(1, 10))
    assert data_certifies_gain_ranking(counts, 5 * conf.radius, Fraction(1, 10))
    assert not data_certifies_gain_ranking(counts, 4 * conf.radius, Fraction(1, 10))


def test_empirical_prior_counts_independent_units_not_within_unit_time_steps():
    assert empirical_latent_prior((3, 1)) == (Fraction(3, 4), Fraction(1, 4))
