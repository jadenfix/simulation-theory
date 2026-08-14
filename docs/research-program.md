# Research Program

## Goal

Turn simulation-theory discussion into explicit mathematical models whose assumptions, observable implications, and failure modes can be checked independently.

The project is not trying to assign a dramatic single-number probability to “simulation.” It is building a hierarchy of restricted questions:

1. Is the model identifiable from internal observations?
2. What observer measure converts world populations into credences?
3. What computational or physical constraints follow from a specified architecture?
4. What experiment distinguishes that architecture from serious alternatives?
5. What predictive information must an online generator retain to keep adaptive and distributed observations globally consistent?
6. How do noise, error correction, query-revelation timing, classical or quantum communication, and tolerated approximation change the necessary predictive state?
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

The project moves from arbitrary probability vectors to explicit bounded physical families:

- one-parameter Werner/singlet Bell visibility laws with exact total variation, Fisher information, and adaptive KL bounds;
- two-parameter visibility-plus-phase laws with a full Fisher matrix and exact predictive geometry;
- canonical CHSH correlation-disk geometry with `TV = ||q-q'||_infinity / (2 sqrt(2))`;
- constructive two-dimensional packing with quadratic `1/epsilon` scaling;
- exact n-qubit computational-basis lower bounds derived from allowed coordinate queries;
- continuous d-qubit product-polarization geometry `TV = ||q-u||_1 / (2d)`;
- q-ary product packings separating subsystem count from accessible precision.

See [`bell-predictive-bounds.md`](bell-predictive-bounds.md), [`quantum-phase-predictive-bounds.md`](quantum-phase-predictive-bounds.md), [`canonical-chsh-disk-geometry.md`](canonical-chsh-disk-geometry.md), [`quantum-sequential-bounds.md`](quantum-sequential-bounds.md), and [`manybody-predictive-bounds.md`](manybody-predictive-bounds.md).

### Relational information and local blindness

- graph-basis stabilizer queries have exact weighted-Hamming predictive geometry;
- cycle graph states with at least five qubits have stabilizer distance three;
- every one- and two-qubit reduction is maximally mixed across all `2^n` cycle graph-basis labels;
- weight-three generators nevertheless reveal all label coordinates;
- finite Gilbert bounds turn normalized-Hamming geometry into robust constant-tolerance memory lower bounds;
- phase-labeled cat states have uniform proper local-X marginals and disjoint complete parity transcripts;
- after `ell-1` outcomes in each of `m` cat blocks, exact online continuation has exactly `2^m` predictive-equivalence classes;
- one parity bit per open block is both necessary and sufficient.

See [`stabilizer-relational-consistency.md`](stabilizer-relational-consistency.md).

### Noisy relational consistency and predictive rate distortion

- local flip probability `p` on an `ell`-qubit cat block induces effective parity crossover `q=[1-(1-2p)^ell]/2`;
- complete noisy phase laws have exact TV `(1-2p)^ell`;
- every proper noisy local marginal remains uniform and phase-independent;
- parity is a sufficient statistic for phase inference;
- block locality and robustness trade off because parity visibility decays exponentially with `ell` at fixed `p`;
- repeated parity inference has exact finite binomial TV and Bayes error;
- KL/Pinsker gives necessary repetition counts and Bhattacharyya gives sufficient counts;
- noisy checkpoint signatures have exact geometry `TV=c*d_H/m` under uniform queries;
- worst-query memory has a sharp threshold: `m` bits below error `c/2`, zero at or above `c/2` in the declared one-step model;
- uniform signatures under average TV distortion obey `m[1-H_2(D/c)]`.

See [`noisy-relational-rate-distortion.md`](noisy-relational-rate-distortion.md).

### Stabilizer-code distance and logical locality

- exact GF(2) rank, span, symplectic commutation, stabilizer, normalizer, and quotient calculations;
- code distance `d=min wt(N(S)\S)` separated from minimum stabilizer weight;
- projected Pauli trichotomy: detectable operators project to zero, stabilizers act as scalars, and normalizer elements outside the stabilizer act logically;
- every encoded state has the same reduced density matrix on every subset of fewer than `d` qubits;
- an entropy proof of the quantum Singleton bound `n-k>=2(d-1)`;
- exact verification that the five-qubit code is `[[5,1,3]]` and saturates Singleton;
- state-vector projector checks of logical basis states, stabilizer eigenvalues, logical mappings, and one-/two-qubit reduced-state equality;
- demonstration that the three-qubit bit-flip repetition code has full quantum distance one despite detecting one-qubit X errors;
- logical-coordinate query geometry and an `mk`-bit predictive lower bound for `m` blocks encoding `k` logical bits each.

See [`stabilizer-code-locality.md`](stabilizer-code-locality.md).

### Distributed classical causal-cut consistency

- exact one-way INDEX answering requires an injective message and therefore `m` bits for an unresolved `m`-coordinate future query;
- shared randomness independent of the record cannot remove the exact collision witness;
- uniform records and uniform post-message queries obey the information lower bound `m[1-H_2(epsilon)]`;
- resident predictive state and later pre-query communication obey one combined cut-set tradeoff;
- indexed parity reconciliation `A_i xor B_i`, with `B_i` local, has the same remote-record lower bound as INDEX;
- weighted query distributions yield the KKT allocation `e_i=1/(1+2^(lambda w_i))`, exposing how rare coordinates are discarded first;
- isolated answer regions with no shared record store require replicated local storage budgets;
- an exact finite prefix-storage protocol supplies an explicit upper bound and keeps the gap from the information lower bound visible.

See [`distributed-causal-consistency.md`](distributed-causal-consistency.md).

### Quantum random-access causal cuts

The causal-cut program permits quantum messages and cleanly separates unassisted from entanglement-assisted architectures:

- coordinatewise binary Fano plus quantum data processing gives `I(X;Q) >= sum_i [1-H_2(e_i)]`;
- a `q`-qubit unassisted message obeys `I(X;Q)<=q`, yielding `q>=m[1-H_2(epsilon)]` under uniform average error;
- receiver-side preshared entanglement independent of the record permits at most a `2q` information increase, yielding `q>=m[1-H_2(epsilon)]/2`;
- exact unassisted transmission needs `m` qubits;
- exact entanglement-assisted transmission needs `ceil(m/2)` qubits and is achieved by superdense coding;
- revealing the query before the message reduces exact communication to one qubit;
- inverse binary entropy converts fixed qubit budgets into minimum-error converses;
- canonical two-to-one and three-to-one one-qubit random access codes are implemented and checked over every record-query pair;
- nonuniform quantum queries inherit the classical KKT allocation, with a factor-two assisted capacity change.

See [`quantum-causal-cut-random-access.md`](quantum-causal-cut-random-access.md).

### Progressive query revelation

The first genuinely multistage causal interface now reveals a coarse query cell between two communication stages:

- for partition-cell sizes `s_j`, exact classical feasibility is characterized by
  `a >= sum_j max(0,s_j-c_j)`;
- the converse is matched by a constructive protocol that stores uncovered cell bits in the shared stage and sends the rest only in the selected branch;
- complete finite enumeration verifies every record, hint cell, and later coordinate for bounded instances;
- equal cells of residual size `s` require exactly `s` classical bits or unassisted qubits per execution when all record communication is deferred until after the hint;
- query-hint information and record-value information are separated: the hint reduces the live future-query family but carries no record values;
- bounded errors replace each exact cell size by `R_j=sum_{i in C_j}[1-H_2(e_i)]` and give the branch-aware converse
  `a >= sum_j max(0,R_j-c_j)`;
- unassisted quantum messages obey the same one-bit-per-qubit information region;
- receiver-side entanglement changes the capacity coefficient from one to two and yields exact equal-cell cost `ceil(s/2)` transmitted qubits;
- predictive-equivalence classes coarsen from `2^m` before the hint to `2^s_j` after cell `j` and then to two after the exact coordinate is known.

See [`progressive-query-revelation.md`](progressive-query-revelation.md).

## Current frontier campaigns

### Campaign A: scalable CSS, concatenated, and topological code families

The five-qubit code proves the local-blindness theorem on one exact block. The next target is a family whose physical size, logical rate, distance, and predictive interface can scale.

Candidate programs:

- CSS construction from pairs of classical binary codes;
- the Steane `[[7,1,3]]` code as the first CSS checker;
- concatenated five-qubit and Steane parameter recurrences;
- small surface/toric-code patches with explicit logical string operators;
- subsystem codes where gauge degrees of freedom alter the predictive interface;
- approximate codes and finite-temperature logical observables.

Deliverables:

1. Typed CSS parity-check inputs and commutation validation.
2. Exact logical X/Z basis extraction from quotient spaces.
3. Code distance and degeneracy checks on bounded instances.
4. Local reduced-state equality below distance.
5. Predictive packing over multiple logical qubits.
6. Parameter-level scaling theorems kept separate from bounded state-vector checks.
7. Time and memory cost of syndrome updates and logical-query answering.

### Campaign B: correlated noise and syndrome-history memory

Independent local flips are analytically clean but restrictive. The next noisy lane should include:

- common-mode and finite-range correlated errors;
- Markov noise along spatial blocks;
- repeated syndrome measurements;
- uncertain measurement-error rates;
- adversarial contamination bounded in total variation;
- erasures and delayed observations.

Research targets:

1. Determine when proper marginal blindness survives.
2. Replace `(1-2p)^ell` with correlation-function or transfer-matrix expressions.
3. Prove strong-data-processing bounds for relational information through noisy causal chains.
4. Quantify the predictive state needed to filter a hidden syndrome process.
5. Separate physical-error history, decoder belief state, and logical predictive memory.

### Campaign C: predictive min-cuts and general causal networks

One-way and two-stage partition-hint cuts are explicit. The next program should replace the hand-written stage topology by a directed capacity network.

Candidate extensions:

- arbitrary finite function families rather than coordinate queries;
- predictive-equivalence class counts attached to sink query interfaces;
- exact classical min-cut lower bounds and matching routable constructions where available;
- unassisted and entanglement-assisted quantum edge capacities;
- multiple sinks with shared upstream information and local downstream branches;
- overlapping query-hint sets and fractional-cover capacity regions;
- several successive hints represented as a query-revelation tree;
- noisy or uncertain hints and robust optimization over possible query families;
- authenticated transcript comparison under adversarial scheduling.

Research questions:

1. Is `ceil(log2 K)` the correct exact cut requirement when a sink has `K` future predictive-equivalence classes?
2. How does that requirement compose across every source-sink cut in a directed acyclic graph?
3. Which network instances admit matching routing or network-coding upper bounds?
4. How should shared upstream capacity be accounted for across several answer regions?
5. What changes for quantum edges and preshared entanglement?
6. Can a recursive tree theorem characterize arbitrary progressive query revelation?
7. How do overlapping hint sets replace the partition sum by a cover or polymatroid region?
8. Which conclusions remain ordinary communication complexity rather than simulation-specific claims?

### Campaign D: update-time and computational lower bounds

Current theorems mostly lower-bound state cardinality or communicated information. Memory alone is not enough. Future work should measure:

- update time after a new observation, syndrome, or remote record change;
- query time for a future conditional law;
- random-bit and qubit-operation complexity;
- communication across a distributed renderer;
- preprocessing versus online computation;
- tensor-network contraction or stabilizer-tableau update cost;
- cell-probe lower bounds for dynamic parity and relational queries.

The goal is a bounded time-space-communication tradeoff rather than an unsupported statement that “the universe is expensive to simulate.”

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
7. Locality claims distinguish one-shot local marginals from adaptive protocols that aggregate a higher-weight observable.
8. Code claims distinguish stabilizer weight, code distance, degeneracy, logical weight, and query weight.
9. Noise claims specify independence, stationarity, and parameter-knowledge assumptions.
10. Distributed claims specify query timing, communication rounds, query-hint support, shared stores, source distribution, and local versus global storage accounting.
11. Quantum-communication claims distinguish transmitted qubits, preshared entanglement, receiver memory, and accessible classical information.
12. Multiround claims distinguish design-wide branch capacity from the one branch executed in a particular run.
13. Physical claims state which laws apply and avoid cross-level leakage.
14. A finite experiment is never promoted into a generic simulation conclusion.
15. A memory or communication lower bound identifies the predictive interface and does not silently become a parent-hardware claim.
16. Average-case, worst-case, necessary, sufficient, exact, converse, achievable, and asymptotic statements remain explicitly separated.

## Tempera Math integration

The repository claim manifests remain the source of truth. Tempera Math can later provide content-addressed claim registration, proof graphs, exact finite certificates, and external checker receipts. The adapter must preserve:

- theorem versus model-result versus finite-check status;
- all assumptions and nonclaims;
- exact source revision and checker command;
- bounded code size, graph size, horizon, locality, tolerance, noise parameters, communication interface, hint partition, and assistance model;
- the boundary between structural validation and mathematical execution.

See [`tempera-math-bridge.md`](tempera-math-bridge.md).

## Nonclaims

This project does not claim that quantum mechanics, Bell violation, entanglement, stabilizer structure, quantum coding, random access coding, superdense coding, progressive query revelation, error correction, communication complexity, Planck scales, cosmic-ray cutoffs, entropy bounds, mathematical elegance, coincidences, observer effects, or finite signal speed are evidence of simulation by themselves. It does not assume digital physics, substrate-independent consciousness, finite parent resources, or a parent universe obeying our constants.

Rejecting one restricted implementation does not reject every possible simulator. Finding an anomaly does not favor simulation until the anomaly is more likely under a specified simulator model than under serious ordinary-physics and measurement alternatives.
