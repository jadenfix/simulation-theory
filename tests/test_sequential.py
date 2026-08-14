from math import isclose

from simtheory.sequential import (
    bernoulli_log_e_path,
    exact_anytime_rejection_probability,
    exact_expected_e_value,
    exact_expected_mixture_e_value,
    exact_anytime_mixture_rejection_probability,
    first_threshold_crossing,
    fixed_alternative_is_composite_null_eprocess,
    mixture_log_e_value,
)


def test_simple_null_expectation_is_one():
    assert isclose(exact_expected_e_value(10, 0.1, 0.1, 0.3), 1.0, rel_tol=1e-12)


def test_one_sided_composite_null_expectation_is_bounded():
    assert fixed_alternative_is_composite_null_eprocess(0.05, 0.1, 0.3)
    assert exact_expected_e_value(10, 0.05, 0.1, 0.3) <= 1.0 + 1e-12


def test_finite_horizon_optional_stopping_control():
    rejection = exact_anytime_rejection_probability(
        horizon=16,
        true_probability=0.1,
        null_probability=0.1,
        alternative_probability=0.5,
        alpha=0.05,
    )
    assert rejection <= 0.05 + 1e-12


def test_threshold_crossing_and_mixture():
    path = bernoulli_log_e_path([1] * 10, 0.1, 0.5)
    assert first_threshold_crossing(path, 0.05) is not None
    value = mixture_log_e_value(4, 10, 0.1, [0.2, 0.4], [0.5, 0.5])
    assert value > 0.0


def test_mixture_eprocess_calibration():
    assert isclose(
        exact_expected_mixture_e_value(12, 0.1, 0.1, [0.2, 0.4], [0.3, 0.7]),
        1.0,
        rel_tol=1e-12,
    )
    rejection = exact_anytime_mixture_rejection_probability(
        horizon=20,
        true_probability=0.1,
        null_probability=0.1,
        alternatives=[0.2, 0.4],
        weights=[0.3, 0.7],
        alpha=0.05,
    )
    assert rejection <= 0.05 + 1e-12
