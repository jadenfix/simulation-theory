# Polyhedral ambiguity, minimax regret, statistical calibration, and block rate

This document separates four questions that are easy to conflate:

1. **Geometry:** which source laws are considered possible?
2. **Decision criterion:** worst absolute expected cost, or regret relative to a law-specific oracle?
3. **Statistics:** why should the true law belong to the ambiguity set?
4. **Coding horizon:** is the object one-shot prefix length or a long-run block rate?

Keeping those layers separate is essential.  A mathematically exact optimizer over a poorly justified ambiguity set does not provide statistical coverage, and a finite-sample confidence set does not by itself say which code is optimal.

## 1. Arbitrary rational ambiguity polytopes

Let the finite source state be in `[n]`.  The most general ambiguity set treated in this lane is

\[
\mathcal U=\{q\in\Delta_{n-1}:Aq\le b\},
\]

where every entry of `A` and `b` is rational.

The implementation eliminates

\[
q_n=1-\sum_{j<n}q_j
\]

and appends the simplex halfspaces.  In the remaining `d=n-1` coordinates, a point is a vertex exactly when its active constraint normals span `R^d`.  Every `d`-row active basis is solved in exact rational arithmetic, every omitted inequality is checked, and degenerate duplicate vertices are canonicalized.

This gives a single reusable geometry for:

- interval probabilities;
- exact equalities encoded by paired inequalities;
- moment or feature bounds;
- Huber contamination sets;
- the full simplex;
- intersections of several independently motivated restrictions.

The exponential active-basis search is deliberately bounded and fails closed.  It is a finite exact certificate, not a large-scale LP runtime claim.

## 2. Linear objectives need only the vertices

For any fixed value vector `g`,

\[
q\mapsto q^Tg
\]

is linear.  Hence on a nonempty compact polytope,

\[
\max_{q\in\mathcal U}q^Tg
=
\max_{v\in\operatorname{vert}(\mathcal U)}v^Tg,
\]

and similarly for the minimum.

The polyhedral expectation certificate records every vertex value, the exact optimum, and an attaining vertex.

## 3. Deterministic robust coding over a polytope

A deterministic zero-error binary prefix code `c` induces a state-length vector `ell_c`.  Its expected cost under source law `q` is

\[
L_c(q)=q^T\ell_c.
\]

Therefore

\[
\min_c\max_{q\in\mathcal U}L_c(q)
=
\min_c\max_{v\in\operatorname{vert}(\mathcal U)}v^T\ell_c.
\]

Once the ambiguity vertices are known, this becomes the existing finite-scenario exact robust coding problem.  The code universe still exhausts every bounded proper independent-set partition and every complete binary prefix shape.

## 4. Regret is a different robust objective

Define the source-law-specific oracle

\[
L^*(q)=\min_d q^T\ell_d.
\]

The regret of fixed code `c` is

\[
R_c(q)=L_c(q)-L^*(q)
=
\max_d q^T(\ell_c-\ell_d).
\]

This is a pointwise maximum of linear functions and is therefore convex in `q`.

A convex function on a compact polytope attains a maximum at at least one vertex.  Thus

\[
\boxed{
\max_{q\in\mathcal U}R_c(q)
=
\max_{v\in\operatorname{vert}(\mathcal U)}
\bigl[L_c(v)-L^*(v)\bigr].
}
\]

This is why minimax regret over the *entire continuous polytope* reduces exactly to a finite vertex problem.

The criterion matters.  Absolute minimax length protects total cost.  Minimax regret protects distance from a clairvoyant law-specific design.  They need not choose the same code.

## 5. Shared codebook randomness under polyhedral ambiguity

Let a source-independent common seed choose code `c` with probability `x_c`.  At ambiguity vertex `v`, expected length is

\[
\sum_cx_cL_c(v).
\]

For absolute cost the finite game matrix is

\[
A_{vc}=L_c(v).
\]

For regret it is

\[
A^{\rm reg}_{vc}=L_c(v)-L^*(v).
\]

The exact rational zero-sum solver then computes

\[
\min_x\max_v\sum_cx_cA_{vc}
\]

or its regret analogue.  The returned shared value is always no larger than the best deterministic value because pure codebooks remain feasible mixtures.

For regret, the continuous adversary again reduces to vertices because

\[
q\mapsto q^Tz-L^*(q)
\]

is convex for every mixed expected length vector `z`.

## 6. Symmetric K3 interval example

Take the complete graph `K3` and

\[
1/10\le q_i\le4/5.
\]

The exact ambiguity vertices are

\[
(4/5,1/10,1/10),
(1/10,4/5,1/10),
(1/10,1/10,4/5).
\]

For absolute expected length,

\[
V_{\rm det}=19/10,
\qquad
V_{\rm mix}=5/3,
\]

so shared randomness gains

\[
19/10-5/3=7/30.
\]

At every skew vertex the law-specific Huffman optimum is `6/5`.  Therefore for minimax regret,

\[
R_{\rm det}=7/10,
\qquad
R_{\rm mix}=7/15.
\]

The same ambiguity geometry produces a different numerical game when the objective changes.

## 7. Huber contamination as a polytope

For nominal law `p` and contamination fraction `epsilon`,

\[
q=(1-\epsilon)p+\epsilon r,
\qquad r\in\Delta_{n-1}.
\]

Equivalently,

\[
q_i\ge(1-\epsilon)p_i
\]

with the simplex equality.  The implementation uses the equivalent interval representation

\[
(1-\epsilon)p_i
\le q_i\le
(1-\epsilon)p_i+\epsilon.
\]

Its vertices are exactly

\[
(1-\epsilon)p+\epsilon e_i.
\]

For the skew `K4` law

\[
p=(7/10,1/10,1/10,1/10),
\qquad \epsilon=1/10,
\]

and state lengths `(1,2,3,3)`, the general polyhedral expectation solver returns

\[
33/20,
\]

matching the specialized Huber calculation.

This cross-check matters because it shows the named ambiguity model is a special case of the generic polyhedral geometry rather than a separately hard-coded answer.

## 8. Statistical calibration is not geometry

An ambiguity set becomes a confidence set only after adding a sampling model.

Assume `n` i.i.d. draws from one stationary categorical law `p` on an alphabet of size `k`, with empirical law `p_hat`.  The Weissman--Ordentlich--Seroussi--Verdu--Weinberger inequality gives the distribution-free finite-sample bound

\[
\Pr\bigl(\|\hat p-p\|_1\ge\epsilon\bigr)
\le
(2^k-2)e^{-n\epsilon^2/2}.
\]

Since

\[
\operatorname{TV}(\hat p,p)=\frac12\|\hat p-p\|_1,
\]

we obtain

\[
\Pr\bigl(\operatorname{TV}(\hat p,p)\ge\rho\bigr)
\le
(2^k-2)e^{-2n\rho^2}.
\]

Thus a sufficient radius for failure probability `delta` is

\[
\rho_\delta
=
\sqrt{
\frac{
\log((2^k-2)/\delta)
}{2n}
}.
\]

The logarithm and square root are usually irrational.  The implementation therefore computes them at high Decimal precision and rounds **outward** onto a declared rational grid.  The resulting rational ball is at least as large as the numerically evaluated threshold, and the exact rational robust-coding machinery can consume it directly.

The logical chain is:

\[
\text{i.i.d. samples}
\Rightarrow
\text{finite-sample TV confidence ball}
\Rightarrow
\text{exact robust code on that ball}.
\]

With probability at least `1-delta` under the sampling assumptions, the true law lies in the calibrated ball.  Conditional on that event, the robust value upper-bounds the selected code's true expected one-shot length.

This statement does **not** survive arbitrary temporal dependence, adaptive censoring, covariate shift, or source drift.  Those require a different confidence process or ambiguity model.

## 9. Why small data can correctly collapse to full-simplex robustness

If the concentration radius exceeds one, TV geometry cannot become larger than the whole simplex.  The implementation clips the ambiguity radius to one and records that clipping occurred.

That is not a numerical failure.  It means the available data plus requested confidence level do not justify excluding any categorical law.  The downstream robust problem should then reduce to hard full-simplex protection rather than manufacture precision.

## 10. One-shot prefix length versus block rate

For a complete confusion graph with source prior `p`, every state requires a distinct message.  For an i.i.d. block of length `m`, every sequence in `[k]^m` is likewise distinct and has product probability

\[
p(x_1,\ldots,x_m)=\prod_{t=1}^mp_{x_t}.
\]

The exact block module enumerates this rational product distribution below a hard sequence cap and applies exact Huffman coding.

For positive support,

\[
H(P^m)
\le
L_H(P^m)
<
H(P^m)+1.
\]

Since

\[
H(P^m)=mH(P),
\]

we get

\[
\boxed{
H(P)
\le
\frac{L_H(P^m)}m
<
H(P)+\frac1m.
}
\]

Therefore a one-shot prefix redundancy of nearly one bit does not imply a one-bit-per-step asymptotic penalty.  Block coding amortizes the prefix integrality overhead.

For non-complete confusion graphs, a multi-letter theorem requires declaring the block side-information and query model and deriving the corresponding graph product.  The repository intentionally does not jump from the complete-graph product source to a general graph-entropy claim.

## 11. Research consequences

The robustness hierarchy is now:

\[
\text{one trusted prior}
\subset
\text{finite prior scenarios}
\subset
\text{named continuous sets (TV, Huber)}
\subset
\text{arbitrary rational polytopes}.
\]

Orthogonal to that geometry are two other axes:

\[
\text{absolute loss}
\quad\text{vs}\quad
\text{regret},
\]

and

\[
\text{declared ambiguity}
\quad\text{vs}\quad
\text{statistically calibrated ambiguity}.
\]

Finally, the horizon axis distinguishes

\[
\text{one-shot expected prefix length}
\quad\text{from}\quad
\text{multi-letter amortized rate}.
\]

A simulation-resource argument that does not say where it lies on all three axes is under-specified.

## Boundaries

These results do not establish:

- that any physical simulator uses prefix coding;
- that a source law is i.i.d. unless the data-generating model says so;
- confidence under arbitrary drift or dependent observations;
- a general non-complete-graph entropy rate;
- queueing delay, peak bandwidth, or parent-substrate energy from expected bits;
- evidence that reality is simulated.

The purpose is narrower: make the mathematical dependency chain explicit enough that changing one assumption changes only the layer that actually depends on it.
