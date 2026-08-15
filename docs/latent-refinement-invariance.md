# Latent refinement invariance: why raw world counts are representation-dependent

## 1. The refinement operation

Consider a finite latent mixture

\[
P(Y=y)=\sum_i \pi_i K_i(y).
\]

Choose one component `j`. Replace it by `r>=2` clones with exactly the same emission law `K_j` and positive split weights

\[
w_1,\ldots,w_r>0,
\qquad
\sum_a w_a=1.
\]

The clone priors are

\[
\pi_{j,a}=\pi_jw_a.
\]

Their total contribution is

\[
\sum_a \pi_jw_aK_j(y)
=\pi_jK_j(y).
\]

Therefore the one-view observed law is unchanged.

## 2. Every finite shared-latent iid view law is unchanged

Suppose one persistent latent component emits `v` conditionally iid observations. The joint law is

\[
P(y_1,\ldots,y_v)
=
\sum_i\pi_i\prod_{t=1}^vK_i(y_t).
\]

After refinement, the cloned contribution is

\[
\sum_a\pi_jw_a\prod_tK_j(y_t)
=
\pi_j\prod_tK_j(y_t).
\]

Hence for every finite `v`,

\[
\boxed{
P_{refined}(Y_{1:v})=P_{original}(Y_{1:v}).
}
\]

No amount of observation generated solely through the declared emission law can tell how many identical latent labels were used to represent that component.

This is stronger than ordinary finite-sample uncertainty: the two representations are exactly observationally equivalent.

## 3. Weighted category mass is refinement invariant

Suppose latent components carry a coarser category label, such as `A` or `B`. Define category probability by additive latent measure

\[
P(C=A)=\sum_{i:C_i=A}\pi_i.
\]

Splitting one `A` component preserves this quantity because the clone weights sum to the original weight:

\[
\boxed{
\sum_a\pi_jw_a=\pi_j.
}
\]

Probability measure is therefore invariant under observationally redundant refinement.

## 4. Uniform label counting is not invariant

Now instead assign equal mass to each latent label solely because it appears once in the representation.

Start with one `base` label and one `simulated` label. Uniform label counting gives

\[
P_{count}(simulated)=\frac12.
\]

Clone the simulated label into `r` positive-weight observationally identical labels. The observed process is exactly unchanged, but uniform label counting gives

\[
\boxed{
P_{count}(simulated)=\frac{r}{r+1}\to1.
}
\]

Clone the base label instead and the same unchanged observed process gives

\[
\boxed{
P_{count}(simulated)=\frac1{r+1}\to0.
}
\]

Thus raw label count can be pushed arbitrarily close to either zero or one by a change of latent bookkeeping that leaves every finite observable distribution unchanged.

The repository tests perform these refinements with strictly positive equal clone weights, so the effect does not rely on adding zero-probability dummy labels.

## 5. Refinement invariance as a consistency requirement

If two latent descriptions differ only by splitting an observationally identical state into weighted clones, a probability assigned to an observable coarse category should not depend on which description was chosen.

This motivates the consistency condition

\[
\boxed{
\mu(j)=\sum_a\mu(j,a)
}
\]

under refinement.

Ordinary additive probability measure satisfies it. Uniform-per-label counting generally does not.

This does not determine the correct measure by itself; it supplies a necessary invariance criterion for any measure intended to represent uncertainty rather than arbitrary model granularity.

## 6. Why this matters for simulation counting arguments

Arguments about "how many" simulated versus nonsimulated observers/worlds exist can accidentally depend on how latent possibilities are individuated.

If one observationally identical simulated world can be represented as one latent state, ten clone states, or a million clone states without changing any observable prediction, then a probability rule that rises merely because more labels were written down is not representation invariant.

The first-principles object that matters is not raw cardinality alone but a declared measure over possibilities together with a rule for how that measure behaves under refinement.

In particular,

\[
\boxed{
\text{number of latent labels}
\neq
\text{probability mass}
}
\]

unless an additional principle justifies equal mass per label and specifies a canonical, refinement-invariant way to define the labels.

This issue exists before questions about computational cost, matter, energy, or how many simulations a civilization could physically instantiate. Those physical questions may constrain a measure, but they do not remove the need to define one invariantly.

## 7. Relation to observer duplication

The theorem is deliberately about **model representation**, not about physically creating additional distinct observers. If a physical theory says two copies are genuinely distinct events with separately justified measure, their weights may add.

The problem occurs when a probability changes solely because the analyst refines one latent description into observationally identical bookkeeping states without adding any new empirical or physical distinction.

Therefore one must distinguish

\[
\boxed{
\text{physical multiplicity}
\quad\text{from}\quad
\text{representational multiplicity}.
}
\]

A simulation-theory probability argument that uses counting must state which one it is counting and why that count is invariant under harmless reparameterization.

## Nonclaims

- Refinement invariance does not uniquely determine an anthropic measure.
- The theorem does not say physical duplication is meaningless.
- It does not assume simulated and nonsimulated categories have identical emissions; only the cloned states within a refinement are identical.
- It does not establish or refute simulation theory.
- The finite code checks exact observational invariance; they do not infer a physical ontology from it.
