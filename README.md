# simulation-theory

First-principles mathematical and computational research on simulation hypotheses.

The project does **not** assume reality is simulated. It asks what can be proved, statistically identified, empirically tested, or ruled out after the hidden assumptions in simulation arguments are made explicit.

## Core rule

A generic simulator that is allowed to reproduce exactly the same observable probability law as ordinary physics is not statistically distinguishable from that base model. Scientific work therefore requires a **restricted simulator model** with explicit observable consequences.

## Current research lanes

- observational indistinguishability and Bayes-factor limits;
- total-variation limits on statistical tests and classifiers;
- observer-measure factorization and Jensen plug-in bias;
- continuation/selection reweighting;
- resource-constrained nesting;
- separation of internal physical quantities from parent-substrate resources;
- exact lazy-generation equivalence under conditional sampling;
- predictive-state lower bounds;
- observer-conditioning sensitivity;
- representation multiplicity in algorithmic priors.

See [`docs/formal-results.md`](docs/formal-results.md), [`docs/research-program.md`](docs/research-program.md), and [`docs/sources.md`](docs/sources.md).

## Run

```bash
python -m pip install pytest
python -m pytest
PYTHONPATH=src python -m simtheory.experiments
```

GitHub Actions runs tests on pushes and pull requests. The mathematical package itself uses only the Python standard library.

## Evidence boundary

Evidence must favor a **restricted** simulator model over a serious base model. A specified lattice, precision model, random source, intervention process, or resource constraint may be scientific if it produces falsifiable signatures. Quantization, randomness, information bounds, mathematical laws, observer effects, or finite signal speed are not generic evidence by themselves.

## Tempera Math

`tempera-math` can be used as an external proof/evidence harness for exact certificates and bounded checks. This repository remains the canonical research home, and no script result is promoted into a theorem without explicit assumptions and claim scope.
