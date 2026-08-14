# Observation channels, public randomization, and the value of source-law information

## Scope

The drift information-pattern work assumes that a source law is observed
exactly when the model says it is observed. Real measurements are generally
noisy.

This note introduces a finite one-shot observation channel:

1. Nature chooses one rational source-law scenario

   \[
   p^{(r)}\in\Delta_{n-1},
   \qquad r\in\{1,\ldots,R\}.
   \]

2. A public signal `Y` is drawn through a declared rational channel

   \[
   O_{r,y}=P(Y=y\mid r).
   \]

3. The designer observes `Y` and selects a deterministic zero-error binary
   prefix codebook. Every decoder also knows the selected codebook.

4. The period source-coding loss under scenario `r` is the scenario expectation
   of the selected codeword lengths.

The analysis distinguishes two resources that are frequently conflated:

- **information:** dependence of the signal distribution on the active source
  law;
- **public randomization:** randomness in the observed signal or a separate
  shared seed, even when that randomness is statistically independent of the
  source law.

All probabilities and finite-game values are exact rational numbers.

---

## 1. Rational observation channel

A channel is a row-stochastic matrix

\[
O\in\mathbb Q_{\ge0}^{R\times m},
\qquad
\sum_{y=1}^{m}O_{r,y}=1.
\]

Rows index source-law scenarios and columns index public signals.

Three constructors are useful.

### Perfect observation

\[
O=I_R.
\]

The signal identifies the scenario exactly.

### Uninformative public signal

For one signal law `u`,

\[
O_{r,y}=u_y
\qquad\forall r.
\]

The signal is independent of the active scenario. It contains no source-law
information, but it can still act as public randomness.

### Symmetric noisy observation

For `R>=2` and declared correct probability `a`,

\[
O_{r,y}
=
\begin{cases}
a,&y=r,\\[3pt]
\dfrac{1-a}{R-1},&y\ne r.
\end{cases}
\]

At

\[
a=1/R,
\]

the rows are identical and the signal is uninformative. Values below `1/R`
can be anti-informative rather than simply “worse noise,” because observing one
label makes that label less likely.

---

## 2. Codebook and policy costs

Let the bounded complete deterministic zero-error prefix-code universe be

\[
\mathcal C.
\]

Codebook `c` has state-length vector

\[
\ell_c.
\]

Its cost in source-law scenario `r` is

\[
L_{r,c}
=
(p^{(r)})^\top\ell_c.
\]

A deterministic signal policy is a map

\[
\delta:\{1,\ldots,m\}\to\mathcal C.
\]

Its scenario cost is

\[
\boxed{
A_{r,\delta}
=
\sum_{y=1}^{m}
O_{r,y}L_{r,\delta(y)}.
}
\]

The implementation exhausts every bounded map `delta`, deduplicates equal
scenario-cost vectors, and removes policies that are componentwise dominated
across every source-law scenario.

Dominance pruning is safe: if policy `delta_1` costs no more than `delta_2` in
every scenario, no nonnegative scenario mixture or minimax objective can make
`delta_2` preferable.

---

## 3. Five distinct benchmark values

The solver returns five costs.

### Deterministic no-signal value

One fixed deterministic codebook is used:

\[
\boxed{
V_{\rm no,det}
=
\min_{c\in\mathcal C}
\max_rL_{r,c}.
}
\]

### Shared-randomness no-signal value

A public seed independent of the source scenario selects a deterministic
codebook with mixture `x`:

\[
\boxed{
V_{\rm no,shared}
=
\min_{x\in\Delta(\mathcal C)}
\max_r
\sum_cx_cL_{r,c}.
}
\]

This is solved with an exact rational primal-dual zero-sum game certificate.

### Deterministic observation value

The signal policy is deterministic:

\[
\boxed{
V_{\rm obs,det}
=
\min_{\delta}
\max_rA_{r,\delta}.
}
\]

Although `delta` is deterministic, a random public signal can induce a random
codebook. Consequently this benchmark can include randomization value even when
the signal is uninformative.

### Shared-randomness observation value

A public seed chooses a complete deterministic signal policy:

\[
\boxed{
V_{\rm obs,shared}
=
\min_{x\in\Delta(\mathcal D)}
\max_r
\sum_{\delta}x_{\delta}A_{r,\delta}.
}
\]

Here `D` is the finite deterministic policy set. The seed is independent of the
scenario and known to every decoder.

### Perfect-information value

If the active scenario is known before selecting a codebook,

\[
\boxed{
V_{\rm perfect}
=
\max_r\min_cL_{r,c}.
}
\]

This is the best achievable benchmark in the declared one-shot problem.

---

## 4. Value hierarchy

The following inequalities hold:

\[
\boxed{
V_{\rm perfect}
\le
V_{\rm obs,shared}
\le
V_{\rm no,shared}
\le
V_{\rm no,det}.
}
\]

Also,

\[
\boxed{
V_{\rm obs,shared}
\le
V_{\rm obs,det}
\le
V_{\rm no,det}.
}
\]

### Why perfect information is best

A designer who knows the scenario can simulate the declared observation
channel with public randomness and then imitate any signal policy. Perfect
information therefore cannot cost more.

### Why observation cannot hurt with shared randomization

A signal policy may ignore the signal. A mixture over constant signal policies
reproduces any shared-randomness no-signal codebook mixture. Thus

\[
V_{\rm obs,shared}\le V_{\rm no,shared}.
\]

### Why mixing cannot hurt

Every deterministic policy is a degenerate mixture, giving

\[
V_{\rm obs,shared}\le V_{\rm obs,det}.
\]

### No general order between deterministic observation and shared no-signal

These two resources are different:

- `V_obs,det` has a signal but no separate shared seed;
- `V_no,shared` has a shared seed but no scenario-dependent signal.

Either may be more useful in a general finite problem. The repository does not
silently impose an ordering that the information sets do not justify.

---

## 5. Separating randomization value from information value

Define the public-randomization value without source information as

\[
\boxed{
\Delta_{\rm rand}
=
V_{\rm no,det}-V_{\rm no,shared}.
}
\]

Define information value relative to an already randomized baseline as

\[
\boxed{
\Delta_{\rm info}
=
V_{\rm no,shared}-V_{\rm obs,shared}.
}
\]

The total deterministic signal improvement is

\[
\boxed{
\Delta_{\rm det-signal}
=
V_{\rm no,det}-V_{\rm obs,det}.
}
\]

These quantities answer different questions.

An uninformative but random public signal can have

\[
\Delta_{\rm det-signal}>0
\]

while

\[
\Delta_{\rm info}=0.
\]

The improvement then comes entirely from coordination randomness, not from
learning the source law.

This is a useful warning for evaluation design: comparing a signal-assisted
deterministic policy only against a deterministic no-signal baseline can
misattribute randomization gain to prediction accuracy.

---

## 6. Exact `K3` source-law family

Consider a complete three-state confusion graph. The nondominated binary prefix
length vectors are permutations of

\[
(1,2,2).
\]

Use three source-law scenarios:

\[
p^{(1)}=(4/5,1/10,1/10),
\]

\[
p^{(2)}=(1/10,4/5,1/10),
\]

\[
p^{(3)}=(1/10,1/10,4/5).
\]

A codebook whose depth-one leaf matches the heavy state costs

\[
\frac45(1)+\frac1{10}(2)+\frac1{10}(2)
=
\boxed{\frac65}.
\]

If the depth-one leaf is assigned to a light state, the cost is

\[
\frac1{10}(1)+\frac9{10}(2)
=
\boxed{\frac{19}{10}}.
\]

### Deterministic and shared no-signal values

Every fixed depth-one assignment is punished by one of the other scenarios:

\[
\boxed{
V_{\rm no,det}=\frac{19}{10}.
}
\]

Mixing uniformly over the three depth-one assignments gives every state expected
length

\[
\frac{1+2+2}{3}=\frac53,
\]

so

\[
\boxed{
V_{\rm no,shared}=\frac53.
}
\]

The pure randomization value is therefore

\[
\boxed{
\Delta_{\rm rand}
=
\frac{19}{10}-\frac53
=
\frac7{30}.
}
\]

### Perfect information

The depth-one leaf is assigned to the known heavy state:

\[
\boxed{
V_{\rm perfect}=\frac65.
}
\]

The perfect information value over the shared-randomness baseline is

\[
\boxed{
\frac53-\frac65
=
\frac7{15}.
}
\]

---

## 7. Uninformative public signal example

Let the public signal have three equiprobable outcomes independently of the
source scenario:

\[
O_{r,y}=1/3.
\]

A deterministic signal policy maps the three signals to the three different
short-leaf codebooks. The signal therefore implements the uniform codebook
mixture without a separate seed.

Hence

\[
\boxed{
V_{\rm obs,det}
=
V_{\rm obs,shared}
=
V_{\rm no,shared}
=
\frac53.
}
\]

But

\[
V_{\rm no,det}=\frac{19}{10}.
\]

Thus the public signal improves the deterministic baseline by

\[
\frac7{30},
\]

even though it contains exactly zero source-law information.

The information value over the shared-randomness baseline is correctly zero:

\[
\boxed{\Delta_{\rm info}=0.}
\]

---

## 8. Symmetric half-accurate observation

Use the symmetric channel with

\[
P(Y=r\mid r)=1/2
\]

and each wrong label having probability

\[
1/4.
\]

Assign the depth-one leaf according to the observed signal. In each true
scenario, the aligned code is selected with probability `1/2` and a misaligned
code with total probability `1/2`. Therefore

\[
V
=
\frac12\left(\frac65\right)
+
\frac12\left(\frac{19}{10}\right)
=
\boxed{\frac{31}{20}}.
\]

Exact policy enumeration and the shared zero-sum game both certify

\[
\boxed{
V_{\rm obs,det}
=
V_{\rm obs,shared}
=
\frac{31}{20}.
}
\]

The source information value beyond public randomization is

\[
\boxed{
\Delta_{\rm info}
=
\frac53-rac{31}{20}
=
\frac7{60}.
}
\]

The total deterministic signal improvement is

\[
\boxed{
\frac{19}{10}-\frac{31}{20}
=
\frac7{20}.
}

Only one third of this total improvement is incremental information beyond the
shared-randomness baseline; the rest is the randomization gap already available
without source information.

---

## 9. Exact sensing-cost threshold

Suppose acquiring the observation channel costs `kappa`, while the alternative
is the shared-randomness no-signal strategy.

The sensing-assisted total is

\[
V_{\rm obs,shared}+\kappa.
\]

Observation is strictly worthwhile exactly when

\[
V_{\rm obs,shared}+\kappa
<
V_{\rm no,shared}.
\]

Therefore the exact threshold is

\[
\boxed{
\kappa_c
=
V_{\rm no,shared}-V_{\rm obs,shared}
=
\Delta_{\rm info}.
}
\]

For the half-accurate `K3` channel,

\[
\boxed{\kappa_c=\frac7{60}}.
\]

At sensing cost

\[
\kappa=1/10<7/60,
\]

the total is

\[
\frac{31}{20}+rac1{10}
=
\boxed{\frac{33}{20}}
<
\frac53.
\]

At the exact boundary the two strategies tie. The implementation uses a
conservative deterministic convention: it declines sensing unless sensing is
strictly better.

---

## 10. Blackwell garbling order

Let channel `B` be obtained by passing channel `A` through a row-stochastic
garbling kernel `G`:

\[
\boxed{B=AG.}
\]

A designer with channel `A` and public shared randomness can:

1. observe the `A` signal;
2. sample the garbled `B` signal using `G`;
3. execute any policy designed for `B`.

Thus every shared-randomness policy feasible under `B` can be simulated under
`A`, and

\[
\boxed{
A\succeq_B B
\quad\Longrightarrow\quad
V_{\rm obs,shared}(A)
\le
V_{\rm obs,shared}(B).
}
\]

This is the finite Blackwell order for the declared coding loss.

### Exact `K3` checks

Garbling perfect observation by the half-accurate symmetric channel gives

\[
\frac65
\le
\frac{31}{20},
\]

with value loss

\[
\boxed{\frac7{20}}.
\]

Garbling the half-accurate channel into an independent uniform signal gives

\[
\frac{31}{20}
\le
\frac53,
\]

with value loss

\[
\boxed{\frac7{60}}.
\]

The latter is exactly the information value beyond public randomization.

### Why shared randomness is stated explicitly

A stochastic garbling requires random sampling conditional on the informative
signal. A deterministic policy without public or common randomness need not be
able to reproduce every garbled policy. The theorem therefore applies to the
shared-randomness value, where the simulation is an admitted resource.

---

## 11. Blackwell order is stronger than one scalar information score

Mutual information, classification accuracy, entropy reduction, and coding
value answer different questions.

Blackwell dominance says one channel can simulate another for **every decision
problem** through garbling. It is a partial order: many channels are
incomparable.

A scalar such as mutual information can rank two channels while failing to
capture which one is better for a particular asymmetric loss. Conversely, two
channels with equal mutual information can induce different robust coding
values.

This repository therefore treats the exact decision value as the primary object
for this lane. No scalar channel statistic is substituted for the coding game.

---

## 12. Abstract interpretation

Observation value depends on more than predictive accuracy.

A signal can create value through:

- correlation with the hidden environment;
- public coordination randomness;
- timing before an action;
- compatibility with the action loss;
- future consequences such as switching or commitment costs.

The relevant resource is therefore not “bits of information” in isolation, but

\[
\boxed{
\text{decision value of an information structure}
}

under a declared loss and causal interface.

For a hypothetical renderer, this means an observation is useful only insofar
as it changes an admissible future action or state representation. The same
signal can be valuable for one task and irrelevant for another. This is a
general decision-theoretic statement, not evidence that observations trigger
rendering.

---

## Nonclaims

- The scenario index is selected adversarially from a finite declared set.
- The observation channel is known exactly and has rational probabilities.
- Every decoder knows the selected codebook and any shared public seed.
- Shared-randomness and deterministic policy values are distinct resources.
- Sensing cost is a declared design input rather than an inferred physical
  quantity.
- The one-shot model has no source drift, repeated measurements, or learning.
- Blackwell monotonicity is claimed for the shared-randomness decision value,
  not every deterministic implementation.
- Mutual information is not computed or claimed sufficient for decision value.
- Internal expected code length is not parent-universe memory, energy, mass, or
  computation.
- None of these observation-channel results is generic evidence for simulation.

---

## Next research targets

1. Compose observation channels with bounded source-law drift.
2. Replace exact current-law knowledge by a posterior or set-valued information
   state.
3. Derive finite-horizon robust belief-state Bellman recurrences.
4. Separate public signals from private encoder-only observations.
5. Price repeated sensing and derive when to measure again.
6. Study channels that are Blackwell-incomparable but ordered by one coding
   loss.
7. Add pathwise observation histories and switching costs.
8. Compare Bayesian scenario priors with minimax scenario selection.
9. Derive certified approximations for continuous observation spaces.
