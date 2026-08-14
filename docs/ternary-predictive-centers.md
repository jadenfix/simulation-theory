# Exact ternary predictive centers and network capacity

## Scope

The stochastic predictive-cover lane computes two general finite bounds:

\[
\mathsf P_{2\epsilon}
\le
M_\epsilon^*
\le
\mathsf C^{\mathrm{target}}_\epsilon.
\]

The packing is a converse. The target-centered cover is a working renderer, but
it can be conservative because an optimal predictor law need not be one of the
target laws.

For Bernoulli distributions, total variation is ordinary distance on the
interval, so arbitrary centers and the exact minimum cover can be solved by
greedy interval covering.

This note moves one dimension higher. It considers a single future query with
three possible outcomes and proves an exact arbitrary-center theory for finite
target families in the two-dimensional probability simplex:

1. ternary total variation is the maximum coordinate difference;
2. common-center feasibility reduces to three intervals and one simplex-sum
   condition;
3. the one-state minimax radius has a closed water-filling formula;
4. exact minimum arbitrary-center covers are computable by finite subset
   enumeration and exact set cover;
5. the resulting cover-index size gives exact one-sink network capacity for the
   declared finite problem.

This is a special property of the three-outcome simplex. It is not silently
promoted to arbitrary categorical dimension.

All results concern declared internal probability laws and query interfaces.
They are not evidence that reality is simulated and do not identify model bits,
qubits, centers, or network capacities with parent-universe hardware, energy,
or spacetime.

---

## 1. The ternary probability simplex

A ternary law is

\[
p=(p_1,p_2,p_3),
\qquad
p_j\ge0,
\qquad
p_1+p_2+p_3=1.
\]

The set of all such laws is the simplex

\[
\Delta_2.
\]

Let

\[
\mathcal P
=\{p^{(1)},\ldots,p^{(N)}\}
\subseteq\Delta_2
\]

be a finite target family.

A predictive state is allowed to use any center

\[
c\in\Delta_2,
\]

not merely one of the target laws. Once the future query occurs, the renderer
samples one of the three outcomes from \(c\).

For total-variation tolerance \(\epsilon\), one state covers target \(p\) when

\[
\operatorname{TV}(p,c)\le\epsilon.
\]

The minimum number of arbitrary ternary centers covering all targets is denoted

\[
M^*_{\epsilon,3}.
\]

---

## 2. Ternary total variation is an infinity norm

Take two ternary laws

\[
p,u\in\Delta_2
\]

and define coordinate differences

\[
d_j=p_j-u_j.
\]

Because both vectors sum to one,

\[
d_1+d_2+d_3=0.
\]

Total variation is

\[
\operatorname{TV}(p,u)
=
\frac12
\left(
|d_1|+|d_2|+|d_3|
\right).
\]

### Zero-sum three-coordinate identity

Among three real numbers summing to zero, either:

- one is nonnegative and two are nonpositive; or
- two are nonnegative and one is nonpositive.

In the first case, the positive coordinate equals the sum of the magnitudes of
the two negative coordinates. It is therefore the largest absolute coordinate,
and

\[
\frac12\sum_j|d_j|
=d_{\mathrm{positive}}
=\max_j|d_j|.
\]

The second case is identical after changing signs: the magnitude of the one
negative coordinate equals the sum of the two positive coordinates and is the
largest absolute value.

Therefore

\[
\boxed{
\operatorname{TV}(p,u)
=
\max_{j\in\{1,2,3\}}
|p_j-u_j|.
}
\]

So the TV ball around a ternary target is an axis-aligned cube in three
coordinates, intersected with the plane whose coordinates sum to one.

### Dimensional boundary

This identity is special to three outcomes. For four zero-sum coordinates,
half the L1 norm need not equal the largest absolute coordinate. The later box
and interval arguments therefore require a separate derivation in higher
categorical dimension.

---

## 3. One common epsilon-center

Let a nonempty target cluster be

\[
A\subseteq\mathcal P.
\]

A center \(c\in\Delta_2\) covers every target in \(A\) exactly when

\[
|p_j-c_j|\le\epsilon
\qquad
\forall p\in A,\quad j=1,2,3.
\]

For coordinate \(j\), define the target extrema

\[
M_j(A)=\max_{p\in A}p_j,
\qquad
m_j(A)=\min_{p\in A}p_j.
\]

Every common center must satisfy

\[
M_j(A)-\epsilon
\le c_j\le
m_j(A)+\epsilon.
\]

Intersecting with the simplex coordinate bounds gives

\[
\boxed{
L_j(A,\epsilon)
=
\max\{0,M_j(A)-\epsilon\},
}
\]

and

\[
\boxed{
U_j(A,\epsilon)
=
\min\{1,m_j(A)+\epsilon\}.}
\]

The candidate center must lie in the coordinate box

\[
L_j\le c_j\le U_j
\]

and satisfy

\[
\sum_jc_j=1.
\]

### Interval-sum lemma

For finite coordinate intervals

\[
[L_1,U_1],\ldots,[L_d,U_d],
\]

there exists a vector \(c\) with

\[
c_j\in[L_j,U_j]
\]

and

\[
\sum_jc_j=T
\]

if and only if

\[
L_j\le U_j\quad\forall j
\]

and

\[
\sum_jL_j\le T\le\sum_jU_j.
\]

Necessity is immediate. For sufficiency, start at \(c=L\). The remaining mass
is

\[
R=T-\sum_jL_j\ge0.
\]

The total unused capacity is

\[
\sum_j(U_j-L_j)
=
\sum_jU_j-\sum_jL_j
\ge R.
\]

Distribute \(R\) across coordinates without exceeding each unused capacity.
The resulting vector lies in every interval and has sum \(T\).

### Exact common-center theorem

Applying the lemma with \(T=1\) gives:

\[
\boxed{
A\text{ has one ternary }\epsilon\text{-center}
}
\]

if and only if

\[
\boxed{
L_j(A,\epsilon)\le U_j(A,\epsilon)
\quad\forall j
}
\]

and

\[
\boxed{
\sum_jL_j(A,\epsilon)\le1
\le
\sum_jU_j(A,\epsilon).}
\]

This is an exact finite feasibility criterion, not a numerical relaxation.

### Constructive center

The implementation starts at

\[
c=L
\]

and distributes

\[
1-\sum_jL_j
\]

of remaining mass in coordinate order, never exceeding \(U_j\). The resulting
center is then independently checked against every target through the exact
ternary-TV identity.

---

## 4. Exact one-state minimax radius

For a fixed target family \(A\), define the best one-state radius

\[
r^*(A)
=
\min_{c\in\Delta_2}
\max_{p\in A}
\operatorname{TV}(p,c).
\]

The common-center theorem says that radius \(r\) is feasible exactly when three
classes of inequalities hold.

### Coordinate overlap

Each coordinate interval must be nonempty:

\[
M_j-r\le m_j+r.
\]

Therefore

\[
\boxed{
r\ge\frac{M_j-m_j}{2}
\quad\forall j.}
\]

Define

\[
r_{\mathrm{range}}
=
\max_j\frac{M_j-m_j}{2}.
\]

### Lower-bound mass

The sum of lower bounds is

\[
\sum_j\max(0,M_j-r).
\]

It must not exceed one:

\[
\sum_j\max(0,M_j-r)\le1.
\]

For a nonnegative vector \(a\) and budget \(B\), define the water-filling
threshold

\[
\boxed{
\theta(a;B)
=
\inf\left\{
r\ge0:
\sum_j\max(0,a_j-r)\le B
\right\}.}
\]

Then the lower-mass requirement is

\[
r\ge\theta(M;1).
\]

### Upper-bound mass

The upper bounds must supply at least one unit:

\[
\sum_j\min(1,m_j+r)\ge1.
\]

Using

\[
\min(1,m_j+r)
=
1-\max(0,1-m_j-r),
\]

this is equivalent to

\[
\sum_j\max(0,1-m_j-r)\le2.
\]

Therefore

\[
r\ge\theta(1-m;2).
\]

### Closed minimax formula

All feasibility conditions are monotone in \(r\). Combining them gives

\[
\boxed{
r^*(A)
=
\max\left\{
\max_j\frac{M_j-m_j}{2},
\theta(M;1),
\theta(1-m;2)
\right\}.}
\]

At this radius, the interval-sum construction returns a minimax center.

### Finite water-filling computation

Sort

\[
a_{(1)}\ge\cdots\ge a_{(d)}.
\]

If the first \(k\) coordinates remain active, the threshold equation is

\[
\sum_{j=1}^k(a_{(j)}-r)=B,
\]

so

\[
\boxed{
r_k
=
\frac{\sum_{j=1}^ka_{(j)}-B}{k}.}
\]

The valid active set is the first \(k\) for which

\[
r_k\ge a_{(k+1)},
\]

with \(a_{(d+1)}=0\). The implementation evaluates this finite formula rather
than using a generic optimizer.

---

## 5. Exact arbitrary-center covering

We now seek the minimum number of arbitrary ternary centers covering all target
laws:

\[
M^*_{\epsilon,3}.
\]

The center space is continuous, but the common-center criterion reduces the
problem to a finite combinatorial search.

### Every predictor induces a feasible cluster

Take any valid predictive center \(c\). Let

\[
A(c)
=
\left\{
p\in\mathcal P:
\operatorname{TV}(p,c)\le\epsilon
\right\}.
\]

The set \(A(c)\) is a feasible cluster by definition: center \(c\) covers it.

### Every feasible cluster has a canonical center

Conversely, for every nonempty subset

\[
A\subseteq\mathcal P
\]

that passes the interval-sum criterion, the constructive procedure returns a
canonical center

\[
c_A.
\]

It covers every member of \(A\), and may also cover additional targets.

### Finite reduction theorem

Enumerate every nonempty target subset. Retain the canonical center of each
feasible subset and its actual coverage set.

Consider an optimal arbitrary-center solution

\[
c_1,\ldots,c_k.
\]

Assign every target to one center that covers it, producing feasible clusters

\[
A_1,\ldots,A_k.
\]

For each \(A_j\), the enumerated canonical center \(c_{A_j}\) covers at least
\(A_j\). Replacing every optimal center by its canonical cluster center
therefore gives a cover using no more than \(k\) enumerated candidates.

The reverse inequality is immediate because every enumerated candidate is an
admissible arbitrary ternary law.

Thus:

\[
\boxed{
M^*_{\epsilon,3}
=
\text{minimum set-cover size over canonical feasible-subset centers}.}
\]

This is an exact unrestricted arbitrary-center result, not merely a
packing-cover bracket.

---

## 6. Finite exact algorithm

For \(N\) target laws, the bounded checker performs:

1. Enumerate the \(2^N-1\) nonempty subsets.
2. Apply the interval-sum feasibility theorem.
3. Construct one canonical center for each feasible subset.
4. Recompute the complete target set covered by that center.
5. Deduplicate equal coverage masks.
6. Remove every mask strictly contained in another candidate mask.
7. Solve the remaining finite minimum set-cover problem by branch and bound.
8. Assign every record to one selected center and verify its TV error.

### Dominance removal

If candidate center \(c_1\) covers a strict subset of the targets covered by
\(c_2\), then \(c_1\) is never needed in an unweighted minimum-state objective.
The implementation removes such candidates with a superset zeta transform over
bit masks.

### Exact set-cover search

A greedy cover supplies an initial upper bound. The exact search then:

- selects an uncovered target having the fewest available centers;
- branches only over centers that cover that target;
- tries centers with larger immediate coverage first;
- uses the largest available new coverage to derive an optimistic lower bound;
- removes symmetric reorderings of already tried centers.

The search is capped at a declared finite target count. It is not presented as
a polynomial-time scalable algorithm.

### Independent checker

The tests independently solve random bounded instances by subset dynamic
programming over partitions into feasible clusters. The DP and the set-cover
implementation agree across deterministic seeded families.

---

## 7. Packing, target covers, and arbitrary centers

For the same ternary target family, three state counts can differ:

\[
\mathsf P_{2\epsilon}
\le
M^*_{\epsilon,3}
\le
\mathsf C^{\mathrm{target}}_\epsilon.
\]

- \(\mathsf P_{2\epsilon}\) is the strict packing converse.
- \(M^*_{\epsilon,3}\) is the exact arbitrary-center optimum from this note.
- \(\mathsf C^{\mathrm{target}}_\epsilon\) restricts centers to supplied target
  laws.

The exact ternary solver therefore closes both gaps for this special geometry:

- it identifies when the packing lower bound is loose;
- and it quantifies exactly how conservative target-centered rendering is.

---

## 8. The three simplex vertices

Consider the three deterministic outcome laws

\[
e_1=(1,0,0),
\qquad
e_2=(0,1,0),
\qquad
e_3=(0,0,1).
\]

Every pair has total variation one.

### One-state minimax radius

The extrema are

\[
M=(1,1,1),
\qquad
m=(0,0,0).
\]

The coordinate half-range is \(1/2\). The lower-mass water-filling threshold
solves

\[
3(1-r)=1,
\]

so

\[
r=\frac23.
\]

The upper-mass threshold is \(1/3\), so the maximum is

\[
\boxed{r^*=\frac23.}
\]

The common center is the uniform law

\[
\boxed{c^*=\left(\frac13,\frac13,\frac13\right).}
\]

Indeed,

\[
\operatorname{TV}(e_j,c^*)
=\frac23
\qquad
j=1,2,3.
\]

### Exact arbitrary-center phase diagram

If

\[
\epsilon<\frac12,
\]

one center cannot cover two vertices, because their pairwise distance one is
strictly greater than \(2\epsilon\). Thus three states are necessary and
sufficient.

At

\[
\epsilon=\frac12,
\]

a midpoint such as

\[
\left(\frac12,\frac12,0\right)
\]

covers two vertices. A second center covers the third. One center is still
impossible because the minimax radius is \(2/3\). Thus exactly two states are
needed throughout

\[
\frac12\le\epsilon<\frac23.
\]

At

\[
\epsilon\ge\frac23,
\]

the uniform center covers all three.

Therefore

\[
\boxed{
M^*_{\epsilon,3}
=
\begin{cases}
3,&0\le\epsilon<1/2,\\
2,&1/2\le\epsilon<2/3,\\
1,&\epsilon\ge2/3.
\end{cases}}
\]

The fixed-length predictive bits are consequently

\[
\boxed{
B^*_{\epsilon,3}
=
\begin{cases}
2,&0\le\epsilon<1/2,\\
1,&1/2\le\epsilon<2/3,\\
0,&\epsilon\ge2/3.
\end{cases}}
\]

### Target-centered conservatism

Every target vertex is distance one from every other target vertex. A
target-centered cover therefore needs all three target laws for every

\[
\epsilon<1.
\]

At \(\epsilon=2/3\), the exact unrestricted state count is one, while the
minimum target-centered cover still has three states:

\[
\boxed{
M^*_{2/3,3}=1
<
\mathsf C^{\mathrm{target}}_{2/3}=3.}
\]

This is a larger version of the Bernoulli endpoint example and shows why
interpolating stochastic centers are a structural resource rather than a
numerical convenience.

---

## 9. Exact one-sink network capacity

Let an integer-capacity directed network connect source \(s\) to sink \(t\).
The source knows which target ternary law applies. The sink must later sample an
\(\epsilon\)-accurate law.

Let

\[
M^*=M^*_{\epsilon,3}
\]

be the exact arbitrary-center state count and

\[
B^*=\lceil\log_2M^*\rceil
\]

its fixed-length center-index bits.

Under a declared capacity multiplier

\[
\kappa=
\text{exact classical index bits per network unit},
\]

the required units are

\[
\boxed{
U^*
=
\left\lceil\frac{B^*}{\kappa}\right\rceil.}
\]

### Necessity

If a source-sink cut carries fewer than \(B^*\) index bits, it induces fewer
than \(M^*\) sink-side predictive states. That contradicts the exact minimum
arbitrary-center cover theorem.

### Sufficiency

The source computes the selected center index from the exact cover assignment.
If the min-cut has at least \(U^*\) units, integral max flow routes the index to
the sink. After the query, the sink samples from the reconstructed center law.

Therefore

\[
\boxed{
\text{ternary approximate one-sink feasibility}
\iff
C_{\min}(s,t)
\ge
\left\lceil
\frac{\lceil\log_2M^*_{\epsilon,3}\rceil}{\kappa}
\right\rceil.}
\]

Unlike the general stochastic packing/target-cover certificate, there is no
`unresolved` region here: the arbitrary-center state optimum is exact.

### Carrier interpretations

The same explicit accounting boundary applies:

\[
\kappa=1
\]

for classical bits or unassisted qubits carrying a classical center index, and

\[
\kappa=2
\]

for transmitted qubits under the declared edge-local dense-coding model.
Preshared entanglement storage and distribution are not included in the
transmitted-unit count.

---

## 10. Finite certificate contents

For a bounded ternary family, the checker returns:

- the exact selected arbitrary centers;
- the exact target-to-center assignment;
- the minimum state count;
- the fixed-length predictive bits;
- optional packing and target-centered comparison sizes;
- the exact network-unit requirement under a declared multiplier;
- the source-sink min-cut;
- and routed paths when the network is feasible.

The test suite checks:

- ternary TV against generic categorical TV;
- common-center feasibility and construction;
- the minimax formula on simplex vertices, edges, and repeated points;
- the exact vertex phase diagram;
- agreement with independent subset-partition dynamic programming;
- deterministic stochastic-family embedding;
- target-centered and packing comparisons;
- classical and two-bit-capacity network routing;
- validation and bounded-search caps.

A finite certificate validates one declared instance. It is not an empirical
measurement and is not a substitute for the symbolic theorem.

---

## 11. First-principles implications

### Approximation can create laws absent from the target family

The optimal center may be an interpolating distribution that no hidden record
produces. An approximate renderer need not “remember one possible world”; it
must retain one law adequate for future prediction.

### Exact covering depends on probability geometry

Bernoulli laws reduce to intervals. Ternary laws reduce to boxes intersecting a
simplex. Higher outcome counts need new geometric or optimization machinery.
There is no dimension-free shortcut.

### Predictive-state cardinality and network topology remain separate

The arbitrary-center cover determines the minimum index. The network min-cut
determines whether that index reaches the observer. Neither step alone answers
the full architecture question.

### Target-centered constructions should be labeled honestly

They are often easy to audit and route, but can be far from optimal. Reporting
them as exact predictive-state requirements would overstate the burden.

### The theorem constrains only the declared interface

An exact or approximate simulator can satisfy the theorem by retaining and
routing the appropriate center index. Ordinary stochastic systems can do the
same. Nothing in the geometry distinguishes simulation from non-simulation.

---

## 12. Nonclaims

- The result covers one finite query with exactly three outcomes.
- The ternary TV infinity-norm identity is not asserted for four or more
  outcomes.
- Predictor centers are allowed to be arbitrary ternary laws; a physical model
  that forbids interpolation has a different cover problem.
- Exact target probabilities are declared inputs, not empirical estimates.
- The exhaustive arbitrary-center cover search is capped at a bounded number of
  targets.
- The minimax formula concerns worst-target TV for one center, not source-prior
  average distortion.
- The one-sink network theorem routes a classical center index.
- Multi-sink, adaptive-query, and coherent quantum-law payloads require separate
  models.
- Dense-coding capacity does not count entanglement creation, storage, or
  distribution.
- Internal centers, bits, qubits, and cuts are not parent-universe hardware,
  energy, mass, or spacetime-volume bounds.
- Ternary interpolation and exact covering are not evidence that reality is
  simulated.

---

## 13. Next research targets

1. Extend arbitrary-center feasibility to four-outcome categorical laws through
   certified linear programming.
2. Enumerate jointly coverable clusters in higher-dimensional simplices.
3. Add exact rational certificates rather than floating-point tolerances for
   rational input laws.
4. Derive source-prior rate-distortion functions for ternary targets.
5. Add uncertainty regions around estimated target probabilities.
6. Combine ternary center refinement with progressive query revelation.
7. Share center indices across multiple sinks with heterogeneous future laws.
8. Add noisy edge channels and distinguishability contraction.
9. Lower-bound update work when a changing target moves between optimal cover
   cells.
10. Connect ternary stochastic centers to physical three-outcome measurements
    without treating the mathematical construction as evidence for simulation.
