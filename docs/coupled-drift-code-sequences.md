# Coupled source-law drift and precommitted code sequences

## Scope

A static ambiguity set and a source law that changes over time are different
objects. The preceding static-drift result treated one fixed cost vector
throughout the horizon. In that special case, the adversary can move
probability mass monotonically from low-cost to high-cost states, so the
single-period TV-ball extrema can be nested into one feasible path.

This note removes the fixed-cost assumption.

Let

\[
q_0=p,\qquad
\operatorname{TV}(q_t,q_{t-1})\le\eta,
\quad t=1,\ldots,T,
\]

and let period \(t\) have a declared finite state-cost vector \(g_t\). The exact
adversarial problem is

\[
\boxed{
V(g_{1:T})
=
\max_{q_{1:T}}
\sum_{t=1}^{T}q_t^\top g_t
}
\]

subject to the path constraints above.

The code also chooses a complete sequence of deterministic zero-error prefix
codebooks before the source path is selected. A rational penalty may be charged
for each adjacent codebook change.

The source path observes the whole precommitted sequence. No feedback-adaptive
code selection is claimed in this lane.

---

## 1. Exact rational path polytope

For finite probability laws,

\[
\operatorname{TV}(u,v)
=
\max_{S\subseteq[n]}|u(S)-v(S)|.
\]

Therefore

\[
\operatorname{TV}(q_t,q_{t-1})\le\eta
\]

is equivalent to

\[
-\eta
\le
q_t(S)-q_{t-1}(S)
\le
\eta
\qquad
\forall S\subseteq[n].
\]

An event and its complement generate the same absolute constraint, so one
representative from each nontrivial complement pair suffices.

Eliminate the final probability coordinate in every period:

\[
q_{t,n}
=
1-\sum_{i=1}^{n-1}q_{t,i}.
\]

The free path vector has dimension

\[
\boxed{d=T(n-1)}.
\]

Every simplex inequality and every TV event inequality becomes an exact rational
halfspace

\[
Ax\le b.
\]

The implementation exhausts every \(d\)-row active basis below an explicit cap,
solves the corresponding rational linear system, checks every omitted
inequality, reconstructs the complete probability path, and deduplicates equal
vertices.

For a linear objective, the optimum occurs at one of these vertices. This is a
bounded exact checker, not a polynomial-time claim for large alphabets or
horizons.

---

## 2. Exact primal-dual certificate

After the same simplex elimination, write

\[
\sum_tq_t^\top g_t
=
c_0+c^\top x.
\]

The primal is

\[
\max_x c_0+c^\top x
\quad\text{subject to }Ax\le b.
\]

Its LP dual is

\[
\min_{y\ge0}c_0+b^\top y
\quad\text{subject to }A^\top y=c.
\]

The repository enumerates bounded dual supports in exact rational arithmetic and
returns multipliers satisfying

\[
\boxed{
A^\top y=c,\qquad
y\ge0,\qquad
c_0+b^\top y=V(g_{1:T}).
}
\]

The maximizing path and the dual multiplier are independent upper and lower
proof objects. Their exact equality establishes optimality.

A basic dual certificate needs support on at most

\[
\boxed{T(n-1)}
\]

path inequalities.

---

## 3. Marginal-ball optimization is only a relaxation

Triangle inequality gives

\[
\operatorname{TV}(q_t,p)\le\min(t\eta,1).
\]

Consequently,

\[
V(g_{1:T})
\le
\sum_{t=1}^{T}
\max_{\operatorname{TV}(q,p)\le\min(t\eta,1)}
q^\top g_t.
\]

The right-hand side allows the adversary to select an unrelated law for every
period. It is therefore a relaxation, not generally an equality.

### Strict two-state example

Let

\[
p=(1/2,1/2),
\qquad
\eta=1/4,
\]

with

\[
g_1=(0,1),
\qquad
g_2=(1,0).
\]

The independent marginal values are

\[
\max_{\operatorname{TV}(q,p)\le1/4}q^\top g_1
=
3/4,
\]

and

\[
\max_{\operatorname{TV}(q,p)\le1/2}q^\top g_2
=
1.
\]

Thus the relaxed value is

\[
V_{\rm marginal}=\frac74.
\]

Write \(x_t=q_t(2)\). The exact path objective is

\[
x_1+(1-x_2)=1+x_1-x_2.
\]

The step constraint gives

\[
|x_2-x_1|\le1/4,
\]

so

\[
1+x_1-x_2\le\frac54.
\]

Equality is feasible, hence

\[
\boxed{V_{\rm coupled}=\frac54}
\]

and

\[
\boxed{
V_{\rm marginal}-V_{\rm coupled}
=
\frac12.
}
\]

The periodwise adversaries point in opposite directions and cannot both be
realized by one bounded-drift path.

---

## 4. Why the fixed-cost theorem remains valid

If

\[
g_1=\cdots=g_T=g,
\]

the same donor-to-recipient TV transport can be continued monotonically as the
radius grows. The radius-\(t\eta\) maximizers are nested, and consecutive
members move at most \(\eta\) mass.

Therefore the special fixed-cost identity remains

\[
\boxed{
V(g,\ldots,g)
=
\sum_{t=1}^{T}
\max_{\operatorname{TV}(q,p)\le\min(t\eta,1)}
q^\top g.
}
\]

The new coupled solver independently recovers this equality. The earlier
theorem was not wrong; its fixed-objective assumption was essential.

At the other endpoints:

- \(\eta=0\) forces every \(q_t=p\);
- \(\eta=1\) permits every period law to be selected independently, so the
  marginal relaxation is exact again.

---

## 5. Precommitted codebook sequences

Let \(\mathcal C\) be the complete bounded deterministic zero-error prefix-code
universe after safe componentwise dominance pruning. Codebook \(c\) has state
length vector

\[
\ell_c=(\ell_{c,1},\ldots,\ell_{c,n}).
\]

A precommitted sequence is

\[
(c_1,\ldots,c_T)\in\mathcal C^T.
\]

The source-law adversary sees this complete sequence and solves

\[
\max_{q_{1:T}}
\sum_tq_t^\top\ell_{c_t}.
\]

If every codebook transition costs \(\kappa\ge0\), the designer minimizes

\[
\boxed{
\max_{q_{1:T}}
\sum_tq_t^\top\ell_{c_t}
+
\kappa
\sum_{t=2}^{T}\mathbf1\{c_t\ne c_{t-1}\}.
}
\]

The switch term is fixed once the open-loop sequence is selected; it does not
alter the path LP.

The implementation enumerates every bounded sequence, evaluates its objective
over the exact common path-polytope vertices, and reconstructs the full
primal-dual certificate for the selected sequence.

Componentwise code dominance remains safe. If one code has no longer codeword
for every source state, replacing a dominated code by it weakly lowers source
cost and cannot require more switches when used consistently.

---

## 6. Exact rotating-code gain on \(K_3\)

For a complete three-state confusion graph, each zero-error code needs three
distinct messages. The nondominated binary prefix length vectors are the
permutations of

\[
(1,2,2).
\]

Start from

\[
p=(1/3,1/3,1/3),
\qquad
\eta=1/6,
\qquad
T=2.
\]

### Best static sequence

Repeat the code whose short word belongs to state one:

\[
\ell_1=\ell_2=(1,2,2).
\]

The adversary lowers the probability of the short state from \(1/3\) to \(1/6\)
in the first period and then to zero. The total is

\[
\left(2-\frac16\right)+2
=
\boxed{\frac{23}{6}}.
\]

Every static permutation has the same value.

### Rotating the short word

Use

\[
\ell_1=(1,2,2),
\qquad
\ell_2=(2,1,2).
\]

The exact coupled adversary must minimize

\[
q_{1,1}+q_{2,2}.
\]

It can reduce both terms to \(1/6\), but cannot drive both to zero within the
step budget. Therefore

\[
V_{\rm rotating}
=
4-\frac16-\frac16
=
\boxed{\frac{11}{3}}.
\]

The precommitted time-varying code improves on every static code by

\[
\boxed{
\frac{23}{6}-\frac{11}{3}
=
\frac16.
}
\]

This is not learning or feedback. It is open-loop temporal diversification:
the cost vector rotates faster than the source law can move to exploit every
short-word location.

---

## 7. Exact switching-cost phase transition

The rotating sequence uses one switch. Its penalized cost is

\[
\frac{11}{3}+\kappa.
\]

The best static cost is

\[
\frac{23}{6}.
\]

Thus switching is strictly beneficial exactly when

\[
\frac{11}{3}+\kappa
<
\frac{23}{6},
\]

or

\[
\boxed{\kappa<\frac16.}
\]

At

\[
\boxed{\kappa_c=\frac16}
\]

the two strategies tie. The implementation's deterministic tie-break chooses
the sequence with fewer switches. Above the threshold, the static code is
optimal.

This is a genuine reconfiguration phase boundary: robustness can justify
planned code changes, but only when the gain exceeds the declared switching
cost.

---

## 8. Abstract interpretation

The coupled problem adds a temporal geometry that a static ambiguity set cannot
capture.

A static robust model asks:

\[
\text{Which laws are possible?}
\]

A path robust model asks:

\[
\text{Which sequences of laws are jointly reachable?}
\]

The second question is strictly richer. Two periodwise-plausible laws may be
mutually incompatible because the path cannot move between them quickly enough.

For a hypothetical on-demand renderer, this suggests a broader principle:

> It is not enough to bound each future state independently. One must preserve
> the transition geometry linking future states across time.

This principle is not evidence for simulation. It applies equally to ordinary
nonstationary compression, caching, prediction, and control systems.

---

## Nonclaims

- The source sequence is adversarial only within the declared TV step budget.
- The entire codebook schedule is chosen before the source path and is visible
  to the adversary.
- No codebook is selected after observing the current or previous source law.
- No realized source symbols are used for learning or adaptation.
- The switching penalty is an external rational design parameter; it is not
  inferred from physics.
- Active-basis and code-sequence enumeration are bounded exact methods, not
  large-scale complexity guarantees.
- A periodwise marginal TV ball is an upper relaxation, not a confidence set
  unless separately calibrated.
- Internal expected code length is not parent-universe memory, energy, or
  computation.
- None of these coding or drift identities is generic evidence for simulation.

---

## Next research targets

1. Separate open-loop schedules from policies that observe delayed source-law
   information.
2. Derive the value ordering among no-feedback, delayed-feedback,
   current-law, and clairvoyant information patterns.
3. Add exact dynamic programming on finite rational prior grids.
4. Extend the continuous path LP to code-dependent transition or switching
   costs.
5. Price shared codebook randomness and compare random schedules with
   deterministic temporal diversification.
6. Study path regret relative to a clairvoyant time-varying code oracle.
7. Replace one global TV step budget with state-dependent or polyhedral
   transition sets.
8. Connect temporal predictive-state geometry to causal policies rather than
   static state representations.
