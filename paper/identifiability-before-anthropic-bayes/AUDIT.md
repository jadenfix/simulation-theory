# Publication audit: Identifiability Before Anthropic Bayes

**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Audit status:** preprint-candidate, adversarial internal audit completed; external expert review still recommended before journal submission.

## Audit philosophy

This paper is intentionally easier to falsify than a broad simulation hypothesis. Every formal claim has a narrow interface, explicit assumptions, and a corresponding nonclaim. Code reproduces finite examples; it is not used as a substitute for universal proofs. Literature claims are separated from mathematical claims, and elementary results are labeled elementary rather than promoted as novel theorems.

## Theorem-by-theorem adversarial audit

| ID | Attack attempted | Result | Remaining scope risk |
|---|---|---|---|
| P1-T1 observable equivalence | Zero-probability transcripts; nondominated notation; adaptive interventions | Equality of measures gives `dP_S/dP_B=1` almost surely; discrete/common-density BF statement is a representation of that fact. | Restricted simulator alternatives can remain testable under a richer interface. |
| P1-T2 refinement invariance | Reinterpret clones as newly created conscious observers | Algebra holds for representational refinement. Physical duplication is a different model. | Individuation/measure theory remains a philosophical input. |
| P1-T3 split additivity | Zero weight; negative weights; nonlocal measures; irrational domain | Proof includes `mu(0)=0` and is exact on nonnegative rational weights for a local weight-only rule. | Not a uniqueness theorem for all anthropic measures. |
| P1-T8 self-location sampling kernel | Treat raw center counts as automatic odds; change world prior; clone a center and either conserve or reset its kernel mass; interpret the kernel as a literal physical sampler | Exact Bayes decomposition shows that centered odds depend on world weights, kernel masses, and evidence likelihoods. Uniform-within-world sampling recovers within-world count calibration. Mass-conserving representational refinement leaves the posterior unchanged; re-uniformizing over refined labels changes the model. | The theorem does not select the normatively correct self-location rule and does not claim a physical global sampler exists. |
| P1-T4 persistent latent LR | Denominator support mismatch; different component likelihoods; continuous transcripts without a common density | Identity holds for discrete transcripts or commonly dominated component laws, under realized-support absolute continuity. Support mismatch can make BF infinite. | A broader measure-theoretic version should not be inferred from the displayed pointwise density formula. |
| P1-T5 known-channel identification | Boundary priors; affine dependence; claim that Bayes becomes impossible | Injectivity of the full simplex map is exactly affine independence. Collision witnesses exist when rank fails. Bayesian set/sensitivity analysis remains possible without point identification. | Local/boundary identification and finite-sample conditioning are separate questions. |
| P1-T6 one-view gauge | Negative transformed prior; fake continuum generated only by relabeling | Proposition requires transformed-prior nonnegativity. A genuine local continuum is constructed for interior `pi` and distinct channel rows. | This is one gauge family, not a classification of NMF ambiguity. |
| P1-T7 repeated-view rigidity | Zero transformed-prior entries; rank-deficient K; signed A; different view-specific channels | Proof survives only for two conditionally independent repeated observations using the same channel, with the declared rank, positivity, and nonnegativity assumptions. | Same-channel gauge-orbit rigidity, not general multiview latent-class identifiability. |

## Independent finite falsification checks

`reproduce.py` uses exact `fractions.Fraction` arithmetic and checks successful and negative cases: clone-count instability; self-location count calibration versus world weighting; mass-conserving versus re-uniformized representational refinement; persistent vs redrawn latent examples; exact finite-mixture LR reconstruction; support mismatch; known-channel collisions; valid/invalid gauge transforms; and exhaustive bounded 2-state and 3-state two-view grids. The grid audits are finite falsification aids, not proofs of the universal theorem.

An additional internal implementation audit exercised the 3x3 exact inverse routine on hundreds of nonsingular integer matrices and recovered the identity exactly in rational arithmetic. This is implementation evidence only and is not promoted to a paper theorem.

## Citation and novelty audit

The bibliography is checked against publisher or primary archival metadata where available, with discrepancies preserved in `citation_provenance.json`. The audit corrected Richmond's issue/pages, resolved Franceschi's publisher issue year to 2016 while preserving secondary-index disagreement, updated Khawaja to final BJPS pages 313--344, and corrected the Fallis--Lewis record from secondary issue/page metadata to the Springer version of record: Peter J. Lewis and Don Fallis, *Synthese* 202, article 180 (2023).

A later novelty pass added Bostrom--Kulczycki's 2011 patch paper and Fallis--Lewis's 2023 self-location paper because both are directly relevant to the manuscript's framing. A fifth-round scope pass added Giacomini--Kitagawa's robust Bayesian treatment of set-identified models to make explicit that nonidentification calls for prior-sensitivity or set-valued reporting rather than a prohibition on Bayesian analysis. The field-impact pass, preserved in `FIELD_IMPACT_AUDIT.md`, read the paper against Thomas's explicit Calibration principle, Weatherson/Bostrom on indifference, Elga on self-location, Neal on FNC, Schneider--Olum on anomalous reference classes, Kipping on model uncertainty, and the latent-identifiability literature. It concluded that the one extension that materially improves this paper is an explicit self-location sampling kernel; further mixture-conditioning results would dilute the thesis and are deferred to companion work.

The paper does **not** claim novelty for equality-of-measures consequences, finite rational additivity, the self-location Bayes decomposition, the finite-mixture LR convex-combination identity, known-channel affine-rank identification, generic NMF ambiguity, generic multiview identification, or Bayesian inference under partial identification. The claimed contribution is the integrated identifiability-first audit hierarchy for simulation-style anthropic Bayes, its boundary examples, the explicit connection from count calibration to a declared self-location kernel, and the auditable synthesis.

## False-positive controls

The manuscript and CI enforce that it does not claim reality is or is not simulated, does not call all simulator hypotheses untestable, does not identify representational refinement with physical observer creation, does not claim probability weight is the unique possible anthropic measure, does not claim a uniquely rational self-location kernel, does not equate raw population counts with centered odds without additional assumptions, does not claim generic two-view identification, does not claim that nonidentified parameters cannot receive Bayesian posteriors, does not promote bounded computation to a universal theorem, and does not treat within-world repetitions as independent world draws.

## Reproduction contract

A release-quality run must:

1. regenerate `receipt.json` byte-for-byte from `reproduce.py`;
2. pass the paper-specific pytest suite and ordinary repository test matrix;
3. record the exact Git commit plus Python/pdfTeX/BibTeX/Poppler and runner provenance;
4. build via `pdflatex -> bibtex -> pdflatex -> pdflatex`;
5. fail on unresolved references/citations or overfull boxes;
6. preflight title/author PDF metadata;
7. hash source, resolved bibliography, bibliography source, claims/provenance, exact receipt, tests, workflow, review/audit artifacts, field-impact audit, toolchain record, and release PDF;
8. upload both release source and the generated PDF/log bundle;
9. render and visually inspect every page before freezing a preprint.

The exact JSON receipt is intended to be byte-stable. The PDF receives a release-specific hash and recorded toolchain; the audit does not claim byte-identical PDFs across future TeX distributions or timestamp behavior.

## What still requires human judgment

No automated audit establishes literature novelty, philosophical adequacy of an observer measure or self-location rule, or the truth of a simulation hypothesis. Before journal submission, at least one external reader familiar with anthropic/self-locating inference and one reader familiar with finite-mixture or latent-variable identifiability should independently seek counterexamples or prior work that subsumes the scoped contribution.
