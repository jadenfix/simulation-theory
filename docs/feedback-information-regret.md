# Feedback information, regret, and oracle-frontier sufficiency

## Scope

A robust absolute-cost game and a regret game answer different questions.
The source-law information-pattern layer already computes the unavoidable
cumulative coding cost under four timing models:

1. open-loop code-sequence commitment;
2. one-period-delayed source-law feedback;
3. current-law feedback before the current codebook is chosen;
4. a path-first clairvoyant benchmark.

This note uses the same finite rational source-law grid, TV transition graph,
zero-error prefix-codebook universe, horizon, and switching charge, but changes
the objective.  Every information pattern is compared with the minimum-cost
code sequence selected after the entire source-law path is known.

For path \(p=(q_1,\ldots,q_T)\) and code sequence
\(a=(a_1,\ldots,a_T)\), write

\[
C(a,p)
=
\sum_{t=1}^{T}q_t^\top\ell_{a_t}
+
\kappa\sum_{t=2}^{T}\mathbf 1\{a_t\ne a_{t-1}\}.
\]

The path oracle is

\[
\boxed{
O(p)=\min_a C(a,p).
}
\]

For a deterministic or shared-randomness decision rule \(\pi\), pathwise
regret is

\[
\boxed{
R(\pi,p)=C(\pi,p)-O(p).
}
\]

The oracle is a benchmark, not an implementable causal policy.  All results are
finite-grid, finite-horizon, exact-rational, zero-error coding statements.  They
are not parent-hardware claims and are not evidence for simulation.

---

## 1. Information-pattern move order

The exact move order is part of every theorem.

### Open loop

The complete code sequence is selected before nature chooses a path:

\[
R_{\rm open}
=
\min_a\max_p[C(a,p)-O(p)].
\]

### Delayed feedback

At period \(t\), the designer knows \(q_{t-1}\) and the previous codebook,
chooses \(a_t\), and then nature chooses \(q_t\) among laws reachable from
\(q_{t-1}\).

### Current-law feedback

Nature first chooses \(q_t\), the designer observes it exactly, and then chooses
\(a_t\).

### Clairvoyance

Nature reveals the complete path before a code sequence is selected.  The
selected sequence is exactly the comparator oracle, so its regret is zero:

\[
\boxed{R_{\rm clairvoyant}=0.}
\]

Changing the move order changes the extensive-form game.  In particular,
current-law feedback is not the same as observing samples from the current law,
and neither is the same as knowing the future path.

---

## 2. Deterministic regret hierarchy

Every open-loop code sequence is also an admissible delayed-feedback policy
that ignores its observations.  Every delayed policy is an admissible
current-law policy that ignores the extra current-law information.  The
clairvoyant benchmark has access to the entire path.

Therefore the policy classes are nested, and minimizing the same pathwise
regret objective over larger classes yields

\[
\boxed{
0
=R_{\rm clairvoyant}
\le
R_{\rm current}
\le
R_{\rm delayed}
\le
R_{\rm open}.
}
\]

The implementation solves delayed and current regret by exact Fraction-valued
Bellman recurrences and stores every selected code, selected next law, witness
path, and value.  The certificate replays the recurrences independently.

---

## 3. Why current-law feedback has zero regret when switching is free

Assume \(\kappa=0\).  Then the path oracle decomposes period by period:

\[
O(p)
=
\sum_{t=1}^{T}
\min_a q_t^\top\ell_a.
\]

A current-law policy sees \(q_t\) before choosing and can select a minimizing
codebook independently at each period.  Hence it realizes the same cost on
every path:

\[
C(\pi_{\rm current},p)=O(p).
\]

Therefore

\[
\boxed{
\kappa=0
\implies
R_{\rm current}=0.
}
\]

This does not imply delayed feedback or open-loop commitment has zero regret.
They may choose before seeing the law that determines the current stage cost.

---

## 4. Switching cost creates a value of future foresight

When \(\kappa>0\), the path oracle is no longer a sum of independent one-period
minima.  A codebook that is locally cheapest at period \(t\) may be globally
suboptimal if switching into it creates another switch later.

Current-law feedback sees the present law but not the future sequence.  The
clairvoyant oracle can trade current stage cost against future switching cost.
Thus strict positive current-feedback regret is possible:

\[
\boxed{
\kappa>0
\centernot\implies
R_{\rm current}=0.
}
\]

The strictness is not caused by estimation noise.  It arises even when the
current law is observed exactly, because future laws remain unresolved.

---

## 5. Full-history Bellman recursion

The terminal regret adjustment is

\[
-O(q_{1:T}).
\]

Although the absolute-cost feedback game is Markov in the current law and the
previous codebook, the oracle subtraction depends on the complete realized path.
The conservative exact implementation therefore uses a Bellman state containing

\[
(t, q_{1:t-1}, a_{t-1}).
\]

### Delayed recursion

Let \(V_t^{\rm del}(h,a)\) be regret-to-go after history \(h\) and previous code
\(a\).  The designer moves before nature:

\[
V_t^{\rm del}(h,a)
=
\min_b
\left[
\kappa\mathbf1\{a\ne b\}
+
\max_{q'\in N(q_{t-1})}
\left(
q'^\top\ell_b
+V_{t+1}^{\rm del}(h\!\circ\!q',b)
\right)
\right].
\]

### Current-law recursion

Nature moves before the designer:

\[
V_t^{\rm cur}(h,a)
=
\max_{q'\in N(q_{t-1})}
\min_b
\left[
\kappa\mathbf1\{a\ne b\}
+q'^\top\ell_b
+V_{t+1}^{\rm cur}(h\!\circ\!q',b)
\right].
\]

At the horizon,

\[
V_T(h,a)=-O(h).
\]

This full-history state is sufficient but not always minimal.

---

## 6. The comparator frontier is an exact sufficient statistic

For the declared code-sequence oracle, define after a realized prefix

\[
z_j
=
\min\{
\text{comparator cost of the prefix among sequences ending in code }j
\}.
\]

When the next source law \(q\) arrives, the frontier updates as

\[
\boxed{
z'_j
=
q^\top\ell_j
+
\min_i
\left[
z_i+\kappa\mathbf1\{i\ne j\}\right].
}
\]

At the first period there is no initial switching charge, so

\[
z_j=q_1^\top\ell_j.
\]

After the complete path,

\[
\boxed{O(p)=\min_j z_j.}
\]

Thus the full law history can be replaced exactly by

\[
\boxed{
(t,q_{t-1},a_{t-1},z).
}
\]

The repository independently solves delayed and current regret using this
frontier state and requires exact equality with the full-history Bellman values.
For every exhaustively enumerated path it also recomputes the frontier oracle
and compares it with the independently enumerated clairvoyant sequence cost.

### Translation equivariance

For any scalar \(c\),

\[
F(z+c\mathbf1,q)
=
F(z,q)+c\mathbf1.
\]

Therefore write

\[
m=\min_j z_j,
\qquad
r=z-m\mathbf1.
\]

The relative frontier \(r\) has minimum zero and determines all future oracle
switching choices; the scalar baseline \(m\) tracks the absolute oracle cost.
Hence \((m,r)\) is another exact sufficient representation.

This is a sufficiency theorem, not a universal minimality theorem.  A particular
code family may admit further quotienting.

---

## 7. Shared open-loop randomization

A public source-independent seed may select an open-loop code sequence before
the source path is chosen.  Let \(x_a\) be the mixture weight of sequence
\(a\).  At path \(p\), expected regret is

\[
\sum_ax_a[C(a,p)-O(p)].
\]

The finite-grid path family produces a rational zero-sum matrix

\[
G_{pa}=C(a,p)-O(p).
\]

The shared open-loop value is

\[
\boxed{
R_{\rm shared}
=
\min_{x\in\Delta}
\max_p\sum_ax_aG_{pa}.
}
\]

It satisfies

\[
R_{\rm shared}\le R_{\rm open},
\]

but there is no general ordering between shared open-loop randomization and
deterministic delayed or current-law feedback.  They are different resources.
A theorem comparing them must specify a hybrid game containing both.

---

## 8. Exact game pruning without weakening the certificate

Finite-grid path games can contain many duplicate or pointwise dominated rows
and columns.

For the maximizing source player, row \(r\) is redundant when some retained row
\(s\) satisfies

\[
G_{sa}\ge G_{ra}
\qquad\forall a.
\]

For the minimizing designer, column \(a\) is redundant when some retained
column \(b\) satisfies

\[
G_{pb}\le G_{pa}
\qquad\forall p.
\]

The implementation iterates exact duplicate and dominance elimination, solves
the reduced game, and then lifts the primal and dual mixtures back to the full
matrix.

The lifted certificate recomputes every original row payoff and every original
column payoff and requires

\[
\max_p G_px
=
v
=
\min_a y^\top G_{:a}
\]

with an exact rational zero gap.  Consequently pruning is only a search
acceleration.  A wrong elimination cannot silently alter the theorem because it
would fail the full-matrix primal or dual receipt.

---

## 9. Exact decomposition of deterministic information value

The deterministic hierarchy gives the identity

\[
\boxed{
R_{\rm open}
=
(R_{\rm open}-R_{\rm delayed})
+
(R_{\rm delayed}-R_{\rm current})
+
R_{\rm current}.
}
\]

The three nonnegative terms quantify:

1. value of one-period-delayed feedback over open loop;
2. incremental value of observing the current law before acting;
3. residual value of future foresight beyond current-law feedback.

Public randomization supplies the separate benefit

\[
R_{\rm open}-R_{\rm shared}.
\]

It is not inserted into the deterministic telescope because information and
randomness may overlap.  Their joint value requires a separately specified
hybrid extensive-form game.

---

## 10. Relevance to an on-demand renderer

A renderer facing a drifting distribution of future queries may possess several
different resources:

- no source-law information;
- lagged estimates of the query law;
- exact current-law information;
- a complete forecast;
- source-independent common randomization;
- permission to reconfigure its internal representation.

The results show that these resources have different mathematical values.  In
particular:

- exact present information need not remove regret when reconfiguration couples
  periods;
- randomization and feedback are not substitutes by definition;
- dynamic regret cannot be recovered by subtracting two robust absolute values;
- the comparator class and move order are part of the claim;
- exact history can sometimes be compressed to a finite oracle frontier.

None of these facts distinguishes a simulator from ordinary distributed or
adaptive computation.  They constrain only systems implementing the declared
finite source-law and coding interface.

---

## Nonclaims

- Source laws are observed exactly in the feedback games; sampled or noisy
  observation requires a belief-state model.
- The clairvoyant oracle is a benchmark, not an implementable causal policy.
- Shared randomness is public, source independent, and known to all required
  decoders.
- Dominance pruning is pointwise; no unsupported convex-dominance shortcut is
  used.
- The comparator frontier is sufficient for the declared switching-cost oracle,
  not proved minimal for every candidate family.
- The source simplex is restricted to one declared rational grid.
- Enumeration caps are fail-closed finite-check boundaries, not scalability
  guarantees.
- Switching cost is a declared rational accounting input.
- Internal regret, code lengths, and frontier coordinates are not physical
  parent-substrate resource claims.
- No result in this note is evidence that reality is simulated.

---

## Next research targets

1. Noisy source-law signals and exact belief-state regret.
2. Observation channels that evolve with the selected codebook or action.
3. Shared-randomness feedback policies rather than shared open-loop sequences.
4. Partial monitoring where only emitted source symbols are observed.
5. Robust regret under uncertainty over the transition law itself.
6. Comparator frontiers for larger switching-state machines and path-dependent
   reconfiguration costs.
7. Strongly adaptive regret over every subinterval.
8. Multi-letter source coding under both drift and feedback.
9. Exact Blackwell comparisons for dynamic observation channels.
