# Prior-weighted zero-error predictive coding

## Scope

The confusion-graph result answers an exact one-shot **worst-case alphabet**
question. If a finite hidden state is mapped to one common message and every
sink must recover its declared target from that message and its local side
information, then the minimum number of message values is

\[
\chi(G),
\]

where \(G\) is the problem's confusion graph. A fixed-length binary label then
uses

\[
\left\lceil \log_2 \chi(G) \right\rceil
\]

bits.

That theorem deliberately does not answer several different questions:

1. What if source states have a nonuniform prior?
2. What if messages use a variable-length binary prefix code?
3. Is the average-optimal coloring always a minimum-coloring?
4. How does average length differ from peak length and cut capacity?
5. Do zero-probability states still require exact codewords?
6. How does more informative side information affect average code length?

This note solves the finite rational-prior, one-shot, binary-prefix, zero-error
problem exactly below explicit enumeration caps.

The result is an internal source-coding theorem for a declared predictive
interface. It does not provide evidence that reality is simulated and does not
identify a message bit with parent-universe storage, energy, mass, or spacetime.

---

## 1. Finite source, graph, and prior

Let

\[
V=\{0,\ldots,n-1\}
\]

be the finite source-state set and let

\[
G=(V,E)
\]

be its confusion graph. Vertices joined by an edge cannot share a zero-error
message.

Let the declared source prior be rational:

\[
\pi=(\pi_0,\ldots,\pi_{n-1}),
\qquad
\pi_i\in\mathbb Q_{\ge0},
\qquad
\sum_i\pi_i=1.
\]

The rational restriction is computational rather than conceptual. It allows
all feasibility, class-mass, expected-length, and ordering calculations in the
bounded checker to remain exact.

A deterministic zero-error encoder induces a partition

\[
\mathcal P=\{C_1,\ldots,C_k\}
\]

of \(V\), where every \(C_j\) is an independent set of \(G\). Conversely,
every partition into independent sets is a valid zero-error message encoder.

The probability of message class \(j\) is

\[
p_j(\mathcal P)
=
\sum_{i\in C_j}\pi_i.
\]

The source-coding problem therefore has two nested decisions:

1. choose a proper independent-set partition;
2. choose a binary prefix code for the resulting class probabilities.

---

## 2. Prefix framing is an explicit resource assumption

A binary prefix code assigns a finite bit string \(w_j\) to every message class
such that no codeword is a prefix of another. This lets a receiver determine
where one message ends without an external message-length side channel.

The codeword lengths

\[
\ell_j=|w_j|
\]

obey Kraft's inequality

\[
\sum_j 2^{-\ell_j}\le1.
\]

For one message class, the empty codeword is allowed and has length zero. For
more than one class, every codeword has positive length.

This assumption must not be hidden. A protocol with externally framed packet
boundaries, a separate length channel, interaction, or amortized block coding
is a different communication model.

For a fixed proper partition, the expected binary prefix length is

\[
L(\mathcal P,\ell)
=
\sum_j p_j(\mathcal P)\ell_j.
\]

---

## 3. Exact Huffman optimum for one partition

For one fixed probability vector

\[
p=(p_1,\ldots,p_k),
\]

Huffman's merge procedure repeatedly combines the two least-probable current
symbols. The resulting full binary tree gives a prefix code.

### Merge-cost identity

Whenever two leaves of probabilities \(a\) and \(b\) are merged, every source
occurrence in either subtree gains one additional code bit. That merge adds

\[
a+b
\]

to expected length.

Summing the weights of all internal merges therefore gives exactly

\[
L_H(p)
=
\sum_j p_j\ell_j.
\]

The implementation checks this equality independently from the constructed
codewords.

### Why the greedy merge is optimal

Take any optimal full binary prefix tree. Two leaves of maximum depth can be
chosen as siblings. If those sibling leaves do not carry two least-probable
symbols, exchanging labels so that the least-probable symbols occupy the
maximum-depth sibling positions cannot increase expected length.

Contract the two sibling leaves into one pseudo-symbol of probability \(a+b\).
The remaining tree must be optimal for the reduced probability list; otherwise
replacing it by a cheaper reduced tree and expanding the contracted sibling
pair would improve the original tree.

This gives the standard induction:

1. an optimal tree can place two least-probable symbols as deepest siblings;
2. contracting them reduces the problem by one symbol;
3. recursively solving the reduced problem and expanding the pair is optimal.

Zero-probability symbols cause no problem. They are assigned to deepest leaves
first, but they still require codewords if zero error is demanded on every
declared source state.

Thus, for a fixed proper partition,

\[
\boxed{
L_H\bigl(p(\mathcal P)\bigr)
=
\min_{\text{binary prefix codes}}
\sum_jp_j(\mathcal P)\ell_j.
}
\]

---

## 4. Exact global prior-weighted optimum

Let \(\operatorname{IndPart}(G)\) denote all partitions of \(V\) into
independent sets. The exact one-shot prior-weighted zero-error prefix cost is

\[
\boxed{
L^*(G,\pi)
=
\min_{\mathcal P\in\operatorname{IndPart}(G)}
L_H\bigl(p(\mathcal P)\bigr).
}
\]

This is not necessarily obtained by first finding a \(\chi(G)\)-coloring.
Chromatic number minimizes the **number** of messages. The new objective
minimizes a prior-weighted average of binary codeword depths.

### Finite reduction

For a bounded graph, every proper partition can be generated once in
restricted-growth order:

- process vertices in a fixed order;
- place the next vertex into any existing block with which it has no edge;
- or open exactly one new final block.

Opening only one new final block removes all global color-label permutations.
Every unlabeled independent-set partition appears exactly once.

For each partition the checker:

1. computes exact rational class probabilities;
2. constructs a deterministic Huffman tree;
3. checks prefix-freeness and Kraft's inequality;
4. checks expected length against the exact merge cost;
5. records message count and maximum codeword length;
6. retains the exact minimum expected-length certificate.

If either the vertex cap or partition cap is exceeded, the solver raises. It
does not return a partial search result and call it an optimum.

---

## 5. Exact message-count frontier

For every feasible exact message count \(k\), define

\[
L_k(G,\pi)
=
\min_{\substack{
\mathcal P\in\operatorname{IndPart}(G)\\
|\mathcal P|=k
}}
L_H\bigl(p(\mathcal P)\bigr).
\]

The feasible values are

\[
\chi(G)\le k\le n.
\]

The at-most-\(k\) frontier is

\[
\overline L_k
=
\min_{\chi(G)\le j\le k}L_j.
\]

The sequence \(\overline L_k\) is nonincreasing because allowing additional
message classes never removes an earlier code. The exact-count sequence
\(L_k\), however, need not be monotone. Requiring an extra nonempty message can
split a useful high-probability class and make the best code worse.

This frontier prevents three different questions from being conflated:

- the minimum number of zero-error messages;
- the best expected length using exactly \(k\) messages;
- the globally best expected length with no message-count penalty.

---

## 6. Minimum coloring entropy and exact rational ordering

For a proper partition \(\mathcal P\), define the message entropy

\[
H(\mathcal P)
=
-\sum_jp_j(\mathcal P)\log_2p_j(\mathcal P).
\]

The minimum coloring entropy under prior \(\pi\) is

\[
H_{\mathrm{col}}(G,\pi)
=
\min_{\mathcal P\in\operatorname{IndPart}(G)}H(\mathcal P).
\]

Naively comparing floating logarithms would weaken an otherwise exact bounded
certificate. Rational priors permit an exact ordering.

Let \(D\) clear every denominator in the state prior. Every class mass then
satisfies

\[
Dp_j\in\mathbb Z_{\ge0}.
\]

Define

\[
Q_D(p)
=
\prod_{j:p_j>0}p_j^{Dp_j}.
\]

Then

\[
\log_2Q_D(p)
=
\sum_jDp_j\log_2p_j
=-D H(p).
\]

Therefore

\[
\boxed{
H(p)<H(q)
\iff
Q_D(p)>Q_D(q).
}
\]

Every exponent is an integer and every base is rational, so \(Q_D\) is a
rational number that can be compared exactly. Floating point is used only to
print the entropy after the minimizing partition has already been selected.

---

## 7. Entropy sandwich for the global optimum

For every prefix code on message distribution \(p\), Shannon's lower bound
gives

\[
H(p)\le L(p).
\]

Huffman coding also satisfies

\[
L_H(p)<H(p)+1.
\]

Let \(\mathcal P_L\) minimize expected prefix length and let \(\mathcal P_H\)
minimize coloring entropy. Then

\[
L^*(G,\pi)
=L_H\bigl(p(\mathcal P_L)\bigr)
\ge
H\bigl(p(\mathcal P_L)\bigr)
\ge
H_{\mathrm{col}}(G,\pi).
\]

For the other direction, use a Huffman code on the entropy-minimizing
partition:

\[
L^*(G,\pi)
\le
L_H\bigl(p(\mathcal P_H)\bigr)
<
H\bigl(p(\mathcal P_H)\bigr)+1.
\]

Hence

\[
\boxed{
H_{\mathrm{col}}(G,\pi)
\le
L^*(G,\pi)
<
H_{\mathrm{col}}(G,\pi)+1.
}
\]

The partition minimizing entropy and the partition minimizing exact Huffman
length need not be assumed identical; both are enumerated and certified
separately.

---

## 8. Fixed length, mean length, and peak length are different

A minimum coloring with \(\chi(G)\) message values can always be transmitted
with

\[
b_{\mathrm{fix}}
=
\left\lceil\log_2\chi(G)\right\rceil
\]

fixed bits. Therefore

\[
\boxed{
L^*(G,\pi)
\le
\left\lceil\log_2\chi(G)\right\rceil.
}
\]

But a variable-length code has a separate peak cost

\[
\ell_{\max}
=
\max_j\ell_j.
\]

It is entirely possible that

\[
L^*<b_{\mathrm{fix}}<\ell_{\max}.
\]

Average-length improvement therefore does not by itself lower a hard one-shot
network cut, a strict deadline, or a fixed-size register requirement. A system
must separately specify:

- whether messages are externally framed;
- whether buffering across executions is allowed;
- whether only expected traffic or every execution must fit;
- whether codebooks and priors are common knowledge;
- whether the source process is IID, adversarial, or drifting.

---

## 9. Skew complete-graph example

Take \(G=K_4\). Every source state is pairwise confusable, so every state must
have a distinct message and

\[
\chi(G)=4,
\qquad
b_{\mathrm{fix}}=2.
\]

Use prior

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

One Huffman tree has lengths

\[
(1,2,3,3)
\]

up to permutation among equal-probability states. Its expected length is

\[
\frac7{10}\cdot1
+
\frac1{10}\cdot2
+
\frac1{10}\cdot3
+
\frac1{10}\cdot3
=
\boxed{\frac32}.
\]

But the maximum length is three:

\[
\boxed{
E[L]=\frac32<2<3=L_{\max}.
}
\]

This is an average-traffic gain, not a two-bit hard-capacity construction.

---

## 10. Average-optimal coding can use more than \(\chi(G)\) messages

Consider five vertices with edges

\[
\{01,02,03,04,12,23,34\}.
\]

Vertex \(0\) is universal and vertices \(1,2,3,4\) form a path. The graph is
3-chromatic.

Use prior weights

\[
\pi
=
\frac1{50}(12,19,1,5,13).
\]

### Best three-message code

The unique relevant 3-color structure is

\[
\{0\},\quad\{1,3\},\quad\{2,4\},
\]

with class probabilities

\[
\left(
\frac6{25},
\frac{12}{25},
\frac7{25}
\right).
\]

The exact best three-message expected length is

\[
\boxed{L_3=\frac{38}{25}.}
\]

### Better four-message code

Use the valid partition

\[
\{0\},\quad\{1,4\},\quad\{2\},\quad\{3\}.
\]

Its class probabilities are

\[
\left(
\frac6{25},
\frac{16}{25},
\frac1{50},
\frac1{10}
\right).
\]

Huffman lengths \((2,1,3,3)\) give

\[
\boxed{L_4=\frac{37}{25}.}
\]

Therefore

\[
\boxed{
L_4<L_3
\quad\text{even though}\quad
4>\chi(G)=3.
}
\]

Using all five singleton messages is worse:

\[
L_5=\frac{21}{10}.
\]

This finite example disproves the tempting shortcut

> first minimize the color count, then optimize codeword lengths.

The correct exact objective must search the space of proper partitions, not
only minimum-colorings.

---

## 11. Uniform five-cycle example

For the cycle \(C_5\),

\[
\chi(C_5)=3.
\]

Under the uniform prior, an optimal proper partition has class sizes

\[
2,2,1,
\]

and probabilities

\[
\frac25,\frac25,\frac15.
\]

Binary Huffman lengths \((1,2,2)\) give

\[
\boxed{
L^*(C_5)=\frac85.
}
\]

The clique number is only two, so the example simultaneously preserves the
previous lesson that pairwise clique bounds can miss the exact message
alphabet.

---

## 12. Edge-deletion and side-information monotonicity

Suppose \(G'\) has the same vertices as \(G\) and

\[
E(G')\subseteq E(G).
\]

Every independent-set partition of \(G\) remains a valid independent-set
partition of \(G'\). Therefore the feasible code set can only expand:

\[
\boxed{
L^*(G',\pi)
\le
L^*(G,\pi).
}
\]

The same argument gives

\[
\chi(G')\le\chi(G).
\]

More informative side information and coarser target functions delete
confusion edges under the earlier theorems. Consequently they cannot increase
the exact prior-weighted optimum when the source prior and communication model
are held fixed.

The inequality can be strict or equal. Removing an ambiguity does not imply a
bit reduction if the deleted edge was not active in any optimal partition.

---

## 13. Zero-mass states expose two different zero-error conventions

Suppose a declared state has prior probability zero. Two legitimate but
different requirements are possible.

### Declared-state zero error

Every state in the declared model must decode correctly, including zero-mass
states. Such states still appear as graph vertices and still require
codewords. They can increase positive-state codeword lengths because the
prefix tree must contain leaves for them.

### Positive-support-only zero error

Only states with

\[
\pi_i>0
\]

must decode correctly. The exact problem is then the induced confusion graph
on the positive support.

Let

\[
G[\operatorname{supp}\pi]
\]

be that induced graph. Its optimum satisfies

\[
\boxed{
L^*_{\mathrm{support}}
\le
L^*_{\mathrm{declared}}.
}
\]

### Discontinuity example

For \(K_3\) with prior

\[
(1,0,0),
\]

declared-state zero error still requires three codewords. The positive state
can receive a one-bit codeword, giving

\[
L^*_{\mathrm{declared}}=1.
\]

The positive-support graph has one vertex and permits the empty codeword:

\[
L^*_{\mathrm{support}}=0.
\]

This is not a contradiction. It is a change in the quantified state set.
Empirical estimates that round tiny probabilities to zero can therefore change
an almost-sure coding claim discontinuously unless the convention is declared.

---

## 14. Bounded certificate contents

The implementation returns:

- the exact rational source prior;
- every search cap;
- the number of proper partitions examined;
- an exact chromatic certificate;
- the expected-optimal independent-set partition;
- its class probabilities;
- exact binary codewords and lengths;
- exact expected and merge costs;
- Kraft sum and prefix-free checks;
- maximum codeword length;
- the exact-count and at-most message frontier;
- the entropy-minimizing partition;
- its exact rational entropy-order product;
- a displayed Shannon entropy;
- the entropy sandwich;
- the fixed-length upper bound;
- optional edge-deletion and support-restriction certificates.

The tests independently:

1. enumerate Kraft-feasible length vectors for small message alphabets and
   compare them with Huffman;
2. enumerate every deterministic coloring and prefix-length assignment on all
   64 labeled four-vertex graphs;
3. verify the richer-than-chromatic example;
4. verify the \(K_4\), \(C_5\), edge-deletion, and zero-support examples;
5. fail closed when a bounded search cap is exceeded.

---

## 15. What this changes in the simulation-theory program

The predictive-state lower-bound program now has another explicit layer:

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

Each arrow depends on assumptions that should not be silently collapsed:

- changing side information changes the graph;
- changing the source prior changes the average objective but not the graph;
- changing from fixed to variable length changes the coding interface;
- changing from declared-state to support-only zero error changes the domain;
- changing from one shot to blocks changes the admissible code family;
- changing from expected traffic to hard cut capacity changes the resource
  being bounded.

The new result therefore makes the project more conservative, not more
speculative. It identifies exactly which compression gains follow from a
prior and a framing model, and which do not.

---

## 16. Nonclaims and next questions

This lane does **not** establish:

- a universal prior over physical states;
- an asymptotic graph-entropy or graph-power theorem;
- robustness to an uncertain or drifting prior;
- allowed-error or lossy function computation;
- interactive or feedback coding;
- quantum variable-length coding;
- network feasibility from expected length alone;
- a parent-substrate memory or energy cost;
- evidence that reality is simulated.

The highest-value next extensions are:

1. finite-scenario minimax and minimax-regret prefix codes;
2. exact total-variation prior balls via probability-mass transport;
3. shared-randomness mixtures of codebooks, with the random seed counted;
4. one-shot allowed-error Bayes-risk frontiers;
5. a proof that the unweighted confusion graph is sufficient for zero error but
   generally insufficient for allowed-error risk;
6. block coding through bounded graph products;
7. online universal coding under a declared source-process class;
8. expected-traffic versus queueing-delay and peak-cut tradeoffs.
