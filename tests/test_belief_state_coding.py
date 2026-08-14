from fractions import Fraction

import pytest

from simtheory.belief_state_coding import (
    exact_belief_state_prefix_coding,
    hidden_law_model,
    posterior_belief,
    predict_belief,
)
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.observation_channel_value import (
    identity_observation_channel,
    symmetric_observation_channel,
    uninformative_observation_channel,
)


def _complete_graph(vertex_count: int) -> ConfusionGraph:
    vertices = tuple(range(vertex_count))
    return ConfusionGraph.from_edges(
        vertices,
        tuple(
            (left, right)
            for left in vertices
            for right in vertices
            if left < right
        ),
    )


def _source_laws():
    return (
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
    )


def _mixing_transition():
    return (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 2)),
    )


def test_exact_bayes_update_and_prediction():
    belief = (Fraction(1, 2), Fraction(1, 2))
    channel = symmetric_observation_channel(2, Fraction(3, 4))
    posterior = posterior_belief(belief, channel, 0)
    assert posterior == (Fraction(3, 4), Fraction(1, 4))
    assert predict_belief(posterior, _mixing_transition()) == belief


def test_identity_signal_matches_perfect_current_state_information():
    model = hidden_law_model(
        _source_laws(),
        (Fraction(1, 2), Fraction(1, 2)),
        _mixing_transition(),
        identity_observation_channel(2),
    )
    certificate = exact_belief_state_prefix_coding(
        _complete_graph(3),
        model,
        3,
        switching_penalty=Fraction(2, 5),
    )
    assert certificate.valid
    assert certificate.observed_value == certificate.perfect_value == 4
    assert certificate.clairvoyant_expected_value == Fraction(159, 40)
    assert certificate.perfect_regret == Fraction(1, 40)
    assert certificate.future_foresight_value == Fraction(1, 40)


def test_uninformative_signal_is_only_exogenous_randomness_and_has_zero_value():
    model = hidden_law_model(
        _source_laws(),
        (Fraction(1, 2), Fraction(1, 2)),
        _mixing_transition(),
        uninformative_observation_channel(2, (Fraction(1, 3), Fraction(2, 3))),
    )
    certificate = exact_belief_state_prefix_coding(
        _complete_graph(3),
        model,
        3,
        switching_penalty=Fraction(2, 5),
    )
    assert certificate.valid
    assert certificate.observed_value == certificate.no_signal_value
    assert certificate.information_value == 0


def test_noisy_signal_value_lies_between_no_signal_and_perfect_information():
    model = hidden_law_model(
        _source_laws(),
        (Fraction(1, 2), Fraction(1, 2)),
        _mixing_transition(),
        symmetric_observation_channel(2, Fraction(3, 4)),
    )
    certificate = exact_belief_state_prefix_coding(
        _complete_graph(3),
        model,
        3,
        switching_penalty=Fraction(2, 5),
    )
    assert certificate.valid
    assert certificate.perfect_value <= certificate.observed_value
    assert certificate.observed_value <= certificate.no_signal_value
    assert certificate.information_telescope == certificate.no_signal_regret
    assert certificate.no_signal_regret >= certificate.observed_regret
    assert certificate.observed_regret >= certificate.perfect_regret


def test_free_switching_makes_perfect_current_state_as_good_as_path_clairvoyance():
    model = hidden_law_model(
        _source_laws(),
        (Fraction(1, 2), Fraction(1, 2)),
        _mixing_transition(),
        identity_observation_channel(2),
    )
    certificate = exact_belief_state_prefix_coding(
        _complete_graph(3),
        model,
        4,
        switching_penalty=0,
    )
    assert certificate.valid
    assert certificate.perfect_value == certificate.clairvoyant_expected_value
    assert certificate.perfect_regret == 0


def test_invalid_hidden_law_models_are_rejected():
    with pytest.raises(ValueError):
        hidden_law_model(
            _source_laws(),
            (Fraction(1, 2), Fraction(1, 2)),
            ((1, 0),),
            identity_observation_channel(2),
        )
    with pytest.raises(ValueError):
        exact_belief_state_prefix_coding(
            _complete_graph(2),
            hidden_law_model(
                _source_laws(),
                (Fraction(1, 2), Fraction(1, 2)),
                _mixing_transition(),
                identity_observation_channel(2),
            ),
            2,
        )
