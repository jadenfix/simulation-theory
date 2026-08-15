from fractions import Fraction

import pytest

from simtheory.experiment_observation_lattice import (
    boolean_mobius_transform,
    boolean_zeta_transform,
    deterministic_model_experiment,
    parity_observation_lattice,
)


def test_boolean_mobius_and_zeta_transforms_are_exact_inverses():
    values = (Fraction(3), Fraction(2), Fraction(5), Fraction(1))
    coefficients = boolean_mobius_transform(values)
    assert boolean_zeta_transform(coefficients) == values


def test_three_bit_parity_has_pure_top_order_deterministic_interaction():
    result = parity_observation_lattice(3)
    assert result.valid
    assert result.oracle_values == (1,) * 8
    full_mask = (1 << 3) - 1

    for value in result.subset_values:
        if value.subset_mask == full_mask:
            assert value.deterministic_gap == 0
        else:
            assert value.deterministic_gap == 1

    # Constant one on every strict subset and zero on the full set has no
    # nonempty lower-order Möbius coefficients. Its sole nonconstant interaction
    # is the top-order coefficient -1.
    assert result.deterministic_mobius[0] == 1
    for mask in range(1, full_mask):
        assert result.deterministic_mobius[mask] == 0
    assert result.deterministic_mobius[full_mask] == -1


def test_three_bit_parity_has_pure_top_order_interaction_after_public_mixing():
    result = parity_observation_lattice(3)
    assert result.valid
    full_mask = 7
    for value in result.subset_values:
        if value.subset_mask == full_mask:
            assert value.mixed_gap == 0
        else:
            assert value.mixed_gap == Fraction(1, 2)
    assert result.mixed_mobius[0] == Fraction(1, 2)
    for mask in range(1, full_mask):
        assert result.mixed_mobius[mask] == 0
    assert result.mixed_mobius[full_mask] == -Fraction(1, 2)


def test_two_bit_parity_recovers_pairwise_complementarity_as_second_order_interaction():
    result = parity_observation_lattice(2)
    assert result.valid
    assert tuple(value.deterministic_gap for value in result.subset_values) == (1, 1, 1, 0)
    assert result.deterministic_mobius == (1, 0, 0, -1)
    assert tuple(value.mixed_gap for value in result.subset_values) == (
        Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), 0
    )
    assert result.mixed_mobius == (
        Fraction(1, 2), 0, 0, -Fraction(1, 2)
    )


def test_four_bit_parity_retains_only_fourth_order_nonconstant_interaction():
    result = parity_observation_lattice(4)
    assert result.valid
    full_mask = 15
    assert all(
        coefficient == 0
        for mask, coefficient in enumerate(result.deterministic_mobius)
        if 0 < mask < full_mask
    )
    assert result.deterministic_mobius[full_mask] == -1
    assert all(
        coefficient == 0
        for mask, coefficient in enumerate(result.mixed_mobius)
        if 0 < mask < full_mask
    )
    assert result.mixed_mobius[full_mask] == -Fraction(1, 2)


def test_experiment_validation_rejects_negative_labels_and_invalid_parity_size():
    with pytest.raises(ValueError):
        deterministic_model_experiment("bad", (0, -1))
    with pytest.raises(ValueError):
        parity_observation_lattice(0)
