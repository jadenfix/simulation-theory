from fractions import Fraction

from simtheory.boolean_fourier_experiments import (
    boolean_walsh_coefficients,
    captured_spectral_weight,
    exact_fourier_experiment_certificate,
    exact_parseval_mass,
    influence_identity_holds,
    spectral_influence,
)
from simtheory.bayesian_boolean_experiments import uniform_boolean_influence


def _truth_table(bit_count, fn):
    return tuple(
        int(fn(tuple((x >> (bit_count - 1 - i)) & 1 for i in range(bit_count))))
        for x in range(1 << bit_count)
    )


def test_parseval_and_spectral_influence_hold_exactly():
    tables = (
        _truth_table(3, lambda x: x[0] ^ x[1] ^ x[2]),
        _truth_table(3, lambda x: x[0] & x[1] & x[2]),
        _truth_table(3, lambda x: int(sum(x) >= 2)),
    )
    for table in tables:
        assert exact_parseval_mass(table) == 1
        for i in range(3):
            assert influence_identity_holds(table, i)
            assert spectral_influence(table, i) == uniform_boolean_influence(table, i)


def test_parity_has_zero_captured_nonconstant_mass_until_full_support_is_observed():
    table = _truth_table(3, lambda x: x[0] ^ x[1] ^ x[2])
    coefficients = boolean_walsh_coefficients(table)
    assert coefficients[(0, 1, 2)] in (Fraction(1), Fraction(-1))
    assert all(value == 0 for subset, value in coefficients.items() if subset != (0, 1, 2))
    for subset in ((), (0,), (1,), (0, 1), (0, 2), (1, 2)):
        cert = exact_fourier_experiment_certificate(table, subset)
        assert cert.bayes_gap == Fraction(1, 2)
        assert cert.absolute_bias == 0
        assert cert.captured_weight == 0
        assert cert.lower_slack == 0
        assert cert.upper_slack == 0
    full = exact_fourier_experiment_certificate(table, (0, 1, 2))
    assert full.bayes_gap == 0
    assert full.absolute_bias == full.captured_weight == 1


def test_leave_one_out_upper_spectral_bound_is_exact_and_equals_half_influence():
    table = _truth_table(3, lambda x: int(sum(x) >= 2))
    coefficients = boolean_walsh_coefficients(table)
    for i in range(3):
        observed = tuple(j for j in range(3) if j != i)
        cert = exact_fourier_experiment_certificate(table, observed)
        omitted_weight = 1 - captured_spectral_weight(coefficients, observed)
        assert cert.bayes_gap == uniform_boolean_influence(table, i) / 2
        assert cert.bayes_gap == omitted_weight / 2
        assert cert.upper_slack == 0


def test_and_exhibits_strict_l1_l2_spectral_sandwich_away_from_leave_one_out_boundary():
    table = _truth_table(3, lambda x: x[0] & x[1] & x[2])
    cert = exact_fourier_experiment_certificate(table, (0,))
    assert cert.bayes_gap == Fraction(1, 8)
    assert cert.absolute_bias == Fraction(3, 4)
    assert cert.absolute_bias**2 <= cert.captured_weight <= cert.absolute_bias
    assert cert.lower_slack >= 0
    assert cert.upper_slack >= 0
    assert cert.lower_slack + cert.upper_slack > 0


def test_majority_captured_weight_increases_with_observed_coordinate_set():
    table = _truth_table(3, lambda x: int(sum(x) >= 2))
    empty = exact_fourier_experiment_certificate(table, ())
    one = exact_fourier_experiment_certificate(table, (0,))
    two = exact_fourier_experiment_certificate(table, (0, 1))
    full = exact_fourier_experiment_certificate(table, (0, 1, 2))
    assert empty.captured_weight <= one.captured_weight <= two.captured_weight <= full.captured_weight
    assert empty.bayes_gap >= one.bayes_gap >= two.bayes_gap >= full.bayes_gap
