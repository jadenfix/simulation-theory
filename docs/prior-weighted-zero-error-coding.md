# Prior-weighted zero-error predictive coding

## Scope

The confusion-graph theorem answers a worst-case one-shot alphabet question. If
one common message must let every sink recover its declared target from that
message and its local side information, then the exact minimum number of
message values is the chromatic number

\[
\chi(G).
\]

A fixed binary label for those values needs

\[
\left\lceil\log_2\chi(G)\right\rceil
\]

bits in every execution.

That does **not** determine average communication under a nonuniform source
prior. This lane adds a different, explicitly declared interface:

- a finite confusion graph \(G\);
- an exact rational source prior \(\pi\);
- zero error on either every declared state or only the positive support;
- one binary prefix-coded message;
- a codebook known to encoder and decoder;
- expected bit length as the optimization objective.

The result is an exact bounded one-shot source-coding theorem. It is not an
asymptotic graph-entropy theorem, a queueing theorem, a hard network-capacity
theorem, or evidence for simulation. Message bits are internal model resources,
not parent-substrate energy, mass, memory, or spacetime.

---

## 1. From future demands to independent message classes

Let

\[
V=\{0,\ldots,n-1\}
\]

be the finite source-state set and let

\[
G=(V,E)
\]

be its confusion graph. An edge \(\{x,y\}\) means that some sink receives the
same local side information under \(x\) and \(y\) but requires different target
answers. Those two states cannot share a zero-error message.

A deterministic zero-error encoder therefore induces a partition

\[
\mathcal P=\{C_1,\ldots,C_k\}
\]

of \(V\) into independent sets. Conversely, every independent-set partition is
a valid common-message encoder: the earlier confusion-graph theorem synthesizes
an unambiguous decoder from the message class and each sink's side information.

Thus the source-coding decision is not merely a choice of color labels. It is a
choice of an **unlabeled proper partition** of the source states.

Let the exact rational prior be

\[
\pi=(\pi_0,\ldots,\pi_{n-1}),
\qquad
\pi_i\in\mathbb Q_{\ge0},
\qquad
\sum_i\pi_i=1.
\]

The probability of message class \(C_j\) is

\[
p_j(\mathcal P)=\sum_{i\in C_j}\pi_i.
\]

The optimization has two nested layers:

1. choose a proper independent-set partition \(\mathcal P\);
2. choose a binary prefix tree for the resulting class probabilities.

This separation matters because chromatic number minimizes \(k\), while the new
objective weights the depths of the classes by \(p_j(\mathcal P)\).

---

## 2. Prefix framing is an assumption, not a free convention

A binary prefix code assigns a finite bit string \(w_j\) to every message class
such that no codeword is a prefix of another. The receiver can then identify the
message boundary without a separate length channel.

Writing

\[
\ell_j=|w_j|,
\]

prefix feasibility implies Kraft's inequality

\[
\sum_j2^{-\ell_j}\le1.
\]

For a one-class source, the empty codeword is admissible and has length zero. If
there are multiple classes, every codeword has positive length.

For one fixed partition, the expected length is

\[
L(\mathcal P,w)
=
\sum_jp_j(\mathcal P)\ell_j.
\]

A protocol with packet boundaries supplied externally, a separate length
field, interaction, feedback, buffering across executions, or block coding has
a different admissible code family. None of those resources is silently
included here.

---

## 3. Exact Huffman optimum for one proper partition

For a fixed rational probability vector

\[
p=(p_1,\ldots,p_k),
\]

Huffman's algorithm repeatedly merges the two least-probable current nodes.
The resulting full binary tree is an optimal prefix tree.

### Merge-cost identity

When nodes of weights \(a\) and \(b\) are merged, every source occurrence in
either subtree gains one bit. The merge contributes exactly

\[
a+b
\]

to expected length. Summing all internal merge weights gives

\[
L_H(p)=\sum_jp_j\ell_j.
\]

The implementation constructs the actual bit strings and independently checks:

- prefix-freeness;
- Kraft's inequality;
- the expected-length sum;
- equality between expected length and total merge cost.

### Greedy optimality

In an optimal full binary tree, two leaves at maximum depth can be chosen as
siblings. Swapping labels can place two least-probable symbols at those deepest
sibling leaves without increasing expected length. Contracting the pair into a
pseudo-symbol of probability \(a+b\) leaves an optimal tree for the reduced
problem; otherwise replacing the reduced tree would improve the original.
Induction yields Huffman's algorithm.

Zero-probability symbols are retained when zero error is required on every
declared state. They receive finite codewords, usually in the deepest part of
the tree. Their own contribution to expectation is zero, but their required
leaves can still increase the lengths of positive-probability symbols.

Therefore, for a fixed proper partition,

\[
\boxed{
L_H\bigl(p(\mathcal P)\bigr)
=
\min_{\text{binary prefix codes}}
\sum_jp_j(\mathcal P)\ell_j.
}
\]

---

## 4. Exact global one-shot optimum

Let \(\operatorname{IndPart}(G)\) denote all partitions of \(V\) into
independent sets. The exact prior-weighted zero-error prefix cost is

\[
\boxed{
L^*(G,\pi)
=
\min_{\mathcal P\in\operatorname{IndPart}(G)}
L_H\bigl(p(\mathcal P)\bigr).
}
\]

This objective cannot in general be solved by first restricting to
\(\chi(G)\)-colorings. Fewer message classes reduce alphabet size, but splitting
a low-probability region can make it possible to isolate a high-probability
class at a shorter codeword.

### Complete bounded enumeration

The checker enumerates unlabeled proper partitions in restricted-growth order.
Vertices are processed in a fixed order. The next vertex may:

- join any existing block with which it has no edge; or
- open exactly one new final block.

Opening only one new final block removes all global color-label permutations.
Every unlabeled independent-set partition appears exactly once.

For every partition, the solver computes exact class masses, builds an exact
Huffman certificate, and records mean, peak, and message count. If the declared
vertex or partition cap is exceeded, the solver raises and reports no optimum.
A truncated search is never relabeled as a theorem certificate.

---

## 5. Exact message-count frontier

For each feasible exact message count \(k\), define

\[
L_k(G,\pi)
=
\min_{\substack{
\mathcal P\in\operatorname{IndPart}(G)\\
|\mathcal P|=k
}}
L_H\bigl(p(\mathcal P)\bigr).
\]

The feasible range is

\[
\chi(G)\le k\le n.
\]

The at-most-\(k\) frontier is

\[
\overline L_k
=
\min_{\chi(G)\le j\le k}L_j.
\]

The sequence \(\overline L_k\) is nonincreasing because allowing more classes
never removes an earlier code. The exact-count sequence \(L_k\) need not be
monotone: requiring another nonempty message can split a useful class and make
the best exact-\(k\) code worse.

The certificate therefore reports separately:

- \(\chi(G)\), the minimum message alphabet;
- \(L_k\), the best mean length at exactly \(k\) messages;
- \(\overline L_k\), the best mean length using at most \(k\) messages;
- the globally optimal message count.

---

## 6. Exact rational ordering of coloring entropies

For a proper partition, define

\[
H(\mathcal P)
=-\sum_jp_j(\mathcal P)\log_2p_j(\mathcal P).
\]

The minimum coloring entropy under the declared prior is

\[
H_{\mathrm{col}}(G,\pi)
=
\min_{\mathcal P\in\operatorname{IndPart}(G)}H(\mathcal P).
\]

Floating logarithms are unnecessary for selecting the exact minimizing
partition. Let \(D\) clear every denominator in the state prior. Then
\(Dp_j\) is an integer for every class mass. Define

\[
Q_D(p)
=
\prod_{j:p_j>0}p_j^{Dp_j}.
\]

Since

\[
\log_2Q_D(p)
=-D H(p),
\]

we have the exact rational ordering

\[
\boxed{
H(p)<H(q)
\iff
Q_D(p)>Q_D(q).
}
\]

The implementation compares the rational products exactly. A decimal entropy
is calculated only after the minimizing partition has already been identified.

---

## 7. Entropy sandwich, including the zero-mass boundary

Every binary prefix code satisfies Shannon's lower bound

\[
H(p)\le L(p).
\]

For a distribution whose message classes all have positive mass, Huffman coding
satisfies the familiar strict upper bound

\[
L_H(p)<H(p)+1.
\]

Declared-state zero error introduces a subtle boundary: a proper partition may
contain classes made entirely of zero-probability states. Those classes still
need codewords. The universal statement is then the weak bound

\[
L_H(p)\le H(p)+1.
\]

One way to see this is to perturb every zero mass by a positive rational amount,
renormalize, apply the strict positive-mass theorem, and take a limit through a
subsequence with a fixed finite tree shape. Huffman optimality at the limiting
distribution cannot be worse than that limiting tree.

Equality is real, not merely technical. For three pairwise-confusable declared
states with prior \((1,0,0)\), the positive state needs a one-bit codeword while
the two zero-mass states occupy the other subtree. Thus

\[
H=0,
\qquad
L_H=1=H+1.
\]

Let \(\mathcal P_L\) minimize exact expected prefix length and
\(\mathcal P_H\) minimize coloring entropy. The lower direction is

\[
L^*(G,\pi)
\ge
H\bigl(p(\mathcal P_L)\bigr)
\ge
H_{\mathrm{col}}(G,\pi).
\]

Using a Huffman code on \(\mathcal P_H\) gives the upper direction. Therefore

\[
\boxed{
H_{\mathrm{col}}(G,\pi)
\le
L^*(G,\pi)
\le
H_{\mathrm{col}}(G,\pi)+1.
}
\]

If the source prior has full support, every nonempty color class has positive
mass and the upper inequality is strict:

\[
L^*(G,\pi)<H_{\mathrm{col}}(G,\pi)+1.
\]

The entropy-minimizing and Huffman-length-minimizing partitions are not assumed
to coincide; the solver certifies them independently.

---

## 8. Fixed length, mean length, and peak length

A minimum coloring can always be encoded by fixed-length labels of size

\[
b_{\mathrm{fix}}
=
\left\lceil\log_2\chi(G)\right\rceil.
\]

Those labels form a prefix code, so

\[
\boxed{
L^*(G,\pi)
\le
\left\lceil\log_2\chi(G)\right\rceil.
}
\]

A variable-length code has a separate peak length

\[
\ell_{\max}=\max_j\ell_j.
\]

It is possible that

\[
L^*<b_{\mathrm{fix}}<\ell_{\max}.
\]

Thus a mean-traffic improvement does not automatically lower:

- a hard one-shot network cut;
- a fixed-size register;
- a strict latency deadline;
- worst-case packet size;
- buffer or queueing requirements.

Any systems claim must state whether the relevant resource is expected bits,
maximum bits, amortized bits, or a tail probability for backlog or delay.

---

## 9. Skew complete-graph example

Take \(G=K_4\) and

\[
\pi
=
\left(
\frac7{10},
\frac1{10},
\frac1{10},
\frac1{10}
\right).
\]

Every state needs a distinct message, so

\[
\chi(G)=4,
\qquad
b_{\mathrm{fix}}=2.
\]

A Huffman tree has lengths \((1,2,3,3)\), up to permutations among equal-mass
states. Its expected length is

\[
\boxed{L^*=\frac32}.
\]

Its peak is three bits:

\[
\boxed{
E[L]=\frac32<2<3=\ell_{\max}.
}
\]

The construction saves average traffic but does not fit every message through
a two-bit hard cut.

---

## 10. The mean-optimal code can use more than \(\chi(G)\) messages

Consider five vertices with edges

\[
\{01,02,03,04,12,23,34\}.
\]

Vertex zero is universal and vertices one through four form a path. The graph is
3-chromatic. Use prior

\[
\pi=\frac1{50}(12,19,1,5,13).
\]

The best three-message structure has class masses

\[
\left(
\frac6{25},
\frac{12}{25},
\frac7{25}
\right)
\]

and exact expected cost

\[
\boxed{L_3=\frac{38}{25}}.
\]

The four-message partition

\[
\{0\},\quad\{1,4\},\quad\{2\},\quad\{3\}
\]

has masses

\[
\left(
\frac6{25},
\frac{16}{25},
\frac1{50},
\frac1{10}
\right)
\]

and exact Huffman cost

\[
\boxed{L_4=\frac{37}{25}}.
\]

Using all five singleton messages is worse:

\[
L_5=\frac{21}{10}.
\]

Therefore

\[
\boxed{
L_4<L_3
\quad\text{while}\quad
4>\chi(G)=3.
}
\]

The exact objective must search proper partitions, not merely minimum-colorings.

---

## 11. Uniform five-cycle example

For \(C_5\),

\[
\chi(C_5)=3.
\]

Under the uniform prior, an optimal partition has class sizes \(2,2,1\), hence
message probabilities

\[
\frac25,\frac25,\frac15.
\]

Huffman lengths \((1,2,2)\) give

\[
\boxed{L^*(C_5)=\frac85}.
\]

The clique number is only two. The example preserves the earlier distinction
between pairwise clique lower bounds and exact chromatic complexity while also
showing the additional prior-weighted layer.

---

## 12. Monotonicity under deleted confusion edges

Suppose \(G'\) has the same ordered vertices as \(G\) and

\[
E(G')\subseteq E(G).
\]

Every proper partition of \(G\) remains proper for \(G'\). The feasible code set
can only expand, so

\[
\boxed{
L^*(G',\pi)
\le
L^*(G,\pi).
}
\]

Likewise,

\[
\chi(G')\le\chi(G).
\]

More informative side information and coarser required targets delete confusion
edges under the earlier theorems. Holding the prior and communication interface
fixed, they cannot increase the exact expected prefix optimum.

The inequality need not be strict. An edge can disappear without participating
in any optimal partition.

---

## 13. Zero-mass states and two correctness conventions

A state with \(\pi_i=0\) exposes two distinct guarantees.

### Declared-state zero error

Every state in the declared model must decode correctly, including zero-mass
states. Those vertices remain in the graph and need finite codewords. They can
increase positive-state lengths even though their direct expected contribution
is zero.

### Positive-support-only zero error

Correctness is required only on

\[
\operatorname{supp}(\pi)=\{i:\pi_i>0\}.
\]

The exact problem becomes the induced graph

\[
G[\operatorname{supp}(\pi)].
\]

Its optimum satisfies

\[
\boxed{
L^*_{\mathrm{support}}
\le
L^*_{\mathrm{declared}}.
}
\]

For \(K_3\) with prior \((1,0,0)\), declared-state zero error yields

\[
L^*_{\mathrm{declared}}=1,
\]

whereas the one-vertex positive-support problem permits the empty codeword:

\[
L^*_{\mathrm{support}}=0.
\]

This is a change in the quantified state set, not a contradiction. Rounding a
small empirical probability to zero can therefore change a support-only claim
discontinuously.

---

## 14. Prior mismatch is a separate robustness problem

The optimizer in this lane assumes one declared prior is known to both encoder
and decoder. It does not prove robustness when the actual distribution is
\(q\ne\pi\).

For any fixed state-length vector \(\ell\), total variation gives the elementary
sensitivity bound

\[
\left|E_q[\ell]-E_\pi[\ell]\right|
\le
\operatorname{TV}(q,\pi)
\left(\max_i\ell_i-\min_i\ell_i\right).
\]

This bound already shows why a highly skew-optimized tree may be fragile: a
small amount of probability moved from short-code states to long-code states
can increase expected traffic. It is only a bound for a **fixed code**, not a
solution of the robust code-design problem.

The next lane should solve, exactly and separately:

- finite-scenario deterministic minimax coding;
- minimax regret relative to prior-specific oracle codes;
- shared-randomness mixtures of codebooks, counting the random seed;
- continuous total-variation prior balls by exact mass transport;
- peak-constrained or queue-aware variants.

---

## 15. Bounded certificate contents and independent audits

The implementation returns:

- the exact rational state prior;
- an exact chromatic certificate;
- the number of proper partitions examined;
- explicit vertex and partition caps;
- the expected-optimal proper partition;
- its exact class probabilities;
- exact binary codewords and lengths;
- exact expected and Huffman merge costs;
- Kraft sum and prefix-free checks;
- maximum codeword length;
- the exact-count and at-most message frontiers;
- the entropy-minimizing partition;
- its exact rational entropy-order product;
- the displayed coloring entropy;
- the corrected weak one-bit entropy sandwich;
- the fixed-length upper bound;
- optional edge-deletion and support-restriction certificates.

The tests independently:

1. enumerate Kraft-feasible length vectors for small message alphabets and
   compare their optima with Huffman;
2. enumerate deterministic colorings and prefix-length assignments on every one
   of the 64 labeled four-vertex simple graphs;
3. verify the richer-than-chromatic five-vertex example;
4. verify the \(K_4\), \(C_5\), edge-deletion, and zero-support examples;
5. reject inexact floating priors in the exact API;
6. fail closed when a search cap is exceeded.

---

## 16. Research boundary

The predictive pipeline now has an additional explicit layer:

\[
\text{future demand}
\to
\text{confusion graph}
\to
\text{proper message partition}
\to
\text{prefix tree}
\to
\text{mean and peak communication}.
\]

Each arrow changes when its assumptions change:

- side information and targets change the graph;
- the source prior changes average cost but not zero-error adjacency;
- prefix framing changes the admissible bit strings;
- support-only correctness changes the vertex set;
- block coding changes the graph object and may change rates;
- expected traffic is not hard cut capacity;
- prior uncertainty changes the optimization game.

This lane therefore narrows claims rather than broadening them. It identifies
exactly which compression follows from a declared prior and framing model, and
which stronger physical or network conclusion does not follow.

## Nonclaims

This work does not establish:

- a universal prior over physical states or observers;
- an asymptotic graph-entropy formula;
- robustness to uncertain, drifting, or adversarial priors;
- allowed-error or lossy function computation;
- interaction, feedback, or online universal coding;
- quantum variable-length coding;
- hard network feasibility from expected length alone;
- parent-substrate memory or energy cost;
- evidence that reality is simulated.
