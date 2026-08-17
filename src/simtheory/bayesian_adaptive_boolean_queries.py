"""Exact adaptive coordinate-query design for Bayesian Boolean coding loss.

A state is the posterior support cell induced by previous deterministic coordinate
queries.  Because query outcomes are deterministic functions of the hidden bit
string, the cell itself is a sufficient statistic: query order can be forgotten.
For a remaining query budget h, Bellman recursion compares stopping now with
querying any coordinate that strictly splits the current cell.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Sequence

from .bayesian_boolean_experiments import bayesian_boolean_gap, uniform_boolean_prior


def _bit_count(table: Sequence[int]) -> int:
    n = len(tuple(table))
    if n < 1 or n & (n - 1):
        raise ValueError("truth-table length must be a positive power of two")
    return n.bit_length() - 1


def _bit(index: int, coordinate: int, bit_count: int) -> int:
    return (index >> (bit_count - 1 - coordinate)) & 1


def _validate_prior(prior: Sequence[Fraction], count: int) -> tuple[Fraction, ...]:
    p = tuple(Fraction(x) for x in prior)
    if len(p) != count or any(x < 0 for x in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("invalid prior")
    return p


@dataclass(frozen=True)
class AdaptiveQueryNode:
    cell: tuple[int, ...]
    remaining: int
    value: Fraction
    selected_coordinate: int | None
    stop_value: Fraction


@dataclass(frozen=True)
class AdaptiveBooleanQueryCertificate:
    bit_count: int
    truth_table: tuple[int, ...]
    prior: tuple[Fraction, ...]
    budget: int
    adaptive_value: Fraction
    nonadaptive_value: Fraction
    adaptivity_gain: Fraction
    root_coordinate: int | None
    nodes: tuple[AdaptiveQueryNode, ...]

    @property
    def valid(self) -> bool:
        return (
            self.budget >= 0
            and self.adaptive_value >= 0
            and self.nonadaptive_value >= self.adaptive_value
            and self.adaptivity_gain == self.nonadaptive_value - self.adaptive_value
            and bool(self.nodes)
            and self.nodes[0].cell == tuple(range(len(self.truth_table)))
            and self.nodes[0].remaining == self.budget
            and self.nodes[0].value == self.adaptive_value
            and self.nodes[0].selected_coordinate == self.root_coordinate
        )


def exact_adaptive_boolean_query_design(
    truth_table: Sequence[int],
    budget: int,
    prior: Sequence[Fraction] | None = None,
) -> AdaptiveBooleanQueryCertificate:
    table = tuple(int(v) for v in truth_table)
    k = _bit_count(table)
    if any(v not in (0, 1) for v in table):
        raise ValueError("truth table must be binary")
    h0 = int(budget)
    if h0 < 0:
        raise ValueError("budget must be nonnegative")
    p = uniform_boolean_prior(k) if prior is None else _validate_prior(prior, len(table))

    records: dict[tuple[tuple[int, ...], int], AdaptiveQueryNode] = {}

    def stop_value(cell: tuple[int, ...]) -> Fraction:
        mass = sum((p[x] for x in cell), Fraction(0))
        if mass == 0:
            return Fraction(0)
        m0 = sum((p[x] for x in cell if table[x] == 0), Fraction(0))
        m1 = mass - m0
        return min(m0, m1) / mass

    @lru_cache(maxsize=None)
    def solve(cell: tuple[int, ...], remaining: int) -> Fraction:
        stop = stop_value(cell)
        best = stop
        best_coordinate = None
        if remaining > 0 and stop > 0:
            mass = sum((p[x] for x in cell), Fraction(0))
            for i in range(k):
                left = tuple(x for x in cell if _bit(x, i, k) == 0)
                right = tuple(x for x in cell if _bit(x, i, k) == 1)
                if not left or not right:
                    continue
                left_mass = sum((p[x] for x in left), Fraction(0))
                right_mass = mass - left_mass
                value = Fraction(0)
                if left_mass:
                    value += left_mass / mass * solve(left, remaining - 1)
                if right_mass:
                    value += right_mass / mass * solve(right, remaining - 1)
                if value < best or (value == best and best_coordinate is not None and i < best_coordinate):
                    best = value
                    best_coordinate = i
        records[(cell, remaining)] = AdaptiveQueryNode(cell, remaining, best, best_coordinate, stop)
        return best

    root = tuple(range(len(table)))
    adaptive = solve(root, h0)

    nonadaptive = min(
        bayesian_boolean_gap(table, p, subset)
        for size in range(min(k, h0) + 1)
        for subset in combinations(range(k), size)
    )
    ordered_nodes = tuple(
        sorted(records.values(), key=lambda r: (-r.remaining, len(r.cell), r.cell))
    )
    root_node = records[(root, h0)]
    result = AdaptiveBooleanQueryCertificate(
        k, table, p, h0, adaptive, nonadaptive, nonadaptive - adaptive,
        root_node.selected_coordinate, (root_node,) + tuple(n for n in ordered_nodes if n != root_node)
    )
    if not result.valid:
        raise AssertionError("adaptive Boolean query certificate failed validation")
    return result
