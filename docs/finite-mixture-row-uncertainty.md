# Finite-mixture identifiability with uncertain emission rows

## Scope

The exact global modulus layer assumes every component emission row `K_i` is known. Real inference often estimates those rows too. This layer declares rowwise uncertainty sets

\[
TV(K_i,K_i')\le r_i
\]

and asks what can still be certified about the true channel `K'`.

The uncertainty set is deterministic. A separate statistical layer must justify the radii `r_i` from data.

## 1. Two-epsilon stability of the global modulus

Let

\[
r_{max}=\max_i r_i.
\]

Take any normalized latent direction

\[
\delta=u-v,
\qquad
TV(\delta)=1,
\]

where `u,v` are disjoint-support probability vectors. Then

\[
TV(uK,uK')\le\sum_i u_i r_i\le r_{max},
\]

and likewise

\[
TV(vK,vK')\le r_{max}.
\]

The reverse triangle inequality gives

\[
TV(uK',vK')
\ge
TV(uK,vK)-2r_{max}.
\]

Taking the infimum over normalized latent directions yields

\[
\alpha(K')\ge\max\{0,\alpha(K)-2r_{max}\}.
\]

Swapping `K` and `K'` gives the symmetric bound

\[
\boxed{
|\alpha(K')-\alpha(K)|\le2r_{max}.
}
\]

The constant two is sharp. For the binary identity channel, move both rows inward by `epsilon`:

\[
K_0'=(1-\varepsilon,\varepsilon),
\qquad
K_1'=(\varepsilon,1-\varepsilon).
\]

Each row moves TV distance `epsilon`, while

\[
\alpha(K')=1-2\varepsilon.
\]

At `epsilon=1/2`, the two rows coincide and identifiability disappears.

**Prior art.** The Lipschitz bound is the standard fact that a minimum gain (lower bound, or minimum modulus) of a linear map is 1-Lipschitz in the induced operator norm, by the reverse triangle inequality: rowwise TV radii `r_i` give `||delta(K'-K)||_TV <= 2 r_max TV(delta)` on zero-sum `delta`. It is the TV analogue of Weyl's singular-value perturbation inequality, and the sharpness example is an instance of the Gastinel-Kahan distance-to-singularity phenomenon (Kahan 1966; Higham, Accuracy and Stability of Numerical Algorithms, 2nd ed. 2002, Ch. 6) under a stochastic-row restriction. Neither is claimed as new.

## 2. Why max-row uncertainty can be too pessimistic

The bound above charges every latent direction twice by the worst row radius. But a dangerous face pair may not use the most uncertain row on both sides.

For disjoint latent faces `P,N`, a pair action `(i,j)` incurs the worst-case per-event uncertainty penalty

\[
r_i+r_j.
\]

For every observed event `A`,

\[
K_i'(A)-K_j'(A)
\ge
K_i(A)-K_j(A)-r_i-r_j.
\]

Therefore the true face distance is lower-bounded by the zero-sum game obtained from the nominal event/pair payoff matrix after subtracting `r_i+r_j` from pair column `(i,j)`.

If `G_{P,N}` is that penalized game value, define

\[
L_{P,N}=\max\{0,G_{P,N}\}.
\]

Then

\[
\boxed{
\operatorname{dist}_{TV}
(\operatorname{conv}K_P',\operatorname{conv}K_N')
\ge L_{P,N}.
}
\]

Taking the minimum over all disjoint nonempty face pairs gives the robust certificate

\[
\boxed{
\alpha(K')\ge
L_{rob}=\min_{P,N}L_{P,N}.
}
\]

Because this retains row-specific radii,

\[
L_{rob}\ge\max\{0,\alpha(K)-2r_{max}\}.
\]

The penalty `sum_{ij} lambda_ij (r_i + r_j) = u.r + v.r` does not depend on the event, so the penalized game value is simply `min over (u, v) of [TV(uK, vK) - (u + v).r]` over the face pair. The certificate is an elementary consequence of the convexity of TV and the triangle inequality, packaged with exact rational game certificates; it is not claimed as a new technique. It is an exactly computed lower certificate, not a claim that it equals the worst admissible channel modulus.

## 3. Exact asymmetric example

For identity `K3`, nominal

\[
\alpha(K)=1.
\]

Suppose only the third row is uncertain:

\[
(r_0,r_1,r_2)=\left(0,0,\frac14\right).
\]

The coarse two-max-radius bound gives

\[
1-2\cdot\frac14=\frac12.
\]

But every dangerous face involving row two pays only one `1/4` penalty because the other face uses zero-radius rows. The exact facewise certificate gives

\[
\boxed{L_{rob}=\frac34.}
\]

Thus preserving the geometry of *which rows participate in which ambiguity direction* materially tightens robust identifiability.

## 4. Robust inverse conditioning

If

\[
L_{rob}>0,
\]

then every channel in the declared rowwise TV uncertainty set remains identifiable and

\[
\boxed{
C_*(K')\le\frac1{L_{rob}}.
}
\]

Consequently, if `rho_obs` bounds `TV(\hat\pi K',\pi K')` with both priors pushed through the same admissible true channel `K'`, it transfers uniformly to

\[
\boxed{
rho_{latent}
\le
\min\left\{1,\frac{\rho_{obs}}{L_{rob}}\right\}.
}
\]

The same-channel condition matters. If `\hat\pi` is fitted with the nominal channel `K` and `rho_obs` only bounds `TV(\hat q,\pi K')`, the triangle inequality gives

\[
TV(\hat\pi,\pi)\le\min\left\{1,\frac{\rho_{obs}+TV(\hat\pi K,\hat q)+\sum_i\hat\pi_i r_i}{L_{rob}}\right\}
\]

and the misspecification term cannot be dropped: with nominal binary identity rows, `r=(1/10,1/10)`, true rows `(9/10,1/10)` and `(1/10,9/10)`, and `\pi=(1,0)`, the observed law `(9/10,1/10)` is matched exactly (`rho_obs=0`), the nominal fit is `\hat\pi=(9/10,1/10)`, and `TV(\hat\pi,\pi)=1/10`. More generally the identified set `{\pi: \pi K'=q` for some admissible `K'}` has positive diameter.

If `L_rob=0`, the certificate is intentionally agnostic. Zero means the declared uncertainty set is too large for this proof to guarantee invertibility; it does not assert that every admissible channel is nonidentifiable.

## 5. A sufficient uniform calibration condition for channel estimation

For uniform row uncertainty `r_i=epsilon`, every pair action receives the same `2 epsilon` penalty. Hence

\[
\boxed{
L_{rob}=\max\{0,\alpha(K)-2\varepsilon\}.
}
\]

A sufficient uniform calibration condition for robust identifiability is therefore

\[
\boxed{
\varepsilon<\frac{\alpha(K)}2.
}
\]

This is a useful experimental-design target: channel-row estimation must become more accurate as the nominal mixture geometry approaches affine dependence.

If row-estimation error scales like `N^{-1/2}`, then the sufficient condition `epsilon<alpha/2` of this certificate needs row-estimation sample size of order

\[
\alpha(K)^{-2}.
\]

No matching necessity is claimed. The same ill-conditioning that amplifies prior uncertainty therefore also raises the precision required of the channel model itself.

## Nonclaims

- Row radii are inputs, not confidence statements manufactured by this module.
- Rows are allowed to vary adversarially inside their declared TV balls; no parametric coupling is assumed.
- A zero robust lower bound is lack of certification, not proof of nonidentifiability.
- The exact facewise solver remains finite and exponentially enumerative.
- These sensitivity results are not evidence for simulation.
