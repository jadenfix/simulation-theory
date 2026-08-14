# Approximate hidden-law quotients and finite-horizon value loss

## Scope

Exact probabilistic bisimulation requires exact equality of source laws,
observation rows, and class-transition probabilities.  That is appropriate for
formal models, but empirical models usually differ by small amounts rather than
exactly zero.

This note compares:

- one detailed hidden-law model \(P\) with hidden state \(S_t\);
- one abstract hidden-law model \(Q\) with hidden state \(Z_t\);
- a declared map

  \[
  \phi:\mathcal S\to\mathcal Z
  \]

  from detailed states to abstract states.

The objective is not to infer an optimal abstraction.  It is to certify a
finite-horizon upper bound on how much a *declared* abstraction can change:

- no-signal Bayesian coding value;
- noisy-observation Bayesian coding value;
- expected clairvoyant code-sequence value;
- the corresponding Bayes regrets.

The theorem is a sequential coupling bound.  It is conservative by design and
uses only exact rational deviations after the two finite models and the state
map are declared.

---

## 1. Exact deviations

Let the partition blocks be

\[
B_z=\{s:\phi(s)=z\}.
\]

### Initial abstract-state deviation

Aggregate the detailed initial law:

\[
\tilde\mu_z
=
\sum_{s\in B_z}\mu_s^P.
\]

Define

\[
\boxed{
\epsilon_0
=
\operatorname{TV}(\tilde\mu,\mu^Q).
}
\]

### Source-law deviation

State \(s\) selects categorical source law \(p_s^P\), while abstract state
\(z=\phi(s)\) selects \(p_z^Q\).  Define

\[
\boxed{
\epsilon_{\rm src}
=
\max_s
\operatorname{TV}(p_s^P,p_{\phi(s)}^Q).
}
\]

The coding theorem uses the tighter induced stage-cost deviation.  For every
allowed deterministic zero-error codebook \(a\), let \(\ell_a(x)\) be the
codeword length of source symbol \(x\).  Define

\[
\boxed{
\epsilon_c
=
\max_{s,a}
\left|
E_{p_s^P}[\ell_a]
-
E_{p_{\phi(s)}^Q}[\ell_a]
\right|.
}
\]

If

\[
\operatorname{span}(\ell_a)
=
\max_x\ell_a(x)-\min_x\ell_a(x),
\]

then the finite-alphabet total-variation expectation inequality gives

\[
\left|
E_p[\ell_a]-E_q[\ell_a]
\right|
\le
\operatorname{TV}(p,q)
\operatorname{span}(\ell_a).
\]

Hence

\[
\boxed{
\epsilon_c
\le
\epsilon_{\rm src}
\max_a\operatorname{span}(\ell_a).
}
\]

The repository computes \(\epsilon_c\) directly over the complete bounded
componentwise-undominated codebook universe and independently checks this range
bound.

### Observation deviation

The two models use one common signal alphabet.  Define

\[
\boxed{
\epsilon_o
=
\max_s
\operatorname{TV}
\left(
O_s^P,
O_{\phi(s)}^Q
\right).
}
\]

### Abstract transition deviation

Aggregate the detailed next-state law into abstract blocks:

\[
\tilde K_s(z')
=
\sum_{u:\phi(u)=z'}K^P_{su}.
\]

Define

\[
\boxed{
\epsilon_K
=
\max_s
\operatorname{TV}
\left(
\tilde K_s,
K^Q_{\phi(s)}
\right).
}
\]

All five quantities are exact rational numbers.

---

## 2. Sequential maximal coupling

Couple the initial abstract states so that

\[
P\{\phi(S_1)\ne Z_1\}=\epsilon_0.
\]

Suppose the abstract states are currently matched:

\[
\phi(S_t)=Z_t=z.
\]

Conditional on the detailed state \(S_t=s\in B_z\), maximal coupling of the
observation rows gives

\[
P\{Y_t^P\ne Y_t^Q\mid\text{matched so far}\}
\le
\epsilon_o.
\]

After the stage, maximal coupling of the abstract next-state laws gives

\[
P\{\phi(S_{t+1})\ne Z_{t+1}\mid\text{matched so far}\}
\le
\epsilon_K.
\]

Multiplying the conditional survival probabilities yields

\[
\boxed{
P\{\text{no observed-history divergence through }T\}
\ge
(1-\epsilon_0)
(1-\epsilon_o)^T
(1-\epsilon_K)^{T-1}.
}
\]

Therefore the observed-policy divergence probability is bounded by

\[
\boxed{
\delta_{\rm obs}
=
1-
(1-\epsilon_0)
(1-\epsilon_o)^T
(1-\epsilon_K)^{T-1}.
}
\]

For a no-signal policy, observations do not influence decisions and need not be
coupled.  The relevant bound is

\[
\boxed{
\delta_{\rm none}
=
1-
(1-\epsilon_0)
(1-\epsilon_K)^{T-1}.
}
\]

The same transition-only bound applies to the path-specific clairvoyant
code-sequence oracle, whose cost does not depend on observation signals.

The product expression is usually sharper than the union bound

\[
\epsilon_0+T\epsilon_o+(T-1)\epsilon_K,
\]

although both are valid after clipping at one.

---

## 3. Uniform policy-cost bound

Let

\[
L_{\max}
=
\max_{a,x}\ell_a(x)
\]

and let \(\kappa\ge0\) be the switching charge.  Every finite-horizon code
sequence has total cost at most

\[
\boxed{
M_T
=
T L_{\max}+(T-1)\kappa.
}
\]

Consider one common deterministic signal-history policy \(\pi\) used in both
models.

On the event that initial abstract state, all signals, and all abstract
transitions remain coupled:

- the policy sees the same signal history;
- it selects the same codebooks;
- switching events are identical;
- each stage expected code length differs by at most \(\epsilon_c\).

Thus the pathwise cost difference on that event is at most

\[
T\epsilon_c.
\]

On the divergence event, both cumulative costs lie in \([0,M_T]\), so their
absolute difference is at most \(M_T\).  Taking expectations gives

\[
\boxed{
\left|
E_P C_\pi-E_Q C_\pi
\right|
\le
T\epsilon_c+M_T\delta_{\rm obs}.
}
\]

For no-signal policies, replace \(\delta_{\rm obs}\) by
\(\delta_{\rm none}\).

The bound remains valid for randomized policies whose exogenous random seed is
coupled identically in both models.

---

## 4. Transfer to optimal values

Let \(\Pi\) be one common policy class, and suppose every \(\pi\in\Pi\)
satisfies

\[
|C_P(\pi)-C_Q(\pi)|\le B.
\]

Let \(\pi_Q^*\) be optimal in model \(Q\).  Then

\[
V_P
\le
C_P(\pi_Q^*)
\le
C_Q(\pi_Q^*)+B
=
V_Q+B.
\]

Reversing the roles of the models gives

\[
V_Q\le V_P+B.
\]

Therefore

\[
\boxed{|V_P-V_Q|\le B.}
\]

Applying this argument gives

\[
\boxed{
|V_{\rm none}^P-V_{\rm none}^Q|
\le
B_{\rm none}
=
T\epsilon_c+M_T\delta_{\rm none},
}
\]

and

\[
\boxed{
|V_{\rm obs}^P-V_{\rm obs}^Q|
\le
B_{\rm obs}
=
T\epsilon_c+M_T\delta_{\rm obs}.
}
\]

The implementation's model-specific solvers may safely prune codebooks that are
componentwise dominated under all source laws in that model.  The proof itself
uses the common complete bounded codebook universe; safe pruning cannot change
the optimum.

---

## 5. Clairvoyant path-oracle bound

Fix one matched abstract-state path.  Every code sequence has identical switch
cost in both models and stage-cost difference at most \(T\epsilon_c\).
Therefore the minima over the common sequence class satisfy

\[
|O_P-O_Q|
\le
T\epsilon_c
\]

on the no-divergence event.

Using the transition-only coupling gives

\[
\boxed{
\left|
E_P O_P-E_Q O_Q
\right|
\le
B_{\rm oracle}
=
T\epsilon_c+M_T\delta_{\rm none}.
}
\]

This is the same numerical expression as the no-signal value bound, although the
operational objects are different.

---

## 6. Bayes-regret bounds

For information pattern \(i\), Bayes regret is

\[
R_i=V_i-E[O].
\]

Hence

\[
\begin{aligned}
|R_i^P-R_i^Q|
&=
\left|
(V_i^P-V_i^Q)
-
(E_PO_P-E_QO_Q)
\right|\\
&\le
|V_i^P-V_i^Q|
+
|E_PO_P-E_QO_Q|.
\end{aligned}
\]

Therefore

\[
\boxed{
|R_{\rm none}^P-R_{\rm none}^Q|
\le
B_{\rm none}+B_{\rm oracle},
}
\]

and

\[
\boxed{
|R_{\rm obs}^P-R_{\rm obs}^Q|
\le
B_{\rm obs}+B_{\rm oracle}.
}
\]

These are triangle-inequality bounds.  Cancellation may make the actual regret
difference much smaller.

---

## 7. Exact-bisimulation limit

If the declared abstraction is the exact bisimulation quotient, then

\[
\epsilon_0
=
\epsilon_c
=
\epsilon_o
=
\epsilon_K
=0.
\]

Consequently

\[
\delta_{\rm none}
=
\delta_{\rm obs}
=0
\]

and every bound collapses to zero.  The approximate theorem therefore recovers
the exact quotient-preservation theorem as a boundary case:

\[
\boxed{
\text{exact bisimulation}
\implies
\text{zero certified value loss}.
}
\]

The repository tests this limit by constructing the exact quotient and solving
both models independently.

---

## 8. Representative abstraction

For a declared partition, one deterministic abstraction selects the first state
in each block as representative:

- representative source law;
- representative observation row;
- representative transition mass into each block.

Initial belief is aggregated exactly.  The representative choice is not claimed
to minimize the bound.  It merely produces a reproducible abstraction whose
errors are then measured.

More sophisticated choices could optimize:

- maximum source-law TV;
- maximum observation TV;
- maximum transition TV;
- the induced stage-cost deviation;
- the final finite-horizon value bound.

Those objectives need not choose the same representative or even a model equal
to one original state's parameters.

---

## 9. What perfect-state observation changes

The noisy-observation theorem transfers one common policy class: both models
receive signals from the same signal alphabet.  A detailed perfect-state policy
can condition on internal state identities that do not exist in the abstract
model.

Under exact bisimulation, that extra identity has zero value and perfect-state
values are preserved.  Under approximate aggregation, internal identity may
carry small but nonzero information about current costs or future transitions.
The present coupling theorem therefore does **not** state a general bound on
perfect-detailed-state value.

A valid extension would need one of:

- a class-only perfect-information policy restriction;
- an explicit bound on the value of internal-state information;
- an approximate controlled-bisimulation metric.

Leaving this case out is part of the theorem's scope, not a missing numerical
check.

---

## 10. Relevance to predictive simulation arguments

Exact state counting can overstate predictive burden when several states are
behaviorally identical.  Approximate state counting can make the opposite
mistake if nearly equal states are merged without quantifying the induced error.

The current result inserts a controlled middle layer:

\[
\boxed{
\text{declared abstraction}
+
\text{measured local deviations}
+
\text{finite-horizon coupling}
\Longrightarrow
\text{explicit value-loss bound}.
}

It does not establish that the abstraction is computationally optimal or that a
hypothetical simulator uses hidden Markov states.  It shows how one can make a
bounded predictive-compression claim without turning visual similarity or small
parameter differences into an unquantified equivalence assertion.

---

## Nonclaims

- The coupling bound is sufficient and may be loose.
- Source, signal, and transition deviations are worst-case local quantities.
- Hidden transitions and observation channels are action independent.
- Both models use the same source-symbol and signal alphabets.
- The value theorem covers no-signal and noisy-signal policy classes, not
  unrestricted perfect detailed-state policies.
- The representative abstraction is deterministic, not optimal.
- The horizon is finite and switching cost is a declared nonnegative input.
- Bounded exact codebook/path enumeration is not a scalability theorem.
- Approximate-state count is not parent-universe hardware or memory.
- A small certified value loss is not evidence that reality is simulated.

---

## Next research targets

1. Optimize abstract source, observation, and transition parameters instead of
   selecting representatives.
2. Replace the global worst-case coupling by state- and time-dependent error
   recursions.
3. Bound the value of detailed perfect-state information inside one approximate
   block.
4. Develop controlled bisimulation metrics for action-dependent models.
5. Derive discounted and average-cost approximate quotient bounds.
6. Combine statistical confidence regions with approximate abstraction error.
7. Learn a quotient under finite data while preserving coverage.
8. Prove lower bounds showing when no smaller abstraction can meet a target
   value tolerance.
