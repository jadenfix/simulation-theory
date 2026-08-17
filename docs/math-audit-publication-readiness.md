# Mathematical audit and publication-readiness review

Date: 2026-08-17

## Audit standard

This review is intentionally stricter than CI. A green test establishes agreement between code and a bounded checker; it does not establish theorem novelty, physical applicability, or freedom from a hidden assumption.

Every result is judged on: algebraic correctness, operational semantics, assumption boundaries, adversarial edge cases, and novelty relative to existing literature.

## Executive result

I found **no high-confidence false mathematical theorem on the current mainline within its written assumptions** in the families re-derived during this audit. The repo is unusually good about separating theorem/model-result/finite-check/nonclaim.

That is not the same as peer review. Several results are correct but known, several open PRs are not independently integrated, and several claims need narrower publication wording.

## High-confidence families

The following survived first-principles re-derivation in their declared scopes:

- identical-law observational nonidentifiability and Bayes-factor equality;
- TV/classification, Le Cam/Fano-style decision bounds;
- predictive equivalence, finite packing/cover arguments, and Dobrushin contraction;
- confusion-graph zero-error coding and prior-weighted Huffman optimization;
- finite-prior and TV-ball robust coding conditional on the enumerated code universe;
- coupled TV-drift versus marginal robustification;
- nested information-pattern inequalities;
- Bayesian hidden-state filtering under the declared action-independent dynamics;
- fixed-model versus rectangular ambiguity semantics;
- active-experiment/public-randomness decompositions;
- fixed-oracle minimax regret;
- Bayesian Boolean minority-mass, influence, Fourier, and adaptive-query identities;
- fixed-sample prior-sensitivity/calibration under iid latent-unit sampling;
- persistent-latent likelihood-ratio ceilings;
- finite-mixture affine identifiability conditional on known emissions;
- latent-component refinement invariance.

## Important corrections / blockers

### 1. Correct does not mean novel

Robust Huffman coding, Dobrushin contraction, rectangularity in dynamic ambiguity, Boolean influence/Fourier analysis, and branch/refinement indifference all have substantial prior literatures. Exact rational certificates improve reproducibility but do not by themselves make a theorem new.

### 2. Global mixture TV modulus is close to known facial distance

For affinely independent channel rows, their convex hull is a simplex. The quantity

\[
\alpha(K)=\inf_{\delta\ne0,\;1^T\delta=0}\frac{TV(\delta K)}{TV(\delta)}
\]

is equivalently a minimum distance between disjoint row faces. This is closely related to the established facial-distance / pyramidal-width / minimum-gain literature. Do not market the face-distance identity itself as a new general convex-geometric theorem without a much deeper novelty search.

The potentially new technical contribution is narrower: exact rational TV computation for mixture-channel inversion, rowwise uncertainty certificates, and composition with statistical confidence sets.

### 3. Two-view rigidity is a gauge-orbit theorem

For the declared gauge

\[
K'=AK,\qquad \pi'=\pi A^{-1},
\]

full row rank, positive transformed prior, nonnegative row-stochastic invertible `A`, and equality of the shared-latent two-view law imply

\[
A^T D_{\pi'}A=D_\pi.
\]

Off-diagonal nonnegative sums then force `A` to be a permutation. This derivation is sound.

But it proves rigidity **inside this gauge class**. It does not establish unrestricted global identifiability of every two-view latent-class factorization. Publication wording must preserve that distinction.

### 4. Refinement-additive measure uniqueness is correct but elementary

A normalized local rational rule additive under every finite split must satisfy `mu(p/q)=p/q`. Equal `r`-way cloning changes escort score `w^gamma` by `r^(1-gamma)`, so only `gamma=1` is refinement invariant.

The mathematics is correct. The publishable value is the application to representation-sensitive observer counting, not novelty of rational additivity itself.

### 5. Persistent-latent evidence ceiling needs absolute-continuity wording

For one latent draw followed by an arbitrary conditional transcript,

\[
\frac{P_a(y)}{P_b(y)}
=\sum_m P_b(M=m\mid y)\frac{a_m}{b_m},
\]

when the relevant denominator weights are positive. Hence the transcript Bayes factor lies between component prior-weight ratios.

This is correct, but there is no finite ceiling if the denominator gives zero mass to a component allowed by the numerator. Also, this limits inference about the **mixing weights/hyperprior** after one persistent draw; it does not prevent a long transcript from identifying which latent model is active.

### 6. Confidence bounds are valid, not efficient

The exact-rational second-moment/Markov radii are conservative. A paper should compare them with sharper multinomial concentration, exact confidence regions, method-of-types bounds, or confidence sequences. `Certified` must not be used as a synonym for `optimal`.

### 7. Open stacked PRs are not verified mainline mathematics

A paper should cite a frozen mainline/paper commit, not a moving stacked PR. Earlier ancestry pollution showed why this matters.

## Adversarial spot checks

- `x/(B+x)` is concave for `B>0`, so the observer-count Jensen warning is correct.
- Dobrushin TV contraction is correct and classical.
- Noisy cat parity visibility `(1-2p)^ell`, proper-marginal blindness, and BSC reduction are correct under independent sign flips.
- The rate-distortion lower bound `I(Z;M)>=m[1-H2(D/c)]` is correct in the documented regime `0<=D<c/2`; the repo correctly drops it to zero beyond that threshold.
- TV-ball robust expectation is a mass-transport problem; its fixed-vector maximum is piecewise linear and concave in radius.
- `exists M for all t` is not the same uncertainty model as `for all t exists M_t`; the fixed-model/rectangular distinction is correct but classical in robust decision theory.
- Bayesian Boolean gap `V(S)=1/2(1-E|E[g|X_S]|)` and leave-one-out `V=Influence/2` are correct under the uniform prior.
- Known-channel finite-mixture weights are identifiable iff channel rows are affinely independent.
- Rowwise TV perturbations change the global inverse modulus by at most `2 max_i r_i`; the factor two is attainable.
- The one-view stochastic gauge preserves `pi K` exactly whenever transformed weights remain a valid prior.
- Splitting one latent component into positive-weight identical clones preserves every finite conditionally-iid shared-latent view law.

## Publication candidates

### P1 — strongest overall

**Identifiability Before Anthropic Bayes: Representation Invariance, Persistent Latents, and Observable Equivalence in Simulation Arguments**

This is the best paper direction. The contribution would be the integrated framework, not a claim that each lemma is new:

1. observational equivalence before Bayesian updating;
2. representation/refinement invariance for observer measures;
3. one persistent latent draw versus repeated world-level draws;
4. prior/channel factorization gauges;
5. multi-view/interventional structures that break specific gauges;
6. a hierarchy of conditions required before simulation-style Bayes factors are meaningful.

**Assessment:** paper-worthy for philosophy of science / foundations if positioned against the simulation-argument, reference-class, anthropic-measure, and branching-indifference literatures.

### P2 — technical note, novelty not yet established

**Inverse Total-Variation Conditioning for Finite Mixture Channels**

Potential contribution: exact rational global modulus, mixture-channel inverse interpretation, examples where pairwise row separation badly misstates mixture conditioning, row-uncertainty lower moduli, and confidence-set composition.

**Assessment:** mathematically coherent, but facial-distance/minimum-gain prior work is close. Needs theorem-by-theorem literature comparison before calling it novel.

### P3 — short decision-theory note

**When Better Experiments Increase Minimax Regret**

The moving-oracle K4 construction cleanly shows that a richer experiment menu can improve absolute performance while increasing regret against an oracle that receives the same richer menu.

**Assessment:** elegant and teachable; likely a short note unless generalized substantially.

### P4 — robust coding/control synthesis

The fixed-model/nonrectangular, partial-observation, public-randomness, drift-coupling, and regret layers form a coherent exact finite laboratory.

**Assessment:** potentially publishable only if centered on a genuinely new theorem/algorithm/complexity result. The conceptual backbone overlaps robust MDP, multiple-priors, POMDP, and robust coding literatures.

## Not standalone-novel without more

Standard Bell/Fisher/Pinsker calculations, Dobrushin contraction, Fano/random-access bounds, Huffman entropy bounds, rational additivity, Boolean Fourier identities, and bounded exhaustive examples are useful infrastructure but should not be sold as standalone new mathematics.

## Required pre-submission gate

Before any claim is described as new:

1. freeze one commit;
2. build a theorem/lemma dependency graph;
3. independently re-derive the central theorem;
4. test equality and assumption-boundary cases;
5. search literature by mathematical object rather than repo vocabulary;
6. write a nearest-prior-work comparison for every claimed contribution;
7. label each result as known lemma, new corollary, new algorithm, or new application;
8. obtain an external adversarial review from a domain expert;
9. reproduce all numerical results from a clean checkout;
10. keep simulation-level interpretations downstream of an explicit observation/implementation map.

## Bottom line

There is real paper material here, but the strongest paper is **not** a proof that reality is simulated. It is a structural paper showing why identifiability, sampling hierarchy, representation invariance, and causal observation structure must be fixed before anthropic or simulation-style Bayesian conclusions are justified.

The strongest technical mathematics is the finite-mixture inverse-conditioning program, but its novelty remains provisional until the facial-distance/minimum-gain literature is exhaustively reconciled.