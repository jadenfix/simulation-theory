# Research Program

## Goal

Turn simulation-theory discussion into explicit mathematical models whose assumptions, observable implications, and failure modes can be checked independently.

The project is not trying to assign a dramatic single-number probability to “simulation.” It is building a hierarchy of restricted questions:

1. Is the model identifiable from internal observations?
2. What observer measure converts world populations into credences?
3. What computational or physical constraints follow from a specified architecture?
4. What experiment distinguishes that architecture from serious alternatives?
5. What predictive information must an online generator retain to keep adaptive and distributed observations globally consistent?
6. How do noise and tolerated error change the necessary predictive state?
7. What exact evidence remains after selection, intervention, nuisance parameters, and optional stopping are modeled?

## Completed mathematical lanes

### Identification before estimation

- Generic simulator classes containing the base observable law are underidentified.
- Bounded likelihood ratios impose exact Bayesian evidence ceilings.
- Total variation, Le Cam, and Fano quantify finite two-model and multi-model limits.
- Hierarchical Bayesian scenarios preserve technical-feasibility uncertainty instead of hiding it inside an expected observer count.

### Observer measure

- Civilization and observer factors remain separate instead of collapsing into one count.
- The Jensen gap prevents plug-in expected counts from masquerading as model-averaged probabilities.
- Finite SSA/SIA/FNC-presence conventions expose duplication and saturation behavior.

### Adaptive consistency and rendering

- Exact conditional lazy generation is transcript-equivalent to full pre-generation.
- Per-step total-variation and conditional-KL errors have transcript-level bounds.
- Exact and approximate predictive-state packing lower bounds are implemented.
- Finite phase-drift Bell processes support exact adaptive transcript enumeration.

### Causal selection and sequential inference

- Outcome-dependent retention has an exact log-odds sensitivity identity.
- Arbitrary finite reweighting is constructively demonstrated.
- Unrestricted latent interventions have explicit minimum mixture mass.
- Fixed and mixture Bernoulli e-processes are implemented in log space.
- Simple and one-sided composite-null validity is proved.
- Finite-horizon optional-stopping error is audited by exact dynamic programming.

### Physics and representation

- Local Landauer, Margolus–Levitin, Bekenstein, mass-energy, and Schwarzschild expressions are implemented with explicit SI inputs.
- Cross-level cost remains an input assumption rather than an inferred consequence.
- Program multiplicity and Kraft diagnostics expose coding-language sensitivity.

### Physically derived predictive-state geometry

The project now moves from arbitrary probability vectors to explicit bounded physical families:

- one-parameter Werner/singlet Bell visibility laws with exact total variation, Fisher information, and adaptive KL bounds;
- two-parameter visibility-plus-phase laws with a full Fisher matrix and exact predictive geometry;
- canonical CHSH correlation-disk geometry with
  `TV = ||q-q'||_infinity / (2 sqrt(2))`;
- constructive two-dimensional packing with quadratic `1/epsilon` scaling;
- exact n-qubit computational-basis lower bounds derived from allowed coordinate queries;
- continuous d-qubit product-polarization geometry
  `TV = ||q-u||_1 / (2d)`;
- q-ary product packings separating subsystem count from accessible precision.

See [`bell-predictive-bounds.md`](bell-predictive-bounds.md), [`quantum-phase-predictive-bounds.md`](quantum-phase-predictive-bounds.md), [`canonical-chsh-disk-geometry.md`](canonical-chsh-disk-geometry.md), [`quantum-sequential-bounds.md`](quantum-sequential-bounds.md), and [`manybody-predictive-bounds.md`](manybody-predictive-bounds.md).

### Relational information and local blindness

The relational lane isolates predictive information absent from low-order marginals:

- graph-basis stabilizer queries have exact weighted-Hamming predictive geometry;
- cycle graph states with at least five qubits have stabilizer distance three;
- every one- and two-qubit reduction is maximally mixed across all `2^n` cycle graph-basis labels;
- weight-three generators nevertheless reveal all label coordinates;
- finite Gilbert bounds turn normalized-Hamming geometry into robust constant-tolerance memory lower bounds;
- phase-labeled cat states have uniform proper local-X marginals and disjoint complete parity transcripts;
- after `ell-1` outcomes in each of `m` cat blocks, exact online continuation has exactly `2^m` predictive-equivalence classes;
- one parity bit per open block is both necessary and sufficient, producing a tight dynamic consistency-memory theorem.

See [`stabilizer-relational-consistency.md`](stabilizer-relational-consistency.md).

### Noisy relational consistency and predictive rate distortion

The exact relational construction has now been extended to independent local readout noise:

- local flip probability `p` on an `ell`-qubit cat block induces effective parity crossover
  `q=[1-(1-2p)^ell]/2`;
- the complete noisy phase laws have exact TV `(1-2p)^ell`;
- every proper noisy local marginal remains uniform and phase-independent;
- parity is a sufficient statistic for phase inference;
- block locality and robustness trade off because parity visibility decays exponentially with `ell` at fixed `p`;
- repeated parity inference has exact finite binomial TV and Bayes error;
- KL/Pinsker gives necessary repetition counts and Bhattacharyya gives sufficient counts;
- noisy checkpoint signatures have exact geometry
  `TV=c*d_H/m` under uniform queries;
- worst-query memory has a sharp threshold: `m` bits below error `c/2`, zero at or above `c/2` in the declared one-step model;
- finite Gilbert codes give explicit noisy predictive packings;
- uniform signatures under average TV distortion obey the exact information lower bound
  `m[1-H_2(D/c)]`.

See [`noisy-relational-rate-distortion.md`](noisy-relational-rate-distortion.md).

## Current frontier campaigns

### Campaign A: quantum error-correcting and stabilizer-code locality

Graph cycles establish two-local blindness with three-local access. The next target is a family with tunable local-indistinguishability distance and explicit logical predictive geometry.

Candidate programs:

- repetition/cat block products with adjustable locality;
- CSS codes where logical labels are invisible below code distance;
- the three-qubit repetition code as a minimal exact checker;
- the five-qubit perfect code and Steane code on bounded state-vector instances;
- graph families whose minimum stabilizer support grows with system size;
- approximate code states with noisy local indistinguishability.

Deliverables:

1. A typed binary-symplectic Pauli and stabilizer representation.
2. Exact commutation, rank, stabilizer, normalizer, and logical-operator checks.
3. A clean distinction between stabilizer distance, code distance, logical-operator weight, and query weight.
4. Reduced-state equality below a declared locality threshold.
5. Predictive packings over logical labels.
6. Independent brute-force checks for small codes.

### Campaign B: correlated-noise and strong-data-processing bounds

Independent local flips are analytically clean but restrictive. The next noisy lane should include:

- common-mode flips;
- finite-range correlated errors;
- Markov noise along a spatial block;
- adversarial contamination bounded in total variation;
- erasures and delayed observations;
- uncertain noise parameters integrated hierarchically.

Research targets:

1. Determine when proper marginal blindness survives.
2. Replace `(1-2p)^ell` with correlation-function or transfer-matrix expressions.
3. Prove strong-data-processing bounds for relational information through a noisy causal chain.
4. Separate robustness to stochastic noise from robustness to adversarial corruption.
5. Quantify prior sensitivity when the noise law is not known exactly.

### Campaign C: distributed and relativistic consistency

The cat result shows that individually random local outcomes can be tied by a later global parity check. The next program should add causal structure:

- spacelike-separated local observers;
- delayed comparison of authenticated records;
- finite-speed communication;
- adversarial query ordering;
- causal diamonds and allowed information flow.

Research questions:

1. What predictive state must be duplicated versus shared across causal regions?
2. What communication is necessary when records are reconciled?
3. Can commitment be postponed without violating no-signaling and later parity constraints?
4. How do memory and communication trade off under a fixed causal graph?
5. Which lower bounds are ordinary distributed-computing bounds rather than specifically quantum bounds?

### Campaign D: update-time and computational lower bounds

Current theorems mostly lower-bound state cardinality. Memory alone is not enough. Future work should measure:

- update time after a new observation;
- query time for a future conditional law;
- random-bit complexity;
- communication across a distributed renderer;
- preprocessing versus online computation;
- tensor-network contraction or graph traversal cost.

The goal is a bounded time-space tradeoff rather than an unsupported statement that “the universe is expensive to simulate.”

### Campaign E: restricted physical signatures

Select one architecture at a time—lattice, finite precision, constrained pseudorandomness, approximation policy, or distributed consistency mechanism. For each:

1. State the null and alternative observable laws.
2. Identify nuisance parameters and ordinary-physics alternatives.
3. Build a leakage-safe data pipeline.
4. Pre-register a likelihood, e-process, or confidence sequence.
5. Report calibration and power before interpreting data.

No anomaly score is evidence without a null sampling model.

### Campaign F: observer-measure and algorithmic-prior robustness

Continue the nonphysical-inference lanes in parallel:

- explicit distributions over civilization survival, deployment, consciousness, observer lifetime, and evidence rarity;
- dependence and duplicate-copy sensitivity;
- SSA/SIA/FNC robustness surfaces rather than single percentages;
- alternative prefix languages and compiler-equivalent implementations;
- observational-law aggregation and finite universal-machine perturbations.

The target is sensitivity analysis, not a representation-free prior that has not been justified.

## Quality gates

A research result is ready for the main branch only when:

1. The claim has an explicit finite, universal, asymptotic, or empirical scope.
2. Assumptions and nonclaims are written next to the result.
3. The derivation has a test, exact checker, or independently reproducible calculation where applicable.
4. Closed-form identities are checked against brute-force enumeration on bounded instances when possible.
5. Numerical demonstrations use fixed seeds and are labeled illustrative when priors are invented.
6. Sequential claims state their sampling model, retained transcript, and stopping guarantee.
7. Locality claims distinguish one-shot local marginals from adaptive protocols that aggregate a global transcript.
8. Noise claims specify independence, stationarity, and parameter-knowledge assumptions.
9. Physical claims state which laws apply and avoid cross-level leakage.
10. A finite experiment is never promoted into a generic simulation conclusion.
11. A memory lower bound identifies the predictive interface and does not silently become a parent-hardware claim.
12. Average-case, worst-case, necessary, sufficient, exact, and asymptotic statements remain explicitly separated.

## Tempera Math integration

The repository claim manifests remain the source of truth. Tempera Math can later provide content-addressed claim registration, proof graphs, exact finite certificates, and external checker receipts. The adapter must preserve:

- theorem versus model-result versus finite-check status;
- all assumptions and nonclaims;
- exact source revision and checker command;
- bounded graph size, horizon, locality, tolerance, and noise parameters;
- the boundary between structural validation and mathematical execution.

See [`tempera-math-bridge.md`](tempera-math-bridge.md).

## Nonclaims

This project does not claim that quantum mechanics, Bell violation, entanglement, stabilizer structure, error correction, Planck scales, cosmic-ray cutoffs, entropy bounds, mathematical elegance, coincidences, observer effects, or finite signal speed are evidence of simulation by themselves. It does not assume digital physics, substrate-independent consciousness, finite parent resources, or a parent universe obeying our constants.

Rejecting one restricted implementation does not reject every possible simulator. Finding an anomaly does not favor simulation until the anomaly is more likely under a specified simulator model than under serious ordinary-physics and measurement alternatives.
