from __future__ import annotations

from random import Random

from .algorithmic import multiplicity_inflation
from .inference import evidence_ceiling, optimal_equal_prior_accuracy
from .lazy_rendering import minimum_exact_memory_bits, minimum_exact_state_count
from .observer_measure import (
    descendant_resource_bound,
    model_averaged_simulated_fraction,
    plug_in_simulated_fraction,
    selection_tilt,
)


def observer_uncertainty_demo(seed: int = 7, draws: int = 20000) -> tuple[float, float]:
    rng = Random(seed)
    values = []
    for _ in range(draws):
        # Broad illustrative uncertainty across independent multiplicative factors.
        # These are not empirical priors.
        x = 1.0
        for _ in range(6):
            x *= 10.0 ** rng.uniform(-2.0, 2.0)
        values.append(x)
    return model_averaged_simulated_fraction(values), plug_in_simulated_fraction(values)


def main() -> None:
    print("== evidence ceiling ==")
    for prior, eps in ((0.1, 0.1), (0.5, 0.5), (0.9, 1.0)):
        print(prior, eps, evidence_ceiling(prior, eps))

    print("\n== Jensen/model-averaging gap (illustrative priors) ==")
    averaged, plugin = observer_uncertainty_demo()
    print("model_averaged", round(averaged, 6))
    print("plug_in", round(plugin, 6))

    print("\n== observable distinguishability ==")
    examples = [
        ([0.5, 0.5], [0.5, 0.5]),
        ([0.5, 0.5], [0.55, 0.45]),
        ([0.5, 0.5], [0.9, 0.1]),
    ]
    for p, q in examples:
        print(p, q, "best_equal_prior_accuracy", optimal_equal_prior_accuracy(p, q))

    print("\n== selection tilt ==")
    print(selection_tilt([0.8, 0.15, 0.05], [1.0, 0.5, 0.01]))

    print("\n== nested resource bound ==")
    for rho in (0.1, 0.3, 0.5, 0.9):
        print("rho", rho, "descendant_bound", descendant_resource_bound(1.0, rho))

    print("\n== predictive-state lower bound ==")
    future_laws = {
        (("h1",),): [0.5, 0.5],
        (("h2",),): [0.9, 0.1],
        (("h3",),): [0.5, 0.5],
        (("h4",),): [0.1, 0.9],
    }
    print("states", minimum_exact_state_count(future_laws))
    print("bits", minimum_exact_memory_bits(future_laws))

    print("\n== representation multiplicity ==")
    programs = [(3, "law-A"), (4, "law-A"), (5, "law-A"), (3, "law-B")]
    print(multiplicity_inflation(programs))


if __name__ == "__main__":
    main()
