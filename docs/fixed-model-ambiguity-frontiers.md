# Fixed probabilistic model ambiguity and dynamic consistency

## Scope

A single Bayesian hidden-Markov model assigns exact probabilities to hidden
state, transitions, and observations. Robust work often begins from a finite
family of plausible models instead:

\[
\mathfrak M
=
\{M_1,\ldots,M_R\}.
\]

This note assumes that nature chooses one model once, before observations are
generated, and that the selected model remains fixed throughout the horizon.
The controller knows the family but not the selected member.

This is not Bayesian model averaging: no probability distribution over models
is supplied. The objective is

\[
\boxed{
\min_{\pi}
\max_{r\in[R]}
E_{M_r}^{\pi}[\text{cumulative code cost}].
}
\]

The same public observation may have different probabilities and induce
different hidden-state posteriors under different models. The controller's
public state is therefore a vector of model-conditional beliefs for every model
that still assigns positive probability to the observed history.

---

## 1. Complete model scenarios

Each scenario \(M_r\) contains:

- hidden-state source laws
  \[
  q^{(r,i)}\in\Delta_{n-1};
  \]
- hidden transition matrix \(P^{(r)}\);
- public observation kernel \(Z^{(r)}\);
- initial hidden-state prior \(b_0^{(r)}\).

All models share the source-symbol alphabet and public observation alphabet, but
they may have different hidden-state spaces and probabilities.

The code action set is common across models. Code actions do not alter model
transitions or observation kernels in this lane.

---

## 2. Public multi-model belief state

After a public observation history \(h\), define the active model set

\[
A(h)
=
\{r:\Pr_{M_r}(h)>0\}.
\]

For each active model, let

\[
b_h^{(r)}
=
\Pr_{M_r}(I_t=\cdot\mid h)
\]

be its model-conditional hidden-state posterior.

The exact public state is

\[
\boxed{
\beta(h)
=
\bigl((r,b_h^{(r)}):r\in A(h)\bigr).
}
\]

An observation with zero probability under model \(r\) removes that model from
the active set. No posterior probability over model labels is introduced.

---

## 3. Why one scalar robust Bellman value is not generally exact

A common robust recursion attaches one scalar value to the active model set and
maximizes over models at every public node. That makes the adversary
**rectangular** across time: after each observation, it may use whichever active
model gives the largest continuation, even if a different model generated the
past.

The fixed-model problem is weaker. One model coordinate must remain consistent
for the entire expected-cost calculation.

To preserve that condition, a policy is represented by a cost vector

\[
v=(v_r)_{r\in A(h)},
\]

where \(v_r\) is the expected future cost of the same public policy when model
\(M_r\) is the fixed true model.

---

## 4. Model-conditional observation branches

At public state

\[
\beta=((r,b^{(r)}))_{r\in A},
\]

model \(r\) first predicts

\[
\bar b_j^{(r)}
=
\sum_i b_i^{(r)}P_{ij}^{(r)}.
\]

For observation \(o\), its model-specific probability is

\[
\pi_r(o)
=
\sum_j\bar b_j^{(r)}Z_{jo}^{(r)}.
\]

If \(\pi_r(o)>0\), its next posterior is

\[
\tau_o^{(r)}(\bar b^{(r)})_j
=
\frac{
\bar b_j^{(r)}Z_{jo}^{(r)}
}{
\pi_r(o)
}.
\]

The next public multi-model state after observing \(o\) contains exactly the
models with positive \(\pi_r(o)\), together with those posteriors.

---

## 5. Fixed-model policy-vector frontier

Let

\[
\mathcal F_t(\beta,c^-)
\subseteq
\mathbb Q^{A(\beta)}
\]

be the Pareto-minimal expected future-cost vectors achievable by deterministic
public policies from period \(t\), given previous code \(c^-\).

### Terminal period

For code \(c\), model-coordinate stage cost is

\[
s_r(\beta,c,c^-)
=
\sum_i b_i^{(r)}
(q^{(r,i)})^\top\ell_c
+
\kappa\mathbf1\{c\ne c^-\}.
\]

Thus

\[
\boxed{
\mathcal F_T(\beta,c^-)
=
\operatorname{ParetoMin}
\{(s_r(\beta,c,c^-))_{r\in A}:c\in\mathcal C\}.
}
\]

### Nonterminal period

Choose one current code \(c\). For every public next observation \(o\), choose
one continuation vector

\[
w^o
\in
\mathcal F_{t+1}(\beta'_o,c).
\]

For fixed model \(r\), expected continuation is averaged with that same model's
observation probabilities:

\[
\boxed{
v_r
=
s_r(\beta,c,c^-)
+
\sum_o\pi_r(o)w^o_r.
}
\]

Terms with \(\pi_r(o)=0\) vanish, and model \(r\) is absent from that branch's
next active set.

The exact recursion is

\[
\boxed{
\mathcal F_t(\beta,c^-)
=
\operatorname{ParetoMin}
\left\{
(v_r)_{r\in A}
:
 c\in\mathcal C,
 w^o\in\mathcal F_{t+1}(\beta'_o,c)
\right\}.
}
\]

The robust value after the public history is

\[
\boxed{
V_t(\beta,c^-)
=
\min_{v\in\mathcal F_t(\beta,c^-)}
\max_{r\in A(\beta)}v_r.
}
\]

---

## 6. Initial observation

Before the first observation, every model is active with its own supplied
initial hidden-state prior. For each possible initial observation \(o\), choose
one continuation vector for the corresponding next multi-model state.

This creates one expected total-cost coordinate per fixed model:

\[
\boxed{
u_r
=
\sum_o
\pi_r^{(0)}(o)
\,w^o_r.
}
\]

The initial minimax value is

\[
\boxed{
V_{\rm fixed}
=
\min_u\max_r u_r.
}
\]

Policies for the same public observation are shared across every model that can
emit it. Policies for different observations may differ.

---

## 7. Rectangular model relaxation

Define a scalar recursion that, at every public node, maximizes over the active
model coordinates again. At a nonterminal node:

\[
W_t(\beta,c^-)
=
\min_c
\max_{r\in A(\beta)}
\left[
 s_r(\beta,c,c^-)
 +
 \sum_o\pi_r(o)W_{t+1}(\beta'_o,c)
\right].
\]

Because \(W_{t+1}\) may be supported by a different active model for each
observation history, this relaxation lets nature splice together model pieces.
Every fixed-model policy vector is feasible against the stronger rectangular
adversary, so

\[
\boxed{
V_{\rm fixed}
\le
V_{\rm rectangular}.
}
\]

The consistency gap is

\[
\boxed{
\Delta_{\rm model}
=
V_{\rm rectangular}-V_{\rm fixed}
\ge0.
}

This is the probabilistic-model analogue of the hidden-path coupling gap. The
two gaps have the same logical source: a marginal or nodewise maximum can violate
one globally fixed latent explanation.

---

## 8. Exact no-signal K3 model-consistency gap

Use complete confusion \(K_3\) and three complete models:

- model one emits source symbol one with probability one;
- model two emits source symbol two with probability one;
- model three emits source symbol three with probability one.

Each model has one hidden state and emits the same uninformative public symbol.
The horizon is three periods. Every complete binary prefix code has a permutation
of

\[
(1,2,2).
\]

### Fixed model

Assign the short leaf to a different source symbol in each period. Under every
fixed model, cumulative length is

\[
1+2+2=5.
\]

A counting argument makes five optimal, so

\[
\boxed{V_{\rm fixed}=5.}
\]

### Rectangular model

A nodewise model adversary selects a source symbol receiving length two at every
period, producing

\[
\boxed{V_{\rm rectangular}=6.}
\]

Hence

\[
\boxed{\Delta_{\rm model}=1.}
\]

No observation arrives, so this gap is caused entirely by whether model identity
is fixed globally or reselected dynamically.

---

## 9. Strict value of a noisy model-discriminating signal

Use two fixed models over source alphabet \(\{1,2,3\}\):

- model A emits source symbol one deterministically;
- model B emits source symbol two deterministically.

For one period, compare three public experiments.

### No signal

Both models emit the same observation. One code must be selected. Whichever
model receives the short leaf, the other incurs length two:

\[
\boxed{V_{\rm none}=2.}
\]

### Noisy signal

Observation `a` has probabilities

\[
\Pr_A(a)=3/4,
\qquad
\Pr_B(a)=1/4,
\]

and observation `b` has the reverse probabilities. Assign the short leaf to
symbol one after `a` and to symbol two after `b`. Expected costs are

\[
\frac34(1)+\frac14(2)=\frac54
\]

under A and symmetrically \(5/4\) under B. Therefore

\[
\boxed{V_{\rm noisy}=5/4.}
\]

### Fully model-revealing signal

A and B emit disjoint deterministic observations. The active model set becomes a
singleton before code choice, giving

\[
\boxed{V_{\rm full}=1.}
\]

Thus

\[
\boxed{2>5/4>1.}
\]

The noisy observation has strict robust value even though no prior probability
over models is supplied.

---

## 10. Zero-probability observations and model elimination

If model \(r\) assigns zero probability to the observed public history, it is
removed from the active set. This is logical elimination under the supplied
model, not posterior downweighting.

A deterministic model-revealing observation therefore creates singleton active
sets and turns robust model ambiguity into an ordinary single-model belief
problem on that branch.

If every model gives every public history positive probability, no model is ever
logically eliminated, although their hidden-state posteriors may still diverge.

---

## 11. Fixed-model robustness, Bayesian averaging, and rectangular robustness

These are different criteria.

### Bayesian model averaging

Supply prior weights \(\lambda_r\) and minimize

\[
\sum_r\lambda_rE_{M_r}[C].
\]

### Fixed-model minimax

Nature chooses one model once:

\[
\min_\pi\max_rE_{M_r}^{\pi}[C].
\]

### Rectangular minimax

Nature may select locally worst model components at future public nodes.

In general,

\[
\text{Bayesian value},
\quad
V_{\rm fixed},
\quad
V_{\rm rectangular}
\]

need not coincide. Moving among them requires an explicit assumption about how
model uncertainty is resolved over time.

---

## 12. Why this matters for simulation-style inference

A generic simulator hypothesis is itself a model class. Treating its unknown
implementation choices as if an adversary can reselect a different architecture
after every observation can make the class artificially powerful and therefore
unfalsifiable. Treating one architecture as fixed can produce stricter cross-time
consistency constraints.

Conversely, averaging over architectures requires a justified prior over them.
The repository therefore keeps three objects separate:

\[
\boxed{
\text{one fixed unknown model},
\quad
\text{a prior mixture of models},
\quad
\text{rectangular local model uncertainty}.
}

The mathematics does not identify which uncertainty semantics applies to
reality. That is an additional modeling claim.

---

## Bounded exactness

The exact frontier may grow rapidly with:

- model count;
- observation count;
- horizon;
- reachable multi-model posterior states;
- deterministic code actions;
- continuation-policy combinations.

The implementation declares hard caps on every frontier and combination search.
Exceeding a cap raises an error rather than returning a truncated theorem.

---

## Nonclaims

- Nature chooses one of the supplied models; the family need not contain the
  true data-generating process.
- No probability distribution over models is inferred or assumed.
- The selected fixed model does not change over time.
- Hidden dynamics remain stochastic within each selected model.
- Observation and transition models are code-independent.
- The rectangular relaxation is a stronger uncertainty model, not an
  approximation guaranteed to be close.
- Model elimination from a zero-probability signal is valid only if the supplied
  model probabilities are exact.
- The result does not cover continuous model classes, unknown parameters,
  confidence sets, or learning.
- Internal expected code length is not parent hardware, energy, mass, or
  spacetime.
- None of these results establishes that reality is simulated.

---

## Next research targets

1. Finite prior-weighted model averaging and comparison with fixed-model minimax.
2. Ambiguity sets over model priors, transitions, or observation kernels.
3. Rectangularity diagnostics and dynamic-consistency conditions.
4. Continuous parameter families with certified finite abstractions.
5. Model learning and experiment design under code-dependent sensing.
6. Dynamic regret against a model-aware oracle.
7. Networked agents holding different model families or observations.
8. Statistical tests that discriminate fixed architectures without silently
   allowing architecture switching after the data are observed.
