# Two shared-latent views collapse the continuous mixture gauge to label switching

## 1. One view has a continuous gauge

For one categorical observation,

\[
q=\pi K.
\]

An invertible row-stochastic matrix `A` gives the observationally equivalent factorization

\[
K'=AK,
\qquad
\pi'=\pi A^{-1},
\]

whenever `pi'` remains nonnegative. This creates a continuous ambiguity when both the latent prior and channel are unknown.

This layer asks what happens if one independent latent unit emits **two conditionally independent observations from the same latent component**.

## 2. Two-view moment

Let `Y_1,Y_2` be iid conditional on `M`. Their joint probability matrix is

\[
\boxed{
T
=
K^\top D_\pi K,
}
\]

where `D_pi=diag(pi)`.

Under the gauge,

\[
T'
=K'^\top D_{\pi'}K'
=K^\top A^\top D_{\pi'}AK.
\]

The one-view law is always preserved by construction. The two-view law generally is not.

## 3. Full affine rank means K has a right inverse

Probability rows all sum to one. Therefore any linear relation

\[
\sum_i c_iK_i=0
\]

automatically satisfies

\[
\sum_i c_i=0.
\]

So for probability vectors, affine independence of the rows is equivalent to ordinary linear independence of the rows.

Thus full affine rank `m-1` means

\[
\operatorname{rank}(K)=m.
\]

There exists a right inverse `R` with

\[
KR=I_m.
\]

## 4. Rigidity theorem

Assume

1. `K` has full affine row rank;
2. `pi'=pi A^{-1}` is strictly positive;
3. `A` is nonnegative, row-stochastic, and invertible;
4. the two-view law is preserved, `T'=T`.

Then

\[
K^\top
\left(A^\top D_{\pi'}A-D_\pi\right)
K=0.
\]

Multiplying by the right inverse on both sides gives

\[
\boxed{
A^\top D_{\pi'}A=D_\pi.
}
\]

Now inspect an off-diagonal entry `j != k`:

\[
0
=
\sum_i \pi'_i A_{ij}A_{ik}.
\]

Every term is nonnegative, and every `pi'_i` is strictly positive. Hence

\[
A_{ij}A_{ik}=0
\]

for every row `i` and every pair of distinct columns `j,k`.

Each row of `A` therefore contains at most one positive entry. But each row sums to one, so every row contains exactly one entry equal to one. Invertibility prevents two rows from selecting the same column.

Therefore

\[
\boxed{A\text{ is a permutation matrix}.}
\]

The continuous one-view gauge has collapsed to ordinary latent-label switching.

## 5. Exact binary example

Take

\[
\pi=(1/2,1/2),
\qquad
K=I_2,
\]

and the nonpermutation gauge

\[
A=
\begin{pmatrix}
3/4&1/4\\
0&1
\end{pmatrix}.
\]

The one-view law remains

\[
(1/2,1/2).
\]

Originally,

\[
T=
\begin{pmatrix}
1/2&0\\
0&1/2
\end{pmatrix}.
\]

After the gauge,

\[
\boxed{
T'=
\begin{pmatrix}
3/8&1/8\\
1/8&3/8
\end{pmatrix}.
}
\]

The second view immediately detects the otherwise invisible factorization change.

## 6. Why the assumptions matter

### Rank deficiency

If two component rows are identical, no number of conditionally iid views distinguishes which identical latent label generated the data. A nonpermutation gauge can then preserve the two-view law. Repository tests include this boundary.

### Zero latent mass

If a transformed latent component has zero prior mass, its row can change without affecting any observed moment. Strict positivity is therefore necessary for the off-diagonal argument to constrain every row of `A`. The tests include a full-rank binary channel with a zero-mass component and a nonpermutation gauge that preserves both views.

### Conditional independence and shared latent identity

The formula `T=K^T D_pi K` assumes both observations share the same latent component and are conditionally independent given it. Two unrelated observations with independently redrawn latent components instead have product law

\[
q\otimes q,
\]

which contains no more factorization information than the one-view marginal `q`.

This distinction mirrors the earlier persistent-latent sampling result: *which variable persists across observations* determines what repeated data can identify.

## 7. Consequence for experimental design

The one-view gauge says that more samples of the same marginal cannot identify both prior and channel. The two-view theorem identifies a concrete structural remedy:

\[
\boxed{
\text{repeat measurements that share latent identity}
\neq
\text{independent repetitions of the marginal mixture}.
}
\]

Correlated multi-view observations can expose latent structure that is exactly invisible in the marginal distribution.

For simulation-style arguments this is a warning and an opportunity. Observations useful for distinguishing latent world-generating mechanisms must contain cross-observation structure tied to a persistent latent cause. Merely accumulating more draws from an already-marginalized distribution cannot break a factorization gauge.

## Nonclaims

- The theorem concerns the specific gauge family `K'=AK, pi'=pi A^{-1}`; it is not a complete theorem for every latent-variable nonidentifiability.
- It assumes exact finite categorical laws.
- Label permutations remain observational symmetries.
- Two views do not solve arbitrary latent models with rank deficiency, zero-weight components, unknown dependence, or model misspecification.
- The result neither establishes nor refutes simulation theory.
