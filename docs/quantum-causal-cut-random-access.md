# Quantum random-access causal-cut bounds

## Scope

The classical causal-cut result asks how much record information must reach a
later region before an unresolved future coordinate query is revealed. This
note allows the message to be quantum.

A uniformly random record

\[
X=(X_1,\ldots,X_m)\in\{0,1\}^m
\]

is encoded into a \(q\)-qubit system \(Q\). Only after \(Q\) reaches the
answering region is the query index \(I\in[m]\) revealed. For each possible
query \(i\), the receiver may choose a different measurement on \(Q\) and
output \(\widehat X_i\).

This is a quantum random access code interface. Two resource models are kept
separate:

1. **unassisted:** no prior receiver system is correlated with the sender's
   encoder;
2. **entanglement assisted:** sender and receiver may share entanglement that is
   independent of the later record \(X\), and the sender transmits \(q\) qubits.

The results are ordinary finite-dimensional quantum-information bounds. They do
not establish that reality is simulated and do not identify the hardware or
physics of an unknown parent substrate.

---

## Unassisted quantum random-access lower bound

Let the encoding of record \(x\) be the density operator

\[
\rho_x^Q.
\]

The joint classical-quantum state is

\[
\rho^{XQ}
=
2^{-m}\sum_x|x\rangle\langle x|\otimes\rho_x^Q.
\]

For query \(i\), let a measurement on \(Q\) produce \(\widehat X_i\), with

\[
e_i=P(\widehat X_i\ne X_i).
\]

### Measurement data processing

The measurement outcome is obtained by a channel from \(Q\), so

\[
I(X_i;Q)
\ge
I(X_i;\widehat X_i).
\]

Since \(X_i\) is a uniform bit, binary Fano gives

\[
I(X_i;\widehat X_i)
=
1-H(X_i\mid\widehat X_i)
\ge
1-H_2(e_i).
\]

Therefore

\[
\boxed{
I(X_i;Q)
\ge
1-H_2(e_i).
}
\]

### Combining coordinates

The source bits are independent, so \(H(X)=m\). Conditional entropy
subadditivity, equivalent to nonnegative conditional mutual information, gives

\[
H(X\mid Q)
\le
\sum_{i=1}^mH(X_i\mid Q).
\]

Hence

\[
\begin{aligned}
I(X;Q)
&=m-H(X\mid Q)\\
&\ge
m-\sum_iH(X_i\mid Q)\\
&=
\sum_iI(X_i;Q)\\
&\ge
\sum_i[1-H_2(e_i)].
\end{aligned}
\]

Thus the quantum encoding must contain at least the aggregate information
needed by all possible post-message measurements:

\[
\boxed{
I(X;Q)
\ge
\sum_i[1-H_2(e_i)].
}
\]

### Entropy capacity of q qubits

For a classical-quantum ensemble,

\[
I(X;Q)
=
H(Q)-2^{-m}\sum_xH(\rho_x^Q)
\le
H(Q).
\]

A \(q\)-qubit system has dimension \(2^q\), so

\[
H(Q)
\le
\log_2(2^q)
=q.
\]

Combining the bounds gives

\[
\boxed{
q
\ge
\sum_{i=1}^m[1-H_2(e_i)].
}
\]

For a uniform future query with average error

\[
\frac1m\sum_i e_i\le\epsilon,
\]

concavity of binary entropy gives

\[
\boxed{
q
\ge
m[1-H_2(\epsilon)].
}
\]

At zero error,

\[
\boxed{q\ge m.}
\]

This lower bound is tight: encode the record as the computational-basis state
\(|x\rangle\) of \(m\) qubits. The receiver can measure the requested qubit or
the complete register.

The theorem does not follow from the continuum of pure quantum states. Although
one qubit admits infinitely many state vectors, its accessible classical mutual
information in this unassisted ensemble is bounded by one bit.

---

## Entanglement-assisted quantum cut

Suppose sender and receiver initially share an arbitrary state on systems
\(A\) and \(B\), independent of \(X\). The sender applies an \(X\)-dependent
operation to \(A\), sends a \(q\)-qubit system \(Q\), and the receiver answers
using \(BQ\).

Before transmission,

\[
I(X;B)=0
\]

because the preshared entanglement was established independently of the later
record.

After transmission,

\[
I(X;BQ)
=
I(X;B)+I(X;Q\mid B)
=
I(X;Q\mid B).
\]

The conditional mutual information can be written

\[
I(X;Q\mid B)
=
H(Q\mid B)-H(Q\mid XB).
\]

Two dimension bounds apply:

\[
H(Q\mid B)
\le H(Q)
\le q,
\]

and the Araki-Lieb inequality gives

\[
H(Q\mid XB)
\ge-H(Q)
\ge-q.
\]

Therefore

\[
\boxed{
I(X;BQ)
\le2q.
}
\]

The coordinate measurements are now performed on \(BQ\), but the same data
processing and binary-Fano lower bound applies:

\[
I(X;BQ)
\ge
\sum_i[1-H_2(e_i)].
\]

Consequently

\[
\boxed{
q
\ge
\frac12
\sum_i[1-H_2(e_i)].
}
\]

and, under a uniform average query error,

\[
\boxed{
q
\ge
\frac m2[1-H_2(\epsilon)].
}
\]

Entanglement can improve the constant by at most a factor of two in this model;
it does not remove the linear dependence on the number of unresolved record
bits.

---

## Exact dense-coding achievability

The factor two is tight for exact full-record transmission.

For each preshared Bell pair, the sender can choose one of four local Pauli
operations, producing four orthogonal Bell states. Sending the sender's half of
the pair lets the receiver perform a Bell measurement and recover two classical
bits.

Thus \(q\) transmitted qubits, together with \(q\) preshared Bell pairs, carry

\[
\boxed{2q\text{ exact classical bits}.}
\]

An \(m\)-bit record can be transmitted exactly using

\[
\boxed{
q=\left\lceil\frac m2\right\rceil
}
\]

qubits, padding an odd final bit with one dummy bit if necessary. This matches
the entanglement-assisted zero-error lower bound.

By contrast, without entanglement exact transmission needs \(m\) qubits.

The resource statement counts transmitted qubits and explicitly assumes the
preshared Bell pairs already exist. It does not claim that entanglement is free
under every physical accounting system.

---

## Query-timing phase change

If the query index is revealed **before** the sender prepares the message, the
sender only needs to encode the requested one-bit answer. Two orthogonal qubit
states suffice:

\[
\boxed{q=1.}
\]

If the query remains unresolved until after the message crosses the cut, exact
unassisted communication requires \(m\) qubits and exact entanglement-assisted
communication requires \(\lceil m/2\rceil\) transmitted qubits.

Thus the same future question family changes from constant to linear
communication depending only on when the query becomes available. A lazy
rendering argument that omits query timing omits the main causal-complexity
assumption.

---

## Inverting the information bound

For a fixed qubit budget, the converse can be written as a minimum error.

### Unassisted

If \(q<m\),

\[
m[1-H_2(\epsilon)]
\le q,
\]

so

\[
H_2(\epsilon)
\ge1-\frac qm.
\]

Since \(H_2\) is strictly increasing on \([0,1/2]\),

\[
\boxed{
\epsilon
\ge
H_2^{-1}\left(1-\frac qm\right).
}
\]

### Entanglement assisted

The accessible-information ceiling becomes \(2q\):

\[
\boxed{
\epsilon
\ge
H_2^{-1}\left(1-\frac{2q}{m}\right)
}
\]

when \(2q<m\), and the bound becomes zero once \(2q\ge m\).

The repository implements a deterministic inverse of binary entropy on
\([0,1/2]\). This is a converse bound. It does not assert that every finite
parameter pair has a code attaining equality.

---

## Canonical two-to-one qubit random access code

The lower bound permits a one-qubit encoding of two bits with nonzero error.
A concrete construction uses four pure states with Bloch vectors

\[
r_{x_1x_2}
=
\frac1{\sqrt2}
\left(
(-1)^{x_1},
0,
(-1)^{x_2}
\right).
\]

To retrieve \(x_1\), measure Pauli \(X\). To retrieve \(x_2\), measure Pauli
\(Z\). For a projective measurement along unit axis \(a\), the probability of
outcome sign \(s\in\{-1,+1\}\) is

\[
P(s\mid r,a)
=
\frac{1+s\,r\cdot a}{2}.
\]

The desired sign is \((-1)^{x_i}\), and its dot product with the corresponding
axis is \(1/\sqrt2\). Therefore every record-query pair succeeds with

\[
\boxed{
p_{2\to1}
=
\frac12\left(1+\frac1{\sqrt2}\right)
\approx0.853553.
}
\]

The error is

\[
\boxed{
\epsilon_{2\to1}
=
\frac12\left(1-\frac1{\sqrt2}\right)
\approx0.146447.
}
\]

The one-qubit Fano converse only requires

\[
\epsilon
\ge
H_2^{-1}(1/2)
\approx0.110028,
\]

so this simple symmetric construction does not saturate the entropy lower
bound. The gap is recorded rather than hidden.

The implementation enumerates all four records and both queries and independently
checks the same average success.

---

## Canonical three-to-one qubit random access code

A single qubit can also encode three bits with lower success. Use the eight cube
vertices

\[
r_{x_1x_2x_3}
=
\frac1{\sqrt3}
\left(
(-1)^{x_1},
(-1)^{x_2},
(-1)^{x_3}
\right).
\]

Queries measure Pauli \(X\), \(Y\), or \(Z\). Each desired component has
magnitude \(1/\sqrt3\), so

\[
\boxed{
p_{3\to1}
=
\frac12\left(1+\frac1{\sqrt3}\right)
\approx0.788675
}
\]

and

\[
\boxed{
\epsilon_{3\to1}
=
\frac12\left(1-\frac1{\sqrt3}\right)
\approx0.211325.
}
\]

The one-qubit information converse gives

\[
\epsilon
\ge
H_2^{-1}(2/3)
\approx0.173952.
\]

Again the explicit construction obeys but does not saturate the general lower
bound.

These examples demonstrate the correct nuance:

- one qubit cannot preserve two or three unresolved bits exactly;
- it can preserve enough geometry to answer one later-chosen bit with advantage
  over random guessing;
- the tradeoff must be stated in terms of query error, not the number of
  continuous amplitudes in a qubit state.

---

## Weighted quantum queries

If the future query distribution has weights \(w_i\) and weighted average error
at most \(\epsilon\), the classical coordinatewise-Fano optimization from the
distributed causal-cut result still lower-bounds the quantum mutual
information. Let \(e_i(\lambda)\) solve

\[
e_i(\lambda)
=
\frac1{1+2^{\lambda w_i}},
\qquad
\sum_iw_ie_i(\lambda)=\epsilon.
\]

Then the unassisted bound is

\[
\boxed{
q
\ge
\sum_i[1-H_2(e_i(\lambda))]
}
\]

and the entanglement-assisted bound is

\[
\boxed{
q
\ge
\frac12
\sum_i[1-H_2(e_i(\lambda))].
}
\]

Quantum encoding changes the capacity side of the argument, while the
query-distribution sensitivity remains the same. Rarely queried coordinates can
be represented less accurately; zero-weight coordinates need carry no
predictive information under the declared loss.

---

## What this adds to the simulation discussion

Quantum state space is sometimes invoked as though continuous amplitudes let a
finite quantum register carry arbitrarily many retrievable classical facts. The
random-access calculation identifies the missing condition: **retrievability
under a later-chosen query**.

A one-qubit density matrix has continuous parameters, but an unresolved family
of reliable classical coordinate queries is constrained by accessible mutual
information. Quantum geometry permits useful approximate codes, but the number
of qubits remains linear in \(m\) at fixed error below one half.

Preshared entanglement changes the constant because sending one qubit can alter
the receiver's classical mutual information by at most two bits. Superdense
coding attains that factor two for exact transmission. It does not create
unbounded classical predictive capacity.

For an internal on-demand renderer, this means:

- replacing classical state with quantum state does not erase the causal-cut
  information requirement;
- the relevant resource is the number and accuracy of future classical queries,
  not raw amplitude count;
- query timing remains decisive;
- entanglement-assisted and unassisted architectures must not be mixed;
- none of the bounds distinguishes an exact simulator from ordinary quantum
  physics, because both can obey the same internal law.

---

## Nonclaims

- The proof assumes ordinary finite-dimensional quantum entropy and data
  processing identities.
- Qubits in the internal model are not parent-universe qubits or hardware units.
- Preshared entanglement is an explicit resource assumption and is not free
  under every physical accounting.
- The entanglement-assisted bound concerns the increase in receiver information
  caused by transmitted qubits; it does not count the storage needed to hold
  the preshared entanglement.
- The two-to-one and three-to-one constructions are finite upper examples, not
  universal optimality proofs derived in this repository.
- Inverting the Fano bound gives a necessary error, not an achievable error for
  every finite parameter pair.
- Weighted-query bounds inherit the assumptions and limitations of the
  coordinatewise-Fano optimization.
- Quantum random access coding and superdense coding are not evidence that
  reality is simulated.

---

## Next research targets

1. Add explicit entanglement-assisted random-access protocols beyond full dense
   coding and compare their finite errors.
2. Extend from classical record bits to logical qubits and entanglement fidelity.
3. Derive quantum-memory plus quantum-communication cut tradeoffs.
4. Add several causal rounds and expose exactly when revealing the query reduces
   communication.
5. Model multiple answering regions and relate replication to monogamy and
   no-cloning constraints without overclaiming.
6. Compare shared randomness, shared entanglement, and record-dependent shared
   quantum memory under one accounting framework.
7. Build finite semidefinite-program certificates for small random access codes
   if a verified numerical dependency is introduced later.
