from fractions import Fraction
from itertools import combinations
from math import isclose

import pytest

from simtheory.stochastic_channels import (
    FiniteOutcomeChannel,
    apply_query_outcome_channels,
    channel_chain_certificate,
    channel_chain_dobrushin_product_fraction,
    channel_contraction_certificate,
    compose_channel_chain,
    exhaustive_distribution_grid,
    predictive_complexity_contraction_certificate,
    query_channel_contraction_certificate,
    total_variation_fraction,
)
from simtheory.stochastic_predictive import (
    FiniteStochasticQueryFamily,
    single_bernoulli_query_family,
    weighted_query_total_variation,
)


def test_identity_bsc_and_erasure_coefficients_are_exact():
    identity = FiniteOutcomeChannel.identity((0, 1, 2))
    assert identity.dobrushin_coefficient_fraction == 1

    bsc = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 5))
    assert bsc.dobrushin_coefficient_fraction == Fraction(3, 5)

    erasure = FiniteOutcomeChannel.erasure(
        ("a", "b", "c"),
        Fraction(1, 4),
    )
    assert erasure.dobrushin_coefficient_fraction == Fraction(3, 4)


def test_bsc_contraction_is_tight_on_opposite_deterministic_inputs():
    channel = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 5))
    certificate = channel_contraction_certificate((1, 0), (0, 1), channel)
    assert certificate.before == 1
    assert certificate.after == Fraction(3, 5)
    assert certificate.upper_bound == Fraction(3, 5)
    assert certificate.slack == 0
    assert certificate.valid


def test_dobrushin_contraction_exhaustively_on_rational_grid():
    channel = FiniteOutcomeChannel(
        ("a", "b", "c"),
        (0, 1),
        (
            (Fraction(9, 10), Fraction(1, 10)),
            (Fraction(3, 5), Fraction(2, 5)),
            (Fraction(2, 5), Fraction(3, 5)),
        ),
    )
    assert channel.dobrushin_coefficient_fraction == Fraction(1, 2)
    grid = exhaustive_distribution_grid(3, 6)
    for left, right in combinations(grid, 2):
        certificate = channel_contraction_certificate(left, right, channel)
        assert certificate.valid
        assert certificate.after <= Fraction(1, 2) * certificate.before


def test_serial_channel_coefficient_is_submultiplicative():
    first = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 10))
    second = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 5))
    composed = compose_channel_chain((first, second))
    # Two BSCs compose to q = q1 + q2 - 2 q1 q2 = 13/50.
    assert composed.rows == (
        (Fraction(37, 50), Fraction(13, 50)),
        (Fraction(13, 50), Fraction(37, 50)),
    )
    assert composed.dobrushin_coefficient_fraction == Fraction(12, 25)
    assert channel_chain_dobrushin_product_fraction((first, second)) == Fraction(12, 25)
    certificate = channel_chain_certificate((first, second))
    assert certificate.valid
    assert certificate.composed_coefficient == certificate.product_bound


def test_composition_can_contract_more_than_product_bound():
    first = FiniteOutcomeChannel(
        (0, 1, 2),
        (0, 1, 2),
        (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
        ),
    )
    second = FiniteOutcomeChannel(
        (0, 1, 2),
        (0, 1),
        (
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
            (Fraction(1, 2), Fraction(1, 2)),
        ),
    )
    third = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 4))
    certificate = channel_chain_certificate((first, second, third))
    assert certificate.valid
    assert certificate.composed_coefficient <= certificate.product_bound


def test_querywise_contraction_uses_each_channel_coefficient():
    family = FiniteStochasticQueryFamily(
        ("left", "right"),
        ("q0", "q1"),
        ((0, 1), (0, 1)),
        (
            ((1.0, 0.0), (0.9, 0.1)),
            ((0.0, 1.0), (0.2, 0.8)),
        ),
    )
    channels = (
        FiniteOutcomeChannel.binary_symmetric(Fraction(1, 5)),
        FiniteOutcomeChannel.binary_symmetric(Fraction(2, 5)),
    )
    certificate = query_channel_contraction_certificate(
        family,
        "left",
        "right",
        channels,
        (Fraction(1, 4), Fraction(3, 4)),
    )
    assert certificate.valid
    assert certificate.before == Fraction(31, 40)
    assert certificate.after == Fraction(51, 200)
    assert certificate.querywise_bound == Fraction(51, 200)
    assert certificate.global_bound == Fraction(93, 200)

    transformed = apply_query_outcome_channels(family, channels)
    assert isclose(
        weighted_query_total_variation(
            transformed,
            "left",
            "right",
            (0.25, 0.75),
        ),
        float(certificate.after),
        abs_tol=1e-12,
    )


def test_complete_randomization_collapses_predictive_classes():
    family = single_bernoulli_query_family(
        (0.0, 0.2, 0.8, 1.0),
        ("a", "b", "c", "d"),
    )
    randomizer = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 2))
    transformed = apply_query_outcome_channels(family, (randomizer,))
    assert family.exact_class_count == 4
    assert transformed.exact_class_count == 1
    assert transformed.exact_predictive_bits == 0
    for left, right in combinations(transformed.records, 2):
        assert weighted_query_total_variation(transformed, left, right) == 0.0


def test_packing_and_target_cover_cannot_grow_after_postprocessing():
    family = single_bernoulli_query_family(
        tuple(index / 10 for index in range(11))
    )
    channel = FiniteOutcomeChannel.binary_symmetric(Fraction(1, 5))
    certificate = predictive_complexity_contraction_certificate(
        family,
        (channel,),
        0.12,
        max_records=20,
    )
    assert certificate.valid
    assert certificate.after_exact_classes <= certificate.before_exact_classes
    assert certificate.after_packing <= certificate.before_packing
    assert certificate.after_target_cover <= certificate.before_target_cover


def test_erasure_pushforward_and_data_processing():
    channel = FiniteOutcomeChannel.erasure(
        ("red", "blue"),
        Fraction(1, 3),
        erasure_outcome="lost",
    )
    assert channel.pushforward_fraction((Fraction(1, 4), Fraction(3, 4))) == (
        Fraction(1, 6),
        Fraction(1, 2),
        Fraction(1, 3),
    )
    certificate = channel_contraction_certificate((1, 0), (0, 1), channel)
    assert certificate.after == Fraction(2, 3)
    assert certificate.upper_bound == Fraction(2, 3)


def test_total_variation_canonicalizes_decimal_inputs():
    assert total_variation_fraction((0.1, 0.9), (0.4, 0.6)) == Fraction(3, 10)
    # Positive vectors are canonicalized to distributions, so harmless common
    # scaling cannot change the theorem input.
    assert total_variation_fraction((1, 9), (4, 6)) == Fraction(3, 10)


def test_validation_rejects_invalid_channels_and_interfaces():
    with pytest.raises(ValueError):
        FiniteOutcomeChannel((0, 0), (0, 1), ((1, 0), (0, 1)))
    with pytest.raises(ValueError):
        FiniteOutcomeChannel.binary_symmetric(Fraction(3, 5))
    with pytest.raises(ValueError):
        FiniteOutcomeChannel.erasure((0, 1), Fraction(1, 2), erasure_outcome=1)
    with pytest.raises(ValueError):
        FiniteOutcomeChannel((0, 1), (0, 1), ((0, 0), (0, 1)))
    with pytest.raises(ValueError):
        compose_channel_chain(())
    with pytest.raises(ValueError):
        apply_query_outcome_channels(
            single_bernoulli_query_family((0.0, 1.0)),
            (FiniteOutcomeChannel.identity(("wrong", "alphabet")),),
        )
