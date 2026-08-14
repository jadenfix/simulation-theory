"""Exact finite block source coding for complete-confusion product sources.

One-shot expected prefix length and asymptotic coding rate are different
resources.  For a complete confusion graph every source state requires a
distinct zero-error message.  For an i.i.d. block of length m, every state
sequence therefore remains a distinct message and has product probability.

This module constructs that product law exactly and runs the existing exact
rational Huffman solver.  For block law P^m,

    H(P^m) <= L_H(P^m) < H(P^m) + 1

under positive support, hence

    H(P) <= L_H(P^m)/m < H(P) + 1/m.

The finite implementation does not claim a general graph-entropy theorem for
non-complete confusion graphs; the relevant graph product depends on the
multi-letter observation/side-information model and must be declared first.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import log2
from typing import Sequence

from .prior_weighted_codes import PrefixCodeCertificate, RationalInput, optimal_binary_prefix_code


def _fraction(value: RationalInput | Fraction) -> Fraction:
    if isinstance(value, float):
        raise ValueError("block probabilities must be exact rational values")
    return value if isinstance(value, Fraction) else Fraction(value)


def validate_probability_vector(probabilities: Sequence[RationalInput]) -> tuple[Fraction, ...]:
    p = tuple(_fraction(value) for value in probabilities)
    if not p or any(value < 0 for value in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("probabilities must form an exact finite distribution")
    return p


def product_distribution(
    probabilities: Sequence[RationalInput],
    block_length: int,
    *,
    max_sequences: int = 1_000_000,
) -> tuple[Fraction, ...]:
    p = validate_probability_vector(probabilities)
    m = int(block_length)
    if m < 1:
        raise ValueError("block_length must be positive")
    sequence_count = len(p) ** m
    if sequence_count > int(max_sequences):
        raise ValueError("product source exceeds configured sequence cap")
    return tuple(
        _product_probability(p, sequence)
        for sequence in product(range(len(p)), repeat=m)
    )


def _product_probability(p: Sequence[Fraction], sequence: Sequence[int]) -> Fraction:
    value = Fraction(1)
    for symbol in sequence:
        value *= p[symbol]
    return value


def entropy_bits(probabilities: Sequence[Fraction]) -> float:
    return -sum(float(p) * log2(float(p)) for p in probabilities if p > 0)


@dataclass(frozen=True)
class BlockPrefixCodeCertificate:
    source_prior: tuple[Fraction, ...]
    block_length: int
    block_prior: tuple[Fraction, ...]
    huffman: PrefixCodeCertificate
    source_entropy_bits: float
    block_entropy_bits: float
    per_symbol_expected_length: Fraction
    redundancy_per_symbol_bits: float
    one_over_block_length: Fraction

    @property
    def full_support(self) -> bool:
        return all(probability > 0 for probability in self.source_prior)

    @property
    def valid(self) -> bool:
        m = self.block_length
        return (
            m >= 1
            and bool(self.source_prior)
            and all(value >= 0 for value in self.source_prior)
            and sum(self.source_prior, Fraction(0)) == 1
            and len(self.block_prior) == len(self.source_prior) ** m
            and sum(self.block_prior, Fraction(0)) == 1
            and self.huffman.valid
            and self.huffman.probabilities == self.block_prior
            and self.per_symbol_expected_length == self.huffman.expected_length / m
            and self.one_over_block_length == Fraction(1, m)
            and abs(self.block_entropy_bits - m * self.source_entropy_bits) < 1e-10
            and abs(
                self.redundancy_per_symbol_bits
                - (float(self.per_symbol_expected_length) - self.source_entropy_bits)
            ) < 1e-12
            and self.redundancy_per_symbol_bits >= -1e-12
            and (
                not self.full_support
                or self.redundancy_per_symbol_bits < 1 / m + 1e-12
            )
        )


def exact_iid_block_prefix_code(
    probabilities: Sequence[RationalInput],
    block_length: int,
    *,
    max_sequences: int = 1_000_000,
) -> BlockPrefixCodeCertificate:
    p = validate_probability_vector(probabilities)
    m = int(block_length)
    block = product_distribution(p, m, max_sequences=max_sequences)
    huffman = optimal_binary_prefix_code(block)
    source_entropy = entropy_bits(p)
    block_entropy = entropy_bits(block)
    per_symbol = huffman.expected_length / m
    certificate = BlockPrefixCodeCertificate(
        p,
        m,
        block,
        huffman,
        source_entropy,
        block_entropy,
        per_symbol,
        float(per_symbol) - source_entropy,
        Fraction(1, m),
    )
    if not certificate.valid:
        raise AssertionError("block prefix-code certificate failed validation")
    return certificate
