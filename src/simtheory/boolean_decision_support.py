"""Boolean decision functions collapse to essential-variable support under worst-case K3 coding.

The observation-lattice layer might suggest that parity is special because its
value appears only at the highest experiment-interaction order.  Under the
specific worst-case K3 coding objective, a stronger and more nuanced statement
holds: the complete truth-table geometry collapses to the set of *essential
variables*.

Let f:{0,1}^k->{0,1}.  Model x is the bit string x, experiment j reveals bit
x_j, and the source law is a point mass at symbol f(x) of complete confusion
K3.  The model-informed oracle cost is one.  For experiment subset S:

* if S contains every essential variable of f, then f is determined in every
  observation cell and the benchmark gap is zero;
* otherwise choose an omitted essential variable j.  By essentiality there are
  inputs x and x xor e_j with opposite f-values.  They agree on every observed
  bit in S, so one observation cell contains both source symbols.  Deterministic
  worst-case gap is therefore one, while independent public mixing reduces the
  cell gap exactly to one-half.

Thus, for nonconstant f with essential-variable set E,

    D(S) = 1[E not subset S]
    M(S) = (1/2) 1[E not subset S].

Their Boolean Möbius transforms contain only a baseline coefficient and one
coefficient on E itself.  Interaction order is |E|, not Fourier degree or
algebraic degree.  For example three-bit AND and three-bit parity have identical
worst-case experiment-value lattices here despite radically different truth
tables.

This collapse is objective-specific.  Average-case/Bayesian experiment values
can retain much more of the truth-table geometry.  The distinction is recorded
explicitly to avoid overinterpreting the parity example.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import log2
from typing import Sequence

from .experiment_observation_lattice import (
    ObservationLatticeCertificate,
    deterministic_model_experiment,
    exact_observation_lattice_values,
)
from .confusion_graphs import ConfusionGraph


@dataclass(frozen=True)
class BooleanDecisionSupportCertificate:
    outputs: tuple[int, ...]
    bit_count: int
    essential_mask: int
    lattice: ObservationLatticeCertificate
    predicted_deterministic: tuple[Fraction, ...]
    predicted_mixed: tuple[Fraction, ...]
    predicted_deterministic_mobius: tuple[Fraction, ...]
    predicted_mixed_mobius: tuple[Fraction, ...]

    @property
    def essential_indices(self) -> tuple[int, ...]:
        return tuple(
            bit for bit in range(self.bit_count)
            if self.essential_mask & (1 << bit)
        )

    @property
    def valid(self) -> bool:
        if (
            self.bit_count < 1
            or len(self.outputs) != 1 << self.bit_count
            or any(value not in (0, 1) for value in self.outputs)
            or self.essential_mask < 0
            or self.essential_mask >= 1 << self.bit_count
            or self.lattice.experiment_count != self.bit_count
        ):
            return False
        actual_det = tuple(value.deterministic_gap for value in self.lattice.subset_values)
        actual_mix = tuple(value.mixed_gap for value in self.lattice.subset_values)
        return (
            actual_det == self.predicted_deterministic
            and actual_mix == self.predicted_mixed
            and self.lattice.deterministic_mobius == self.predicted_deterministic_mobius
            and self.lattice.mixed_mobius == self.predicted_mixed_mobius
        )


def _validate_truth_table(outputs: Sequence[int]) -> tuple[tuple[int, ...], int]:
    values = tuple(int(value) for value in outputs)
    if len(values) < 2 or len(values) & (len(values) - 1):
        raise ValueError("truth table length must be a power of two at least two")
    if any(value not in (0, 1) for value in values):
        raise ValueError("Boolean truth table outputs must be zero or one")
    return values, int(log2(len(values)))


def essential_variable_mask(outputs: Sequence[int]) -> int:
    values, bits = _validate_truth_table(outputs)
    mask = 0
    for bit in range(bits):
        step = 1 << bit
        if any(values[x] != values[x ^ step] for x in range(len(values)) if not x & step):
            mask |= step
    return mask


def predicted_worst_case_boolean_values(
    outputs: Sequence[int],
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    values, bits = _validate_truth_table(outputs)
    essential = essential_variable_mask(values)
    count = 1 << bits
    if essential == 0:
        zeros = tuple(Fraction(0) for _ in range(count))
        return zeros, zeros
    deterministic = tuple(
        Fraction(0) if mask & essential == essential else Fraction(1)
        for mask in range(count)
    )
    mixed = tuple(value / 2 for value in deterministic)
    return deterministic, mixed


def predicted_worst_case_boolean_mobius(
    outputs: Sequence[int],
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    values, bits = _validate_truth_table(outputs)
    essential = essential_variable_mask(values)
    count = 1 << bits
    deterministic = [Fraction(0) for _ in range(count)]
    mixed = [Fraction(0) for _ in range(count)]
    if essential:
        deterministic[0] = Fraction(1)
        deterministic[essential] = Fraction(-1)
        mixed[0] = Fraction(1, 2)
        mixed[essential] = Fraction(-1, 2)
    return tuple(deterministic), tuple(mixed)


def exact_boolean_decision_support(
    outputs: Sequence[int],
    *,
    max_game_bases: int = 2_000_000,
) -> BooleanDecisionSupportCertificate:
    values, bits = _validate_truth_table(outputs)
    graph = ConfusionGraph.from_edges((0, 1, 2), ((0, 1), (0, 2), (1, 2)))
    model_laws = tuple(
        tuple(
            Fraction(1) if symbol == output else Fraction(0)
            for symbol in range(3)
        )
        for output in values
    )
    experiments = tuple(
        deterministic_model_experiment(
            f"bit-{bit}",
            tuple((model >> bit) & 1 for model in range(len(values))),
        )
        for bit in range(bits)
    )
    lattice = exact_observation_lattice_values(
        graph,
        model_laws,
        experiments,
        max_experiments=max(12, bits),
        max_subsets=1 << bits,
        max_game_bases=max_game_bases,
    )
    deterministic, mixed = predicted_worst_case_boolean_values(values)
    det_mobius, mix_mobius = predicted_worst_case_boolean_mobius(values)
    result = BooleanDecisionSupportCertificate(
        values,
        bits,
        essential_variable_mask(values),
        lattice,
        deterministic,
        mixed,
        det_mobius,
        mix_mobius,
    )
    if not result.valid:
        raise AssertionError("Boolean essential-support certificate failed validation")
    return result
