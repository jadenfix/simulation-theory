from math import inf, isclose

from simtheory.minimax import (
    fano_error_lower_bound,
    fano_iid_error_lower_bound,
    kl_divergence,
    le_cam_absolute_risk_lower_bound,
    necessary_iid_samples_for_error,
    uniform_model_information,
)


def test_identical_models_have_zero_information():
    models = [[0.5, 0.5], [0.5, 0.5], [0.5, 0.5]]
    assert uniform_model_information(models) == 0.0
    assert necessary_iid_samples_for_error(models, 0.1) == inf


def test_fano_bound_decreases_with_samples():
    models = [[0.8, 0.2], [0.5, 0.5], [0.2, 0.8], [0.1, 0.9]]
    assert fano_iid_error_lower_bound(models, 0) >= fano_error_lower_bound(models)
    assert fano_iid_error_lower_bound(models, 1) >= fano_iid_error_lower_bound(models, 2)


def test_kl_and_le_cam_bound():
    assert isclose(kl_divergence([0.5, 0.5], [0.5, 0.5]), 0.0)
    assert le_cam_absolute_risk_lower_bound(2.0, [0.5, 0.5], [0.5, 0.5]) == 0.5
