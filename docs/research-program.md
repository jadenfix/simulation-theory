# Research Program

## Goal

Turn simulation-theory discussion into explicit mathematical models whose assumptions, observable implications, computational requirements, and failure modes can be checked independently.

The project is not trying to manufacture one dramatic probability that reality is simulated. It is building a hierarchy of restricted questions:

1. Is the model identifiable from internal observations?
2. Which observer measure turns populations into credences?
3. Which future query family defines the required predictive state?
4. How do approximation, noise, query timing, and selection change that state?
5. What must cross each causal or communication cut?
6. When do routing, replication, coding, or quantum assistance change feasibility?
7. Which claims are lower bounds, which are constructions, and where is the gap?
8. What experiment distinguishes one restricted architecture from ordinary alternatives?

## Completed foundations

### Identification before estimation

Completed results include:

- observational indistinguishability when the simulator class contains the base law;
- Bayes-factor equality for identical observable laws;
- bounded likelihood-ratio evidence ceilings;
- total-variation classification limits;
- Le Cam and Fano minimax bounds;
- hierarchical Bayesian feasibility mixtures;
- robust posterior intervals.

The governing rule is: **do not estimate a parameter for a model that has not first been identified by the declared observation interface.**

### Observer measure and anthropic sensitivity

The observer-count argument is decomposed into survival, deployment, simulation count, observer count, consciousness, evidence compatibility, and duration factors. The repository keeps SSA-, SIA-, and FNC-style conditioning rules separate and proves the Jensen plug-in bias for uncertain observer measure.

The goal is sensitivity analysis rather than an unjustified representation-independent prior.

### Adaptive rendering and predictive equivalence

Completed work includes:

- exact lazy-rendering equivalence by conditional chain factorization;
- adaptive transcript bounds from stepwise total variation;
- conditional-KL chain bounds;
- exact predictive-equivalence state counts;
- approximate packing lower bounds;
- target-centered and arbitrary-center constructive covers;
- exact finite stochastic law tensors;
- deterministic and stochastic network index certificates.

The state object is always defined by allowed future laws, not raw hidden history.

### Selection, intervention, and sequential testing

Completed work includes:

- exact selection log-odds shifts;
- finite selection reweighting;
- latent-intervention mixture sensitivity;
- minimum intervention mass;
- fixed and mixture e-processes;
- optional-stopping-safe thresholds;
- exact finite-horizon crossing probabilities.

No anomaly score is interpreted without a null sampling model, selection process, and stopping guarantee.

### Local physics and parent-resource boundaries

The repository implements local Landauer, Margolus–Levitin, Bekenstein, mass-energy, and Schwarzschild expressions while preserving the cross-level boundary:

\[
\text{internal physical quantity}
\not\Rightarrow
\text{parent implementation cost}.
\]

A parent-resource claim requires a separate implementation map and law-transfer assumption.

## Completed physical and quantum lanes

### Bell and multidimensional predictive geometry

Completed work derives total variation, Fisher information, adaptive KL bounds, visibility-plus-phase geometry, the canonical CHSH disk norm, constructive physical packings, and exact finite phase-drift transcripts.

The program deliberately derives lower bounds from explicit allowed measurements rather than Hilbert-space dimension alone.

### Many-body and relational information

Completed work includes:

- exact computational-basis coordinate-query scaling;
- continuous product-qubit \(L_1\) geometry;
- graph-state weighted-Hamming geometry;
- cycle-state two-local blindness with three-local access;
- finite coding-theoretic relational packings;
- cat-state proper-marginal blindness;
- exact parity sufficient statistics for online continuation.

These constructions show that simple low-order marginals do not imply simple global predictive state.

### Noise and predictive rate distortion

Independent local flips produce exact cat-parity visibility

\[
c_\ell(p)=(1-2p)^\ell.
\]

Completed results include exact noisy transcript laws, proper-marginal blindness, repeated-BSC inference, KL/Pinsker necessary counts, Bhattacharyya sufficient counts, sharp worst-query thresholds, finite Gilbert packings, and the average rate-distortion lower bound

\[
m[1-H_2(D/c)].
\]

### Stabilizer-code locality

The binary-symplectic module implements stabilizers, normalizers, code distance, logical cosets, projectors, and reduced-state checks. It proves complete local indistinguishability below distance and independently verifies the five-qubit \([[5,1,3]]\) code.

Code distance, stabilizer weight, logical weight, query weight, and selected-error protection remain distinct notions.

## Completed causal and network lanes

### Classical and quantum random-access cuts

Completed results include:

- exact one-way INDEX injectivity;
- bounded-error information lower bounds;
- weighted-query KKT allocation;
- memory-communication cut tradeoffs;
- parity-reconciliation equivalence;
- isolated-region replication;
- quantum random-access converses;
- entanglement-assisted factor-two bounds;
- exact dense-coding achievability;
- finite two-to-one and three-to-one qubit random-access codes.

Query timing is treated as a resource. A query known before encoding can reduce linear communication to one answer symbol.

### Progressive query revelation

The two-stage program gives exact shared/branch capacity regions for partition hints, branch-aware bounded-error converses, unassisted and assisted quantum variants, constructive finite protocols, and predictive-class coarsening after each hint.

Design-wide branch budgets and one executed branch are kept separate.

### Predictive network min-cuts

For finite deterministic query families, exact class labels are routed through integer-capacity networks. Completed work includes exact max-flow/min-cut, route decomposition, parity-rank compression, approximate packing cuts, quantum payload accounting, and careful separation of one-sink sufficiency from multi-sink necessity.

### Stochastic predictive covers

Finite stochastic future laws now have:

- exact equivalence classes;
- weighted TV and KL geometry;
- strict packing lower bounds;
- exact target-centered set-cover upper bounds;
- arbitrary-center Bernoulli covering;
- three-way network certificates: impossible, constructively feasible, or unresolved.

The gap between packing and unrestricted covering is not hidden.

### Stochastic observation-channel contraction

For a shared record-independent channel \(K\), the repository proves

\[
\operatorname{TV}(\mu K,\nu K)
\le
\delta(K)\operatorname{TV}(\mu,
u),
\]

with exact rational certificates, query-specific coefficients, serial submultiplicativity, BSC and erasure examples, and monotonicity of exact classes, strict packings, and target-centered covers.

Observation loss can weaken evidence and reduce the required observable interface. It is not silently reinterpreted as microscopic exact-world compression.

### Finite multicast network coding

The newest completed lane extends one-sink predictive cuts to a bounded common-demand multicast model:

- exact Gaussian elimination and solving over prime fields;
- topological propagation of global encoding vectors;
- sink recovery iff incoming global-vector rank equals source dimension;
- per-sink cut necessity;
- named unit-capacity DAGs and integer-capacity expansion;
- routing-only classification;
- bounded exhaustive scalar-code search;
- analytic butterfly routing impossibility;
- exact binary butterfly coding with \(x_1+x_2\) on the bottleneck;
- exhaustive verification of all 4096 local binary scalar assignments;
- predictive-class injection into \(\mathbb F_p^h\).

The project does not yet claim the general multicast max-flow/min-cut theorem. It owns the finite theorems and certificates it proves.

## Current frontier campaigns

### Campaign A: bounded general multicast construction

The butterfly demonstrates that coding can resolve a routing conflict. The next step is a constructive bounded multicast program across arbitrary finite DAGs.

Targets:

1. Implement algebraic multicast construction for one source and common-demand sinks.
2. Derive explicit field-size sufficiency conditions.
3. Distinguish scalar from vector codes and track block length.
4. Produce exact failure certificates when a selected field is too small.
5. Compare exhaustive search, randomized coefficient selection, and deterministic construction.
6. Preserve receiver-wise cut necessity separately from constructive sufficiency.
7. Add formal proof receipts for global-vector propagation and sink decoding.

Quality boundary: do not cite a general theorem and then treat a finite implementation as verified. The constructor and checker must be independently testable.

### Campaign B: approximate stochastic multicast

Current multicast uses exact deterministic class labels. Current stochastic networks use one sink. The next bridge should combine them.

Research questions:

1. Can several sinks share one upstream stochastic cover index?
2. When do heterogeneous sink tolerances require different refinements?
3. Which demands are common multicast, function computation, or multiple unicast?
4. How should a source prior alter worst-record cover design?
5. Can one code interpolating predictive centers rather than only target labels?
6. What packing cuts remain necessary at each sink?
7. What constructive cover or rate-distortion code is jointly feasible?

Deliverables:

- typed sink-demand objects;
- per-sink distortion metrics;
- common-refinement and sink-specific cover solvers;
- network lower/upper certificates;
- bounded examples where coding strictly improves replication or routing.

### Campaign C: noisy edges and robust channels

Observation channels and communication edges are currently modeled separately. The next lane must preserve that distinction while composing them.

Targets:

1. Add finite noisy edge kernels.
2. Separate source coding, channel coding, network coding, and observation post-processing.
3. Compute Dobrushin and KL contraction along paths and cuts.
4. Add uncertain channel sets and worst-case robust certificates.
5. Distinguish record-independent noise from record-dependent intervention.
6. Add erasures, correlated failures, and adversarial contamination.
7. Prove when coding restores reliable class transmission and at what block length.

Noisy-edge capacity must not be inferred from one-shot total-variation contraction alone.

### Campaign D: progressive causal networks

The repository has progressive hints on one cut and exact multicast on one stage. The next target is a query-revelation tree embedded in a network.

Research questions:

1. Which state must cross before each hint?
2. Which branches can share upstream summaries?
3. How do branch-specific covers refine after observations?
4. When can later side information decode a coded bottleneck symbol?
5. How do memory, communication, and delay trade off?
6. Which branch capacities are design-wide versus per execution?
7. How does quantum assistance change each stage without being double-counted?

### Campaign E: scalable quantum-code families

The five-qubit code is a bounded checker, not a scaling theory. Next targets include:

- CSS construction from classical parity-check matrices;
- Steane \([[7,1,3]]\) validation;
- concatenation recurrences;
- surface/toric-code patches;
- logical predictive packings over several encoded qubits;
- noisy syndrome-history state;
- distributed logical queries across causal regions.

Every result must distinguish code distance, stabilizer weight, degeneracy, logical operator weight, and query locality.

### Campaign F: dynamic update-time lower bounds

State cardinality does not determine update cost. Future work should measure:

- update time after one observation or syndrome change;
- query time;
- random-bit and field-operation complexity;
- preprocessing versus online work;
- dynamic parity cell-probe bounds;
- stabilizer-tableau update cost;
- network recoding after edge failure;
- cover-cell changes under drifting stochastic laws.

The goal is a bounded time-space-communication tradeoff, not an unsupported claim that the universe is computationally expensive.

### Campaign G: restricted empirical architectures

For each candidate physical architecture—lattice, finite precision, constrained randomness, approximate rendering, or limited communication—require:

1. a declared null and alternative law;
2. nuisance parameters and ordinary alternatives;
3. a leakage-safe data pipeline;
4. a pre-registered likelihood, e-process, or confidence sequence;
5. calibration and power;
6. explicit model-selection and stopping rules;
7. a statement of which broader simulator classes remain untouched.

No anomaly becomes simulation evidence merely because it is surprising.

### Campaign H: observer-measure and algorithmic-prior robustness

Continue in parallel:

- dependence among civilization factors;
- duplicate-copy sensitivity;
- SSA/SIA/FNC robustness surfaces;
- uncertain consciousness instantiation;
- complete-evidence rarity;
- alternative prefix machines;
- compiler-equivalent program aggregation;
- observational-law versus implementation priors.

The target is transparent sensitivity, not a universal prior assumed into existence.

## Quality gates

A result is ready for `main` only when:

1. The claim has an explicit finite, universal, asymptotic, or empirical scope.
2. Assumptions and nonclaims appear next to the claim.
3. A derivation has an exact checker or independently reproducible calculation where applicable.
4. Closed forms are checked against bounded enumeration when possible.
5. Numerical examples label invented priors and fixed seeds.
6. Sequential results state their sampling and stopping models.
7. Locality results distinguish local marginals from aggregated higher-weight protocols.
8. Noise results state independence, correlation, and parameter-knowledge assumptions.
9. Quantum results separate qubits, classical payload, receiver memory, and preshared entanglement.
10. Progressive results separate shared-stage capacity, branch budgets, and executed paths.
11. Network results separate one-sink sufficiency, per-sink necessity, routing, replication, coding, and multicast demand type.
12. Search-based impossibility claims require exhaustion of the declared finite domain; capped searches remain incomplete.
13. Packing lower bounds, target-centered covers, arbitrary-center covers, rate-distortion results, and constructions remain distinct.
14. Physical results avoid cross-level resource leakage.
15. A finite result is never promoted into a generic simulation conclusion.
16. Internal bits, symbols, qubits, operations, and capacities are not silently converted into parent hardware.

## Tempera Math integration

The claim manifests in this repository remain the source of truth. Tempera Math may later provide content-addressed registration, proof graphs, exact finite certificates, and independent checker receipts.

Any bridge must preserve:

- theorem versus model-result versus finite-check status;
- every assumption and nonclaim;
- exact source revision and checker command;
- graph size, field, horizon, locality, tolerance, block length, noise law, assistance model, and search domain;
- the difference between structural validation and mathematical execution.

See [`tempera-math-bridge.md`](tempera-math-bridge.md).

## Nonclaims

This project does not claim that quantum mechanics, Bell violation, entanglement, graph states, quantum codes, error correction, random-access coding, network coding, max flow, min cuts, predictive equivalence, stochastic covers, information bounds, Planck scales, mathematical elegance, observer effects, or finite signal speed are evidence of simulation by themselves.

Rejecting one restricted implementation does not reject every possible simulator. Finding one anomaly does not favor simulation until it is more likely under a specified simulator model than under serious physical, measurement, selection, and intervention alternatives.
