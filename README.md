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

### Statistical identifiability

1. **Unrestricted indistinguishability.** If the simulator class contains a member with the same observable law as the base model, no test can distinguish that member better than its false-positive rate; its Bayes factor against base reality is one.
2. **Evidence ceiling.** If the observable likelihood ratio stays in `[exp(-epsilon), exp(epsilon)]`, posterior log-odds can move by at most `epsilon`.
3. **Total-variation ceiling.** Equal-prior optimal classification accuracy is `(1 + TV(P,Q))/2`. Better algorithms cannot recover information absent from the observation law.
4. **Fano and Le Cam bounds.** Multi-architecture identification and parameter estimation have explicit minimax lower bounds when candidate observable laws overlap.
5. **Hierarchical Bayesian model averaging.** Technical feasibility, data likelihood, and scenario-conditional observer measure remain separate; posterior simulation probability is an average of conditional ratios, not a ratio built from expected counts.

### Observer measure and anthropic conditioning

6. **Observer-measure factorization.** A population count becomes a probability only after a measure over observers or observer-moments is chosen.
7. **Jensen expectation trap.** For uncertain simulated measure `X`, `E[X/(B+X)] <= E[X]/(B+E[X])`; plugging an expected count into the familiar ratio overstates the properly averaged result.
8. **SSA/SIA/FNC-style divergence.** Finite weighting rules can produce sharply different posteriors from the same worlds. Duplicating a world leaves its SSA-style within-world fraction unchanged, scales its SIA-style weight linearly, and makes a Poisson full-evidence-presence weight saturate toward one.

### Lazy rendering and predictive complexity

9. **Exact lazy-rendering equivalence.** Sampling every next answer from the exact target conditional law produces the same transcript distribution as pre-sampling the full hidden world.
10. **Adaptive approximate-rendering bound.** If step-`t` conditional total-variation error is at most `epsilon_t`, transcript error is at most `1 - product_t(1-epsilon_t)`, even under adaptive querying.
11. **Conditional-KL bound.** The KL chain rule plus Pinsker bounds transcript total variation by `sqrt(sum_t kappa_t / 2)` when expected conditional KL terms are bounded by `kappa_t`.
12. **Predictive-state lower bounds.** Exact renderers need at least one state per distinct future law. An `epsilon`-accurate renderer needs at least the maximum number of future laws separated pairwise by more than `2 epsilon` in total variation.

### Causal selection and sequential testing

13. **Selection-policy confounding.** Outcome-dependent retention shifts binary log-odds by exactly `log(r1/r0)`. A bounded retention odds ratio gives sharp raw-probability sensitivity intervals.
14. **Latent-intervention ambiguity.** An observed anomaly-rate shift can be represented as a mixture of an ordinary law and an unconstrained intervention law; the code computes the minimum intervention mass required.
15. **Anytime-valid restricted tests.** Fixed-alternative and mixture Bernoulli likelihood ratios form e-processes under their declared sampling assumptions, permitting optional-stopping-safe tests for a *specific binary signature*.

### Physics and representation

16. **Local physical envelopes.** Landauer, Margolus–Levitin, Bekenstein, mass-energy, and Schwarzschild expressions are implemented in SI units for devices obeying the relevant local physics.
17. **Parent-resource non-transfer.** Internal mass, energy, or information does not constrain an unknown parent substrate without an explicit implementation or law-transfer coefficient.
18. **Program multiplicity.** Many programs can implement one observable law. Raw algorithmic mass depends on the coding language and implementation multiplicity; the repo exposes that sensitivity rather than treating syntax as independent worlds.

Detailed statements and proofs are in [`docs/formal-results.md`](docs/formal-results.md).

## Layout

```text
claims/
  claims-v1.json        typed claim scopes, assumptions, evidence, and nonclaims

docs/
  formal-results.md     theorem statements and proofs
  research-program.md   completed work, next campaigns, and quality gates
  sources.md            primary research context
  tempera-math-bridge.md optional external proof-harness boundary

src/simtheory/
  inference.py          Bayesian and total-variation evidence bounds
  bayesian.py           hierarchical feasibility/model averaging
  minimax.py            KL, Fano, and Le Cam lower bounds
  anthropic.py          finite SSA/SIA/FNC-style conditioning models
  observer_measure.py   observer measure, selection, and recursive budgets
  lazy_rendering.py     adaptive transcript and predictive-state bounds
  causal.py             retention and latent-intervention sensitivity
  sequential.py         Bernoulli e-processes and exact finite calibration
  physics.py            explicitly local physical-computation envelopes
  algorithmic.py        program-multiplicity and Kraft diagnostics
  claims.py             deterministic claim-manifest validation
  experiments.py        deterministic research demonstrations

tests/                  unit, exact-enumeration, and randomized property checks
```

## Run

```bash
python -m pip install -e . pytest
python -m pytest
python -m simtheory.experiments
```

The mathematical core uses only the Python standard library. GitHub Actions runs the test suite across Python 3.11, 3.12, and 3.13.

## What would count as evidence?

Evidence must favor a **restricted** simulator model over serious alternative physical models. Examples include a specified lattice, finite-precision mechanism, constrained random source, or resource model that predicts a previously unobserved signature. Merely observing quantization, randomness, mathematical laws, finite signal speed, observer effects, or information bounds is not generic evidence for simulation: ordinary physical theories can contain those features too.

## Tempera Math boundary

`tempera-math` may be used as an external certificate and proof-receipt harness. This repository remains the canonical research home. A script run, CI pass, or structural manifest validation never promotes a bounded result into an unbounded theorem. See [`docs/tempera-math-bridge.md`](docs/tempera-math-bridge.md).
