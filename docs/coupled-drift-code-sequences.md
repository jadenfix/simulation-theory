# Coupled source-law drift and precommitted code sequences

## Purpose

The previous drift result solved a special but important case: one source law
moves through time, but the same state-cost vector is used at every period.
For one fixed linear objective, total-variation extremizers can be chosen along
one nested mass-transport path, so the sum of periodwise marginal optima is
attainable.

That argument fails as soon as the cost vector changes with time. A law that is
best for period one may be too far away to reach the law that is best for period
two. The source path is then a coupled object rather than a collection of
independent ambiguity balls.

This lane solves the exact bounded rational problem

\[
\begin{aligned}
\max_{q_1,\ldots,q_T}
&\quad \sum_{t=1}^T q_t^\top g_t\\
\text{subject to}
&\quad q_t\in\Delta_{n-1},\\
&\quad q_0=p,\\
&\quad \operatorname{TV}(q_t,q_{t-1})\le \eta_t
\quad(t=1,\ldots,T),
\end{aligned}
\]

where every input is rational and every finite search has an explicit hard cap.
It then places an outer decision problem around that path optimizer: choose a
complete deterministic zero-error prefix codebook for each period before the
source path is selected, optionally paying a rational cost whenever the
codebook changes.

The resulting hierarchy separates:

1. the source alphabet and zero-error confusion relation;
2. the initial source law;
3. the allowed temporal motion of that law;
4. the precommitted sequence of state-cost vectors;
5. the adversarial path chosen after the sequence is fixed;
6. the accounting rule for codebook reconfiguration.

None of those objects is automatically a model of parent-universe hardware.

---

## 1. Total variation gives an exact event-halfspace representation

For probability laws \(u,v\) on a finite alphabet \([n]\),

\[
\operatorname{TV}(u,v)
=
\max_{S\subseteq[n]}
|u(S)-v(S)|.
\]

Because signed probability differences sum to zero,

\[
u(S)-v(S)
=
-\bigl(u(S^c)-v(S^c)\bigr).
\]

Therefore one event from each complement pair is enough. The implementation
chooses every nonempty subset of the first \(n-1\) states. There are

\[
2^{n-1}-1
\]

such event representatives.

For every transition \(t\), the TV condition is exactly the finite collection

\[
q_t(S)-q_{t-1}(S)\le\eta_t,
\]

\[
q_{t-1}(S)-q_t(S)\le\eta_t
\]

for all canonical events \(S\).

This is not an approximation to total variation. It is an exact finite
halfspace description.

---

## 2. Eliminate one simplex coordinate per period

Write

\[
x_{t,j}=q_t(j),
\qquad j=1,\ldots,n-1,
\]

and recover the final coordinate from

\[
q_t(n)=1-\sum_{j=1}^{n-1}x_{t,j}.
\]

The path has

\[
\boxed{d=T(n-1)}
\]

free rational coordinates.

For each period, simplex feasibility contributes

\[
-x_{t,j}\le0
\qquad(j<n)
\]

and

\[
\sum_{j<n}x_{t,j}\le1.
\]

The event constraints from the preceding section are linear in the same free
coordinates. Consequently, the complete admissible path family is a bounded
rational polytope

\[
\boxed{\mathcal P_{p,\eta_{1:T}}=\{x:Ax\le b\}.}
\]

The number of declared halfspaces is

\[
T\left[n+2\left(2^{n-1}-1\right)\right].
\]

The exact checker enumerates every \(d\)-row active basis below a configured
cap, solves it over \(\mathbb Q\), checks every omitted halfspace, reconstructs
the full probability path, and deduplicates degenerate representations.

This is deliberately a bounded exact method. The active-basis count

\[
\binom{m}{d}
\]

can grow quickly. Exceeding the cap raises an error rather than returning a
partial search that could be mistaken for an optimum certificate.

---

## 3. Time-varying costs remain a single linear program

For period cost vector

\[
g_t=(g_{t,1},\ldots,g_{t,n}),
\]

eliminating the final probability coordinate gives

\[
q_t^\top g_t
=
g_{t,n}
+
\sum_{j<n}
\bigl(g_{t,j}-g_{t,n}\bigr)x_{t,j}.
\]

Thus the coupled path objective is

\[
\boxed{
\max_x c_0+c^\top x
\quad\text{subject to }Ax\le b.
}
\]

A linear objective over a nonempty bounded polytope reaches its optimum at a
vertex. The primal certificate therefore consists of:

- the complete bounded path-polytope vertex set;
- the selected maximizing vertex;
- the reconstructed path \(q_1,\ldots,q_T\);
- an exact check of every simplex and TV transition constraint;
- an exact rational objective value.

---

## 4. An independent exact dual proves optimality

The dual problem is

\[
\boxed{
\min_{y\ge0}
\ c_0+b^\top y
\quad\text{subject to }A^\top y=c.
}
\]

The implementation exhausts rational basic dual supports below a hard cap. A
valid receipt satisfies

\[
y\ge0,
\qquad
A^\top y=c,
\]

and exact equality

\[
\boxed{
c_0+c^\top x^*
=
c_0+b^\top y^*.
}
\]

It also checks complementary slackness:

\[
y_i^*\bigl(b_i-a_i^\top x^*\bigr)=0
\qquad\forall i.
\]

The dual multipliers can be read as shadow prices on simplex boundaries and
per-event speed limits. That is a decision-theoretic interpretation inside the
declared finite model, not an energy or physical-force interpretation.

---

## 5. Independent marginal balls form only a relaxation

Triangle inequality implies

\[
\operatorname{TV}(q_t,p)
\le
R_t,
\qquad
R_t=\min\left(1,\sum_{s=1}^t\eta_s\right).
\]

Therefore

\[
\sup_{\text{admissible paths}}
\sum_t q_t^\top g_t
\le
\sum_t
\sup_{\operatorname{TV}(q,p)\le R_t}
q^\top g_t.
\]

The right-hand side optimizes every time marginal independently. It forgets
that the selected marginals must be connected by one feasible path. The code
reports this quantity as a **marginal relaxation upper bound**, not as the
coupled optimum.

### Strict two-state gap

Take

\[
p=(1/2,1/2),
\qquad
\eta_1=\eta_2=1/4,
\]

with

\[
g_1=(0,1),
\qquad
g_2=(1,0).
\]

Let \(x_t=q_t(2)\). The coupled objective is

\[
x_1+(1-x_2)=1+x_1-x_2.
\]

The second TV constraint gives

\[
|x_2-x_1|\le1/4,
\]

hence

\[
1+x_1-x_2\le5/4.
\]

The path

\[
x_1=3/4,
\qquad
x_2=1/2
\]

attains the bound, so

\[
\boxed{V_{\mathrm{coupled}}=5/4.}
\]

The independent marginal calculation instead chooses \(x_1=3/4\) for period
one and \(x_2=0\) for period two, producing

\[
3/4+1=7/4.
\]

Those marginals are not one-step reachable from each other. The relaxation gap
is therefore

\[
\boxed{7/4-5/4=1/2.}
\]

This is the simplest explicit demonstration that time-indexed ambiguity cannot
always be replaced by a list of expanding static balls.

---

## 6. Common ordering is a sufficient condition for equality

The TV support-function maximizer for one linear cost vector is constructed by
moving probability mass from low-cost states to high-cost states in sorted
order. The transported distribution depends on that ordering and on the radius,
not on an overall positive rescaling of the costs.

If every \(g_t\) induces the same weak ordering of states, one canonical
transport path can be continued through the cumulative radii

\[
R_1\le R_2\le\cdots\le R_T.
\]

That single path simultaneously attains every marginal support function. Hence,
under the common-ordering condition,

\[
\boxed{
V_{\mathrm{coupled}}
=
\sum_t
\sup_{\operatorname{TV}(q,p)\le R_t}
q^\top g_t.
}
\]

The condition is sufficient, not necessary. Different orderings can still
happen to share compatible maximizers in special degenerate instances.

---

## 7. Precommitted codebook sequences

For a finite zero-error function-computation problem, every deterministic
prefix codebook induces one source-state length vector

\[
\ell^{(c)}=(\ell^{(c)}_1,\ldots,\ell^{(c)}_n).
\]

A horizon-\(T\) precommitted sequence is

\[
c_{1:T}=(c_1,\ldots,c_T).
\]

The source adversary sees the entire declared sequence and chooses one
admissible law path. Its communication cost is

\[
\sup_{q_{1:T}}
\sum_{t=1}^T
q_t^\top\ell^{(c_t)}.
\]

If changing the codebook costs \(\kappa\ge0\), define

\[
N_{\mathrm{switch}}(c_{1:T})
=
\sum_{t=2}^T\mathbf 1\{c_t\ne c_{t-1}\}.
\]

The precommitted design problem is

\[
\boxed{
\min_{c_{1:T}}
\left[
\sup_{q_{1:T}}
\sum_t q_t^\top\ell^{(c_t)}
+
\kappa N_{\mathrm{switch}}(c_{1:T})
\right].
}
\]

The repository exhausts every sequence from the bounded componentwise-
undominated deterministic code universe below an explicit sequence cap.

Componentwise dominance is safe here. If

\[
\ell^{(a)}_i\le\ell^{(b)}_i
\qquad\forall i,
\]

then

\[
q^\top\ell^{(a)}
\le
q^\top\ell^{(b)}
\]

for every source law \(q\). A codebook dominated in every state can never help
at any period or on any admissible path.

The sequence is fixed before the source path. This is not an adaptive policy
that observes current probabilities or realized symbols and then changes code.

---

## 8. Exact rotating-leaf gain for uniform K3

Let the confusion graph be complete on three states, so each state needs a
distinct message. Every full binary three-leaf tree has one length-one leaf and
two length-two leaves.

Start from

\[
p=(1/3,1/3,1/3),
\qquad
\eta_1=\eta_2=1/6.
\]

Consider the rotating sequence

\[
\ell_1=(1,2,2),
\qquad
\ell_2=(2,1,2).
\]

Its total communication cost is

\[
4-q_{1,1}-q_{2,2}.
\]

The first drift constraint implies

\[
q_{1,3}\le1/2,
\]

so

\[
q_{1,1}+q_{1,2}\ge1/2.
\]

The second drift constraint implies

\[
q_{2,2}\ge q_{1,2}-1/6.
\]

Therefore

\[
q_{1,1}+q_{2,2}
\ge
q_{1,1}+q_{1,2}-1/6
\ge
1/3.
\]

Hence the worst communication cost is at most

\[
4-1/3=11/3.
\]

The path

\[
q_1=(1/4,1/4,1/2),
\]

\[
q_2=(1/4,1/12,2/3)
\]

has TV increment \(1/6\) at each step and attains the bound. Thus

\[
\boxed{V_{\mathrm{rotate}}=11/3.}
\]

For the best static tree, the adversary can drive the one short-leaf state from
probability \(1/3\) to \(1/6\) and then to zero. Therefore

\[
\boxed{V_{\mathrm{static}}=23/6.}
\]

The communication gain from precommitted rotation is

\[
\boxed{23/6-11/3=1/6.}
\]

The independent marginal relaxation for the rotating sequence is also
\(23/6\), so the gain appears precisely because the two marginal worst laws
cannot be connected fast enough.

---

## 9. Exact switching-cost phase boundary

The rotating sequence uses one codebook switch. With switching penalty
\(\kappa\), its total cost is

\[
11/3+\kappa.
\]

The best static sequence costs \(23/6\). Rotation is strictly preferred when

\[
11/3+\kappa<23/6,
\]

or

\[
\boxed{\kappa<1/6.}
\]

At

\[
\boxed{\kappa_c=1/6}
\]

the two plans tie. The deterministic tie-breaking rule selects the lower-
switch static sequence. Above that threshold, the static code is optimal.

This is a reconfiguration threshold inside the declared coding model, not a
physical phase transition.

---

## 10. What the exact certificate contains

A coupled cost certificate records:

1. the initial rational source law;
2. every per-period drift budget;
3. the complete bounded path halfspace system;
4. every exact rational path vertex below the declared active-basis cap;
5. the maximizing path and its exact cumulative cost;
6. the dual multipliers;
7. exact primal-dual equality;
8. complementary slackness;
9. the independent marginal relaxation and its gap.

A code-sequence certificate additionally records:

1. the complete bounded undominated deterministic code universe;
2. every admissible precommitted sequence below the sequence cap;
3. its exact worst coupled path value;
4. its switch count and switching cost;
5. the selected global sequence;
6. the best static sequence;
7. the exact reconfiguration gain.

A search cap is part of the theorem scope. If a cap is exceeded, no optimum
certificate is returned.

---

## 11. First-principles interpretation

The deepest point is not that a renderer or encoder must be expensive. It is
that a temporal consistency problem is defined by a **reachable set of future
laws**, not merely by independent uncertainty at each time.

When future objectives change, the relevant state includes enough information
to answer questions such as:

- Which source laws remain reachable from the current law?
- Which future cost directions are mutually compatible?
- How much optionality is lost by moving probability mass now?
- Is a specialized codebook worth its future reconfiguration cost?

That is a dynamic sufficient-state problem. The one-step law by itself may be
insufficient if future feasibility depends on how the law was reached or on a
remaining movement budget.

For simulation-theory applications, this suggests a general caution:

\[
\text{separate per-time plausibility}
\not\Rightarrow
\text{jointly realizable world history}.
\]

Any claimed anomaly, resource bound, or rendering shortcut based on marginal
snapshots must still satisfy one coherent causal path model.

---

## 12. Boundaries and nonclaims

The current lane assumes:

- a finite source alphabet;
- rational initial law, costs, and drift budgets;
- total variation as the temporal movement metric;
- a finite known horizon;
- zero-error deterministic prefix codebooks;
- a code sequence committed before the source path is chosen;
- additive expected communication cost;
- a constant nonnegative cost per codebook switch;
- complete active-basis and sequence enumeration below explicit caps.

It does not yet solve:

- adaptive codebook policies based on observed symbols or estimated laws;
- partial observation of the source law;
- online learning and exploration;
- stochastic or adversarially uncertain drift budgets;
- KL-, Wasserstein-, or physics-derived transition geometry;
- delay, queueing, or peak-bandwidth constraints;
- source feedback caused by the selected codebook;
- mixed or quantum codebook policies;
- infinite-horizon average-cost control;
- parent-substrate computation, energy, mass, or spacetime.

The next mathematical layer is a finite dynamic game in which the encoder can
condition future code choices on a declared observation history. That requires
specifying the observation kernel and information pattern before writing a
Bellman equation; otherwise “adaptation” silently grants the encoder access to
the hidden source law.
