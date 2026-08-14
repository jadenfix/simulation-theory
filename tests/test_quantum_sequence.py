from math import isclose, pi

from simtheory.quantum_sequence import (
    PhaseProcess,
    constant_policy,
    greedy_transcript_packing,
    parity_adaptive_policy,
    phase_hypothesis_processes,
    transcript_law,
    transcript_memory_lower_bound_bits,
    transcript_total_variation,
)


def test_zero_horizon_is_point_mass():
    process = PhaseProcess(0.7, 0.2, 0.1)
    assert transcript_law(process, 0, constant_policy((0, 0))) == {(): 1.0}


def test_transcript_law_normalizes():
    process = PhaseProcess(0.8, -0.4, 0.3)
    for horizon in range(1, 5):
        law = transcript_law(process, horizon, parity_adaptive_policy())
        assert isclose(sum(law.values()), 1.0, abs_tol=1e-12)
        assert len(law) <= 4**horizon


def test_identical_processes_have_zero_tv():
    process = PhaseProcess(0.9, 0.5, -0.2)
    for horizon in range(5):
        assert isclose(
            transcript_total_variation(process, process, horizon, parity_adaptive_policy()),
            0.0,
            abs_tol=1e-12,
        )


def test_transcript_tv_is_nondecreasing_with_horizon_for_fixed_process_pair():
    left = PhaseProcess(0.85, -0.8, 0.17)
    right = PhaseProcess(0.85, 0.6, 0.17)
    policy = parity_adaptive_policy()
    values = [transcript_total_variation(left, right, h, policy) for h in range(5)]
    for a, b in zip(values, values[1:]):
        assert b + 1e-12 >= a


def test_phase_drift_wraps_without_changing_equivalent_process():
    left = PhaseProcess(0.6, 0.2, 0.4)
    right = PhaseProcess(0.6, 0.2 + 2 * pi, 0.4 + 2 * pi)
    assert isclose(
        transcript_total_variation(left, right, 4, parity_adaptive_policy()),
        0.0,
        abs_tol=1e-12,
    )


def test_greedy_transcript_packing_is_pairwise_certified():
    phases = tuple(-pi + 2 * pi * j / 12 for j in range(12))
    processes = phase_hypothesis_processes(0.9, phases, 0.15)
    epsilon = 0.04
    policy = parity_adaptive_policy()
    packing = greedy_transcript_packing(processes, 3, epsilon, policy)
    for i, left in enumerate(packing):
        for right in packing[i + 1 :]:
            assert transcript_total_variation(left, right, 3, policy) > 2 * epsilon


def test_memory_bound_covers_packing_size():
    phases = tuple(-pi + 2 * pi * j / 16 for j in range(16))
    processes = phase_hypothesis_processes(0.8, phases, 0.11)
    policy = parity_adaptive_policy()
    packing = greedy_transcript_packing(processes, 3, 0.05, policy)
    bits = transcript_memory_lower_bound_bits(processes, 3, 0.05, policy)
    assert 2**bits >= len(packing)
