from fractions import Fraction

import pytest

from simtheory.belief_state_coding import hidden_law_model
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.hidden_law_bisimulation import (
    aggregate_hidden_belief,
    exact_hidden_law_bisimulation,
    exact_hidden_law_quotient_values,
    initial_label_partition,
    partition_is_hidden_law_bisimulation,
    quotient_hidden_law_model,
    refine_hidden_law_partition,
    transition_signature,
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


def _mergeable_model():
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


def test_partition_refinement_merges_internal_transition_variants_with_equal_block_mass():
    model = _mergeable_model()
    initial = initial_label_partition(model)
    assert initial == ((0, 1), (2,))
    assert transition_signature(model, 0, initial) == (
        Fraction(3, 4),
        Fraction(1, 4),
    )
    assert transition_signature(model, 1, initial) == (
        Fraction(3, 4),
        Fraction(1, 4),
    )
    assert refine_hidden_law_partition(model, initial) == initial

    certificate = exact_hidden_law_bisimulation(model)
    assert certificate.valid
    assert certificate.partition == ((0, 1), (2,))
    assert certificate.quotient_state_count == 2
    assert certificate.state_reduction == 1
    assert partition_is_hidden_law_bisimulation(model, certificate.partition)


def test_quotient_model_aggregates_initial_mass_and_transition_classes_exactly():
    certificate = exact_hidden_law_bisimulation(_mergeable_model())
    quotient = quotient_hidden_law_model(certificate)
    assert quotient.initial_belief == (Fraction(1, 2), Fraction(1, 2))
    assert quotient.transition == (
        (Fraction(3, 4), Fraction(1, 4)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    assert quotient.source_laws == (
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
    )
    assert quotient.observation.matrix == (
        (Fraction(3, 4), Fraction(1, 4)),
        (Fraction(1, 4), Fraction(3, 4)),
    )
    assert aggregate_hidden_belief(
        (Fraction(1, 10), Fraction(2, 5), Fraction(1, 2)),
        certificate.partition,
    ) == (Fraction(1, 2), Fraction(1, 2))


def test_original_and_quotient_preserve_all_declared_coding_values():
    result = exact_hidden_law_quotient_values(
        _complete_graph(3),
        _mergeable_model(),
        3,
        switching_penalty=Fraction(1, 4),
    )
    assert result.valid
    assert result.bisimulation.partition == ((0, 1), (2,))
    assert result.original.no_signal_value == result.quotient.no_signal_value
    assert result.original.observed_value == result.quotient.observed_value
    assert result.original.perfect_value == result.quotient.perfect_value
    assert (
        result.original.clairvoyant_expected_value
        == result.quotient.clairvoyant_expected_value
    )


def test_equal_labels_but_different_class_transition_mass_are_split():
    model = hidden_law_model(
        (
            (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
            (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
            (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
        ),
        (Fraction(1, 3),) * 3,
        (
            (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)),
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
    assert initial_label_partition(model) == ((0, 1), (2,))
    certificate = exact_hidden_law_bisimulation(model)
    assert certificate.valid
    assert certificate.partition == ((0,), (1,), (2,))
    assert certificate.refinement_trace == (
        ((0, 1), (2,)),
        ((0,), (1,), (2,)),
    )


def test_source_or_observation_label_difference_prevents_initial_merging():
    model = hidden_law_model(
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(3, 4), Fraction(1, 4)),
        ),
        (Fraction(1, 3),) * 3,
        (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
        ),
        RationalObservationChannel.from_values(
            (
                (Fraction(1, 2), Fraction(1, 2)),
                (Fraction(2, 3), Fraction(1, 3)),
                (Fraction(1, 2), Fraction(1, 2)),
            )
        ),
    )
    assert initial_label_partition(model) == ((0,), (1,), (2,))
    assert exact_hidden_law_bisimulation(model).partition == ((0,), (1,), (2,))


def test_invalid_partitions_and_beliefs_are_rejected():
    model = _mergeable_model()
    assert not partition_is_hidden_law_bisimulation(model, ((0, 1),))
    with pytest.raises(ValueError):
        aggregate_hidden_belief((Fraction(1, 2), Fraction(1, 2)), ((0,), (1,), (2,)))
