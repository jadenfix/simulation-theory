# Distributed causal-cut consistency bounds

## Scope

The previous relational results show that a locally random transcript can carry
a later global constraint. This note asks what changes when the observations
and future queries occur in different causal or computational regions.

The bounded interface is deliberately simple:

1. An earlier region knows a binary record

   \[
   X=(X_1,\ldots,X_m)\in\{0,1\}^m.
   \]

2. Before the future query index \(I\) is revealed, all record-dependent
   information available to the answering region must cross a declared one-way
   cut or already reside there.
3. After receiving \(I\), the answering region outputs an estimate of \(X_I\).

This is the one-way **INDEX** problem interpreted as a predictive-consistency
interface. The theorem is not specifically quantum. It is a communication and
information constraint that any classical or quantum-world renderer must obey
if it implements this exact classical future-query interface.

The causal language is operational rather than cosmological. The result does
not assert that our universe uses this architecture, does not identify a parent
substrate, and is not evidence for simulation.

---

## Exact zero-error causal-cut bound

Let

\[
f:\{0,1\}^m\rightarrow\mathcal M
\]

be the message or predictive-state map sent before the query is known. A
decoder

\[
g:\mathcal M\times[m]\rightarrow\{0,1\}
\]

must satisfy

\[
g(f(x),i)=x_i
\qquad
\forall x\in\{0,1\}^m,\ i\in[m].
\]

### Injectivity proof

Suppose two distinct records collide:

\[
f(x)=f(x'),
\qquad x\ne x'.
\]

There is some coordinate \(i\) for which

\[
x_i\ne x'_i.
\]

The decoder receives the same pair \((f(x),i)=(f(x'),i)\) in both worlds, so it
must return the same answer. That answer cannot equal both \(x_i\) and
\(x'_i\). This contradicts zero error.

Therefore \(f\) is injective and

\[
\boxed{|\mathcal M|\ge2^m.}
\]

Equivalently,

\[
\boxed{\log_2|\mathcal M|\ge m.}
\]

This lower bound is tight: transmitting the complete record uses exactly
\(m\) bits.

### Why query timing matters

The query arrives **after** the message is fixed. If the sender knew \(I\) in
advance, it could send only \(X_I\), requiring one bit. Thus the \(m\)-bit
result is not a generic consequence of having \(m\) possible questions. It is a
consequence of preserving the ability to answer every question after the
future query choice remains unresolved.

### Zero-error shared randomness

Shared randomness \(R\), independent of \(X\), does not remove the argument.
Condition on any random seed used with positive probability. If the protocol is
zero-error for every input and query, the seed-conditioned encoding must still
separate every pair of records. Randomness may choose among injective encodings,
but cannot reduce their message-state cardinality.

The implementation explicitly audits finite encoders. Every collision returns
a concrete pair of records and a coordinate that no deterministic decoder can
answer correctly for both.

---

## Bounded-error information lower bound

Now assume:

- \(X_1,\ldots,X_m\) are independent uniform bits;
- the future query \(I\) is uniform on \([m]\);
- \(R\) is shared randomness independent of \(X\);
- \(M\) is the complete record-dependent message or resident predictive state;
- the decoder outputs

  \[
  \widehat X_i=g_i(M,R).
  \]

Let

\[
e_i=P(\widehat X_i\ne X_i)
\]

and suppose the uniform-query average error is

\[
\frac1m\sum_{i=1}^m e_i\le\epsilon,
\qquad0\le\epsilon\le\frac12.
\]

### Coordinatewise binary Fano step

Because \(\widehat X_i\) is a function of \((M,R)\), binary Fano gives

\[
H(X_i\mid M,R)
\le H_2(e_i),
\]

where

\[
H_2(p)=-p\log_2p-(1-p)\log_2(1-p).
\]

Entropy subadditivity yields

\[
H(X\mid M,R)
\le
\sum_{i=1}^m H(X_i\mid M,R)
\le
\sum_{i=1}^m H_2(e_i).
\]

Since \(H_2\) is concave,

\[
\frac1m\sum_iH_2(e_i)
\le
H_2\left(\frac1m\sum_ie_i\right)
\le H_2(\epsilon).
\]

Because \(X\) is independent of \(R\),

\[
H(X\mid R)=H(X)=m.
\]

Therefore

\[
\begin{aligned}
I(X;M\mid R)
&=H(X\mid R)-H(X\mid M,R)\\
&\ge m-mH_2(\epsilon).
\end{aligned}
\]

Thus

\[
\boxed{
I(X;M\mid R)
\ge
m[1-H_2(\epsilon)].
}
\]

If the message has at most \(2^b\) possible values for every shared seed, then

\[
I(X;M\mid R)
\le H(M\mid R)
\le b,
\]

so

\[
\boxed{
b\ge m[1-H_2(\epsilon)].}
\]

The finite-state integer consequence is

\[
\boxed{
b\ge\left\lceil m[1-H_2(\epsilon)]\right\rceil.}
\]

### Boundaries

- \(\epsilon=0\) recovers \(b\ge m\).
- \(\epsilon=1/2\) gives the trivial lower bound zero, because independent
  guessing achieves error one half.
- At \(m=100\), \(\epsilon=0.1\), the information lower bound is approximately
  \(53.10\) bits, so a finite message alphabet needs at least \(54\) bits.

This is an information lower bound. It does not by itself construct an optimal
finite protocol at every \((m,\epsilon)\).

---

## Memory-communication cut tradeoff

Suppose the later region already holds a record-dependent state \(S\) of at
most \(s\) bits before separation, and an additional message \(C\) of at most
\(c\) bits can cross later but still before the query is revealed.

The pair \((S,C)\) is one combined INDEX message. Hence

\[
\boxed{s+c\ge m}
\]

for exact answering and

\[
\boxed{s+c\ge m[1-H_2(\epsilon)]}
\]

under the uniform bounded-error model.

Therefore the required additional communication obeys

\[
\boxed{
c\ge
\max\{0,m[1-H_2(\epsilon)]-s\}.}
\]

Integer message lengths use the ceiling of the positive remainder.

This is a cut-set statement. The split between “memory” and “communication” is
architectural; only the total record information available on the answering
side before the unresolved query matters to this proof.

Shared randomness is not counted as record information because

\[
I(X;R)=0.
\]

If a supposedly shared cache was populated using \(X\), it belongs in \(S\) or
\(C\), not in \(R\).

---

## Parity reconciliation equivalence

Let an earlier region hold

\[
A\in\{0,1\}^m
\]

and the answering region hold

\[
B\in\{0,1\}^m.
\]

After the one-way message is fixed, query \(i\) asks for

\[
A_i\oplus B_i.
\]

Because \(B_i\) is locally known, a parity answer immediately yields

\[
A_i=(A_i\oplus B_i)\oplus B_i.
\]

Conversely, knowing \(A_i\) yields the parity. Therefore indexed parity
reconciliation and INDEX have exactly the same one-way information lower bounds
with respect to the remote record \(A\).

This connects the communication theorem to distributed consistency checks. If
two regions independently hold local records whose future comparison may query
any coordinate, the remote contribution cannot be discarded merely because the
final requested object is a relation rather than an absolute bit.

---

## Weighted-query information bound

Uniform future queries treat every coordinate symmetrically. Many systems do
not. Let

\[
w_i=P(I=i),
\qquad
w_i\ge0,
\qquad
\sum_iw_i=1,
\]

and assume

\[
\sum_iw_ie_i\le\epsilon.
\]

The coordinatewise Fano argument still gives

\[
I(X;M\mid R)
\ge
m-\sum_iH_2(e_i).
\]

If only the weighted average error is known, the weakest valid lower bound is
obtained by maximizing the conditional-entropy upper bound:

\[
\begin{aligned}
\text{maximize}\quad &\sum_iH_2(e_i)\\
\text{subject to}\quad
&\sum_iw_ie_i\le\epsilon,\\
&0\le e_i\le\frac12.
\end{aligned}
\]

This is a concave maximization over a convex compact set, equivalently a convex
optimization after negating the objective.

### KKT solution

For a positive-weight coordinate in the interior,

\[
H_2'(e_i)
=
\log_2\frac{1-e_i}{e_i}.
\]

The Lagrangian stationarity equation is

\[
\log_2\frac{1-e_i}{e_i}
=
\lambda w_i,
\qquad\lambda\ge0.
\]

Solving gives

\[
\boxed{
e_i(\lambda)
=
\frac{1}{1+2^{\lambda w_i}}.
}
\]

For \(w_i=0\), the coordinate never appears in the query distribution, so the
entropy-maximizing choice is

\[
e_i=\frac12.
\]

For \(0<\epsilon<1/2\), choose the unique \(\lambda>0\) satisfying

\[
\sum_iw_i e_i(\lambda)=\epsilon.
\]

The resulting lower bound is

\[
\boxed{
I(X;M\mid R)
\ge
\sum_{i=1}^m[1-H_2(e_i(\lambda))].
}
\]

The repository solves the scalar multiplier by a deterministic bounded binary
search. An analytic bracket avoids overflow: because

\[
\frac1{1+2^x}\le2^{-x},
\]

if \(w_{\min}\) is the smallest positive weight, then

\[
\lambda
\ge
\frac{\log_2(1/\epsilon)}{w_{\min}}
\]

is sufficient to drive the weighted error below \(\epsilon\).

### Interpretation

If \(w_i>w_j\), then for the same \(\lambda\),

\[
e_i<e_j.
\]

The least-informative admissible protocol protects frequently queried bits more
accurately and sacrifices rare bits first. At zero weight, a bit can be
forgotten completely without affecting the declared objective.

For uniform weights \(w_i=1/m\), symmetry forces

\[
e_i=\epsilon
\]

and the expression reduces exactly to

\[
m[1-H_2(\epsilon)].
\]

This weighted result is the sharpest bound produced by the coordinatewise
binary-Fano argument when only the weighted error constraint is supplied. It is
not automatically the exact finite communication complexity of every weighted
INDEX instance.

---

## Isolated-region replication bound

Suppose there are \(r\) later regions. Each receives its own finite local state
\(M_j\) before its future query is known. After separation:

- region \(j\) must answer its query locally;
- no later communication is allowed;
- no record-dependent shared store remains accessible to all regions.

The single-region lower bound applies independently to each local alphabet. If
\(b_j\) is the local storage length,

\[
b_j\ge L
\]

for every region, where \(L\) is the appropriate uniform or weighted INDEX
lower bound. Therefore the sum of physically separate local storage budgets
obeys

\[
\boxed{
\sum_{j=1}^r b_j
\ge rL.
}
\]

For exact uniform INDEX,

\[
\boxed{
\sum_jb_j\ge rm.
}
\]

This is a replication result about separate local storage. It does **not** say
the joint mutual information in all copies is \(rm\); identical replicas are
highly redundant globally. It says each isolated answering region needs its own
locally accessible predictive state.

If all regions can query one shared record-dependent store after separation,
the premise fails and the replication factor cannot be claimed.

---

## A simple finite upper construction

To keep lower and upper bounds distinct, consider a deliberately simple
protocol:

1. Store the first \(s\) record bits exactly.
2. Answer stored coordinates exactly.
3. Guess zero for every unstored coordinate.

For uniform \(X\) and uniform \(I\), an unstored bit is wrong with probability
one half. Therefore

\[
\boxed{
\epsilon_{\mathrm{prefix}}(m,s)
=
\frac{m-s}{2m}.
}

The repository verifies this identity by complete enumeration for small
records.

To reach average error at most \(\epsilon\), this scheme uses

\[
s\ge m(1-2\epsilon)
\]

bits. This is an upper bound from one explicit protocol, not an optimality
claim. For example, at \(\epsilon=0.1\), it uses \(0.8m\) bits, while the Fano
lower bound is approximately \(0.531m\). The gap is an honest unresolved space
between this simple construction and the information lower bound.

---

## Causal-cut interpretation

The theorem can be read as a statement about unresolved future branches.
Before the query is chosen, the answering side must retain enough information
to distinguish records that some future query could separate.

The exact equivalence relation is

\[
x\sim x'
\iff
x_i=x_i'\quad\forall i\text{ allowed in the future}.
\]

When every coordinate remains queryable, each equivalence class contains one
record, producing \(2^m\) exact predictive classes.

With allowed error and a query distribution, records can be compressed because
some future answers may be wrong. The entropy and weighted KKT calculations
quantify how much predictive distinction can be discarded under the declared
loss.

This applies equally to an ordinary distributed database, a cached physics
engine, or a hypothetical on-demand renderer. It is not uniquely diagnostic of
simulation. An exact simulator can satisfy the bound by transmitting or storing
an adequate sufficient state.

---

## What researchers can easily miss

### Marginal correctness is not distributed consistency

A region can generate each local bit with the right marginal while lacking the
remote record needed for later indexed reconciliation. Correct one-point laws
do not guarantee correct future cross-region relations.

### Shared randomness is not shared record information

Randomness independent of \(X\) can align protocol choices, but cannot encode
which one of \(2^m\) records occurred. A record-dependent shared object is
memory or communication and must be counted as such.

### Query timing changes complexity by a factor of m

Known-before-message queries need one bit. Unknown-until-after-message queries
can require linear information. Discussions of lazy rendering that omit query
timing leave out the main source of the lower bound.

### Local storage and global information are different accounting measures

Replicating the same \(m\)-bit state in \(r\) isolated regions costs \(rm\)
local storage bits while containing only \(m\) bits of unique global
information. Both statements can be true.

### A lower bound needs an interface

Changing any of the following can change the result:

- which queries remain possible;
- when the query becomes known;
- whether later communication is allowed;
- whether a shared store remains accessible;
- the query distribution;
- average versus worst-case error;
- whether the source bits are uniform and independent.

There is no architecture-free statement that “the universe needs m bits here.”

---

## Nonclaims

- The one-way INDEX model is not asserted to describe the actual universe.
- “Causal cut” is an operational communication boundary, not evidence about a
  parent spacetime.
- Information lower bounds are not automatically hardware, energy, mass, or
  Landauer-cost lower bounds in an unknown substrate.
- The bounded-error proof assumes independent uniform source bits unless the
  weighted query section explicitly changes only the query distribution.
- Shared randomness is assumed independent of the record.
- The replication theorem excludes a causally accessible shared store and later
  inter-region communication.
- The weighted KKT expression optimizes the coordinatewise-Fano lower bound; it
  is not claimed to be the exact finite weighted communication complexity.
- The prefix protocol is an illustrative upper bound, not an optimal code.
- None of these communication identities is generic evidence for simulation.

---

## Next research targets

1. Add distributed parity blocks with several rounds of communication and prove
   round-memory tradeoffs.
2. Replace independent uniform records with Markov, sparse, and structured
   sources and use conditional entropy rather than raw bit count.
3. Add quantum messages and compare classical versus entanglement-assisted
   random-access-code bounds under the same future query interface.
4. Model a causal network rather than one cut and derive min-cut or network
   coding constraints.
5. Combine noisy relational checkpoints with uncertain query distributions and
   robust optimization over a set of possible weights.
6. Lower-bound online update time when one new observation changes many future
   parity or logical-query answers.
7. Connect isolated-region replication to authenticated record comparison and
   finite-speed reconciliation.
