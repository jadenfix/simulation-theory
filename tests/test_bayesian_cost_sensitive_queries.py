from fractions import Fraction

from simtheory.bayesian_cost_sensitive_queries import exact_cost_sensitive_boolean_query_design


def _truth_table(bit_count, fn):
    return tuple(
        int(fn(tuple((x >> (bit_count - 1 - i)) & 1 for i in range(bit_count))))
        for x in range(1 << bit_count)
    )


def test_multiplexer_selector_is_dynamically_optimal_despite_negative_myopic_net_value():
    table = _truth_table(3, lambda x: x[1] if x[0] == 0 else x[2])
    result = exact_cost_sensitive_boolean_query_design(table, (Fraction(1, 8),) * 3, 2)
    assert result.valid
    assert result.root_coordinate == 0
    assert result.value == Fraction(1, 4)
    root = result.nodes[0]
    assert root.stop_loss == Fraction(1, 2)
    # Querying selector x0 and then stopping would cost 1/8 + 1/2, worse than stopping.
    assert Fraction(1, 8) + Fraction(1, 2) > root.stop_loss


def test_multiplexer_uniform_cost_threshold_is_one_quarter():
    table = _truth_table(3, lambda x: x[1] if x[0] == 0 else x[2])
    below = exact_cost_sensitive_boolean_query_design(table, (Fraction(1, 5),) * 3, 2)
    threshold = exact_cost_sensitive_boolean_query_design(table, (Fraction(1, 4),) * 3, 2)
    above = exact_cost_sensitive_boolean_query_design(table, (Fraction(1, 3),) * 3, 2)
    assert below.root_coordinate == 0
    assert below.value == Fraction(2, 5)
    assert threshold.value == Fraction(1, 2)
    assert threshold.root_coordinate is None
    assert above.value == Fraction(1, 2)
    assert above.root_coordinate is None


def test_zero_query_cost_recovers_two_query_zero_terminal_gap():
    table = _truth_table(3, lambda x: x[1] if x[0] == 0 else x[2])
    result = exact_cost_sensitive_boolean_query_design(table, (0, 0, 0), 2)
    assert result.value == 0
    assert result.root_coordinate == 0


def test_parity_stops_when_query_cost_exceeds_remaining_value_of_information():
    table = _truth_table(3, lambda x: x[0] ^ x[1] ^ x[2])
    result = exact_cost_sensitive_boolean_query_design(table, (Fraction(1, 10),) * 3, 2)
    # Two queries cannot reduce parity error at all, so any positive cost makes stopping optimal.
    assert result.value == Fraction(1, 2)
    assert result.root_coordinate is None
