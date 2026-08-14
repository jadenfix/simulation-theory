from math import isclose
from random import Random

from simtheory.anthropic import WorldModel, reference_sampling, scale_observer_counts
from simtheory.causal import retained_distribution, retention_policy_for_target
from simtheory.lazy_rendering import (
    conditional_tv_profile,
    sequential_total_variation_bound,
    transcript_total_variation,
)
from simtheory.observer_measure import (
    model_averaged_simulated_fraction,
    plug_in_simulated_fraction,
)
from simtheory.sequential import exact_expected_e_value


def _binary(rng: Random) -> list[float]:
    p = rng.random()
    return [p, 1.0 - p]


def test_random_finite_adaptive_trees_respect_coupling_bound():
    rng = Random(20260814)
    for _ in range(200):
        target = {(): _binary(rng), (0,): _binary(rng), (1,): _binary(rng)}
        renderer = {(): _binary(rng), (0,): _binary(rng), (1,): _binary(rng)}
        profile = conditional_tv_profile(target, renderer, 2)
        exact = transcript_total_variation(target, renderer, 2)
        assert exact <= sequential_total_variation_bound(profile) + 1e-12


def test_random_reweighting_construction_hits_target():
    rng = Random(19)
    for _ in range(200):
        raw_unnormalized = [rng.random() + 0.01 for _ in range(5)]
        target_unnormalized = [rng.random() + 0.01 for _ in range(5)]
        raw_total = sum(raw_unnormalized)
        target_total = sum(target_unnormalized)
        raw = [value / raw_total for value in raw_unnormalized]
        target = [value / target_total for value in target_unnormalized]
        policy = retention_policy_for_target(raw, target)
        observed = retained_distribution(raw, policy)
        assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(observed, target))


def test_random_simple_null_likelihood_ratios_have_unit_expectation():
    rng = Random(23)
    for _ in range(100):
        p0 = rng.uniform(0.01, 0.99)
        p1 = rng.uniform(0.01, 0.99)
        n = rng.randrange(0, 30)
        assert isclose(exact_expected_e_value(n, p0, p0, p1), 1.0, rel_tol=1e-10, abs_tol=1e-12)


def test_random_jensen_gap_and_ssa_duplication_invariance():
    rng = Random(29)
    for _ in range(100):
        samples = [10.0 ** rng.uniform(-8.0, 8.0) for _ in range(50)]
        assert model_averaged_simulated_fraction(samples) <= plug_in_simulated_fraction(samples) + 1e-15

        fixed = WorldModel("fixed", 0.5, 100.0, 2.0, 0.5)
        scalable = WorldModel("scaled", 0.5, 200.0, 4.0, 0.5)
        factor = 10.0 ** rng.uniform(-3.0, 3.0)
        before = reference_sampling([fixed, scalable])["scaled"]
        after = reference_sampling([fixed, scale_observer_counts(scalable, factor)])["scaled"]
        assert isclose(before, after, abs_tol=1e-12)
