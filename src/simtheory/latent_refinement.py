"""Representation-invariant refinement of observationally identical latent states.

A latent component can be split into any number of observationally identical
clones whose weights sum to the original component weight.  This leaves every
finite shared-latent iid view law unchanged.  Consequently raw latent-label
counts are not observational invariants: uniform-per-label category mass can be
moved arbitrarily by cloning labels while probability-weighted category mass is
preserved exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Sequence

Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]


def _prior(values: Sequence[Fraction]) -> Vector:
    p = tuple(Fraction(v) for v in values)
    if not p or any(v < 0 for v in p) or sum(p, Fraction(0)) != 1:
        raise ValueError("prior must be a probability vector")
    return p


def _channel(rows: Sequence[Sequence[Fraction]]) -> Matrix:
    k = tuple(tuple(Fraction(v) for v in row) for row in rows)
    if not k or not k[0] or any(
        len(row) != len(k[0])
        or any(v < 0 for v in row)
        or sum(row, Fraction(0)) != 1
        for row in k
    ):
        raise ValueError("channel rows must be probability vectors on one alphabet")
    return k


def shared_latent_view_law(
    prior: Sequence[Fraction],
    channel: Sequence[Sequence[Fraction]],
    views: int,
    *,
    max_outcomes: int = 1_000_000,
) -> tuple[tuple[tuple[int, ...], Fraction], ...]:
    """Exact law of iid emissions sharing one persistent latent component."""

    p, k = _prior(prior), _channel(channel)
    if len(p) != len(k):
        raise ValueError("prior length must match channel rows")
    v = int(views)
    if v < 1:
        raise ValueError("at least one view is required")
    n = len(k[0])
    if n**v > int(max_outcomes):
        raise ValueError("shared-view outcome space exceeds configured cap")
    result = []
    for outcome in product(range(n), repeat=v):
        probability = sum(
            (
                p[i]
                * _product(k[i][symbol] for symbol in outcome)
                for i in range(len(p))
            ),
            Fraction(0),
        )
        result.append((tuple(outcome), probability))
    law = tuple(result)
    if sum((probability for _, probability in law), Fraction(0)) != 1:
        raise AssertionError("shared-view law failed normalization")
    return law


def _product(values) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def weighted_category_mass(
    prior: Sequence[Fraction], categories: Sequence[str], target: str
) -> Fraction:
    p = _prior(prior)
    labels = tuple(str(value) for value in categories)
    if len(labels) != len(p):
        raise ValueError("one category label is required per latent component")
    return sum((p[i] for i, label in enumerate(labels) if label == target), Fraction(0))


def uniform_label_category_mass(categories: Sequence[str], target: str) -> Fraction:
    labels = tuple(str(value) for value in categories)
    if not labels:
        raise ValueError("at least one latent label is required")
    return Fraction(sum(label == target for label in labels), len(labels))


@dataclass(frozen=True)
class LatentRefinementCertificate:
    original_prior: Vector
    original_channel: Matrix
    original_categories: tuple[str, ...]
    refined_prior: Vector
    refined_channel: Matrix
    refined_categories: tuple[str, ...]
    refined_index: int
    split_weights: Vector
    max_views_checked: int
    original_view_laws: tuple[tuple[tuple[tuple[int, ...], Fraction], ...], ...]
    refined_view_laws: tuple[tuple[tuple[tuple[int, ...], Fraction], ...], ...]

    @property
    def valid(self) -> bool:
        try:
            p = _prior(self.original_prior)
            k = _channel(self.original_channel)
            p2 = _prior(self.refined_prior)
            k2 = _channel(self.refined_channel)
            split = _prior(self.split_weights)
        except ValueError:
            return False
        i = self.refined_index
        r = len(split)
        if not (
            len(p) == len(k) == len(self.original_categories)
            and 0 <= i < len(p)
            and r >= 2
            and len(p2) == len(k2) == len(self.refined_categories) == len(p) + r - 1
            and self.max_views_checked >= 1
            and len(self.original_view_laws) == len(self.refined_view_laws) == self.max_views_checked
        ):
            return False
        expected_prior = p[:i] + tuple(p[i] * w for w in split) + p[i + 1 :]
        expected_channel = k[:i] + (k[i],) * r + k[i + 1 :]
        expected_categories = (
            self.original_categories[:i]
            + (self.original_categories[i],) * r
            + self.original_categories[i + 1 :]
        )
        if (
            p2 != expected_prior
            or k2 != expected_channel
            or self.refined_categories != expected_categories
        ):
            return False
        for view in range(1, self.max_views_checked + 1):
            if self.original_view_laws[view - 1] != shared_latent_view_law(p, k, view):
                return False
            if self.refined_view_laws[view - 1] != shared_latent_view_law(p2, k2, view):
                return False
            if self.original_view_laws[view - 1] != self.refined_view_laws[view - 1]:
                return False
        return True


def exact_latent_refinement(
    prior: Sequence[Fraction],
    channel: Sequence[Sequence[Fraction]],
    categories: Sequence[str],
    refined_index: int,
    split_weights: Sequence[Fraction],
    *,
    max_views_checked: int = 4,
    max_outcomes: int = 1_000_000,
) -> LatentRefinementCertificate:
    p, k = _prior(prior), _channel(channel)
    labels = tuple(str(value) for value in categories)
    if len(p) != len(k) or len(labels) != len(p):
        raise ValueError("prior, channel, and category dimensions must match")
    i = int(refined_index)
    if not 0 <= i < len(p):
        raise ValueError("refined component index is out of range")
    split = _prior(split_weights)
    if len(split) < 2:
        raise ValueError("refinement requires at least two clone weights")
    p2 = p[:i] + tuple(p[i] * w for w in split) + p[i + 1 :]
    k2 = k[:i] + (k[i],) * len(split) + k[i + 1 :]
    labels2 = labels[:i] + (labels[i],) * len(split) + labels[i + 1 :]
    views = int(max_views_checked)
    if views < 1:
        raise ValueError("max_views_checked must be positive")
    before = tuple(
        shared_latent_view_law(p, k, view, max_outcomes=max_outcomes)
        for view in range(1, views + 1)
    )
    after = tuple(
        shared_latent_view_law(p2, k2, view, max_outcomes=max_outcomes)
        for view in range(1, views + 1)
    )
    result = LatentRefinementCertificate(
        p,
        k,
        labels,
        p2,
        k2,
        labels2,
        i,
        split,
        views,
        before,
        after,
    )
    if not result.valid:
        raise AssertionError("latent refinement certificate failed validation")
    return result
