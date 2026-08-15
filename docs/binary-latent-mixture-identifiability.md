# Binary latent-mixture identifiability through noisy emissions

## Scope

Each independent unit draws an unobserved binary latent label

\[
M\sim\operatorname{Bernoulli}(\theta),
\]

then emits one observation from a known categorical row `R_M`. The marginal observed law is

\[
Q_\theta=(1-\theta)R_0+\theta R_1.
\]

This layer asks when and how accurately the population mixing weight `theta` can be inferred from the observed emission distribution.

## Exact TV geometry

For any `theta, eta`,

\[
Q_\theta-Q_\eta=(\theta-\eta)(R_1-R_0).
\]

Therefore

\[
\boxed{
TV(Q_\theta,Q_\eta)
=|\theta-\eta|\,TV(R_0,R_1).
}
\]

Let

\[
d=TV(R_0,R_1).
\]

Because Bernoulli mixing-weight TV is simply `|theta-eta|`, `d` is the exact observation-channel identifiability coefficient.

If `d=0`, the rows are identical and every `theta` induces the same observed law. The mixing weight is completely unidentified from these emissions.

If `d>0`, an observed-law ambiguity radius `rho` transfers to

\[
\boxed{
|\theta-\theta_0|\le\rho/d.
}
\]

Thus observational noise amplifies latent-prior uncertainty by the inverse row separation.

## Binary-output inversion

For Bernoulli emissions with

\[
P(Y=1\mid M=0)=p_0,\qquad
P(Y=1\mid M=1)=p_1,
\]

we have

\[
q=P(Y=1)=p_0+(p_1-p_0)\theta.
\]

When `p0 != p1` and `q` lies on the mixture segment,

\[
\boxed{
\theta=\frac{q-p_0}{p_1-p_0}.
}
\]

## Fixed-sample uncertainty amplification

For `N` independent Bernoulli emissions, the empirical success frequency `q_hat` obeys

\[
E(\hat q-q)^2=\frac{q(1-q)}N\le\frac1{4N}.
\]

Markov gives a sufficient squared observed-law radius

\[
r_q^2=\frac1{4N\alpha}
\]

at failure probability `alpha`. Since the binary row separation is

\[
d=|p_1-p_0|,
\]

the corresponding latent-weight squared radius is

\[
\boxed{
r_\theta^2=\frac1{4N\alpha d^2}.}
\]

The inverse-square factor is the central conditioning result. Halving row separation multiplies the sample size required for the same latent-weight precision by four.

At `d=0`, no finite sample size repairs nonidentifiability because the observation laws are exactly equal.

## Relation to persistent latent models

This theorem assumes every independent unit receives a fresh latent draw. If one latent `M` is drawn once and many emissions are observed conditionally on that same persistent label, the data can identify that unit's `M` but do not constitute repeated draws from `theta`. The persistent-latent evidence-ceiling lane treats that different hierarchy.

## Nonclaims

- Emission rows are treated as known exactly. Estimating them introduces another uncertainty layer.
- The second-moment/Markov confidence radius is conservative and fixed-sample.
- The binary exact scaling does not automatically generalize to a scalar coefficient for arbitrary multi-component mixtures; rank and conditioning of the full channel matter.
- None of these identifiability results is evidence for simulation.
