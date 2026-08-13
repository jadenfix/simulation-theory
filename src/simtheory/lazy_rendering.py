"""Finite predictive-state and approximate lazy-rendering bounds.

The functions in this module concern observable transcript laws. They do not
assume that a simulator exists. A "renderer" is simply an online generator
whose next-output distribution may depend on the complete observable history.
"""

from __future__ import annotations

from collections import defaultdict
from math import ceil, log2, prod, sqrt
from typing import Hashable, Mapping, Sequence

History = tuple[Hashable, ...]
Distribution = Sequence[float]


def _validated_distribution(distribution: Distribution) -> tuple[float, ...]:
    xs = tuple(float(p) for p in distribution)
    if not xs or any(p < 0.0 for p in xs) or abs(sum(xs) - 1.0) > 1e-10:
        raise ValueError("future law must be a nonempty probability distribution")
    return xs


def finite_total_variation(p: Distribution, q: Distribution) -> float:
    p_tuple = _validated_distribution(p)
    q_tuple = _validated_distribution(q)
    if len(p_tuple) != len(q_tuple):
        raise ValueError("distributions must have equal support size")
    return 0.5 * sum(abs(a - b) for a, b in zip(p_tuple, q_tuple))


def predictive_equivalence_classes(
    future_distributions: Mapping[History, Distribution],
) -> dict[tuple[float, ...], list[History]]:
    """Group histories with exactly identical supplied next/future laws."""
    groups: dict[tuple[float, ...], list[History]] = defaultdict(list)
    for history, distribution in future_distributions.items():
        normalized = _validated_distribution(distribution)
        groups[normalized].append(history)
    return dict(groups)


def minimum_exact_state_count(future_distributions: Mapping[History, Distribution]) -> int:
    """Lower bound for an exact renderer whose future depends only on state."""
    return len(predictive_equivalence_classes(future_distributions))


def minimum_exact_memory_bits(future_distributions: Mapping[History, Distribution]) -> int:
    states = minimum_exact_state_count(future_distributions)
    return 0 if states <= 1 else ceil(log2(states))


def sequential_total_variation_bound(per_step_tv_bounds: Sequence[float]) -> float:
    """Coupling bound for an adaptive approximate renderer.

    If, whenever the two transcript prefixes still agree, the target and
    renderer next-answer laws have total variation at most ``epsilon_t``, then
    the complete transcript laws have total variation at most

        1 - product_t (1 - epsilon_t).

    The proof uses a maximal coupling at every step. The result remains valid
    for adaptive queries because the query at a matched prefix is the same in
    both coupled executions.
    """
    eps = [float(value) for value in per_step_tv_bounds]
    if any(value < 0.0 or value > 1.0 for value in eps):
        raise ValueError("per-step total-variation bounds must lie in [0,1]")
    return 1.0 - prod(1.0 - value for value in eps)


def sequential_union_bound(per_step_tv_bounds: Sequence[float]) -> float:
    """Simpler but weaker sum-of-errors transcript bound."""
    eps = [float(value) for value in per_step_tv_bounds]
    if any(value < 0.0 or value > 1.0 for value in eps):
        raise ValueError("per-step total-variation bounds must lie in [0,1]")
    return min(1.0, sum(eps))


def sequential_pinsker_bound(per_step_expected_kl_bounds: Sequence[float]) -> float:
    """Transcript-TV bound from the conditional KL chain rule and Pinsker.

    Inputs must upper-bound the target-law expectation of each conditional KL
    term. No independence assumption is required, but absolute continuity and
    correctness of the supplied KL bounds are external assumptions.
    """
    terms = [float(value) for value in per_step_expected_kl_bounds]
    if any(value < 0.0 for value in terms):
        raise ValueError("KL bounds must be nonnegative")
    return min(1.0, sqrt(0.5 * sum(terms)))


def transcript_distribution(
    conditional_tree: Mapping[tuple[int, ...], Distribution],
    horizon: int,
) -> dict[tuple[int, ...], float]:
    """Expand a finite adaptive conditional tree into its transcript law.

    Every prefix shorter than ``horizon`` must map to a distribution over the
    same finite response alphabet. Query adaptation can be folded into the
    prefix: at each prefix the policy has already selected the next query.
    """
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    frontier: dict[tuple[int, ...], float] = {(): 1.0}
    alphabet_size: int | None = None
    for _ in range(horizon):
        next_frontier: dict[tuple[int, ...], float] = {}
        for prefix, prefix_probability in frontier.items():
            if prefix not in conditional_tree:
                raise ValueError(f"missing conditional law for prefix {prefix!r}")
            law = _validated_distribution(conditional_tree[prefix])
            if alphabet_size is None:
                alphabet_size = len(law)
            elif len(law) != alphabet_size:
                raise ValueError("all conditional laws must use one response alphabet")
            for response, probability in enumerate(law):
                next_frontier[prefix + (response,)] = prefix_probability * probability
        frontier = next_frontier
    return frontier


def transcript_total_variation(
    target_tree: Mapping[tuple[int, ...], Distribution],
    renderer_tree: Mapping[tuple[int, ...], Distribution],
    horizon: int,
) -> float:
    target = transcript_distribution(target_tree, horizon)
    renderer = transcript_distribution(renderer_tree, horizon)
    keys = sorted(set(target) | set(renderer))
    return 0.5 * sum(abs(target.get(key, 0.0) - renderer.get(key, 0.0)) for key in keys)


def conditional_tv_profile(
    target_tree: Mapping[tuple[int, ...], Distribution],
    renderer_tree: Mapping[tuple[int, ...], Distribution],
    horizon: int,
) -> list[float]:
    """Worst conditional TV at each depth over common transcript prefixes."""
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    profile: list[float] = []
    prefixes: set[tuple[int, ...]] = {()}
    for _ in range(horizon):
        depth_max = 0.0
        next_prefixes: set[tuple[int, ...]] = set()
        for prefix in prefixes:
            if prefix not in target_tree or prefix not in renderer_tree:
                raise ValueError(f"missing conditional law for prefix {prefix!r}")
            p = _validated_distribution(target_tree[prefix])
            q = _validated_distribution(renderer_tree[prefix])
            if len(p) != len(q):
                raise ValueError("target and renderer alphabets must agree")
            depth_max = max(depth_max, finite_total_variation(p, q))
            next_prefixes.update(prefix + (response,) for response in range(len(p)))
        profile.append(depth_max)
        prefixes = next_prefixes
    return profile


def _maximum_clique_size(adjacency: Sequence[int]) -> int:
    """Exact bitset branch-and-bound maximum clique for small finite studies."""
    n = len(adjacency)
    if n == 0:
        return 0
    if n > 60:
        raise ValueError("exact packing search is capped at 60 histories")

    best = 0

    def expand(candidates: int, size: int) -> None:
        nonlocal best
        if size + candidates.bit_count() <= best:
            return
        while candidates:
            if size + candidates.bit_count() <= best:
                return
            bit = candidates & -candidates
            vertex = bit.bit_length() - 1
            candidates ^= bit
            expand(candidates & adjacency[vertex], size + 1)
        best = max(best, size)

    expand((1 << n) - 1, 0)
    return best


def approximate_state_packing_lower_bound(
    future_distributions: Mapping[History, Distribution],
    epsilon: float,
) -> int:
    """Exact finite packing lower bound for epsilon-accurate predictive state.

    If two target future laws are more than ``2*epsilon`` apart in total
    variation, one renderer state cannot approximate both within epsilon. The
    maximum size of a pairwise-separated subset is therefore a state-count
    lower bound. Computing this packing number is a maximum-clique problem, so
    this exact implementation is intentionally capped at 60 histories.
    """
    if epsilon < 0.0 or epsilon > 1.0:
        raise ValueError("epsilon must lie in [0,1]")
    laws = [_validated_distribution(law) for law in future_distributions.values()]
    if not laws:
        return 0
    support_size = len(laws[0])
    if any(len(law) != support_size for law in laws):
        raise ValueError("all future laws must use the same finite support")

    adjacency = [0] * len(laws)
    separation = 2.0 * epsilon
    for i in range(len(laws)):
        for j in range(i + 1, len(laws)):
            if finite_total_variation(laws[i], laws[j]) > separation + 1e-12:
                adjacency[i] |= 1 << j
                adjacency[j] |= 1 << i
    return _maximum_clique_size(adjacency)


def approximate_memory_bits_lower_bound(
    future_distributions: Mapping[History, Distribution],
    epsilon: float,
) -> int:
    states = approximate_state_packing_lower_bound(future_distributions, epsilon)
    return 0 if states <= 1 else ceil(log2(states))
