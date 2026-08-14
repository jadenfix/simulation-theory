# Coupled-drift design decisions

## Exact arithmetic over generic numerical solvers

The bounded checker uses `Fraction` arithmetic and active-set enumeration so the
returned path and dual can be replayed exactly. This trades scalability for a
clear theorem boundary.

## Event halfspaces over auxiliary absolute-value variables

Finite TV is represented through event differences. This directly exposes the
probability events whose motion limits are binding and avoids adding one
absolute-value variable per state transition.

## Full path polytope over marginal dynamic programming

The first implementation solves one finite path polytope. This prevents an
incorrect Bellman decomposition before rectangularity and information patterns
are stated.

## Componentwise code dominance only

A code is pruned only when another code has no larger length on every source
state. Nominal or scenario-specific dominance is not safe for an arbitrary
dynamic path.

## Open-loop sequence before adaptive policy

The code sequence is selected before the source path. This is the strongest
nonadaptive comparison that permits changing representations while avoiding
undeclared access to hidden source laws.

## Switching cost on state-length-vector changes

Candidate codebooks are deduplicated by their pure-state cost vectors. A switch
is therefore charged when the operational source-state length vector changes,
not merely when two syntactic codeword labels differ.

## Separate marginal upper bound

The independent expanding-ball value is retained because it is useful as a
fast converse and because its gap quantifies temporal incompatibility. It is
never labeled achievable without a joint path.
