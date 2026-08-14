# Source-drift information patterns and the value of timing

## Scope

The coupled-drift solver answers an open-loop question:

> Which complete codebook sequence should be committed before the source-law
> path is chosen?

That is not the only meaningful timing model. A designer may learn the evolving
source law before or after some decisions, while nature may choose the next law
before or after seeing the current codebook.

This note separates four deterministic finite-horizon games on an exact rational
simplex grid:

1. **Open-loop:** the complete codebook sequence is chosen first; nature then
   chooses the complete admissible source-law path.
2. **Delayed feedback:** at period `t`, the designer knows `q_(t-1)` and the
   previous codebook, chooses the new codebook, and nature then chooses `q_t`.
3. **Current-law feedback:** nature chooses `q_t`; the designer observes that
   law before choosing the period-`t` codebook.
4. **Clairvoyant:** nature chooses the complete path first; the designer then
   chooses the complete codebook sequence with the entire path known.

The source-law state space is finite because the simplex is restricted to a
declared denominator grid. Every law, transition, Bellman value, switching cost,
and witness is exact rational.

The finite grid is a bounded checker and a discrete model in its own right. It
is not silently identified with the continuous simplex.

---

## 1. Exact rational simplex grid

Fix an alphabet of size `n` and an integer denominator `D`. The grid is

\[
\mathcal G_D
=
\left\{
q\in\Delta_{n-1}:
q_i=\frac{k_i}{D},\quad
k_i\in\mathbb Z_{\ge0},\quad
\sum_i k_i=D
\right\}.
\]

The number of grid laws is the stars-and-bars count

\[
\boxed{
|\mathcal G_D|
=
\binom{D+n-1}{n-1}.
}
\]

For `n=3`, `D=6`, this gives

\[
|\mathcal G_6|=\binom82=28.
\]

Connect two laws when

\[
\operatorname{TV}(q,q')\le\eta.
\]

Because total variation is symmetric, this produces an undirected transition
graph with a self-loop at every law. A length-`T` admissible path is a graph
walk

\[
q_0=p,
\qquad
q_t\in N(q_{t-1}),
\quad t=1,\ldots,T.
\]

The implementation constructs the complete pairwise transition relation and
fails rather than truncates when the declared pair cap is exceeded.

### Grid alignment

The initial law must lie exactly on the declared grid. It is not rounded to the
nearest point. Rounding would introduce an additional approximation model that
would need its own error bound.

---

## 2. Deterministic zero-error code universe

Let `C` be the complete bounded set of componentwise-undominated deterministic
zero-error binary prefix codebooks for the declared confusion graph.

Codebook `c` has a state-length vector

\[
\ell_c=(\ell_{c,1},\ldots,\ell_{c,n}).
\]

At source law `q`, its expected source-coding cost is

\[
L(q,c)=q^\top\ell_c.
\]

Changing from previous codebook `c^-` to `c` costs

\[
K(c^-,c)
=
\kappa\mathbf1\{c^-\ne c\},
\]

with no charge at the initial period because no earlier codebook exists.

The source law is assumed to know the declared information pattern and the
designer's strategy. The common zero-error codebook is known to every decoder.

---

## 3. Open-loop value

The designer commits to

\[
c_{1:T}=(c_1,\ldots,c_T)
\]

before nature chooses the path. The value is

\[
\boxed{
V_{\rm open}
=
\min_{c_{1:T}}
\max_{q_{1:T}\in\mathcal P(p,\eta)}
\left[
\sum_{t=1}^T q_t^\top\ell_{c_t}
+
\kappa\sum_{t=2}^T
\mathbf1\{c_t\ne c_{t-1}\}
\right].
}
\]

This is the finite-grid analogue of the continuous coupled path problem merged
in the preceding lane.

The checker exhausts all code sequences and all reachable law paths below
explicit caps and stores a worst path for every sequence.

---

## 4. Delayed-feedback Bellman equation

At the beginning of period `t`, the designer observes the previous source law
`q` and previous codebook `c^-`, but not the next law. It chooses `c`; nature
then chooses

\[
q'\in N(q).
\]

Let

\[
D_t(q,c^-)
\]

be the remaining worst-case cost from period `t`. The exact recursion is

\[
\boxed{
D_t(q,c^-)
=
\min_{c\in\mathcal C}
\left[
K(c^-,c)
+
\max_{q'\in N(q)}
\left\{
q'^\top\ell_c
+
D_{t+1}(q',c)
\right\}
\right].
}
\]

The terminal condition is

\[
D_T(q,c^-)=0
\]

when period indices start at zero after all `T` costs have been paid.

The value is

\[
\boxed{
V_{\rm delayed}=D_0(p,\varnothing).
}
\]

This policy can react to realized drift after a one-period delay. It cannot
choose the current codebook after seeing the current law.

---

## 5. Current-law-feedback Bellman equation

Now nature first chooses

\[
q'\in N(q).
\]

The designer observes `q'` and then chooses the period codebook. Let

\[
C_t(q,c^-)
\]

be the remaining value. The exact recursion is

\[
\boxed{
C_t(q,c^-)
=
\max_{q'\in N(q)}
\min_{c\in\mathcal C}
\left[
K(c^-,c)
+
q'^\top\ell_c
+
C_{t+1}(q',c)
\right].
}
\]

Thus

\[
\boxed{
V_{\rm current}=C_0(p,\varnothing).
}
\]

The only algebraic difference from delayed feedback is the order of `min` and
`max`. That order encodes a causal fact: who moves first in the period.

In general,

\[
\max_{q'}\min_c F(q',c)
\le
\min_c\max_{q'}F(q',c),
\]

which is the local source of the value-of-current-information improvement.

---

## 6. Clairvoyant value

For each complete admissible path, a clairvoyant designer chooses the best
complete code sequence after seeing every future law:

\[
\boxed{
V_{\rm clair}
=
\max_{q_{1:T}\in\mathcal P(p,\eta)}
\min_{c_{1:T}}
\left[
\sum_{t=1}^Tq_t^\top\ell_{c_t}
+
\kappa\sum_{t=2}^T
\mathbf1\{c_t\ne c_{t-1}\}
\right].
}
\]

This is a benchmark, not an implementable online policy unless the future path
is actually known.

---

## 7. Information-pattern value hierarchy

The four values obey

\[
\boxed{
V_{\rm clair}
\le
V_{\rm current}
\le
V_{\rm delayed}
\le
V_{\rm open}.
}
\]

### Clairvoyant versus current-law feedback

A clairvoyant can imitate any current-law policy because it knows every law that
the policy will observe, plus the future. Its feasible strategy set is weakly
larger. Therefore

\[
V_{\rm clair}\le V_{\rm current}.
\]

### Current-law versus delayed feedback

A current-law policy can ignore `q_t` and take the codebook that the delayed
policy would have selected from `q_(t-1)`. Therefore

\[
V_{\rm current}\le V_{\rm delayed}.
\]

### Delayed feedback versus open-loop

A delayed policy can ignore every observed previous law and execute any fixed
open-loop sequence. Therefore

\[
V_{\rm delayed}\le V_{\rm open}.
\]

These are set-inclusion arguments for the minimizing designer. They do not
require a numerical approximation.

---

## 8. Zero switching cost collapses current feedback to clairvoyance

Suppose

\[
\kappa=0.
\]

For a fixed source path, the code choices decouple across periods:

\[
\min_{c_{1:T}}
\sum_tq_t^\top\ell_{c_t}
=
\sum_t
\min_c q_t^\top\ell_c.
\]

A current-law policy observes each `q_t` before choosing `c_t`, so it can attain
the same periodwise minimum. Hence

\[
\boxed{
\kappa=0
\quad\Longrightarrow\quad
V_{\rm current}=V_{\rm clair}.
}
\]

Positive switching costs couple code choices through time. A clairvoyant may
accept a locally inferior codebook now to avoid a future switch, while a
current-law policy without future knowledge cannot always make the same trade.
The equality can therefore become strict when `kappa>0`.

---

## 9. Exact strict `K3` separation

Consider the complete three-state confusion graph. The nondominated binary
prefix length vectors are the permutations of

\[
(1,2,2).
\]

Use

\[
p=(1/3,1/3,1/3),
\qquad
D=6,
\qquad
\eta=1/6,
\qquad
T=2.
\]

The denominator-six grid contains 28 laws, and one drift step moves at most one
sixth of probability mass.

### No switching cost

At

\[
\kappa=0,
\]

the exact finite-grid values are

\[
\boxed{
V_{\rm clair}=V_{\rm current}=\frac{10}{3},
}
\]

\[
\boxed{
V_{\rm delayed}=\frac72,
\qquad
V_{\rm open}=\frac{11}{3}.
}
\]

The equal current/clairvoyant value is the zero-switch theorem above. Delayed
feedback and open-loop remain strictly worse because neither sees the current
law before assigning the short codeword.

### Switching cost `1/4`

At

\[
\kappa=1/4,
\]

the exact values become

\[
\boxed{
V_{\rm clair}=\frac{10}{3},
}
\]

\[
\boxed{
V_{\rm current}=\frac{41}{12},
}
\]

\[
\boxed{
V_{\rm delayed}=\frac{15}{4},
}
\]

\[
\boxed{
V_{\rm open}=\frac{23}{6}.
}
\]

All four inequalities are strict:

\[
\boxed{
\frac{10}{3}
<
\frac{41}{12}
<
\frac{15}{4}
<
\frac{23}{6}.
}
\]

The exact adjacent information values are

\[
V_{\rm current}-V_{\rm clair}
=
\frac1{12},
\]

\[
V_{\rm delayed}-V_{\rm current}
=
\frac13,
\]

\[
V_{\rm open}-V_{\rm delayed}
=
\frac1{12}.
\]

This gives a finite example in which:

- future information is valuable even after the current law is observed,
  because switching costs create intertemporal coupling;
- current-law observation is more valuable than merely observing the previous
  law;
- delayed feedback still improves on a fully precommitted schedule.

---

## 10. Zero drift removes the value of source-law information

If

\[
\eta=0,
\]

the only admissible path is

\[
q_1=\cdots=q_T=p.
\]

No uncertainty remains about the source law. Every information pattern therefore
has the same value:

\[
\boxed{
V_{\rm clair}
=
V_{\rm current}
=
V_{\rm delayed}
=
V_{\rm open}.
}
\]

For uniform `K3`, `T=2`, this common value is

\[
2\cdot\frac53
=
\boxed{\frac{10}{3}}.
\]

This check helps separate the value of information from unrelated differences
in the code universe.

---

## 11. Finite-grid versus continuous source adversaries

Every grid path is a valid path in the continuous simplex, but not every
continuous path lies on the grid. Therefore, for a fixed open-loop code
sequence,

\[
\max_{\text{grid paths}}\operatorname{cost}
\le
\max_{\text{continuous paths}}\operatorname{cost}.
\]

Taking the minimum over the same code sequences preserves the inequality:

\[
\boxed{
V_{\rm open}^{\rm grid}
\le
V_{\rm open}^{\rm continuous}.
}
\]

The grid result is thus a lower bound on the continuous adversarial value—not a
conservative upper bound.

For the uniform `K3`, `D=6`, `eta=1/6`, `T=2` example, the exact grid open-loop
value equals the independently computed continuous value:

\[
\boxed{
V_{\rm open}^{\rm grid}
=
V_{\rm open}^{\rm continuous}
=
\frac{23}{6}
}
\]

when the switching penalty is `1/4`. Equality is checked for this example; it is
not claimed for every denominator or problem.

---

## 12. Abstract interpretation: information is an action-timing resource

The same physical observations can have different decision value depending on
when they arrive relative to action and adversarial choice.

The state variable is not only the source law. A sufficient dynamic state also
contains:

- the previous codebook, because switching costs couple decisions;
- the remaining horizon, because future option value changes with time;
- the information available at the decision node;
- the order in which nature and the designer move.

Thus a predictive system's relevant state can be written schematically as

\[
\boxed{
\text{dynamic sufficient state}
=
(	ext{belief or law},
\text{installed action},
\text{remaining horizon},
\text{information pattern}).
}
\]

A static ambiguity set cannot represent all of this structure.

For an on-demand renderer, the analogue is that future observations are useful
only when they arrive before the commitments they could alter. An exact future
answer revealed after an irreversible action has no value for that action.
This is a general causal-decision principle, not evidence that the world is
rendered on demand.

---

## Nonclaims

- The source law is observed exactly in the current- and delayed-feedback
  models; there is no estimation noise.
- The policy observes a probability law, not merely one sampled source symbol.
- The source process is adversarial within the finite-grid transition graph; no
  stochastic transition probabilities are inferred.
- Policies and codebooks are deterministic. Shared-randomness policy games are
  not included here.
- The finite denominator grid is a declared model restriction and bounded
  checker, not a continuum theorem.
- The grid open-loop value is a lower bound on the continuous adversarial value.
- Switching cost is a declared rational design parameter rather than a physical
  measurement.
- The clairvoyant benchmark is not an online implementable policy without actual
  future knowledge.
- Internal expected code length is not parent-universe memory, energy, mass, or
  computation.
- None of these timing or coding identities is generic evidence for simulation.

---

## Next research targets

1. Replace exact law observation with finite noisy observation channels.
2. Promote the dynamic state from the true law to a set or distribution of
   plausible laws.
3. Solve robust belief-state games under delayed observations.
4. Price information acquisition and derive sensing-cost phase transitions.
5. Add shared-randomness policies and distinguish public from private random
   seeds.
6. Compare source-first, action-first, and simultaneous-move games through exact
   minimax gaps.
7. Extend finite-grid policies to certified upper and lower bounds for the
   continuous simplex.
8. Add path regret relative to current-law and clairvoyant dynamic oracles.
9. Study whether sufficient beliefs admit finite predictive-state compression.
