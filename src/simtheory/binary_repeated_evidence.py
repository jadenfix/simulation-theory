"""Exact sufficient statistics and parity plateaus for binary repeated evidence.

For two hidden scenarios and a binary symmetric observation channel with
accuracy ``a``, the likelihood pair of a complete history depends only on the
signed count

    S(h) = number_of_zeros - number_of_ones.

The ordered signal history can therefore be compressed to one integer for every
terminal decision whose loss depends on the hidden scenario only through the
likelihoods.

A second exact certificate proves the fair-tie majority identity

    B_(2m)(a) = B_(2m-1)(a).

The even observation is Blackwell-additional information, but its value for this
particular symmetric majority decision can be exactly zero.  This separates
informativeness of an experiment from strict value under one loss.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb
from typing import Sequence

from .prior_weighted_codes import RationalInput
from .repeated_observation_policies import binary_symmetric_majority_accuracy

ExactInput = RationalInput | Fraction | int
History = tuple[int, ...]


def _fraction(value: ExactInput, *, name: str) -> Fraction:
    if isinstance(value, float):
        raise ValueError(f"{name} must be exact rational input")
    try:
        return value if isinstance(value, Fraction) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid exact rational {name}") from error


def _validate_history(history: Sequence[int]) -> History:
    supplied = tuple(int(signal) for signal in history)
    if any(signal not in (0, 1) for signal in supplied):
        raise ValueError("binary histories may contain only zero and one")
    return supplied


def binary_signed_count(history: Sequence[int]) -> int:
    supplied = _validate_history(history)
    return sum(1 if signal == 0 else -1 for signal in supplied)


def binary_symmetric_history_likelihoods(
    correct_probability: ExactInput,
    history: Sequence[int],
) -> tuple[Fraction, Fraction]:
    """Return P(history|scenario 0) and P(history|scenario 1)."""

    correct = _fraction(correct_probability, name="correct_probability")
    if not Fraction(1, 2) <= correct <= 1:
        raise ValueError("correct_probability must lie in [1/2,1]")
    supplied = _validate_history(history)
    zeros = supplied.count(0)
    ones = len(supplied) - zeros
    wrong = Fraction(1) - correct
    return (
        correct**zeros * wrong**ones,
        wrong**zeros * correct**ones,
    )


def binary_symmetric_likelihood_ratio(
    correct_probability: ExactInput,
    history: Sequence[int],
) -> Fraction:
    """Return the exact scenario-0/scenario-1 likelihood ratio.

    The endpoint ``a=1`` is excluded because histories impossible under one
    scenario can have an infinite ratio, which is not a rational number.
    """

    correct = _fraction(correct_probability, name="correct_probability")
    if not Fraction(1, 2) <= correct < 1:
        raise ValueError("likelihood ratio requires correct_probability in [1/2,1)")
    exponent = binary_signed_count(history)
    base = correct / (Fraction(1) - correct)
    return base**exponent


@dataclass(frozen=True)
class BinaryLikelihoodClass:
    signed_count: int
    histories: tuple[History, ...]
    scenario_likelihoods: tuple[Fraction, Fraction]
    likelihood_ratio: Fraction


@dataclass(frozen=True)
class BinaryHistorySufficiencyCertificate:
    correct_probability: Fraction
    repetitions: int
    classes: tuple[BinaryLikelihoodClass, ...]
    histories_examined: int
    max_histories: int

    @property
    def valid(self) -> bool:
        if (
            not Fraction(1, 2) <= self.correct_probability < 1
            or self.repetitions < 0
            or self.histories_examined != 2**self.repetitions
            or self.histories_examined > self.max_histories
            or len({item.signed_count for item in self.classes}) != len(self.classes)
        ):
            return False
        all_histories = tuple(
            history for item in self.classes for history in item.histories
        )
        if (
            len(all_histories) != self.histories_examined
            or len(set(all_histories)) != self.histories_examined
            or set(all_histories)
            != set(product((0, 1), repeat=self.repetitions))
        ):
            return False
        for item in self.classes:
            if not item.histories:
                return False
            for history in item.histories:
                if (
                    binary_signed_count(history) != item.signed_count
                    or binary_symmetric_history_likelihoods(
                        self.correct_probability,
                        history,
                    )
                    != item.scenario_likelihoods
                    or binary_symmetric_likelihood_ratio(
                        self.correct_probability,
                        history,
                    )
                    != item.likelihood_ratio
                ):
                    return False
            base = self.correct_probability / (Fraction(1) - self.correct_probability)
            if item.likelihood_ratio != base**item.signed_count:
                return False
        return True


def exact_binary_history_sufficiency(
    correct_probability: ExactInput,
    repetitions: int,
    *,
    max_histories: int = 1_000_000,
) -> BinaryHistorySufficiencyCertificate:
    correct = _fraction(correct_probability, name="correct_probability")
    if not Fraction(1, 2) <= correct < 1:
        raise ValueError("correct_probability must lie in [1/2,1)")
    count = int(repetitions)
    if count != repetitions or count < 0:
        raise ValueError("repetitions must be a nonnegative integer")
    history_count = 2**count
    if history_count > int(max_histories):
        raise ValueError("binary history space exceeds configured cap")
    grouped: dict[int, list[History]] = {}
    for history in product((0, 1), repeat=count):
        grouped.setdefault(binary_signed_count(history), []).append(history)
    classes = tuple(
        BinaryLikelihoodClass(
            signed_count,
            tuple(histories),
            binary_symmetric_history_likelihoods(correct, histories[0]),
            binary_symmetric_likelihood_ratio(correct, histories[0]),
        )
        for signed_count, histories in sorted(grouped.items())
    )
    result = BinaryHistorySufficiencyCertificate(
        correct,
        count,
        classes,
        history_count,
        int(max_histories),
    )
    if not result.valid:
        raise AssertionError("binary history sufficiency certificate failed")
    return result


@dataclass(frozen=True)
class BinaryEvenPlateauCertificate:
    correct_probability: Fraction
    odd_repetitions: int
    even_repetitions: int
    boundary_lower_probability: Fraction
    boundary_upper_probability: Fraction
    tie_gain: Fraction
    tie_loss: Fraction
    odd_accuracy: Fraction
    even_accuracy: Fraction

    @property
    def valid(self) -> bool:
        m = (self.odd_repetitions + 1) // 2
        correct = self.correct_probability
        wrong = Fraction(1) - correct
        return (
            Fraction(1, 2) <= correct <= 1
            and self.odd_repetitions >= 1
            and self.odd_repetitions % 2 == 1
            and self.even_repetitions == self.odd_repetitions + 1
            and self.boundary_lower_probability
            == comb(self.odd_repetitions, m - 1)
            * correct ** (m - 1)
            * wrong**m
            and self.boundary_upper_probability
            == comb(self.odd_repetitions, m)
            * correct**m
            * wrong ** (m - 1)
            and self.tie_gain
            == correct * self.boundary_lower_probability / 2
            and self.tie_loss
            == wrong * self.boundary_upper_probability / 2
            and self.tie_gain == self.tie_loss
            and self.odd_accuracy
            == binary_symmetric_majority_accuracy(
                correct,
                self.odd_repetitions,
            )
            and self.even_accuracy
            == binary_symmetric_majority_accuracy(
                correct,
                self.even_repetitions,
            )
            and self.odd_accuracy == self.even_accuracy
        )


def exact_binary_even_plateau(
    correct_probability: ExactInput,
    odd_repetitions: int,
) -> BinaryEvenPlateauCertificate:
    correct = _fraction(correct_probability, name="correct_probability")
    if not Fraction(1, 2) <= correct <= 1:
        raise ValueError("correct_probability must lie in [1/2,1]")
    odd = int(odd_repetitions)
    if odd != odd_repetitions or odd < 1 or odd % 2 != 1:
        raise ValueError("odd_repetitions must be a positive odd integer")
    m = (odd + 1) // 2
    wrong = Fraction(1) - correct
    lower = comb(odd, m - 1) * correct ** (m - 1) * wrong**m
    upper = comb(odd, m) * correct**m * wrong ** (m - 1)
    result = BinaryEvenPlateauCertificate(
        correct,
        odd,
        odd + 1,
        lower,
        upper,
        correct * lower / 2,
        wrong * upper / 2,
        binary_symmetric_majority_accuracy(correct, odd),
        binary_symmetric_majority_accuracy(correct, odd + 1),
    )
    if not result.valid:
        raise AssertionError("binary even-sample plateau certificate failed")
    return result
