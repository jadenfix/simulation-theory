# Bayesian Boolean experiment geometry

## Scope

This lane changes the uncertainty criterion rather than the latent experiment family. A hidden model is a bit string `X in {0,1}^k` with a declared rational prior. Experiment `i` reveals coordinate `X_i`. The decision-relevant future source symbol is a Boolean function `f(X)`.

The coding interface is complete confusion K3, with only source symbols zero and one used. If the model is known, the realized symbol gets the one-bit leaf, so the model-informed oracle cost is one. Given only an observation cell, the Bayesian controller assigns the one-bit leaf to the more probable output.

## Exact cell formula

For an observation cell `C`, define

\[
m_b(C)=P(X\in C,f(X)=b),\qquad b\in\{0,1\}.
\]

The cell contributes

\[
\boxed{\min\{m_0(C),m_1(C)\}}
\]

to excess expected prefix length. Hence for observed coordinate set `S`,

\[
\boxed{
V(S)=\sum_C\min\{m_0(C),m_1(C)\}.
}
\]

This is also the Bayes classification error for predicting `f(X)` from `X_S`.

## Conditional-bias form under the uniform prior

Let

\[
g(X)=(-1)^{f(X)}.
\]

Inside one cell,

\[
\min\{P(f=0\mid X_S),P(f=1\mid X_S)\}
=
\frac{1-|E[g\mid X_S]|}{2}.
\]

Averaging over cells gives

\[
\boxed{
V(S)=\frac12\left(1-E|E[g\mid X_S]|\right).
}
\]

As observations are refined, `E[g|X_S]` is a martingale. Since absolute value is convex, conditional Jensen gives monotonicity:

\[
S\subseteq T\implies V(T)\le V(S).
\]

## Boolean influence appears exactly

Observe every coordinate except `i`. Each observation cell contains one cube edge `{x,x\oplus e_i}`. A cell contributes zero when the two endpoint outputs agree and one endpoint's uniform mass when they disagree. Therefore

\[
\boxed{
V([k]\setminus\{i\})=\frac12\operatorname{Inf}_i(f),
}
\]

where

\[
\operatorname{Inf}_i(f)=P(f(X)\ne f(X\oplus e_i)).
\]

This is an operational equality for the declared coding problem, not an analogy.

## Worst-case collapse versus Bayesian geometry

A worst-case cell criterion only asks whether some observational cell contains both outputs. For Boolean functions this can collapse to essential-variable support. Bayesian weighting preserves how much prior mass lies on ambiguous cells and how imbalanced those cells are.

For three uniform bits:

- parity has `V(S)=1/2` for every strict subset and zero only after all bits are observed;
- AND has the same support pattern but `V(S)=1/8` for every strict subset;
- majority has `V(empty)=1/2`, singleton and pair values `1/4`, and full-information value zero.

Thus identical essential support does not imply identical Bayesian experiment value.

## Möbius interaction hierarchy

The exact Boolean-lattice Möbius transform is

\[
\mu(S)=\sum_{T\subseteq S}(-1)^{|S|-|T|}V(T).
\]

Parity on three bits has only a constant term `1/2` and top-order term `-1/2`. AND has the same interaction support with magnitudes `1/8` and `-1/8`. Majority has nonzero first-, second-, and third-order coefficients.

So interaction order and interaction magnitude are separate objects, and both depend on the decision criterion and model prior.

## Prior sensitivity

For a nonuniform prior, the exact cell formula remains valid but the conditional-bias and influence identities must use the declared weighted law rather than uniform cube counting. The same truth table can therefore induce a different experiment-value geometry under a different prior.

## Public randomization boundary

This lane optimizes one Bayesian expected cost under one declared prior. Mixing deterministic policies with an independent public seed cannot beat the best deterministic Bayes policy because expected cost is linear in mixture weights: a convex combination cannot be smaller than its smallest component. This contrasts with minimax robust objectives, where public randomization can lower the worst model coordinate.

## Nonclaims

- The supplied model prior is not inferred or empirically validated by this theorem.
- Boolean influence here is tied to the declared uniform prior unless otherwise stated.
- The K3 coding reduction is an internal decision model, not a claim about physical computation.
- Möbius coefficients are interaction descriptors, not causal effects by themselves.
- None of these results is evidence that reality is simulated.
