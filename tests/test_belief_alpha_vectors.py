from fractions import Fraction

from simtheory.belief_alpha_vectors import (
    alpha_value,
    exact_belief_alpha_vector_certificate,
    posterior_martingale_identity,
)
from simtheory.belief_state_coding import (
    exact_belief_state_prefix_coding,
    hidden_law_model,
)
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.observation_channel_value import symmetric_observation_channel


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


def _model():
    return hidden_law_model(
        (
            (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10)),
            (Fraction(1, 10), Fraction(4, 5), Fraction(1, 10)),
        ),
        (Fraction(1, 2), Fraction(1, 2)),
        (
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
        ),
        symmetric_observation_channel(2, Fraction(3, 4)),
    )


def test_policy_tree_alpha_vectors_reproduce_every_reachable_bellman_value():
    coding = exact_belief_state_prefix_coding(
        _complete_graph(3),
        _model(),
        2,
        switching_penalty=Fraction(1, 4),
    )
    certificate = exact_belief_alpha_vector_certificate(coding)
    assert certificate.valid
    assert all(entry.valid for entry in certificate.no_signal_families)
    assert all(entry.valid for entry in certificate.observed_families)


def test_minimum_of_alpha_vectors_is_concave_on_exact_rational_mixtures():
    coding = exact_belief_state_prefix_coding(
        _complete_graph(3),
        _model(),
        2,
        switching_penalty=Fraction(1, 4),
    )
    certificate = exact_belief_alpha_vector_certificate(coding)
    family = {
        (entry.remaining_horizon, entry.previous_code): entry.vectors
        for entry in certificate.observed_families
    }[(2, -1)]

    left = (Fraction(1), Fraction(0))
    right = (Fraction(0), Fraction(1))
    midpoint = (Fraction(1, 2), Fraction(1, 2))
    left_value = min(alpha_value(left, vector) for vector in family)
    right_value = min(alpha_value(right, vector) for vector in family)
    midpoint_value = min(alpha_value(midpoint, vector) for vector in family)
    assert midpoint_value >= Fraction(1, 2) * (left_value + right_value)


def test_posterior_belief_and_predicted_belief_are_exact_martingales():
    model = _model()
    belief = (Fraction(2, 5), Fraction(3, 5))
    posterior_mean, predicted_mean = posterior_martingale_identity(belief, model)
    assert posterior_mean == belief
    assert predicted_mean == (
        Fraction(9, 20),
        Fraction(11, 20),
    )
