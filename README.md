# simulation-theory

A first-principles mathematical and computational investigation of simulation hypotheses.

This repository does **not** assume that reality is simulated. It asks a narrower and more scientific question: **what can actually be inferred, proved, tested, or ruled out once the hidden assumptions in simulation arguments are made explicit?**

## Research stance

The generic claim "some external process generates our observations" is too broad to test if that process is allowed to reproduce the same observable probability law as ordinary physics. The scientific object is therefore a **restricted simulator model** with explicit assumptions about observer selection, computation, architecture, interventions, discretization, randomness, or resource limits.

We separate four scopes throughout the repo:

- **Theorem** — follows from stated mathematical assumptions.
- **Model result** — exact within a specified model, not a claim about reality.
- **Empirical hypothesis** — could in principle be tested against data.
- **Open problem** — not established; included as a research target.

## Main results currently encoded

1. **Unrestricted indistinguishability.** If a simulator class contains a member inducing exactly the same observable law as the base model, no statistical test can uniformly distinguish that member; its Bayes factor against base reality is exactly one.
2. **Evidence ceiling.** A bounded likelihood ratio gives an exact bound on how far any observation can move posterior log-odds.
3. **Total-variation ceiling.** For simple equal-prior hypotheses, optimal classification accuracy is `(1 + TV(P,Q))/2`; no classifier can extract discrimination absent from the observable distribution.
4. **Observer-measure factorization.** The familiar population-count argument becomes a probability only after a measure over relevant observers/observer-moments is chosen.
5. **Jensen expectation trap.** For uncertain simulated measure `X`, `E[X/(1+X)] <= E[X]/(1+E[X])`; plugging an expected count into the ratio overstates the properly averaged fraction.
6. **Selection-policy confounding.** Continuation, pruning, reset, or sampling policies reweight the distribution actually seen by observers.
7. **Resource-bounded nesting.** Recursive simulations do not imply infinite simulated observer measure when cross-level relevant budget contracts geometrically.
8. **Exact lazy-rendering equivalence.** An online renderer that samples the exact target conditional distribution at every adaptive query produces the same transcript law as pre-sampling the full hidden world. "Lazy rendering" is therefore not itself detectable; the meaningful question is the complexity of maintaining/sampling the required predictive state.
9. **Predictive-state lower bound.** Any exact online renderer must distinguish histories that induce different future conditional laws. Thus the number of renderer states is at least the number of predictive-equivalence classes; memory is at least the log2 of that number.
10. **Implementation-multiplicity warning.** Counting programs rather than observational laws can create artificial prior mass. Algorithmic priors need an explicit representation convention or quotient by observational equivalence.

See [`docs/formal-results.md`](docs/formal-results.md) for statements and proofs.

## Layout

```text
src/simtheory/
  inference.py          Bayesian/frequentist information bounds
  observer_measure.py   anthropic measure and selection models
  lazy_rendering.py     adaptive-query equivalence and state lower bounds
  algorithmic.py        representation / program-multiplicity experiments
  experiments.py        deterministic research sweeps

tests/test_core.py      invariant tests
docs/formal-results.md  proof trail
docs/research-program.md research roadmap and nonclaims
```

## Run

```bash
python -m pytest
python -m simtheory.experiments
```

The code deliberately uses only the Python standard library so the mathematical core is easy to audit.

## What would count as evidence?

Evidence must favor a **restricted** simulator model over a serious base model. Examples include a specified lattice or precision architecture that predicts previously unobserved violations, a constrained random-number mechanism with detectable structure, or a resource model that forces characteristic approximation artifacts. Merely observing quantization, randomness, information bounds, mathematical laws, or finite signal speed is not generic evidence for simulation because ordinary physical theories can contain those features too.

## Tempera Math

`tempera-math` may be used as an external proof/evidence harness for exact certificates or bounded checks, but this repository remains the canonical research home. No result is promoted merely because a script ran; claim scope and assumptions stay explicit.
