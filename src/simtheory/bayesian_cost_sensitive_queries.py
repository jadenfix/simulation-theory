"""Exact cost-sensitive adaptive Boolean query stopping.

At posterior cell C with h queries remaining, the controller may stop and pay
Bayesian terminal gap L(C), or pay query cost c_i and recurse after observing
coordinate i.  This separates immediate experiment value from future option
value under exact rational costs.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Sequence

from .bayesian_boolean_experiments import uniform_boolean_prior


def _bit_count(table: Sequence[int]) -> int:
    n = len(tuple(table))
    if n < 1 or n & (n - 1):
        raise ValueError("truth-table length must be a positive power of two")
    return n.bit_length() - 1


def _bit(index: int, coordinate: int, bit_count: int) -> int:
    return (index >> (bit_count - 1 - coordinate)) & 1


@dataclass(frozen=True)
class CostSensitiveQueryNode:
    cell: tuple[int, ...]
    remaining: int
    stop_loss: Fraction
    value: Fraction
    selected_coordinate: int | None


@dataclass(frozen=True)
class CostSensitiveQueryCertificate:
    bit_count: int
    budget: int
    query_costs: tuple[Fraction, ...]
    value: Fraction
    root_coordinate: int | None
    nodes: tuple[CostSensitiveQueryNode, ...]

    @property
    def valid(self) -> bool:
        return (
            self.bit_count >= 0
            and self.budget >= 0
            and len(self.query_costs) == self.bit_count
            and all(cost >= 0 for cost in self.query_costs)
            and self.value >= 0
            and bool(self.nodes)
            and self.nodes[0].remaining == self.budget
            and self.nodes[0].value == self.value
            and self.nodes[0].selected_coordinate == self.root_coordinate
        )


def exact_cost_sensitive_boolean_query_design(
    truth_table: Sequence[int],
    query_costs: Sequence[Fraction],
    budget: int,
    prior: Sequence[Fraction] | None = None,
) -> CostSensitiveQueryCertificate:
    table = tuple(int(v) for v in truth_table)
    k = _bit_count(table)
    if any(v not in (0, 1) for v in table):
        raise ValueError("truth table must be binary")
    costs = tuple(Fraction(c) for c in query_costs)
    if len(costs) != k or any(c < 0 for c in costs):
        raise ValueError("query costs must be nonnegative and match bit count")
    h0 = int(budget)
    if h0 < 0:
        raise ValueError("budget must be nonnegative")
    p = uniform_boolean_prior(k) if prior is None else tuple(Fraction(x) for x in prior)
    if len(p) != len(table) or any(x < 0 for x in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("invalid prior")

    records: dict[tuple[tuple[int, ...], int], CostSensitiveQueryNode] = {}

    def cell_mass(cell: tuple[int, ...]) -> Fraction:
        return sum((p[x] for x in cell), Fraction(0))

    def stop_loss(cell: tuple[int, ...]) -> Fraction:
        mass = cell_mass(cell)
        if mass == 0:
            return Fraction(0)
        m0 = sum((p[x] for x in cell if table[x] == 0), Fraction(0))
        return min(m0, mass - m0) / mass

    @lru_cache(maxsize=None)
    def solve(cell: tuple[int, ...], remaining: int) -> Fraction:
        stop = stop_loss(cell)
        best = stop
        selected = None
        if remaining > 0 and stop > 0:
            mass = cell_mass(cell)
            for i in range(k):
                left = tuple(x for x in cell if _bit(x, i, k) == 0)
                right = tuple(x for x in cell if _bit(x, i, k) == 1)
                if not left or not right:
                    continue
                left_mass = cell_mass(left)
                right_mass = mass - left_mass
                continuation = Fraction(0)
                if left_mass:
                    continuation += left_mass / mass * solve(left, remaining - 1)
                if right_mass:
                    continuation += right_mass / mass * solve(right, remaining - 1)
                candidate = costs[i] + continuation
                if candidate < best or (candidate == best and selected is not None and i < selected):
                    best = candidate
                    selected = i
        records[(cell, remaining)] = CostSensitiveQueryNode(cell, remaining, stop, best, selected)
        return best

    root = tuple(range(len(table)))
    value = solve(root, h0)
    root_node = records[(root, h0)]
    nodes = (root_node,) + tuple(
        node for node in sorted(records.values(), key=lambda n: (-n.remaining, len(n.cell), n.cell))
        if node != root_node
    )
    result = CostSensitiveQueryCertificate(k, h0, costs, value, root_node.selected_coordinate, nodes)
    if not result.valid:
        raise AssertionError("cost-sensitive query certificate failed validation")
    return result
