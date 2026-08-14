# Stochastic predictive laws, covers, and network capacity

## Scope

The exact predictive-network theorem groups hidden records by deterministic
future-query signatures. That is the correct zero-error object when every query
has a fixed answer.

Many physical and statistical interfaces are stochastic. A hidden state may
specify not one future outcome but a probability law:

\[
P_x(\cdot\mid q).
\]

An approximate renderer may also be allowed to replace a target law by a nearby
law. A packing lower bound shows that some number of predictive states is
necessary, but it does not show that the number is sufficient.

This note develops both sides for finite stochastic query families:

1. exact equivalence by equality of all conditional laws;
2. weighted and worst-query total-variation geometry;
3. a finite predictive packing lower bound;
4. a constructive target-centered covering upper bound;
5. a single-sink network certificate with three outcomes: impossible,
   constructively feasible, or unresolved;
6. an exact arbitrary-center solution for finite Bernoulli families.

The distinction between **target-centered covers** and **arbitrary predictor
laws** is essential. Restricting centers to existing target laws gives a clean
constructive upper bound, but can require more states than an optimal renderer.

All results concern declared finite internal probability models. They are not
evidence that reality is simulated and do not identify model bits, qubits, or
network capacities with parent-universe hardware or energy.

---

## 1. Finite stochastic future-query families

Let

\[
\mathcal X=\{x_1,\ldots,x_N\}
\]

be a finite hidden-record family. Let

\[
\mathcal Q=\{q_1,\ldots,q_r\}
\]

be the future queries, and let query \(q\) have finite outcome space

\[
\mathcal Y_q.
\]

For every record and query, specify a categorical law

\[
P_x(y\mid q),
\qquad
P_x(y\mid q)\ge0,
\qquad
\sum_{y\in\mathcal Y_q}P_x(y\mid q)=1.
\]

The complete stochastic signature is the tensor

\[
\boxed{
\Sigma(x)
=
\bigl(P_x(\cdot\mid q_1),\ldots,P_x(\cdot\mid q_r)\bigr).
}
\]

The repository stores finite outcome spaces and aligned probability vectors for
every record-query pair. Validation checks nonnegativity, normalization,
finite values, unique records, unique queries, and unique named outcomes.

### Deterministic families are a special case

If query \(q\) has deterministic outcome \(f_q(x)\), define

\[
P_x(y\mid q)
=
\mathbf1\{y=f_q(x)\}.
\]

Every deterministic signature embeds as a collection of categorical point
masses. The stochastic implementation verifies that this embedding preserves
exact class counts and total-variation geometry.

---

## 2. Exact stochastic predictive equivalence

Define

\[
\boxed{
x\sim x'
\iff
P_x(\cdot\mid q)=P_{x'}(\cdot\mid q)
\quad\forall q\in\mathcal Q.}
\]

Let

\[
K
=
|\{\Sigma(x):x\in\mathcal X\}|
\]

be the number of distinct conditional-law tensors.

Suppose a finite renderer state \(M(x)\) is fixed before the future query is
chosen. Given \(M\) and query \(q\), the renderer uses fresh randomness to
sample an outcome law

\[
\widehat P(\cdot\mid M,q).
\]

If two records share one state,

\[
M(x)=M(x'),
\]

then the induced law for every query is the same. Exact correctness therefore
requires

\[
P_x(\cdot\mid q)
=
P_{x'}(\cdot\mid q)
\quad\forall q.
\]

Thus one renderer state cannot contain two different exact stochastic
signatures. Hence

\[
\boxed{|\mathcal M|\ge K.}
\]

Conversely, send one label for each distinct law tensor. The decoder stores the
associated query laws and samples from the requested one. Therefore

\[
\boxed{
\text{minimum exact states}=K,
\qquad
\text{minimum fixed-length bits}=\lceil\log_2K\rceil.
}
\]

Fresh sampling randomness does not encode which target law was intended. It can
sample a declared law after the class label is known, but cannot merge two
incompatible target tensors into one exact state.

---

## 3. Exogenous query schedules and the joint future law

Let a query schedule be

\[
w_q\ge0,
\qquad
\sum_qw_q=1.
\]

The joint law over selected query and observed outcome is

\[
\boxed{
P_x(q,y)
=
w_qP_x(y\mid q).
}
\]

For two records,

\[
\begin{aligned}
\operatorname{TV}(P_x,P_u)
&=
\frac12
\sum_q\sum_y
\left|
w_qP_x(y\mid q)-w_qP_u(y\mid q)
\right|\\
&=
\sum_qw_q
\frac12\sum_y
|P_x(y\mid q)-P_u(y\mid q)|.
\end{aligned}
\]

Therefore

\[
\boxed{
\operatorname{TV}(P_x,P_u)
=
\sum_qw_q
\operatorname{TV}
\bigl(P_x(\cdot\mid q),P_u(\cdot\mid q)\bigr).
}
\]

This is an exact chain rule for total variation when the query marginal is the
same under both records and the query identity is retained in the transcript.

### Worst-query metric

If the renderer must be accurate for every allowed query rather than under one
average schedule, use

\[
\boxed{
d_{\max}(x,u)
=
\max_q
\operatorname{TV}
\bigl(P_x(\cdot\mid q),P_u(\cdot\mid q)\bigr).
}
\]

The weighted and worst-query metrics answer different operational questions:

- weighted TV permits larger errors on rarely selected queries;
- worst-query TV protects every query individually.

The implementation requires the caller to choose one and does not silently
substitute between them.

---

## 4. Weighted KL and Pinsker

For categorical laws \(p\) and \(r\), define

\[
D_{\mathrm{KL}}(p\|r)
=
\sum_{y:p_y>0}
p_y\log\frac{p_y}{r_y}.
\]

If \(p_y>0\) while \(r_y=0\), the divergence is infinite.

Because the query marginal is shared,

\[
\boxed{
D_{\mathrm{KL}}(P_x\|P_u)
=
\sum_qw_q
D_{\mathrm{KL}}
\bigl(P_x(\cdot\mid q)\|P_u(\cdot\mid q)\bigr).
}
\]

Pinsker then gives

\[
\boxed{
\operatorname{TV}(P_x,P_u)
\le
\sqrt{rac12
D_{\mathrm{KL}}(P_x\|P_u)}.
}
\]

The repository computes the exact finite weighted KL expression and the
corresponding Pinsker upper bound. This provides an independent consistency
check between probability geometry and information geometry.

The bound is directional because KL is directional, while total variation is
symmetric.

---

## 5. The approximate predictive-state problem

Fix a metric \(d\), either weighted joint TV or worst-query TV.

A renderer with state set \(\mathcal M\) assigns each hidden record to a state
and each state to one predictor law tensor \(R_m\). It is
\(\epsilon\)-accurate when

\[
\boxed{
\forall x\in\mathcal X,
\quad
d(P_x,R_{M(x)})\le\epsilon.}
\]

Let

\[
M_\epsilon^*
\]

be the minimum possible number of predictive states, allowing the predictor
centers \(R_m\) to be arbitrary admissible probability-law tensors, not only
laws already present among the targets.

Computing \(M_\epsilon^*\) is a metric covering problem. For general finite
stochastic families, the center space is continuous and the exact optimization
can be difficult.

The repository therefore computes one rigorous lower bound and one constructive
upper bound:

\[
\boxed{
\mathsf P_{2\epsilon}
\le
M_\epsilon^*
\le
\mathsf C^{\mathrm{target}}_\epsilon.}
\]

The two quantities have different meanings and must remain separate.

---

## 6. Packing lower bound

A set

\[
\mathcal A\subseteq\mathcal X
\]

is a strict \(2\epsilon\)-packing when

\[
\boxed{
d(P_x,P_u)>2\epsilon
\quad\forall x\ne u\in\mathcal A.}
\]

Suppose one predictor center \(R\) approximated two packed targets:

\[
d(P_x,R)\le\epsilon,
\qquad
d(P_u,R)\le\epsilon.
\]

The triangle inequality would imply

\[
d(P_x,P_u)
\le
d(P_x,R)+d(R,P_u)
\le2\epsilon,
\]

contradicting strict separation.

Thus one predictive state covers at most one member of the packing. If the
maximum packing size is

\[
\mathsf P_{2\epsilon},
\]

then

\[
\boxed{
M_\epsilon^*
\ge
\mathsf P_{2\epsilon}.}
\]

The memory lower bound is

\[
\boxed{
\log_2|\mathcal M|
\ge
\left\lceil
\log_2\mathsf P_{2\epsilon}
\right\rceil.}
\]

The finite implementation forms a graph whose vertices are targets and whose
edges join pairs farther than \(2\epsilon\). An exact bounded maximum-clique
search returns the largest packing.

---

## 7. Target-centered covering upper bound

A target-centered \(\epsilon\)-cover is a subset

\[
\mathcal C\subseteq\mathcal X
\]

such that every target is within \(\epsilon\) of at least one selected target
law:

\[
\boxed{
\forall x\in\mathcal X,
\quad
\exists c\in\mathcal C:
\quad
d(P_x,P_c)\le\epsilon.}
\]

Let

\[
\mathsf C^{\mathrm{target}}_\epsilon
\]

be the minimum size of such a cover.

This gives a constructive renderer:

1. assign each hidden record to one covering center;
2. retain or transmit the center index;
3. when query \(q\) arrives, sample from the center law
   \(P_c(\cdot\mid q)\).

By construction the induced future law is within \(\epsilon\) of the target.
Therefore

\[
\boxed{
M_\epsilon^*
\le
\mathsf C^{\mathrm{target}}_\epsilon.}
\]

The repository solves the finite target-centered problem exactly as a bounded
set-cover search:

- each possible target center covers the records inside its
  \(\epsilon\)-ball;
- a greedy cover provides an initial upper bound;
- branch and bound chooses an uncovered target with few feasible centers;
- an optimistic maximum-coverage bound prunes impossible improvements.

Random bounded Bernoulli instances were additionally checked against complete
combination enumeration during development.

### Why the upper bound may be conservative

An optimal predictor center need not be a target law. Restricting centers to
\(\{P_x:x\in\mathcal X\}\) can require extra states. Therefore

\[
\mathsf C^{\mathrm{target}}_\epsilon
\]

is an exact target-centered cover number but only an upper bound on the
unrestricted predictive-state optimum.

---

## 8. Packing-cover bracket

Combining the two finite computations gives

\[
\boxed{
\mathsf P_{2\epsilon}
\le
M_\epsilon^*
\le
\mathsf C^{\mathrm{target}}_\epsilon.}
\]

In fixed-length bits,

\[
\boxed{
\left\lceil\log_2\mathsf P_{2\epsilon}\right\rceil
\le
\left\lceil\log_2M_\epsilon^*\right\rceil
\le
\left\lceil
\log_2\mathsf C^{\mathrm{target}}_\epsilon
\right\rceil.}
\]

Three cases are informative:

1. **The bounds match.** The exact number of predictive bits is determined.
2. **The state counts differ but the bit ceilings match.** The fixed-length
   network capacity can still be determined.
3. **The bit bounds differ.** The general finite problem remains unresolved
   between a converse and one constructive scheme.

The implementation reports both sizes and both bit counts rather than hiding
the gap behind one number.

---

## 9. Approximate single-sink network certificate

Let a directed integer-capacity network connect source \(s\) to sink \(t\).
Let one network unit carry \(\kappa\) exact classical index bits under the
declared carrier model.

Define

\[
L
=
\left\lceil
\frac{
\left\lceil\log_2\mathsf P_{2\epsilon}\right\rceil
}{\kappa}
\right\rceil
\]

and

\[
U
=
\left\lceil
\frac{
\left\lceil
\log_2\mathsf C^{\mathrm{target}}_\epsilon
\right\rceil
}{\kappa}
\right\rceil.
\]

Let the source-sink min-cut be \(C_{\min}\).

### Impossible region

If

\[
C_{\min}<L,
\]

the cut cannot distinguish every packed target. No
\(\epsilon\)-accurate renderer exists under the declared interface.

### Constructively feasible region

If

\[
C_{\min}\ge U,
\]

the source sends the target-cover center index through an integral max flow.
The sink reconstructs the center and samples its conditional law. This is an
explicit \(\epsilon\)-accurate renderer.

### Unresolved region

If

\[
L\le C_{\min}<U,
\]

the packing converse does not rule the network out, while the target-centered
construction does not fit. An arbitrary-center cover or a better coding scheme
may close the gap.

The certificate therefore returns one of exactly three statuses:

\[
\boxed{
\texttt{impossible},
\quad
\texttt{constructively-feasible},
\quad
\texttt{unresolved}.}
\]

It also returns:

- the exact bounded packing;
- the exact target-centered cover;
- the target-to-center assignment;
- lower and constructive upper network units;
- the min-cut;
- and routed paths when the constructive upper scheme fits.

This is more honest than interpreting a lower bound as an implementation or an
upper construction as an optimality theorem.

---

## 10. Exact stochastic network capacity

At \(\epsilon=0\), arbitrary and target-centered centers coincide with exact
law tensors. Let \(K\) be the number of distinct stochastic signatures.

The exact network requirement is

\[
\boxed{
U_0
=
\left\lceil
\frac{\lceil\log_2K\rceil}{\kappa}
\right\rceil.}
\]

For one sink, the predictive min-cut theorem gives

\[
\boxed{
\text{exact stochastic feasibility}
\iff
C_{\min}(s,t)\ge U_0.}
\]

Records with identical future law tensors can be merged even if they are
otherwise different. The exact payload depends on law classes, not record
count.

---

## 11. Bernoulli total variation is one-dimensional

For one Bernoulli query with success probabilities \(p\) and \(u\),

\[
P_p=(1-p,p),
\qquad
P_u=(1-u,u).
\]

Their total variation is

\[
\begin{aligned}
\operatorname{TV}(P_p,P_u)
&=
\frac12\left(
|(1-p)-(1-u)|+|p-u|
\right)\\
&=|p-u|.
\end{aligned}
\]

Thus a finite Bernoulli family is a finite subset of the interval \([0,1]\)
with ordinary absolute distance.

This special geometry permits exact arbitrary-center solutions rather than only
a target-centered upper bound.

---

## 12. One-state Bernoulli minimax radius

Given finite parameters

\[
p_1,\ldots,p_N,
\]

let

\[
p_{\min}=\min_i p_i,
\qquad
p_{\max}=\max_i p_i.
\]

For one predictor center \(c\), the worst error is

\[
R(c)=\max_i|p_i-c|.
\]

Every center obeys

\[
R(c)
\ge
\frac{p_{\max}-p_{\min}}2,
\]

because the two extreme points are separated by
\(p_{\max}-p_{\min}\), and one center cannot be closer than half their
separation to both.

The midpoint

\[
\boxed{
c^*
=
\frac{p_{\min}+p_{\max}}2}
\]

achieves equality. Therefore

\[
\boxed{
R^*
=
\frac{p_{\max}-p_{\min}}2.}
\]

The repository returns this exact minimax center and radius.

---

## 13. Exact finite Bernoulli covering

We now seek the minimum number of arbitrary Bernoulli centers whose radius-
\(\epsilon\) intervals cover all target parameters.

Sort the targets:

\[
p_{(1)}\le\cdots\le p_{(N)}.
\]

Consider the leftmost uncovered target \(a\). Any center covering it must lie in

\[
[a-\epsilon,a+\epsilon].
\]

To cover as far right as possible without losing \(a\), choose

\[
\boxed{c=\min(1,a+\epsilon).}
\]

This center covers every target up to

\[
c+\epsilon.
\]

Remove those targets and repeat.

### Greedy optimality proof

Take any feasible cover. Its first center covering the leftmost target \(a\)
can be moved rightward to \(\min(1,a+\epsilon)\):

- it still covers \(a\);
- its right endpoint does not decrease;
- no target lies left of \(a\), so no required target is lost.

Therefore some optimal cover begins with the greedy center. Removing all points
it covers leaves the same problem on the remaining suffix. Induction proves the
algorithm uses the minimum possible number of arbitrary centers.

Hence the repository computes the exact unrestricted Bernoulli state count

\[
\boxed{M_{\epsilon,\mathrm{Bern}}^*.}
\]

The corresponding exact one-sink network units are

\[
\boxed{
\left\lceil
\frac{
\left\lceil\log_2M_{\epsilon,\mathrm{Bern}}^*\right\rceil
}{\kappa}
\right\rceil.}
\]

---

## 14. Why arbitrary centers matter

Take only two target laws:

\[
p=0,
\qquad
p=1,
\]

with tolerance

\[
\epsilon=\frac12.
\]

### Packing lower bound

The pairwise distance is one, which is not strictly greater than

\[
2\epsilon=1.
\]

The strict packing can contain only one target, so the lower bound is one state.

### Target-centered cover

Neither target covers the other because their distance is one, greater than
\(\epsilon=1/2\). A target-centered cover needs two states.

### Arbitrary center

The predictor

\[
c=\frac12
\]

is at distance \(1/2\) from both. Therefore one state is sufficient.

Thus

\[
\boxed{
1
=
M_{1/2}^*
<
\mathsf C^{\mathrm{target}}_{1/2}
=2.}
\]

This is not a numerical corner case. It demonstrates a structural point:

> A target-centered cover is a constructive upper bound, not the unrestricted
> approximate state optimum.

The network certificate correctly labels a zero-capacity network as
`unresolved` under the general packing/target-cover bracket, while the special
Bernoulli solver proves it feasible with one zero-bit state.

---

## 15. Finite even-grid example

Consider Bernoulli targets

\[
\{0,0.2,0.4,0.6,0.8,1\}
\]

with

\[
\epsilon=0.2.
\]

### Packing

A strict packing needs pairwise distance greater than

\[
0.4.
\]

Two targets can be selected, but no three satisfy the strict separation. Thus

\[
\mathsf P_{0.4}=2.
\]

### Target-centered cover

Centers at \(0.2\) and \(0.8\) cover the whole set:

\[
[0,0.4]
\cup
[0.6,1].
\]

Therefore

\[
\mathsf C^{\mathrm{target}}_{0.2}=2.
\]

The lower and upper bounds match:

\[
\boxed{M_{0.2}^*=2.}
\]

One predictive bit is necessary and sufficient. A one-unit classical or
unassisted-qubit min-cut is therefore exact for this finite approximate family;
a disconnected sink is impossible.

The finite implementation recovers both packing and cover size two and routes
the cover index through a one-unit network.

---

## 16. Quantum capacity interpretation

The stochastic certificate carries a classical predictive-center index.
Therefore it inherits the explicit capacity multiplier from the exact network
lane:

\[
\kappa=
\begin{cases}
1,&\text{classical bit edge},\\
1,&\text{unassisted qubit carrying exact classical index bits},\\
2,&\text{edge-local entanglement-assisted dense-coded index bits}.
\end{cases}
\]

The stochastic sampling happens at the sink after the index is recovered. The
payload itself is classical in this construction.

The factor-two assisted model assumes:

- preshared Bell pairs independent of the hidden record;
- suitable decoding at each receiving node;
- and re-encoding if the path continues.

It does not count entanglement storage or distribution and does not describe a
fully coherent quantum-law payload.

---

## 17. First-principles implications

### Exact equality and approximate closeness are different quotients

Exact equivalence groups only identical law tensors. Approximation introduces a
metric geometry in which several nearby tensors may share one predictor.

### Lower and upper bounds solve different tasks

- a packing says how many states no renderer can beat;
- a cover gives one renderer that works;
- equality identifies the optimum;
- a gap is a real open interval, not permission to choose the preferred number.

### Query schedules shape observable geometry

The same conditional laws may be close under an average query distribution and
far under a worst-query metric. A resource claim must state which query policy
is protected.

### Arbitrary predictor laws can be more efficient than remembered worlds

An approximate renderer need not select one existing target history as its
representative. It may use an interpolating law, as the Bernoulli midpoint
example shows.

### Network topology enters after predictive compression

The state problem determines an index size. The network problem determines
whether that index crosses the cut. Conflating these layers obscures both.

### None of this detects simulation

An ordinary stochastic physical model, a distributed service, and a
hypothetical simulator can all satisfy the same law, cover, and cut bounds. The
results constrain a declared internal architecture but do not distinguish its
metaphysical interpretation.

---

## 18. What researchers can easily miss

### A packing is not a code implementation

Pairwise separation proves a lower bound. It does not specify predictor centers,
assignments, sampling, or network routing.

### A target cover is not always optimal

Existing target laws are convenient centers, but interpolation can reduce the
state count.

### Average-query error can hide a catastrophic rare-query error

Weighted TV should not be reported as worst-query accuracy. Both metrics are
implemented separately.

### Exact float equality is a declared-table statement

Exact stochastic classes use equality of the normalized probability vectors
supplied to the finite model. Empirical estimates require uncertainty regions
and hypothesis testing rather than literal floating-point equality.

### One-sink cover routing is not multi-sink stochastic network coding

Several sinks may require different center assignments or law families. Shared
upstream compression requires a separate joint-demand model.

### Better centers need not be physical hidden states

A predictor law can be operationally valid even if no hidden record in the
chosen family induces it. Whether such interpolation is physically admissible
must be stated by the model.

---

## 19. Nonclaims

- The finite categorical tables are declared models, not empirical estimates of
  the universe.
- Exact equivalence uses equality of the supplied normalized probability
  vectors.
- The weighted TV identity assumes the same exogenous query marginal under both
  records and retains the query identity.
- Worst-query and weighted-query distortion are not interchangeable.
- The packing lower bound permits arbitrary predictor centers.
- The target-centered cover is constructive but can be conservative.
- Exact minimum target-centered cover and maximum packing searches are capped at
  bounded family sizes.
- The general certificate's `unresolved` status does not mean infeasible; it
  means the implemented lower and upper bounds do not meet.
- The exact Bernoulli greedy theorem is one-dimensional and does not extend
  automatically to multidimensional categorical families.
- The routed approximate construction carries a classical center index rather
  than an arbitrary quantum state.
- Entanglement-assisted capacity excludes entanglement distribution and storage
  costs.
- Internal predictive bits, qubits, covers, and min-cuts are not parent-hardware
  or energy bounds.
- Stochastic equivalence, metric entropy, interpolation, and network routing are
  not evidence that reality is simulated.

---

## 20. Next research targets

1. Solve arbitrary-center covering for small categorical simplices using exact
   linear or convex programming certificates.
2. Add finite distributional uncertainty sets so empirical laws are not treated
   as exact tables.
3. Derive rate-distortion bounds under a source prior rather than worst-record
   covering.
4. Add stochastic query policies that adapt to previous outcomes.
5. Combine progressive query hints with stochastic cover refinement at each
   stage.
6. Extend the constructive cover-index network theorem to several sinks with a
   declared joint demand.
7. Add noisy edges and strong-data-processing contraction of KL and TV.
8. Study stochastic logical observables in error-correcting code families.
9. Replace target-centered set cover with certified arbitrary-center upper
   bounds in higher-dimensional probability spaces.
10. Lower-bound the update work needed when a changing hidden record crosses
    cover-cell boundaries.
