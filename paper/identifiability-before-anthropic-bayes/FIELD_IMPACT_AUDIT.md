# Field-impact and extension audit

## Purpose

This document records the external-literature pass used to decide whether the manuscript should be extended before release. It is intentionally separate from the manuscript so that novelty decisions, rejected extensions, and citation checks remain auditable.

The question is not whether more mathematics can be added. The question is whether an addition materially sharpens the paper's contribution relative to the closest literature without diluting the central identifiability-first thesis.

## Closest simulation and anthropic literature

### Bostrom (2003), *Are You Living in a Computer Simulation?*

The original argument is a trilemma about posthuman survival, willingness to run ancestor simulations, and the fraction of observers with human-type experiences who are simulated. It is not itself a generic empirical simulator-detection theorem.

**Relation to this paper:** the present manuscript moves one level earlier in the inferential chain: before a population ratio or posterior is interpreted, the observation interface, measure-bearing units, sampling hierarchy, and identifiability assumptions must be specified.

### Bostrom and Kulczycki (2011), *A Patch for the Simulation Argument*

The authors explicitly identify a mathematical non sequitur in one formula in the original presentation and give two patches intended to preserve the original conclusion.

**Relation:** this is strong precedent for auditing the exact probability model rather than treating formula choices as philosophically inert. It should remain explicitly cited in the introduction and related-work discussion.

### Weatherson (2003), *Are You a Sim?*, and Bostrom (2005), reply

Weatherson attacks the indifference step connecting population structure to self-locating credence; Bostrom responds that the relevant principle has been mischaracterized.

**Relation:** the manuscript should not try to settle that normative disagreement. Instead it can expose the generative object underneath it: a self-location sampling kernel. Uniform sampling over the declared candidate centers recovers count calibration; another kernel gives another weighting. This makes the assumption explicit without claiming that one kernel is uniquely rational.

### Elga (2004), *Defeating Dr. Evil with Self-Locating Belief*

Elga defends indifference across subjectively similar centered worlds. Later literature disputes whether the principle is derivable, but the paper is a canonical articulation of self-locating indifference.

**Relation:** useful direct prior for the new sampling-kernel section. The proposed theorem is not a rival decision theory; it translates a self-location rule into a generative probability kernel.

### Neal (2006), full non-indexical conditioning

Neal advocates conditioning on the observer's full non-indexical evidence rather than only a reference-class membership fact.

**Relation:** the current manuscript correctly treats FNC as downstream of a specified generative likelihood. The new sampling-kernel formalization should make this distinction even clearer: the kernel identifies how centered possibilities are weighted; the likelihood describes how full evidence is generated conditional on a centered possibility.

### Schneider and Olum (2013), anomalous observers

They stress that a subjectively identical reference class can become difficult to delimit once simulations, replays, stored computations, or abstract representations are admitted.

**Relation:** this is the closest conceptual precursor to the manuscript's representation-refinement concern. Our incremental contribution is not the observation that reference classes are hard. It is the explicit invariance diagnostic: if a transformation is declared representation-only and total measure-bearing mass is conserved, posterior changes must come from a changed sampling measure rather than new observational evidence.

### Fallis and Lewis (2023), *Simulation and Self-Location*

They argue that the treatment of self-locating uncertainty can substantially alter the probability assigned to simulation and use the analogy with Sleeping Beauty to evaluate competing approaches.

**Relation:** this makes it especially important that our paper not present ordinary Bayes alone as resolving self-location. The new kernel theorem should be framed as a neutral parameterization of the self-location rule, not as a normative endorsement.

### Kipping (2020), *A Bayesian Approach to the Simulation Argument*

Kipping adds model uncertainty about whether ancestor simulations are technically possible and performs Bayesian model averaging.

**Relation:** model averaging and identifiability are distinct. A posterior can average across specified models while remaining sensitive to unidentified internal parameterizations. The manuscript's contribution is complementary.

### Thomas (2024 online / 2026 issue), *Simulation Expectation*

Thomas replaces a high realized simulant ratio with a high conditional expected ratio and states an explicit calibration principle: conditional on only reference-class membership and a ratio of F to G members, the self-locating odds equal that ratio. Thomas also emphasizes that discovering many simulations need not raise the odds that one is simulated.

**Relation:** this is the paper the new extension must engage most directly. The proposed sampling-kernel theorem identifies exactly what calibration means in a finite generative model. Within a fixed world, count calibration is recovered by a uniform self-location kernel. Across uncertain worlds, a raw global count ratio additionally requires a specific world-weighting rule. This is a useful clarification rather than a refutation of Thomas.

## Closest statistical literature

### Allman, Matias, and Rhodes (2009)

General latent-structure identifiability requires substantially more than the manuscript's scoped two-view gauge argument. The current paper correctly avoids claiming generic two-view latent-class identification.

### Gillis (2020)

Nonnegative factorization is generically nonunique without additional structure. The manuscript's one-view stochastic gauge is therefore best presented as a constructive witness tailored to the simulation-inference hierarchy, not as a new classification theorem.

### Giacomini and Kitagawa (2021)

Set identification does not make Bayesian analysis impossible. Robust posterior sets/ranges can be reported when point identification fails.

**Relation:** the paper should continue to say “identifiability before interpreting a precise data-driven posterior,” not “Bayes is invalid under nonidentification.”

## Extension candidates considered

### Candidate A: add more finite-mixture conditioning theorems

**Decision: reject for this paper.**

The repository contains deeper inverse-TV and conditioning results, but they would move the paper toward a technical mixture-identifiability article and away from the central anthropic contribution. They are better candidates for a separate technical paper.

### Candidate B: strengthen the two-view theorem to general multiview identification

**Decision: reject.**

That would collide directly with a mature literature and require substantially stronger assumptions. The existing theorem is useful precisely because it is narrow and auditable.

### Candidate C: add a self-location sampling-kernel theorem

**Decision: accept. High impact / low-to-moderate complexity.**

This fills the largest conceptual gap in the current manuscript. The paper presently says that measure-bearing units must be specified, but it does not yet show algebraically how a chosen self-location rule converts world populations into posterior odds.

Proposed finite model:

- `W`: a world with prior `rho(w)`;
- `C_w`: finite candidate centered locations/observers in world `w`;
- `s(c|w)`: a self-location kernel with `sum_c s(c|w)=1`;
- `L(e|w,c)`: likelihood of the observer's evidence;
- `F` and `G`: mutually exclusive centered categories, e.g. simulant and non-simulant.

Then

\[
\frac{P(F\mid e)}{P(G\mid e)}
=
\frac{\sum_w \rho(w)\sum_{c\in F_w}s(c\mid w)L(e\mid w,c)}
{\sum_w \rho(w)\sum_{c\in G_w}s(c\mid w)L(e\mid w,c)}.
\]

Consequences:

1. **Within-world count calibration.** If `s(c|w)=1/|C_w|` and the relevant evidence does not distinguish candidates inside the reference class, then conditional self-locating odds within that world equal `|F_w|/|G_w|`.
2. **Weighted calibration.** For a nonuniform kernel, counts are replaced by total kernel mass.
3. **Across-world warning.** Even if every within-world kernel is uniform, the aggregate odds are generally
   \[
   \frac{\sum_w \rho(w)|F_w|/|C_w|}{\sum_w \rho(w)|G_w|/|C_w|},
   \]
   not the raw ratio of total counts across worlds. The latter requires additional world weighting, e.g. weights proportional to reference-class size in the simplest finite construction.
4. **Refinement invariance.** Splitting one centered possibility into observationally identical representational clones leaves the posterior unchanged when its kernel mass is split among the clones. Re-imposing a uniform-over-label kernel after adding clones changes the sampling model; it is not an evidential update.

This section would directly connect the paper's representation-invariance result to the philosophical indifference/calibration debate without pretending to resolve the normative choice of self-location rule.

### Candidate D: add a numerical probability that we are simulated

**Decision: reject.**

Doing so would undermine the central methodological contribution. The paper is strongest when it explains why a numerical answer is conditional on a precisely stated observation, measure, hierarchy, and identification model.

## Expected impact of the accepted extension

Without the kernel theorem, the paper can be read as a sequence of good but somewhat disconnected diagnostics. With it, the argument becomes a single generative hierarchy:

1. choose a world/model prior;
2. choose a self-location kernel over measure-bearing centered possibilities;
3. generate evidence conditional on the centered possibility;
4. check representation invariance and the sampling hierarchy;
5. check whether structural parameters are identified by the observation law;
6. then perform the chosen ordinary or self-locating Bayesian update.

That hierarchy creates a direct bridge between the simulation-argument literature and statistical identifiability. It is the extension most likely to increase the paper's conceptual impact without overstating mathematical novelty.

## Publication recommendation after extension

If the sampling-kernel theorem is incorporated with explicit nonclaims and exact finite reproduction tests, the paper has a clearer publishable thesis:

> Simulation-style anthropic Bayes is not one inferential step. Population counts influence credence only through a declared self-location sampling rule; repeated evidence has the sample size implied by its latent causal hierarchy; and latent prevalence can be interpreted as learned from data only to the degree that the observation model identifies it.

The paper should then stop expanding. Additional technical results should move to companion papers rather than making this manuscript longer and less coherent.
