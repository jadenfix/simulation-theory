# Refinement-additive measure uniqueness on rational latent weights

## 1. From invariance to a functional equation

The latent-refinement layer showed that raw label counting changes when one observational state is split into positive-weight clones. We can ask a sharper question:

> If the mass assigned locally to a latent component depends only on its probability weight, which local rules survive arbitrary rational refinement?

Let

\[
\mu:\mathbb Q\cap[0,1]\to\mathbb R_{\ge0}
\]

be normalized by

\[
\mu(1)=1
\]

and additive under every finite rational split:

\[
\boxed{
\mu(w)=\sum_{a=1}^r\mu(w_a)
\quad\text{whenever}\quad
w_a\ge0,\ \sum_aw_a=w.
}
\]

## 2. Rational uniqueness theorem

Split unit mass into `n` equal pieces:

\[
1=\underbrace{\frac1n+\cdots+\frac1n}_{n\text{ terms}}.
\]

Additivity and normalization imply

\[
1=n\mu(1/n),
\]

so

\[
\mu(1/n)=1/n.
\]

For any rational `p/n` in `[0,1]`, split it into `p` pieces of size `1/n`:

\[
\mu(p/n)=p\mu(1/n)=p/n.
\]

Therefore

\[
\boxed{
\mu(w)=w
\qquad
\forall w\in\mathbb Q\cap[0,1].
}
\]

No continuity assumption is needed on the rational domain. Normalization plus exact refinement additivity already forces ordinary probability weight.

This is a characterization of **local weight-only rules**. It does not rule out measures that depend on additional physical, computational, causal, or observer-specific structure.

## 3. Escort-weight family

A common family of alternative local scores is

\[
s_\gamma(w)=w^\gamma.
\]

For `gamma=0` and positive `w`, every represented label receives score one, reproducing raw label counting. For `gamma=1`, the score is ordinary probability weight.

Split a positive component of weight `w` into `r` equal clones. Their total score becomes

\[
r\left(\frac wr\right)^\gamma
=
\boxed{r^{1-\gamma}w^\gamma}.
\]

Thus

\[
\boxed{
\text{equal-clone refinement invariance occurs exactly at }\gamma=1.
}
\]

For `gamma<1`, cloning increases the category score. For `gamma>1`, cloning decreases it.

## 4. Exact two-category phase reversal

Start with equal category weights

\[
\pi=(1/2,1/2)
\]

for `base` and `simulated`. Refine only the simulated half into `r` equal positive clones.

Under `gamma=0`,

\[
P_0(simulated)=\frac r{r+1}\to1.
\]

Under `gamma=1`,

\[
\boxed{P_1(simulated)=1/2}
\]

for every `r`.

Under `gamma=2`,

\[
P_2(simulated)=\frac1{r+1}\to0.
\]

So the **same observationally null refinement** can push an inferred category mass toward one, leave it unchanged, or push it toward zero depending only on the analyst's non-invariant local scoring convention.

At `r=20`, repository tests obtain exactly

\[
\boxed{
P_0=20/21,
\qquad
P_1=1/2,
\qquad
P_2=1/21.
}
\]

## 5. Consequence for observer/world measures

If a proposed probability over latent worlds or observers is meant to depend only on pre-existing probability weights, then refinement invariance is highly restrictive: on rational weights it forces the linear rule.

If a different measure is desired, the extra weighting must come from **additional declared structure**, not merely from how many equivalent labels happen to appear in a model description.

For example, one might attempt to weight by physical multiplicity, computational resources, causal influence, observer moments, algorithmic description length, or some other quantity. Those proposals require their own invariance and identifiability analysis. The present theorem does not endorse any of them.

The main point is narrower:

\[
\boxed{
\text{representation alone cannot supply probability mass consistently.}
}
\]

## 6. Simulation-theory relevance

A statement such as "there are many more simulated observers" does not by itself define a probability until "more" is tied to a measure that survives harmless refinement.

Duplicating a latent label in a mathematical description is not the same operation as physically instantiating another observer with independently justified measure. Any counting argument must specify why its units are canonical and why splitting or merging observationally equivalent descriptions cannot arbitrarily alter the result.

The rational uniqueness theorem supplies one clean baseline: if the only input to local mass is an already-declared probability weight and refinement must be additive, the unique normalized answer is that weight itself.

## Nonclaims

- The theorem does not uniquely characterize measures that depend on structure beyond local probability weight.
- It does not prove that physical observer copies should receive any particular weight.
- Integer-power escort scores are examples, not an exhaustive taxonomy of nonadditive measures.
- The result does not establish or refute simulation theory.
