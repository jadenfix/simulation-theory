# Visibility + phase predictive-state bounds

## Scope

This note extends the one-parameter Werner/singlet visibility family to a two-parameter predictive state

\[
\theta=(v,\phi),\qquad 0\le v\le 1,\quad \phi\in \mathbb S^1.
\]

For coplanar projective settings \(\alpha_x,\beta_y\), define

\[
r_{xy}(v,\phi)=v\cos(\alpha_x-\beta_y-\phi)
\]

and

\[
P(a,b\mid x,y,v,\phi)=\frac14\left(1-ab\,r_{xy}(v,\phi)\right),\qquad a,b\in\{-1,+1\}.
\]

This is a bounded physical model used to derive predictive-state geometry. It is not evidence that reality is simulated.

## Exact predictive-law distance

For one fixed setting pair, two states \(\theta,\theta'\) have four-outcome total variation distance

\[
\operatorname{TV}_{xy}(\theta,\theta')
=\frac12\left|r_{xy}(\theta)-r_{xy}(\theta')\right|.
\]

If the setting pair is externally randomized with weights \(w_{xy}\), the joint setting/outcome law satisfies

\[
\boxed{
\operatorname{TV}(P_\theta,P_{\theta'})
=\frac12\sum_{x,y}w_{xy}
\left|r_{xy}(\theta)-r_{xy}(\theta')\right|.
}
\]

This is exact, not an asymptotic approximation. `state_total_variation` implements the closed form and `brute_force_state_tv` independently enumerates the full outcome law.

## Why phase creates a genuine extra predictive dimension

The visibility-only family moves along one scalar direction. With phase, the state maps naturally to the unit disk

\[
q=(q_1,q_2)=(v\cos\phi,v\sin\phi).
\]

Each setting pair observes a linear projection of this disk:

\[
r_{xy}=q_1\cos(\alpha_x-\beta_y)+q_2\sin(\alpha_x-\beta_y).
\]

So a sufficiently rich measurement schedule probes two independent directions. A single setting pair cannot identify both coordinates.

## Fisher geometry

Let

\[
d=\alpha-\beta-\phi,
\qquad r=v\cos d.
\]

The gradient is

\[
\nabla r=
\begin{pmatrix}
\cos d\\
v\sin d
\end{pmatrix}.
\]

Direct evaluation of the score gives the one-query Fisher matrix

\[
\boxed{
I_{\alpha,\beta}(v,\phi)
=
\frac{\nabla r\,\nabla r^\top}{1-r^2}.
}
\]

Hence every individual setting is rank at most one. For a randomized schedule,

\[
I(v,\phi)=\sum_{x,y}w_{xy}I_{xy}(v,\phi).
\]

Two-parameter local identification requires this sum to have rank two. This yields an explicit experimental-design condition: the allowed setting gradients must span both predictive directions.

At \(v=0\),

\[
\frac{\partial r}{\partial\phi}=v\sin d=0,
\]

so phase is locally unidentifiable. This is a physical degeneracy, not a numerical artifact.

For regular interior points with full-rank Fisher matrix, any locally unbiased estimator obeys the matrix Cramer-Rao inequality

\[
\operatorname{Cov}(\hat\theta)\succeq \frac1n I(\theta)^{-1}.
\]

The implementation returns the explicit \(2\times2\) inverse lower bound.

## Predictive-state packing

Given a finite physically defined state grid \(\Theta\) and approximation tolerance \(\epsilon\), any subset \(S\subseteq\Theta\) satisfying

\[
\operatorname{TV}(P_\theta,P_{\theta'})>2\epsilon
\quad\forall\theta\ne\theta'\in S
\]

is a certified packing. By the approximate predictive-state theorem already proved in the repository, one renderer state cannot approximate two members of such a packing within \(\epsilon\). Therefore

\[
|\mathcal Z|\ge |S|
\]

and

\[
\boxed{
\text{memory bits}\ge \lceil\log_2|S|\rceil.
}
\]

The code provides two packers:

- a deterministic greedy construction, which is always a valid lower bound on the maximum packing number;
- an exact branch-and-bound maximum-clique solver for small grids, capped at 48 states.

Unlike the one-dimensional visibility family, greedy packing is **not** claimed optimal in two dimensions.

## What this advances

The previous Bell result established a physically derived one-dimensional predictive geometry. This extension adds:

1. a two-dimensional latent physical state;
2. exact finite predictive-law distances;
3. rank-based local identifiability;
4. matrix Fisher information rather than a scalar information rate;
5. higher-dimensional physically generated packing numbers;
6. explicit phase-degeneracy boundaries.

## Nonclaims

- A Bell violation is not evidence for simulation.
- A lower bound on internal predictive states is not a lower bound on parent-universe hardware bits.
- Fisher information is local and model-dependent; it does not establish global identifiability by itself.
- The finite grid packing is a bounded result, not an asymptotic lower bound for arbitrary quantum field theories.
- This model assumes the stated two-qubit correlation law and measurement family.

## Next step

The next deeper target is a sequential/adaptive version in which the latent phase evolves or measurement choices depend on previous outcomes. That moves the object from a static two-parameter family to a finite quantum hidden-state process and lets the project study state growth with transcript length rather than only parameter resolution on one trial.
