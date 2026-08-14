from __future__ import annotations

from collections import defaultdict
from math import exp2
from typing import Hashable, Iterable


def prefix_weight(program_length_bits: int) -> float:
    if program_length_bits < 0:
        raise ValueError("program length must be nonnegative")
    return exp2(-program_length_bits)


def raw_program_mass(programs: Iterable[tuple[int, Hashable]]) -> float:
    return sum(prefix_weight(length) for length, _ in programs)


def observational_class_mass(programs: Iterable[tuple[int, Hashable]]) -> dict[Hashable, float]:
    masses: dict[Hashable, float] = defaultdict(float)
    for length, observable_law in programs:
        masses[observable_law] += prefix_weight(length)
    return dict(masses)


def shortest_description_mass(programs: Iterable[tuple[int, Hashable]]) -> dict[Hashable, float]:
    shortest: dict[Hashable, int] = {}
    for length, observable_law in programs:
        if length < 0:
            raise ValueError("program length must be nonnegative")
        shortest[observable_law] = min(length, shortest.get(observable_law, length))
    return {law: prefix_weight(length) for law, length in shortest.items()}


def multiplicity_inflation(programs: Iterable[tuple[int, Hashable]]) -> dict[Hashable, float]:
    xs = list(programs)
    summed = observational_class_mass(xs)
    shortest = shortest_description_mass(xs)
    return {law: summed[law] / shortest[law] for law in summed}


def kraft_sum(program_lengths_bits: Iterable[int]) -> float:
    """Kraft sum for a proposed binary prefix-code length multiset."""
    lengths = list(program_lengths_bits)
    if any(length < 0 for length in lengths):
        raise ValueError("program lengths must be nonnegative")
    return sum(prefix_weight(length) for length in lengths)


def kraft_admissible(program_lengths_bits: Iterable[int], tolerance: float = 1e-12) -> bool:
    """Necessary and sufficient length condition for some binary prefix code."""
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")
    return kraft_sum(program_lengths_bits) <= 1.0 + tolerance


def normalized_observational_prior(
    programs: Iterable[tuple[int, Hashable]],
) -> dict[Hashable, float]:
    """Normalize raw prefix weights after aggregating observational classes.

    This still depends on the chosen coding language and program list. It only
    prevents counting each implementation as a separate *observable law* in the
    returned support.
    """
    masses = observational_class_mass(programs)
    total = sum(masses.values())
    if total <= 0.0:
        raise ValueError("program set must have positive total mass")
    return {law: mass / total for law, mass in masses.items()}
