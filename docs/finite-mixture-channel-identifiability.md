# Finite latent-mixture channels: affine identifiability and inverse TV conditioning

## Scope

Let a latent component `M` take values in `{1,...,m}` with prior `pi`. Conditional on `M=i`, one observed categorical draw has known law `K_i` on an `n`-symbol alphabet. The observed mixture law is

\[
q=\pi K=\sum_{i=1}^m \pi_i K_i.
\]

This layer asks a structural question before attempting statistical estimation:

> If the observed law `q` were known exactly, would it uniquely determine the latent mixing weights `pi`?

That is an identifiability question, not a sample-size question.

## 1. Affine-rank criterion

Choose row `K_m` as a reference and define

\[
D_i=K_i-K_m,\qquad i=1,\ldots,m-1.
\]

For two priors `pi,pi'`, put `delta=pi-pi'`. Because both priors sum to one,

\[
\sum_i\delta_i=0,
\]

so writing `x=(delta_1,...,delta_{m-1})`,

\[
\delta K=xD.
\]

Therefore

\[
\boxed{
\pi K=\pi'K\Longleftrightarrow xD=0.
}
\]

The mixture map is injective on the probability simplex exactly when

\[
\boxed{
\operatorname{rank}(D)=m-1.
}
\]

Equivalently, the emission rows `K_1,...,K_m` are affinely independent. In particular, an `n`-symbol observed alphabet cannot identify more than `n` affinely independent categorical component laws.

## 2. Rank failure gives an explicit collision

If `rank(D)<m-1`, choose nonzero rational `x` with

\[
xD=0.
\]

Extend it to the zero-sum latent perturbation

\[
\delta=(x_1,\ldots,x_{m-1},-\sum_i x_i).
\]

Starting from the interior uniform prior `u=(1/m,...,1/m)`, choose sufficiently small rational `epsilon>0` and define

\[
\pi_+=u+\epsilon\delta,
\qquad
\pi_-=u-\epsilon\delta.
\]

Both are valid distinct priors and

\[
\boxed{
\pi_+K=\pi_-K.
}
\]

The implementation constructs and validates this collision rather than returning only a Boolean rank flag.

## 3. Exact coordinate reconstruction when rank is full

Let `r=m-1`. Full row rank guarantees at least one set `S` of `r` observed coordinates for which the square minor

\[
A=D_{[:,S]}
\]

is invertible. For an observed difference

\[
z=\delta K=xD,
\]

write `y=z_S`. Then

\[
y=xA,
\qquad
\boxed{x=yA^{-1}}.
\]

The final latent coordinate is restored by the zero-sum constraint. Thus one invertible coordinate minor gives an exact rational left inverse on the channel tangent image.

The repository enumerates coordinate minors below an explicit cap and keeps the searched minor with the smallest certified TV constant.

## 4. A fail-closed TV conditioning certificate

Let `R` be the matrix mapping selected observed coordinates `y` to the full zero-sum latent difference `delta`. If

\[
L=\max_i\|R_{i,:}\|_1,
\]

then

\[
\|\delta\|_1\le L\|y\|_1.
\]

Because the full observed difference `z` sums to zero,

\[
|z_j|\le TV(z)
\]

for one selected coordinate, while for two or more selected coordinates

\[
\|y\|_1\le\|z\|_1=2TV(z).
\]

Hence with `r=m-1`,

\[
\boxed{
TV(\pi,\pi')
\le
C_S\,TV(\pi K,\pi'K),
\qquad
C_S=\frac{\min(2,r)}2L.
}
\]

This is a certified inverse-sensitivity bound. It can be conservative because it discards unselected observed coordinates.

For a binary latent mixture with a binary observed alphabet, it reduces to

\[
C=\frac1{TV(K_1,K_2)},
\]

matching the exact coefficient from the binary-mixture layer.

For the identity `K3` channel, however, the true inverse constant is one because the channel preserves TV exactly, while the generic coordinate-minor certificate returns two. The test suite records this deliberately: a safe certificate must not be mislabeled as an optimal modulus.

## 5. The exact global conditioning object

There is a sharper first-principles quantity. Define

\[
\alpha(K)
=
\inf_{\substack{\delta\ne0\\\sum_i\delta_i=0}}
\frac{TV(\delta K)}{TV(\delta)}.
\]

When the channel is identifiable, the optimal inverse TV constant is

\[
\boxed{C_*(K)=\frac1{\alpha(K)}}.
\]

Normalize any nonzero zero-sum `delta` so `TV(delta)=1`. Its positive and negative parts are probability distributions `u` and `v` on disjoint latent supports `P` and `N`, and

\[
\delta K=uK-vK.
\]

Conversely, any two probability mixtures supported on disjoint nonempty latent sets define such a normalized zero-sum direction. Therefore

\[
\boxed{
\alpha(K)
=
\min_{\substack{P,N\ne\varnothing\\P\cap N=\varnothing}}
\operatorname{dist}_{TV}
\left(
\operatorname{conv}\{K_i:i\in P\},
\operatorname{conv}\{K_j:j\in N\}
\right).
}
\]

This gives a geometric interpretation that pairwise row separation misses: with three or more components, the dangerous ambiguity can occur between **mixtures of rows**, not merely between individual rows.

Affine dependence is exactly the zero-separation boundary. If rows are affinely dependent, two disjoint-support convex mixtures coincide and `alpha(K)=0`. If rows are affinely independent, disjoint faces of the row simplex are disjoint compact polytopes, so every such distance is positive and `alpha(K)>0`.

The current code certifies a computable upper bound on `C_*` through coordinate inversion. Exact optimization of the disjoint-face separation is intentionally left as the next layer rather than silently equating the two.

## 6. Why this matters for hierarchical evidence

The preceding persistent-latent result separates repeated observations inside one latent unit from independent draws of latent units. This layer adds another prerequisite: even with genuinely independent units, the population mixing distribution can only be recovered from emissions to the extent that the emission channel is identifiable and well-conditioned.

Thus the chain is

\[
\boxed{
\text{independent latent units}
+\text{identifiable channel}
+\text{finite-sample calibration}
\Longrightarrow
\text{controlled latent-prior uncertainty}.
}
\]

Removing any term breaks the inference:

- within-unit repetition does not create new latent draws;
- affine dependence makes distinct priors observationally identical even with infinite data;
- poor conditioning amplifies observed-law uncertainty;
- finite data still require an explicit confidence argument.

## Nonclaims

- Component emission rows are treated as known in this layer.
- The selected-coordinate conditioning constant is not claimed optimal.
- Identifiability does not imply practical estimability at small sample size.
- A finite alphabet is an explicit model restriction.
- No rank or conditioning result is evidence for simulation, a simulator, or a parent substrate.
