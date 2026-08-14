"""Closed shared-randomness solution for complete graphs at full TV radius.

For K_n every source state needs its own zero-error message.  At TV radius one,
the source law may concentrate on any state.  A shared codebook mixture is
therefore judged by the largest expected state depth.

The exact value is the minimum uniform-source binary prefix length:

    b + 1 - 2^b / n,  where b = ceil(log2 n).

A cyclic mixture of at most n near-balanced complete trees makes every state's
expected depth equal to this value.  The lower bound follows because the
maximum coordinate of any mixed depth vector is at least its average and every
deterministic n-leaf prefix tree has average depth at least the uniform Huffman
optimum.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from .robust_prior_codes import (
    CompletePrefixShape,
    canonical_codewords_from_lengths,
)


def _ceil_log2_integer(value: int) -> int:
    integer = int(value)
    if integer != value or integer < 1:
        raise ValueError("state count must be a positive integer")
    return 0 if integer == 1 else (integer - 1).bit_length()


@dataclass(frozen=True)
class FullTVCompleteGraphCertificate:
    state_count: int
    fixed_length_bits: int
    short_depth: int
    long_depth: int
    short_leaf_count: int
    long_leaf_count: int
    minimum_total_leaf_depth: int
    shared_value: Fraction
    deterministic_value: int
    cyclic_shapes: tuple[CompletePrefixShape, ...]
    cyclic_weights: tuple[Fraction, ...]
    mixed_state_lengths: tuple[Fraction, ...]

    @property
    def randomization_gain(self) -> Fraction:
        return Fraction(self.deterministic_value) - self.shared_value

    @property
    def symmetric_support_size(self) -> int:
        return len(self.cyclic_shapes)

    @property
    def all_permutation_support_size(self) -> int:
        if self.short_leaf_count in (0, self.state_count):
            return 1
        return comb(self.state_count, self.short_leaf_count)

    @property
    def valid(self) -> bool:
        n = self.state_count
        b = self.fixed_length_bits
        return (
            n >= 1
            and b == _ceil_log2_integer(n)
            and self.deterministic_value == b
            and self.short_depth == max(0, b - 1)
            and self.long_depth == b
            and self.short_leaf_count == (0 if n == 1 else (1 << b) - n)
            and self.long_leaf_count == n - self.short_leaf_count
            and self.minimum_total_leaf_depth
            == self.short_leaf_count * self.short_depth
            + self.long_leaf_count * self.long_depth
            and self.shared_value
            == Fraction(self.minimum_total_leaf_depth, n)
            and self.shared_value
            == Fraction(b + 1) - Fraction(1 << b, n)
            if n > 1
            else self.shared_value == 0
        ) and (
            bool(self.cyclic_shapes)
            and len(self.cyclic_weights) == len(self.cyclic_shapes)
            and all(weight >= 0 for weight in self.cyclic_weights)
            and sum(self.cyclic_weights, Fraction(0)) == 1
            and all(shape.valid and shape.message_count == n for shape in self.cyclic_shapes)
            and self.mixed_state_lengths
            == tuple(
                sum(
                    (
                        weight * shape.lengths[state]
                        for weight, shape in zip(
                            self.cyclic_weights,
                            self.cyclic_shapes,
                        )
                    ),
                    Fraction(0),
                )
                for state in range(n)
            )
            and self.mixed_state_lengths == (self.shared_value,) * n
            and self.randomization_gain
            == Fraction((1 << b) - n, n)
            if n > 1
            else self.randomization_gain == 0
        )


def full_tv_complete_graph_certificate(
    state_count: int,
) -> FullTVCompleteGraphCertificate:
    """Return the exact full-TV shared-randomness value for K_n."""

    n = int(state_count)
    if n != state_count or n < 1:
        raise ValueError("state_count must be a positive integer")
    b = _ceil_log2_integer(n)
    if n == 1:
        shapes = (CompletePrefixShape((0,), ("",), Fraction(1)),)
        weights = (Fraction(1),)
        certificate = FullTVCompleteGraphCertificate(
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            Fraction(0),
            0,
            shapes,
            weights,
            (Fraction(0),),
        )
        if not certificate.valid:
            raise AssertionError("one-state full-TV certificate failed")
        return certificate

    short_count = (1 << b) - n
    long_count = n - short_count
    short_depth = b - 1
    long_depth = b
    base_lengths = tuple(
        [short_depth] * short_count + [long_depth] * long_count
    )
    if short_count == 0:
        length_vectors = (base_lengths,)
    else:
        length_vectors = tuple(
            tuple(base_lengths[(state - shift) % n] for state in range(n))
            for shift in range(n)
        )
    shapes = tuple(
        CompletePrefixShape(
            lengths,
            canonical_codewords_from_lengths(lengths),
            sum(
                (Fraction(1, 1 << length) for length in lengths),
                Fraction(0),
            ),
        )
        for lengths in length_vectors
    )
    weights = (Fraction(1, len(shapes)),) * len(shapes)
    total_depth = short_count * short_depth + long_count * long_depth
    shared_value = Fraction(total_depth, n)
    mixed = tuple(
        sum(
            (
                weight * shape.lengths[state]
                for weight, shape in zip(weights, shapes)
            ),
            Fraction(0),
        )
        for state in range(n)
    )
    certificate = FullTVCompleteGraphCertificate(
        n,
        b,
        short_depth,
        long_depth,
        short_count,
        long_count,
        total_depth,
        shared_value,
        b,
        shapes,
        weights,
        mixed,
    )
    if not certificate.valid:
        raise AssertionError("full-TV complete-graph certificate failed")
    return certificate
