# Coupled-drift proof outline

## Theorem A: path-polytope equivalence

1. Eliminate the final simplex coordinate at each time.
2. Enforce nonnegativity of every reconstructed coordinate.
3. Use `TV(u,v)=max_S |u(S)-v(S)|`.
4. Retain one event per complement pair.
5. Add both signed event inequalities for each transition.
6. Conclude exact equivalence between admissible paths and the rational
   halfspace system.

## Theorem B: exact coupled optimum

1. The path set is a nonempty bounded rational polytope.
2. The cumulative cost is affine in free coordinates.
3. A maximum is attained at a polytope vertex.
4. Complete active-basis enumeration finds all vertices below the declared cap.
5. The LP dual supplies nonnegative multipliers with `A^T y=c`.
6. Exact primal-dual equality and complementary slackness prove optimality.

## Theorem C: marginal relaxation

1. Triangle inequality gives `TV(q_t,p)<=R_t`.
2. Each path term is bounded by the support function of the radius-`R_t` ball.
3. Summing gives the relaxation upper bound.
4. Under common weak cost ordering, canonical TV transport is nested in radius.
5. The nested path respects every incremental budget and attains every support
   function, proving equality.

## Theorem D: precommitted sequence optimum

1. Pure-state source scenarios map each deterministic codebook to its complete
   state-length vector.
2. Componentwise dominance is safe for every source law and every path.
3. Exhaust every surviving sequence below the cap.
4. Solve the exact coupled inner path value for each sequence.
5. Add the declared switching penalty.
6. Select the minimum and replay its exact primal-dual path certificate.

## Model results

- Binary reversing costs: derive `5/4` and strict marginal gap `1/2`.
- Uniform K3 rotating short leaf: derive `11/3` versus static `23/6`.
- Equate rotating plus one switch with static to obtain `kappa_c=1/6`.
