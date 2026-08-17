# Mathematical audit and publication-readiness review

Date: 2026-08-17

## Purpose

This document is an adversarial audit of the mathematical research program. It is deliberately stricter than CI. Passing tests establishes that implementations and bounded receipts agree with their declared checks; it does not establish novelty, physical applicability, or the truth of a theorem whose proof has a hidden assumption.

The audit separates five questions:

1. **Algebraic correctness:** does the displayed result follow from the stated assumptions?
2. **Operational correctness:** does the solver implement the same timing, uncertainty, and benchmark semantics as the theorem?
3. **Boundary correctness:** are finite checks, asymptotic claims, physical interpretations, and statistical confidence kept distinct?
4. **Adversarial robustness:** do degenerate, zero-mass, nonidentifiable, off-model, and moving-benchmark cases fail closed?
5. **Novelty:** is the result actually new, or a correct specialization/repackaging of known mathematics?

## Executive audit status

### High-confidence mathematical core

The following families were re-derived from first principles and no mathematical contradiction was found in their declared scopes:

- observational nonidentifiability when two hypotheses induce the same law;
- TV/classification identities and standard Le Cam/Fano-style finite decision bounds;
- predictive-equivalence quotienting and finite packing/cover logic;
- Dobrushin TV contraction and serial contraction;
- finite confusion-graph zero-error coding;
- prior-weighted prefix coding by independent-set partitions plus Huffman coding;
- finite-prior and TV-ball robust one-shot coding, conditional on the declared finite code universe;
- coupled TV-drift LPs and the distinction between marginal robustification and path-consistent robustification;
- information-pattern ordering when policy classes are literally nested;
- Bayesian hidden-state filtering when transition/observation laws are action-independent as declared;
- fixed-model versus rectangular ambiguity as distinct uncertainty semantics;
- active experiment value after explicitly matching public-randomization resources;
- model-informed minimax regret when the oracle timing and experiment costs are held fixed;
- Bayesian Boolean minority-mass, conditional-bias, influence, Fourier, and adaptive-query identities;
- fixed-sample prior sensitivity/calibration results under the explicitly declared iid latent-unit sampling model;
- persistent-latent likelihood-ratio ceilings;
- finite-mixture affine identifiability conditional on a known emission channel;
- latent refinement invariance for duplicated identical components.

This status means "no false theorem found under the written assumptions," not "peer reviewed" and not "novel."

## Corrections and publication blockers found by the audit

### A1. Novelty must not be inferred from exact certificates

Several correct results sit directly inside established literatures. Exact rational code and proof receipts are valuable reproducibility machinery, but do not by themselves create theorem novelty.

Examples:

- robust/minimax Huffman coding has a substantial prior literature;
- Dobrushin/ergodicity coefficients already formalize TV contraction of stochastic matrices;
- nonrectangular versus rectangular dynamic ambiguity is classical in multiple-priors decision theory and robust MDPs;
- Boolean influence/Fourier identities are standard analysis-of-Boolean-functions objects;
- branch/refinement indifference has close analogues in Everettian probability and anthropic measure debates.

Any paper must distinguish **new theorem**, **new exact algorithm/certificate**, **new synthesis**, and **new application**.

### A2. The finite-mixture global TV modulus is closely related to known facial-distance geometry

For affinely independent channel rows, their convex hull is a simplex. The quantity

\[
\alpha(K)=\inf_{\delta\ne0,\,\mathbf 1^T\delta=0}
\frac{TV(\delta K)}{TV(\delta)}
\]

can be written as the minimum TV distance between convex hulls of disjoint row subsets. Because adding unused vertices to one side can only decrease set distance, this is a norm-specific facial-distance/minimum-gain quantity for the row simplex. Facial distance/pyramidal width is established in convex-optimization literature.

Therefore the disjoint-face characterization should not currently be advertised as a novel general convex-geometric theorem. The potentially publishable contribution is narrower: exact rational computation in TV norm, mixture-channel conditioning interpretation, row-uncertainty certificates, and statistically composable inverse bounds.

### A3. Two-view rigidity is a gauge-orbit theorem, not unrestricted latent-class identifiability

The two-view result starts from a specific one-view gauge

\[
K'=AK,\qquad \pi'=\pi A^{-1}
\]

with invertible nonnegative row-stochastic `A`. Under full row rank, positive `pi'`, and equality of the shared-latent second-view law, the derivation forcing `A` to be a permutation is sound.

But this proves rigidity **inside that declared stochastic gauge orbit**. It does not, by itself, prove that every alternative two-view factorization of the same joint law must be related by such an `A`. General latent-class/multiview identifiability is a larger literature with additional rank/Kruskal/tensor conditions.

Publication wording must say "the continuous row-stochastic gauge collapses to label switching" rather than "two views globally identify every finite latent model."

### A4. Refinement-additive measure uniqueness is correct but elementary

If a local rational weight rule satisfies normalization and finite split additivity, then `mu(p/q)=p/q`. This is a direct rational additivity argument. Likewise, equal cloning changes escort score `w^gamma` by `r^(1-gamma)`.

These are correct, but theorem novelty is low. Their value is conceptual: they expose a representation-invariance requirement for observer-counting arguments. A philosophy/foundations paper must engage existing work on reference classes, branching indifference, self-locating credence, and branch counting rather than presenting rational additivity itself as a new mathematical discovery.

### A5. Persistent-latent repetition versus repeated latent draws is correct and important, but causal semantics must stay explicit

For one latent draw `M` followed by an arbitrarily long conditional transcript,

\[
\frac{P_a(y)}{P_b(y)}
=\sum_m P_b(M=m\mid y)\frac{a_m}{b_m},
\]

when the denominator weights needed by the ratio are positive. Hence the Bayes factor is bounded by component prior-weight ratios. This is mathematically sound.

The result fails to give a finite ceiling when the denominator assigns zero weight to a component that the numerator allows; the theorem/implementation must keep absolute-continuity assumptions explicit. More importantly, the result concerns inference about **mixing weights/hyperpriors** after one persistent latent draw. It does not say long within-world transcripts cannot identify which latent model is active.

### A6. Confidence statements are deliberately conservative and must not be sold as optimal

The second-moment/Markov TV radii are valid under their iid assumptions but loose. They are useful because they are exact-rational and fail closed. A paper should compare them against sharper multinomial concentration, exact multinomial confidence regions, method-of-types bounds, or time-uniform confidence sequences. "Certified" must not be conflated with "statistically efficient."

### A7. Open stacked PRs are not part of the verified mainline

Research PRs built on unmerged parents can have mathematically correct content while still lacking independent integration verification. Publication claims should cite a commit on `main` or a frozen paper branch, not a moving stacked PR. The earlier branch-history pollution incidents justify this rule.

### A8. A claim-ledger anchor failure is evidence that metadata is part of the proof surface

The Bayesian Boolean branch correctly failed CI because `Möbius` generated a Unicode-aware Markdown anchor different from the ASCII claim reference. This was not a theorem failure, but it demonstrates that evidence binding must itself be audited. Claim IDs, anchors, source revisions, and theorem scopes should be frozen for any paper artifact.

## Adversarial theorem checks

### Identical observable laws

If `P=Q`, every measurable transcript statistic has the same distribution. Bayes factor one follows wherever both likelihoods are positive and equal. No internal test can identify an implementation-level distinction absent from the observable law. Correct.

### Jensen observer-count warning

For fixed `B>0`, `f(x)=x/(B+x)` is concave on `x>=0`, so

\[
E[f(X)]\le f(E[X]).
\]

Correct. It is a sensitivity warning, not an anthropic-measure theorem.

### TV contraction

For a Markov kernel `K`,

\[
TV(\mu K,\nu K)\le \delta(K)TV(\mu,\nu)
\]

with Dobrushin coefficient `delta(K)=max_{i,j}TV(K_i,K_j)`. Correct and classical.

### Noisy cat parity

Independent sign flips multiply the parity expectation, giving `(1-2p)^ell`; proper marginals cancel the parity Fourier term. The BSC reduction and repeated-product formulas are correct under independent readout flips.

### Rate-distortion bound

The reduction to binary Hamming distortion is correct for the declared two-point target biases. The lower bound

\[
I(Z;M)\ge m[1-H_2(D/c)]
\]

requires `0<=D<c/2`; the documentation already states the zero lower bound beyond that regime. Correct within scope.

### Robust TV coding

The fixed-vector worst-case expectation over a TV ball is a mass-transport problem. Piecewise linearity and concavity in radius for the maximized value follow from decreasing marginal transport gains. The outer finite code optimization remains exact only because the code universe is explicitly bounded/enumerated. Correct within scope.

### Fixed-model versus rectangular ambiguity

`exists M for all t` and `for all t exists M_t` are different uncertainty sets. Rectangular reselection is a relaxation and can be strictly more conservative. Correct; not novel in general robust-control theory.

### Boolean Bayesian geometry

For cell masses `m0,m1`, Bayes error is `min(m0,m1)`. Under uniform prior and `g=(-1)^f`, this gives

\[
V(S)=\frac12(1-E|E[g\mid X_S]|).
\]

Leave-one-out cells are cube edges, giving `V([k]\\{i})=Inf_i(f)/2`. Fourier projection and the `B^2<=W<=B` sandwich follow from Jensen and `z^2<=|z|` on `[-1,1]`. Correct.

### Finite-mixture affine identifiability

For known `K`, priors are identifiable iff row differences relative to one reference have rank `m-1`. Rank failure gives a zero-sum latent direction and hence two nearby interior priors with the same observed law. Correct.

### Row-uncertainty modulus

If each row moves by at most TV radius `r_i`, a normalized zero-sum latent direction has positive and negative masses one, so perturbation of its observed signed law is bounded by the weighted positive-side plus negative-side row radii and hence by `2 max_i r_i`. The global `2 epsilon` bound is correct; face-specific penalties can sharpen it.

### One-view gauge

If `A` is invertible row-stochastic, `K'=AK` is stochastic and `pi'=pi A^{-1}` gives `pi'K'=pi K` whenever `pi'` is a valid prior. Correct. The existence of such gauges proves joint nonidentifiability; it does not classify all possible nonidentifiabilities.

### Shared-latent two-view gauge rigidity

Under the declared gauge, full row rank and strictly positive transformed prior, equality of `K^T D_pi K` and `K'^T D_pi' K'` forces `A^T D_pi' A=D_pi`. Nonnegative off-diagonal sums then force each row of `A` to have one positive entry; invertibility makes `A` a permutation. Correct within the gauge class.

### Refinement invariance

Replacing one component `(w,K)` by clones `(w_j,K)` with `sum_j w_j=w` leaves every finite conditionally-iid shared-latent view law unchanged by linearity. Correct. Uniform label counting is therefore representation-sensitive.

## Publication-readiness matrix

### Candidate P1 — strongest conceptual paper

**Working title:** *Identifiability Before Anthropic Bayes: Representation Invariance, Persistent Latents, and Observable Equivalence in Simulation Arguments*

Potential contribution:

1. formalize the distinction between observational hypotheses and implementation labels;
2. prove representation/refinement invariance requirements for observer measures;
3. separate one persistent latent draw from repeated draws of a world-level prior;
4. expose prior/channel factorization gauges;
5. show how shared-latent multiview observations or interventions can break specific gauges;
6. provide a disciplined hierarchy for when Bayes factors about simulation-like hypotheses are meaningful.

**Assessment:** paper-worthy as a philosophy-of-science / foundations synthesis if the literature positioning is done carefully. The individual lemmas are mostly elementary or connected to known areas; the contribution is the integrated identifiability framework applied to simulation/anthropic reasoning.

### Candidate P2 — technical note, conditional on novelty search

**Working title:** *Inverse Total-Variation Conditioning for Finite Mixture Channels*

Core object:

\[
\alpha(K)=\inf_{\delta\ne0,\,1^T\delta=0}\frac{TV(\delta K)}{TV(\delta)}.
\]

Potential contribution:

- exact rational computation through finite TV games;
- channel-mixture inverse interpretation;
- explicit near-affine-dependence examples where pairwise row separation is misleading;
- robust lower moduli under rowwise uncertainty;
- composition with observed-law confidence sets.

**Assessment:** mathematically coherent, but novelty is not yet established. Facial-distance/pyramidal-width and minimum-gain literature are close enough that a paper must explicitly prove what is new beyond a TV-norm specialization/application.

### Candidate P3 — decision-theory note

**Working title:** *When Better Experiments Increase Minimax Regret*

The moving-oracle K4 construction shows that enriching an experiment menu can weakly improve absolute robust performance while increasing regret against an oracle that receives the same richer menu.

**Assessment:** clean and teachable. Likely a short note unless generalized substantially. Benchmark instability is a general decision-theoretic phenomenon, so novelty requires literature work.

### Candidate P4 — robust source-coding/control synthesis

The nonrectangular/fixed-model coding, partial observation, public-randomness matching, drift coupling, and regret layers form a coherent exact finite laboratory.

**Assessment:** potentially a paper if reframed around one new theorem or algorithmic complexity result. As currently written, much of the conceptual backbone overlaps robust MDP, multiple-priors, robust coding, and POMDP literatures.

## What is not currently paper-worthy by itself

The following are valuable repo components but should not be sold as standalone novel papers without a new contribution:

- standard Bell/Fisher/Pinsker calculations;
- standard Dobrushin contraction;
- standard Fano/random-access lower bounds;
- standard Huffman entropy bounds;
- rational additivity alone;
- Boolean influence/Fourier identities alone;
- exact finite examples whose only novelty is exhaustive enumeration;
- CI/proof-receipt infrastructure without a scientific theorem or systems contribution.

## Required pre-submission audit

Before any theorem is described as new in a manuscript:

1. freeze one commit containing the exact theorem statement and proof;
2. produce a dependency graph of lemmas and assumptions;
3. re-derive each theorem independently from the implementation;
4. test all equality cases and assumption boundaries;
5. search MathSciNet/zbMATH/Google Scholar/arXiv by mathematical object, not project vocabulary;
6. add explicit nearest-prior-work comparisons theorem by theorem;
7. separate known lemma, new corollary, new algorithm, and new application;
8. have at least one external domain expert attempt to break the central theorem;
9. reproduce every numerical table from a clean checkout;
10. keep all simulation-level interpretations downstream of an explicit observation/implementation map.

## Bottom line

The repository contains a large amount of mathematically coherent work, but **coherence is not novelty**. The most promising paper is not "a proof that we are simulated." It is a disciplined negative/structural paper about when simulation-style Bayesian and observer-counting arguments are identifiable and representation invariant.

The strongest technical subproject is the finite-mixture