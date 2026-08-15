# Exact global TV modulus for finite latent-mixture channels

## 1. Why affine rank is not enough

Affine independence answers a binary question: can two distinct latent priors produce exactly the same observed law?

For inference, the harder question is quantitative:

> How much can the observation channel shrink a nonzero latent-prior difference?

For a zero-sum latent perturbation `delta`, define

\[
\alpha(K)
=
\inf_{\delta\ne0,\,\sum_i\delta_i=0}
\frac{TV(\delta K)}{TV(\delta)}.
\]

Then every pair of latent priors satisfies

\[
TV(\pi K,\pi'K)
\ge
\alpha(K)TV(\pi,\pi'),
\]

and, when `alpha(K)>0`,

\[
\boxed{
TV(\pi,\pi')
\le
C_*(K)TV(\pi K,\pi'K),
\qquad
C_*(K)=\alpha(K)^{-1}.
}
\]

`C_*` is the globally optimal inverse TV Lipschitz constant.

## 2. Positive/negative decomposition

Normalize a nonzero zero-sum perturbation so

\[
TV(\delta)=1.
\]

Its positive and negative parts each have total mass one. Therefore

\[
\delta=u-v,
\]

where `u` and `v` are probability vectors with disjoint supports `P` and `N`.

Thus

\[
TV(\delta K)=TV(uK,vK).
\]

Conversely every pair of probability vectors with disjoint supports produces a zero-sum perturbation of latent TV one. Hence

\[
\boxed{
\alpha(K)
=
\min_{P\cap N=\varnothing\atop P,N\ne\varnothing}
\min_{u\in\Delta(P),\,v\in\Delta(N)}
TV(uK,vK).
}
\]

Equivalently,

\[
\boxed{
\alpha(K)
=
\min_{P\cap N=\varnothing\atop P,N\ne\varnothing}
\operatorname{dist}_{TV}
\bigl(\operatorname{conv}K_P,\operatorname{conv}K_N\bigr).
}
\]

The dangerous direction can therefore be a **mixture versus mixture** ambiguity. Minimum pairwise row distance is not enough once there are at least three latent components.

## 3. Turning one face distance into a finite zero-sum game

For probability laws `p,q` on a finite observed alphabet,

\[
TV(p,q)=\max_{A}[p(A)-q(A)],
\]

where `A` ranges over observed events.

Fix disjoint latent faces `P,N`. For `u in Delta(P)` and `v in Delta(N)`,

\[
TV(uK,vK)
=
\max_A
\left[
\sum_{i\in P}u_iK_i(A)
-
\sum_{j\in N}v_jK_j(A)
\right].
\]

Introduce a joint distribution `lambda` on ordered pairs `(i,j) in P x N`. Its marginals are `u` and `v`, and the event payoff is

\[
\sum_{i,j}\lambda_{ij}[K_i(A)-K_j(A)].
\]

Every pair `(u,v)` admits a product coupling, and every coupling has marginals `(u,v)`. Therefore

\[
\boxed{
\operatorname{dist}_{TV}(\operatorname{conv}K_P,\operatorname{conv}K_N)
=
\min_{\lambda\in\Delta(P\times N)}
\max_A
\sum_{i,j}\lambda_{ij}[K_i(A)-K_j(A)].
}
\]

This is exactly a finite zero-sum game. The implementation reuses the repository's exact rational primal/dual support enumerator. Each face certificate therefore contains both the minimizing latent mixtures and a zero-duality-gap adversarial event mixture.

## 4. Global exactness

There are finitely many disjoint nonempty face pairs and finitely many observed events. Enumerating both below explicit caps and taking the smallest exact game value gives `alpha(K)` exactly.

The solver returns

- every bounded disjoint-face certificate;
- the minimizing face pair;
- exact `alpha(K)`;
- `C_*(K)=1/alpha(K)` when positive;
- the earlier affine-rank/coordinate-inverse certificate for comparison.

For an identifiable channel the conservative coordinate-minor constant `C_coord` must satisfy

\[
\boxed{C_{coord}\ge C_*}.
\]

Identity `K3` is the clean boundary:

\[
\alpha(I_3)=1,
\qquad
C_*(I_3)=1,
\qquad
C_{coord}=2.
\]

The global solver removes that factor-two artifact.

## 5. Pairwise separation can be radically misleading

Consider

\[
K_0=(1,0,0),
\qquad
K_1=(0,1,0),
\]

and

\[
K_2=\left(\frac12,\frac12-\varepsilon,\varepsilon\right),
\qquad
0<\varepsilon<\frac12.
\]

Every pair of rows remains well separated:

\[
\min_{i\ne j}TV(K_i,K_j)=\frac12.
\]

But the midpoint mixture of the first two rows is

\[
\frac12K_0+\frac12K_1
=\left(\frac12,\frac12,0\right),
\]

which lies only TV distance `epsilon` from `K_2`. Therefore

\[
\boxed{
\alpha(K)=\varepsilon,
\qquad
C_*(K)=\varepsilon^{-1}.
}
\]

At `epsilon=1/10`, all component pairs are at least `1/2` apart, yet latent-prior uncertainty can be amplified by a factor of ten.

As `epsilon -> 0`, the rows remain pairwise separated while the mixture problem approaches affine nonidentifiability. At `epsilon=0`, `K_2` is exactly the midpoint of `K_0,K_1` and `alpha(K)=0`.

This is a key distinction:

\[
\boxed{
\text{component distinguishability}
\not\Rightarrow
\text{mixture-weight conditioning}.
}
\]

## 6. Relation to ordinary channel contraction

The usual forward TV contraction coefficient asks how much a channel can preserve or contract differences over all input distributions. Here the relevant object is the **minimum** contraction restricted to the zero-sum tangent space of latent mixing weights.

A channel can simultaneously have strong forward distinguishability in some directions and near-zero separation in another mixture direction. For hierarchical inference, the weakest identifiable direction controls worst-case inversion.

This is why using only maximum pairwise distinguishability, average classification accuracy, or a single mutual-information number can miss the conditioning bottleneck.

## 7. Statistical consequence

Suppose a finite-sample procedure gives an observed-law confidence radius `rho_obs`. The sharp deterministic transfer is

\[
\boxed{
rho_{latent}
\le
\min\{1,C_*(K)\rho_{obs}\}.
}
\]

Thus sample complexity inherits a conditioning penalty. Under second-moment radii scaling as `N^{-1/2}`, maintaining a fixed latent-prior radius requires sample size proportional to

\[
\boxed{C_*(K)^2=\alpha(K)^{-2}.}
\]

Near affine dependence this diverges even though every individual component pair may still look easy to classify.

## Nonclaims

- Channel rows are known exactly in this layer.
- The face/event enumeration is exponential and bounded by explicit caps.
- `alpha(K)` is an inverse-conditioning quantity, not a posterior probability.
- A small `alpha(K)` does not imply that the latent models are physically similar; it says mixtures of their declared emission laws can be observationally close.
- None of these finite-channel results is evidence for simulation or for any particular simulator architecture.
