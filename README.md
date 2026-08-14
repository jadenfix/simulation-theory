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

The machine-readable claim ledger is [`claims/claims-v1.json`](claims/claims-v1.json). Its purpose is to stop finite experiments, philosophical premises, and restricted tests from silently becoming generic claims.

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

Detailed statements and proofs are in [`docs/formal-results.md`](docs/formal-results.md).

## Layout

```text
claims/claims-v1.json       typed claims, assumptions, evidence, and nonclaims
docs/formal-results.md      theorem statements and proofs
docs/research-program.md    completed lanes, next campaigns, and quality gates
docs/sources.md             primary research context
docs/tempera-math-bridge.md optional external proof-harness boundary
src/simtheory/              mathematical models and deterministic experiments
tests/                      exact, unit, and randomized property checks
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

Quantization, randomness, mathematical laws, finite signal speed, observer effects, or information bounds are not generic evidence for simulation; ordinary physical theories can contain those features too.

## Tempera Math boundary

`tempera-math` may be used as an external certificate and proof-receipt harness. This repository remains the canonical research home. A script run, CI pass, manifest hash, or structural validation never promotes a bounded result into an unbounded theorem. See [`docs/tempera-math-bridge.md`](docs/tempera-math-bridge.md).
