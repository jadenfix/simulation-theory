# Coupled-drift API guide

## Build a path polytope

```python
from fractions import Fraction
from simtheory.coupled_drift import enumerate_coupled_drift_path_polytope

polytope = enumerate_coupled_drift_path_polytope(
    initial_prior=(Fraction(1, 2), Fraction(1, 2)),
    drift_budgets=Fraction(1, 4),
    horizon=2,
)
assert polytope.valid
```

A scalar drift budget is repeated across the horizon. A sequence may be supplied
for time-varying budgets.

The function fails closed when exact active-basis enumeration exceeds
`max_bases`.

## Optimize a time-varying cost sequence

```python
from simtheory.coupled_drift import optimize_coupled_drift_costs

certificate = optimize_coupled_drift_costs(
    polytope,
    cost_vectors=((0, 1), (1, 0)),
)
assert certificate.valid
assert certificate.primal_value == Fraction(5, 4)
assert certificate.dual_value == Fraction(5, 4)
assert certificate.marginal_upper_bound == Fraction(7, 4)
```

Important fields:

- `optimal_path`: exact adversarial probability path;
- `primal_value`: exact coupled optimum;
- `dual_multipliers`: exact nonnegative LP receipt;
- `dual_support`: active shadow-price constraints;
- `marginal_upper_bound`: independent expanding-ball relaxation;
- `marginal_relaxation_gap`: incompatibility gap.

## Detect a shared cost ordering

```python
from simtheory.coupled_drift import common_cost_ordering

assert common_cost_ordering(((0, 1), (0, 3)))
assert not common_cost_ordering(((0, 1), (1, 0)))
```

A common weak ordering is a sufficient condition for the canonical nested TV
transport path to attain every marginal support function simultaneously.

## Optimize a precommitted codebook sequence

```python
from simtheory.confusion_graphs import ConfusionGraph
from simtheory.coupled_drift import exact_precommitted_code_sequence

graph = ConfusionGraph.from_edges(
    vertices=(0, 1, 2),
    edges=((0, 1), (0, 2), (1, 2)),
)

certificate = exact_precommitted_code_sequence(
    graph,
    nominal_prior=(Fraction(1, 3),) * 3,
    drift_budgets=Fraction(1, 6),
    horizon=2,
    switching_penalty=0,
)
assert certificate.valid
assert certificate.selected_total_value == Fraction(11, 3)
assert certificate.static_total_value == Fraction(23, 6)
```

Optional limits:

- `max_switches` restricts the number of codebook changes;
- `max_sequences` caps exact outer enumeration;
- `max_path_bases` caps path-polytope enumeration;
- `max_dual_bases` caps the selected sequence's exact dual search;
- existing graph-partition and prefix-shape caps remain available.

## Resource boundaries

The API solves expected zero-error prefix length plus an explicit abstract
switching penalty. It does not compute queue delay, peak bandwidth, codebook
distribution cost, or physical energy. Those require separate models.
