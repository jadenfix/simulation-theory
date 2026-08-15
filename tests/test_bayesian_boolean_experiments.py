from fractions import Fraction

from simtheory.bayesian_boolean_experiments import (
    bayesian_boolean_gap,
    boolean_zeta_reconstruct,
    exact_bayesian_boolean_geometry,
    essential_coordinates,
    uniform_boolean_influence,
    uniform_boolean_prior,
)


def _truth_table(bit_count, fn):
    return tuple(
        int(fn(tuple((x >> (bit_count - 1 - i)) & 1 for i in range(bit_count))))
        for x in range(1 << bit_count)
    )


def test_uniform_leave_one_out_gap_is_half_boolean_influence():
    functions = (
        _truth_table(3, lambda x: x[0] ^ x[1] ^ x[2]),
        _truth_table(3, lambda x: x[0] & x[1] & x[2]),
        _truth_table(3, lambda x: int(sum(x) >= 2)),
    )
    prior = uniform_boolean_prior(3)
    for table in functions:
        for i in range(3):
            observed = tuple(j for j in range(3) if j != i)
            assert bayesian_boolean_gap(table, prior, observed) == uniform_boolean_influence(table, i) / 2


def test_parity_retains_maximal_bayesian_uncertainty_until_all_bits_are_seen():
    table = _truth_table(3, lambda x: x[0] ^ x[1] ^ x[2])
    result = exact_bayesian_boolean_geometry(table)
    assert result.valid
    for subset, value in result.subset_values:
        assert value == (0 if len(subset) == 3 else Fraction(1, 2))
    coefficients = result.coefficients
    assert coefficients[()] == Fraction(1, 2)
    assert coefficients[(0, 1, 2)] == Fraction(-1, 2)
    assert all(
        value == 0
        for subset, value in coefficients.items()
        if subset not in ((), (0, 1, 2))
    )


def test_and_has_same_support_order_as_parity_but_much_smaller_bayesian_gap():
    table = _truth_table(3, lambda x: x[0] & x[1] & x[2])
    result = exact_bayesian_boolean_geometry(table)
    for subset, value in result.subset_values:
        assert value == (0 if len(subset) == 3 else Fraction(1, 8))
    assert result.coefficients[()] == Fraction(1, 8)
    assert result.coefficients[(0, 1, 2)] == Fraction(-1, 8)


def test_majority_spreads_interaction_mass_across_multiple_orders():
    table = _truth_table(3, lambda x: int(sum(x) >= 2))
    result = exact_bayesian_boolean_geometry(table)
    values = result.values
    assert values[()] == Fraction(1, 2)
    assert all(values[(i,)] == Fraction(1, 4) for i in range(3))
    assert all(values[pair] == Fraction(1, 4) for pair in ((0, 1), (0, 2), (1, 2)))
    assert values[(0, 1, 2)] == 0
    coefficients = result.coefficients
    assert all(coefficients[(i,)] == Fraction(-1, 4) for i in range(3))
    assert all(coefficients[pair] == Fraction(1, 4) for pair in ((0, 1), (0, 2), (1, 2)))
    assert coefficients[(0, 1, 2)] == Fraction(-1, 2)
    assert boolean_zeta_reconstruct(coefficients, 3) == values


def test_nonuniform_prior_changes_geometry_without_changing_truth_table():
    table = _truth_table(2, lambda x: x[0] ^ x[1])
    uniform = exact_bayesian_boolean_geometry(table)
    skewed_prior = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 10), Fraction(1, 10))
    skewed = exact_bayesian_boolean_geometry(table, skewed_prior)
    assert uniform.values[()] == Fraction(1, 2)
    assert skewed.values[()] == Fraction(1, 5)
    assert skewed.values[(0,)] == Fraction(1, 5)
    assert skewed.values[(1,)] == Fraction(1, 5)
    assert skewed.values[(0, 1)] == 0


def test_essential_coordinates_are_detected_operationally():
    table = _truth_table(4, lambda x: x[0] ^ x[2])
    assert essential_coordinates(table) == (0, 2)
    assert uniform_boolean_influence(table, 0) == 1
    assert uniform_boolean_influence(table, 1) == 0
    assert uniform_boolean_influence(table, 2) == 1
    assert uniform_boolean_influence(table, 3) == 0
