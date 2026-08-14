# Bayesian belief-state coding for a hidden source law

## Scope

The robust and adversarial source-law lanes ask what happens when nature may
select any law or any bounded-drift path in a declared uncertainty set.  This
note studies a different model: one fully specified stochastic hidden Markov
source-law process.

There are finitely many hidden scenarios

\[
S_t\in\{1,\ldots,m\}.
\]

Scenario \(s\) selects one categorical source law

\[
p^{(s)}\in\Delta_{d-1}.
\]

The hidden process has an exact rational initial law and transition matrix:

\[
P(S_1=s)=\mu_s,
\qquad
P(S_{t+1}=s'\mid S_t=s)=K_{ss'}.
\]

Before selecting the period-\(t\) codebook, the designer observes a signal

\[
Y_t\sim O(\cdot\mid S_t)
\]

through a declared rational observation channel.  The selected deterministic
zero-error prefix codebook is known to every required decoder.  Changing
codebooks incurs a rational charge \(\kappa\).

This is a Bayesian expected-cost model, not a minimax model.  Every distinction
below depends on that choice of criterion.

---

## 1. Exact Bayesian filtering

Let

\[
b_t^-(s)=P(S_t=s\mid Y_{1:t-1})
\]

be the prior belief before observing the current signal.  The signal
probability is

\[
P(Y_t=y\mid b_t^-)
=
\sum_s b_t^-(s)O_{sy}.
\]

For a positive-probability signal, Bayes' rule gives

\[
\boxed{
b_t^y(s)
=
\frac{b_t^-(s)O_{sy}}
{\sum_u b_t^-(u)O_{uy}}.}
\]

After the period, the next prior is

\[
\boxed{
b_{t+1}^-(s')
=
\sum_s b_t^y(s)K_{ss'}.}
\]

All inputs are rational, so every reachable finite-horizon belief is rational.
The repository stores beliefs as exact `Fraction` tuples rather than rounded
floating vectors.

---

## 2. Why the posterior belief is sufficient

Fix a previous codebook \(a_{t-1}\).  Conditional on the current posterior
belief \(b\):

- expected stage cost of codebook \(a\) is

  \[
  \sum_s b(s)L(s,a),
  \]

  where \(L(s,a)\) is the exact expected prefix length under source law
  \(p^{(s)}\);
- the next hidden-state predictive belief is \(bK\);
- future signals depend on the past only through the next hidden state;
- switching cost depends on the past only through \(a_{t-1}\).

Therefore two signal histories producing the same pair

\[
(b,a_{t-1})
\]

induce identical conditional laws for every future source state, signal, stage
cost, and switching cost under every future policy.

Thus

\[
\boxed{
(t,b,a_{t-1})
}

is an exact sufficient state for finite-horizon expected-cost optimization.
The complete signal history may be discarded.

This is a standard Bayesian sufficient-state argument specialized to the
repository's exact zero-error coding interface.  It does not claim the belief
vector is a physical state or a parent-substrate memory representation.

---

## 3. Three causal information patterns

Let \(V_t^{\rm none}(b,a_-)\) be the minimum expected remaining cost with no
source-law signal.  Since the action does not affect hidden dynamics, the next
belief is \(bK\):

\[
\boxed{
V_t^{\rm none}(b,a_-)
=
\min_a
\left[
\kappa\mathbf 1\{a\ne a_-\}
+
\sum_s b(s)L(s,a)
+
V_{t+1}^{\rm none}(bK,a)
\right].
}
\]

For a noisy current signal, the designer observes \(y\) and acts using the
posterior \(b^y\):

\[
\boxed{
V_t^{\rm obs}(b,a_-)
=
\sum_y P(y\mid b)
\min_a
\left[
\kappa\mathbf1\{a\ne a_-\}
+
\sum_s b^y(s)L(s,a)
+
V_{t+1}^{\rm obs}(b^yK,a)
\right].
}
\]

With perfect current hidden-state observation,

\[
\boxed{
V_t^{\rm perf}(s,a_-)
=
\min_a
\left[
\kappa\mathbf1\{a\ne a_-\}
+
L(s,a)
+
\sum_{s'}K_{ss'}V_{t+1}^{\rm perf}(s',a)
\right].
}
\]

The initial perfect-information value is

\[
V^{\rm perf}
=
\sum_s\mu_sV_1^{\rm perf}(s,-1).
\]

The implementation stores and independently replays every selected codebook,
posterior, next belief, and exact Bellman value.

---

## 4. Information hierarchy

Perfect hidden-state information can simulate any noisy signal policy.  A noisy
signal policy can ignore its signal and simulate a no-signal policy.  Therefore

\[
\boxed{
V^{\rm perf}
\le
V^{\rm obs}
\le
V^{\rm none}.
}
\]

The path-first clairvoyant oracle sees the complete hidden-state path and then
selects the minimum-cost code sequence.  It has at least as much information as
perfect current-state feedback, so

\[
\boxed{
V^{\rm clair}
\le
V^{\rm perf}
\le
V^{\rm obs}
\le
V^{\rm none}.
}
\]

The repository enumerates every positive-probability hidden-state path below an
explicit cap, computes its exact Markov probability, advances the exact
code-sequence switching frontier, and averages the path-oracle cost.

---

## 5. Identity and uninformative channel endpoints

### Identity channel

If

\[
O_{sy}=\mathbf1\{s=y\},
\]

then the signal reveals the hidden state exactly.  Hence

\[
\boxed{V^{\rm obs}=V^{\rm perf}.}
\]

### Signal independent of the hidden state

Suppose every observation-channel row is identical:

\[
O_{sy}=r_y
\qquad\forall s.
\]

Then

\[
b^y=b
\]

for every positive-probability signal.  The signal provides only exogenous
randomness independent of the hidden source state.

Any randomized finite-horizon policy can be viewed as a distribution over
complete deterministic policy trees after all exogenous random bits are sampled
in advance.  Its expected cost is an average of deterministic-policy costs and
therefore cannot be below the best deterministic no-signal policy.
The signal policy can also ignore the signal, giving the reverse inequality.
Thus

\[
\boxed{V^{\rm obs}=V^{\rm none}.}
\]

This sharply contrasts with a minimax problem.  In a minimax game, public
randomization may lower worst-case cost by convexifying the designer's action
set.  Under one fixed Bayesian law and linear expected cost, source-independent
randomization has no such benefit.

---

## 6. Dynamic Blackwell monotonicity

Let channel \(B\) be a garbling of channel \(A\):

\[
B=AG,
\]

where \(G\) is row stochastic.  A designer receiving the richer \(A\)-signal can
sample \(G\) privately and feed the resulting garbled signal into any policy
built for \(B\).

Because the hidden transition and signal channels are action independent, this
simulation preserves the joint law of:

- hidden states;
- garbled signals;
- selected codebooks;
- stage costs;
- switching costs.

Therefore

\[
\boxed{
V^{\rm obs}(A)
\le
V^{\rm obs}(B).
}
\]

The exact comparison solves both dynamic programs independently and requires
no-signal cost, perfect-state cost, and expected clairvoyant path-oracle cost to
agree.  Only the noisy-observation value may change.

Although the simulation argument uses randomized garbling, deterministic
optimal policies are sufficient in the solved Bayesian problem: the optimum
over deterministic policies is no worse than any randomized simulated policy.

---

## 7. Bayes regret differs from Bayes cost by one constant

Let

\[
O(S_{1:T})
]

be the path-specific clairvoyant code-sequence oracle.  For policy \(\pi\),
Bayes regret is

\[
\begin{aligned}
\mathcal R(\pi)
&=
E\left[C_\pi(S_{1:T},Y_{1:T})-O(S_{1:T})\right]\\
&=
E[C_\pi]-E[O].
\end{aligned}
\]

The second term is independent of \(\pi\).  Consequently

\[
\boxed{
\arg\min_\pi \mathcal R(\pi)
=
\arg\min_\pi E[C_\pi].
}
\]

The optimal values are related by

\[
\boxed{
R^{i}=V^{i}-V^{\rm clair}
}
\]

for each information pattern \(i\in\{\rm none,obs,perf\}\).

This equivalence is specific to expected regret under one fixed stochastic
model.  It does not hold for minimax pathwise regret, where the path maximizing
the difference need not maximize either term separately.

---

## 8. Exact information-value telescope

Subtracting the same clairvoyant constant from the information hierarchy gives

\[
0
\le
R^{\rm perf}
\le
R^{\rm obs}
\le
R^{\rm none}.
\]

Moreover,

\[
\boxed{
R^{\rm none}
=
(V^{\rm none}-V^{\rm obs})
+
(V^{\rm obs}-V^{\rm perf})
+
(V^{\rm perf}-V^{\rm clair}).
}
\]

The terms quantify:

1. value of the noisy source-law signal;
2. value of perfect current-state information beyond that signal;
3. residual value of complete future path foresight.

Every term is nonnegative under the declared information ordering.

---

## 9. Switching cost creates strict future-foresight value

Consider two hidden source-law scenarios and the complete three-symbol
confusion graph.  Let the source laws be

\[
p^{(0)}=(4/5,1/10,1/10),
\]

\[
p^{(1)}=(1/10,4/5,1/10).
\]

The two nondominated prefix trees have scenario costs

\[
\ell_A=(6/5,19/10),
\qquad
\ell_B=(19/10,6/5).
\]

Take a uniform initial hidden state and a transition that redraws the hidden
state uniformly at every step.  For horizon three and switching charge

\[
\kappa=2/5,
\]

exact dynamic programming gives

\[
V^{\rm perf}=4,
\]

while exact hidden-path enumeration gives

\[
V^{\rm clair}=159/40.
\]

Therefore

\[
\boxed{
R^{\rm perf}
=
4-159/40
=
1/40>0.
}
\]

The current hidden state is observed perfectly.  The remaining regret comes
solely from not knowing whether future state changes will justify paying the
switching charge.

When \(\kappa=0\), the oracle decomposes period by period and perfect current
state observation achieves the path oracle on every path:

\[
\boxed{
\kappa=0
\implies
V^{\rm perf}=V^{\rm clair}.
}

---

## 10. Relevance to an on-demand renderer

A renderer may face uncertainty over which future-query regime is currently
active.  Several models that sound similar are mathematically different:

- adversarial law uncertainty;
- a known stochastic hidden-law process;
- exact current-law observation;
- a noisy source-law signal;
- samples drawn from the active source law;
- unknown transition dynamics;
- a path-specific clairvoyant benchmark.

The belief-state result says that, under one known finite hidden Markov model,
the entire observation history can be compressed to an exact posterior belief
plus the previous representation choice.  It does not say that the true world
has a finite hidden state, that the model is known, or that this internal belief
is a physical substrate state.

---

## Nonclaims

- The hidden transition and observation channels are known and action
  independent.
- The signal reports information about the hidden source-law scenario, not a
  finite sample from the categorical source itself.
- Source laws, transition probabilities, and observation probabilities are
  exact rational model inputs.
- The posterior belief is sufficient under this model, not universally minimal
  under every observation or control architecture.
- The path oracle is a retrospective benchmark, not a causal policy.
- Expected Bayes regret is not minimax regret.
- Public or private randomization may matter under other objectives even though
  an uninformative signal has zero value here.
- Finite path and policy enumeration is bounded and fail-closed, not a
  scalability theorem.
- Internal beliefs, prefix lengths, and switch costs are not parent-substrate
  resource claims.
- None of these results is evidence that reality is simulated.

---

## Next research targets

1. Signals produced by sampled source symbols rather than a direct scenario
   channel.
2. Unknown transition matrices and exact finite credal-state filtering.
3. Action-dependent observations and active sensing costs.
4. Hidden-law control where codebook choice affects future source dynamics.
5. Bayesian learning of model parameters rather than filtering a known state.
6. Risk-sensitive, tail, and minimax-regret objectives on the same HMM.
7. Dynamic Blackwell comparisons with action-dependent experiments.
8. Infinite-horizon discounted and average-cost limits.
9. Approximate belief compression with explicit value-loss bounds.
