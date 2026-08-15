"""Exact Bayesian experiment geometry for Boolean decision-relevant sources.

A hidden model is a bit string x in {0,1}^k with a declared rational prior.  The
future source symbol is the Boolean value f(x).  Deterministic experiment i
reveals coordinate x_i.  For a selected subset S, observation cells are the
fibers of x -> x_S.

On complete confusion K3 with only two source symbols used, the model-informed
oracle always gives the realized symbol the one-bit leaf.  Inside one posterior
cell C, an uninformed Bayesian controller puts the one-bit leaf on the more
probable Boolean output.  Its excess expected length over the oracle is exactly

    min(P(C,f=0), P(C,f=1)).

Hence the global Bayesian benchmark gap is the sum of minority masses across
observation cells.  Under the uniform prior and g=(-1)^f this is

    V(S) = (1 - E | E[g | X_S] |) / 2.

If every coordinate except i is observed, each remaining cell is a two-point
edge of the Boolean cube and V([k]\{i}) = Influence_i(f)/2 exactly.

These are finite exact decision identities.  They do not turn a supplied prior
into empirical evidence and they are not evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable, Mapping, Sequence


def _subsets(bit_count: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        subset
        for size in range(bit_count + 1)
        for subset in combinations(range(bit_count), size)
    )


def _bits(index: int, bit_count: int) -> tuple[int, ...]:
    return tuple((index >> (bit_count - 1 - j)) & 1 for j in range(bit_count))


def _validate_truth_table(values: Sequence[int]) -> tuple[int, tuple[int, ...]]:
    table = tuple(int(value) for value in values)
    if not table or any(value not in (0, 1) for value in table):
        raise ValueError("truth table must be a nonempty binary sequence")
    count = len(table)
    if count & (count - 1):
        raise ValueError("truth-table length must be a power of two")
    return count.bit_length() - 1, table


def _validate_prior(prior: Sequence[Fraction], count: int) -> tuple[Fraction, ...]:
    result = tuple(Fraction(value) for value in prior)
    if len(result) != count or any(value < 0 for value in result):
        raise ValueError("prior has wrong size or a negative mass")
    if sum(result, Fraction(0)) != 1:
        raise ValueError("prior must sum to one")
    return result


def uniform_boolean_prior(bit_count: int) -> tuple[Fraction, ...]:
    if bit_count < 0:
        raise ValueError("bit count must be nonnegative")
    count = 1 << bit_count
    return (Fraction(1, count),) * count


def observation_cells(bit_count: int, subset: Iterable[int]) -> tuple[tuple[int, ...], ...]:
    selected = tuple(sorted(set(int(i) for i in subset)))
    if any(i < 0 or i >= bit_count for i in selected):
        raise ValueError("observed coordinate outside Boolean cube")
    by_signature: dict[tuple[int, ...], list[int]] = {}
    for index in range(1 << bit_count):
        bits = _bits(index, bit_count)
        signature = tuple(bits[i] for i in selected)
        by_signature.setdefault(signature, []).append(index)
    return tuple(tuple(group) for _, group in sorted(by_signature.items()))


def bayesian_boolean_gap(
    truth_table: Sequence[int],
    prior: Sequence[Fraction],
    observed: Iterable[int],
) -> Fraction:
    bit_count, table = _validate_truth_table(truth_table)
    weights = _validate_prior(prior, len(table))
    total = Fraction(0)
    for cell in observation_cells(bit_count, observed):
        mass0 = sum((weights[i] for i in cell if table[i] == 0), Fraction(0))
        mass1 = sum((weights[i] for i in cell if table[i] == 1), Fraction(0))
        total += min(mass0, mass1)
    return total


def uniform_boolean_influence(truth_table: Sequence[int], coordinate: int) -> Fraction:
    bit_count, table = _validate_truth_table(truth_table)
    i = int(coordinate)
    if not 0 <= i < bit_count:
        raise ValueError("coordinate outside Boolean cube")
    mask = 1 << (bit_count - 1 - i)
    disagreements = sum(table[x] != table[x ^ mask] for x in range(len(table)))
    return Fraction(disagreements, len(table))


def essential_coordinates(truth_table: Sequence[int]) -> tuple[int, ...]:
    bit_count, _ = _validate_truth_table(truth_table)
    return tuple(i for i in range(bit_count) if uniform_boolean_influence(truth_table, i) > 0)


def boolean_mobius_transform(
    values: Mapping[tuple[int, ...], Fraction],
    bit_count: int,
) -> dict[tuple[int, ...], Fraction]:
    all_subsets = _subsets(bit_count)
    normalized = {tuple(sorted(key)): Fraction(value) for key, value in values.items()}
    if set(normalized) != set(all_subsets):
        raise ValueError("value map must contain every coordinate subset exactly once")
    result: dict[tuple[int, ...], Fraction] = {}
    for subset in all_subsets:
        subset_set = set(subset)
        coefficient = Fraction(0)
        for inner in all_subsets:
            if set(inner).issubset(subset_set):
                coefficient += (-1) ** (len(subset) - len(inner)) * normalized[inner]
        result[subset] = coefficient
    return result


def boolean_zeta_reconstruct(
    coefficients: Mapping[tuple[int, ...], Fraction],
    bit_count: int,
) -> dict[tuple[int, ...], Fraction]:
    all_subsets = _subsets(bit_count)
    normalized = {tuple(sorted(key)): Fraction(value) for key, value in coefficients.items()}
    if set(normalized) != set(all_subsets):
        raise ValueError("coefficient map must contain every subset exactly once")
    return {
        subset: sum(
            (normalized[inner] for inner in all_subsets if set(inner).issubset(subset)),
            Fraction(0),
        )
        for subset in all_subsets
    }


@dataclass(frozen=True)
class BayesianBooleanGeometry:
    bit_count: int
    truth_table: tuple[int, ...]
    prior: tuple[Fraction, ...]
    subset_values: tuple[tuple[tuple[int, ...], Fraction], ...]
    mobius: tuple[tuple[tuple[int, ...], Fraction], ...]

    @property
    def values(self) -> dict[tuple[int, ...], Fraction]:
        return dict(self.subset_values)

    @property
    def coefficients(self) -> dict[tuple[int, ...], Fraction]:
        return dict(self.mobius)

    @property
    def valid(self) -> bool:
        subsets = _subsets(self.bit_count)
        values = self.values
        coeffs = self.coefficients
        return (
            len(self.truth_table) == 1 << self.bit_count
            and len(self.prior) == len(self.truth_table)
            and sum(self.prior, Fraction(0)) == 1
            and set(values) == set(subsets)
            and set(coeffs) == set(subsets)
            and all(values[a] >= values[b] for a in subsets for b in subsets if set(a).issubset(b))
            and boolean_zeta_reconstruct(coeffs, self.bit_count) == values
        )


def exact_bayesian_boolean_geometry(
    truth_table: Sequence[int],
    prior: Sequence[Fraction] | None = None,
) -> BayesianBooleanGeometry:
    bit_count, table = _validate_truth_table(truth_table)
    weights = uniform_boolean_prior(bit_count) if prior is None else _validate_prior(prior, len(table))
    subsets = _subsets(bit_count)
    values = {subset: bayesian_boolean_gap(table, weights, subset) for subset in subsets}
    coefficients = boolean_mobius_transform(values, bit_count)
    result = BayesianBooleanGeometry(
        bit_count,
        table,
        weights,
        tuple((subset, values[subset]) for subset in subsets),
        tuple((subset, coefficients[subset]) for subset in subsets),
    )
    if not result.valid:
        raise AssertionError("Bayesian Boolean geometry failed validation")
    return result
