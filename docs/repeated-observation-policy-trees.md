# Repeated noisy observations and finite policy trees

## Scope

A single noisy observation and a sequence of noisy observations are different
information structures. Repetition creates three new effects:

1. evidence can accumulate about a fixed hidden source-law scenario;
2. the observation history itself provides public coordination randomness;
3. when codebooks are selected repeatedly, switching costs couple present
   decisions to past actions.

This note keeps two decision problems separate.

### Terminal decision

A hidden source-law scenario is fixed. The designer observes `T`
conditionally independent public signals and then chooses one zero-error prefix
codebook.

### Sequential decision

After signal `Y_t`, the designer chooses the period-`t` codebook as a function
of the complete signal prefix

\[
Y_{1:t}=(Y_1,\ldots,Y_t).
\]

The hidden scenario remains fixed. A rational switching charge is paid whenever
adjacent selected codebooks differ.

The terminal problem studies the value of accumulated evidence for one action.
The sequential problem studies a policy tree with intertemporal action costs.
They coincide only at horizon one.

All scenario laws, observation probabilities, code lengths, switching charges,
and finite-game values are exact rational numbers. Enumeration is bounded by
explicit caps.

---

## 1. Exact product observation channel

Let the hidden source-law scenario be

\[
R\in\{1,\ldots,s\}.
\]

One public signal takes values in

\[
\mathcal Y=\{0,\ldots,m-1\}
\]

with rational channel

\[
O_{r,y}=P(Y=y\mid R=r).
\]

Assume repeated signals are conditionally independent given `R`. For history

\[
h=(y_1,\ldots,y_T)\in\mathcal Y^T,
\]

the product channel is

\[
\boxed{
O^{\otimes T}_{r,h}
=
\prod_{t=1}^{T}O_{r,y_t}.
}
\]

The number of terminal histories is

\[
\boxed{m^T.}
\]

The implementation enumerates every history lexicographically, multiplies the
rational channel entries exactly, and verifies that each scenario row sums to
one.

This conditional-i.i.d. assumption is substantive. Correlated measurement
noise, a drifting hidden scenario, adaptive measurement choice, or stateful
sensors require different product laws.

---

## 2. Longer histories Blackwell-dominate their prefixes

Take `T>=K>=1`. The complete `T`-signal history can be deterministically
projected to its first `K` signals:

\[
\pi_K(y_1,\ldots,y_T)
=(y_1,\ldots,y_K).
\]

Let `G` be the row-stochastic matrix implementing this deterministic map. Then

\[
\boxed{
O^{\otimes K}
=
O^{\otimes T}G.
}
\]

Thus the longer history Blackwell-dominates the shorter one. A designer who
observes all `T` signals can discard the suffix and imitate any shorter-history
policy.

For the shared-randomness minimax terminal value,

\[
\boxed{
V_T^{\rm terminal}
\le
V_K^{\rm terminal}.
}
\]

The same inequality also holds for deterministic policies because the garbling
is deterministic: compose the shorter deterministic decision rule with the
prefix projection.

The inequality need not be strict. More data can be decision-theoretically
redundant at finite sample sizes.

---

## 3. Symmetric binary evidence has an exact sufficient statistic

Consider two hidden scenarios and a binary symmetric observation channel with
accuracy `a`:

\[
P(Y=0\mid R=0)=P(Y=1\mid R=1)=a,
\]

\[
P(Y=1\mid R=0)=P(Y=0\mid R=1)=1-a.
\]

For a binary history `h`, let

\[
n_0(h)=\#\{t:y_t=0\},
\qquad
n_1(h)=\#\{t:y_t=1\}.
\]

The likelihood ratio is

\[
\frac{P(h\mid R=0)}{P(h\mid R=1)}
=
\left(
\frac{a}{1-a}
\right)^{n_0(h)-n_1(h)}.
\]

Therefore the signed count

\[
\boxed{S(h)=n_0(h)-n_1(h)}
\]

is sufficient for the terminal scenario decision. The order of equal signal
counts contains no additional terminal information in this symmetric model.

The repository still enumerates complete histories as an independent finite
checker. Compressing to the sufficient statistic is a future scaling
optimization, not an assumption used to obtain the exact small-instance
values.

---

## 4. Exact majority accuracy with public fair ties

For `a>=1/2`, majority vote is the symmetric likelihood rule. Let

\[
B_T(a)
\]

be its correct-decision probability when an even-sample tie is resolved by a
fair public random bit. Then

\[
\boxed{
B_T(a)
=
\sum_{k>T/2}
\binom Tk a^k(1-a)^{T-k}
+
\frac12\mathbf1\{T\text{ even}\}
\binom T{T/2}
[a(1-a)]^{T/2}.
}
\]

### Even-sample plateau

For every `m>=1`,

\[
\boxed{
B_{2m}(a)=B_{2m-1}(a).
}
\]

To see this, condition on the number `X` of correct signals among the first
`2m-1` observations. Only two boundary cases differ.

- At `X=m`, the odd rule is correct. The even rule loses half credit when the
  last signal is wrong, producing decrement

  \[
  \frac12(1-a)P(X=m).
  \]

- At `X=m-1`, the odd rule is wrong. A correct last signal creates a tie and
  half credit, producing increment

  \[
  \frac12aP(X=m-1).
  \]

The two central binomial coefficients are equal, so

\[
(1-a)P(X=m)=aP(X=m-1).
\]

The increment and decrement cancel exactly.

This is an important nuance: an additional observation can be Blackwell-more
informative while leaving the value of a particular symmetric minimax decision
problem unchanged.

---

## 5. Terminal coding value for two symmetric scenarios

Suppose the relevant code universe contains two scenario-specialized
codebooks. The aligned code has scenario cost `L_low`, while the misaligned code
has cost `L_high>=L_low`.

After `T` symmetric signals, majority selection with fair public ties has cost

\[
\boxed{
C_T
=
B_T(a)L_{\rm low}
+
[1-B_T(a)]L_{\rm high}.
}
\]

### Exact `K3` instance

Use the complete three-state confusion graph and two source-law scenarios

\[
p^{(0)}=(4/5,1/10,1/10),
\]

\[
p^{(1)}=(1/10,4/5,1/10).
\]

The useful nondominated codebooks assign the depth-one leaf to state zero or
state one. Their aligned and misaligned costs are

\[
L_{\rm low}=6/5,
\qquad
L_{\rm high}=19/10.
\]

Let the binary observation accuracy be

\[
a=3/4.
\]

Then

\[
B_1=B_2=3/4,
\]

and

\[
B_3=B_4=27/32.
\]

Therefore

\[
\boxed{
C_1=C_2
=
\frac34\left(\frac65\right)
+
\frac14\left(\frac{19}{10}\right)
=
\frac{11}{8}.
}
\]

For three or four observations,

\[
\boxed{
C_3=C_4
=
\frac{27}{32}\left(\frac65\right)
+
\frac5{32}\left(\frac{19}{10}\right)
=
\frac{419}{320}.
}
\]

The shared-randomness no-observation baseline is

\[
\frac12\left(\frac65+\frac{19}{10}\right)
=
\frac{31}{20}.
\]

Thus one observation is worth

\[
\frac{31}{20}-rac{11}{8}
=
\boxed{rac7{40}},
\]

while three observations are worth

\[
\frac{31}{20}-rac{419}{320}
=
\boxed{rac{77}{320}}.
\]

The third signal adds value; the second and fourth do not in this symmetric
terminal problem.

The exact policy enumerator independently reproduces the one-, two-, and
three-signal values without assuming a majority rule.

---

## 6. Sequential signal-history policy tree

For horizon `T`, the action at period `t` is a deterministic function of the
nonempty signal prefix

\[
h_t=(Y_1,\ldots,Y_t).
\]

The policy-tree node set is

\[
\mathcal H_T
=
\bigcup_{t=1}^{T}\mathcal Y^t.
\]

For `m>1`, its size is

\[
\boxed{
N_T
=
\sum_{t=1}^{T}m^t
=
\frac{m(m^T-1)}{m-1}.
}
\]

With `C` candidate codebooks, the raw deterministic policy count is

\[
\boxed{C^{N_T}.}
\]

This exponential count is why the implementation is explicitly bounded. It
fails instead of silently sampling or truncating policies.

For a complete history `h=(y_1,...,y_T)`, a deterministic policy selects
codebooks

\[
c_t=\delta(h_t).
\]

Its path cost under source scenario `r` is

\[
\sum_{t=1}^{T}L_{r,c_t}
+
\kappa
\sum_{t=2}^{T}
\mathbf1\{c_t\ne c_{t-1}\}.
\]

The exact scenario cost averages this quantity over the product observation
law:

\[
\boxed{
A_{r,\delta}
=
\sum_{h\in\mathcal Y^T}
P(h\mid r)
\left[
\sum_tL_{r,\delta(h_t)}
+
\kappa\sum_{t=2}^{T}
\mathbf1\{\delta(h_t)\ne\delta(h_{t-1})\}
\right].
}
\]

The solver deduplicates equal scenario-cost vectors, removes componentwise
inferior policies, and solves an exact shared-public-randomness minimax game
over the remaining complete policy trees.

---

## 7. Sequential benchmark hierarchy

The sequential certificate reports:

- deterministic no-observation code-sequence value;
- shared-randomness no-observation code-sequence value;
- deterministic observation-policy value;
- shared-randomness observation-policy value;
- perfect-scenario-information value.

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

A signal policy may ignore every signal and imitate any no-observation sequence.
A shared mixture may imitate a deterministic policy. Perfect scenario knowledge
can simulate the observation channel and policy.

As before, deterministic observation and shared no-observation are different
resources and are not assigned a universal ordering.

---

## 8. Exact three-period sequential `K3` values

Use the two heavy-state `K3` scenarios and binary accuracy `3/4` above.

### Zero switching cost

With

\[
\kappa=0,
\qquad T=3,
\]

the exact values are

\[
\boxed{
V_{\rm no,det}=5,
}
\]

\[
\boxed{
V_{\rm no,shared}=rac{93}{20},
}
\]

\[
\boxed{
V_{\rm obs,det}
=
V_{\rm obs,shared}
=
rac{1299}{320},
}
\]

and

\[
\boxed{
V_{\rm perfect}=rac{18}{5}.
}
\]

The observed value decomposes into the terminal-prefix values for this symmetric
instance:

\[
\frac{11}{8}
+
\frac{11}{8}
+
rac{419}{320}
=
oxed{rac{1299}{320}}.
\]

The information value over the shared-randomness no-observation baseline is

\[
oxed{
rac{93}{20}-rac{1299}{320}
=
rac{189}{320}.
}

This additive decomposition is an exact property of the declared symmetric,
zero-switch instance. It is not asserted for every minimax scenario family.

### Switching cost `1/10`

Now set

\[
\kappa=1/10.
\]

The selected exact observation policy has expected switch count

\[
oxed{rac3{16}}
\]

under each source scenario. The source-cost component remains `1299/320`, so

\[
\boxed{
V_{\rm obs,det}
=
V_{\rm obs,shared}
=
rac{1299}{320}
+
rac1{10}rac3{16}
=
rac{261}{64}.
}

The shared no-observation value remains

\[
rac{93}{20},
\]

because its optimal symmetric mixture uses constant codebook sequences and pays
no switch charge.

The incremental information value is

\[
oxed{
rac{93}{20}-rac{261}{64}
=
rac{183}{320}.
}

Switching cost reduces the value of reacting to noisy evidence, but does not
eliminate it in this instance.

---

## 9. Terminal repetition and sequential observation are not interchangeable

In the terminal problem, all `T` signals arrive before one action. In the
sequential problem, prefix `Y_{1:t}` can alter period `t`, and earlier actions
may incur switching consequences.

At horizon one, the models agree exactly.

For longer horizons:

- terminal value concerns one final codebook;
- sequential value sums several source-coding costs;
- sequential switching costs make the previously installed codebook part of the
  sufficient decision state;
- a signal arriving at period `T` cannot improve earlier code choices.

Thus “number of observations” is not enough to characterize value. Their timing
relative to actions matters.

---

## 10. Abstract interpretation: evidence state versus action state

Repeated observation introduces two different state-compression problems.

### Evidence state

For a fixed hidden scenario, the complete signal history may admit a sufficient
statistic—such as signed count in the binary symmetric model—that preserves all
future likelihood ratios.

### Action state

With switching costs, the current installed codebook must also be retained.
Even two signal histories with the same posterior evidence can require different
future actions if they end in different installed codebooks.

A dynamic sufficient state therefore has the schematic form

\[
\boxed{
(
\text{compressed evidence},
\text{installed action},
\text{remaining horizon}
).
}
\]

This is closely analogous to predictive-state reasoning elsewhere in the
repository: histories may be merged only when they induce the same future
conditional decision problem.

For a hypothetical renderer, the analogous lesson is that preserving a posterior
about hidden state may still be insufficient when prior commitments affect
future costs. This is a general control and information principle, not evidence
of simulation.

---

## Nonclaims

- The hidden source-law scenario is fixed throughout the repeated-observation
  model.
- Signals are conditionally independent and generated by one known channel.
- Every signal and selected codebook is public to all decoders.
- Policy trees are deterministic; a separate public seed may mix complete
  trees.
- The policy observes signals, not the hidden scenario or true source law.
- The finite policy enumeration is not a scalable large-horizon algorithm.
- Even-sample plateaus are proved for the symmetric binary fair-tie decision,
  not arbitrary channels or losses.
- More observations Blackwell-dominate fewer, but their value can be equal for
  a specific loss.
- Internal source-code length and switching cost are not parent-universe memory,
  energy, or computation.
- None of these repeated-observation results is evidence that reality is
  simulated.

---

## Next research targets

1. Compress policy trees by exact likelihood-ratio sufficient statistics.
2. Replace a fixed hidden scenario with bounded source-law drift.
3. Solve robust belief-state policies under noisy observations and switching
   costs.
4. Price each observation and derive optimal stopping or resampling rules.
5. Add optional stopping with anytime-valid inference rather than fixed sample
   counts.
6. Compare public observations with private encoder-only signals.
7. Allow adaptive measurement-channel choice and information acquisition cost.
8. Derive upper and lower certificates for larger horizons without full policy
   enumeration.
9. Study when finite predictive evidence states exist and how many are required.
