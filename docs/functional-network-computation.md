# Sink-specific linear predictive functions and side information

## Scope

The earlier multicast lane asks every sink to reconstruct the same complete
source vector. That is often stronger than a predictive system actually needs.
One observer may only need one parity, another may need a different linear
summary, and each may already possess local side information.

This note studies the finite exact model

\[
x\in\mathbb F_p^h,
\]

where sink \(t\) needs

\[
B_tx
\]

and already knows

\[
S_tx.
\]

The rows of \(B_t\) are demanded linear functions. The rows of \(S_t\) are
local side-information functions. Network edges carry scalar symbols over the
same declared prime field.

The central questions are:

1. Which incoming network symbols let one sink compute its requested functions?
2. How much new linear dimension must cross every cut to that sink?
3. Why can all per-sink cut bounds hold while a shared bottleneck remains
   jointly infeasible?
4. When does side information let one coded symbol replace several uncoded
   symbols?
5. How can a finite predictive-class label be reduced to sink-specific future
   functions rather than multicast in full?

These are bounded internal communication and predictive-function statements.
They are not evidence that reality is simulated. Field symbols, side
information, ranks, messages, and cuts are not parent-universe hardware,
energy, mass, or spacetime.

---

## 1. Linear observation model

Let the source state be a column vector

\[
x=(x_1,\ldots,x_h)^\top\in\mathbb F_p^h.
\]

Every network edge carries one linear form

\[
y_e=g_e x,
\qquad
g_e\in\mathbb F_p^{1\times h}.
\]

For sink \(t\), stack the global encoding rows of its incoming network edges:

\[
G_t
=
\begin{pmatrix}
 g_{e_1}\\
 \vdots\\
 g_{e_m}
\end{pmatrix}.
\]

The sink receives

\[
y_t=G_tx.
\]

It also has local side information

\[
z_t=S_tx
\]

and must output

\[
u_t=B_tx.
\]

The sink may linearly combine all received network symbols and all local side
information. The repository checks exact arithmetic over a declared prime
field.

---

## 2. Exact row-space recovery theorem

### Theorem

Sink \(t\) can recover \(B_tx\) exactly for every source vector \(x\) if and
only if

\[
\boxed{
\operatorname{rowspan}(B_t)
\subseteq
\operatorname{rowspan}
\begin{pmatrix}
G_t\\S_t
\end{pmatrix}.
}
\]

Equivalently,

\[
\boxed{
\operatorname{rank}
\begin{pmatrix}
G_t\\S_t\\B_t
\end{pmatrix}
=
\operatorname{rank}
\begin{pmatrix}
G_t\\S_t
\end{pmatrix}.
}
\]

### Sufficiency

If every row of \(B_t\) lies in the span of the available rows, there is a
matrix \(D_t\) satisfying

\[
B_t
=
D_t
\begin{pmatrix}
G_t\\S_t
\end{pmatrix}.
\]

The sink computes

\[
D_t
\begin{pmatrix}
y_t\\z_t\end{pmatrix}
=
D_t
\begin{pmatrix}
G_t\\S_t
\end{pmatrix}x
=
B_tx.
\]

Thus the requested functions are recovered for every source state.

### Necessity

Suppose exact linear recovery is possible. Each output coordinate must be a
linear combination of the available network and side-information symbols. So
there must be a decoder matrix \(D_t\) with

\[
B_tx
=
D_t
\begin{pmatrix}
G_t\\S_t
\end{pmatrix}x
\qquad\forall x.
\]

Two linear maps that agree on every \(x\in\mathbb F_p^h\) have the same matrix,
so

\[
B_t
=
D_t
\begin{pmatrix}
G_t\\S_t
\end{pmatrix}.
\]

Every row of \(B_t\) therefore lies in the available row span.

### Computational certificate

The implementation independently checks the theorem in two ways:

1. compare the two finite-field ranks;
2. solve one exact linear system for every target row and verify the resulting
   decoder coefficients on every bounded example.

A disagreement between rank inclusion and decoder solvability raises an
internal assertion.

---

## 3. Conditional demand rank

Some demanded rows may already be available through side information. The raw
rank of \(B_t\) therefore overstates the amount of new information required
from the network.

Define

\[
\boxed{
r_t
=
\operatorname{rank}
\begin{pmatrix}
S_t\\B_t
\end{pmatrix}
-
\operatorname{rank}(S_t).
}
\]

This is the dimension added by the target row space after quotienting out the
side-information row space.

Equivalent interpretation:

\[
r_t
=
\dim
\frac{\operatorname{rowspan}(S_t)+\operatorname{rowspan}(B_t)}
{\operatorname{rowspan}(S_t)}.
\]

Examples:

- no side information and one nonzero target row: \(r_t=1\);
- target already known locally: \(r_t=0\);
- two target rows with one independent combination already known: \(r_t=1\);
- duplicate target rows do not increase \(r_t\).

This avoids counting syntax rather than information. Asking twice for the same
linear function does not require two new dimensions.

---

## 4. Conditional cut lower bound

### Theorem

Every source-to-sink cut in the declared scalar finite-field network must have
capacity at least \(r_t\):

\[
\boxed{
\operatorname{mincut}(s,t)
\ge
r_t.
}
\]

### Proof

Fix any source-sink cut containing \(c\) scalar unit edges. Let \(W\) be the
row span of the global encoding vectors carried across that cut. Since each
edge carries one scalar field symbol,

\[
\dim W\le c.
\]

Every downstream network symbol is a linear function of the cut symbols, so
all network information reaching the sink lies in \(W\). Exact recovery
requires

\[
\operatorname{rowspan}(B_t)
\subseteq
\operatorname{rowspan}(S_t)+W.
\]

Therefore

\[
\operatorname{rank}
\begin{pmatrix}
S_t\\B_t
\end{pmatrix}
\le
\operatorname{rank}(S_t)+\dim W
\le
\operatorname{rank}(S_t)+c.
\]

Rearranging gives

\[
c
\ge
\operatorname{rank}
\begin{pmatrix}
S_t\\B_t
\end{pmatrix}
-
\operatorname{rank}(S_t)
=r_t.
\]

Because the argument applies to every cut, it applies to the minimum cut.

### Boundary

This is a necessary receiver-wise condition. It does not say that satisfying
all sink inequalities produces one jointly compatible network code.

---

## 5. Why per-sink cut adequacy is not jointly sufficient

Consider a one-symbol broadcast network:

\[
s\longrightarrow b
\longrightarrow
\{t_1,t_2\}.
\]

The source-to-relay edge carries one scalar

\[
y=gx,
\qquad g\in\mathbb F_2^{1\times2},
\]

and the relay copies it to both sinks.

Let

\[
x=(x_1,x_2)^\top.
\]

Suppose:

\[
B_{t_1}=(1,0),
\qquad
B_{t_2}=(0,1),
\]

with no side information.

Each sink asks for one independent scalar, so

\[
r_{t_1}=r_{t_2}=1.
\]

Each sink also has source min-cut one. Thus every receiver-wise cut inequality
holds exactly.

But exact recovery would require

\[
(1,0)
\in
\operatorname{span}\{g\}
\]

and

\[
(0,1)
\in
\operatorname{span}\{g\}.
\]

One one-dimensional subspace cannot contain both independent basis rows. Hence
no scalar linear code exists.

The common unresolved requirement is the span of both demands:

\[
\operatorname{rank}
\begin{pmatrix}
1&0\\
0&1
\end{pmatrix}
=2.
\]

So the smallest common message subspace has dimension two even though the
maximum individual conditional rank is one.

This gives a sharp first-principles warning:

\[
\boxed{
\max_t r_t
\text{ is not generally the common-bottleneck requirement.}
}
\]

Receiver-wise cuts ignore incompatibility between heterogeneous demands that
must share the same upstream message.

---

## 6. Common linear summary problem

Let \(W\le\mathbb F_p^h\) be the row space of a common summary sent before the
network branches. Every sink can combine \(W\) with its local side information.
The summary is valid exactly when

\[
\boxed{
\operatorname{rowspan}(B_t)
\subseteq
W+\operatorname{rowspan}(S_t)
\qquad\forall t.
}
\]

The minimum common linear summary dimension is

\[
\boxed{
R^\star
=
\min_W
\left\{
\dim W:
\operatorname{rowspan}(B_t)
\subseteq
W+\operatorname{rowspan}(S_t)
\ \forall t
\right\}.
}
\]

This quantity accounts for demand overlap and side information jointly. It can
be:

- larger than \(\max_t r_t\), when heterogeneous demands conflict;
- equal to \(\max_t r_t\), when one common coded summary serves all sinks;
- smaller than the rank of the union of all target rows, because side
  information lets different sinks interpret the same coded symbol differently.

The source can transmit any basis of an optimal \(W\). Basis choice is a
representation convention; the subspace is the invariant.

---

## 7. Exact bounded subspace search

The repository computes \(R^\star\) exactly for bounded finite fields and
source dimensions.

For each candidate dimension

\[
r=0,1,\ldots,h,
\]

the checker:

1. enumerates every set of \(r\) distinct nonzero vectors;
2. discards linearly dependent sets;
3. converts each independent set to one canonical reduced-row-echelon basis;
4. deduplicates bases representing the same subspace;
5. tests every sink row-space inclusion;
6. stops at the first feasible dimension.

### Completeness proof

Every \(r\)-dimensional subspace has some basis of \(r\) distinct nonzero
vectors. That basis appears in the finite enumeration. Reduced-row-echelon form
maps every basis of one subspace to the same canonical row basis, so
deduplication removes repetition without removing any subspace.

All smaller dimensions are exhausted before dimension \(r\) is considered.
Therefore the first feasible subspace has minimum dimension.

### Search cap semantics

If the configured generator-set cap is reached before a dimension is
exhausted, the result is marked **incomplete**. It is not reported as an
optimum or impossibility theorem.

This mirrors the repository-wide rule that bounded search supports an
impossibility claim only after its declared domain is exhausted.

---

## 8. Complementary side information and one XOR symbol

Now use the same two-bit source, but give each sink the other half of the
problem:

\[
S_{t_1}=(1,0),
\qquad
B_{t_1}=(0,1),
\]

so \(t_1\) knows \(x_1\) and wants \(x_2\), while

\[
S_{t_2}=(0,1),
\qquad
B_{t_2}=(1,0),
\]

so \(t_2\) knows \(x_2\) and wants \(x_1\).

Each conditional rank remains one:

\[
r_{t_1}=r_{t_2}=1.
\]

Consider the common summary row

\[
g=(1,1).
\]

The source sends

\[
y=x_1+x_2
\]

over \(\mathbb F_2\).

Sink \(t_1\) computes

\[
x_2=y+x_1,
\]

and sink \(t_2\) computes

\[
x_1=y+x_2.
\]

Thus

\[
\boxed{R^\star=1.}
\]

The bounded subspace checker finds the unique one-dimensional feasible
subspace

\[
W=\operatorname{span}\{(1,1)\}.
\]

Neither \(W=\operatorname{span}\{(1,0)\}\) nor
\(W=\operatorname{span}\{(0,1)\}\) serves both sinks.

The side information has not reduced either individual new-information rank
below one. It has changed which **common** one-dimensional message can be useful
to both receivers.

---

## 9. Coding-versus-routing separation

In the declared routing-only scalar model, the source edge may carry:

\[
0,
\qquad x_1,
\qquad x_2,
\]

but not the coded combination \(x_1+x_2\).

- Sending zero serves neither sink.
- Sending \(x_1\) lets \(t_2\) recover its demand but gives \(t_1\) nothing new.
- Sending \(x_2\) lets \(t_1\) recover its demand but gives \(t_2\) nothing new.

Therefore no routing-only scalar assignment solves the complementary
side-information problem.

The linear code sends \(x_1+x_2\) and solves both demands.

For the finite broadcast topology, the complete binary local-coefficient domain
contains

\[
4\times2\times2=16
\]

assignments:

- four source vectors on \(s\to b\);
- two copy coefficients on \(b\to t_1\);
- two copy coefficients on \(b\to t_2\).

The checker exhausts all 16 assignments and confirms:

1. no scalar linear code solves the no-side-information heterogeneous demands;
2. no routing-only code solves the complementary side-information demands;
3. a linear XOR code does solve the side-information demands.

It then enumerates every source vector

\[
(0,0),(0,1),(1,0),(1,1)
\]

and verifies both sink decoders end to end.

---

## 10. Side information is part of the interface

The XOR gain is not free compression of the source. It depends on each sink
already possessing a different source-dependent function.

A valid resource statement must specify:

- how side information was created;
- where it is stored;
- whether it remains causally accessible;
- whether it is exact or noisy;
- whether it is correlated with the source as declared;
- whether its acquisition cost is inside or outside the modeled cut.

If side information was itself transmitted earlier, that communication must be
counted in the appropriate earlier stage. If it is local measurement data, its
physical acquisition belongs to the observation model.

The theorem says what additional message suffices **conditional on the declared
side information**. It does not declare side information free in every
architecture.

---

## 11. Predictive-function bridge

Let a finite exact predictive-class label be embedded as

\[
x(r)\in\mathbb F_p^h
\]

for each hidden record \(r\).

Suppose sink \(t\)'s allowed future answers depend only on the linear signature

\[
B_tx(r),
\]

and it already knows

\[
S_tx(r).
\]

If the network and side information let the sink recover \(B_tx(r)\), it can
answer every future query represented by those rows. The sink need not recover
the full class vector \(x(r)\).

This can strictly reduce required communication when the sink's query family
coarsens the complete predictive partition.

The bridge is restricted:

- the chosen class embedding must be explicit;
- the sink signatures must actually be linear in that embedding;
- different embeddings can change which functions are linear and which code is
  convenient;
- arbitrary finite predictive functions need not admit the selected linear
  representation.

The repository includes a finite signature-map checker so representation
choices remain visible rather than being treated as physical identities.

---

## 12. What this adds to the simulation discussion

A hypothetical on-demand renderer need not send every hidden detail to every
observer. It must send enough information for each observer's unresolved future
queries, conditional on information already available in that observer's
causal region.

The function-computation results expose several missing assumptions in informal
arguments:

### Full-state multicast can be a severe overestimate

If a sink only needs \(B_tx\), requiring recovery of all \(x\) counts irrelevant
predictive distinctions.

### Individual cut bounds can underestimate joint shared demand

Two sinks can each require one new dimension while one shared one-dimensional
message is impossible without suitable overlap or side information.

### Side information changes coding geometry

The same XOR symbol can reveal different missing facts to different sinks.
Without the declared side information, it may reveal too little.

### Coding changes the message, not the underlying law

Sending \(x_1+x_2\) is a different representation of predictive information.
It does not erase the need for exact globally consistent answers.

### Representation labels are not ontology

A finite-field vector is a code for a predictive class. It is not a claim that
the universe is literally made of finite-field coordinates.

None of these results distinguishes ordinary distributed physics from an exact
simulator. Both must satisfy the same internal information constraints under
the declared interface.

---

## 13. Computational objects

The implementation provides:

- canonical finite-field row reduction;
- exact row-space containment;
- conditional demand rank;
- typed sink demands and side-information rows;
- network global-vector propagation through the existing scalar-code checker;
- exact per-target decoder coefficients;
- end-to-end sink decoding;
- conditional cut certificates;
- exhaustive scalar linear and routing-only search;
- exact bounded common-summary subspace search;
- explicit incomplete-search reporting;
- the no-side heterogeneous broadcast obstruction;
- the complementary-side-information XOR construction;
- full enumeration of source vectors and local binary assignments;
- a restricted predictive linear-signature bridge.

Closed-form rank criteria are checked against exact solver outputs and bounded
exhaustive searches.

---

## Nonclaims

- The module does not solve general nonlinear network function computation.
- It does not prove a general index-coding theorem.
- All functions, side information, and edge operations are linear over one
  declared prime field.
- The network is finite, directed, acyclic, scalar, and exact.
- Per-sink conditional-rank cuts are necessary, not jointly sufficient.
- The common-summary search is exact only when its declared finite enumeration
  completes.
- Routing-only semantics are the repository's zero-or-unchanged-basis-copy
  model.
- Side information is an explicit resource assumption, not automatically free.
- A linear predictive signature depends on the chosen finite-field class
  embedding.
- Field dimensions, ranks, symbols, cuts, and side-information rows are not
  parent-substrate resource units.
- Linear function computation and XOR coding are not evidence for simulation.

---

## Next research targets

1. Extend from scalar functions to vector block codes and track delay.
2. Add noisy side information and Slepian-Wolf-style source uncertainty without
   silently importing an asymptotic theorem.
3. Solve bounded linear common-summary problems more efficiently than subspace
   enumeration.
4. Add sink-specific approximate stochastic functions rather than exact rows.
5. Place side information at intermediate nodes and model where it crosses the
   causal graph.
6. Add multiple communication rounds and progressive query revelation.
7. Develop nonlinear finite function-computation checks for very small domains.
8. Add robust edge failures and uncertain side-information channels.
9. Connect logical observables of quantum codes to sink-specific distributed
   function demands.
