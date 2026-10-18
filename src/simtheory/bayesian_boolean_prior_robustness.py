"""Exact prior-sensitivity bounds for Bayesian Boolean experiment value.

For a fixed observed coordinate set S, Bayesian K3 excess cost is the Bayes
classification risk of f(X) from X_S.  For any two priors p,q on the same finite
hidden-model space, optimal bounded-loss risk is 1-Lipschitz in total variation:

    |V_p(S)-V_q(S)| <= TV(p,q).

The module turns that into exact rational uncertainty bands for values,
marginal experiment gains, and ranking margins.  These are deterministic
sensitivity bounds conditional on a declared TV radius; they do not themselves
produce a statistical confidence radius.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

from .bayesian_boolean_experiments import bayesian_boolean_gap


def _validate_prior(prior: Sequence[Fraction]) -> tuple[Fraction, ...]:
    p = tuple(Fraction(x) for x in prior)
    if not p or any(x < 0 for x in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("prior must be a nonempty probability vector")
    return p


def prior_total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    p = _validate_prior(left)
    q = _validate_prior(right)
    if len(p) != len(q):
        raise ValueError("priors must have the same support size")
    return sum((abs(a - b) for a, b in zip(p, q)), Fraction(0)) / 2


@dataclass(frozen=True)
class ValueSensitivityCertificate:
    observed: tuple[int, ...]
    left_value: Fraction
    right_value: Fraction
    total_variation: Fraction
    slack: Fraction

    @property
    def valid(self) -> bool:
        return (
            self.total_variation >= 0
            and self.slack == self.total_variation - abs(self.left_value - self.right_value)
            and self.slack >= 0
        )


def exact_value_sensitivity_certificate(
    truth_table: Sequence[int],
    left_prior: Sequence[Fraction],
    right_prior: Sequence[Fraction],
    observed: Iterable[int],
) -> ValueSensitivityCertificate:
    selected = tuple(sorted(set(int(i) for i in observed)))
    left = bayesian_boolean_gap(truth_table, left_prior, selected)
    right = bayesian_boolean_gap(truth_table, right_prior, selected)
    tv = prior_total_variation(left_prior, right_prior)
    result = ValueSensitivityCertificate(selected, left, right, tv, tv - abs(left - right))
    if not result.valid:
        raise AssertionError("Bayesian prior sensitivity certificate failed")
    return result


def value_interval(nominal_value: Fraction, tv_radius: Fraction) -> tuple[Fraction, Fraction]:
    value = Fraction(nominal_value)
    rho = Fraction(tv_radius)
    if not 0 <= value <= Fraction(1, 2) or not 0 <= rho <= 1:
        raise ValueError("invalid Bayesian value or TV radius")
    return max(Fraction(0), value - rho), min(Fraction(1, 2), value + rho)


def marginal_gain(
    truth_table: Sequence[int],
    prior: Sequence[Fraction],
    before: Iterable[int],
    after: Iterable[int],
) -> Fraction:
    b = tuple(sorted(set(int(i) for i in before)))
    a = tuple(sorted(set(int(i) for i in after)))
    if not set(b).issubset(a):
        raise ValueError("after-observation set must refine before-observation set")
    return bayesian_boolean_gap(truth_table, prior, b) - bayesian_boolean_gap(truth_table, prior, a)


def marginal_gain_interval(nominal_gain: Fraction, tv_radius: Fraction) -> tuple[Fraction, Fraction]:
    gain = Fraction(nominal_gain)
    rho = Fraction(tv_radius)
    if not 0 <= rho <= 1:
        raise ValueError("invalid TV radius")
    return max(Fraction(0), gain - 2 * rho), min(Fraction(1, 2), gain + 2 * rho)


def value_ranking_is_tv_robust(nominal_margin: Fraction, tv_radius: Fraction) -> bool:
    """Certify ordering of two Bayesian values throughout one TV ball.

    Each value can move by at most rho, so a strict nominal separation greater
    than 2 rho cannot reverse.
    """
    margin = Fraction(nominal_margin)
    rho = Fraction(tv_radius)
    if margin < 0 or not 0 <= rho <= 1:
        raise ValueError("invalid margin or radius")
    return margin > 2 * rho


def gain_ranking_is_tv_robust(nominal_margin: Fraction, tv_radius: Fraction) -> bool:
    """Certify ordering of two marginal gains throughout one TV ball.

    Each marginal gain is a difference of two 1-Lipschitz values and can move
    by at most 2 rho, so the difference between two gains can move by 4 rho.
    """
    margin = Fraction(nominal_margin)
    rho = Fraction(tv_radius)
    if margin < 0 or not 0 <= rho <= 1:
        raise ValueError("invalid margin or radius")
    return margin > 4 * rho


def concavity_gap(
    truth_table: Sequence[int],
    left_prior: Sequence[Fraction],
    right_prior: Sequence[Fraction],
    weight: Fraction,
    observed: Iterable[int],
) -> Fraction:
    p = _validate_prior(left_prior)
    q = _validate_prior(right_prior)
    if len(p) != len(q):
        raise ValueError("priors must have same support")
    lam = Fraction(weight)
    if not 0 <= lam <= 1:
        raise ValueError("mixture weight must lie in [0,1]")
    mixture = tuple(lam * a + (1 - lam) * b for a, b in zip(p, q))
    selected = tuple(sorted(set(int(i) for i in observed)))
    vmix = bayesian_boolean_gap(truth_table, mixture, selected)
    rhs = lam * bayesian_boolean_gap(truth_table, p, selected) + (1 - lam) * bayesian_boolean_gap(truth_table, q, selected)
    gap = vmix - rhs
    if gap < 0:
        raise AssertionError("Bayesian Boolean value violated concavity")
    return gap
