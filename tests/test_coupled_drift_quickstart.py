from fractions import Fraction

from simtheory.coupled_drift import exact_coupled_drift_path


def test_coupled_drift_quickstart_values():
    certificate = exact_coupled_drift_path(
        (Fraction(1, 2), Fraction(1, 2)),
        ((0, 1), (1, 0)),
        Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.objective_value == Fraction(5, 4)
    assert certificate.marginal_envelope == Fraction(7, 4)
