"""Deterministic examples for the coupled-drift theorem lane."""

from fractions import Fraction

from simtheory.confusion_graphs import complete_graph
from simtheory.coupled_drift import (
    exact_coupled_drift_path,
    exact_precommitted_code_sequence,
)


def main() -> None:
    antagonistic = exact_coupled_drift_path(
        (Fraction(1, 2), Fraction(1, 2)),
        ((0, 1), (1, 0)),
        Fraction(1, 4),
    )
    print("coupled_value", antagonistic.objective_value)
    print("marginal_envelope", antagonistic.marginal_envelope)
    print("coupling_gap", antagonistic.coupling_gap)
    print("attaining_path", antagonistic.extremal_path)
    print("dual_support", antagonistic.dual_support)

    rotation = exact_precommitted_code_sequence(
        complete_graph(3),
        (Fraction(1, 3),) * 3,
        Fraction(1, 6),
        2,
    )
    print("static_value", rotation.static_best_value)
    print("sequence_value", rotation.total_value)
    print("sequence_gain", rotation.sequence_gain_over_static)
    print(
        "selected_lengths",
        tuple(candidate.scenario_costs for candidate in rotation.selected_candidates),
    )


if __name__ == "__main__":
    main()
