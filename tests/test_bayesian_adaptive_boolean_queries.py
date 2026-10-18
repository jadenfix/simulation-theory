from fractions import Fraction

from simtheory.bayesian_adaptive_boolean_queries import exact_adaptive_boolean_query_design
from simtheory.bayesian_boolean_experiments import bayesian_boolean_gap, uniform_boolean_prior


def _truth_table(bit_count, fn):
    return tuple(
        int(fn(tuple((x >> (bit_count - 1 - i)) & 1 for i in range(bit_count))))
        for x in range(1 << bit_count)
    )


def test_three_bit_multiplexer_has_strict_two_query_adaptivity_gain():
    table = _truth_table(3, lambda x: x[1] if x[0] == 0 else x[2])
    result = exact_adaptive_boolean_query_design(table, 2)
    assert result.valid
    assert result.adaptive_value == 0
    assert result.nonadaptive_value == Fraction(1, 4)
    assert result.adaptivity_gain == Fraction(1, 4)
    assert result.root_coordinate == 0


def test_multiplexer_selector_has_zero_myopic_gain_but_positive_option_value():
    table = _truth_table(3, lambda x: x[1] if x[0] == 0 else x[2])
    prior = uniform_boolean_prior(3)
    baseline = bayesian_boolean_gap(table, prior, ())
    selector_only = bayesian_boolean_gap(table, prior, (0,))
    assert baseline == selector_only == Fraction(1, 2)
    one_query = exact_adaptive_boolean_query_design(table, 1)
    two_query = exact_adaptive_boolean_query_design(table, 2)
    assert one_query.adaptive_value == Fraction(1, 4)
    assert two_query.adaptive_value == 0
    assert two_query.root_coordinate == 0


def test_adaptivity_cannot_hurt_and_budget_is_monotone():
    table = _truth_table(3, lambda x: int(sum(x) >= 2))
    values = [exact_adaptive_boolean_query_design(table, budget) for budget in range(4)]
    assert all(result.adaptive_value <= result.nonadaptive_value for result in values)
    assert all(values[i + 1].adaptive_value <= values[i].adaptive_value for i in range(3))
    assert values[-1].adaptive_value == 0


def test_parity_has_no_adaptive_advantage_before_full_information():
    table = _truth_table(3, lambda x: x[0] ^ x[1] ^ x[2])
    for budget in (0, 1, 2):
        result = exact_adaptive_boolean_query_design(table, budget)
        assert result.adaptive_value == result.nonadaptive_value == Fraction(1, 2)
    full = exact_adaptive_boolean_query_design(table, 3)
    assert full.adaptive_value == full.nonadaptive_value == 0


def _brute_force_adaptive_value(table, prior, cell, budget):
    # Independent recursion over every coordinate, including non-splitting ones.
    bit_count = len(table).bit_length() - 1
    mass = sum((prior[x] for x in cell), Fraction(0))
    if mass == 0:
        return Fraction(0)
    zero = sum((prior[x] for x in cell if table[x] == 0), Fraction(0))
    best = min(zero, mass - zero) / mass
    if budget == 0:
        return best
    for i in range(bit_count):
        total = Fraction(0)
        for b in (0, 1):
            side = tuple(x for x in cell if (x >> (bit_count - 1 - i)) & 1 == b)
            side_mass = sum((prior[x] for x in side), Fraction(0))
            if side_mass:
                total += side_mass / mass * _brute_force_adaptive_value(table, prior, side, budget - 1)
        best = min(best, total)
    return best


def test_bellman_solver_matches_brute_force_on_every_three_bit_table():
    # ST-T216, against an independent recursion; the bit order is checked on x0.
    assert _truth_table(3, lambda x: x[0]) == (0, 0, 0, 0, 1, 1, 1, 1)
    priors = (
        uniform_boolean_prior(3),
        tuple(Fraction(w, 36) for w in (1, 2, 3, 4, 5, 6, 15, 0)),
    )
    for mask in range(256):
        table = tuple((mask >> index) & 1 for index in range(8))
        for prior in priors:
            for budget in range(4):
                result = exact_adaptive_boolean_query_design(table, budget, prior)
                assert result.adaptive_value == _brute_force_adaptive_value(
                    table, prior, tuple(range(8)), budget
                )
