from fractions import Fraction

import pytest

from simtheory.approximate_hidden_law import (
    exact_approximate_hidden_law_comparison,
    representative_approximate_quotient,
)
from simtheory.belief_state_coding import hidden_law_model
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.hidden_law_bisimulation import (
    exact_hidden_law_bisimulation,
    quotient_hidden_law_model,
)
from simtheory.observation_channel_value import RationalObservationChannel


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


def _exact_model():
    law_a = (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10))
    law_b = (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10))
    return hidden_law_model(
        (law_a, law_a, law_b),
        (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
        (
            (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
        ),
        RationalObservationChannel.from_values(
            (
                (Fraction(3, 4), Fraction(1, 4)),
                (Fraction(3, 4), Fraction(1, 4)),
                (Fraction(1, 4), Fraction(3, 4)),
            )
        ),
    )


def _approximate_model():
    return hidden_law_model(
        (
            (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
            (Fraction(3, 4), Fraction(3, 20), Fraction(1, 10)),
            (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
        ),
        (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
        (
            (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(9, 20), Fraction(3, 10)),
            (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
        ),
        RationalObservationChannel.from_values(
            (
                (Fraction(3, 4), Fraction(1, 4)),
                (Fraction(7, 10), Fraction(3, 10)),
                (Fraction(1, 4), Fraction(3, 4)),
            )
        ),
    )


def test_exact_bisimulation_limit_has_zero_bound_and_zero_value_difference():
    detailed = _exact_model()
    quotient = quotient_hidden_law_model(exact_hidden_law_bisimulation(detailed))
    certificate = exact_approximate_hidden_law_comparison(
        _complete_graph(3),
        detailed,
        quotient,
        ((0, 1), (2,)),
        3,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.exact_limit
    assert certificate.initial_tv == 0
    assert certificate.maximum_source_tv == 0
    assert certificate.maximum_stage_deviation == 0
    assert certificate.maximum_observation_tv == 0
    assert certificate.maximum_transition_tv == 0
    assert certificate.no_signal_value_bound == 0
    assert certificate.observed_value_bound == 0
    assert certificate.oracle_value_bound == 0


def test_representative_approximation_has_positive_certified_deviations():
    detailed = _approximate_model()
    abstract = representative_approximate_quotient(
        detailed,
        ((0, 1), (2,)),
    )
    certificate = exact_approximate_hidden_law_comparison(
        _complete_graph(3),
        detailed,
        abstract,
        ((0, 1), (2,)),
        3,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert not certificate.exact_limit
    assert certificate.initial_tv == 0
    assert certificate.maximum_source_tv == Fraction(1, 20)
    assert certificate.maximum_observation_tv == Fraction(1, 20)
    assert certificate.maximum_transition_tv == Fraction(1, 20)
    assert certificate.maximum_stage_deviation > 0
    assert certificate.no_signal_divergence_bound > 0
    assert certificate.observed_divergence_bound >= certificate.no_signal_divergence_bound

    assert abs(
        certificate.detailed_values.no_signal_value
        - certificate.abstract_values.no_signal_value
    ) <= certificate.no_signal_value_bound
    assert abs(
        certificate.detailed_values.observed_value
        - certificate.abstract_values.observed_value
    ) <= certificate.observed_value_bound
    assert abs(
        certificate.detailed_values.clairvoyant_expected_value
        - certificate.abstract_values.clairvoyant_expected_value
    ) <= certificate.oracle_value_bound


def test_longer_horizon_weakly_increases_the_declared_coupling_bounds():
    detailed = _approximate_model()
    abstract = representative_approximate_quotient(
        detailed,
        ((0, 1), (2,)),
    )
    short = exact_approximate_hidden_law_comparison(
        _complete_graph(3),
        detailed,
        abstract,
        ((0, 1), (2,)),
        2,
        switching_penalty=Fraction(1, 4),
    )
    long = exact_approximate_hidden_law_comparison(
        _complete_graph(3),
        detailed,
        abstract,
        ((0, 1), (2,)),
        4,
        switching_penalty=Fraction(1, 4),
    )
    assert short.valid and long.valid
    assert long.no_signal_divergence_bound >= short.no_signal_divergence_bound
    assert long.observed_divergence_bound >= short.observed_divergence_bound
    assert long.no_signal_value_bound >= short.no_signal_value_bound
    assert long.observed_value_bound >= short.observed_value_bound


def test_observation_error_affects_observed_but_not_no_signal_or_oracle_mismatch():
    detailed = _exact_model()
    exact_quotient = quotient_hidden_law_model(
        exact_hidden_law_bisimulation(detailed)
    )
    noisy_observation = hidden_law_model(
        exact_quotient.source_laws,
        exact_quotient.initial_belief,
        exact_quotient.transition,
        RationalObservationChannel.from_values(
            (
                (Fraction(7, 10), Fraction(3, 10)),
                (Fraction(1, 4), Fraction(3, 4)),
            )
        ),
    )
    certificate = exact_approximate_hidden_law_comparison(
        _complete_graph(3),
        detailed,
        noisy_observation,
        ((0, 1), (2,)),
        3,
        switching_penalty=0,
    )
    assert certificate.valid
    assert certificate.maximum_stage_deviation == 0
    assert certificate.maximum_transition_tv == 0
    assert certificate.no_signal_divergence_bound == 0
    assert certificate.oracle_value_bound == 0
    assert certificate.observed_divergence_bound > 0
    assert certificate.no_signal_value_bound == 0
    assert certificate.observed_value_bound > 0


def test_invalid_partitions_and_signal_alphabets_are_rejected():
    detailed = _approximate_model()
    abstract = representative_approximate_quotient(
        detailed,
        ((0, 1), (2,)),
    )
    with pytest.raises(ValueError):
        exact_approximate_hidden_law_comparison(
            _complete_graph(3),
            detailed,
            abstract,
            ((0,), (1,)),
            2,
        )

    incompatible = hidden_law_model(
        abstract.source_laws,
        abstract.initial_belief,
        abstract.transition,
        RationalObservationChannel.from_values(
            (
                (Fraction(1, 3),) * 3,
                (Fraction(1, 3),) * 3,
            )
        ),
    )
    with pytest.raises(ValueError):
        exact_approximate_hidden_law_comparison(
            _complete_graph(3),
            detailed,
            incompatible,
            ((0, 1), (2,)),
            2,
        )
