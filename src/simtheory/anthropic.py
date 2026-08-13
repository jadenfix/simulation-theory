from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class WorldModel:
    name: str
    prior: float
    total_observers: float
    matching_observers: float
    evidence_exists_probability: float


def _norm(pairs):
    pairs = list(pairs)
    z = sum(v for _, v in pairs)
    if z <= 0:
        raise ValueError("positive total weight required")
    return {k: v / z for k, v in pairs}


def reference_sampling(models):
    return _norm((m.name, m.prior * (m.matching_observers / m.total_observers if m.total_observers > 0 else 0.0)) for m in models)


def observer_number_weighted(models):
    return _norm((m.name, m.prior * m.matching_observers) for m in models)


def full_evidence_presence(models):
    return _norm((m.name, m.prior * m.evidence_exists_probability) for m in models)


def poisson_presence(expected_matching_copies: float) -> float:
    if expected_matching_copies < 0:
        raise ValueError("expected count must be nonnegative")
    return 1.0 - exp(-expected_matching_copies)
