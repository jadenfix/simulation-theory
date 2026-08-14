# Stochastic source-law observations and exact rational belief control

## Scope

The deterministic coarsened-observation lane is a worst-case set-membership
game: the controller knows an information set and nature chooses one hidden path.
This note studies a different object. It assumes a fully specified finite hidden
Markov model with rational probabilities and minimizes **expected** cumulative
zero-error prefix length.

The model contains:

- hidden law state \(I_t\in\{1,\ldots,m\}\);
- categorical source law \(q^{(i)}\in\Delta_{n-1}\) for each hidden state;
- Markov transition matrix \(P_{ij}\);
- stochastic observation kernel \(Z_{io}\);
- exact initial hidden-state prior \(b_0\);
- deterministic zero-error prefix-code actions;
- rational code-switching penalty.

The transition and observation laws are treated as known model inputs. They are
not estimated or given statistical coverage by this theorem.

---

## 1. Timing

Before the first code choice, an observation of the initial hidden state is
emitted. At each later period:

1. the current posterior belief is available;
2. the controller chooses one code;
3. expected source-code length and any switching penalty are charged;
4. the hidden state transitions according to \(P\);
5. the next observation is emitted according to \(Z\);
6. the posterior is updated exactly.

The observation arrives before the action whose cost it informs. Changing this
timing changes the dynamic program.

---

## 2. Exact observation update

Let \(\bar b\) be a predictive belief before observing \(o\). The observation
probability is

\[
\Pr(o\mid\bar b)
=
\sum_i\bar b_i Z_{io}.
\]

For a positive-probability observation, Bayes' rule gives

\[
\boxed{
\tau_o(\bar b)_i
=
\frac{\bar b_iZ_{io}}
{\sum_j\bar b_jZ_{jo}}.
}
\]

All quantities remain rational when the supplied model is rational.
Zero-probability observations are omitted from the reachable tree.

After a code action, the next predictive belief is

\[
\boxed{
\bar b'_j
=
\sum_i b_iP_{ij}.
}
\]

The next posterior branches are obtained by applying \(\tau_o\) to \(\bar b'\).

---

## 3. Belief sufficiency

Conditioned on the public observation history, the posterior belief contains
all information needed to predict:

- the current hidden law distribution;
- expected current code length;
- the distribution of the next hidden state;
- the distribution of the next observation;
- every future posterior reached under the declared model.

Because code actions do not affect \(P\) or \(Z\) in this lane, two public
histories with the same posterior belief and previous code have identical
future control problems.

Thus the exact controller state is

\[
\boxed{(t,b,c^-).}
\]

This is a probabilistic sufficient statistic. It is not interchangeable with
the information set used in the adversarial coarsened-observation game.

---

## 4. Stage cost

Let code \(c\) have source-symbol length vector \(\ell_c\). In hidden law state
\(i\), its expected one-shot source length is

\[
g_i(c)
=
(q^{(i)})^\top\ell_c.
\]

Under posterior belief \(b\), expected stage cost is

\[
\boxed{
G(b,c,c^-)
=
\sum_i b_i g_i(c)
+
\kappa\mathbf1\{c\ne c^-\}.
}
\]

The first code has a sentinel predecessor and pays no switch cost.

---

## 5. Exact belief-state Bellman recursion

At terminal period \(T\),

\[
\boxed{
V_T(b,c^-)
=
\min_c G(b,c,c^-).
}
\]

For \(t<T\), let \(\bar b'=bP\). For every observation \(o\) with positive
probability under \(\bar b'\), define

\[
b'_o=\tau_o(\bar b').
\]

Then

\[
\boxed{
V_t(b,c^-)
=
\min_c
\left[
G(b,c,c^-)
+
\sum_o
\Pr(o\mid\bar b')
V_{t+1}(b'_o,c)
\right].
}
\]

### Proof

Fix current \((b,c^-)\). The chosen code determines the current expected cost
and becomes the previous code for the continuation. Since actions do not alter
the hidden transition or observation kernel, the distribution of the next
observation and posterior branches depends only on \(b\). Conditional on each
next observation, the posterior is sufficient by the preceding argument.
Applying the induction hypothesis to every continuation branch and taking the
minimum current action proves the recursion.

The implementation stores every reachable rational belief node, selected code,
stage cost, observation probability, posterior, and continuation value. The
certificate replays every Bellman equality and every alternative action exactly.

---

## 6. Initial observation

The supplied initial prior \(b_0\) is defined before the first observation. Let

\[
\pi_o
=
\Pr(o\mid b_0),
\qquad
b_o=\tau_o(b_0).
\]

The initial expected value is

\[
\boxed{
V_0
=
\sum_{o:\pi_o>0}
\pi_oV_1(b_o,\bot).
}
\]

This differs from a worst-case initial observation, where nature chooses the
highest-cost signal cell. The distinction between expectation and worst case is
part of the model, not an implementation detail.

---

## 7. Blackwell garbling monotonicity

Let a fine observation kernel be \(Z^f\). Let \(G\) be a row-stochastic
post-processing channel from fine observations to coarse observations. Define

\[
\boxed{
Z^c=Z^fG.
}
\]

The coarse signal is a stochastic garbling of the fine signal.

A controller receiving the fine signal can simulate the coarse signal by
applying \(G\) with source-independent private randomization and then execute
any coarse-signal policy. The resulting joint hidden-state, coarse-observation,
action, and cost distribution is exactly the coarse model's distribution.

Finite expected-cost belief control admits an optimal deterministic policy: at
each belief node a minimum of finitely many action values is attained. Therefore
the deterministic optimum under the fine signal is no larger than the value of
the randomized emulation.

Hence

\[
\boxed{
V(Z^f)
\le
V(Z^c).
}

The exact information value is

\[
\boxed{
\mathcal V(Z^f:Z^c)
=V(Z^c)-V(Z^f)
\ge0.
}

This theorem compares observation experiments inside a fixed probabilistic
model. It does not say that a more detailed sensor is free, accurate, or
available in reality.

---

## 8. No-information and full-information endpoints

### No information

If every hidden state emits the same single observation, the posterior after an
observation equals the predictive belief. The code depends only on the current
belief generated by the Markov model and previous public observations—which
carry no state information.

### Full information

If hidden state \(i\) emits unique observation \(i\) deterministically, every
posterior after observation is a point mass. The controller knows the exact
current hidden law state before selecting the code.

These are probabilistic endpoints. Their values need not equal the adversarial
open-loop and feedback values because the source-law evolution is averaged under
\(P\), not maximized over a transition relation.

---

## 9. Strict K3 deterministic-observation chain

Use three hidden point-mass source laws, identity hidden-state transitions, a
uniform initial prior, complete confusion \(K_3\), no switching penalty, and a
two-period horizon. Every complete binary prefix code has a permutation of

\[
(1,2,2).
\]

### No information

The posterior remains uniform. Expected cost per period is

\[
\frac13(1+2+2)=\frac53,
\]

so

\[
\boxed{V_{\rm none}=\frac{10}{3}.}
\]

### Partition \(\{1\},\{2,3\}\)

With probability \(1/3\), the singleton state is known and costs two over two
periods. With probability \(2/3\), the posterior is uniform on a pair; assigning
the short leaf to either member costs \(3/2\) per period, or three total. Thus

\[
\boxed{
V_{\rm partial}
=
\frac13(2)+\frac23(3)
=
\frac83.
}
\]

### Full information

The point-mass state is known and receives the short leaf each period:

\[
\boxed{V_{\rm full}=2.}
\]

Therefore

\[
\boxed{
\frac{10}{3}
>
\frac83
>
2.
}
\]

This is an expected-cost analogue of the strict deterministic partition chain,
but it is generated by posterior averaging rather than worst-case hidden-state
coordinates.

---

## 10. Strict stochastic garbling example

Again use uniform static point-mass \(K_3\), now for one period.

Start with the full signal. Garble it so that, independently:

- the exact state label is revealed with probability \(1/2\);
- an uninformative symbol `?` is emitted with probability \(1/2\).

On an exact label, optimal cost is one. On `?`, the posterior is uniform and
optimal expected cost is \(5/3\). Therefore

\[
\boxed{
V_{\rm noisy}
=
\frac12(1)+\frac12\left(\frac53\right)
=
\frac43.
}
\]

Garbling all four outputs into one symbol yields no information and value

\[
\boxed{V_{\rm none}=\frac53.}
\]

Thus

\[
\boxed{
1
<
\frac43
<
\frac53.
}
\]

Each exact Blackwell information gain is \(1/3\) in this example.

---

## 11. Bayesian belief versus robust information-set frontiers

The two partial-observation lanes answer different questions.

### Bayesian lane

- one exact prior over hidden states;
- one exact transition matrix;
- one exact observation kernel;
- expected cumulative cost;
- posterior belief is sufficient;
- scalar Bellman values are exact.

### Robust set-membership lane

- one set of possible hidden states;
- one transition relation;
- deterministic observation cells;
- worst-case hidden path;
- no probabilities over possible hidden states;
- a Pareto cost-vector frontier is needed to preserve hidden-path consistency.

Replacing one with the other changes the claim. A prior is not a confidence set,
and a confidence set is not a posterior.

---

## 12. Bounded exactness

Reachable rational beliefs can proliferate with horizon and observation count.
The implementation therefore declares hard caps on:

- deterministic code candidates;
- reachable belief nodes;
- total positive-probability observation branches.

Exceeding a cap raises an error. The solver never labels a truncated belief tree
as exact.

---

## Nonclaims

- The initial prior, transition matrix, and observation kernel are assumed known.
- The model supplies no frequentist coverage guarantee for those probabilities.
- The source law is not adversarial in this lane; costs are averaged under the
  hidden Markov model.
- The controller observes the signal before choosing the current code.
- Code actions do not affect hidden transitions or observation quality.
- The Blackwell proof uses source-independent randomization as a simulation
  device; the exact finite control optimum itself is deterministic.
- The result does not cover continuous beliefs, unknown parameters, online
  learning, optional stopping, or robust Bayesian ambiguity.
- Expected message length is not peak bandwidth, queueing delay, decoder update
  cost, or parent-substrate storage.
- None of these results is evidence that reality is simulated.

---

## Next research targets

1. Robust Bayesian games with a set of transition or observation kernels.
2. Parameter learning and dual control where code choices affect observation
   quality.
3. Active sensing with an explicit observation-acquisition cost.
4. Exact finite belief-state abstractions for continuous source-law models.
5. Risk-sensitive criteria beyond expected cumulative length.
6. Anytime-valid filtering under drift and model misspecification.
7. Networked decoders with different observation kernels.
8. Shared-randomness code policies and common-randomness accounting.
