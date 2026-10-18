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

Enlarging `P` or `N` only enlarges the hulls, so the minimum is attained on complementary partitions `P\cup N=\{1,\dots,m\}`. When the rows are affinely independent the hulls are faces of the simplex `conv{K_i}`; otherwise they are hulls of row subsets.

The dangerous direction can therefore be a **mixture versus mixture** ambiguity. Minimum pairwise row distance is not enough once there are at least three latent components.

**Prior art.** This identity is an elementary consequence of the Jordan decomposition of a zero-sum vector. For affinely independent rows, `alpha(K)` is the facial distance of the simplex `conv{K_i}` taken in the TV norm. Gutman and Pena define the facial distance for an arbitrary norm, and their Proposition 1 ("The condition of a function relative to a polytope", arXiv:1802.00271; later "The condition number of a function relative to a set", arXiv:1901.08359, Math. Program.) gives, with the `l1` norm on the weights, exactly this minimum-ratio characterization `min 2||Ax - u|| / dist_1(x, Z(u))`; its diameter companion `max 2||A(x - y)||/||x - y||_1` is here the Dobrushin coefficient `max_{i,j} TV(K_i,K_j) = sup TV(delta K)/TV(delta)`. So the identity, and the "lower counterpart of Dobrushin" remark, are a direct special case of that published general-norm proposition. Pena and Rodriguez (*Math. Oper. Res.* 2019, doi:10.1287/moor.2017.0910) introduced the facial distance in the Euclidean norm (their Theorem 1 is the face characterization) and proved that, in the Euclidean norm, it equals the pyramidal width of Lacoste-Julien and Jaggi (NeurIPS 2015, "On the Global Linear Convergence of Frank-Wolfe Optimization Variants") (their Theorem 2). No TV-norm pyramidal-width equality is claimed.

`alpha(K)` is also the restriction to zero-sum (prior-difference) directions of the `l1` condition number of Kleinberg and Sandler ("Using mixture models for collaborative filtering", J. Comput. Syst. Sci. 74 (2008) 49-69), the smallest `kappa` with `||x K||_1 >= ||x||_1 / kappa` for all `x`; Arora, Ge, Koehler, Ma and Moitra ("Provable algorithms for inference in topic models", ICML 2016) use it to invert known-topic mixtures, the setting of this layer, and note that no efficient algorithm is known for computing it, consistent with the exponential face enumeration here. *Elementary remark (new, verified):* for row-stochastic `K`, `alpha/(2 + alpha) <= 1/kappa(K) <= alpha`. The upper bound restricts to zero-sum `x`. For the lower bound write `x = a u - b v` with disjoint-support probability vectors and `a, b >= 0`; then `||x K||_1 >= |a - b|` (row sums are one) and `||x K||_1 >= 2 alpha min(a, b) - |a - b|`, and minimizing `max(d, 2 alpha m - d)/(2m + d)` over `d, m >= 0` gives `alpha/(2 + alpha)`. So the inverse constant `C_*` is equivalent to the Kleinberg-Sandler condition number up to a factor of about 3.

`alpha(K) = 0` exactly when the rows are affinely dependent, while the facial distance of `conv(K)` stays positive there, so the facial-distance identification holds only in the affinely independent case. The qualitative criterion (positive `alpha` iff affinely independent rows, i.e. known-component identifiability) is classical (Teicher 1963; Yakowitz and Spragins, Ann. Math. Statist. 39 (1968) 209-214) and bears on ST-T238. The identity is not claimed as a new convex-geometric result; the contribution of this layer is the exact rational primal-dual face and event certificates and their use for mixture-channel inversion.

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

Suppose a finite-sample procedure gives an observed-law confidence radius `rho_obs` with `rho_obs >= TV(\hat\pi K, \pi K)` for a model-image estimate `\hat\pi`. The sharp deterministic transfer is

\[
\boxed{
rho_{latent}
\le
\min\{1,C_*(K)\rho_{obs}\}.
}
\]

If `rho_obs` only bounds the distance to an off-model empirical law `\hat p`, replace `rho_obs` by `2 rho_obs`; this is valid when `\hat\pi` is a TV minimum-distance fit (or any fit with `TV(\hat\pi K, \hat p) <= rho_obs`).

Thus sample complexity inherits a conditioning penalty. Under second-moment radii scaling as `N^{-1/2}`, the sample size sufficient under this transfer to maintain a fixed latent-prior radius scales as

\[
\boxed{C_*(K)^2=\alpha(K)^{-2}.}
\]

Near affine dependence this diverges even though every individual component pair may still look easy to classify. This is an upper-bound cost, not a minimax lower bound. The Euclidean (`sigma_min`) analogues of this `alpha^-2` cost are standard in label-shift estimation through a confusion matrix, including estimated-matrix error (Lipton, Wang and Smola, "Detecting and correcting for label shift with black box predictors", ICML 2018), and in the condition-number factors of Kleinberg and Sandler (2008) and Arora et al. (2016).

## Nonclaims

- Channel rows are known exactly in this layer.
- The disjoint-face identity is not claimed as a new convex-geometric result; for affinely independent rows it is the TV-norm facial distance of Gutman and Pena (Prop. 1), and in general the zero-sum restriction of the Kleinberg-Sandler `l1` condition number.
- The face/event enumeration is exponential and bounded by explicit caps.
- `alpha(K)` is an inverse-conditioning quantity, not a posterior probability.
- A small `alpha(K)` does not imply that the latent models are physically similar; it says mixtures of their declared emission laws can be observationally close.
- None of these finite-channel results is evidence for simulation or for any particular simulator architecture.
