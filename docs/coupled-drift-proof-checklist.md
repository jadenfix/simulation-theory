# Coupled-drift proof checklist

A coupled-drift result is accepted only when the following objects agree.

## Path geometry

- The initial law is a valid exact rational probability vector.
- Every per-period drift budget is exact rational and lies in `[0,1]`.
- The final simplex coordinate is eliminated independently at every period.
- One representative from every nontrivial event/complement pair is present.
- Both signed event inequalities are included at every transition.
- Every active basis below the declared cap is examined.
- Every candidate vertex is checked against every omitted halfspace.
- Reconstructed paths satisfy every simplex and consecutive-TV constraint.
- Degenerate copies of one path are deduplicated.

## Primal optimization

- One cost vector is declared for every period.
- The free-coordinate objective includes the correct eliminated-coordinate
  constant.
- Every enumerated path vertex is evaluated exactly.
- The selected path attains the largest exact rational value.

## Dual optimization

- Multipliers are nonnegative.
- The transpose equation `A^T y = c` holds exactly.
- The dual objective equals the primal objective exactly.
- Every positive multiplier is supported on a tight primal inequality.
- The configured dual-basis cap is not exceeded.

## Marginal relaxation

- Cumulative radii are derived from triangle inequality and clipped at one.
- Each period's TV support function is independently certified.
- The marginal sum is labeled an upper bound.
- Any equality claim states a compatibility condition such as common cost
  ordering or directly supplies one simultaneously attaining path.

## Code-sequence outer search

- The deterministic code universe is complete below its caps.
- Pure-state prior scenarios make each candidate's scenario-cost vector equal
  its source-state length vector.
- Only componentwise-dominated candidates are pruned.
- Every admissible code sequence below the sequence and switch caps is checked.
- Switching cost depends only on the declared codebook-change rule.
- Every reported sequence value replays against the exact path polytope.
- The selected sequence is compared against the best static sequence.
- Open-loop commitment is not called adaptive feedback.

## Interpretation

- A shadow price is not a physical energy claim.
- A decision threshold is not called a thermodynamic phase transition.
- Expected communication is not peak capacity, queue delay, or parent hardware.
- A drift budget is not called a confidence guarantee without a separate data
  theorem.
- A bounded exact checker is not called a scalability result.
- None of the results is evidence for simulation without a restricted
  architecture whose observable law favors that interpretation.
