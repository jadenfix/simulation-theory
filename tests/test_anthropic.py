from math import isclose

from simtheory.anthropic import (
    WorldModel,
    conditioning_posteriors,
    full_evidence_presence,
    maximum_conditioning_disagreement,
    observer_number_weighted,
    reference_sampling,
    scale_observer_counts,
    scale_poisson_population,
    two_world_scale_sensitivity,
)


def test_conditioning_rules_can_disagree():
    worlds = [
        WorldModel("small", 0.5, 10.0, 1.0, 0.8),
        WorldModel("large", 0.5, 1000.0, 10.0, 0.2),
    ]
    a = reference_sampling(worlds)
    b = observer_number_weighted(worlds)
    c = full_evidence_presence(worlds)
    assert a != b
    assert b != c
    assert c != a
    assert maximum_conditioning_disagreement(worlds) > 0.0


def test_duplication_invariance_and_noninvariance():
    fixed = WorldModel("base", 0.5, 100.0, 1.0, 0.6)
    sim = WorldModel("sim", 0.5, 100.0, 1.0, 1.0 - 2.718281828459045 ** -1)
    scaled_counts = scale_observer_counts(sim, 100.0)
    scaled = scale_poisson_population(sim, 100.0)
    original_posteriors = conditioning_posteriors([fixed, sim])
    scaled_count_posteriors = conditioning_posteriors([fixed, scaled_counts])
    scaled_posteriors = conditioning_posteriors([fixed, scaled])
    assert isclose(original_posteriors["ssa"]["sim"], scaled_count_posteriors["ssa"]["sim"])
    assert scaled_count_posteriors["sia"]["sim"] > original_posteriors["sia"]["sim"]
    assert isclose(scaled_count_posteriors["fnc_presence"]["sim"], original_posteriors["fnc_presence"]["sim"])
    assert scaled_posteriors["fnc_presence"]["sim"] > original_posteriors["fnc_presence"]["sim"]


def test_sensitivity_surface_rows():
    fixed = WorldModel("base", 0.5, 100.0, 1.0, 0.5)
    sim = WorldModel("sim", 0.5, 100.0, 1.0, 0.5)
    rows = two_world_scale_sensitivity(fixed, sim, [1.0, 10.0])
    assert rows[0]["ssa"] == rows[1]["ssa"]
    assert rows[1]["sia"] > rows[0]["sia"]
