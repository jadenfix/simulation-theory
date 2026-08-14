"""Exact alpha-vector certificates for finite-horizon belief-state coding.

For a fixed previous codebook and remaining horizon, every deterministic policy
tree induces one affine expected-cost functional of the hidden-state belief:

    C_pi(b) = b . alpha_pi.

The optimal Bayesian cost is the pointwise minimum over finitely many policy
trees,

    V(b) = min_{alpha in Gamma} b . alpha.

Therefore the finite-horizon value is piecewise linear and concave in belief.
This module enumerates exact rational alpha vectors for both no-signal and
current noisy-signal policies below explicit caps.  Componentwise dominated
vectors are removed safely because beliefs are nonnegative.

The recursion provides an independent representation-level check of the
belief-state Bellman solver: every reachable Bellman entry must equal the
minimum alpha-vector value for its remaining horizon and previous codebook.

This is a bounded exact policy-tree construction, not a scalability theorem or
a claim that an internal alpha vector is a parent-substrate physical object.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Sequence

from .belief_state_coding import (
    Belief,
    BeliefStateCodingCertificate,
    HiddenLawModel,
    _switch_cost,
)
from .robust_prior_codes import RobustCodeCandidate

AlphaVector = tuple[Fraction, ...]


def alpha_value(belief: Sequence[Fraction], alpha: Sequence[Fraction]) -> Fraction:
    supplied_belief = tuple(Fraction(value) for value in belief)
    supplied_alpha = tuple(Fraction(value) for value in alpha)
    if not supplied_belief or len(supplied_belief) != len(supplied_alpha):
        raise ValueError("belief and alpha vector dimensions differ")
    return sum(
        (
            probability * value
            for probability, value in zip(supplied_belief, supplied_alpha)
        ),
        Fraction(0),
    )


def _dominates(left: AlphaVector, right: AlphaVector) -> bool:
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def _pareto_minimal(vectors: Sequence[AlphaVector]) -> tuple[AlphaVector, ...]:
    unique = tuple(sorted(set(vectors)))
    return tuple(
        vector
        for index, vector in enumerate(unique)
        if not any(
            _dominates(other, vector)
            for other_index, other in enumerate(unique)
            if index != other_index
        )
    )


def _continuation_cost(
    model: HiddenLawModel,
    alpha: AlphaVector,
    state: int,
) -> Fraction:
    return sum(
        (
            model.transition[state][next_state] * alpha[next_state]
            for next_state in range(model.hidden_state_count)
        ),
        Fraction(0),
    )


@dataclass(frozen=True)
class AlphaVectorFamilyEntry:
    observed: bool
    remaining_horizon: int
    previous_code: int
    vectors: tuple[AlphaVector, ...]
    raw_vector_count: int

    @property
    def dominated_or_duplicate_count(self) -> int:
        return self.raw_vector_count - len(self.vectors)

    @property
    def valid(self) -> bool:
        return (
            self.remaining_horizon >= 0
            and bool(self.vectors)
            and self.raw_vector_count >= len(self.vectors)
            and all(len(vector) == len(self.vectors[0]) for vector in self.vectors)
            and len(set(self.vectors)) == len(self.vectors)
            and not any(
                _dominates(left, right)
                for left_index, left in enumerate(self.vectors)
                for right_index, right in enumerate(self.vectors)
                if left_index != right_index
            )
        )


def _build_alpha_families(
    model: HiddenLawModel,
    candidates: Sequence[RobustCodeCandidate],
    horizon: int,
    switching_penalty: Fraction,
    *,
    observed: bool,
    max_raw_vectors: int,
) -> tuple[AlphaVectorFamilyEntry, ...]:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    cap = int(max_raw_vectors)
    if cap < 1:
        raise ValueError("max_raw_vectors must be positive")
    state_count = model.hidden_state_count
    candidate_count = len(candidates)
    if candidate_count < 1:
        raise ValueError("at least one codebook candidate is required")

    families: dict[tuple[int, int], tuple[AlphaVector, ...]] = {}
    entries: list[AlphaVectorFamilyEntry] = []
    previous_codes = tuple(range(-1, candidate_count))
    zero = tuple(Fraction(0) for _ in range(state_count))
    for previous_code in previous_codes:
        families[(0, previous_code)] = (zero,)
        entries.append(
            AlphaVectorFamilyEntry(observed, 0, previous_code, (zero,), 1)
        )

    for remaining in range(1, horizon + 1):
        for previous_code in previous_codes:
            raw: list[AlphaVector] = []
            if not observed:
                for code, candidate in enumerate(candidates):
                    for continuation in families[(remaining - 1, code)]:
                        raw.append(
                            tuple(
                                candidate.scenario_costs[state]
                                + _switch_cost(
                                    previous_code,
                                    code,
                                    switching_penalty,
                                )
                                + _continuation_cost(model, continuation, state)
                                for state in range(state_count)
                            )
                        )
                        if len(raw) > cap:
                            raise ValueError(
                                "no-signal alpha-vector enumeration exceeded cap"
                            )
            else:
                options = tuple(
                    (
                        code,
                        continuation,
                    )
                    for code in range(candidate_count)
                    for continuation in families[(remaining - 1, code)]
                )
                option_space = len(options) ** model.observation.signal_count
                if option_space > cap:
                    raise ValueError(
                        "observed alpha-vector policy-tree space exceeds cap"
                    )
                for signal_options in product(
                    options,
                    repeat=model.observation.signal_count,
                ):
                    vector: list[Fraction] = []
                    for state in range(state_count):
                        value = Fraction(0)
                        for signal, (code, continuation) in enumerate(
                            signal_options
                        ):
                            observation_probability = model.observation.matrix[
                                state
                            ][signal]
                            value += observation_probability * (
                                candidates[code].scenario_costs[state]
                                + _switch_cost(
                                    previous_code,
                                    code,
                                    switching_penalty,
                                )
                                + _continuation_cost(
                                    model,
                                    continuation,
                                    state,
                                )
                            )
                        vector.append(value)
                    raw.append(tuple(vector))
            minimal = _pareto_minimal(raw)
            if not minimal:
                raise AssertionError("alpha-vector recursion produced no policy")
            families[(remaining, previous_code)] = minimal
            entries.append(
                AlphaVectorFamilyEntry(
                    observed,
                    remaining,
                    previous_code,
                    minimal,
                    len(raw),
                )
            )
    return tuple(entries)


@dataclass(frozen=True)
class BeliefAlphaVectorCertificate:
    coding: BeliefStateCodingCertificate
    no_signal_families: tuple[AlphaVectorFamilyEntry, ...]
    observed_families: tuple[AlphaVectorFamilyEntry, ...]

    @property
    def valid(self) -> bool:
        if (
            not self.coding.valid
            or not self.no_signal_families
            or not self.observed_families
            or any(not entry.valid for entry in self.no_signal_families)
            or any(not entry.valid for entry in self.observed_families)
        ):
            return False
        no_signal = {
            (entry.remaining_horizon, entry.previous_code): entry.vectors
            for entry in self.no_signal_families
        }
        observed = {
            (entry.remaining_horizon, entry.previous_code): entry.vectors
            for entry in self.observed_families
        }
        if (
            len(no_signal) != len(self.no_signal_families)
            or len(observed) != len(self.observed_families)
        ):
            return False

        for entry in self.coding.no_signal_entries:
            remaining = self.coding.horizon - entry.period
            vectors = no_signal.get((remaining, entry.previous_code))
            if vectors is None:
                return False
            expected = min(
                alpha_value(entry.prior_belief, vector)
                for vector in vectors
            )
            if expected != entry.value:
                return False

        for entry in self.coding.observed_entries:
            remaining = self.coding.horizon - entry.period
            vectors = observed.get((remaining, entry.previous_code))
            if vectors is None:
                return False
            expected = min(
                alpha_value(entry.prior_belief, vector)
                for vector in vectors
            )
            if expected != entry.value:
                return False

        initial_no_signal = min(
            alpha_value(
                self.coding.model.initial_belief,
                vector,
            )
            for vector in no_signal[(self.coding.horizon, -1)]
        )
        initial_observed = min(
            alpha_value(
                self.coding.model.initial_belief,
                vector,
            )
            for vector in observed[(self.coding.horizon, -1)]
        )
        return (
            initial_no_signal == self.coding.no_signal_value
            and initial_observed == self.coding.observed_value
        )


def exact_belief_alpha_vector_certificate(
    coding: BeliefStateCodingCertificate,
    *,
    max_raw_vectors: int = 2_000_000,
) -> BeliefAlphaVectorCertificate:
    """Construct independent policy-tree representations of both belief DPs."""

    if not coding.valid:
        raise ValueError("belief-state coding certificate must be valid")
    no_signal = _build_alpha_families(
        coding.model,
        coding.candidates,
        coding.horizon,
        coding.switching_penalty,
        observed=False,
        max_raw_vectors=max_raw_vectors,
    )
    observed = _build_alpha_families(
        coding.model,
        coding.candidates,
        coding.horizon,
        coding.switching_penalty,
        observed=True,
        max_raw_vectors=max_raw_vectors,
    )
    result = BeliefAlphaVectorCertificate(coding, no_signal, observed)
    if not result.valid:
        raise AssertionError("belief alpha-vector certificate failed validation")
    return result


def posterior_martingale_identity(
    belief: Belief,
    model: HiddenLawModel,
) -> tuple[Belief, Belief]:
    """Return E[b^Y] and E[b^Y K], which equal b and bK exactly."""

    posterior_mean = [Fraction(0) for _ in belief]
    predicted_mean = [Fraction(0) for _ in belief]
    for signal in range(model.observation.signal_count):
        probability = sum(
            (
                belief[state] * model.observation.matrix[state][signal]
                for state in range(len(belief))
            ),
            Fraction(0),
        )
        if probability == 0:
            continue
        posterior = tuple(
            belief[state] * model.observation.matrix[state][signal] / probability
            for state in range(len(belief))
        )
        predicted = tuple(
            sum(
                (
                    posterior[state] * model.transition[state][next_state]
                    for state in range(len(belief))
                ),
                Fraction(0),
            )
            for next_state in range(len(belief))
        )
        for state in range(len(belief)):
            posterior_mean[state] += probability * posterior[state]
            predicted_mean[state] += probability * predicted[state]
    result = tuple(posterior_mean), tuple(predicted_mean)
    expected = tuple(belief), tuple(
        sum(
            (
                belief[state] * model.transition[state][next_state]
                for state in range(len(belief))
            ),
            Fraction(0),
        )
        for next_state in range(len(belief))
    )
    if result != expected:
        raise AssertionError("posterior martingale identity failed")
    return result
