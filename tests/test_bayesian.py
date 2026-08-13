from simtheory.bayesian import (
    Scenario,
    feasibility_mixture,
    plug_in_across_scenarios,
    posterior_simulated_probability,
)


def test_feasibility_uncertainty_is_not_discarded():
    scenarios = feasibility_mixture(0.2, 1_000_000.0)
    posterior = posterior_simulated_probability(scenarios)
    assert 0.19 < posterior < 0.21


def test_capability_evidence_changes_hierarchical_posterior():
    neutral = posterior_simulated_probability(feasibility_mixture(0.2, 10.0))
    favorable = posterior_simulated_probability(
        feasibility_mixture(
            0.2,
            10.0,
            likelihood_if_infeasible=0.1,
            likelihood_if_feasible=1.0,
        )
    )
    assert favorable > neutral


def test_average_of_ratios_differs_from_ratio_of_averages():
    scenarios = [
        Scenario("a", 0.5, 1.0, 0.0, 1.0),
        Scenario("b", 0.5, 1.0, 1000.0, 1.0),
    ]
    assert posterior_simulated_probability(scenarios) < plug_in_across_scenarios(scenarios)
