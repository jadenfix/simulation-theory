# simulation-theory

A first-principles mathematical and computational investigation of simulation hypotheses.

This repository does **not** assume that reality is simulated. It asks a narrower and more scientifically useful question:

> What can be inferred, proved, tested, or ruled out once every observer-selection, statistical, computational, causal, quantum, and physical assumption is made explicit?

The central boundary is simple:

A generic claim that “some external process generates our observations” is not internally identifiable when that process is permitted to reproduce the same observable probability law as ordinary physics. Scientific progress therefore requires a **restricted simulator model** with a declared observable law, approximation mechanism, architecture, intervention policy, query interface, or physical implementation assumption.

## Core conclusion

If a permitted simulator model and a base model induce the same internal observable law,

\[
P_{\mathrm{sim}}=P_{\mathrm{base}},
\]

then every internal test has the same distribution under both models and

\[
BF_{\mathrm{sim}:\mathrm{base}}=1.
\]

No experiment, classifier, Bayesian update, or larger AI model can recover information that is absent from the observable distribution.

The productive program is therefore:

1. define a restricted hypothesis;
2. derive its observable law;
3. establish identifiability before estimation;
4. separate lower bounds from constructions;
5. test the resulting finite claims independently;
6. keep every nonclaim and parent-substrate assumption explicit.

## Research discipline

Every repository claim is typed as one of:

- **Theorem** — follows from stated assumptions.
- **Model result** — exact inside one specified model, not a statement about reality.
- **Finite check** — reproducible computation on a bounded domain.
- **Open problem** — a research target, not an established conclusion.

Machine-readable claim manifests record scope, assumptions, evidence paths, and nonclaims. A CI pass validates code and bounded certificates; it does not promote a finite check into a universal theorem.

## Result map

### 1. Statistical identifiability and evidence ceilings

The repository formalizes:

- unrestricted observational indistinguishability;
- Bayes-factor equality for identical laws;
- bounded likelihood-ratio evidence ceilings;
- optimal equal-prior classification

  \[
  A^\star=\frac{1+\operatorname{TV}(P,Q)}2;
  \]

- Le Cam two-point estimation bounds;
- Fano multi-model identification bounds;
- finite sample-size necessities for restricted architecture families;
- robust posterior intervals under prior and likelihood uncertainty.

The point is methodological: **identification comes before estimation**.

### 2. Bayesian and anthropic uncertainty

Observer counting is decomposed into its hidden factors instead of being treated as one number:

\[
M_S
=
\sum_i r_i d_i s_i n_i c_i q_i\tau_i.
\]

The code and proofs keep separate:

- civilization survival and technical feasibility;
- deployment policy;
- number of simulated environments;
- observer or observer-moment measure;
- consciousness assumptions;
- compatibility with the observer's complete evidence;
- duration and duplication conventions.

For uncertain simulated measure \(X\), the Jensen result

\[
E\!\left[\frac{X}{B+X}\right]
\le
\frac{E[X]}{B+E[X]}
\]

shows why plugging an expected observer count into a nonlinear ratio can systematically overstate the model-averaged result.

Finite SSA-, SIA-, and FNC-style conditioning rules are implemented as sensitivity models rather than silently treated as one uniquely correct prior.

### 3. Adaptive rendering and predictive state

Exact lazy generation is observationally equivalent to pre-generating a hidden world when every response is sampled from the exact target conditional:

\[
P(A_{1:T}\mid Q_{1:T})
=
\prod_{t=1}^{T}P(A_t\mid H_t,Q_t).
\]

For approximate renderers, per-step total-variation and conditional-KL errors compose into transcript-level bounds, including adaptive query policies.

The key state concept is predictive equivalence:

\[
h\sim h'
\iff
P(\text{all allowed futures}\mid h)
=
P(\text{all allowed futures}\mid h').
\]

If there are \(K\) exact future-law classes, an exact finite renderer needs exactly \(K\) states and at least

\[
\lceil\log_2K\rceil
\]

fixed-length predictive bits.

For approximation, strict \(2\epsilon\)-packings give state lower bounds, while target-centered and arbitrary-center covers give constructive upper bounds. The gap between converse and construction remains explicit.

### 4. Stochastic future laws, arbitrary centers, and channel contraction

Future queries need not be deterministic. A finite stochastic family assigns a full conditional probability law to every record-query pair.

Under an exogenous query schedule, joint total variation and KL are the query-weighted sums of their conditional counterparts.

For one query with exactly three outcomes, the repository solves the unrestricted arbitrary-center problem exactly. For ternary probability laws \(p,u\),

\[
\boxed{
\operatorname{TV}(p,u)
=
\max_j|p_j-u_j|.
}
\]

A finite target cluster has one \(\epsilon\)-accurate center exactly when

\[
L_j=\max\{0,\max_i p_{ij}-\epsilon\},
\qquad
U_j=\min\{1,\min_i p_{ij}+\epsilon\}
\]

satisfy

\[
L_j\le U_j\quad\forall j,
\qquad
\sum_jL_j\le1\le\sum_jU_j.
\]

Enumerating every feasible target subset, constructing a canonical center, and solving exact finite set cover gives the true arbitrary-center optimum—not merely a target-centered upper bound. For the three simplex vertices the exact phase diagram is:

- three states for \(\epsilon<1/2\);
- two states for \(1/2\le\epsilon<2/3\);
- one uniform state for \(\epsilon\ge2/3\).

This max-coordinate identity is special to exactly three outcomes; higher categorical dimensions require a different geometry.

For a shared record-independent finite outcome channel \(K\), the exact Dobrushin coefficient is

\[
\delta(K)
=
\max_{a,b}
\operatorname{TV}\!\left(K(\cdot\mid a),K(\cdot\mid b)\right),
\]

and

\[
\operatorname{TV}(\mu K,\nu K)
\le
\delta(K)\operatorname{TV}(\mu,
u).
\]

Consequences implemented in the repo:

- exact predictive equivalence can only coarsen;
- strict predictive packings cannot grow;
- target-centered covers cannot grow;
- serial coefficients obey

  \[
  \delta(K_1\cdots K_T)
  \le
  \prod_t\delta(K_t);
  \]

- a binary symmetric channel has coefficient \(1-2q\);
- an erasure channel has coefficient \(1-e\).

Lossy observation can weaken evidence. It cannot create distinguishability absent from the pre-channel law.

### 5. Selection, intervention, and sequential inference

Outcome-dependent retention is modeled as a causal confounder. For a binary event,

\[
\operatorname{logit}(p_{\mathrm{observed}})
=
\operatorname{logit}(p)
+
\log\frac{r_1}{r_0}.
\]

The repository includes:

- exact selection sensitivity intervals;
- arbitrary finite selection reweighting;
- latent-intervention mixture bounds;
- minimum intervention mass needed to explain an observed shift;
- likelihood-ratio e-processes for declared binary signatures;
- mixture e-processes;
- optional-stopping-safe thresholds;
- exact finite-horizon crossing probabilities.

An anomaly is not evidence until its null sampling model, selection process, and stopping rule are stated.

### 6. Physics and cross-level resource boundaries

The local-physics module implements SI-unit forms of:

- Landauer erasure energy;
- Margolus–Levitin dynamical rates;
- Bekenstein information bounds;
- mass-energy conversion;
- Schwarzschild radius;
- mass-limited operation rates.

The crucial boundary is preserved throughout:

\[
\text{internal mass, energy, or entropy}
\not\Rightarrow
\text{parent-substrate cost}
\]

without an implementation map and a law-transfer assumption.

The repository therefore avoids unsupported statements such as “a simulated kilogram requires a kilogram of parent hardware.”

### 7. Quantum predictive geometry

The physical-query program derives predictive distances from explicit measurement families rather than raw Hilbert-space dimension.

Implemented examples include:

- Werner/singlet visibility laws;
- exact Bell total variation and Fisher information;
- adaptive Bell-query KL and sample lower bounds;
- visibility-plus-phase geometry;
- the canonical CHSH disk identity

  \[
  \operatorname{TV}(P_q,P_{q'})
  =
  \frac{\|q-q'\|_\infty}{2\sqrt2};
  \]

- constructive two-dimensional physical packings;
- exact \(n\)-qubit computational-basis query scaling;
- continuous product-qubit \(L_1\) geometry;
- dimension-by-resolution packings.

Quantum amplitudes are not counted as freely retrievable classical facts. Every lower bound is tied to an allowed future observation interface.

### 8. Relational information, noise, and quantum codes

Graph and cat-state constructions isolate information stored in correlations rather than low-order marginals.

For cycle graph states \(C_n\), \(n\ge5\):

- every one- and two-qubit reduction is maximally mixed across all graph-basis labels;
- weight-three stabilizer queries recover the labels;
- uniform generator-query distance is normalized Hamming distance.

For a phase-labeled cat block, every proper local-X transcript is uniform and phase blind, while the complete transcript obeys one global parity constraint.

After \(\ell-1\) outcomes in each of \(m\) open cat blocks, exact continuation has exactly \(2^m\) predictive classes. One parity bit per block is both necessary and sufficient.

Under independent local flip probability \(p\), the relational visibility is

\[
c_\ell(p)=(1-2p)^\ell,
\]

and the average predictive rate-distortion lower bound is

\[
I(Z;M)
\ge
m\left[1-H_2(D/c)\right].
\]

The stabilizer-code module adds exact binary-symplectic rank, normalizer, distance, logical-coset, state-vector, and reduced-density checks. It proves that every encoded state in an \([[n,k,d]]\) code has identical reduced laws on every subset of fewer than \(d\) physical qubits and independently verifies the five-qubit \([[5,1,3]]\) code.

### 9. Causal cuts and query timing

For an \(m\)-bit record sent before an unresolved coordinate query, exact one-way answering requires an injective message:

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

- resident-memory versus communication cut tradeoffs;
- weighted future-query error allocation;
- isolated-region replication bounds;
- indexed parity-reconciliation equivalence;
- explicit finite upper constructions;
- progressive query revelation and shared/branch capacity regions.

Query timing can change exact communication from linear in \(m\) to one bit when the requested coordinate is revealed before encoding.

### 10. Quantum causal cuts

For an unresolved \(m\)-bit future query encoded into \(q\) qubits:

\[
q
\ge
m[1-H_2(\epsilon)]
\]

without assistance, while receiver-side preshared entanglement gives the factor-two converse

\[
q
\ge
\frac m2[1-H_2(\epsilon)].
\]

Superdense coding exactly attains the assisted zero-error rate for full-record transmission. Canonical two-to-one and three-to-one one-qubit random access codes are implemented and exhaustively checked over every record-query pair.

Preshared entanglement, transmitted qubits, receiver memory, and classical payload are kept as separate resources.

### 11. Predictive networks and multicast coding

A deterministic future-query family with \(K\) exact classes requires a class label of

\[
\lceil\log_2K\rceil
\]

bits. For one sink, exact delivery is characterized by the declared source-sink min-cut under the repository's capacity interpretation.

Approximate stochastic families have a three-way certificate:

- below the packing lower bound: impossible;
- above a constructive cover-index upper bound: feasible;
- between them: unresolved by the current certificate.

The exact ternary arbitrary-center solver closes that gap for bounded one-query three-outcome families and turns the optimal center index directly into an exact one-sink capacity requirement.

For several sinks, separate min-cuts are necessary but routing plans may conflict. The finite multicast module implements exact scalar linear coding over prime fields.

For the declared binary butterfly network:

- both sinks have min-cut two;
- all 4096 local binary scalar assignments are checked;
- no routing-only assignment delivers both source symbols to both sinks;
- transmitting \(x_1+x_2\) through the shared bottleneck lets both sinks decode;
- exact predictive classes embed into \(\mathbb F_p^h\) whenever \(K\le p^h\).

The repo does not silently claim the full general multicast theorem; it proves and checks the bounded statements it owns.

### 12. Algorithmic priors and multiplicity

Many syntactically different programs can implement one observable law. The algorithmic-probability lane distinguishes:

- raw program mass;
- observational-law class mass;
- shortest-description mass;
- multiplicity inflation;
- normalized finite observational priors;
- Kraft admissibility.

Grouping implementations prevents each syntactic variant from being presented as a separate observable universe, but it does not create a universal-machine-independent prior.

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
```

Each entry records a stable ID, claim type, exact scope, assumptions, evidence paths, and explicit nonclaims.

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
docs/ternary-predictive-centers.md
docs/research-program.md
docs/sources.md
docs/tempera-math-bridge.md
```

## Code layout

```text
src/simtheory/    theorem models, exact algorithms, and deterministic experiments
tests/            unit, property, exhaustive, and independent finite checks
claims/           machine-readable scope and evidence manifests
docs/             derivations, assumptions, nonclaims, and research roadmap
```

The mathematical core uses only the Python standard library.

## Run locally

```bash
python -m pip install -e . pytest
python -m compileall -q src
python -m pytest
python -m simtheory.experiments
```

GitHub Actions runs editable installation, bytecode compilation, the complete test suite, and the deterministic experiment smoke suite on Python 3.11, 3.12, and 3.13.

## What would count as evidence?

Evidence must favor one **restricted simulator model** over serious alternative physical and measurement models. A useful proposal must state:

1. the null and alternative observable laws;
2. nuisance parameters;
3. measurement and selection channels;
4. the query or intervention protocol;
5. a predeclared likelihood, e-process, or confidence procedure;
6. calibration and power;
7. how ordinary-physics alternatives are excluded.

Quantization, randomness, mathematical laws, finite signal speed, observer effects, Bell violation, entanglement, stabilizer structure, quantum coding, error correction, max flow, min cuts, network coding, predictive equivalence, arbitrary predictive centers, or information bounds are not generic evidence for simulation. Ordinary physical theories and ordinary distributed systems can contain all of those features.

## Current frontier

The highest-value next campaigns are:

- higher-dimensional categorical arbitrary-center geometry beyond three outcomes;
- general bounded multicast construction and field-size sensitivity;
- noisy network coding with source, channel, and network coding kept separate;
- sink-specific predictive functions rather than common-demand multicast;
- robust observation channels drawn from uncertainty sets;
- progressive query revelation across a causal network;
- online update-time and cell-probe lower bounds for overlapping relational constraints;
- scalable CSS, concatenated, and topological code families;
- observer-measure and algorithmic-prior robustness surfaces;
- pre-registered tests for one restricted physical architecture at a time.

## Tempera Math boundary

`tempera-math` may be used as an external certificate and proof-receipt harness. This repository remains the canonical research home.

A script run, CI pass, content hash, or structural validation never promotes a bounded result into an unbounded theorem. Any bridge must preserve claim type, assumptions, nonclaims, exact source revision, checker command, and finite scope.
