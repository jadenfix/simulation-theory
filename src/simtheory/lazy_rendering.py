from __future__ import annotations

from collections import defaultdict
from math import ceil, log2
from typing import Hashable, Mapping, Sequence

History = tuple[Hashable, ...]


def predictive_equivalence_classes(future_distributions: Mapping[History, Sequence[float]]) -> dict[tuple[float, ...], list[History]]:
    groups: dict[tuple[float, ...], list[History]] = defaultdict(list)
    for history, distribution in future_distributions.items():
        if any(p < 0.0 for p in distribution) or abs(sum(distribution) - 1.0) > 1e-10:
            raise ValueError("future law must be a probability distribution")
        groups[tuple(round(float(p), 14) for p in distribution)].append(history)
    return dict(groups)


def minimum_exact_state_count(future_distributions: Mapping[History, Sequence[float]]) -> int:
    return len(predictive_equivalence_classes(future_distributions))


def minimum_exact_memory_bits(future_distributions: Mapping[History, Sequence[float]]) -> int:
    states = minimum_exact_state_count(future_distributions)
    return 0 if states <= 1 else ceil(log2(states))
