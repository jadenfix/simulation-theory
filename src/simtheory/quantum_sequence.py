"""Finite adaptive quantum phase-drift transcript laws.

A latent state starts at (visibility, initial_phase). After each Bell trial the
phase advances by a fixed drift omega. A deterministic policy may choose the
next allowed setting pair from the complete observed outcome history.

This bounded model connects the static visibility+phase geometry to the
repository's adaptive-rendering question: how many distinct evolving predictive
states remain distinguishable from finite internal transcripts?
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2
from typing import Callable, Iterable, Sequence

from .bell_predictive import BellSchedule, CANONICAL_CHSH
from .quantum_phase import PhaseState, conditional_outcome_law, wrap_phase

Outcome = tuple[int, int]
History = tuple[Outcome, ...]
SettingIndex = tuple[int, int]
Policy = Callable[[History], SettingIndex]


@dataclass(frozen=True)
class PhaseProcess:
    visibility: float
    initial_phase: float
    phase_drift: float

    def phase_at(self, step: int) -> float:
        if step < 0:
            raise ValueError("step must be nonnegative")
        return wrap_phase(self.initial_phase + step * self.phase_drift)


def constant_policy(setting: SettingIndex) -> Policy:
    def choose(_: History) -> SettingIndex:
        return setting
    return choose


def parity_adaptive_policy(
    first: SettingIndex = (0, 0),
    even: SettingIndex = (0, 1),
    odd: SettingIndex = (1, 0),
) -> Policy:
    """Example deterministic adaptive policy based on previous product parity."""
    def choose(history: History) -> SettingIndex:
        if not history:
            return first
        parity = 1
        for a, b in history:
            parity *= a * b
        return even if parity == 1 else odd
    return choose


def _validate_setting(setting: SettingIndex, schedule: BellSchedule) -> None:
    x, y = setting
    if not (0 <= x < len(schedule.alice_angles) and 0 <= y < len(schedule.bob_angles)):
        raise ValueError("policy returned a setting outside the schedule")


def transcript_law(
    process: PhaseProcess,
    horizon: int,
    policy: Policy,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> dict[History, float]:
    """Exact outcome-transcript law under a deterministic adaptive policy."""
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    if not 0.0 <= process.visibility <= 1.0:
        raise ValueError("visibility must lie in [0,1]")
    frontier: dict[History, float] = {(): 1.0}
    for step in range(horizon):
        phase = process.phase_at(step)
        next_frontier: dict[History, float] = {}
        for history, mass in frontier.items():
            setting = policy(history)
            _validate_setting(setting, schedule)
            x, y = setting
            law = conditional_outcome_law(
                process.visibility,
                phase,
                schedule.alice_angles[x],
                schedule.bob_angles[y],
            )
            for outcome, probability in law.items():
                extended = history + (outcome,)
                next_frontier[extended] = next_frontier.get(extended, 0.0) + mass * probability
        frontier = next_frontier
    return frontier


def transcript_total_variation(
    left: PhaseProcess,
    right: PhaseProcess,
    horizon: int,
    policy: Policy,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> float:
    p = transcript_law(left, horizon, policy, schedule)
    q = transcript_law(right, horizon, policy, schedule)
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def phase_hypothesis_processes(
    visibility: float,
    phases: Iterable[float],
    phase_drift: float,
) -> tuple[PhaseProcess, ...]:
    unique = sorted({wrap_phase(phi) for phi in phases})
    return tuple(PhaseProcess(float(visibility), phi, float(phase_drift)) for phi in unique)


def greedy_transcript_packing(
    processes: Sequence[PhaseProcess],
    horizon: int,
    epsilon: float,
    policy: Policy,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> tuple[PhaseProcess, ...]:
    """Certified 2*epsilon-separated packing in horizon transcript TV."""
    if epsilon < 0:
        raise ValueError("epsilon must be nonnegative")
    chosen: list[PhaseProcess] = []
    for process in processes:
        if all(
            transcript_total_variation(process, other, horizon, policy, schedule) > 2.0 * epsilon
            for other in chosen
        ):
            chosen.append(process)
    return tuple(chosen)


def transcript_memory_lower_bound_bits(
    processes: Sequence[PhaseProcess],
    horizon: int,
    epsilon: float,
    policy: Policy,
    schedule: BellSchedule = CANONICAL_CHSH,
) -> int:
    """Predictive-state bits certified by a finite adaptive transcript packing."""
    k = len(greedy_transcript_packing(processes, horizon, epsilon, policy, schedule))
    return 0 if k <= 1 else ceil(log2(k))
