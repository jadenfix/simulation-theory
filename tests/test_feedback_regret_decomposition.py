from fractions import Fraction

from simtheory.confusion_graphs import ConfusionGraph
from simtheory.feedback_regret_decomposition import decompose_feedback_regret
from simtheory.feedback_regret_solver import exact_drift_information_regret


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


def test_deterministic_information_values_telescope_exactly():
    certificate = exact_drift_information_regret(
        _complete_graph(3),
        (Fraction(1, 3),) * 3,
        3,
        Fraction(1, 3),
        2,
        switching_penalty=Fraction(1, 4),
    )
    decomposition = decompose_feedback_regret(certificate)
    assert decomposition.valid
    assert decomposition.deterministic_total == certificate.open_loop_value
    assert decomposition.delayed_feedback_value >= 0
    assert decomposition.current_law_timing_value >= 0
    assert decomposition.future_foresight_value >= 0
    assert decomposition.shared_open_loop_randomization_value >= 0


def test_zero_drift_eliminates_every_information_and_randomization_value():
    certificate = exact_drift_information_regret(
        _complete_graph(3),
        (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
        10,
        0,
        2,
        switching_penalty=Fraction(1, 4),
    )
    decomposition = decompose_feedback_regret(certificate)
    assert decomposition.valid
    assert decomposition.delayed_feedback_value == 0
    assert decomposition.current_law_timing_value == 0
    assert decomposition.future_foresight_value == 0
    assert decomposition.shared_open_loop_randomization_value == 0
