"""Evidence ceilings for one persistent latent-model draw.

Let a and b be two candidate mixing-weight vectors over latent model M.  A
single M is drawn once, then an arbitrary transcript Y is generated through a
common model-conditional channel P(Y|M).  For every transcript with positive
probability under b,

    P_a(Y=y) / P_b(Y=y)
      = sum_m w_m(y) * a_m / b_m,

where w_m(y) is the posterior model weight under b.  The likelihood ratio is
therefore a convex average of the prior-weight ratios and lies between their
minimum and maximum, independently of transcript length or channel complexity.

Fresh independent latent-model draws are different: likelihood factors multiply
across independent units, so evidence can scale with the number of latent draws,
not merely the number of repeated observations within one persistent unit.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import prod
from typing import Sequence


def _probability_vector(values: Sequence[Fraction], *, strictly_positive: bool = False) -> tuple[Fraction, ...]:
    result = tuple(Fraction(v) for v in values)
    if not result or any(v < 0 for v in result) or sum(result, Fraction(0)) != 1:
        raise ValueError("weights must form a probability vector")
    if strictly_positive and any(v <= 0 for v in result):
        raise ValueError("reference weights must be strictly positive")
    return result


def _channel(rows: Sequence[Sequence[Fraction]], model_count: int) -> tuple[tuple[Fraction, ...], ...]:
    result = tuple(tuple(Fraction(v) for v in row) for row in rows)
    if len(result) != model_count or not result or not result[0]:
        raise ValueError("channel must have one nonempty outcome row per model")
    width = len(result[0])
    if any(len(row) != width or any(v < 0 for v in row) or sum(row, Fraction(0)) != 1 for row in result):
        raise ValueError("every channel row must be a probability vector with common width")
    return result


def mixture_outcome_law(weights: Sequence[Fraction], channel: Sequence[Sequence[Fraction]]) -> tuple[Fraction, ...]:
    w = _probability_vector(weights)
    c = _channel(channel, len(w))
    return tuple(
        sum((w[m] * c[m][y] for m in range(len(w))), Fraction(0))
        for y in range(len(c[0]))
    )


def prior_ratio_bounds(numerator: Sequence[Fraction], denominator: Sequence[Fraction]) -> tuple[Fraction, Fraction]:
    a = _probability_vector(numerator)
    b = _probability_vector(denominator, strictly_positive=True)
    if len(a) != len(b):
        raise ValueError("weight vectors must have the same length")
    ratios = tuple(x / y for x, y in zip(a, b))
    return min(ratios), max(ratios)


@dataclass(frozen=True)
class PersistentEvidenceCertificate:
    numerator_weights: tuple[Fraction, ...]
    denominator_weights: tuple[Fraction, ...]
    outcome: int
    numerator_probability: Fraction
    denominator_probability: Fraction
    likelihood_ratio: Fraction
    posterior_weights_under_denominator: tuple[Fraction, ...]
    component_prior_ratios: tuple[Fraction, ...]
    lower_bound: Fraction
    upper_bound: Fraction

    @property
    def valid(self) -> bool:
        if self.denominator_probability <= 0:
            return False
        weighted = sum(
            (w * r for w, r in zip(self.posterior_weights_under_denominator, self.component_prior_ratios)),
            Fraction(0),
        )
        return (
            all(w >= 0 for w in self.posterior_weights_under_denominator)
            and sum(self.posterior_weights_under_denominator, Fraction(0)) == 1
            and self.likelihood_ratio == self.numerator_probability / self.denominator_probability
            and self.likelihood_ratio == weighted
            and self.lower_bound == min(self.component_prior_ratios)
            and self.upper_bound == max(self.component_prior_ratios)
            and self.lower_bound <= self.likelihood_ratio <= self.upper_bound
        )


def persistent_evidence_certificate(
    numerator_weights: Sequence[Fraction],
    denominator_weights: Sequence[Fraction],
    channel: Sequence[Sequence[Fraction]],
    outcome: int,
) -> PersistentEvidenceCertificate:
    a = _probability_vector(numerator_weights)
    b = _probability_vector(denominator_weights, strictly_positive=True)
    if len(a) != len(b):
        raise ValueError("weight vectors must have the same length")
    c = _channel(channel, len(a))
    y = int(outcome)
    if not 0 <= y < len(c[0]):
        raise ValueError("outcome outside channel alphabet")
    pa = sum((a[m] * c[m][y] for m in range(len(a))), Fraction(0))
    pb = sum((b[m] * c[m][y] for m in range(len(a))), Fraction(0))
    if pb <= 0:
        raise ValueError("chosen outcome has zero probability under denominator mixture")
    posterior = tuple(b[m] * c[m][y] / pb for m in range(len(a)))
    ratios = tuple(a[m] / b[m] for m in range(len(a)))
    result = PersistentEvidenceCertificate(
        a, b, y, pa, pb, pa / pb, posterior, ratios, min(ratios), max(ratios)
    )
    if not result.valid:
        raise AssertionError("persistent latent evidence certificate failed validation")
    return result


def fresh_unit_likelihood_ratio(per_unit_ratios: Sequence[Fraction]) -> Fraction:
    ratios = tuple(Fraction(r) for r in per_unit_ratios)
    if any(r < 0 for r in ratios):
        raise ValueError("likelihood ratios must be nonnegative")
    return prod(ratios, start=Fraction(1))


def noiseless_persistent_binary_likelihood(theta: Fraction, observed_model: int, repeats: int) -> Fraction:
    """Likelihood of repeated noiseless observations from one persistent binary model.

    Once M is drawn, Y_t=M for every t.  For any positive repeat count, seeing
    all ones has probability theta and all zeros has probability 1-theta.
    """
    t = Fraction(theta)
    if not 0 <= t <= 1 or int(observed_model) not in (0, 1) or int(repeats) < 1:
        raise ValueError("invalid binary persistence parameters")
    return t if int(observed_model) == 1 else 1 - t


def misspecified_iid_binary_likelihood(theta: Fraction, observed_model: int, repeats: int) -> Fraction:
    """Likelihood under the different model that redraws M independently each time."""
    t = Fraction(theta)
    n = int(repeats)
    if not 0 <= t <= 1 or int(observed_model) not in (0, 1) or n < 1:
        raise ValueError("invalid binary iid parameters")
    p = t if int(observed_model) == 1 else 1 - t
    return p**n
