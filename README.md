# simulation-theory

A first-principles mathematical and computational investigation of simulation
hypotheses.

This repository does **not** assume that reality is simulated. It asks a more
scientifically useful question:

> What can be inferred, proved, tested, or ruled out after the observable
> interface, observer measure, source law, temporal dynamics, approximation
> metric, causal architecture, communication resources, and physical
> implementation assumptions are stated explicitly?

## Core boundary

A generic claim that “some external process generates our observations” is not
internally identifiable when that process may reproduce the same observable law
as an ordinary physical model.

If

\[
P_{\mathrm{sim}}=P_{\mathrm{base}},
\]

then every internal statistic has the same distribution under both models and

\[
BF_{\mathrm{sim}:\mathrm{base}}=1.
\]

No classifier, Bayesian update, larger model, or additional computation can
recover information absent from the observable distribution.

The productive program is therefore:

1. define a **restricted** hypothesis;
2. derive its observable law;
3. establish identifiability before estimation;
4. declare the future-query, intervention, and timing interface;
5. separate converse bounds from constructive protocols;
6. build exact or independently replayable certificates;
7. keep every assumption and nonclaim next to the result.

## Claim discipline

Every result is typed as one of:

- **Theorem** — follows from stated mathematical assumptions.
- **Model result** — exact inside one declared model or finite example.
- **Finite check** — reproducible computation on an explicitly bounded domain.
- **Open problem** — a research target rather than an established conclusion.

Machine-readable manifests under [`claims/`](claims/) record stable IDs, scope,
assumptions, evidence paths, and nonclaims. A test or CI run validates code and
bounded receipts; it never promotes a finite check into a universal theorem.

## First-principles dependency chain

The technical program is organized as a dependency graph:

\[
\text{allowed observations, queries, and interventions}
\]

\[
\Downarrow
\]

\[
\text{observable laws and predictive equivalence}
\]

\[
\Downarrow
\]

\[
\text{exact classes, packings, covers, channels, or confusion graphs}
\]

\[
\Downarrow
\]

\[
\text{state, message, center-index, or codebook requirements}
\]

\[
\Downarrow
\]

\[
\text{causal-cut, network, source-coding, robustness, and control constraints}.
\]

Changing any upstream interface can change every downstream result. Raw hidden
state count, Hilbert-space dimension, or internal mass is never substituted for
an operationally declared observation problem.

# Result map

## 1. Identification, evidence ceilings, and sequential inference

The statistical foundation includes:

- unrestricted observational indistinguishability;
- Bayes-factor equality for identical laws;
- posterior movement ceilings from bounded likelihood ratios;
- equal-prior optimal classification

  \[
  A^\star=\frac{1+\operatorname{TV}(P,Q)}2;
  \]

- Le Cam and Fano lower bounds;
- finite sample-size necessities for restricted architecture families;
- hierarchical feasibility mixtures and robust posterior intervals;
- selection-policy and latent-intervention ambiguity;
- anytime-valid likelihood-ratio e-processes;
- exact finite-horizon optional-stopping audits.

The governing rule is: **identification comes before estimation**.

## 2. Observer measure and anthropic sensitivity

Observer counting is decomposed rather than hidden inside one dramatic number.
The model keeps separate:

- civilization survival and technical feasibility;
- deployment policy;
- number of environments;
- observers versus observer-moments;
- consciousness assumptions;
- compatibility with complete evidence;
- duration and duplication conventions.

For uncertain simulated measure \(X\),

\[
E\!\left[\frac{X}{B+X}\right]
\le
\frac{E[X]}{B+E[X]},
\]

so inserting an expected count into a nonlinear ratio can overstate the
properly averaged result. Finite SSA-, SIA-, and FNC-style rules are implemented
as sensitivity models, not collapsed into one universal prior.

## 3. Adaptive rendering and predictive state

Exact lazy generation is transcript-equivalent to pre-generating a hidden world
when each answer is sampled from the exact target conditional:

\[
P(A_{1:T}\mid Q_{1:T})
=
\prod_{t=1}^T P(A_t\mid H_t,Q_t).
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

If there are \(K\) exact future-law classes, an exact finite renderer requires
\(K\) predictive states and at least

\[
\lceil\log_2 K\rceil
\]

fixed-length bits. For approximation, strict \(2\epsilon\)-packings provide
converse lower bounds and arbitrary-center covers provide constructive upper
bounds. Gaps are reported rather than silently closed.

## 4. Stochastic future laws, arbitrary centers, and observation channels

Finite stochastic query families assign a full conditional outcome law to each
record-query pair. Under an exogenous query schedule, joint TV and KL are
query-weighted sums of their conditional counterparts.

Exact rational arbitrary-center optimization is implemented for finite
categorical laws, including Farkas infeasibility receipts and minimax LP duals.
For one ternary query,

\[
\operatorname{TV}(p,u)=\max_j|p_j-u_j|,
\]

which yields exact common-center feasibility and closed finite examples.

For a record-independent outcome channel \(K\), the exact Dobrushin coefficient

\[
\delta(K)
=
\max_{a,b}
\operatorname{TV}
\bigl(K(\cdot\mid a),K(\cdot\mid b)\bigr)
\]

satisfies

\[
\operatorname{TV}(\mu K,\nu K)
\le
\delta(K)\operatorname{TV}(\mu,
u).
\]

Lossy observation can weaken evidence. It cannot create distinguishability that
was absent before the channel.

## 5. Physical and quantum predictive geometry

Physical-query lower bounds are derived from explicit measurement families,
not raw Hilbert-space dimension.

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
- exact adaptive phase-drift transcript laws.

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

With independent local flip probability \(p\), parity visibility is

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

The repository includes resident-state versus communication tradeoffs, weighted
future-query allocation, indexed parity reconciliation, isolated-region
replication, progressive query revelation, and explicit finite upper protocols.

Without entanglement assistance, an unresolved \(m\)-bit random-access record
encoded into \(q\) qubits obeys

\[
q\ge m[1-H_2(\epsilon)].
\]

Receiver-side preshared entanglement changes the coefficient by at most a factor
of two. Exact dense coding attains the assisted zero-error full-record rate.
Query timing is itself a resource: revealing the requested coordinate before
encoding can reduce linear communication to one answer symbol.

## 8. Predictive networks and function computation

For one sink, a finite predictive-class index can be routed through an integer-
capacity network exactly when the declared min-cut carries the required fixed-
length index. Approximate stochastic networks distinguish:

- **impossible** below a packing lower bound;
- **constructively feasible** above a cover-index upper bound;
- **unresolved** in between.

The finite multicast lane checks all 4096 binary scalar assignments on a
butterfly network and verifies that the shared bottleneck must carry
\(x_1+x_2\) rather than a routed uncoded symbol.

For sink-specific linear demands over \(\mathbb F_p\), exact recoverability is

\[
\operatorname{rowspan}(B_t)
\subseteq
\operatorname{rowspan}
\begin{pmatrix}G_t\\S_t\end{pmatrix}.
\]

For arbitrary finite nonlinear functions, define the confusion edge

\[
x\sim_c y
\iff
\exists t:
s_t(x)=s_t(y)
\text{ and }
f_t(x)\ne f_t(y).
\]

Zero-error common-message encoders are precisely proper colorings, so

\[
|\mathcal M|_{\min}=\chi(G),
\qquad
b_{\min}=\lceil\log_2\chi(G)\rceil.
\]

Every finite simple graph can be realized as a finite side-information function
problem. All 64 labeled four-vertex graphs are independently audited.

## 9. Prior-weighted zero-error source coding

Chromatic number minimizes the hard message alphabet, not expected bits under a
nonuniform source law.

For a proper independent-set partition \(\mathcal P\) and rational prior
\(\pi\), class probabilities are

\[
p_j(\mathcal P)=\sum_{x\in C_j}\pi_x.
\]

Huffman coding is exact for each partition, and exhaustive bounded partition
search gives

\[
\boxed{
L^*(G,\pi)
=
\min_{\mathcal P\in\operatorname{IndPart}(G)}
L_H\bigl(p(\mathcal P)\bigr).
}
\]

The implementation keeps separate:

- minimum message alphabet;
- fixed-length bits;
- expected prefix length;
- peak codeword length;
- declared-state versus positive-support-only zero error;
- one-shot cost versus block-amortized rate.

For complete-confusion i.i.d. blocks,

\[
H(P)
\le
\frac{L_H(P^m)}m
<
H(P)+\frac1m
\]

under positive support.

## 10. Finite-prior and polyhedral robustness

For finite prior scenarios \(\Pi\), deterministic minimax cost is

\[
V_{\mathrm{det}}
=
\min_c\max_{\pi\in\Pi}E_\pi[\ell_c].
\]

Minimax regret is kept separate:

\[
R_{\mathrm{det}}
=
\min_c\max_{\pi\in\Pi}
\left(E_\pi[\ell_c]-L^*(G,\pi)\right).
\]

Shared source-independent codebook randomness produces an exact finite rational
zero-sum game with zero primal-dual gap.

The ambiguity geometry is generalized to arbitrary compact rational polytopes

\[
\mathcal U
=
\{q\in\Delta_{n-1}:Aq\le b\}.
\]

The simplex equality is eliminated exactly, all bounded vertices are enumerated
below active-basis caps, empty systems carry sparse Farkas witnesses, and linear
expectation extrema carry exact LP dual multipliers. Continuous polyhedral
minimax regret reduces to ambiguity vertices because

\[
q\mapsto E_q[\ell_c]-L^*(G,q)
\]

is convex piecewise linear.

A separate statistical layer calibrates TV confidence regions from finite i.i.d.
multinomial samples. Transcendental radii are evaluated at high precision and
rounded outward onto a rational grid; downstream robust optimization remains
exact conditional on that conservative radius.

## 11. Continuous TV-ball robustness and shared codebook mixtures

For nominal prior \(p\) and radius \(\rho\),

\[
\mathcal U_{\mathrm{TV}}(p,\rho)
=
\{q:\operatorname{TV}(q,p)\le\rho\}.
\]

For a fixed value vector, total variation is exactly moved probability mass.
The robust maximum is obtained by moving mass from the lowest-value donors to
maximum-value recipients. Every transfer, extremal law, and expectation is
rational.

The same problem has an exact fractional-knapsack dual with complementary
slackness. Fixed-code robust expectation is continuous, monotone, piecewise
linear, and concave in radius for maximization.

The outer deterministic coding problem is

\[
V_{\mathrm{TV}}(G,p,\rho)
=
\min_c
\sup_{q:\operatorname{TV}(q,p)\le\rho}E_q[\ell_c].
\]

With source-independent shared codebook randomness, the continuous adversary
reduces exactly to a finite game over TV-polytope vertices. The least-favorable
dual barycenter is replayed by the nominal coding oracle. Exact Carathéodory
elimination bounds support size without confusing support count with random-seed
entropy.

## 12. Static coding under bounded source-law drift

A static ambiguity ball and a changing source law are different models. The
finite path model is

\[
q_0=p,
\qquad
\operatorname{TV}(q_t,q_{t-1})\le\eta.
\]

For one fixed cost vector \(\ell\), canonical TV mass transport can be continued
monotonically, giving

\[
\sup_{\text{paths}}
\sum_{t=1}^T q_t^\top\ell
=
\sum_{t=1}^T
\sup_{\operatorname{TV}(q,p)\le\min(t\eta,1)}
q^\top\ell.
\]

The static-code optimizer exhausts every bounded componentwise-undominated
zero-error prefix code. For skew \(K_4\), the exact finite-horizon decision
boundary is

\[
\eta_c(T)=\frac{1}{2(T+1)}.
\]

Statistical estimation uncertainty and separately declared drift combine by TV
triangle inequality, but the drift assumption does not acquire statistical
coverage merely by being added to a confidence radius.

## 13. Coupled drift, changing objectives, and code reconfiguration

When the state-cost vector changes with time, independently maximizing each
period can select mutually unreachable source laws. The exact coupled problem is

\[
\max_{q_{1:T}}
\sum_{t=1}^Tq_t^\top g_t
\quad\text{s.t.}\quad
q_0=p,
\quad
\operatorname{TV}(q_t,q_{t-1})\le\eta_t.
\]

Finite-alphabet TV is represented exactly by event halfspaces. After eliminating
one simplex coordinate per period, the path is a bounded rational polytope in
\(T(n-1)\) variables. The implementation enumerates all vertices below a hard
cap and independently supplies an exact LP dual with complementary slackness.

The sum of independent expanding-ball optima is only an upper bound. For

\[
p=(1/2,1/2),
\quad
\eta_1=\eta_2=1/4,
\quad
g_1=(0,1),
\quad
g_2=(1,0),
\]

the independent relaxation is \(7/4\), while the exact coupled value is

\[
\boxed{5/4.}
\]

The outer decision problem chooses a precommitted codebook sequence and may pay
\(\kappa\) per switch. For uniform \(K_3\) with two drift steps of \(1/6\),
rotating the length-one leaf gives

\[
V_{\mathrm{rotate}}=11/3,
\qquad
V_{\mathrm{static}}=23/6.
\]

The exact reconfiguration gain and switching threshold are both

\[
\boxed{1/6.}
\]

This is the first dynamic-control layer in the repository. It does not yet
grant the encoder hidden access to the current source law; the complete sequence
is committed before the adversarial path is chosen.

See [`docs/coupled-drift-code-sequences.md`](docs/coupled-drift-code-sequences.md).

## 14. Algorithmic priors and implementation multiplicity

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

# Repository map

## Claim manifests

```text
claims/claims-v1.json
claims/quantum-phase-claims.json
claims/stabilizer-relational-claims.json
claims/noisy-relational-claims.json
claims/stabilizer-code-claims.json
claims/distributed-consistency-claims.json
claims/quantum-causal-cut-claims.json
claims/progressive-query-claims.json
claims/predictive-network-claims.json
claims/stochastic-predictive-claims.json
claims/stochastic-channel-claims.json
claims/multicast-network-coding-claims.json
claims/ternary-predictive-claims.json
claims/functional-network-claims.json
claims/confusion-graph-claims.json
claims/prior-weighted-code-claims.json
claims/robust-prior-code-claims.json
claims/distributionally-robust-code-claims.json
claims/polyhedral-regret-confidence-claims.json
claims/polyhedral-dual-claims.json
claims/prior-drift-claims.json
claims/coupled-drift-claims.json
```

## Proof and derivation map

```text
docs/formal-results.md
docs/bell-predictive-bounds.md
docs/quantum-phase-predictive-bounds.md
docs/canonical-chsh-disk-geometry.md
docs/quantum-sequential-bounds.md
docs/manybody-predictive-bounds.md
docs/stabilizer-relational-consistency.md
docs/noisy-relational-rate-distortion.md
docs/stabilizer-code-locality.md
docs/distributed-causal-consistency.md
docs/quantum-causal-cut-random-access.md
docs/progressive-query-revelation.md
docs/predictive-network-mincuts.md
docs/stochastic-predictive-covers.md
docs/stochastic-channel-contraction.md
docs/multicast-network-coding.md
docs/functional-network-computation.md
docs/nonlinear-confusion-graphs.md
docs/ternary-predictive-centers.md
docs/prior-weighted-zero-error-coding.md
docs/finite-prior-robust-coding.md
docs/distributionally-robust-tv-coding.md
docs/tv-transport-dual.md
docs/polyhedral-regret-confidence.md
docs/polyhedral-dual-certificates.md
docs/prior-drift-path-robustness.md
docs/coupled-drift-code-sequences.md
docs/research-program.md
docs/sources.md
docs/tempera-math-bridge.md
```

## Code layout

```text
src/simtheory/    theorem models, exact algorithms, and deterministic experiments
tests/            unit, property, exhaustive, and independent finite checks
claims/           machine-readable scope, evidence, assumptions, and nonclaims
docs/             derivations, examples, quality boundaries, and research roadmap
```

The mathematical core uses only the Python standard library.

## Run locally

```bash
python -m pip install -e . pytest
python -m compileall -q src
python -m pytest
python -m simtheory.experiments
```

GitHub Actions runs editable installation, bytecode compilation, the complete
test suite, and the deterministic experiment smoke suite on Python 3.11, 3.12,
and 3.13.

# What would count as evidence?

Evidence must favor a **restricted simulator model** over serious alternative
physical, measurement, selection, and intervention models. A useful proposal
must predeclare:

1. null and alternative observable laws;
2. nuisance parameters;
3. measurement and selection channels;
4. query or intervention protocol;
5. likelihood, e-process, confidence sequence, or other inferential rule;
6. calibration, power, and stopping behavior;
7. ordinary-physics alternatives and how they are excluded;
8. which broader simulator classes remain untouched.

Quantization, randomness, mathematical laws, Bell violation, entanglement,
stabilizer structure, quantum coding, graph coloring, Huffman coding, robust
optimization, network coding, max flow, min cuts, predictive equivalence,
dynamic programming, or information bounds are not generic evidence for
simulation. Ordinary physical theories and ordinary distributed systems can
contain all of those structures.

# Current frontier

The highest-value next campaigns are:

- adaptive codebook policies under an explicitly declared observation kernel;
- dynamic regret when the encoder learns only realized symbols rather than the
  hidden source law;
- exact finite-horizon Bellman and minimax-game certificates;
- stochastic or adversarially uncertain drift budgets;
- KL-, Wasserstein-, and physics-derived transition geometry with certified
  primal and dual bounds;
- allowed-error function computation, where an unweighted confusion graph no
  longer contains the full risk information;
- multi-letter graph products and asymptotic side-information source coding;
- queueing, buffer, and tail-delay consequences of variable-length messages;
- progressive query revelation embedded in causal networks;
- scalable CSS, concatenated, and topological code families;
- dynamic update-time and cell-probe lower bounds;
- preregistered tests of one restricted physical architecture at a time.

## Tempera Math boundary

`tempera-math` may be used as an external content-addressed proof and receipt
harness. This repository remains the canonical research home.

A script run, CI pass, content hash, or structural validation never promotes a
bounded result into an unbounded theorem. Any bridge must preserve claim type,
assumptions, nonclaims, source revision, checker command, finite domain, and the
difference between structural validation and mathematical execution.
