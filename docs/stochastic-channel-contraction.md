# Stochastic outcome channels and predictive-law contraction

## Scope

A future observable law is often not seen directly. It may pass through
measurement noise, coarse-graining, lossy logging, erasure, randomized
post-processing, or a deliberately simplified interface.

The first-principles question is:

> Can record-independent post-processing create observable evidence or
> predictive distinctions that were absent before it?

For finite outcome spaces, the answer is no. This note proves a quantitative
version using the Dobrushin contraction coefficient, extends it to a family of
future queries, and derives consequences for exact predictive equivalence,
packings, covers, and serial channels.

The channel is part of a declared internal observation model. Nothing here
identifies a parent substrate, supplies evidence for simulation, or says that a
real measurement device follows the selected finite kernel.

---

## 1. Finite outcome channels

Let \(\mathcal Y\) be a finite input alphabet and \(\mathcal Z\) a finite
output alphabet. A channel is a Markov kernel

\[
K(z\mid y)\ge0,
\qquad
\sum_{z\in\mathcal Z}K(z\mid y)=1
\]

for every \(y\in\mathcal Y\).

If \(\mu\) is a distribution on \(\mathcal Y\), its output distribution is

\[
(\mu K)(z)
=
\sum_y\mu(y)K(z\mid y).
\]

For finite probability laws, total variation is

\[
\operatorname{TV}(\mu,\nu)
=
\frac12\sum_y|\mu(y)-\nu(y)|.
\]

The repository stores channel rows as exact rational numbers. Floating-point
stochastic-family laws are canonicalized to rational probability vectors when
constructing theorem certificates.

---

## 2. Dobrushin coefficient

Define

\[
\boxed{
\delta(K)
=
\max_{y,y'\in\mathcal Y}
\operatorname{TV}
\left(
K(\cdot\mid y),K(\cdot\mid y')
\right).
}
\]

Because every pair of probability distributions has TV between zero and one,

\[
0\le\delta(K)\le1.
\]

Interpretation:

- \(\delta(K)=0\): every input row is identical, so the output forgets the
  input completely.
- \(\delta(K)=1\): some pair of inputs can remain perfectly distinguishable.
- \(0<\delta(K)<1\): every input distinction is uniformly attenuated.

The coefficient is determined by the most distinguishable pair of channel
rows, not by the number of input or output symbols.

---

## 3. Dobrushin total-variation contraction theorem

### Theorem

For every pair of input distributions \(\mu,\nu\),

\[
\boxed{
\operatorname{TV}(\mu K,\nu K)
\le
\delta(K)\operatorname{TV}(\mu,\nu).
}
\]

### Proof from the Jordan decomposition

Let

\[
\alpha=\mu-\nu.
\]

The signed measure \(\alpha\) has total mass zero. Let \(\alpha^+\) and
\(\alpha^-\) be its positive and negative parts. Their common total mass is

\[
\tau
=
\alpha^+(\mathcal Y)
=
\alpha^-(\mathcal Y)
=
\operatorname{TV}(\mu,\nu).
\]

If \(\tau=0\), then \(\mu=\nu\) and the theorem is immediate. Otherwise define

\[
r=\frac{\alpha^+}{\tau},
\qquad
s=\frac{\alpha^-}{\tau}.
\]

Both \(r\) and \(s\) are probability distributions, and

\[
\mu-
u
=
\tau(r-s).
\]

Applying the channel gives

\[
\mu K-
u K
=
\tau(rK-sK),
\]

so

\[
\operatorname{TV}(\mu K,\nu K)
=
\tau\operatorname{TV}(rK,sK).
\]

It remains to show \(\operatorname{TV}(rK,sK)\le\delta(K)\).
Write

\[
rK
=
\sum_y r(y)K_y,
\qquad
sK
=
\sum_{y'}s(y')K_{y'},
\]

where \(K_y=K(\cdot\mid y)\). Since
\(\sum_{y'}s(y')=\sum_y r(y)=1\), both mixtures can be written using the same
joint weights:

\[
rK
=
\sum_{y,y'}r(y)s(y')K_y,
\]

and

\[
sK
=
\sum_{y,y'}r(y)s(y')K_{y'}.
\]

By convexity of total variation,

\[
\begin{aligned}
\operatorname{TV}(rK,sK)
&\le
\sum_{y,y'}r(y)s(y')
\operatorname{TV}(K_y,K_{y'})\\
&\le
\delta(K)
\sum_{y,y'}r(y)s(y')\\
&=
\delta(K).
\end{aligned}
\]

Multiplying by \(\tau\) proves the theorem.

### What the proof assumes

The same channel \(K\) is applied under both compared hidden records. If the
post-processing rule itself depends on which record is true, it can insert new
record information, and this theorem no longer applies in this form.

---

## 4. Tightness

The coefficient is not merely a loose universal constant. By definition,
there is a pair of channel rows attaining the maximum in a finite alphabet.
Choose deterministic input distributions concentrated on that pair:

\[
\mu=\delta_y,
\qquad
\nu=\delta_{y'}.
\]

Then

\[
\operatorname{TV}(\mu,\nu)=1
\]

and

\[
\operatorname{TV}(\mu K,\nu K)
=
\delta(K).
\]

Therefore the multiplicative constant cannot be improved uniformly over all
input pairs.

---

## 5. Binary symmetric channel

For crossover probability \(q\in[0,1/2]\),

\[
K_q
=
\begin{pmatrix}
1-q&q\\
q&1-q
\end{pmatrix}.
\]

Its two rows have total variation

\[
\frac12
\left(
|(1-q)-q|+|q-(1-q)|
\right)
=
1-2q.
\]

Hence

\[
\boxed{
\delta(K_q)=1-2q.
}
\]

For opposite deterministic inputs, equality holds:

\[
\operatorname{TV}
\left(
(1,0)K_q,(0,1)K_q
\right)
=1-2q.
\]

At \(q=0\), the channel is the identity. At \(q=1/2\), both rows are
\((1/2,1/2)\), and all binary input information is erased.

This recovers the visibility factor that appeared earlier in the noisy parity
and noisy checkpoint models, now as a general channel coefficient.

---

## 6. Erasure channel

Let the input alphabet be \(\mathcal Y\), and add an erasure symbol
\(\bot\). With erasure probability \(e\),

\[
K_e(z\mid y)
=
\begin{cases}
1-e,&z=y,\\
e,&z=\bot,\\
0,&\text{otherwise}.
\end{cases}
\]

For two different inputs, the common erasure mass cancels and the remaining
point masses have weight \(1-e\). Therefore

\[
\boxed{
\delta(K_e)=1-e.
}
\]

Again, deterministic distinct inputs attain equality.

---

## 7. Query-specific post-processing

Let a hidden record be \(x\). Future query \(q\) is selected from a fixed
exogenous distribution \(w_q\), and its raw outcome law is

\[
P_x(\cdot\mid q).
\]

The joint law over query and outcome is

\[
P_x(q,y)
=
w_qP_x(y\mid q).
\]

For two records \(x,u\), disjoint query labels give the exact decomposition

\[
\boxed{
 d_{\mathrm{before}}(x,u)
=
\sum_qw_q
\operatorname{TV}
\left(
P_x(\cdot\mid q),P_u(\cdot\mid q)
\right).
}
\]

Now apply one record-independent channel \(K_q\) after each query. The new
distance is

\[
 d_{\mathrm{after}}(x,u)
=
\sum_qw_q
\operatorname{TV}
\left(
P_x(\cdot\mid q)K_q,
P_u(\cdot\mid q)K_q
\right).
\]

Applying the one-channel theorem separately to every query gives

\[
\boxed{
 d_{\mathrm{after}}(x,u)
\le
\sum_qw_q\delta(K_q)
\operatorname{TV}
\left(
P_x(\cdot\mid q),P_u(\cdot\mid q)
\right).
}
\]

Let

\[
\delta_{\max}=\max_q\delta(K_q).
\]

Then

\[
\boxed{
 d_{\mathrm{after}}(x,u)
\le
\delta_{\max}d_{\mathrm{before}}(x,u).
}
\]

The querywise bound can be much tighter than the global bound. A highly noisy
channel matters little when it is attached to a query on which the records
already agree, while a nearly noiseless channel matters greatly on a query
carrying most of the original separation.

---

## 8. Serial channels

Suppose channel \(K\) is followed by channel \(L\). For two input symbols
\(y,y'\), apply the contraction theorem for \(L\) to the two rows of \(K\):

\[
\operatorname{TV}(K_yL,K_{y'}L)
\le
\delta(L)\operatorname{TV}(K_y,K_{y'}).
\]

Taking the maximum over \(y,y'\) gives

\[
\boxed{
\delta(KL)
\le
\delta(K)\delta(L).
}
\]

By induction, for a serial chain \(K_1K_2\cdots K_T\),

\[
\boxed{
\delta(K_1K_2\cdots K_T)
\le
\prod_{t=1}^{T}\delta(K_t).
}
\]

The inequality can be strict because the pair of rows that maximizes one stage
need not map onto the pair that maximizes the next stage.

For binary symmetric channels, equality holds. Two BSCs with crossover
probabilities \(q_1,q_2\) compose to

\[
q_{\mathrm{eff}}
=
q_1+q_2-2q_1q_2,
\]

and

\[
1-2q_{\mathrm{eff}}
=(1-2q_1)(1-2q_2).
\]

---

## 9. Exact predictive equivalence can only coarsen

Two records are exactly predictively equivalent when every query law is equal:

\[
P_x(\cdot\mid q)
=
P_u(\cdot\mid q)
\qquad\forall q.
\]

Applying the same channel to equal laws preserves equality. Therefore every
pre-channel equivalence class is contained in one post-channel equivalence
class, and

\[
\boxed{
K_{\mathrm{after}}
\le
K_{\mathrm{before}}.
}
\]

Consequently, the exact fixed-length predictive-state requirement cannot
increase:

\[
\boxed{
\left\lceil\log_2K_{\mathrm{after}}\right\rceil
\le
\left\lceil\log_2K_{\mathrm{before}}\right\rceil.
}
\]

At complete binary randomization, \(q=1/2\), every Bernoulli target is mapped to
\(\operatorname{Bernoulli}(1/2)\). Arbitrarily many exact input law classes
collapse to one observable class.

This is not free simulation compression. It is compression created by changing
the required observable interface so that previously distinct targets become
indistinguishable.

---

## 10. Packing monotonicity

Fix tolerance \(\epsilon\). A strict predictive packing is a record set
\(A\) such that

\[
d(x,u)>2\epsilon
\qquad
\forall x\ne u\in A.
\]

Because

\[
d_{\mathrm{after}}(x,u)
\le d_{\mathrm{before}}(x,u),
\]

every post-channel strict packing is also a valid pre-channel strict packing.
Therefore

\[
\boxed{
\mathcal P_{>2\epsilon}^{\mathrm{after}}
\le
\mathcal P_{>2\epsilon}^{\mathrm{before}}.
}
\]

The packing lower bound on approximate predictive states can only stay the same
or weaken under record-independent post-processing.

This is an information statement, not a statement that the true internal
state of a physical system became smaller.

---

## 11. Target-centered cover monotonicity

Suppose target law indexed by center record \(c\) approximates target record
\(x\) before the channel:

\[
d_{\mathrm{before}}(x,c)
\le\epsilon.
\]

Contraction gives

\[
d_{\mathrm{after}}(x,c)
\le\epsilon.
\]

Thus every target-centered pre-channel \(\epsilon\)-cover remains a valid
post-channel cover using the same center records. Taking minima gives

\[
\boxed{
\mathcal N_{\epsilon,\mathrm{target}}^{\mathrm{after}}
\le
\mathcal N_{\epsilon,\mathrm{target}}^{\mathrm{before}}.
}
\]

Together, the implemented finite bracket obeys

\[
\mathcal P_{>2\epsilon}^{\mathrm{after}}
\le
M_{\epsilon}^{\mathrm{after}}
\le
\mathcal N_{\epsilon,\mathrm{target}}^{\mathrm{after}},
\]

with both implemented outer quantities nonincreasing under the channel.

The target-centered cover remains only a constructive upper bound. An
interpolating off-family predictor can still use fewer states.

---

## 12. Inference consequences

Suppose two restricted physical architectures induce internal observable laws
\(P\) and \(Q\), but the recorded data pass through a shared channel \(K\).
Then

\[
\operatorname{TV}(PK,QK)
\le
\delta(K)\operatorname{TV}(P,Q).
\]

The equal-prior optimal classifier accuracy after recording is

\[
A_K^\star
=
\frac{1+\operatorname{TV}(PK,QK)}2,
\]

so

\[
\boxed{
A_K^\star
\le
\frac{1+\delta(K)\operatorname{TV}(P,Q)}2.
}
\]

No downstream classifier, neural network, Bayesian procedure, or hypothesis
test can reconstruct distinguishability removed from the recorded distribution
without additional information.

This does not mean all processing is harmful. A sufficient statistic can
preserve the relevant likelihood ratio exactly while discarding irrelevant
raw detail. The theorem says only that a record-independent stochastic channel
cannot increase total-variation separation between fixed hypotheses.

---

## 13. Computational certificates

The implementation includes:

- exact rational channel rows;
- exact pushforwards;
- exact Dobrushin coefficients;
- exact one-channel contraction certificates;
- exact serial composition and product bounds;
- exact querywise and global contraction certificates;
- binary symmetric and erasure channel constructors;
- complete rational probability grids for bounded exhaustive checking;
- transformed finite stochastic query families;
- exact-class, maximum-packing, and minimum-target-cover monotonicity checks.

Closed forms are checked independently against enumerated distributions and the
existing finite packing and set-cover solvers.

---

## What this adds to the simulation discussion

The broad simulation hypothesis remains observationally underidentified when a
permitted simulator reproduces the same observable law as ordinary physics.
The channel theorem sharpens a related boundary:

> Lossy observation cannot rescue an underidentified model and cannot create
> evidence that was absent in the pre-channel law.

It also clarifies a common ambiguity in computational-resource discussions.
If an architecture is allowed to approximate only a coarse or noisy interface,
its required predictive state may be smaller because the target future-law
family itself has contracted. That is a change in the specification, not a
proof that an exact microscopic world can be represented at the same cost.

The right comparison must therefore state:

1. the pre-channel target law;
2. the observation channel;
3. whether the channel is shared by all hypotheses;
4. the future query distribution;
5. the tolerated post-channel error;
6. whether lost information can later be queried through another interface.

Without those details, “observers cannot notice the shortcut” is not a complete
mathematical claim.

---

## Nonclaims

- A channel model is not evidence that reality is simulated.
- The theorem requires record-independent post-processing shared by the compared
  laws.
- The Dobrushin coefficient concerns total variation; other divergences have
  different contraction coefficients.
- Exact rational channel arithmetic does not make an empirically selected noise
  model exact.
- A reduction in observable predictive classes is not automatically a reduction
  in microscopic physical state.
- Packing contraction weakens one lower bound; it does not construct an optimal
  renderer.
- Target-cover contraction concerns the target-centered constructive cover, not
  arbitrary-center covering optimality.
- Serial product bounds are upper bounds and can be strict.
- Internal predictive bits are not parent-universe RAM, mass, energy, or qubits.

---

## Next research targets

1. Compute contraction coefficients for KL, chi-square, Hellinger, and mutual
   information under declared channel families.
2. Add noisy causal-network edges and separate observation contraction from
   communication coding capacity.
3. Derive robust bounds when the channel belongs to an uncertainty set rather
   than being known exactly.
4. Study record-dependent selection channels explicitly as interventions rather
   than applying the shared-channel theorem incorrectly.
5. Combine query-revelation trees with channel contraction at every stage.
6. Develop multicast coding certificates for several sinks requiring related
   predictive class labels.
7. Add continuous-channel approximations only with certified discretization
   error.
