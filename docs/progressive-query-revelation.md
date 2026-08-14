# Progressive query revelation and multiround causal cuts

## Scope

The one-way causal-cut results study the hardest timing regime:

1. a hidden record \(X\in\{0,1\}^m\) is fixed;
2. all record-dependent communication crosses a cut;
3. only afterward is the requested coordinate \(I\) revealed.

Exact answering then requires preserving all \(m\) record bits across the cut.

That result changes when the future query is revealed progressively. This note
models one intermediate hint:

1. a shared message or state \(M_0\) crosses before any query hint;
2. a hint reveals one cell \(C_j\) of a partition of the coordinates;
3. a cell-specific message or state \(M_j\) crosses;
4. only then is the exact coordinate \(I\in C_j\) revealed.

The question is:

> How much information must be committed before the hint, and how much can be
> deferred until the residual query set is known?

The answer separates three different uncertainties:

- **record uncertainty:** which binary record occurred;
- **query uncertainty:** which coordinates can still be requested;
- **timing:** which messages may depend on which query information.

The results are ordinary communication and quantum-information statements for
this declared interface. They are not evidence that reality is simulated and do
not identify the physical representation of an unknown parent substrate.

---

## 1. Query partitions

Let

\[
[m]=C_1\sqcup C_2\sqcup\cdots\sqcup C_b
\]

be a partition into nonempty cells, with

\[
s_j=|C_j|,
\qquad
\sum_{j=1}^b s_j=m.
\]

The intermediate hint reveals \(J=j\), meaning only that the final query lies
inside \(C_j\). The exact coordinate \(I\in C_j\) remains unresolved until
after the second message.

A protocol has:

- a shared encoder

  \[
  f_0:\{0,1\}^m\to\mathcal M_0;
  \]

- one branch encoder for every cell,

  \[
  f_j:\{0,1\}^m\to\mathcal M_j;
  \]

- decoders

  \[
  g_j:\mathcal M_0\times\mathcal M_j\times C_j\to\{0,1\}.
  \]

For exact classical communication, write

\[
|\mathcal M_0|\le 2^a,
\qquad
|\mathcal M_j|\le 2^{c_j}.
\]

The exact requirement is

\[
g_j(f_0(x),f_j(x),i)=x_i
\]

for every record \(x\), every cell \(j\), and every \(i\in C_j\).

The second-stage message is branch-specific. In one execution only \(M_J\)
crosses, not all \(M_1,\ldots,M_b\). Nevertheless, the family of all branch
encoders constrains how much of the record may be omitted from the common
message.

---

## 2. Exact classical tradeoff

### Theorem

An exact progressive classical protocol with shared budget \(a\) and branch
budgets \(c_1,\ldots,c_b\) exists if and only if

\[
\boxed{
a\ge
\sum_{j=1}^b\max(0,s_j-c_j).
}
\]

Equivalently,

\[
\boxed{
a+\sum_{j=1}^b\min(c_j,s_j)\ge m.
}
\]

The two expressions are identical because

\[
s_j=\min(c_j,s_j)+\max(0,s_j-c_j).
\]

### Necessity: fiber counting

Fix one shared-message value \(u\in\mathcal M_0\), and let

\[
F_u=\{x:f_0(x)=u\}
\]

be its fiber.

For a fixed cell \(C_j\), consider the restrictions

\[
x_{C_j}
\qquad
x\in F_u.
\]

There can be at most \(2^{c_j}\) distinct restrictions. Otherwise two records
\(x,x'\in F_u\) would:

- share the common message \(u\);
- share a branch message by the pigeonhole principle;
- differ on some coordinate \(i\in C_j\).

The decoder would then receive the same \((u,f_j(x),i)\) in both worlds and
could not answer both correctly.

There are at most \(2^{s_j}\) possible cell restrictions in total, so

\[
|\{x_{C_j}:x\in F_u\}|
\le
2^{\min(c_j,s_j)}.
\]

A complete record is the tuple of its cell restrictions. Hence

\[
|F_u|
\le
\prod_{j=1}^b
2^{\min(c_j,s_j)}
=
2^{\sum_j\min(c_j,s_j)}.
\]

There are at most \(2^a\) shared-message fibers, so

\[
2^m
\le
2^a
2^{\sum_j\min(c_j,s_j)}.
\]

Taking base-two logarithms gives

\[
a+\sum_j\min(c_j,s_j)\ge m.
\]

### Sufficiency: store exactly the uncovered bits

For each cell, let

\[
r_j=\max(0,s_j-c_j).
\]

Store any \(r_j\) bits from \(C_j\) in the shared message. After hint \(J=j\),
send the remaining

\[
s_j-r_j=\min(c_j,s_j)
\]

bits of that cell.

The shared message uses

\[
\sum_jr_j
=
\sum_j\max(0,s_j-c_j)
\le a
\]

bits. The branch message respects its \(c_j\)-bit budget. Once the final
coordinate is revealed, its value is present either in the common message or in
the selected branch message.

Thus the lower bound is exactly achievable.

The repository constructs this protocol explicitly and exhaustively checks all
records and later coordinates for bounded record sizes.

---

## 3. Equal-cell phase diagram

Suppose there are \(b\) equal cells of size \(s\), so

\[
m=bs.
\]

Let every branch have the same budget \(c\). The exact condition becomes

\[
\boxed{
a+b\min(c,s)\ge bs.
}
\]

When \(0\le c\le s\),

\[
\boxed{
a+bc\ge m.
}
\]

### One-round endpoint

With one cell, \(b=1\) and \(s=m\). The condition is

\[
a+c\ge m,
\]

which recovers the original post-message INDEX bound.

### Exact-query hint endpoint

With singleton cells, \(b=m\) and \(s=1\). Setting \(a=0\) and \(c=1\)
suffices. Only one bit crosses in the executed branch because the hint has
already identified the exact coordinate.

### Intermediate hint

With \(a=0\), the selected cell must be transmitted:

\[
c\ge s.
\]

Therefore exact per-execution communication is

\[
\boxed{s}
\]

bits. A hint that reduces the unresolved query set from \(m\) coordinates to
\(s\) coordinates reduces exact communication by the factor

\[
\boxed{\frac ms=b.}
\]

This is not a \(\log_2s\) dependence. The sender does not merely identify which
coordinate will be asked. It must preserve the values of all \(s\) coordinates
because the final choice remains unresolved.

### Why common communication is inefficient after a useful hint

For equal cells and a fixed per-run objective \(a+c\), the constraint is

\[
a+bc\ge bs.
\]

Increasing branch capacity by one bit costs one bit in the realized execution
but contributes one bit of capacity in every possible branch of the design.
Increasing the pre-hint shared message by one bit also costs one bit per
execution but contributes only one unit to the global inequality.

For \(b>1\), the minimum of \(a+c\) is therefore attained at

\[
a=0,\qquad c=s.
\]

This is a timing theorem: when later communication is allowed after the cell
hint, committing record bits before that hint is not communication-optimal in
the unconstrained exact model.

It may still be necessary under latency, one-way availability, or second-round
capacity limits. The exact tradeoff quantifies that architectural price.

---

## 4. Bounded-error branch-aware converse

Now let the record bits be independent and uniform:

\[
X_1,\ldots,X_m
\overset{\mathrm{iid}}{\sim}
\operatorname{Bernoulli}(1/2).
\]

For coordinate \(i\in C_j\), the decoder uses \((M_0,M_j)\) and has error

\[
e_i=P(\widehat X_i\ne X_i),
\qquad
0\le e_i\le\frac12.
\]

Define the information requirement of cell \(j\):

\[
\boxed{
R_j
=
\sum_{i\in C_j}
[1-H_2(e_i)].
}
\]

### Lower bound inside one cell

By data processing and binary Fano,

\[
I(X_i;M_0,M_j)
\ge
I(X_i;\widehat X_i)
\ge
1-H_2(e_i).
\]

The bits inside a cell are independent. Conditional entropy subadditivity gives

\[
I(X_{C_j};M_0,M_j)
\ge
\sum_{i\in C_j}
I(X_i;M_0,M_j).
\]

Therefore

\[
\boxed{
I(X_{C_j};M_0,M_j)\ge R_j.
}
\]

### How much of one cell can the branch message supply?

By the chain rule,

\[
I(X_{C_j};M_0,M_j)
=
I(X_{C_j};M_0)
+
I(X_{C_j};M_j\mid M_0).
\]

A \(c_j\)-bit branch message contributes at most \(c_j\) bits:

\[
I(X_{C_j};M_j\mid M_0)
\le
H(M_j)
\le c_j.
\]

Hence the shared message must contain at least

\[
\boxed{
I(X_{C_j};M_0)
\ge
\max(0,R_j-c_j).
}
\]

### Summing shared information across independent cells

Because the source blocks \(X_{C_1},\ldots,X_{C_b}\) are independent,

\[
\sum_j I(X_{C_j};M_0)
\le
I(X;M_0).
\]

A shared message with at most \(2^a\) values satisfies

\[
I(X;M_0)\le H(M_0)\le a.
\]

Combining the inequalities gives the branch-aware converse

\[
\boxed{
a
\ge
\sum_{j=1}^b
\max(0,R_j-c_j).
}
\]

Equivalently,

\[
\boxed{
a+\sum_j\min(c_j,R_j)
\ge
\sum_jR_j.
}
\]

This is the approximate analogue of the exact uncovered-bit theorem.

It is a necessary information condition. Unlike the zero-error result, it is
not asserted to be sufficient for every finite block length and arbitrary error
profile.

---

## 5. Uniform-error consequences

Suppose every coordinate has error at most or exactly the same value
\(\epsilon\). Then

\[
R_j
=
s_j[1-H_2(\epsilon)].
\]

Summing over all cells gives

\[
\boxed{
a+\sum_jc_j
\ge
m[1-H_2(\epsilon)]
}
\]

as a weaker total-capacity consequence.

For \(b\) equal cells of size \(s\), equal branch budgets, and the per-execution
objective \(a+c\), the branch-aware inequality again favors deferring capacity
until after the hint. Optimizing gives

\[
\boxed{
a+c
\ge
s[1-H_2(\epsilon)].
}
\]

Thus the information converse depends on the **residual query cell size** rather
than the original record length:

\[
\boxed{
\text{per-run information}
\gtrsim
s[1-H_2(\epsilon)].
}
\]

Boundary checks:

- \(\epsilon=0\) gives \(s\);
- \(\epsilon=1/2\) gives zero;
- one cell with \(s=m\) recovers the one-way random-access bound;
- singleton cells give one-bit binary-Fano requirements per selected branch.

Again, this is a converse. A finite classical code attaining equality is not
claimed for every \((s,\epsilon)\).

---

## 6. Unassisted quantum messages

Replace \(M_0,M_j\) by quantum systems \(Q_0,Q_j\). Suppose the receiver has no
preshared system correlated with the encoder.

Let \(q_0\) and \(q_j\) be the transmitted qubit counts. The same decoding and
binary-Fano argument gives

\[
I(X_{C_j};Q_0Q_j)\ge R_j.
\]

The branch message adds at most its entropy:

\[
I(X_{C_j};Q_j\mid Q_0)
\le
H(Q_j)
\le q_j.
\]

Therefore

\[
I(X_{C_j};Q_0)
\ge
\max(0,R_j-q_j).
\]

Independence of the cells and the \(q_0\)-qubit entropy ceiling imply

\[
\sum_jI(X_{C_j};Q_0)
\le
I(X;Q_0)
\le q_0.
\]

Hence

\[
\boxed{
q_0
\ge
\sum_j\max(0,R_j-q_j).
}
\]

The continuous state space of a qubit does not alter the result. What matters
is how much classical information remains recoverable under a later-selected
measurement.

### Exact unassisted tradeoff

At zero error, \(R_j=s_j\), so exact feasibility requires

\[
\boxed{
q_0
\ge
\sum_j\max(0,s_j-q_j).
}
\]

It is also sufficient: encode selected record bits in computational-basis
qubits, placing uncovered cell bits in the shared stage and the rest in each
branch stage.

Thus the exact classical and unassisted-quantum tradeoffs coincide when one bit
or one qubit is counted as one exactly retrievable classical coordinate value.

For equal cells, the exact per-run lower and upper bound is

\[
\boxed{s\text{ unassisted qubits}.}
\]

---

## 7. Entanglement-assisted quantum messages

Now allow the receiver to hold preshared entanglement independent of \(X\).
Sending \(q\) qubits can increase receiver classical mutual information by at
most \(2q\).

The branch-specific increment obeys

\[
I(X_{C_j};Q_j\mid Q_0B)
\le 2q_j,
\]

where \(B\) denotes the receiver's prior entangled system. Likewise, the shared
stage can create at most \(2q_0\) bits of record information.

The branch-aware converse becomes

\[
\boxed{
2q_0
\ge
\sum_j\max(0,R_j-2q_j).
}
\]

At zero error,

\[
\boxed{
2q_0
\ge
\sum_j\max(0,s_j-2q_j).
}
\]

This is achievable with dense coding: assign record bits to the common and
branch stages, then use one preshared Bell pair and one transmitted qubit for
each pair of classical bits.

For equal cells, exact per-execution transmitted qubits are

\[
\boxed{
\left\lceil\frac s2\right\rceil.
}
\]

The factor two concerns transmitted qubits. The theorem does not count the
storage, creation, or distribution cost of the preshared entanglement.

For uniform error, the per-run converse is

\[
\boxed{
q_0+q_J
\ge
\frac{s}{2}[1-H_2(\epsilon)]
}
\]

after optimizing the timing allocation in the symmetric model.

---

## 8. A general capacity-unit formulation

The exact formulas depend only on how many classical record bits one resource
unit can transmit exactly in the declared assistance model.

Let

\[
\kappa=
\begin{cases}
1,&\text{classical bit or unassisted transmitted qubit},\\
2,&\text{entanglement-assisted transmitted qubit}.
\end{cases}
\]

If the shared stage has \(u_0\) units and branch \(j\) has \(u_j\) units, the
exact criterion is

\[
\boxed{
\kappa u_0
\ge
\sum_j\max(0,s_j-\kappa u_j).
}
\]

The repository exposes this through a typed budget object. The abstraction is
only bookkeeping. It does not claim every physical carrier has an integer,
context-independent capacity multiplier.

---

## 9. Query information versus record information

A hint identifying one of \(b\) equal cells can itself be represented using

\[
\log_2 b
\]

bits when the cells are equally likely. Yet it can reduce exact record
communication from \(m\) to

\[
s=\frac mb.
\]

This does not violate information accounting because the hint does not reveal
record values. It changes **which subset of values must remain recoverable**.

The correct decomposition is:

- hint information reduces the future query family;
- record communication preserves values for the residual family.

The two kinds of information are not interchangeable. A million bits of query
metadata cannot answer one record bit unless it is correlated with the record.
Conversely, one well-timed query hint can make most record coordinates
irrelevant to that execution.

This distinction is central to on-demand rendering:

> The cost of deferred commitment is controlled by the set of observations that
> remain jointly possible at each causal stage.

---

## 10. Progressive predictive equivalence

The theorem can be phrased without communication language.

Before the hint, two records are predictively equivalent only if every future
branch can still answer every coordinate. After hint \(J=j\), equivalence needs
only preserve coordinates in \(C_j\).

Thus the predictive partition coarsens over time:

\[
\{0,1\}^m
\longrightarrow
\{0,1\}^{C_j}
\longrightarrow
\{0,1\}^{\{i\}}.
\]

The number of exact future-law classes changes from

\[
2^m
\]

before any hint, to

\[
2^{s_j}
\]

after cell \(j\), and finally to

\[
2
\]

after the exact coordinate is known but before its value is communicated.

The multiround protocol is a mechanism for paying only for the distinctions
that remain live at each stage. The exact tradeoff identifies which distinctions
must be carried early because later branch channels cannot supply enough of
them.

---

## 11. What this changes in simulation arguments

### “Render later” is incomplete without a query-revelation schedule

If the exact future observation is known before generation, one answer bit may
suffice. If only a coarse region of possible observations is known, all values
inside that region remain live. If no hint is available, the entire record may
need to remain recoverable.

### Precomputation and late communication are substitutable, but not one-for-one

For \(b\) equal branches, one bit of extra capacity in every possible late
branch can replace \(b\) bits of shared design deficit while costing only one
bit in the realized execution. The timing topology matters.

### Quantum state does not erase the residual-query burden

Unassisted qubits obey the same one-bit accessible-information coefficient.
Entanglement assistance supplies the dense-coding factor two and no more under
the declared model.

### Approximation changes cell size into cell information

At error \(\epsilon\), the exact requirement \(s_j\) becomes the Fano quantity

\[
s_j[1-H_2(\epsilon)]
\]

for a uniform cell. This is a predictive information requirement, not a claim
that every implementation must literally store a compressed binary string of
that length.

### A simulator could satisfy every theorem

An exact simulator can maintain sufficient common state and transmit or compute
the selected branch state after a query hint. These results constrain one
architecture; they do not distinguish simulation from ordinary physical
evolution.

---

## 12. Nonclaims

- The partition hint model is not asserted to describe actual observation
  timing in the universe.
- The exact classical theorem assumes finite zero-error messages and a binary
  record.
- The bounded-error converse assumes independent uniform source bits.
- The Fano information inequalities are necessary conditions, not universal
  finite-block achievability theorems.
- Branch capacities are design budgets; only the selected branch is executed in
  one run.
- Shared and branch messages are allowed to depend on the complete record at
  their permitted times.
- Entanglement is assumed independent of the later record.
- The factor-two assisted coefficient counts transmitted qubits but not
  entanglement storage or distribution.
- Bits and qubits in the internal model are not parent-substrate hardware,
  energy, mass, or spacetime volume.
- Query hints are not evidence for simulation.
- The theorem does not yet cover overlapping hint sets, adaptive noisy hints,
  multiple query rounds, or general causal networks.

---

## 13. Next research targets

1. Replace a partition by overlapping query sets and characterize the resulting
   set-cover or fractional-cover capacity region.
2. Allow several successive hints and derive a tree-recursive capacity theorem.
3. Build a directed causal network and prove min-cut predictive-class bounds.
4. Add noisy or uncertain hints and integrate over the posterior query set.
5. Track latency and round complexity in addition to information capacity.
6. Study multiple answer regions with shared prefixes and branch-specific
   caches.
7. Extend from coordinate queries to arbitrary finite function families, where
   the relevant quantity is the number of predictive-equivalence classes.
8. Add dynamic records and lower-bound the update work needed to keep every
   future branch consistent.
