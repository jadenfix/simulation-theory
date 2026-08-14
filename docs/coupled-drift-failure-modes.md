# Coupled-drift failure modes

## Incorrect relaxation

**Failure:** Sum independent per-time worst cases and call the result an
attainable path value.

**Guard:** Report the sum only as `marginal_upper_bound`; solve the coupled path
polytope separately and expose the gap.

## Missing event constraints

**Failure:** Check only coordinatewise differences and assume this equals TV for
more than two states.

**Guard:** Include one event from every event/complement pair.

## Wrong simplex elimination

**Failure:** Drop the final coordinate without adding its constant and coefficient
corrections to the objective and constraints.

**Guard:** Reconstruct every full probability vector and independently verify
simplex membership and objective values.

## Partial active-set search

**Failure:** Stop after finding a good vertex and call it optimal.

**Guard:** Count every candidate basis before search, enforce a cap, and fail
closed if complete enumeration is unavailable.

## One-sided proof

**Failure:** Trust only vertex maximization.

**Guard:** Return a matching exact rational dual and verify complementary
slackness.

## Unsafe code pruning

**Failure:** Prune a code because it is worse under one nominal law.

**Guard:** Prune only componentwise state-length dominance for the dynamic path
problem.

## Hidden adaptation

**Failure:** Let the encoder choose later codebooks after seeing the hidden
source law while describing the plan as precommitted.

**Guard:** Enumerate a complete codebook sequence before path optimization.

## Unpriced reconfiguration

**Failure:** Compare a changing sequence with a static code while ignoring the
cost to distribute or activate the new codebook.

**Guard:** Expose an explicit switching penalty and switch count; keep physical
interpretation separate.

## Statistical overclaim

**Failure:** Treat an assumed drift budget as if it had sampling coverage.

**Guard:** Keep statistical radius and declared drift in separate fields and
claims.

## Cross-level leakage

**Failure:** Convert exact internal expected bits into parent-universe energy or
hardware.

**Guard:** Require a separate implementation map and law-transfer assumption.
