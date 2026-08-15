from fractions import Fraction
from itertools import combinations

import pytest

from simtheory.active_experiment_complementarity import exact_active_experiment_complementarity
from simtheory.active_fixed_model_experiments import active_experiment
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.fixed_model_ambiguity import fixed_model_family, fixed_model_scenario
from simtheory.stochastic_observation_beliefs import bayesian_law_model, observation_kernel


def _complete_graph(count: int) -> ConfusionGraph:
    vertices = tuple(range(count))
    return ConfusionGraph.from_edges(vertices, tuple(combinations(vertices, 2)))


def _point_mass(symbol: int, count: int):
    return tuple(Fraction(1) if index == symbol else Fraction(0) for index in range(count))


def _two_bit_family():
    # Four fixed models are indexed by latent bits (a,b). Period 1 emits the
    # common source symbol 1. A deterministic hidden transition then moves to a
    # period-2 state whose source is 0,1,1,2 for models 00,01,10,11. Knowing one
    # bit narrows the final source to a two-symbol set; knowing both bits fixes it.
    final_symbols = (0, 1, 1, 2)
    scenarios = []
    no_signal = observation_kernel(((1,), (1,)))
    for model_index, final_symbol in enumerate(final_symbols):
        model = bayesian_law_model(
            (_point_mass(1, 3), _point_mass(final_symbol, 3)),
            ((0, 1), (0, 1)),
        )
        scenarios.append(
            fixed_model_scenario(
                f"m{model_index:02b}",
                model,
                no_signal,
                (1, 0),
            )
        )
    return fixed_model_family(tuple(scenarios))


def _none(family):
    return active_experiment(
        "none",
        tuple(observation_kernel(((1,), (1,))) for _ in family.scenarios),
    )


def _bit_experiment(family, bit_position: int, name: str):
    # bit_position 0 is the high bit, 1 the low bit. The observation is
    # deterministic from model identity and independent of hidden state.
    kernels = []
    for model_index in range(family.model_count):
        bit = (model_index >> (1 - bit_position)) & 1
        row = (Fraction(1), Fraction(0)) if bit == 0 else (Fraction(0), Fraction(1))
        kernels.append(observation_kernel((row, row)))
    return active_experiment(name, tuple(kernels))


def test_two_latent_bits_are_strictly_complementary_for_deterministic_regret():
    graph = _complete_graph(3)
    family = _two_bit_family()
    none = _none(family)
    bit_a = _bit_experiment(family, 0, "bit-a")
    bit_b = _bit_experiment(family, 1, "bit-b")

    result = exact_active_experiment_complementarity(
        graph, family, (none,), bit_a, bit_b, 2
    )
    assert result.valid
    assert result.benchmark == (2, 2, 2, 2)

    # Stage 1 is common and costs one. With no bit information, the second
    # period may be any of three K3 symbols, so deterministic minimax gap is one.
    assert result.baseline.deterministic_gap == 1

    # Either bit alone leaves two possible final symbols. A deterministic K3
    # code still has worst length two over that pair, so the gap remains one.
    assert result.with_a.deterministic_gap == 1
    assert result.with_b.deterministic_gap == 1

    # Together the two persistent observations identify the model before the
    # second code action, matching the model-informed oracle exactly.
    assert result.with_both.deterministic_gap == 0

    assert result.deterministic_gain_b_empty == 0
    assert result.deterministic_gain_b_after_a == 1
    assert result.deterministic_complementarity == 1
    assert result.deterministic_submodularity_slack == -1


def test_complementarity_survives_after_public_randomness_is_matched():
    graph = _complete_graph(3)
    family = _two_bit_family()
    result = exact_active_experiment_complementarity(
        graph,
        family,
        (_none(family),),
        _bit_experiment(family, 0, "bit-a"),
        _bit_experiment(family, 1, "bit-b"),
        2,
    )
    assert result.valid

    # With a free public seed and no information, K3's one-period minimax mixed
    # length is 5/3, hence two-period gap 2/3 relative to oracle cost two.
    assert result.baseline.mixed_gap == Fraction(2, 3)

    # One bit leaves a two-symbol future set. Mixing the short leaf uniformly
    # over those two symbols gives final expected length 3/2, hence gap 1/2.
    assert result.with_a.mixed_gap == Fraction(1, 2)
    assert result.with_b.mixed_gap == Fraction(1, 2)
    assert result.with_both.mixed_gap == 0

    assert result.mixed_gain_b_empty == Fraction(1, 6)
    assert result.mixed_gain_b_after_a == Fraction(1, 2)
    assert result.mixed_complementarity == Fraction(1, 3)
    assert result.mixed_submodularity_slack == -Fraction(1, 3)


def test_experiment_order_is_symmetric_in_the_exact_two_bit_example():
    graph = _complete_graph(3)
    family = _two_bit_family()
    none = _none(family)
    bit_a = _bit_experiment(family, 0, "bit-a")
    bit_b = _bit_experiment(family, 1, "bit-b")
    ab = exact_active_experiment_complementarity(graph, family, (none,), bit_a, bit_b, 2)
    ba = exact_active_experiment_complementarity(graph, family, (none,), bit_b, bit_a, 2)
    assert ab.valid and ba.valid
    assert ab.deterministic_complementarity == ba.deterministic_complementarity == 1
    assert ab.mixed_complementarity == ba.mixed_complementarity == Fraction(1, 3)


def test_candidate_experiments_must_have_new_distinct_names():
    graph = _complete_graph(3)
    family = _two_bit_family()
    none = _none(family)
    bit_a = _bit_experiment(family, 0, "bit-a")
    duplicate = _bit_experiment(family, 1, "bit-a")
    with pytest.raises(ValueError):
        exact_active_experiment_complementarity(graph, family, (none,), bit_a, duplicate, 2)
    with pytest.raises(ValueError):
        exact_active_experiment_complementarity(graph, family, (none,), none, bit_a, 2)
