from fractions import Fraction

import pytest

from simtheory.binary_repeated_evidence import (
    binary_signed_count,
    binary_symmetric_history_likelihoods,
    binary_symmetric_likelihood_ratio,
    exact_binary_even_plateau,
    exact_binary_history_sufficiency,
)


def test_signed_count_is_an_exact_likelihood_sufficient_statistic():
    certificate = exact_binary_history_sufficiency(Fraction(3, 4), 6)
    assert certificate.valid
    assert certificate.histories_examined == 64
    assert tuple(item.signed_count for item in certificate.classes) == (
        -6,
        -4,
        -2,
        0,
        2,
        4,
        6,
    )
    assert tuple(len(item.histories) for item in certificate.classes) == (
        1,
        6,
        15,
        20,
        15,
        6,
        1,
    )


def test_histories_with_equal_counts_have_equal_likelihood_pairs():
    left = (0, 1, 0, 1, 0, 1)
    right = (1, 0, 1, 0, 1, 0)
    assert binary_signed_count(left) == binary_signed_count(right) == 0
    assert binary_symmetric_history_likelihoods(Fraction(3, 4), left) == binary_symmetric_history_likelihoods(Fraction(3, 4), right)
    assert binary_symmetric_likelihood_ratio(Fraction(3, 4), left) == 1


def test_likelihood_ratio_is_exact_power_of_signed_count():
    history = (0, 0, 0, 1, 0)
    assert binary_signed_count(history) == 3
    assert binary_symmetric_likelihood_ratio(Fraction(3, 4), history) == 27
    reverse = tuple(1 - signal for signal in history)
    assert binary_symmetric_likelihood_ratio(Fraction(3, 4), reverse) == Fraction(1, 27)


def test_even_sample_plateau_has_exact_boundary_cancellation():
    for odd in (1, 3, 5, 7, 9):
        certificate = exact_binary_even_plateau(Fraction(3, 4), odd)
        assert certificate.valid
        assert certificate.tie_gain == certificate.tie_loss
        assert certificate.odd_accuracy == certificate.even_accuracy


def test_binary_evidence_caps_and_boundaries_fail_loudly():
    with pytest.raises(ValueError):
        exact_binary_history_sufficiency(Fraction(3, 4), 20, max_histories=100)
    with pytest.raises(ValueError):
        binary_symmetric_likelihood_ratio(1, (0, 0))
    with pytest.raises(ValueError):
        binary_signed_count((0, 2, 1))
    with pytest.raises(ValueError):
        exact_binary_even_plateau(Fraction(3, 4), 2)
