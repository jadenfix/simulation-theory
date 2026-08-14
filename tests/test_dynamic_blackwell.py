from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.dynamic_blackwell import exact_dynamic_blackwell_comparison
from simtheory.observation_channel_value import identity_observation_channel


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


def test_identity_signal_dominates_symmetric_garbling_dynamically():
    certificate = exact_dynamic_blackwell_comparison(
        _complete_graph(3),
        _source_laws(),
        (Fraction(1, 2), Fraction(1, 2)),
        (
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
        ),
        identity_observation_channel(2),
        (
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
        ),
        3,
        switching_penalty=Fraction(1, 3),
    )
    assert certificate.valid
    assert certificate.richer.observed_value == certificate.richer.perfect_value
    assert certificate.richer.observed_value <= certificate.poorer.observed_value
    assert certificate.observed_information_gain >= 0


def test_complete_garbling_reduces_to_no_signal_value():
    certificate = exact_dynamic_blackwell_comparison(
        _complete_graph(3),
        _source_laws(),
        (Fraction(1, 2), Fraction(1, 2)),
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(1, 2), Fraction(1, 2)),
        ),
        identity_observation_channel(2),
        (
            (Fraction(1, 3), Fraction(2, 3)),
            (Fraction(1, 3), Fraction(2, 3)),
        ),
        2,
        switching_penalty=Fraction(1, 4),
    )
    assert certificate.valid
    assert certificate.poorer.model.observation_is_uninformative
    assert certificate.poorer.observed_value == certificate.poorer.no_signal_value
    assert certificate.richer.no_signal_value == certificate.poorer.no_signal_value
