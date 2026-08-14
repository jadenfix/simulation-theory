# Stabilizer relations and streaming consistency

## Scope

This note asks a narrower question than “how large is a quantum state?”

> How many internally distinct predictive states are forced by an explicit set
> of future observations, especially when the information is stored in
> correlations rather than local marginals?

Two bounded constructions are used:

1. graph-state basis labels observed through stabilizer-generator queries;
2. phase-labeled cat blocks observed through distributed local-X transcripts.

Neither construction is evidence that reality is simulated. The results are
about the predictive state required by the declared internal observation model.
They do not identify the representation or resource cost of a parent substrate.

---

## 1. Graph-state basis

Let \(G=(V,E)\) be a simple graph on \(n\) qubits and define

\[
|G\rangle = \prod_{(i,j)\in E}CZ_{ij}|+\rangle^{\otimes n}.
\]

For each vertex \(i\), the standard graph-state stabilizer generator is

\[
K_i=X_i\prod_{j\in N(i)}Z_j.
\]

The graph-basis family is

\[
|G,z\rangle=Z^z|G\rangle,
\qquad z\in\{0,1\}^n.
\]

Because \(Z_i\) anticommutes with the \(X_i\) factor in \(K_i\), while every
other \(Z_j\) commutes with \(K_i\),

\[
K_iZ^z=(-1)^{z_i}Z^zK_i.
\]

Since \(K_i|G\rangle=|G\rangle\),

\[
\boxed{K_i|G,z\rangle=(-1)^{z_i}|G,z\rangle.}
\]

If \(z\ne u\), some generator has different eigenvalues on the two states, so
the states are orthogonal. Thus the family contains exactly \(2^n\) mutually
orthogonal predictive labels.

The implementation also constructs the computational-basis amplitudes

\[
\langle x|G,z\rangle
=2^{-n/2}(-1)^{\sum_{(i,j)\in E}x_ix_j+z\cdot x}
\]

and exhaustively checks the generator eigenrelation for bounded graph sizes.

---

## 2. Exact relational query geometry

Suppose query \(i\) is selected with probability \(w_i\), and the observed
outcome is the \(\pm1\) eigenvalue of \(K_i\). Then

\[
P_z(i,s)=w_i\mathbf 1\{s=(-1)^{z_i}\}.
\]

For one coordinate where \(z_i=u_i\), the conditional laws coincide. Where
they differ, the two deterministic outcome laws have disjoint support and
contribute exactly \(w_i\) to total variation. Therefore

\[
\boxed{
\operatorname{TV}(P_z,P_u)
=\sum_{i=1}^n w_i\mathbf 1\{z_i\ne u_i\}.
}
\]

For uniform generator queries,

\[
\boxed{
\operatorname{TV}(P_z,P_u)
=\frac{d_H(z,u)}{n}.
}
\]

This is an exact finite probability identity. It is not obtained by counting
Hilbert-space coordinates.

For a worst-case query chosen after the two states are specified, every
distinct pair has distance one, because a differing generator can be selected.

---

## 3. Why local marginals can forget all of the label

For a stabilizer state with stabilizer group \(\mathcal S\),

\[
\rho=2^{-n}\sum_{g\in\mathcal S}g.
\]

For the graph-basis state \(|G,z\rangle\), generator signs change, but the
support of every stabilizer element is unchanged. Let \(S\subseteq V\). When
tracing out \(S^c\), every Pauli term with nonidentity support outside \(S\)
vanishes. Hence

\[
\rho_{z,S}
=2^{-|S|}
\sum_{g:\operatorname{supp}(g)\subseteq S}
\chi_z(g)g|_S,
\]

where \(\chi_z(g)\in\{\pm1\}\) is the graph-basis sign.

Therefore:

\[
\boxed{
\rho_{z,S}=I/2^{|S|}\ \text{for every }z
\iff
I\text{ is the only stabilizer supported inside }S.
}
\]

This is the precise form of “local blindness.” It is not enough to say that a
state is entangled; one must inspect which stabilizers survive the partial
trace.

### Binary support formula

Let \(a\in\mathbb F_2^n\) select a product of graph generators. In binary
symplectic form,

\[
x=a,
\qquad z=\Gamma a,
\]

where \(\Gamma\) is the graph adjacency matrix over \(\mathbb F_2\). Thus the
Pauli support is

\[
\boxed{
\operatorname{supp}(g(a))
=\operatorname{supp}(a\lor\Gamma a).
}
\]

Equivalently, if \(A=\operatorname{supp}(a)\) and \(\operatorname{Odd}(A)\)
is the set of vertices with an odd number of neighbors in \(A\), then

\[
\operatorname{supp}(g(a))=A\cup\operatorname{Odd}(A).
\]

The code uses this identity to enumerate stabilizer support without constructing
\(2^n\)-dimensional state vectors.

---

## 4. Cycle-graph locality threshold

Consider the cycle graph \(C_n\) with \(n\ge5\).

Every generator has support on one vertex and its two neighbors, so there is a
weight-three stabilizer. This gives an upper bound of three on the minimum
nonidentity stabilizer weight.

To rule out weights one and two, take a nonempty generator index set \(A\).
Because \(A\subseteq A\cup\operatorname{Odd}(A)\), a support of size at most
two would require \(|A|\le2\).

- If \(|A|=1\), its two cycle neighbors are distinct, and the support has size
  three.
- If \(|A|=2\), direct cyclic separation shows that at least one vertex outside
  \(A\) is adjacent to exactly one selected vertex. The only cycle in which
  two selected vertices can cancel both external neighborhoods is \(C_4\).
  Therefore \(\operatorname{Odd}(A)\) contributes an external vertex for
  \(n\ge5\).

Hence

\[
\boxed{d_{\mathrm{stab}}(C_n)=3\quad(n\ge5).}
\]

Consequences:

1. every one- and two-qubit reduced density matrix is maximally mixed for every
   one of the \(2^n\) graph-basis states;
2. weight-three generator queries recover the label coordinates;
3. local state simplicity does not imply relational predictive simplicity.

This gives a sharp bounded example: **all two-body marginals are identical,
yet three-body observables expose an \(n\)-bit label.**

---

## 5. Coding-theoretic predictive packings

Under uniform generator queries, the predictive metric is normalized Hamming
distance. Let \(C\subseteq\{0,1\}^n\) be a binary code with minimum distance
\(d\). If

\[
\frac d n>2\epsilon,
\]

then the graph-basis laws indexed by \(C\) are pairwise more than
\(2\epsilon\) apart in total variation. By the repository's approximate
predictive-state packing theorem, an \(\epsilon\)-accurate renderer needs at
least \(|C|\) internal states:

\[
\boxed{
|\mathcal Z|\ge |C|,
\qquad
\text{memory}\ge\lceil\log_2|C|\rceil.
}
\]

### Finite Gilbert certificate

Let

\[
d_\epsilon=\lfloor2\epsilon n\rfloor+1
\]

and

\[
V(n,r)=\sum_{j=0}^r\binom nj.
\]

A maximal binary code of distance \(d_\epsilon\) has Hamming balls of radius
\(d_\epsilon-1\) covering the cube. Each ball contains at most
\(V(n,d_\epsilon-1)\) words, so

\[
\boxed{
|C|\ge
\left\lceil
\frac{2^n}{V(n,d_\epsilon-1)}
\right\rceil.
}
\]

This is a finite lower bound. The repository also constructs a deterministic
lexicographic greedy code and independently verifies its pairwise distances.

For example, at \(n=100\) and \(\epsilon=0.05\), the finite formula certifies
at least 55 predictive bits. This number is a consequence of the declared
uniform stabilizer-query model, not a probability estimate about simulation.

### Asymptotic rate

For constant \(0\le\epsilon<1/4\), the binary entropy estimate gives the
asymptotic achievable rate

\[
\boxed{
R(\epsilon)\ge1-H_2(2\epsilon).
}
\]

Thus a constant predictive tolerance still permits exponentially many
relational states and a memory lower bound linear in \(n\), while every
one- and two-qubit marginal remains identical in the cycle construction.

---

## 6. Cat-state parity as pure relational information

For a block of \(\ell\ge2\) qubits, define

\[
|\mathrm{Cat}_z\rangle
=\frac{|0^\ell\rangle+(-1)^z|1^\ell\rangle}{\sqrt2}.
\]

Measure each physical qubit in the \(X\) basis, writing the local outcomes as
\(x_i\in\{-1,+1\}\). Since

\[
\langle x|0^\ell\rangle=2^{-\ell/2},
\qquad
\langle x|1^\ell\rangle=2^{-\ell/2}\prod_i x_i,
\]

we obtain

\[
\langle x|\mathrm{Cat}_z\rangle
=2^{-(\ell+1)/2}
\left(1+(-1)^z\prod_i x_i\right).
\]

Therefore

\[
\boxed{
P_z(x_1,\ldots,x_\ell)
=
\begin{cases}
2^{-(\ell-1)},&\prod_i x_i=(-1)^z,\\
0,&\text{otherwise}.
\end{cases}
}
\]

The two phase laws have disjoint complete-transcript supports, so their total
variation is one.

But fix any proper subset of \(k<\ell\) outcomes. For every assignment to
those outcomes, exactly half of the completions satisfy either required global
parity. Summing over the unobserved outcomes gives

\[
\boxed{
P_z(x_S)=2^{-k}
\quad\text{for every proper }S,
}
\]

independent of \(z\).

This is stronger than “each individual outcome is random.” Every incomplete
local record is phase-blind; only the completed relation carries the bit.

For \(m\) independent cat blocks labeled by
\(z\in\{0,1\}^m\), there are \(2^m\) complete transcript laws with disjoint
supports. A selected marginal distinguishes two labels exactly when it includes
every qubit of at least one block on which their phase labels differ.

---

## 7. Exact online consistency memory

Now view the same experiment as an online rendering problem.

Suppose the renderer has already emitted \(\ell-1\) local outcomes in every
block. Let

\[
p_b=\prod_{j=1}^{\ell-1}x_{b,j}
\]

be the observed prefix parity in block \(b\). The final outcome must satisfy

\[
p_bx_{b,\ell}=(-1)^{z_b},
\]

so

\[
\boxed{x_{b,\ell}=(-1)^{z_b}p_b.}
\]

For a fixed hidden label \(z\), every prefix-parity vector

\[
p\in\{-1,+1\}^m
\]

occurs, and the map

\[
p\mapsto((-1)^{z_1}p_1,\ldots,(-1)^{z_m}p_m)
\]

is bijective. Two distinct parity vectors disagree on some future block query,
and that query requires opposite deterministic outcomes. Therefore the
checkpoint has exactly \(2^m\) predictive-equivalence classes:

\[
\boxed{
|\mathcal Z_{\mathrm{checkpoint}}|=2^m,
\qquad
\text{dynamic memory}=m\text{ bits}.
}
\]

This is both a lower and an upper bound.

- **Lower bound:** distinct parity signatures induce distinct future laws.
- **Upper bound:** retaining one accumulated parity bit per block is sufficient;
  the full local-outcome history may be discarded.

So the theorem does not say that a renderer must remember every generated bit.
It identifies the minimal relational sufficient statistic that cannot be
forgotten.

### Approximate worst-query version

Distinct signatures have worst-future-query total variation one. If one
renderer state were within \(\epsilon\) of both, the triangle inequality would
imply

\[
1\le2\epsilon.
\]

Hence for every \(\epsilon<1/2\), the same \(m\)-bit lower bound remains:

\[
\boxed{
\epsilon<1/2
\implies
\text{memory}\ge m.
}
\]

### Random final-block query

If the final block is selected uniformly rather than adversarially, two parity
signatures have distance

\[
\operatorname{TV}=\frac{d_H(p,u)}m.
\]

The same finite Gilbert and asymptotic coding bounds therefore apply. Even
under constant average-query tolerance, a positive linear fraction of the
\(m\) consistency bits remains necessary.

---

## 8. What this adds to the simulation discussion

The result targets a gap in informal “render only when observed” reasoning.
Generating each local answer with the correct marginal is insufficient. A
renderer must preserve the relations needed for later cross-checks.

The cat construction isolates the burden:

- every early local answer can be perfectly unbiased;
- every proper partial record can look exactly phase-independent;
- the final answer is nevertheless constrained by all earlier answers;
- one parity bit per open correlation block is necessary and sufficient.

The graph-state construction adds a different lesson:

- exponentially many labels may share every one- and two-body marginal;
- bounded-weight relational observables can still expose a linear number of
  predictive bits;
- coding converts exact coordinate information into robust constant-tolerance
  lower bounds.

These are internal consistency theorems, not generic simulation detectors.
An exact simulator can satisfy them by maintaining an adequate predictive
state. The results constrain only architectures that attempt to discard too
much relational information.

---

## Nonclaims

- Graph states, stabilizers, Bell correlations, or cat-state parity are not
  evidence that reality is simulated.
- Internal predictive bits are not parent-universe RAM bits.
- Identical low-order marginals do not imply indistinguishability under an
  adaptive protocol that eventually aggregates a global transcript.
- The cycle result concerns the declared graph-basis and generator-query
  family, not arbitrary many-body quantum matter.
- The cat checkpoint result assumes exact phase-parity transcript laws and the
  specified future query interface.
- The asymptotic coding rate is not a finite certificate for a particular
  block length; finite claims use the explicit Hamming-ball formula.

---

## Next research target

The next extension should replace exact parity constraints with noisy and
approximate ones. High-value directions are:

1. noisy cat blocks and rate-distortion bounds for approximate consistency;
2. stabilizer and quantum-error-correcting code families with larger local
   indistinguishability distance;
3. spacetime-distributed observers with communication constraints;
4. lower bounds on update time, not just stored predictive state;
5. tensor-network families where bond dimension controls accessible relational
   memory.
