# simulation-theory

A first-principles mathematical and computational investigation of simulation hypotheses.

This repository does **not** assume that reality is simulated. It asks a narrower scientific question:

> What can be inferred, proved, tested, or ruled out after every observer-selection, statistical, computational, causal, and physical assumption is made explicit?

The generic claim that “some external process generates our observations” is too broad to test when that process is allowed to reproduce the same observable probability law as ordinary physics. The scientifically meaningful object is therefore a **restricted simulator model** with a specified observable law, architecture, approximation mechanism, intervention policy, or physical resource model.

## Research discipline

Every claim is kept in one of four scopes:

- **Theorem** — follows from stated mathematical assumptions.
- **Model result** — exact inside a specified model, not a statement about reality.
- **Finite check** — reproducible computation over a bounded domain.
- **Open problem** — a research target, not an established conclusion.

The core machine-readable ledger is [`claims/claims-v1.json`](claims/claims-v1.json). Multidimensional quantum, relational, noisy, code-locality, distributed, and quantum-communication extensions are registered in [`claims/quantum-phase-claims.json`](claims/quantum-phase-claims.json), [`claims/stabilizer-relational-claims.json`](claims/stabilizer-relational-claims.json), [`claims/noisy-relational-claims.json`](claims/noisy-relational-claims.json), [`claims/stabilizer-code-claims.json`](claims/stabilizer-code-claims.json), [`claims/distributed-consistency-claims.json`](claims/distributed-consistency-claims.json), and [`claims/quantum-causal-cut-claims.json`](claims/quantum-causal-cut-claims.json). Their purpose is to stop finite experiments, philosophical premises, and restricted tests from silently becoming generic claims.

## Main results encoded

1. **Unrestricted indistinguishability.** If the simulator class contains a member with the same observable law as the base model, no test can distinguish that member better than its false-positive rate; its Bayes factor against base reality is one.
2. **Evidence ceiling.** A bounded observable likelihood ratio gives a matching bound on posterior log-odds movement.
3. **Total-variation ceiling.** Equal-prior optimal classification accuracy is `(1 + TV(P,Q))/2`.
4. **Fano and Le Cam bounds.** Multi-architecture identification and parameter estimation have explicit minimax lower bounds when candidate laws overlap.
5. **Hierarchical Bayesian model averaging.** Technical feasibility, data likelihood, and scenario-conditional observer measure remain separate.
6. **Observer-measure factorization.** Population counts become probabilities only after a measure over observers or observer-moments is chosen.
7. **Jensen expectation trap.** Inserting an expected simulated count into the familiar ratio overstates the properly averaged result under uncertainty.
8. **SSA/SIA/FNC-style divergence.** Explicit finite conditioning rules can produce sharply different posteriors from the same worlds.
9. **Exact lazy-rendering equivalence.** Exact target-conditionals reproduce the same transcript law as pre-sampling the hidden world.
10. **Adaptive approximate-rendering bound.** Per-step total-variation errors compose into a transcript error bound even under adaptive queries.
11. **Conditional-KL bound.** The KL chain rule and Pinsker yield a transcript-level bound from conditional KL errors.
12. **Predictive-state lower bounds.** Exact and approximate renderers require enough states to separate distinct future observable laws.
13. **Selection-policy confounding.** Outcome-dependent retention shifts binary log-odds by an exact amount.
14. **Latent-intervention ambiguity.** Observed rate shifts can be decomposed into ordinary and unconstrained intervention laws.
15. **Anytime-valid restricted tests.** Bernoulli likelihood-ratio e-processes support optional-stopping-safe tests for specified signatures.
16. **Local physical envelopes.** Landauer, Margolus–Levitin, Bekenstein, mass-energy, and Schwarzschild expressions are implemented for local physics.
17. **Parent-resource non-transfer.** Internal physical quantities do not constrain an unknown parent substrate without an implementation map.
18. **Program multiplicity.** Many programs can implement one observable law, so raw algorithmic mass depends on coding and implementation choices.
19. **Bell predictive-law geometry.** For a finite Werner/singlet Bell schedule, total variation between visibility states has an exact closed form derived from the physical measurement family.
20. **Physically derived renderer-memory bound.** A finite visibility grid induces an explicit Bell-law packing number and therefore a lower bound on the number of renderer states and internal memory bits required for epsilon-accurate prediction.
21. **Adaptive Bell-query lower bound.** KL chain rules plus Pinsker give a necessary number of allowed Bell measurements before two visibility states can reach a target transcript distinguishability, even with adaptive setting choice.
22. **Visibility-phase predictive geometry.** A two-parameter Bell family gives an exact predictive-law metric over physical states `(visibility, phase)` and a full 2x2 Fisher geometry.
23. **Canonical CHSH disk norm.** In correlation-disk coordinates `q=(v cos(phi), v sin(phi))`, canonical CHSH predictive TV is exactly `||q-q'||_infinity/(2*sqrt(2))`.
24. **Quadratic physical packing.** The canonical visibility-phase family contains an explicit epsilon-packing of size at least `ceil(1/(4 epsilon))^2`, producing a memory lower bound that scales as `2 log2(1/epsilon)` up to constants.
25. **Fisher-rank identifiability.** One Bell setting has rank at most one for the two-parameter state, while a sufficiently rich schedule can locally identify both dimensions; phase becomes unidentifiable at zero visibility.
26. **Adaptive phase-drift transcripts.** Exact finite transcript laws are computed under history-dependent Bell queries, and transcript TV is monotone under retained-history refinement.
27. **Exact n-qubit basis scaling.** Coordinate-Z queries separate all `2^n` computational-basis states, forcing `n` internal predictive bits without inferring anything from Hilbert-space dimension alone.
28. **Many-body L1 geometry.** A `d`-qubit product-polarization family has exact randomized-query distance `||q-u||_1/(2d)`.
29. **Dimension-resolution factorization.** Explicit q-ary product packings yield memory scaling `ceil(d log2 L)`, separating subsystem count from accessible precision.
30. **Graph-basis weighted-Hamming geometry.** Stabilizer-generator queries on `|G,z>` give exact predictive TV equal to weighted Hamming distance between graph-basis labels.
31. **Two-local blindness with three-local access.** For cycle graph states `C_n`, `n>=5`, every one- and two-qubit reduction is maximally mixed for all `2^n` labels, while weight-three stabilizer queries reveal the label coordinates.
32. **Constant-tolerance relational coding.** Finite Gilbert bounds and the rate `1-H_2(2 epsilon)` preserve a linear number of predictive bits under constant uniform-query tolerance below one quarter.
33. **Cat-state proper-marginal blindness.** Every incomplete local-X transcript of a phase-labeled cat block is uniform and phase-independent, while the complete parity transcript separates the phases perfectly.
34. **Exact streaming consistency memory.** After `ell-1` local outcomes in each of `m` cat blocks, an exact online renderer has exactly `2^m` predictive-equivalence classes and needs exactly `m` parity bits; the lower bound survives worst-query error below one half.
35. **Noise-renormalized parity law.** Independent local flip probability `p` on an `ell`-qubit cat block produces effective parity crossover `q=[1-(1-2p)^ell]/2` and exact phase TV `(1-2p)^ell`.
36. **Noisy proper-marginal blindness.** Even after independent local flips, every proper local-X marginal remains exactly uniform and phase-independent.
37. **Locality-robustness tradeoff.** Relational locality increases with block length while observable parity visibility decays exponentially as `(1-2p)^ell` under fixed independent local noise.
38. **Sharp noisy checkpoint threshold.** With parity visibility `c`, worst-query predictive memory is exactly `m` bits for error below `c/2` and collapses to zero at or above `c/2` in the declared one-step model.
39. **Exact predictive rate distortion.** For a uniform `m`-bit noisy checkpoint signature and average TV distortion `D`, internal predictive information is at least `m[1-H_2(D/c)]` for `D<c/2`.
40. **Noisy codeword recovery.** Exact binomial TV, KL/Pinsker necessary counts, and Bhattacharyya sufficient counts quantify repeated parity recovery and complete noisy-codeword separation.
41. **Binary-symplectic code distance.** Exact GF(2) stabilizer and normalizer enumeration computes `d=min wt(N(S)\S)` and the `4^k` logical Pauli quotient without dense Hilbert-space counting.
42. **Complete sub-distance local blindness.** Every encoded state in an `[[n,k,d]]` stabilizer code has the same reduced density matrix on every subset of fewer than `d` physical qubits.
43. **Quantum Singleton constraint.** Two correctable erasures imply `n-k>=2(d-1)`; the five-qubit perfect code saturates the bound.
44. **Five-qubit exact certificate.** Independent symplectic and state-vector checks verify the declared code is `[[5,1,3]]`, with all one- and two-qubit reductions identical across logical basis and superposition states.
45. **Encoded logical predictive memory.** `m` blocks encoding `k` logical bits each require `mk` internal bits under worst logical-coordinate queries below error `1/2`, even though every sub-distance physical measurement is blind.
46. **Error-set versus quantum-distance distinction.** The three-qubit bit-flip repetition code detects one-qubit X errors but has full quantum distance one because a weight-one logical Z exists.
47. **Exact post-query causal-cut bound.** An `m`-bit record sent before an unresolved future coordinate query requires `2^m` exact message states, because every encoder collision fails on some query.
48. **Bounded-error causal-cut information.** Uniform records and uniform post-message queries require at least `m[1-H_2(epsilon)]` bits of record information at average error `epsilon`.
49. **Weighted-query forgetting law.** The least-informative coordinate errors satisfy `e_i=1/(1+2^(lambda w_i))`; frequently queried bits are protected more strongly and zero-weight bits can be forgotten.
50. **Memory-communication cut tradeoff.** Record-dependent resident state plus later pre-query communication must jointly meet the same exact or bounded-error INDEX lower bound.
51. **Indexed parity reconciliation.** Answering `A_i xor B_i` with `B_i` locally known is exactly as hard, for the remote contribution, as answering `A_i`.
52. **Isolated-region replication.** If `r` regions must answer locally with no later communication or shared record store, the sum of separate local storage lower bounds scales by `r`.
53. **Explicit upper/lower gap.** Storing an exact prefix of `s` bits and guessing the rest has verified average error `(m-s)/(2m)`, providing a concrete upper construction without pretending it meets the Fano lower bound.
54. **Unassisted quantum random-access cut.** Encoding an unresolved `m`-bit future-query record into `q` qubits requires `q>=m[1-H_2(epsilon)]` under uniform average error; exact recovery requires `m` qubits.
55. **Entanglement-assisted factor-two limit.** Preshared entanglement independent of the record permits a `q`-qubit transmission to increase receiver information by at most `2q`, yielding `q>=m[1-H_2(epsilon)]/2`.
56. **Exact dense-coding achievability.** With one preshared Bell pair per transmitted qubit, an exact `m`-bit record requires and can be sent using `ceil(m/2)` qubits.
57. **Quantum query-timing phase change.** If the coordinate query is known before encoding, one qubit suffices exactly; if it remains unresolved, exact communication is linear in `m`.
58. **Inverse-entropy quantum converse.** A fixed qubit budget implies a minimum average error through `H_2^{-1}(1-q/m)` unassisted or `H_2^{-1}(1-2q/m)` with entanglement assistance.
59. **Canonical one-qubit random-access codes.** Explicit square and cube Bloch encodings achieve success `(1+1/sqrt(2))/2` for two bits and `(1+1/sqrt(3))/2` for three bits; complete finite enumeration verifies every record-query law.
60. **Weighted quantum future queries.** Nonuniform query distributions inherit the KKT error allocation `e_i=1/(1+2^(lambda w_i))`, while the quantum capacity side changes by the unassisted versus assisted factor of two.

General proofs are in [`docs/formal-results.md`](docs/formal-results.md). Physical, relational, code, and distributed derivations are developed in:

- [`docs/bell-predictive-bounds.md`](docs/bell-predictive-bounds.md)
- [`docs/quantum-phase-predictive-bounds.md`](docs/quantum-phase-predictive-bounds.md)
- [`docs/canonical-chsh-disk-geometry.md`](docs/canonical-chsh-disk-geometry.md)
- [`docs/quantum-sequential-bounds.md`](docs/quantum-sequential-bounds.md)
- [`docs/manybody-predictive-bounds.md`](docs/manybody-predictive-bounds.md)
- [`docs/stabilizer-relational-consistency.md`](docs/stabilizer-relational-consistency.md)
- [`docs/noisy-relational-rate-distortion.md`](docs/noisy-relational-rate-distortion.md)
- [`docs/stabilizer-code-locality.md`](docs/stabilizer-code-locality.md)
- [`docs/distributed-causal-consistency.md`](docs/distributed-causal-consistency.md)
- [`docs/quantum-causal-cut-random-access.md`](docs/quantum-causal-cut-random-access.md)

## Layout

```text
claims/claims-v1.json                    core typed claims, assumptions, evidence, and nonclaims
claims/quantum-phase-claims.json         multidimensional quantum claim registry
claims/stabilizer-relational-claims.json relational and online-consistency claim registry
claims/noisy-relational-claims.json      noisy parity and rate-distortion claim registry
claims/stabilizer-code-claims.json       code-distance and logical-locality claim registry
claims/distributed-consistency-claims.json causal-cut and communication claim registry
claims/quantum-causal-cut-claims.json    quantum random-access and assistance claim registry
docs/formal-results.md                   general theorem statements and proofs
docs/bell-predictive-bounds.md           one-parameter physical Bell derivations
docs/quantum-phase-predictive-bounds.md  two-parameter geometry and Fisher analysis
docs/canonical-chsh-disk-geometry.md     exact disk norm and constructive scaling bound
docs/quantum-sequential-bounds.md        adaptive phase-drift transcript model
docs/manybody-predictive-bounds.md       subsystem-count and precision scaling
docs/stabilizer-relational-consistency.md local blindness and streaming parity memory
docs/noisy-relational-rate-distortion.md noise attenuation, repetition, and predictive coding
docs/stabilizer-code-locality.md         code distance, erasures, and logical observables
docs/distributed-causal-consistency.md   query timing, cut-set bounds, and reconciliation
docs/quantum-causal-cut-random-access.md quantum messages, entanglement assistance, and QRACs
docs/research-program.md                 completed lanes, next campaigns, and quality gates
docs/sources.md                          primary research context
docs/tempera-math-bridge.md              optional external proof-harness boundary
src/simtheory/                           mathematical models and deterministic experiments
tests/                                   exact, unit, and randomized property checks
```

## Run

```bash
python -m pip install -e . pytest
python -m pytest
python -m simtheory.experiments
```

The mathematical core uses only the Python standard library. GitHub Actions runs editable installation, bytecode compilation, all tests, and the experiment smoke suite on Python 3.11, 3.12, and 3.13.

## What would count as evidence?

Evidence must favor a **restricted** simulator model over serious alternative physical models. Examples include a specified lattice, finite-precision mechanism, constrained random source, or resource model that predicts a previously unobserved signature.

Quantization, randomness, mathematical laws, finite signal speed, observer effects, Bell violation, entanglement, stabilizer structure, quantum coding, random-access coding, superdense coding, error correction, communication complexity, or information bounds are not generic evidence for simulation; ordinary physical theories and ordinary distributed systems can contain those features too.

## Tempera Math boundary

`tempera-math` may be used as an external certificate and proof-receipt harness. This repository remains the canonical research home. A script run, CI pass, manifest hash, or structural validation never promotes a bounded result into an unbounded theorem. See [`docs/tempera-math-bridge.md`](docs/tempera-math-bridge.md).
