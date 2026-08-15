# Evidence ceilings for one persistent latent-model draw

## The sampling distinction

Let `M` be a latent model drawn once from a mixing-weight vector `pi`, after which an arbitrarily long transcript `Y` is generated from a model-conditional law `P(Y|M)`.

This is not the same sampling model as independently redrawing `M` before every observation. Repeated observations can identify the one persistent `M`, but they do not become repeated independent draws from the hyperdistribution `pi`.

## Exact likelihood-ratio identity

Consider two candidate mixing vectors `a` and `b`, with `b_m>0` for every component. For any transcript `y` with positive probability under `b`,

\[
P_a(y)=\sum_m a_m P_m(y),\qquad
P_b(y)=\sum_m b_mP_m(y).
\]

Therefore

\[
\frac{P_a(y)}{P_b(y)}
=
\sum_m
\frac{b_mP_m(y)}{P_b(y)}
\frac{a_m}{b_m}.
\]

The first factor is the posterior model probability under candidate `b`:

\[
w_m(y)=P_b(M=m\mid Y=y).
\]

Hence

\[
\boxed{
\frac{P_a(y)}{P_b(y)}
=
\sum_mw_m(y)\frac{a_m}{b_m}.
}
\]

The transcript Bayes factor is a convex average of the component prior-weight ratios. Consequently,

\[
\boxed{
\min_m\frac{a_m}{b_m}
\le
\frac{P_a(y)}{P_b(y)}
\le
\max_m\frac{a_m}{b_m}.
}
\]

The bound is independent of transcript length and of how complicated the model-conditional observation process is.

## Saturation

If model components are mutually singular and transcript `y_m` identifies component `m` exactly, then

\[
\frac{P_a(y_m)}{P_b(y_m)}=\frac{a_m}{b_m}.
\]

Thus the upper and lower prior-ratio bounds can be attained. Learning the persistent model perfectly does not generate more evidence about its population mixing weights than the weight ratio associated with that one model draw.

## Binary noiseless example

Let

\[
M\sim\operatorname{Bernoulli}(\theta),
\]

and suppose every subsequent observation is noiseless:

\[
Y_t=M.
\]

For every `T>=1`, transcript `Y_1=...=Y_T=1` has likelihood

\[
\boxed{P_\theta(1^T)=\theta.}
\]

So comparing `theta_a=3/4` to `theta_b=1/4` gives Bayes factor

\[
\boxed{3}
\]

whether one repeated outcome or one hundred repeated outcomes are observed.

If one instead writes

\[
P_\theta(1^T)=\theta^T,
\]

one has silently changed the causal model: this is the model in which a fresh latent `M_t~Bernoulli(theta)` is redrawn independently before every observation. Under that different model, the Bayes factor is indeed

\[
3^T.
\]

The exponential evidence is about the number of independent latent draws, not the number of conditionally repeated observations from one draw.

## Multiple independent units

If there are `N` genuinely independent units and each receives a fresh latent model draw

\[
M_u\sim\pi,
\]

then unit likelihood ratios multiply:

\[
\Lambda_{1:N}=\prod_{u=1}^N\Lambda_u.
\]

Thus log evidence about the mixing distribution can scale with the number of independent latent units. The relevant effective sample size for the hyperdistribution is the number of latent draws, not automatically the number of lower-level observations.

## Why this matters for simulation arguments

Many observer-count and simulation arguments contain hierarchical uncertainty:

- a world or simulator architecture is chosen;
- then many observations, observer moments, or events occur conditional on that one choice.

Those later observations can provide strong evidence about the chosen architecture if the architecture-specific laws differ. They do not automatically provide the same amount of evidence about a population-level prior over architectures.

Treating every observation moment as an independent draw from the architecture prior can exponentiate evidence that the declared causal model does not contain.

## Nonclaims

- The theorem does not say long transcripts cannot identify the persistent latent model.
- It does not say model mixing weights are unlearnable when multiple independent latent draws or additional hierarchical structure exist.
- Candidate mixing weights remain supplied model inputs unless a separate statistical model estimates them.
- The result is a general hierarchical sampling theorem, not evidence that reality is simulated.
