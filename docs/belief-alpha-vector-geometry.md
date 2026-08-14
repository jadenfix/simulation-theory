# Alpha-vector geometry of hidden-law coding

## Scope

The belief-state Bellman equations establish that the posterior belief is a
sufficient state.  This note derives a second representation of the same finite
problem: every deterministic policy tree induces one affine cost function of
the initial belief, and the optimal value is the lower envelope of those affine
functions.

The construction gives:

- an independent exact checker for the belief Bellman recursion;
- piecewise-linear concavity of finite-horizon cost in the belief;
- safe componentwise alpha-vector pruning;
- an exact posterior-martingale identity explaining why information creates a
  mean-preserving spread of beliefs rather than changing their prior mean.

All claims concern the declared finite rational hidden Markov coding model.

---

## 1. One deterministic policy tree is affine in belief

Fix a remaining horizon \(h\), previous codebook \(a_-\), and one complete
deterministic policy tree \(\pi\).  Conditional on hidden state \(S_t=s\), let

\[
\alpha_\pi(s)
]

be its expected remaining cost, including every future signal, hidden-state
transition, stage cost, and switch charge.

For prior belief \(b\), the law of total expectation gives

\[
\boxed{
C_\pi(b)
=
\sum_s b(s)\alpha_\pi(s)
=
b^\top\alpha_\pi.
}
\]

Thus a deterministic policy tree is represented by one vector

\[
\alpha_\pi\in\mathbb Q^m.
\]

---

## 2. No-signal alpha recursion

Let \(\Gamma_{h,a_-}^{\rm none}\) be the set of alpha vectors induced by every
no-signal deterministic policy with \(h\) periods remaining.

At zero horizon,

\[
\Gamma_{0,a_-}^{\rm none}=\{0\}.
\]

Choose current codebook \(a\) and a continuation vector

\[
\beta\in\Gamma_{h-1,a}^{\rm none}.
\]

For current hidden state \(s\), the resulting vector is

\[
\boxed{
\alpha(s)
=
L(s,a)
+
\kappa\mathbf1\{a\ne a_-\}
+
\sum_{s'}K_{ss'}\beta(s').
}
\]

Enumerating every current action and continuation vector generates the complete
finite family.

---

## 3. Noisy-signal alpha recursion

Let \(O_{sy}=P(Y_t=y\mid S_t=s)\).  A deterministic policy tree chooses, for
each possible current signal \(y\):

- a codebook \(a_y\);
- one continuation alpha vector

  \[
  \beta_y\in\Gamma_{h-1,a_y}^{\rm obs}.
  \]

Conditional on hidden state \(s\), signal \(y\) occurs with probability
\(O_{sy}\).  Therefore

\[
\boxed{
\alpha(s)
=
\sum_y O_{sy}
\left[
L(s,a_y)
+
\kappa\mathbf1\{a_y\ne a_-\}
+
\sum_{s'}K_{ss'}\beta_y(s')
\right].
}
\]

Every finite deterministic signal-contingent policy tree appears in this
recursion, and every generated vector corresponds to such a tree.

---

## 4. Value function is a lower envelope

Let \(\Gamma_{h,a_-}\) be either complete family.  Since the policy may select
any deterministic tree before the hidden state is drawn,

\[
\boxed{
V_{h,a_-}(b)
=
\min_{\alpha\in\Gamma_{h,a_-}}
b^\top\alpha.
}
\]

A finite minimum of affine functions is piecewise linear and concave.  For
beliefs \(b_1,b_2\) and \(\theta\in[0,1]\),

\[
\begin{aligned}
V(\theta b_1+(1-\theta)b_2)
&=
\min_\alpha
\left[
\theta b_1^\top\alpha
+(1-\theta)b_2^\top\alpha
\right]\\
&\ge
\theta\min_\alpha b_1^\top\alpha
+(1-\theta)\min_\alpha b_2^\top\alpha.
\end{aligned}
\]

Hence

\[
\boxed{
V(\theta b_1+(1-\theta)b_2)
\ge
\theta V(b_1)+(1-\theta)V(b_2).
}
\]

The direction is concave because this is a cost minimization problem.  For
reward maximization the familiar POMDP convention gives a convex upper
envelope instead.

---

## 5. Safe alpha-vector pruning

Suppose two alpha vectors satisfy

\[
\alpha(s)\le\beta(s)
\qquad\forall s,
\]

with strict inequality for at least one state.  Every belief is nonnegative, so

\[
b^\top\alpha
\le
b^\top\beta
\qquad\forall b\in\Delta_{m-1}.
\]

Therefore \(\beta\) can never be the unique minimizing vector and may be
removed:

\[
\boxed{
\alpha\le\beta\text{ componentwise}
\implies
\beta\text{ is value-dominated on the entire belief simplex}.}
\]

The repository removes exact duplicates and componentwise dominated vectors at
every recursion depth.  This is a sufficient pruning rule, not a claim that the
remaining family is the smallest possible representation; convex-hull pruning
could remove additional vectors.

---

## 6. Independent Bellman verification

The standard belief Bellman solver and alpha-vector recursion use different
representations:

- Bellman recursion computes values only at reachable posterior beliefs;
- alpha recursion enumerates complete policy-tree affine functionals over the
  whole belief simplex.

For every stored Bellman entry with belief \(b\), remaining horizon \(h\), and
previous code \(a_-\), the checker requires

\[
\boxed{
V_{\rm Bellman}(b,a_-)
=
\min_{\alpha\in\Gamma_{h,a_-}}b^\top\alpha
}
\]

as an exact rational identity.

Agreement at the initial belief and every reachable continuation belief makes
it harder for an indexing or conditioning error to survive both calculations.

---

## 7. Posterior belief is a martingale

Let \(B^Y\) be the posterior after observing the current signal.  For each
hidden state \(s\),

\[
\begin{aligned}
E[B^Y(s)]
&=
\sum_yP(y)
\frac{b(s)O_{sy}}{P(y)}\\
&=
b(s)
\sum_yO_{sy}\\
&=b(s).
\end{aligned}
\]

Therefore

\[
\boxed{E[B^Y]=b.}
\]

After the hidden-state transition,

\[
\boxed{E[B^YK]=bK.}
\]

The observation changes the dispersion of posterior beliefs but not their
conditional mean.

Combined with concavity of the continuation cost, Jensen gives the correct
information direction:

\[
E[V(B^Y)]
\le
V(E[B^Y])
=
V(b).
\]

This is another route to the statement that a freely available signal cannot
increase optimal expected cost.  Exact dynamic Blackwell monotonicity is
stronger because it compares arbitrary garblings, not only a signal with its
unobserved prior.

---

## 8. Representation complexity

The exact policy-tree family can grow rapidly.  If a signal alphabet has
\(|\mathcal Y|\) outcomes, and there are \(M_{h-1,a}\) retained continuation
vectors after action \(a\), the raw observed recursion considers

\[
\left(
\sum_a M_{h-1,a}
\right)^{|\mathcal Y|}
\]

signal-contingent choices for each previous codebook.

This growth is a property of the exact policy-tree representation, not proof
that every implementation must enumerate all trees.  Point-based methods,
convex-hull algorithms, and approximate belief compression can be much more
scalable, but they require explicit approximation guarantees before replacing
the exact bounded checker.

---

## Nonclaims

- Piecewise-linear concavity is proved for finite horizon, finite hidden state,
  finite signal, finite action, and linear expected cost.
- Componentwise dominance is safe but not necessarily complete pruning.
- The exact alpha family is not asserted to be the smallest predictive
  representation.
- Posterior martingale structure assumes the observation model is correctly
  specified.
- Jensen's inequality establishes a Bayesian expected-cost information result,
  not a minimax theorem.
- Bounded policy-tree enumeration is not a scalability guarantee.
- Alpha vectors and beliefs are internal mathematical objects, not inferred
  physical memory or parent-substrate state.
- None of these identities is evidence that reality is simulated.
