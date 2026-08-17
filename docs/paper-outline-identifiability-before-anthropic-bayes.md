# Paper outline: Identifiability Before Anthropic Bayes

## Provisional title

**Identifiability Before Anthropic Bayes: Representation Invariance, Persistent Latents, and Observable Equivalence in Simulation Arguments**

## Central thesis

Simulation-style posterior probabilities are not well-defined merely from a count of implementations or observers. Before Bayesian updating is meaningful, one must specify an observable hypothesis, a sampling hierarchy, a representation-invariant measure, and an identifiable causal observation model.

The paper should not claim to prove or refute that reality is simulated. It should prove a sequence of structural obstructions and recovery conditions.

## Proposed contribution chain

### 1. Observable equivalence theorem

If two hypotheses induce the same law on every allowed observation/intervention transcript, no internal statistic distinguishes them and the likelihood ratio is one wherever defined.

This establishes the identification-before-estimation principle.

### 2. Representation refinement theorem

Splitting one latent component into positive-weight observational clones leaves every finite shared-latent conditionally-iid view law unchanged. Raw label counting can nevertheless be driven toward zero or one by cloning only one category.

This separates physical multiplicity from representational multiplicity.

### 3. Local refinement-additivity characterization

On rational probability weights, normalization plus finite refinement additivity forces the local weight rule to equal ordinary probability weight. This is presented as a consistency characterization, not as a new measure theory theorem.

### 4. Persistent-latent sampling theorem

For one latent model drawn once and an arbitrary subsequent transcript, evidence about competing hyperprior weights is bounded by component prior-weight ratios. Repeated within-world observations are not repeated draws from a world-level prior.

This section must explicitly distinguish learning the active model from learning the population mixing weights.

### 5. One-view factorization gauge

When both prior and emission channel are free, an invertible stochastic latent transformation can change both while preserving the complete one-view observed law.

Conditional identifiability of `pi` given known `K` therefore does not imply joint identifiability of `(pi,K)`.

### 6. Recovery by causal structure

A second conditionally independent observation sharing the same persistent latent identity can collapse the declared stochastic gauge to permutations under full-row-rank and positivity assumptions. Independently redrawing the latent label instead gives only the product marginal and does not break the one-view factorization ambiguity.

This is the positive result: what matters is not merely more data, but what is held fixed across observations.

### 7. Consequences for simulation arguments

A defensible posterior about a restricted simulation hypothesis requires, at minimum:

1. a representation-invariant observer/world measure;
2. a declared reference class;
3. an explicit statement of which latent variables persist and which are resampled;
4. an identifiable mapping from latent hypotheses to observables;
5. a likelihood or e-process defined on those observables;
6. ordinary-physics alternatives in the same observation space.

Without these, a large observer count or long within-world transcript need not correspond to a large Bayes factor about the claimed world-level hypothesis.

## What is actually new enough to emphasize

The likely novelty is the **integrated identifiability framework for simulation/anthropic inference**, plus exact counterexamples showing how representation refinement, sampling hierarchy, and factorization gauges separately break naive counting/Bayesian moves.

Do not claim novelty for rational additivity, generic latent-class nonidentifiability, or branching indifference in isolation.

## Nearest literatures that must be engaged

- Bostrom's simulation argument and later patches;
- self-sampling / self-indication / full-non-indexical conditioning;
- reference-class problems and recent simulation-expectation arguments;
- Everettian branch counting and branching indifference as a close representation-refinement analogue;
- finite-mixture and latent-class identifiability;
- multiview/repeated-measurement identifiability;
- Blackwell experiments and statistical sufficiency;
- nonnegative matrix/tensor factorization identifiability.

## Submission criterion

This paper is ready only after an external philosopher of probability and an external statistician/latent-variable expert both attempt to break the central claims. The manuscript should include a table marking every mathematical statement as `known`, `new synthesis`, `new corollary`, or `new theorem`.