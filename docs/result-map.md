# Result map

A guided tour of the main results, in the order the research program builds
them. Stable claim IDs, assumptions, and nonclaims live in the manifests under
[`claims/`](../claims/); each section here links to the derivation it
summarizes through those manifests.

## 1. Identification, evidence ceilings, and model uncertainty

The statistical foundations include:

- unrestricted observational indistinguishability;
- Bayes-factor equality for identical laws;
- posterior movement bounds from bounded likelihood ratios;
- equal-prior optimal classification

  \[
  A^\star=\frac{1+\operatorname{TV}(P,Q)}2;
  \]

- Le Cam two-point lower bounds;
- Fano multi-model identification bounds;
- finite sample-size necessities for restricted architecture families;
- hierarchical feasibility mixtures;
- robust posterior intervals;
- anytime-valid likelihood-ratio e-processes for specified signatures;
- exact finite-horizon optional-stopping audits.

The governing rule is: **identification comes before estimation**.

## 2. Observer measure and anthropic sensitivity

Observer counting is decomposed instead of hidden inside one dramatic number.
The model keeps separate:

- civilization survival and technical feasibility;
- deployment policy;
- number of simulated environments;
- observers versus observer-moments;
- consciousness assumptions;
- compatibility with the observer's complete evidence;
- duration and duplication conventions.

For uncertain simulated measure \(X\),

\[
E\!\left[\frac{X}{B+X}\right]
\le
\frac{E[X]}{B+E[X]},
\]

so inserting an expected count into a nonlinear ratio can overstate the
properly averaged result. Finite SSA-, SIA-, and FNC-style conditioning rules
are implemented as sensitivity models rather than silently collapsed into a
single universal prior.

## 3. Adaptive rendering and predictive state

Exact lazy generation is transcript-equivalent to pre-generating a hidden world
when each answer is sampled from the exact target conditional:

\[
P(A_{1:T}\mid Q_{1:T})
=
\prod_{t=1}^TP(A_t\mid H_t,Q_t).
\]

Approximate renderers have adaptive transcript bounds from per-step total
variation and conditional KL.

Predictive equivalence is defined by the allowed future interface:

\[
h\sim h'
\iff
P(\text{all allowed futures}\mid h)
=
P(\text{all allowed futures}\mid h').
\]

If there are \(K\) exact future-law classes, an exact finite renderer needs
exactly \(K\) predictive states and at least

\[
\lceil\log_2K\rceil
\]

fixed-length bits.

For approximation, strict \(2\epsilon\)-packings provide converse lower bounds,
while target-centered and arbitrary-center covers provide constructive upper
bounds. The gap is kept explicit unless an exact geometry closes it.

## 4. Stochastic future laws, arbitrary centers, and observation channels

Finite stochastic query families assign a full conditional outcome law to each
record-query pair. Under an exogenous query schedule, joint TV and KL are the
query-weighted sums of their conditional counterparts.

For one query with exactly three outcomes,

\[
\operatorname{TV}(p,u)=\max_j|p_j-u_j|.
\]

This yields exact common-center feasibility, a closed one-state minimax radius,
and exact unrestricted arbitrary-center covering by finite subset enumeration
plus minimum set cover. For the three simplex vertices, the exact state count is:

- three for \(\epsilon<1/2\);
- two for \(1/2\le\epsilon<2/3\);
- one uniform state for \(\epsilon\ge2/3\).

The max-coordinate identity is special to three outcomes and is not generalized
by analogy.

For a shared record-independent outcome channel \(K\), the exact Dobrushin
coefficient is

\[
\delta(K)
=
\max_{a,b}
\operatorname{TV}
\bigl(K(\cdot\mid a),K(\cdot\mid b)\bigr),
\]

and

\[
\operatorname{TV}(\mu K,\nu K)
\le
\delta(K)\operatorname{TV}(\mu,\nu).
\]

Exact classes can only coarsen, and strict packings and target-centered covers
cannot grow. Serial coefficients are submultiplicative. Binary symmetric and
erasure channels have exact coefficients.

Lossy observation can weaken evidence. It cannot create distinguishability that
was absent before the channel.

## 5. Physical and quantum predictive geometry

Physical-query lower bounds are derived from explicit measurement families,
not from raw Hilbert-space dimension.

Implemented examples include:

- Werner/singlet Bell visibility laws;
- exact Bell TV, Fisher information, and adaptive KL bounds;
- visibility-plus-phase geometry;
- the canonical CHSH disk identity

  \[
  \operatorname{TV}(P_q,P_{q'})
  =
  \frac{\|q-q'\|_\infty}{2\sqrt2};
  \]

- constructive two-dimensional physical packings;
- exact computational-basis coordinate-query scaling;
- continuous product-qubit \(L_1\) geometry;
- subsystem-count versus accessible-resolution packings;
- exact finite adaptive phase-drift transcript laws.

The local-physics module separately implements Landauer, Margolus–Levitin,
Bekenstein, mass-energy, Schwarzschild, and mass-limited operation expressions.
The cross-level boundary is preserved:

\[
\text{internal physical quantity}
\not\Rightarrow
\text{parent implementation cost}
\]

without an implementation map and law-transfer assumption.

## 6. Relational information, noise, and quantum codes

Graph and cat-state constructions isolate information stored in correlations
rather than low-order marginals.

For cycle graph states with at least five qubits:

- every one- and two-qubit reduction is maximally mixed across all graph-basis
  labels;
- weight-three stabilizer queries recover the labels;
- uniform generator-query distance is normalized Hamming distance.

For phase-labeled cat blocks, every proper local-X transcript is phase blind,
while the complete transcript obeys one global parity constraint. After
\(\ell-1\) outcomes in each of \(m\) open blocks, exact continuation has
\(2^m\) predictive classes and needs one parity bit per block.

With independent flip probability \(p\), parity visibility is

\[
c_\ell(p)=(1-2p)^\ell,
\]

and the average predictive rate-distortion lower bound is

\[
I(Z;M)
\ge
m\left[1-H_2(D/c)\right].
\]

The stabilizer-code lane implements exact binary-symplectic rank, normalizer,
distance, logical cosets, projectors, and reduced-state checks. It proves local
indistinguishability below code distance and independently verifies the
five-qubit \([[5,1,3]]\) code.

## 7. Causal cuts, query timing, and quantum communication

For an \(m\)-bit record sent before an unresolved coordinate query, exact
one-way answering requires an injective message:

\[
|\mathcal M|\ge2^m.
\]

Under uniform average error \(\epsilon\),

\[
I(X;M)
\ge
m[1-H_2(\epsilon)].
\]

The repository includes:

- resident-state versus later-communication tradeoffs;
- weighted future-query error allocation;
- indexed parity-reconciliation equivalence;
- isolated-region replication bounds;
- progressive query revelation and exact shared/branch capacity regions;
- explicit finite upper protocols.

Without entanglement assistance, an unresolved \(m\)-bit random-access record
encoded into \(q\) qubits obeys

\[
q\ge m[1-H_2(\epsilon)].
\]

Receiver-side preshared entanglement changes the coefficient by at most a factor
of two. Exact dense coding attains the assisted zero-error full-record rate.
Canonical two-to-one and three-to-one one-qubit random-access codes are checked
on every record-query pair.

Query timing is a resource: revealing the requested coordinate before encoding
can reduce linear communication to one answer symbol.

## 8. Predictive networks and multicast coding

For one sink, a finite exact predictive-class label can be routed through a
directed integer-capacity network exactly when the declared source-sink min-cut
can carry its fixed-length index. Approximate stochastic networks report three
states:

- **impossible** below a packing lower bound;
- **constructively feasible** above a cover-index upper bound;
- **unresolved** in between.

Per-sink min-cuts are necessary but not generally jointly sufficient for
multiple sinks.

The finite multicast lane implements exact scalar linear coding over prime
fields. In the declared binary butterfly network:

- both sinks have min-cut two;
- all 4096 local binary scalar assignments are checked;
- no routing-only assignment serves both sinks;
- sending \(x_1+x_2\) through the shared bottleneck lets both decode.

The project proves this bounded result and does not silently claim the full
general multicast theorem.

## 9. Sink-specific linear and nonlinear function computation

A receiver need not reconstruct the entire source. For source
\(x\in\mathbb F_p^h\), incoming rows \(G_t\), local side-information rows
\(S_t\), and desired rows \(B_t\), exact recovery is equivalent to

\[
\operatorname{rowspan}(B_t)
\subseteq
\operatorname{rowspan}
\begin{pmatrix}G_t\\S_t\end{pmatrix}.
\]

The new linear information required across a cut is

\[
\operatorname{rank}
\begin{pmatrix}S_t\\B_t\end{pmatrix}
-
\operatorname{rank}(S_t).
\]

Complementary side information can make one XOR symbol serve two different
receivers.

For arbitrary finite nonlinear target and side-information functions, define a
confusion edge

\[
x\sim_c y
\iff
\exists t:
s_t(x)=s_t(y)
\text{ and }
f_t(x)\ne f_t(y).
\]

Zero-error common-message encoders are exactly proper colorings of this graph.
Therefore

\[
|\mathcal M|_{\min}=\chi(G),
\qquad
b_{\min}=\lceil\log_2\chi(G)\rceil.
\]

The implementation includes exact bounded chromatic, clique, independent-set,
decoder, realization, monotonicity, and randomized-support checks. Every simple
finite graph can be realized as a finite side-information function problem.
All 64 labeled four-vertex graphs are independently audited.

## 10. Prior-weighted zero-error source coding

Chromatic number minimizes the hard message alphabet, not expected bits under a
nonuniform source law.

For a proper independent-set partition

\[
\mathcal P=\{C_1,\ldots,C_k\},
\]

and rational prior \(\pi\), class probabilities are

\[
p_j(\mathcal P)=\sum_{x\in C_j}\pi_x.
\]

For that partition, Huffman coding gives the exact minimum binary-prefix mean.
The global one-shot optimum is

\[
\boxed{
L^*(G,\pi)
=
\min_{\mathcal P\in\operatorname{IndPart}(G)}
L_H\bigl(p(\mathcal P)\bigr).
}
\]

The bounded solver enumerates every unlabeled proper partition and complete
prefix certificate. It reports the exact message-count frontier, mean length,
peak length, and minimum coloring entropy.

For rational probabilities, coloring entropies are ordered exactly through

\[
Q_D(p)=\prod_jp_j^{Dp_j}=2^{-D H_2(p)}.
\]

The universal one-shot entropy sandwich, including zero-mass declared classes,
is

\[
H_{\mathrm{col}}(G,\pi)
\le
L^*(G,\pi)
\le
H_{\mathrm{col}}(G,\pi)+1,
\]

with a strict upper inequality under full support.

Important exact examples:

- skew \(K_4\): mean \(3/2\), fixed length two, peak length three;
- uniform \(C_5\): mean \(8/5\);
- one five-vertex graph has \(\chi=3\) but its mean-optimal code uses four
  message classes;
- declared-state versus positive-support-only zero error can differ
  discontinuously at zero prior mass.

## 11. Finite-prior robust coding and shared codebook randomness

For finite prior scenarios

\[
\Pi=\{\pi^{(1)},\ldots,\pi^{(R)}\},
\]

the deterministic robust value is

\[
V_{\mathrm{det}}
=
\min_c\max_rL_r(c).
\]

Scenario-specific oracle costs

\[
L_r^*=\min_cL_r(c)
\]

define minimax regret

\[
R_{\mathrm{det}}
=
\min_c\max_r[L_r(c)-L_r^*].
\]

The complete bounded code universe includes every proper partition and every
full binary prefix shape. A deterministic minimax tree need not be Huffman-
optimal for any one scenario, and minimax length need not select the same code
as minimax regret.

With a source-independent seed shared by encoder and all decoders, one may mix
complete deterministic codebooks:

\[
V_{\mathrm{mix}}
=
\min_q\max_r\sum_cq_cL_r(c).
\]

The finite rational zero-sum game is solved by exact primal and dual support
enumeration with zero rational gap. An optimum needs at most \(R\) codebooks in
its support.

The dual scenario mixture defines a least-favorable barycenter prior, and

\[
V_{\mathrm{mix}}
=
\max_{\bar\pi\in\operatorname{conv}(\Pi)}L^*(G,\bar\pi).
\]

For a declared \(K_3\) example, deterministic minimax is \(19/10\), while a
shared 50/50 codebook mixture achieves \(31/20\). The zero-error alphabet is
unchanged; the gain is in worst-prior expected length and consumes shared
codebook randomness.

## 12. Continuous TV-ball distributional robustness

A finite prior list is not the only uncertainty model. For nominal prior \(p\)
and radius \(\rho\), define

\[
\mathcal U_{\mathrm{TV}}(p,\rho)
=
\{q:\operatorname{TV}(q,p)\le\rho\}.
\]

For a fixed value vector \(f\), total variation is exactly moved probability
mass. The robust maximum is obtained by moving mass from the lowest-value donors
to a maximum-value state:

\[
\boxed{
\sup_{q\in\mathcal U_{\mathrm{TV}}}E_q[f]
=
E_p[f]
+
\sum_t m_t(f_{j_t}-f_{i_t}).
}
\]

The minimum reverses the transport order. Every transfer, extremal distribution,
and expectation is rational.

The same inner problem has an exact fractional-knapsack dual:

\[
\boxed{
\min_{\lambda\ge0}
\left[
\rho\lambda
+
\sum_i p_i(g_i-\lambda)_+
\right],
}
\]

with exact complementary-slackness receipts and zero rational gap.

Fixed-code robust expectation is continuous, monotone, piecewise linear, and
concave in radius for maximization. It saturates once all nonmaximum mass reaches
the maximum-value face. The range bound

\[
|E_q[f]-E_p[f]|
\le
\operatorname{TV}(q,p)
\operatorname{range}(f)
\]

has an explicit tightness window.

The outer exact deterministic coding problem is

\[
V_{\mathrm{TV}}(G,p,\rho)
=
\min_c
\sup_{q:\operatorname{TV}(q,p)\le\rho}E_q[\ell_c].
\]

It exhausts every bounded proper partition and complete prefix shape. Exact
endpoints are

\[
V_{\mathrm{TV}}(G,p,0)=L^*(G,p),
\]

and

\[
V_{\mathrm{TV}}(G,p,1)
=
\lceil\log_2\chi(G)\rceil.
\]

For skew \(K_4\), the robust code changes from an unbalanced tree to the
balanced two-bit tree at exact radius \(1/4\). Huber contamination is implemented
separately and is generally a strict subset of the equal-radius TV ball.

## 13. Algorithmic priors and implementation multiplicity

Many programs can implement one observable law. The algorithmic lane separates:

- raw program mass;
- observational-law class mass;
- shortest-description mass;
- multiplicity inflation;
- finite normalization;
- Kraft admissibility;
- dependence on the selected prefix machine and representation.

Grouping implementations prevents syntactic variants from being presented as
separate observable universes, but does not create a machine-independent
universal prior.
