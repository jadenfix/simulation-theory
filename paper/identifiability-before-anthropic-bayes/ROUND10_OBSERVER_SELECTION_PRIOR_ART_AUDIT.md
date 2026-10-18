# Round 10 — observer-selection prior-art audit

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Status:** synthetic internal review, not independent peer review.

## Objective

Round 10 asked whether the paper's explicit self-location formalism still omitted peer-reviewed work whose main contribution is itself to expose observer-selection assumptions. The answer was yes: Robert Garisto's 2020 *Physical Review Research* article **“How to select observers”** is sufficiently close prior art that it should constrain novelty language.

## Primary-source finding

The APS version of record describes Garisto's goal as reconciling observer-selection disputes by “introducing a formalism to lay bare assumptions made” and distinguishes whether an observer is selected by **picking from** or **being in** a set of worlds. It also relaxes equal-typicality assumptions. This is directly adjacent to the present manuscript's insistence that observer counts do not become centered probabilities without an explicit self-location/selection convention.

Bibliographic record:

- Robert Garisto, “How to select observers,” *Physical Review Research* **2**, 033464 (2020).
- DOI: `10.1103/PhysRevResearch.2.033464`.
- Published 22 September 2020.

## Findings

| ID | Finding | Severity | Impact | Feasible? | Disposition |
|---|---|---|---|---|---|
| R10.1 | Garisto (2020) is close peer-reviewed prior art for formalizing observer-selection assumptions and distinguishing alternative selection semantics. | **Major novelty-positioning issue** | Prevents the manuscript from implying that explicit observer-selection formalization itself is the integrated contribution. | Yes | **Accepted.** Add as direct related work and machine-readable provenance. |
| R10.2 | Garisto's formalism does not by itself subsume the paper's persistent-latent likelihood-ratio ceiling, known/unknown-channel identifiability distinction, one-view gauge, or scoped repeated-view rigidity result. | Scope distinction | Preserves a narrower incremental contribution after novelty correction. | Yes | **Accepted.** Position the paper as extending the audit from observer-selection semantics into sampling hierarchy and structural identifiability. |
| R10.3 | The paper should not portray “selection fallacy” as meaning that centered credences can never be represented probabilistically. Hartle--Srednicki object to an unjustified literal physical-selection story; xerographic and other conditional credence distributions remain legitimate explicit assumptions. | Conceptual scope | Avoids a false dichotomy between literal sampling and formal conditional credence. | Yes | **Already satisfied.** Round 9 language uses a conditional self-location kernel and explicitly denies a required physical chooser. |
| R10.4 | A close prior-art citation should not be treated as proof of the paper's theorems. | Provenance | Keeps literature support and mathematical proof roles separate. | Yes | **Accepted.** Garisto is cited for observer-selection formalism only. |

## Revised novelty map

After Rounds 8--10, the manuscript should make no novelty claim for any of the following in isolation:

- a distribution over centered locations;
- separating observer selection/self-location assumptions from a literal global sampler;
- formalizing observer-selection semantics;
- count calibration under a declared uniform centered rule;
- finite additivity;
- affine-rank identifiability with a known channel;
- generic nonnegative-factorization ambiguity;
- generic multiview latent-variable identification.

The remaining integrated contribution is the simulation-specific audit chain

```text
observation interface
  -> measure-bearing unit / self-location rule
  -> representation-refinement invariance
  -> persistent-versus-redrawn latent hierarchy
  -> conditional and joint identifiability
  -> Bayesian or self-locating update.
```

The paper's strongest methodological claim is therefore not “we discovered observer selection.” It is that several debates commonly treated separately become one falsifiable generative-model audit when applied to numerical simulation probabilities.

## Mathematical recheck triggered by the prior-art comparison

Garisto's distinction between observer-selection semantics prompted a recheck of Proposition T8. The exact Bayes decomposition remains correct. Round 9 already fixed the only substantive scope issue: bare kernel-mass odds require nondiscriminating evidence, whereas discriminating evidence requires the likelihood-weighted mass expression. A dedicated exact-rational regression test now exercises this negative boundary.

## Decision

**Pass with literature revision.** No mathematical false positive was found. Garisto should be added to the bibliography/provenance and cited as peer-reviewed prior art before the manuscript is frozen. No new theorem is warranted in response.
