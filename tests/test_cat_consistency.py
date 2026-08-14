from itertools import product
from math import isclose

import pytest

from simtheory.cat_consistency import (
    CatConsistencyState,
    block_cat_full_transcript_tv,
    block_cat_marginal_tv,
    block_cat_x_transcript_law,
    brute_force_checkpoint_tv,
    cat_x_marginal_law,
    cat_x_marginal_total_variation,
    cat_x_transcript_law,
    checkpoint_average_query_memory_lower_bound_bits,
    checkpoint_exact_memory_bits,
    checkpoint_exact_predictive_state_count,
    checkpoint_signature,
    checkpoint_total_variation,
    checkpoint_worst_query_memory_lower_bound_bits,
    prefix_parity_vectors,
)


def test_single_cat_transcript_is_uniform_on_one_parity_class():
    for phase in (0, 1):
        law = cat_x_transcript_law(phase, 5)
        positive = [outcomes for outcomes, probability in law.items() if probability > 0.0]
        assert len(positive) == 2**4
        assert isclose(sum(law.values()), 1.0, abs_tol=1e-12)
        target = 1 if phase == 0 else -1
        assert all(__import__("math").prod(outcomes) == target for outcomes in positive)
        assert all(isclose(law[outcomes], 2.0**-4) for outcomes in positive)


def test_every_proper_x_marginal_is_uniform_and_phase_blind():
    block_size = 5
    for positions in ((0,), (1, 3), (0, 1, 2, 4)):
        plus = cat_x_marginal_law(0, block_size, positions)
        minus = cat_x_marginal_law(1, block_size, positions)
        assert plus == minus
        assert len(plus) == 2 ** len(positions)
        assert all(isclose(probability, 2.0 ** (-len(positions))) for probability in plus.values())
        assert cat_x_marginal_total_variation(0, 1, block_size, positions) == 0.0

    full = tuple(range(block_size))
    assert cat_x_marginal_total_variation(0, 1, block_size, full) == 1.0


def test_multiblock_complete_transcripts_are_disjoint_but_partial_views_are_blind():
    left = (0, 0)
    right = (1, 1)
    block_size = 3
    law = block_cat_x_transcript_law(left, block_size)
    assert isclose(sum(law.values()), 1.0, abs_tol=1e-12)
    assert sum(probability > 0.0 for probability in law.values()) == 2 ** (2 * (block_size - 1))
    assert block_cat_full_transcript_tv(left, right) == 1.0

    # Five of the six physical outcomes are visible, but neither differing
    # block is completely observed, so the labels remain indistinguishable.
    assert block_cat_marginal_tv(left, right, block_size, (0, 1, 3, 4)) == 0.0
    assert block_cat_marginal_tv(left, right, block_size, (0, 1, 2, 3, 4)) == 1.0


def test_checkpoint_geometry_is_normalized_hamming_on_required_final_outcomes():
    label = (0, 1, 0, 1)
    left_prefix = (1, 1, -1, -1)
    right_prefix = (-1, 1, 1, -1)
    left_signature = checkpoint_signature(label, left_prefix)
    right_signature = checkpoint_signature(label, right_prefix)
    assert sum(a != b for a, b in zip(left_signature, right_signature)) == 2
    assert isclose(checkpoint_total_variation(label, left_prefix, label, right_prefix), 0.5)
    assert isclose(brute_force_checkpoint_tv(label, left_prefix, label, right_prefix), 0.5)


def test_checkpoint_has_exactly_two_to_the_m_predictive_classes():
    for blocks in range(1, 8):
        label = tuple(0 for _ in range(blocks))
        signatures = {checkpoint_signature(label, parity) for parity in prefix_parity_vectors(blocks)}
        assert len(signatures) == checkpoint_exact_predictive_state_count(blocks)
        assert checkpoint_exact_memory_bits(blocks) == blocks
        assert checkpoint_worst_query_memory_lower_bound_bits(blocks, 0.499) == blocks
        assert checkpoint_worst_query_memory_lower_bound_bits(blocks, 0.5) == 0


def test_average_query_constant_tolerance_keeps_linear_memory():
    assert checkpoint_average_query_memory_lower_bound_bits(100, 0.05) >= 55


def test_explicit_renderer_state_is_a_tight_parity_sufficient_statistic():
    label = (0, 1)
    block_size = 4
    state = CatConsistencyState.initial(2)

    # The first ell-1 outcomes in a block are unbiased.
    assert state.next_outcome_law(label, 0, block_size) == {-1: 0.5, 1: 0.5}
    for outcome in (1, -1, -1):
        state = state.observe(0, outcome, block_size)

    # Prefix parity is +1, while phase bit zero requires total parity +1.
    assert state.parities[0] == 1
    assert state.next_outcome_law(label, 0, block_size) == {-1: 0.0, 1: 1.0}

    for outcome in (-1, 1, 1):
        state = state.observe(1, outcome, block_size)
    # Prefix parity is -1 and phase bit one requires total parity -1,
    # so the final outcome must be +1.
    assert state.next_outcome_law(label, 1, block_size) == {-1: 0.0, 1: 1.0}


def test_validation_rejects_invalid_cat_inputs():
    with pytest.raises(ValueError):
        cat_x_transcript_law(0, 1)
    with pytest.raises(ValueError):
        block_cat_x_transcript_law((0, 1), 11, max_qubits=20)
    with pytest.raises(ValueError):
        CatConsistencyState.initial(0)
