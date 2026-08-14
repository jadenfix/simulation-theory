# Coupled-drift certificate schema

This is a human-readable schema for external receipt adapters.

## Path polytope receipt

```text
initial_prior: exact rational vector
horizon: positive integer
drift_budgets: exact rational vector in [0,1]^T
state_count: positive integer
free_dimension: T * (state_count - 1)
constraints:
  - exact coefficient vector
  - exact bound
  - semantic label
vertices:
  - exact free-coordinate vector
  - reconstructed probability path
  - complete active-constraint labels
candidate_bases: integer
bases_examined: integer
nonsingular_bases: integer
configured_basis_cap: integer
```

## Coupled objective receipt

```text
cost_vectors: one exact rational vector per period
objective_constant: exact rational
objective_coefficients: exact rational vector
maximizing_vertex_index: integer
primal_value: exact rational
dual_multipliers: exact nonnegative rational vector
dual_transpose: exact rational vector
dual_value: exact rational
dual_support: integer indices
dual_candidate_bases: integer
dual_bases_examined: integer
marginal_certificates: exact TV support-function receipts
marginal_upper_bound: exact rational
```

Required checker equalities:

```text
A^T y == c
primal_value == objective(maximizing_vertex)
dual_value == objective_constant + b^T y
primal_value == dual_value
y_i * primal_slack_i == 0 for every i
marginal_upper_bound >= primal_value
```

## Code-sequence receipt

```text
graph: exact finite confusion graph
nominal_prior: exact rational vector
path_polytope: path receipt
code_universe: bounded exact deterministic code candidates
switching_penalty: exact nonnegative rational
max_switches: integer or none
evaluations:
  - code candidate index per period
  - exact state-length vector per period
  - exact adversarial path value
  - maximizing path vertex index
  - switch count
  - switching cost
  - total value
selected_evaluation_index: integer
selected_path_certificate: coupled objective receipt
best_static_evaluation: one evaluation
sequence_count: integer
configured_sequence_cap: integer
```

An external harness may hash or register these fields, but structural validation
alone is not mathematical execution. The canonical checker remains the exact
repository implementation at a declared source revision.
