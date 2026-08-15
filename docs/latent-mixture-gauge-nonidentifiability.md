# Joint prior/channel nonidentifiability as a latent-mixture gauge

## 1. Conditional identifiability is not joint identifiability

The finite-mixture channel results answer:

> If the component emission channel `K` is fixed and known, can the latent mixing weights `pi` be recovered from `q=pi K`?

Full affine row rank can make the answer yes.

A different question is:

> Can one observational mixture law `q` identify both `pi` and `K` when both are unknown?

In general the answer is no, even with infinite data for `q` and even when both candidate channels have fully affinely independent rows.

## 2. Exact gauge transformation

Let

\[
q=\pi K.
\]

Take any invertible row-stochastic latent matrix `A` and define

\[
\boxed{
K'=AK,
\qquad
\pi'=\pi A^{-1}.
}
\]

Because `A` is row-stochastic,

\[
A\mathbf 1=\mathbf 1,
\qquad
A^{-1}\mathbf 1=\mathbf 1,
\]

so `pi'` still sums to one. Whenever `pi'` is nonnegative, it is a valid prior. The transformed channel is automatically valid because every row of `AK` is a convex mixture of rows of `K`.

Then

\[
\boxed{
\pi'K'
=\pi A^{-1}AK
=\pi K
=q.
}
\]

Thus an entire latent reparameterization can be observationally invisible.

Permutation matrices are the familiar label-switching symmetry. The important point here is that `A` need not be a permutation: it can mix latent components and simultaneously compensate the mixing weights.

## 3. Full affine rank survives the gauge

Append a column of ones to the channel rows:

\[
\widetilde K=[K\mid\mathbf1].
\]

The rows of `K` are affinely independent exactly when

\[
\operatorname{rank}(\widetilde K)=m.
\]

Since `A 1=1`,

\[
\widetilde K'
=[AK\mid\mathbf1]
=A[K\mid\mathbf1]
=A\widetilde K.
\]

Invertibility of `A` therefore gives

\[
\boxed{
\operatorname{rank}(\widetilde K')
=
\operatorname{rank}(\widetilde K).
}
\]

So the ambiguity is not caused by using an internally nonidentifiable channel. Both factorizations can separately identify their own mixing weights **conditional on knowing which channel is correct**, while the one-view observational law cannot identify the channel/prior factorization jointly.

## 4. There is a local continuum, not merely one counterexample

Suppose `pi` is in the interior of the latent simplex and `K` has at least two affinely independent rows. Choose a nonidentity row-stochastic matrix `B` and form

\[
A_t=(1-t)I+tB.
\]

For sufficiently small positive `t`, `A_t` remains invertible. Moreover,

\[
\pi A_t^{-1}\to\pi
\]

as `t -> 0`. Because `pi` is strictly positive, the transformed prior remains inside the simplex for all sufficiently small `t`.

Hence there is a continuum of nontrivial observationally equivalent factorizations arbitrarily close to the original one:

\[
\boxed{
(\pi_t,K_t)
=
(\pi A_t^{-1},A_tK),
\qquad
\pi_tK_t=\pi K.
}
\]

This is a local structural nonidentifiability, not a finite-sample problem.

## 5. Exact binary witness

Start from

\[
\pi=\left(\frac12,\frac12\right),
\qquad
K=I_2,
\]

and

\[
A=
\begin{pmatrix}
3/4&1/4\\
0&1
\end{pmatrix}.
\]

Then

\[
\pi'=\left(\frac23,\frac13\right),
\qquad
K'=A,
\]

but both give

\[
\boxed{q=(1/2,1/2).}
\]

Both channels have affine rank one. The prior changed, the emission rows changed, and the complete one-view observed law did not.

An independent second witness uses

\[
\pi_1=(1/2,1/2),
\quad
K_1=((3/4,1/4),(1/4,3/4)),
\]

versus

\[
\pi_2=(1/4,3/4),
\quad
K_2=((1,0),(1/3,2/3)).
\]

Again both produce `(1/2,1/2)` and both channels have distinct rows.

## 6. What breaks the gauge

The gauge exists because one marginal mixture law supplies only the product `pi K`. Additional structure can break or reduce it, for example:

- labeled component calibration data that fixes rows of `K`;
- multiple conditionally independent views sharing the same latent component;
- interventions whose action on components is known;
- anchor outcomes or separability restrictions;
- parametric constraints on component laws;
- temporal structure that ties emissions across observations in a known way;
- external information fixing some mixing weights or component semantics.

The important requirement is not merely "more data." It is **data whose causal or structural relationship to the latent factorization is different**.

## 7. Consequence for simulation-style Bayesian arguments

A posterior over hypotheses requires likelihoods. If both

1. the prior mass assigned to candidate simulator/world classes, and
2. the observation law emitted by each class

are allowed to move freely, then the decomposition of the observed distribution into those objects is not identified by the observations alone.

The equation

\[
P(O)=\sum_m P(M=m)P(O\mid M=m)
\]

does not let one infer both factors from the left-hand side without additional assumptions. Infinite precision on `P(O)` does not fix that structural problem.

Therefore a large Bayes factor is only meaningful relative to a declared likelihood family and prior/hyperprior semantics. Treating both as freely adjustable after seeing the data introduces an observational gauge rather than additional evidence.

## Nonclaims

- The gauge does not say latent-variable models are useless; it identifies what extra structure they need.
- It does not apply once enough externally justified constraints fix the latent representation.
- The transformation is an observational equivalence, not a claim that two latent descriptions are physically identical.
- None of this establishes or refutes simulation theory.
