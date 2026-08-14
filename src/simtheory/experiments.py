"""Deterministic research demonstrations for the theorem modules."""

from __future__ import annotations

from random import Random

from .algorithmic import multiplicity_inflation
from .anthropic import WorldModel, two_world_scale_sensitivity
from .bayesian import feasibility_mixture, plug_in_across_scenarios, posterior_simulated_probability
from .bell_predictive import (
    adaptive_trials_necessary_for_tv,
    analytic_visibility_tv,
    chsh_value,
    maximum_epsilon_packing,
    predictive_memory_lower_bound_bits,
    schedule_fisher_information,
    uniform_visibility_grid,
)
from .causal import (
    minimum_selection_gamma,
    minimum_unrestricted_intervention_rate,
    raw_probability_bounds_from_selected,
    selected_binary_probability,
)
from .inference import evidence_ceiling, optimal_equal_prior_accuracy, robust_posterior_interval
from .lazy_rendering import (
    approximate_memory_bits_lower_bound,
    approximate_state_packing_lower_bound,
    conditional_tv_profile,
    sequential_total_variation_bound,
    transcript_total_variation,
)
from .minimax import fano_iid_error_lower_bound, necessary_iid_samples_for_error
from .observer_measure import (
    descendant_resource_bound,
    model_averaged_simulated_fraction,
    plug_in_simulated_fraction,
)
from .physics import (
    bekenstein_information_bits,
    landauer_erasure_energy,
    mass_limited_operation_rate,
    schwarzschild_radius_meters,
)
from .sequential import (
    exact_anytime_mixture_rejection_probability,
    exact_expected_mixture_e_value,
)


def observer_uncertainty_demo(seed: int = 7, draws: int = 20_000) -> tuple[float, float]:
    rng = Random(seed)
    values: list[float] = []
    for _ in range(draws):
        # Illustrative uncertainty only; these are not empirical priors.
        measure = 1.0
        for _ in range(6):
            measure *= 10.0 ** rng.uniform(-2.0, 2.0)
        values.append(measure)
    return (
        model_averaged_simulated_fraction(values),
        plug_in_simulated_fraction(values),
    )


def main() -> None:
    print("== robust Bayesian evidence ==")
    print("ceiling", evidence_ceiling(0.25, 0.3))
    print("prior+BF uncertainty", robust_posterior_interval((0.05, 0.5), (0.5, 4.0)))

    print("\n== hierarchical feasibility uncertainty ==")
    scenarios = feasibility_mixture(0.2, 1_000_000.0)
    print("posterior_average", posterior_simulated_probability(scenarios))
    print("measure_plugin", plug_in_across_scenarios(scenarios))

    print("\n== observer-measure Jensen gap ==")
    averaged, plugin = observer_uncertainty_demo()
    print("model_averaged", round(averaged, 6))
    print("plug_in", round(plugin, 6))

    print("\n== anthropic conditioning sensitivity ==")
    base = WorldModel("base", 0.5, 100.0, 1.0, 1.0 - 2.718281828459045**-1)
    simulated = WorldModel("sim", 0.5, 100.0, 1.0, 1.0 - 2.718281828459045**-1)
    for row in two_world_scale_sensitivity(base, simulated, [1.0, 10.0, 1_000.0]):
        print(row)

    print("\n== adaptive approximate rendering ==")
    target = {(): [0.5, 0.5], (0,): [0.9, 0.1], (1,): [0.2, 0.8]}
    renderer = {(): [0.55, 0.45], (0,): [0.85, 0.15], (1,): [0.25, 0.75]}
    profile = conditional_tv_profile(target, renderer, 2)
    print("conditional_tv", profile)
    print("exact_transcript_tv", transcript_total_variation(target, renderer, 2))
    print("coupling_bound", sequential_total_variation_bound(profile))

    laws = {
        ("a",): [1.0, 0.0, 0.0],
        ("b",): [0.0, 1.0, 0.0],
        ("c",): [0.0, 0.0, 1.0],
        ("near-a",): [0.95, 0.05, 0.0],
    }
    print("packing_states", approximate_state_packing_lower_bound(laws, 0.1))
    print("packing_bits", approximate_memory_bits_lower_bound(laws, 0.1))

    print("\n== physically derived Bell predictive bounds ==")
    grid = uniform_visibility_grid(101)
    packing = maximum_epsilon_packing(grid, 0.02)
    print("TV_v0.2_v0.8", analytic_visibility_tv(0.2, 0.8))
    print("CHSH_v0.8", chsh_value(0.8))
    print("packing_states_eps0.02", len(packing))
    print("packing_bits_eps0.02", predictive_memory_lower_bound_bits(grid, 0.02))
    print("Fisher_v0.6", schedule_fisher_information(0.6))
    print("adaptive_trials_for_TV0.8_v0.4_v0.6", adaptive_trials_necessary_for_tv(0.4, 0.6, 0.8))

    print("\n== multi-architecture minimax bounds ==")
    models = [[0.9, 0.1], [0.6, 0.4], [0.4, 0.6], [0.1, 0.9]]
    for samples in (0, 1, 2, 5, 10):
        print("samples", samples, "fano_error_lower_bound", fano_iid_error_lower_bound(models, samples))
    print("necessary_for_10pct", necessary_iid_samples_for_error(models, 0.1))

    print("\n== selection and intervention sensitivity ==")
    raw = 0.05
    selected = selected_binary_probability(raw, 0.8, 0.2)
    gamma = minimum_selection_gamma(raw, selected)
    print("selected", selected, "gamma", gamma)
    print("raw_bounds", raw_probability_bounds_from_selected(selected, gamma))
    print("minimum_intervention_rate", minimum_unrestricted_intervention_rate(0.05, 0.2))

    print("\n== anytime-valid restricted-signature check ==")
    alternatives = [0.15, 0.25, 0.4]
    weights = [0.2, 0.5, 0.3]
    print("E_null_fixed_time", exact_expected_mixture_e_value(20, 0.1, 0.1, alternatives, weights))
    print(
        "P_null_cross_by_50",
        exact_anytime_mixture_rejection_probability(50, 0.1, 0.1, alternatives, 0.05, weights),
    )

    print("\n== local physical envelope (not parent-physics inference) ==")
    print("landauer_1e12_bits_300K_J", landauer_erasure_energy(1e12, 300.0))
    print("one_kg_ops_per_second", mass_limited_operation_rate(1.0))
    print("one_kg_schwarzschild_radius_m", schwarzschild_radius_meters(1.0))
    print("one_joule_10cm_bekenstein_bits", bekenstein_information_bits(1.0, 0.1))

    print("\n== representation multiplicity ==")
    print(multiplicity_inflation([(3, "law-A"), (4, "law-A"), (5, "law-A"), (3, "law-B")]))

    print("\n== binary distinguishability ==")
    print(optimal_equal_prior_accuracy([0.5, 0.5], [0.55, 0.45]))
    print("nested_budget_rho_0.3", descendant_resource_bound(1.0, 0.3))


if __name__ == "__main__":
    main()
