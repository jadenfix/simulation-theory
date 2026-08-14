# Exact Farkas and LP dual certificates for prior ambiguity

The polyhedral prior lane originally had a complete primal route: eliminate the simplex equality, enumerate every active rational basis, retain every feasible vertex, and optimize a linear expectation over those vertices.  This document adds an independent dual route so that both infeasibility and optimality have explicit proof objects.

## 1. Transformed ambiguity system

After eliminating the last probability coordinate,

\[
q_n=1-\sum_{j=1}^{n-1}q_j,
\]

a rational ambiguity set has the form

\[
\mathcal X=\{x\in\mathbb R^d:Cx\le d_0\},
\qquad d=n-1.
\]

The transformed rows include every user-declared prior restriction and the simplex nonnegativity inequalities.  All coefficients are exact rational numbers.

## 2. Farkas alternative for an empty ambiguity set

If

\[
Cx\le d_0
\]

has no solution, Farkas' alternative provides multipliers

\[
y\ge0
\]

such that

\[
C^Ty=0,
\qquad
d_0^Ty<0.
\]

Indeed, if a feasible `x` existed then

\[
y^TCx\le y^Td_0<0,
\]

but

\[
y^TCx=(C^Ty)^Tx=0,
\]

a contradiction.

Because any positive scalar multiple is also a witness, the implementation normalizes

\[
\mathbf1^Ty=1.
\]

The normalized witness set is described by `d+1` linear equalities.  A basic feasible normalized witness therefore needs no more than `d+1` positive multipliers.  The bounded exact checker exhausts all candidate supports of that size, solves the rational equality system, requires nonnegative multipliers, and accepts only a witness with strictly negative rational bound product.

The resulting receipt stores:

- every multiplier;
- the exact zero vector `C^T y`;
- the exact negative scalar `d_0^T y`;
- normalization `1^T y=1`;
- the positive support;
- the number of candidate bases examined.

An empty vertex list is therefore no longer used by itself as a proof of infeasibility.

## 3. Exact expectation dual

For state values

\[
g=(g_1,\ldots,g_n),
\]

the expected value becomes, after eliminating `q_n`,

\[
q^Tg
=
g_n+c^Tx,
\]

where

\[
c_j=g_j-g_n.
\]

The primal maximum is

\[
\boxed{
\max_x\;g_n+c^Tx
\quad\text{s.t.}\quad Cx\le d_0.
}
\]

Its LP dual is

\[
\boxed{
\min_{y\ge0}\;g_n+d_0^Ty
\quad\text{s.t.}\quad C^Ty=c.
}
\]

The primal route obtains an optimizer by exact vertex enumeration.  The dual route independently enumerates rational basic dual solutions, checks nonnegativity and the equality `C^T y=c`, and minimizes the exact dual objective.

A certificate is accepted only if

\[
\boxed{
q_*^Tg
=
g_n+d_0^Ty_*.
}
\]

The gap is therefore exactly zero in rational arithmetic.

For minimization of `q^Tg`, the same machinery is applied to `-g`; the final sign is transformed back before comparison with the primal minimum.

## 4. Sparse optimality receipts

There are `d` dual equality constraints

\[
C^Ty=c.
\]

A basic dual optimum can be represented with at most `d=n-1` positive inequality multipliers.  The implementation records this sparse support but does not confuse sparsity with uniqueness: degenerate problems may have many different optimal dual witnesses.

For a constant state-value vector, `c=0`.  The zero multiplier vector is already dual feasible, and the objective is constant everywhere in the ambiguity set.  The checker handles this degeneracy explicitly rather than forcing an artificial active basis.

## 5. Independent checks

The repository exercises the two proof routes on several qualitatively different cases:

- contradictory probability intervals whose lower bounds sum above one;
- an explicit pair of incompatible halfspaces;
- maximum and minimum expectations over the symmetric three-state interval polytope;
- the skew four-state Huber contamination example, reproducing the exact maximum `33/20`;
- a constant objective with zero dual support.

One test deliberately caught an incorrect handwritten expected minimum.  Both independent rational routes returned

\[
\frac75
=\frac45(1)+\frac1{10}(2)+\frac1{10}(4),
\]

so the human expectation was corrected rather than altering the certificate machinery.

## 6. What the dual variables mean

A nonzero expectation-dual multiplier prices one active ambiguity restriction.  In that narrow mathematical sense the dual identifies which constraints support the worst-case expectation.  It should not be automatically interpreted as a physical price, causal effect, or parent-substrate resource cost.

Likewise a Farkas witness explains why the declared uncertainty assumptions are mutually inconsistent: a nonnegative combination of them yields the impossible inequality `0 < 0`.  It does not say which empirical assumption should be relaxed; that is a modeling decision outside the linear certificate.

## Boundaries

These certificates establish exact finite rational feasibility and LP optimality for the declared transformed system.  They do not establish:

- statistical validity of the ambiguity constraints;
- large-instance polynomial runtime for active-basis enumeration;
- uniqueness of primal or dual optimizers;
- robustness under source drift unless drift is explicitly encoded;
- a physical implementation map from internal expected bits to external resources;
- evidence for simulation.
