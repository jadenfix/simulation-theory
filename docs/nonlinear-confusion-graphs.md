# Nonlinear predictive functions and confusion graphs

## Scope

Earlier network lanes encode exact predictive classes as finite-field vectors
and compute linear functions of those vectors. That is powerful but still
assumes the sink's target and side information have a chosen linear
representation.

This note removes that assumption for the finite one-shot zero-error problem.

Let the hidden source state lie in a finite set

\[
X\in\mathcal X.
\]

Before any sink decodes, a common encoder sends one message

\[
M=c(X)
\]

from a finite alphabet \(\mathcal M\).

Sink \(t\):

- already knows side information

  \[
  S_t=s_t(X);
  \]

- needs only the finite target

  \[
  F_t=f_t(X);
  \]

- uses a decoder

  \[
  d_t:\mathcal M\times\mathcal S_t\to\mathcal F_t.
  \]

Exact zero-error recovery requires

\[
 d_t(c(x),s_t(x))=f_t(x)
 \qquad
 \forall x\in\mathcal X,\ \forall t.
\]

The functions \(f_t\) and \(s_t\) may be completely nonlinear and their values
may be arbitrary finite hashable objects. The problem is one-shot,
deterministic, common-message, and zero-error.

The main result is exact:

> The minimum common message alphabet is the chromatic number of a finite
> confusion graph defined by the target and side-information tables.

This is an internal communication theorem for a declared finite interface. It
is not evidence that reality is simulated. Graph colors, states, messages,
side-information values, and bit counts are not parent-universe hardware,
energy, mass, or spacetime.

---

## 1. Confusable source states

Take two distinct source states

\[
x,y\in\mathcal X.
\]

They are **confusable** when some sink sees identical side information but must
produce different answers:

\[
\boxed{
 x\sim_c y
 \iff
 \exists t:\
 s_t(x)=s_t(y)
 \ \text{and}\
 f_t(x)\ne f_t(y).
}
\]

Build a finite simple graph

\[
G=(\mathcal X,E)
\]

with one vertex per source state and edge

\[
\{x,y\}\in E
\iff
x\sim_c y.
\]

This is the **confusion graph**.

Every edge has an explicit witness:

- one sink \(t\);
- one common side-information value;
- two different required targets.

The repository stores and audits one such witness for every edge.

### Why equality of side information matters

If

\[
s_t(x)\ne s_t(y),
\]

sink \(t\) may distinguish the two source states locally even when the common
message is the same. The message does not need to separate distinctions that
are already resolved by the decoder's local side information.

If the side values agree, however, the decoder receives the same pair

\[
(c(x),s_t(x))=(c(y),s_t(y))
\]

whenever \(c(x)=c(y)\). It must then return one output, which cannot equal two
different targets.

---

## 2. Encoder-coloring equivalence theorem

### Theorem

A deterministic encoder

\[
c:\mathcal X\to\mathcal M
\]

admits exact zero-error decoders for all sinks if and only if its message labels
form a proper coloring of the confusion graph:

\[
\boxed{
\{x,y\}\in E
\implies
c(x)\ne c(y).
}
\]

### Necessity

Suppose exact decoders exist. Let \(x,y\) be adjacent. By definition, some
sink \(t\) satisfies

\[
s_t(x)=s_t(y)
\]

and

\[
f_t(x)\ne f_t(y).
\]

If \(c(x)=c(y)\), then the decoder receives the same message and the same side
information in both source states:

\[
(c(x),s_t(x))=(c(y),s_t(y)).
\]

A deterministic decoder must return the same value in both cases, contradicting

\[
f_t(x)\ne f_t(y).
\]

Therefore adjacent vertices receive different messages.

### Sufficiency

Now suppose \(c\) is a proper coloring. For every sink \(t\), message
\(m\), and side-information value \(s\) that actually occurs, define

\[
d_t(m,s)=f_t(x)
\]

for any source state \(x\) satisfying

\[
c(x)=m,
\qquad
s_t(x)=s.
\]

We must show this is well defined.

Suppose two states \(x,y\) satisfy the same message and side value. If their
targets differed, then \(x,y\) would be adjacent in the confusion graph. A
proper coloring would require \(c(x)\ne c(y)\), contradicting the common
message. Hence

\[
f_t(x)=f_t(y).
\]

So every populated decoder cell has one unique target. The resulting decoder
satisfies every source state and sink exactly.

### Consequence

The finite function-computation problem is not merely bounded by graph
coloring. It **is** graph coloring under this exact one-shot deterministic
interface.

The implementation verifies both sides independently:

1. direct edge/message separation;
2. explicit decoder-table construction and full source-state evaluation.

---

## 3. Exact message states and fixed-length bits

Let

\[
\chi(G)
\]

be the chromatic number of the confusion graph.

Every valid encoder is a proper coloring, so it uses at least \(\chi(G)\)
message values. A \(\chi(G)\)-coloring constructs an encoder and the sufficiency
proof constructs its decoders. Therefore:

\[
\boxed{
|\mathcal M|_{\min}=\chi(G).
}
\]

If a fixed-length classical message is used, the minimum number of bits is

\[
\boxed{
 b_{\min}
 =
 \left\lceil\log_2\chi(G)\right\rceil.
}
\]

The state count and bit count are different optimization outputs. For example,
three colors require two fixed-length bits even though one of the four bit
patterns is unused.

This theorem does not address variable-length expected code length under a
source prior. It also does not address repeated block coding, allowed error,
interactive communication, or quantum messages.

---

## 4. Lower and upper certificates

Exact coloring is combinatorial. The repository keeps several certificates
separate.

### Clique lower bound

A clique is a set of pairwise confusable states. Every pair must receive
different messages, so

\[
\boxed{
\omega(G)\le\chi(G),
}
\]

where \(\omega(G)\) is the maximum clique size.

Operationally, a clique is a source-state family in which every pair conflicts
at at least one sink. No two states in the family can share one common message.

### Independent-set lower bound

Each color class is an independent set. If

\[
\alpha(G)
\]

is the maximum independent-set size, one color covers at most \(\alpha(G)\)
vertices. Covering all \(|\mathcal X|\) states therefore needs at least

\[
\boxed{
\chi(G)
\ge
\left\lceil
\frac{|\mathcal X|}{\alpha(G)}
\right\rceil.
}
\]

This can be stronger than the clique bound.

For the five-cycle \(C_5\):

\[
\omega(C_5)=2,
\qquad
\alpha(C_5)=2,
\]

so

\[
\chi(C_5)
\ge
\left\lceil\frac52\right\rceil
=3.
\]

The exact chromatic number is indeed three.

### Greedy constructive upper bound

A deterministic DSATUR procedure repeatedly colors an uncolored vertex with:

1. maximum number of distinct neighboring colors;
2. then maximum uncolored degree;
3. then deterministic vertex order.

It always produces a proper coloring and therefore an explicit encoder. Its
number of colors is an upper bound, not automatically the optimum.

### Exact bounded search

The exact checker:

1. computes maximum clique and maximum independent set;
2. takes the strongest implemented lower bound;
3. computes a DSATUR upper coloring;
4. tests \(k\)-colorability for every integer \(k\) between the bounds;
5. stops at the first feasible \(k\).

Each infeasible smaller \(k\) has been exhausted by bounded backtracking before
the returned value is called exact. Graphs above the declared vertex cap are
rejected rather than treated as solved.

---

## 5. Any finite graph can occur

The confusion-graph structure is not restricted to complete graphs, bipartite
graphs, or graphs arising from linear functions.

### Theorem

Every finite simple graph \(H=(V,E_H)\) is the confusion graph of some finite
one-shot function-computation problem with side information.

### Construction

Use the graph vertices as source states:

\[
\mathcal X=V.
\]

For each graph edge

\[
e=\{u,v\},
\]

create one sink \(t_e\).

At that sink:

- assign the same side-information value to \(u\) and \(v\);
- assign target zero to \(u\) and target one to \(v\);
- assign every other source state its own unique side-information value.

Then \(u,v\) are confusable at sink \(t_e\). No other pair becomes confusable
at that sink because every other state has a unique side value.

Taking the union over all edge sinks produces exactly \(E_H\).

For an edgeless graph, use one constant target and a unique side value for every
state.

Therefore:

\[
\boxed{
\text{finite zero-error side-information problems realize all finite simple graphs.}
}
\]

This matters methodologically. One cannot assume the exact message geometry is
always a Hamming cube, a vector space, or a low-dimensional simplex. The
nonlinear finite problem inherits the full variety of graph-coloring geometry.

The code constructs the problem from a supplied graph and checks exact adjacency
mask equality after reconstruction.

---

## 6. Two-bit source without side information

Let

\[
X=(X_1,X_2)\in\{0,1\}^2.
\]

Sink \(t_1\) wants \(X_1\); sink \(t_2\) wants \(X_2\). Neither receives
side information.

Take any two distinct source states. They differ in at least one coordinate.
The sink requesting that coordinate has the same constant side information in
both states but needs different targets. Therefore every pair is adjacent:

\[
G=K_4.
\]

Hence

\[
\chi(G)=4
\]

and

\[
\boxed{b_{\min}=2.}
\]

This is unsurprising in hindsight: without side information, the common
message must distinguish all four source states because the two sinks together
request the complete two-bit record.

---

## 7. Complementary side information

Keep the same targets, but give each sink the other source bit:

- \(t_1\) wants \(X_1\) and knows \(X_2\);
- \(t_2\) wants \(X_2\) and knows \(X_1\).

Two states are confusable when they differ in exactly one coordinate:

- same \(X_2\), different \(X_1\); or
- same \(X_1\), different \(X_2\).

The confusion graph is the four-cycle

\[
G=C_4.
\]

It is bipartite, so

\[
\chi(G)=2.
\]

One proper coloring is parity:

\[
\boxed{
c(x_1,x_2)=x_1\oplus x_2.}
\]

The decoders are

\[
X_1=c(X)\oplus X_2
\]

and

\[
X_2=c(X)\oplus X_1.
\]

Thus one common bit suffices:

\[
\boxed{b_{\min}=1.}
\]

The reduction from two bits to one is conditional on exact complementary side
information. The side information has not disappeared from the resource model;
it is explicitly available at the sinks.

---

## 8. Side-information refinement monotonicity

Suppose a transformed problem has the same source states, sinks, and targets,
but more informative side information.

Formally, refined side information \(s'_t\) refines coarse side information
\(s_t\) when

\[
 s'_t(x)=s'_t(y)
 \implies
 s_t(x)=s_t(y)
\]

for every sink and state pair. Equivalently, the coarse side value is a
function of the refined side value on the finite source set.

If two states are confusable after refinement, then they have equal refined
side information and different targets. Equal refined values imply equal coarse
values, so they were already confusable before refinement.

Therefore:

\[
E_{\mathrm{refined}}
\subseteq
E_{\mathrm{coarse}}.
\]

Deleting graph edges cannot increase chromatic number, so

\[
\boxed{
\chi(G_{\mathrm{refined}})
\le
\chi(G_{\mathrm{coarse}}).
}
\]

Complementary side information changes the two-bit problem from \(K_4\) to
\(C_4\), reducing the optimum from four messages to two.

The theorem does not say side information is free. It says that **conditional
on a more informative decoder input**, the additional common message need not
be larger.

---

## 9. Target coarsening monotonicity

Now keep source states, sinks, and side information fixed, but replace each
target \(f_t\) by a coarser target \(g_t\) that is a function of it:

\[
 f_t(x)=f_t(y)
 \implies
 g_t(x)=g_t(y).
\]

If the coarsened targets differ,

\[
g_t(x)\ne g_t(y),
\]

then the original targets must also differ. Thus every new confusion edge was
already present:

\[
E_{\mathrm{coarse\ target}}
\subseteq
E_{\mathrm{original}}.
\]

Hence

\[
\boxed{
\chi(G_{\mathrm{coarse\ target}})
\le
\chi(G_{\mathrm{original}}).
}
\]

This formalizes an obvious but frequently omitted point: asking sinks to
predict less detailed functions can reduce the required common state. It is a
change in the observable requirement, not evidence that the original exact
world was equally cheap to represent.

---

## 10. Zero-error randomization does not reduce message alphabet

Suppose the encoder is allowed to randomize. For source state \(x\), let

\[
A_x\subseteq\mathcal M
\]

be the nonempty support of possible messages.

For zero error, adjacent source states must have disjoint supports. If
\(x,y\) are confusable and share a possible message \(m\), then under that
message and their common sink side value the decoder would again need two
different outputs.

Thus

\[
\{x,y\}\in E
\implies
A_x\cap A_y=\varnothing.
\]

Now choose one arbitrary message

\[
a_x\in A_x
\]

for every state. Adjacent supports are disjoint, so adjacent states choose
different messages. The selected labels form a deterministic proper coloring
using no more than \(|\mathcal M|\) colors.

Therefore:

\[
\boxed{
\text{one-shot private encoder randomization cannot reduce the zero-error message alphabet below }\chi(G).
}
\]

The implementation stores finite message supports, checks pairwise disjointness
on every confusion edge, determinizes by selecting one support element, and
audits the resulting coloring.

This result does not address allowed error, expected length, shared randomness
with changing accounting, block coding, or quantum messages.

---

## 11. Common-message multicast bridge

Suppose an exact network code multicasts a source vector

\[
z\in\mathbb F_p^h
\]

to every function-demand sink.

If

\[
\chi(G)\le p^h,
\]

inject the optimal color labels into distinct field vectors:

\[
\iota:
\{0,\ldots,\chi(G)-1\}
\hookrightarrow
\mathbb F_p^h.
\]

The source sends

\[
z(x)=\iota(c(x)).
\]

Every sink recovers the color vector, inverts the finite injection, and combines
the color with its local side information using the decoder table from the
coloring theorem.

Therefore:

\[
\boxed{
\chi(G)\le p^h
\ \text{and exact multicast of }h\text{ field symbols}
\implies
\text{exact solution of the finite function problem.}
}
\]

For the complementary two-bit example,

\[
\chi(C_4)=2,
\]

so one binary field symbol suffices and may be copied through a one-symbol
broadcast network.

For the no-side-information example,

\[
\chi(K_4)=4,
\]

so a one-symbol binary source alphabet is too small.

This bridge multicasts the complete common color. More specialized
sink-specific network function codes may avoid reconstructing the color itself;
those belong to the separate linear-function and future nonlinear-function
lanes.

---

## 12. Bounded computational certificates

The implementation provides:

- finite function and side-information tables;
- one confusion witness per graph edge;
- exact adjacency masks;
- proper-color and direct zero-error encoder checks;
- explicit decoder-table synthesis;
- deterministic DSATUR upper colorings;
- exact maximum clique and independent set;
- exact bounded \(k\)-colorability search;
- chromatic and fixed-length bit certificates;
- arbitrary finite graph realization;
- side-information and target-coarsening monotonicity certificates;
- zero-error randomized-support determinization;
- finite-field color embeddings into a validated multicast certificate.

The test suite independently exhausts all 64 labeled simple graphs on four
vertices. For every graph it compares:

- exact chromatic search against direct coloring enumeration;
- maximum clique against subset enumeration;
- maximum independent set against subset enumeration.

It separately checks \(C_5\), \(K_4\), \(C_4\), edgeless graphs, randomized
supports, monotonicity, decoder tables, and end-to-end color multicast.

---

## 13. What this contributes to the simulation discussion

A proposed on-demand renderer need not preserve distinctions irrelevant to all
future observers. It must preserve exactly those distinctions that some future
observer could still need after accounting for information already available
in that observer's region.

The confusion graph makes that statement operational.

### Side information changes which histories may merge

Two histories that demand different outputs can share one central message when
the sink can distinguish them locally. Without that side information, the same
merge is invalid.

### Full-state recovery can overcount predictive distinctions

The optimal message depends on requested functions, not on the source-state
label itself. Coarsening targets deletes confusion edges.

### Nonlinear finite demand geometry can be arbitrary

Every finite graph can occur. One should not assume all predictive-state
problems reduce to rank, Hamming distance, or convex geometry.

### A larger model cannot decode a missing distinction

If two confusable states receive the same message and the sink has the same
side information, no downstream computation can determine which target to
return. The obstruction is informational, not algorithmic intelligence.

### Randomness does not evade exact one-shot ambiguity

Random support overlap on a confusion edge reintroduces the same impossible
decoder cell. Zero-error randomization therefore cannot beat the chromatic
message alphabet.

### Compression claims are interface claims

Reducing \(\chi(G)\) by adding side information or coarsening targets changes
the required observable interface. It is not a proof that a more detailed
microscopic target can be represented at the same cost.

None of these facts distinguishes ordinary distributed physics from an exact
simulator. Both must obey the same finite internal communication constraints.

---

## Nonclaims

- The result is one-shot, deterministic, common-message, finite, and zero-error.
- It does not give asymptotic graph entropy, fractional coloring, or block-code
  rates.
- It does not cover interactive protocols or query revelation after partial
  communication.
- It does not cover allowed-error stochastic encoders or average distortion.
- It does not cover quantum messages or entanglement assistance.
- Private zero-error randomization is shown not to reduce the message alphabet;
  other resource models require separate analysis.
- The exact chromatic solver is bounded and exponential; a configured vertex
  cap is a scope boundary.
- Every finite graph is realizable only because the construction may introduce
  one artificial sink per edge with arbitrary side-information values.
- The multicast bridge sends a complete color index and is not claimed optimal
  among all sink-specific network codes.
- More informative side information is an explicit resource assumption, not a
  free operation.
- Graph colors and fixed-length bits are internal information measures, not
  parent-substrate RAM, energy, mass, or qubits.
- Confusion graphs, chromatic numbers, parity messages, or side-information
  gains are not evidence for simulation.

---

## Next research targets

1. Add prior-weighted variable-length coding and distinguish chromatic count
   from expected prefix length.
2. Develop finite block products and compare one-shot chromatic number with
   multiletter rates without silently importing asymptotic graph entropy.
3. Add allowed-error confusion and rate-distortion formulations.
4. Add interactive protocols in which side information or queries arrive after
   partial communication.
5. Generalize the multicast bridge to sink-specific nonlinear function codes
   that do not reconstruct the common color.
6. Add noisy side information and robust decoder ambiguity bounds.
7. Compare classical, shared-randomness, quantum, and entanglement-assisted
   message resources under one finite interface.
8. Connect logical quantum-code observables to nonlinear finite sink demands.
9. Add certified graph decompositions for larger structured confusion graphs.
