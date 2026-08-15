# Active experiments under one globally fixed probabilistic model

## Scope

This layer extends finite fixed-model ambiguity by allowing the controller to
choose which public experiment to run before each period's observation.
Nature chooses one model \(M\in\mathfrak M\) once, before the horizon, and that
same model generates every later observation and hidden-state transition.

The timing in period \(t\) is

1. choose experiment \(e_t\);
2. observe public signal \(Y_t\);
3. choose zero-error prefix code \(c_t\);
4. pay acquisition cost \(a(e_t)\) plus expected code length;
5. transition the hidden state if another period remains.

Experiment choices and later codes may depend on the full public history. All
probabilities and costs are exact rational inputs.

---

## 1. Fixed-model policy vectors

At a public pre-observation history, let the still-compatible fixed models be
\(A\). For each \(m\in A\), retain its model-conditional hidden-state belief
\(b^{(m)}\). A deterministic continuation policy has one expected future cost
per globally fixed model,

\[
v=(v_m)_{m\in A}.
\]

The exact robust value is obtained from the Pareto-minimal achievable vectors:

\[
V_t=\min_{v\in\mathcal F_t}\max_{m\in A}v_m.
\]

The vector representation is essential. Replacing it by a scalar maximum at
every public node would permit the adversary to reselect a different model
later and therefore solve a stronger rectangular problem.

---

## 2. Experiment and observation branches

Experiment \(e\) supplies one observation kernel \(Z^{(m,e)}\) for each fixed
model \(m\). Given current model-conditional belief \(b^{(m)}\), observation
\(y\) has probability

\[
\pi_m^e(y)=\sum_i b_i^{(m)}Z_{iy}^{(m,e)}.
\]

If \(\pi_m^e(y)>0\), the current posterior is

\[
\tau_{m,e,y}(b)_i
=
\frac{b_i Z_{iy}^{(m,e)}}{\pi_m^e(y)}.
\]

Models assigning zero probability to the observed signal disappear from that
public branch. Importantly, a model with positive probability remains the same
model in every future period.

For nonterminal periods, its next pre-observation belief is

\[
\bar b_j^{(m)}
=
\sum_i \tau_{m,e,y}(b)_iP_{ij}^{(m)}.
\]

---

## 3. Exact recursion

Fix an experiment \(e\). For each possible public signal \(y\), the controller
may choose a different current code and a different future experiment policy.
Let \(d_y\) denote one such signal-contingent decision. For fixed model \(m\),
its expected total cost is

\[
\boxed{
C_m(e,(d_y)_y)
=
a(e)
+
\sum_y \pi_m^e(y)
\left[
L_m(c_y\mid y)+V_m(d_y)
\right].
}
\]

At the terminal period the continuation term vanishes. Enumerating every
bounded experiment, signal-contingent code, and continuation-frontier choice,
then Pareto pruning the resulting model-cost vectors, gives the exact finite
recursion implemented in `exact_active_fixed_model_experiment_design`.

Adding an experiment cannot worsen the minimizing controller because it may
ignore the new action and execute an old policy.

---

## 4. The key semantic separation: information versus public randomness

A public signal need not reveal anything about the fixed model to improve a
deterministic minimax policy.

Suppose the signal law is identical for every hidden state of every model:

\[
P(Y=y\mid M=m,I=i)=r_y
\qquad\forall m,i.
\]

Then

\[
Y\perp (M,I).
\]

The signal contains zero source/model information. Nevertheless, because the
signal is public and arrives before the code choice, a deterministic policy may
map different signal outcomes to different codebooks. The signal therefore
implements a source-independent public random seed.

Consequently,

\[
\boxed{
\text{observation gain}
\neq
\text{information gain in general minimax control}.
}
\]

Any scientific interpretation of an intervention's decision value must separate
what comes from epistemic discrimination from what comes merely from admitted
randomization resources.

---

## 5. Exact K3 decomposition

Take complete confusion \(K_3\) and three globally fixed one-state models. Model
\(m\) emits source symbol \(m\) deterministically. Every complete binary prefix
code has a length vector that is a permutation of

\[
(1,2,2).
\]

### No public signal

One deterministic code must be chosen. At least two models receive length two,
so

\[
\boxed{V_{\rm none}=2.}
\]

### Source-independent public three-way coin

Let the public signal be uniform on three labels under every model. Rotate which
source symbol receives the short leaf across the three labels. Every model then
has expected length

\[
\frac13(1+2+2)=\frac53.
\]

Hence

\[
\boxed{V_{\rm rand}=\frac53.}
\]

The signal is statistically independent of the fixed model, so the exact gain

\[
\boxed{2-\frac53=\frac13}
\]

is pure public-randomization value.

### Fully model-revealing experiment

Let model \(m\) emit public label \(m\) deterministically. The controller gives
the revealed model's source symbol the short leaf:

\[
\boxed{V_{\rm reveal}=1.}
\]

Relative to the randomness-matched public-coin baseline, the additional
informational gain is

\[
\boxed{
\frac53-1=\frac23.
}
\]

Thus the total no-signal improvement decomposes exactly as

\[
\boxed{
2-1
=
\underbrace{\frac13}_{\text{public randomness}}
+
\underbrace{\frac23}_{\text{model information}}.
}
\]

This decomposition is example-specific in magnitude but not in the underlying
semantic distinction.

---

## 6. Sensing cost must be compared with a resource-matched baseline

If revealing the model costs \(\kappa\), its one-period value is

\[
1+\kappa.
\]

Against the no-signal deterministic baseline, the apparent threshold is one.
But if a source-independent public randomizer is already admitted, the correct
resource-matched baseline is \(5/3\). Revelation is then strictly worthwhile
only when

\[
1+\kappa<\frac53,
\]

or

\[
\boxed{\kappa<\frac23.}
\]

At equality, the implementation's deterministic tie break selects the
lexicographically earlier public-coin experiment.

This is a general warning: intervention value can be overstated when the
comparison baseline differs in noninformational coordination resources.

---

## 7. Persistence creates option value for early information

The model identity is fixed across time. Therefore an informative observation
can affect more than the current code choice.

In the same three-model \(K_3\) example over three periods, no observations are
needed to rotate the short leaf across the three models. Every fixed model then
pays

\[
1+2+2=5,
\]

so

\[
V_{\rm no\ sensing}=5.
\]

Now make a perfectly revealing experiment available at acquisition cost
\(3/2\). Running it immediately identifies the globally fixed model. The current
and two future periods can all assign that model's source symbol the short leaf,
while later periods use the free no-signal experiment. The total is

\[
\boxed{
1+1+1+\frac32=\frac92<5.
}
\]

The immediate one-period coding improvement is not the whole value. Early
information changes the future feasible policy because the same latent model
must remain responsible for later observations and source laws.

This is an exact finite form of **option value of information under latent-state
persistence**.

---

## 8. Why this matters for simulation-theory arguments

A proposed observation or intervention can appear highly valuable for several
different reasons:

- it distinguishes competing latent mechanisms;
- it reveals a hidden state inside one mechanism;
- it supplies public randomness without revealing either;
- it rules out models through zero-probability observations;
- it has persistent option value because one model must explain the future;
- it changes the admissible action set or incurs an acquisition cost.

Collapsing these effects into one number called "information" can produce a
category error. In particular, a decision improvement under a random public
signal is not by itself evidence that the signal learned anything about whether
reality is simulated.

---

## Nonclaims

- The finite model family is declared, not learned from data.
- Model probabilities are not assigned; the outer criterion is minimax over one
  fixed model.
- Experiment kernels and costs are treated as exact inputs.
- The controller is deterministic conditional on public history; random public
  observations can nevertheless implement randomized behavior ex ante.
- Code actions do not alter hidden dynamics in this lane.
- Enumeration is bounded and is not a scalability theorem.
- Decision value is not mutual information, KL divergence, Bayes factor, or
  empirical evidence for simulation.

## Next targets

1. Add statistically calibrated uncertainty over experiment kernels.
2. Add safety budgets and model-dependent intervention harm.
3. Compare ex-ante fixed-model minimax design with rectangular adaptive design.
4. Add model priors and derive a robust-Bayes interpolation.
5. Add experiment actions that also change hidden-state transitions, creating
   genuine dual control.
