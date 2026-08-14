# Predictive-equivalence classes and causal-network min-cuts

## Scope

The earlier causal-cut results use one particular future-query family: a hidden
binary record is fixed, and a later observer may request any one coordinate.
That interface forces the record to remain recoverable because every pair of
records differs on some possible future query.

But the full record is not always the right object. A future interface might
ask only:

- one global parity;
- a bounded collection of checksums;
- membership in one of several observable classes;
- a logical code observable;
- or any other finite family of functions.

The correct first-principles question is therefore:

> Which hidden records induce genuinely different future observable laws under
> the queries that remain possible at the sink?

This note defines those predictive-equivalence classes and proves an exact
single-sink network theorem:

> A finite directed causal network can answer every later deterministic query
> exactly if and only if its source-sink min-cut can carry a fixed-length label
> for the predictive-equivalence class.

The result generalizes one-way INDEX without silently transmitting information
that no allowed future query can reveal.

All statements concern declared finite internal interfaces. They do not prove
that reality is simulated and do not identify bits, qubits, or edge capacities
with hardware, energy, or spacetime resources in an unknown parent substrate.

---

## 1. Finite deterministic future-query families

Let

\[
\mathcal X=\{x_1,\ldots,x_N\}
\]

be a finite hidden-record family, and let

\[
\mathcal Q=\{q_1,\ldots,q_r\}
\]

be the set of future queries that remain allowed.

Each query has a deterministic outcome function

\[
f_q:\mathcal X\to\mathcal Y_q.
\]

The complete future-query signature of record \(x\) is

\[
\boxed{
\sigma(x)
=
\bigl(f_{q_1}(x),\ldots,f_{q_r}(x)\bigr).
}
\]

Two records are **exactly predictively equivalent** when every allowed future
query produces the same outcome:

\[
\boxed{
x\sim_{\mathcal Q}x'
\iff
\sigma(x)=\sigma(x').}
\]

Let

\[
K
=
|\mathcal X/\!\sim_{\mathcal Q}|
=
|\{\sigma(x):x\in\mathcal X\}|
\]

be the number of predictive-equivalence classes.

The repository represents a family by its finite records, named queries, and
signature table. The signature table is the operational object: two underlying
states may be physically or mathematically different while belonging to one
predictive class if the declared future interface cannot separate them.

---

## 2. Exact predictive-state cardinality

Suppose an encoder maps the hidden record to a finite state

\[
E:\mathcal X\to\mathcal M,
\]

before the future query is known. A decoder must answer

\[
D(E(x),q)=f_q(x)
\]

for every record and every allowed query.

### Lower bound

Assume

\[
E(x)=E(x').
\]

Then the decoder receives the same state for both records. For every query
\(q\), it must return one common answer. Therefore exact correctness requires

\[
f_q(x)=f_q(x')
\qquad
\forall q\in\mathcal Q.
\]

Thus

\[
E(x)=E(x')
\implies
x\sim_{\mathcal Q}x'.
\]

Every encoder state may contain records from at most one predictive-equivalence
class. Hence

\[
\boxed{|\mathcal M|\ge K.}
\]

A fixed-length binary state therefore needs at least

\[
\boxed{B=\lceil\log_2K\rceil}
\]

bits.

### Matching upper bound

Assign one integer label to each predictive class. Send the class label. The
decoder stores one signature per class and returns the component associated
with the requested query.

This uses exactly

\[
\lceil\log_2K\rceil
\]

fixed-length bits, padding unused codewords when \(K\) is not a power of two.
Therefore

\[
\boxed{
\text{minimum exact predictive-state bits}
=
\lceil\log_2K\rceil.
}
\]

This theorem identifies the minimal future-relevant state. It does not require
transmitting the full hidden record, its generative history, or a dense physical
state representation.

### Zero-error randomization

Shared randomness independent of the record does not reduce the zero-error
cardinality. Condition on any seed used with positive probability. The
seed-conditioned encoder must still avoid collisions between different
predictive classes. Randomness can choose among valid class encodings but cannot
make two incompatible signatures share one exact state.

---

## 3. Coordinate queries versus parity queries

The importance of the query family can be seen on

\[
\mathcal X=\{0,1\}^m.
\]

### Every coordinate remains queryable

If

\[
f_i(x)=x_i,
\qquad i=1,\ldots,m,
\]

then every pair of distinct records differs on at least one query. Thus

\[
K=2^m
\]

and

\[
\boxed{B=m.}
\]

This recovers the exact INDEX lower bound.

### Only total parity remains queryable

If the only query is

\[
f(x)=x_1\oplus\cdots\oplus x_m,
\]

then all even-parity records share one signature and all odd-parity records
share the other. Therefore

\[
K=2
\]

and

\[
\boxed{B=1.}
\]

The hidden record still contains \(m\) bits, but the declared future interface
contains only one predictive bit.

### Several linear parity queries

Let masks \(a_1,\ldots,a_r\in\mathbb F_2^m\) define

\[
f_j(x)=a_j\cdot x\pmod2.
\]

The signature map is the linear transformation

\[
x\mapsto Ax.
\]

If the mask matrix has rank \(\rho\), its image contains exactly

\[
2^\rho
\]

signatures. Hence

\[
\boxed{K=2^\rho,
\qquad
B=\rho.}
\]

This is the linear-algebraic version of predictive compression: only the rank
of the observable parity family matters, not the raw number of hidden bits or
the number of possibly redundant query descriptions.

The repository enumerates bounded coordinate and parity families and checks the
resulting class counts directly.

---

## 4. A finite causal-capacity network

Let

\[
G=(V,E)
\]

be a finite directed acyclic graph. A source node \(s\) initially knows the
hidden record. A sink node \(t\) must answer a query chosen only after all
record-dependent information has traversed the network.

Each directed edge \(e\) has a positive integer capacity

\[
c_e\in\mathbb N.
\]

For the classical interpretation, one capacity unit carries one exact binary
symbol. Intermediate nodes may compute arbitrary deterministic functions of the
messages they receive and forward messages subject to edge capacities.

For a source-sink cut \(S\subset V\), with

\[
s\in S,
\qquad
t\notin S,
\]

define its capacity

\[
C(S)
=
\sum_{(u,v)\in E:\,u\in S,\,v\notin S}c_{uv}.
\]

The min-cut is

\[
\boxed{
C_{\min}(s,t)
=
\min_{S:s\in S,t\notin S}C(S).
}
\]

Because the graph is acyclic, it can also be read as a causal computation
network: messages flow only from earlier to later nodes in a topological order.
The cut theorem itself is information-theoretic and does not depend on a
particular physical embedding.

---

## 5. Exact predictive min-cut lower bound

Let the sink's future interface have \(K\) predictive classes and

\[
B=\lceil\log_2K\rceil.
\]

Consider any source-sink cut of capacity \(C\) classical bits.

Condition on all record-independent randomness and on all information already
available on the sink side of the cut. The complete record-dependent influence
that can cross from the source side to the sink side has at most

\[
2^C
\]

possible transcripts.

If

\[
2^C<K,
\]

two different predictive classes must induce the same cut transcript. Every
node on the sink side then evolves identically for those two classes. The sink
receives the same final state, yet some allowed query requires different
answers. Exact correctness is impossible.

Therefore every source-sink cut must satisfy

\[
2^C\ge K,
\]

or

\[
\boxed{C\ge\lceil\log_2K\rceil.}
\]

Taking the minimum over cuts gives

\[
\boxed{
C_{\min}(s,t)
\ge
B.
}
\]

This is the predictive-class cut-set bound.

### Why the theorem uses classes rather than records

A cut need not preserve distinctions that no future query at the sink can
observe. If two records have the same signature, merging them creates no future
error. Conversely, every distinction between signatures must survive at least
one source-sink cut in a form the sink can recover.

The right cut payload is therefore a sufficient statistic for the future query
family, not necessarily the source record itself.

---

## 6. Single-sink sufficiency by integral max flow

The lower bound is exact for one sink with integer capacities.

Assume

\[
C_{\min}(s,t)
\ge B.
\]

By the integral max-flow/min-cut theorem, the network has an integer flow of
value at least \(B\). Such a flow decomposes into directed source-sink paths
with integer multiplicities.

The source computes the \(B\)-bit predictive-class label and routes its bits
along the flow paths. Intermediate nodes need only forward, split, and
recombine fixed-length bit blocks. The sink reconstructs the class label and
therefore the complete signature. After the future query is revealed, it
returns the corresponding signature component.

Thus

\[
C_{\min}(s,t)\ge B
\]

is sufficient.

Combining necessity and sufficiency gives the exact theorem:

\[
\boxed{
\text{exact single-sink feasibility}
\iff
C_{\min}(s,t)
\ge
\lceil\log_2K\rceil.
}
\]

The repository implements:

- directed-acyclic-network validation;
- exact integer Edmonds-Karp max flow;
- the residual min-cut certificate;
- decomposition of a sufficient flow into routed paths;
- and an exact predictive-network certificate containing required units,
  available min-cut units, and the routed paths.

### What is and is not being optimized

The theorem minimizes exact information capacity across the network. It does
not minimize:

- latency;
- number of arithmetic operations;
- total edge usage;
- energy;
- robustness to edge failures;
- or the cost of computing the class label at the source.

Those are separate architectural objectives.

---

## 7. Capacity units and quantum interpretations

The implementation permits a declared multiplier

\[
\kappa=
\text{exact classical payload bits per edge-capacity unit}.
\]

Then a query family requiring \(B\) predictive bits needs

\[
\boxed{
U
=
\left\lceil\frac B\kappa\right\rceil
}
\]

network units.

### Classical bit edges

For ordinary classical binary channels,

\[
\kappa=1.
\]

### Unassisted transmitted qubits

A noiseless unassisted qubit can carry one exact classical bit using two
orthogonal states. Exact classical payload therefore uses

\[
\kappa=1.
\]

The continuum of amplitudes does not produce more exactly retrievable
classical class labels.

### Entanglement-assisted transmitted qubits

If each directed quantum edge has receiver-side Bell pairs established
independently of the later hidden record, dense coding permits one transmitted
qubit to carry two exact classical bits. Under this explicit edge-local
assistance and decode/re-encode assumption,

\[
\kappa=2.
\]

The exact unit requirement becomes

\[
\boxed{
U_{\mathrm{EA}}
=
\left\lceil
\frac{\lceil\log_2K\rceil}{2}
\right\rceil.
}
\]

This accounting counts transmitted qubit units. It does not count the creation,
distribution, storage, or refresh cost of the preshared entanglement. It also
does not claim that arbitrary quantum network coding problems reduce to a
scalar multiplier. The factor-two model applies to exact classical labels with
edge-local dense-coding resources and intermediate classical recovery.

---

## 8. Exact deterministic predictive geometry

Now equip the finite query set with an exogenous probability distribution

\[
w_q\ge0,
\qquad
\sum_{q\in\mathcal Q}w_q=1.
\]

For hidden record \(x\), define the joint future law over query and outcome:

\[
P_x(q,y)
=
w_q\mathbf1\{y=f_q(x)\}.
\]

Take two records \(x,x'\). For a query on which their outcomes agree, the two
conditional laws are identical. For a query on which they disagree, the two
conditional point masses have disjoint support and contribute exactly \(w_q\)
to total variation.

Therefore

\[
\boxed{
\operatorname{TV}(P_x,P_{x'})
=
\sum_{q\in\mathcal Q}
 w_q
 \mathbf1\{f_q(x)\ne f_q(x')\}.
}
\]

This is a weighted Hamming metric on query signatures.

For uniform coordinate queries on \(m\)-bit records, it reduces to

\[
\operatorname{TV}(P_x,P_{x'})
=
\frac{d_H(x,x')}{m}.
\]

For parity or other query families, the Hamming comparison occurs in signature
space rather than raw record space.

This identity makes the observable geometry explicit. It avoids inferring
predictive distance from the dimension or encoding length of the underlying
record.

---

## 9. Approximate predictive packing cut bound

Let

\[
\mathcal P\subseteq\mathcal X
\]

be a family such that

\[
\operatorname{TV}(P_x,P_{x'})>2\epsilon
\qquad
\forall x\ne x'\in\mathcal P.
\]

Suppose one state on the sink side of a cut approximated both \(P_x\) and
\(P_{x'}\) within total variation \(\epsilon\). By the triangle inequality,

\[
\operatorname{TV}(P_x,P_{x'})
\le
\operatorname{TV}(P_x,\widehat P)
+
\operatorname{TV}(\widehat P,P_{x'})
\le2\epsilon,
\]

contradicting the strict separation.

Thus every member of \(\mathcal P\) needs a distinct approximate predictive
state. If

\[
P=|\mathcal P|,
\]

then every cut must carry at least

\[
\boxed{
B_\epsilon
=
\lceil\log_2P\rceil
}
\]

bits, or

\[
\boxed{
U_\epsilon
=
\left\lceil
\frac{\lceil\log_2P\rceil}{\kappa}
\right\rceil
}
\]

capacity units under multiplier \(\kappa\).

The repository constructs the finite separation graph whose vertices are
records and whose edges join pairs at distance greater than \(2\epsilon\). An
exact bounded maximum-clique search returns the largest predictive packing for
small families.

### Necessary, not generally sufficient

The packing number is a lower bound. A network meeting this many bits is not
automatically sufficient to approximate the entire family within \(\epsilon\).
A matching upper bound would require an explicit covering, quantizer, or
rate-distortion code together with a decoder and network implementation.

The repository therefore reports approximate packing cuts only as necessary
conditions.

---

## 10. Finite coordinate packing example

Take all four-bit records and uniformly random coordinate queries. The distance
is

\[
\operatorname{TV}(P_x,P_{x'})
=
\frac{d_H(x,x')}{4}.
\]

At

\[
\epsilon=0.2,
\]

a valid packing requires

\[
\frac{d_H(x,x')}{4}>0.4,
\]

so distinct codewords must have Hamming distance at least two.

The largest binary length-four code with minimum distance two has eight
codewords, for example the even-parity code. Therefore

\[
P=8
\]

and the cut lower bound is

\[
\boxed{B_\epsilon=3\text{ bits}.}
\]

The exact maximum-clique checker independently recovers packing size eight.
This bounded example tests the complete chain:

\[
\text{physical query law}
\to
\text{TV geometry}
\to
\text{packing}
\to
\text{cut capacity}.
\]

---

## 11. Several sinks

Suppose one source feeds sinks

\[
t_1,\ldots,t_L,
\]

and sink \(t_j\) has its own future-query family with

\[
K_j
\]

predictive classes.

Applying the single-sink cut argument separately gives the necessary condition

\[
\boxed{
C_{\min}(s,t_j)
\ge
\left\lceil
\frac{\lceil\log_2K_j\rceil}{\kappa}
\right\rceil
\qquad
\forall j.
}
\]

The repository reports the deficit for each sink independently.

### Why per-sink cuts are not a general multicast theorem

Even when every individual sink min-cut is large enough, shared upstream edges
may create simultaneous-demand conflicts. The source may need to multicast a
common label, send different labels, or satisfy correlated query families.
Routing, replication, and network coding can differ.

Therefore this lane claims only:

- exact necessity for every sink cut;
- exact sufficiency for one sink;
- no generic multi-sink sufficiency result.

A later extension must state the simultaneous sink demands and the coding model
before asserting a multicast theorem.

---

## 12. Predictive network certificate

For a single sink, the finite checker returns:

1. the required number of capacity units;
2. the exact integer max-flow value;
3. the matching min-cut capacity;
4. a decomposition into routed source-sink paths when feasible.

For every routed path, the checker records its node sequence and integer unit
multiplicity. The aggregate routed use of each edge is bounded by the declared
edge capacity.

This certificate is independently inspectable, but its scope remains finite:

- it checks the declared network instance;
- it does not prove a symbolic theorem for all networks by enumeration;
- the general theorem is the mathematical max-flow/min-cut argument;
- and a successful computation is not evidence about an unknown physical
  simulator.

---

## 13. First-principles interpretation

### The record is not the state requirement

The source may contain enormous hidden detail. The cut only needs enough
information to preserve distinctions that the sink's future interface can
still reveal.

### Query design determines effective information

Coordinate queries expose every bit. One parity query exposes one equivalence
bit. A rank-\(\rho\) linear query family exposes \(\rho\) bits. The same hidden
record can therefore produce radically different cut requirements under
different future observations.

### Topology matters after the sufficient statistic is known

The predictive class determines the payload size. The network topology
determines whether that payload can reach the sink. These are separate layers:

\[
\boxed{
\text{query family}
\to
\text{predictive classes}
\to
\text{payload bits}
\to
\text{network min-cut}.
}
\]

### Approximation changes cardinality into geometry

For exact prediction, signatures are either equal or different. Under allowed
error, the relevant object is a metric packing or covering of future laws.
The finite implementation uses total variation and maximum packing, while a
complete asymptotic theory would involve rate distortion, information
complexity, or metric entropy.

### Quantum carriers alter capacity, not the query equivalence relation

The sink's predictive classes are defined by future outcomes. Changing the
communication carrier changes how many capacity units transmit a class label,
but it does not change which hidden records the future query family can
separate.

### An exact simulator can satisfy the theorem

A hypothetical simulator can compute the predictive class and route its label
through a sufficiently capacitated internal network. Ordinary physical systems
and distributed computers can do the same. The theorem constrains one declared
architecture; it does not distinguish simulation from non-simulation.

---

## 14. What researchers can easily miss

### Counting source states can overstate the burden

If the sink can observe only one parity, transmitting all \(m\) source bits is
unnecessary. The exact burden is one predictive bit.

### Counting queries can also overstate the burden

Many named queries may be redundant. The signature image size, not the query
count alone, determines the number of exact classes. Linear parity queries are
controlled by rank.

### A min-cut lower bound requires a future interface

Without specifying what the sink must answer, no payload size is defined. The
same network can be adequate for a parity interface and inadequate for a
coordinate interface.

### Per-sink feasibility does not imply simultaneous multicast feasibility

Several individually adequate cuts may share bottlenecks. A multi-sink claim
needs a demand model and, potentially, network coding.

### Approximate packing is not approximate achievability

A large packing proves many states are necessary. It does not construct a
small cover or a working renderer.

### Capacity units are model assumptions

The values \(\kappa=1\) and \(\kappa=2\) come from declared classical,
unassisted-quantum, and dense-coding interfaces. They are not universal
conversion factors for unknown parent physics.

---

## 15. Nonclaims

- The finite hidden-record family is a declared model and need not represent
  the actual microstate space of the universe.
- Deterministic query outcomes do not cover every stochastic physical
  observation; stochastic extensions require comparing full conditional laws.
- The exact single-sink theorem assumes finite fixed-length class labels and
  integer edge capacities.
- The causal network is directed and acyclic in the implementation.
- Max-flow sufficiency concerns one sink and exact label routing.
- Per-sink min-cuts are necessary but not generally sufficient for simultaneous
  multi-sink demands.
- The approximate packing bound is necessary rather than sufficient.
- The bounded maximum-clique search is capped at small record families.
- Entanglement-assisted capacity assumes appropriate edge-local preshared Bell
  pairs and intermediate recovery or re-encoding.
- Preshared entanglement is not physically free and is not counted by the
  transmitted-qubit multiplier.
- Internal bits, qubits, flows, and cuts are not parent-universe hardware,
  energy, mass, or spacetime-volume bounds.
- Predictive equivalence, max flow, parity compression, and network coding are
  not evidence that reality is simulated.

---

## 16. Next research targets

1. Replace deterministic outcomes by finite stochastic future laws and define
   exact equivalence by equality of conditional distributions.
2. Derive approximate covering and rate-distortion upper bounds to accompany
   packing lower bounds.
3. Generalize from one sink to explicit multicast and multiple-unicast demand
   models.
4. Implement linear network coding certificates for finite fields.
5. Combine progressive query-revelation trees with network cuts at every stage.
6. Allow overlapping query-hint sets and derive submodular or polymatroid
   capacity regions.
7. Add noisy edges and strong-data-processing contraction along causal paths.
8. Add dynamic hidden records and lower-bound update work needed to maintain the
   sink's predictive class.
9. Study latency, path length, and total edge usage in addition to min-cut
   capacity.
10. Connect stabilizer logical-query classes to explicit distributed quantum
    code networks without conflating code distance with communication capacity.
