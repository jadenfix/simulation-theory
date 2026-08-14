from fractions import Fraction

import pytest

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.observation_channel_value import (
    exact_blackwell_comparison,
    exact_observation_channel_value,
    exact_sensing_decision,
    garble_observation_channel,
    identity_observation_channel,
    symmetric_heavy_source_laws,
    symmetric_observation_channel,
    uninformative_observation_channel,
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


def _k3_scenarios():
    return symmetric_heavy_source_laws(3, Fraction(4, 5))


def test_symmetric_k3_channel_separates_randomization_and_information_value():
    certificate = exact_observation_channel_value(
        _complete_graph(3),
        _k3_scenarios(),
        symmetric_observation_channel(3, Fraction(1, 2)),
    )
    assert certificate.valid
    assert certificate.deterministic_no_signal_value == Fraction(19, 10)
    assert certificate.shared_no_signal_value == Fraction(5, 3)
    assert certificate.deterministic_observation_value == Fraction(31, 20)
    assert certificate.shared_observation_value == Fraction(31, 20)
    assert certificate.perfect_information_value == Fraction(6, 5)
    assert certificate.randomization_value_without_information == Fraction(7, 30)
    assert certificate.information_value_over_shared_randomness == Fraction(7, 60)
    assert certificate.deterministic_signal_value == Fraction(7, 20)
    assert certificate.perfect_information_value_over_shared_randomness == Fraction(7, 15)


def test_uninformative_public_signal_can_supply_randomization_but_no_information():
    certificate = exact_observation_channel_value(
        _complete_graph(3),
        _k3_scenarios(),
        uninformative_observation_channel(
            3,
            (Fraction(1, 3),) * 3,
        ),
    )
    assert certificate.valid
    assert certificate.deterministic_no_signal_value == Fraction(19, 10)
    assert certificate.shared_no_signal_value == Fraction(5, 3)
    assert certificate.deterministic_observation_value == Fraction(5, 3)
    assert certificate.shared_observation_value == Fraction(5, 3)
    assert certificate.information_value_over_shared_randomness == 0
    assert len(set(certificate.deterministic_observation_policy.codes_by_signal)) == 3


def test_perfect_channel_and_symmetric_garbling_obey_blackwell_order():
    noisy = symmetric_observation_channel(3, Fraction(1, 2))
    comparison = exact_blackwell_comparison(
        _complete_graph(3),
        _k3_scenarios(),
        identity_observation_channel(3),
        noisy.matrix,
    )
    assert comparison.valid
    assert comparison.garbled_channel == noisy
    assert comparison.informative_value.shared_observation_value == Fraction(6, 5)
    assert comparison.garbled_value.shared_observation_value == Fraction(31, 20)
    assert comparison.value_improvement == Fraction(7, 20)


def test_garbling_to_independent_public_randomness_loses_only_information():
    noisy = symmetric_observation_channel(3, Fraction(1, 2))
    uniform_kernel = ((Fraction(1, 3),) * 3,) * 3
    garbled = garble_observation_channel(noisy, uniform_kernel)
    assert garbled == uninformative_observation_channel(3, (Fraction(1, 3),) * 3)

    comparison = exact_blackwell_comparison(
        _complete_graph(3),
        _k3_scenarios(),
        noisy,
        uniform_kernel,
    )
    assert comparison.valid
    assert comparison.informative_value.shared_observation_value == Fraction(31, 20)
    assert comparison.garbled_value.shared_observation_value == Fraction(5, 3)
    assert comparison.value_improvement == Fraction(7, 60)


def test_sensing_cost_has_exact_seven_over_sixty_threshold():
    certificate = exact_observation_channel_value(
        _complete_graph(3),
        _k3_scenarios(),
        symmetric_observation_channel(3, Fraction(1, 2)),
    )
    below = exact_sensing_decision(certificate, Fraction(1, 10))
    boundary = exact_sensing_decision(certificate, Fraction(7, 60))
    above = exact_sensing_decision(certificate, Fraction(1, 8))
    assert below.valid and boundary.valid and above.valid
    assert below.threshold == Fraction(7, 60)
    assert below.use_observation
    assert below.optimal_total_value == Fraction(33, 20)
    assert not boundary.use_observation
    assert boundary.optimal_total_value == Fraction(5, 3)
    assert not above.use_observation
    assert above.optimal_total_value == Fraction(5, 3)


def test_identity_channel_reaches_perfect_information_value():
    certificate = exact_observation_channel_value(
        _complete_graph(3),
        _k3_scenarios(),
        identity_observation_channel(3),
    )
    assert certificate.valid
    assert certificate.deterministic_observation_value == Fraction(6, 5)
    assert certificate.shared_observation_value == Fraction(6, 5)
    assert certificate.perfect_information_value == Fraction(6, 5)


def test_policy_and_game_caps_fail_loudly():
    graph = _complete_graph(3)
    scenarios = _k3_scenarios()
    channel = symmetric_observation_channel(3, Fraction(1, 2))
    with pytest.raises(ValueError):
        exact_observation_channel_value(
            graph,
            scenarios,
            channel,
            max_policies=2,
        )
    with pytest.raises(ValueError):
        exact_observation_channel_value(
            graph,
            scenarios,
            channel,
            max_game_bases=1,
        )


def test_invalid_channels_are_rejected():
    with pytest.raises(ValueError):
        symmetric_observation_channel(1, Fraction(1, 2))
    with pytest.raises(ValueError):
        uninformative_observation_channel(3, (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)))
    with pytest.raises(ValueError):
        garble_observation_channel(
            identity_observation_channel(3),
            ((1, 0), (0, 1)),
        )
