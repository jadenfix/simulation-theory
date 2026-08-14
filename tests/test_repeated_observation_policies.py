from fractions import Fraction

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.observation_channel_value import (
    symmetric_heavy_source_laws,
    symmetric_observation_channel,
)
from simtheory.repeated_observation_policies import (
    binary_symmetric_majority_accuracy,
    exact_repeated_terminal_blackwell_comparison,
    exact_repeated_terminal_observation_value,
    exact_sequential_observation_value,
    history_projection_garbling,
    product_observation_channel,
    symmetric_binary_terminal_cost,
)


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in range(count)
            for right in range(left + 1, count)
        ),
    )


def _two_scenario_k3():
    all_scenarios = symmetric_heavy_source_laws(3, Fraction(4, 5))
    return all_scenarios[:2]


def _binary_channel():
    return symmetric_observation_channel(2, Fraction(3, 4))


def test_product_channel_and_history_projection_are_exact():
    base = _binary_channel()
    product_three = product_observation_channel(base, 3)
    product_one = product_observation_channel(base, 1)
    projection = history_projection_garbling(2, 3, 1)
    assert product_three.valid and product_one.valid
    assert len(product_three.histories) == 8
    assert all(sum(row, Fraction(0)) == 1 for row in product_three.channel.matrix)

    from simtheory.observation_channel_value import garble_observation_channel

    assert garble_observation_channel(product_three.channel, projection) == product_one.channel


def test_symmetric_binary_majority_has_even_sample_plateaus():
    accuracy = Fraction(3, 4)
    expected = {
        1: Fraction(3, 4),
        2: Fraction(3, 4),
        3: Fraction(27, 32),
        4: Fraction(27, 32),
        5: Fraction(459, 512),
        6: Fraction(459, 512),
    }
    for repetitions, value in expected.items():
        assert binary_symmetric_majority_accuracy(accuracy, repetitions) == value
    for odd in (1, 3, 5, 7):
        assert binary_symmetric_majority_accuracy(accuracy, odd) == binary_symmetric_majority_accuracy(accuracy, odd + 1)


def test_terminal_repeated_observation_values_match_majority_formula():
    graph = _complete_graph(3)
    scenarios = _two_scenario_k3()
    channel = _binary_channel()
    # Exact policy enumeration is exercised through three signals.  The
    # four-signal plateau is proved independently by the closed binomial check
    # above, avoiding an unnecessary 2^16 policy sweep in every CI matrix job.
    expected = {
        1: Fraction(11, 8),
        2: Fraction(11, 8),
        3: Fraction(419, 320),
    }
    for repetitions, value in expected.items():
        certificate = exact_repeated_terminal_observation_value(
            graph,
            scenarios,
            channel,
            repetitions,
            max_policies=10_000,
        )
        assert certificate.valid
        assert certificate.shared_value == value
        assert certificate.deterministic_value == value
        assert value == symmetric_binary_terminal_cost(
            Fraction(6, 5),
            Fraction(19, 10),
            Fraction(3, 4),
            repetitions,
        )
    assert symmetric_binary_terminal_cost(
        Fraction(6, 5),
        Fraction(19, 10),
        Fraction(3, 4),
        4,
    ) == Fraction(419, 320)


def test_longer_terminal_history_blackwell_dominates_its_prefix():
    comparison = exact_repeated_terminal_blackwell_comparison(
        _complete_graph(3),
        _two_scenario_k3(),
        _binary_channel(),
        3,
        1,
        max_policies=10_000,
    )
    assert comparison.valid
    assert comparison.longer.shared_value == Fraction(419, 320)
    assert comparison.shorter.shared_value == Fraction(11, 8)
    assert comparison.value_improvement == Fraction(21, 320)


def test_sequential_zero_switching_values_accumulate_repeated_information():
    certificate = exact_sequential_observation_value(
        _complete_graph(3),
        _two_scenario_k3(),
        _binary_channel(),
        3,
        max_policies=100_000,
    )
    assert certificate.valid
    assert certificate.deterministic_no_observation_value == 5
    assert certificate.shared_no_observation_value == Fraction(93, 20)
    assert certificate.deterministic_observation_value == Fraction(1299, 320)
    assert certificate.shared_observation_value == Fraction(1299, 320)
    assert certificate.perfect_information_value == Fraction(18, 5)
    assert certificate.information_value_over_shared_randomness == Fraction(189, 320)


def test_sequential_switching_cost_couples_signal_history_actions():
    certificate = exact_sequential_observation_value(
        _complete_graph(3),
        _two_scenario_k3(),
        _binary_channel(),
        3,
        switching_penalty=Fraction(1, 10),
        max_policies=100_000,
        max_policy_dominance_pairs=20_000_000,
    )
    assert certificate.valid
    assert certificate.deterministic_observation_value == Fraction(261, 64)
    assert certificate.shared_observation_value == Fraction(261, 64)
    assert certificate.shared_no_observation_value == Fraction(93, 20)
    assert certificate.perfect_information_value == Fraction(18, 5)
    assert certificate.information_value_over_shared_randomness == Fraction(183, 320)
    assert certificate.selected_observation_policy.scenario_expected_switches == (
        Fraction(3, 16),
        Fraction(3, 16),
    )


def test_one_period_sequential_and_terminal_problems_agree():
    graph = _complete_graph(3)
    scenarios = _two_scenario_k3()
    channel = _binary_channel()
    terminal = exact_repeated_terminal_observation_value(
        graph,
        scenarios,
        channel,
        1,
    )
    sequential = exact_sequential_observation_value(
        graph,
        scenarios,
        channel,
        1,
    )
    assert terminal.valid and sequential.valid
    assert terminal.shared_value == sequential.shared_observation_value == Fraction(11, 8)
    assert terminal.deterministic_value == sequential.deterministic_observation_value == Fraction(11, 8)


def test_repeated_observation_caps_fail_loudly():
    graph = _complete_graph(3)
    scenarios = _two_scenario_k3()
    channel = _binary_channel()
    with pytest.raises(ValueError):
        product_observation_channel(channel, 10, max_histories=100)
    with pytest.raises(ValueError):
        exact_repeated_terminal_observation_value(
            graph,
            scenarios,
            channel,
            4,
            max_policies=10,
        )
    with pytest.raises(ValueError):
        exact_sequential_observation_value(
            graph,
            scenarios,
            channel,
            3,
            max_policies=10,
        )
