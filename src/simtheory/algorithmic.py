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
