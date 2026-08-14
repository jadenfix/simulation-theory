# Coupled-drift audit matrix

| Claim | Analytic derivation | Exact implementation | Independent check |
|---|---|---|---|
| Event-halfspace path equivalence | `coupled-drift-code-sequences.md` | `enumerate_coupled_drift_path_polytope` | every returned path rechecks all halfspaces and TV steps |
| Coupled linear optimum | primal LP derivation | path vertex evaluation | exact dual equality and complementary slackness |
| Marginal upper bound | TV triangle inequality | per-period TV support receipts | strict binary counterexample |
| Common-order equality | nested transport argument | `common_cost_ordering` | aligned binary example |
| Precommitted sequence optimum | exhaustive finite outer minimization | `exact_precommitted_code_sequence` | every K3 sequence value replays against the path polytope |
| K3 rotating gain | hand derivation | exact sequence search | exact values `11/3` and `23/6` |
| Switching threshold | equate static and rotating totals | rational penalty search | boundary and above-boundary tests |
| Claim ledger | typed manifest | evidence-path validation | canonical manifest hash |
