"""Walsh-Fourier certificates for uniform-prior Boolean experiment value.

For g=(-1)^f on the uniform Boolean cube, observing coordinates S projects g
onto Walsh characters supported inside S:

    h_S = E[g | X_S] = sum_{T subset S} ghat(T) chi_T.

The Bayesian K3 benchmark gap from ``bayesian_boolean_experiments`` is

    V(S) = (1 - E|h_S|)/2.

Parseval gives W(S)=E[h_S^2]=sum_{T subset S} ghat(T)^2.  Since |h_S| <= 1,

    W(S) <= E|h_S|,

and Cauchy-Schwarz gives

    (E|h_S|)^2 <= W(S).

Thus every exact rational certificate obeys

    (1-2V(S))^2 <= W(S) <= 1-2V(S).

The familiar square-root bounds follow without requiring irrational arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Mapping, Sequence

from .bayesian_boolean_experiments import (
    bayesian_boolean_gap,
    uniform_boolean_influence,
    uniform_boolean_prior,
)


def _bit_count(table: Sequence[int]) -> int:
    count = len(tuple(table))
    if count < 1 or count & (count - 1):
        raise ValueError("truth-table length must be a positive power of two")
    return count.bit_length() - 1


def _subsets(bit_count: int):
    return tuple(
        subset
        for size in range(bit_count + 1)
        for subset in combinations(range(bit_count), size)
    )


def _bit(index: int, coordinate: int, bit_count: int) -> int:
    return (index >> (bit_count - 1 - coordinate)) & 1


def walsh_character(index: int, subset: Sequence[int], bit_count: int) -> int:
    parity = sum(_bit(index, coordinate, bit_count) for coordinate in subset) & 1
    return -1 if parity else 1


def boolean_walsh_coefficients(truth_table: Sequence[int]) -> dict[tuple[int, ...], Fraction]:
    table = tuple(int(value) for value in truth_table)
    bit_count = _bit_count(table)
    if any(value not in (0, 1) for value in table):
        raise ValueError("truth table must be binary")
    scale = Fraction(1, len(table))
    result: dict[tuple[int, ...], Fraction] = {}
    for subset in _subsets(bit_count):
        result[subset] = scale * sum(
            ((-1 if table[x] else 1) * walsh_character(x, subset, bit_count) for x in range(len(table))),
            0,
        )
    return result


def captured_spectral_weight(
    coefficients: Mapping[tuple[int, ...], Fraction],
    observed: Sequence[int],
) -> Fraction:
    selected = set(int(i) for i in observed)
    return sum(
        (Fraction(value) ** 2 for subset, value in coefficients.items() if set(subset).issubset(selected)),
        Fraction(0),
    )


@dataclass(frozen=True)
class FourierExperimentCertificate:
    observed: tuple[int, ...]
    bayes_gap: Fraction
    absolute_bias: Fraction
    captured_weight: Fraction
    lower_slack: Fraction
    upper_slack: Fraction

    @property
    def valid(self) -> bool:
        return (
            0 <= self.bayes_gap <= Fraction(1, 2)
            and self.absolute_bias == 1 - 2 * self.bayes_gap
            and 0 <= self.captured_weight <= 1
            and self.lower_slack == self.captured_weight - self.absolute_bias**2
            and self.upper_slack == self.absolute_bias - self.captured_weight
            and self.lower_slack >= 0
            and self.upper_slack >= 0
        )


def exact_fourier_experiment_certificate(
    truth_table: Sequence[int],
    observed: Sequence[int],
) -> FourierExperimentCertificate:
    table = tuple(int(value) for value in truth_table)
    bit_count = _bit_count(table)
    selected = tuple(sorted(set(int(i) for i in observed)))
    if any(i < 0 or i >= bit_count for i in selected):
        raise ValueError("observed coordinate outside Boolean cube")
    coefficients = boolean_walsh_coefficients(table)
    gap = bayesian_boolean_gap(table, uniform_boolean_prior(bit_count), selected)
    absolute_bias = 1 - 2 * gap
    weight = captured_spectral_weight(coefficients, selected)
    result = FourierExperimentCertificate(
        selected,
        gap,
        absolute_bias,
        weight,
        weight - absolute_bias**2,
        absolute_bias - weight,
    )
    if not result.valid:
        raise AssertionError("Fourier experiment certificate failed validation")
    return result


def spectral_influence(truth_table: Sequence[int], coordinate: int) -> Fraction:
    table = tuple(int(value) for value in truth_table)
    bit_count = _bit_count(table)
    i = int(coordinate)
    if not 0 <= i < bit_count:
        raise ValueError("coordinate outside Boolean cube")
    coefficients = boolean_walsh_coefficients(table)
    return sum(
        (value**2 for subset, value in coefficients.items() if i in subset),
        Fraction(0),
    )


def exact_parseval_mass(truth_table: Sequence[int]) -> Fraction:
    return sum((value**2 for value in boolean_walsh_coefficients(truth_table).values()), Fraction(0))


def influence_identity_holds(truth_table: Sequence[int], coordinate: int) -> bool:
    return spectral_influence(truth_table, coordinate) == uniform_boolean_influence(truth_table, coordinate)
