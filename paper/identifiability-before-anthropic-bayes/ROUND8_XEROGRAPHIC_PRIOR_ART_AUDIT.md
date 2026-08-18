# Round 8 — xerographic-distribution prior-art audit

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`

This is an internal synthetic review round. It records a prior-art correction discovered after the self-location extension was added. It is not external peer review.

## R8.1 — the self-location kernel is not a new probability object

**Finding.** Hartle and Srednicki's large-universe framework explicitly introduces a **xerographic distribution**, a probability distribution for our location among otherwise compatible instances. The finite conditional kernel `s(c|w)` added in Round 7 plays the same mathematical role once one conditions on a world.

**Severity.** Major novelty-positioning correction; no mathematical error.

**Impact if ignored.** A reviewer familiar with anthropic cosmology could reasonably object that the manuscript reinvents an established self-location/typicality object while presenting it as a new formalization. That would damage confidence in the literature audit even though the displayed Bayes decomposition is correct.

**Feasibility.** High.

**Disposition. Accepted.** The manuscript now:

- calls the finite kernel closely analogous to / a finite conditional version of a xerographic distribution;
- cites Hartle and Srednicki directly;
- removes any implication that the location-distribution object itself is novel;
- keeps the paper's claimed contribution at the level of the integrated simulation-specific audit: self-location rule -> refinement invariance -> latent sampling hierarchy -> identifiability -> Bayesian update.

The machine-readable claim ledger now says explicitly that the location-distribution idea is not claimed as novel.

## R8.2 — a self-location kernel must not be mistaken for a literal random selector

**Finding.** Hartle and Srednicki's earlier discussion of typicality warns against a **selection fallacy**: one should not infer that observers were physically randomly selected from a class merely because a predictive calculation uses a typicality or location assumption.

**Severity.** Important conceptual-scope correction.

**Impact if ignored.** The word "sampling" could be read as asserting an actual physical sampling mechanism. That would make the paper vulnerable to a criticism it is otherwise designed to prevent: confusing a credence convention with a causal data-generating process.

**Feasibility.** High.

**Disposition. Accepted.** The paper now states that `s(c|w)` is a mathematical representation of a conditional centered-credence rule. No literal global sampler is required. A theory such as FNC may use richer evidence and a different centered weighting.

## R8.3 — does the prior art make the Round-7 extension unnecessary?

**Finding.** Because xerographic distributions already exist, one might remove the self-location section entirely.

**Impact analysis.** Removing it would avoid any appearance of reinvention, but it would recreate the paper's earlier conceptual gap. The core question is not whether a location distribution has appeared before; it is how population counts, representational refinement, world weighting, persistent-latent sampling, and structural identifiability fit into one auditable generative hierarchy for simulation arguments.

**Disposition. Reject removal.** Retain the section, but position it explicitly as synthesis/application rather than invention. The exact two-world example is still useful because it shows:

- equal world priors + uniform within-world self-location gives odds `5/3`;
- raw global counts give `2`;
- reference-class-size world weights recover `2`;
- mass-conserving representational refinement keeps `5/3`;
- re-uniformizing the refined labels changes the odds to `3`.

That example directly connects self-location prior art to the paper's representation-invariance diagnostic.

## R8.4 — field-impact decision after the correction

**Decision.** Keep the self-location extension and **stop expanding this manuscript mathematically** after this round.

The strongest publishable thesis is now narrower and more defensible:

> Simulation-style anthropic Bayes is an inferential pipeline rather than one posterior formula. Population counts affect centered credence through an explicit self-location/typicality rule; representation-only refinements should preserve that rule's total mass; repeated evidence has the sample size implied by the latent causal hierarchy; and latent prevalence can be interpreted as learned from data only insofar as the observation model identifies it.

Additional inverse-conditioning, robust-control, experimental-design, and multiview results should be reserved for companion technical papers.

## Round-8 disposition

**Pass with literature-positioning revision.** The mathematical self-location decomposition survives. The novelty claim is reduced. No new theorem is required. The main remaining release work is reproducibility/CI/PDF verification and external specialist review, not further expansion.
