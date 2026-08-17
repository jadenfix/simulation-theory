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
| P1-T3 split additivity | Zero weight; negative weights; nonlocal measures; irrational domain | Proof now includes `mu(0)=0` and is exact on nonnegative rational weights for a local weight-only rule. | Not a uniqueness theorem for all anthropic measures. |
| P1-T4 persistent latent LR | Denominator support mismatch; different component likelihoods; continuous transcripts without a common density | Identity holds for discrete transcripts or commonly dominated component laws, under realized-support absolute continuity. Support mismatch can make BF infinite. | A broader measure-theoretic version should not be inferred from the displayed pointwise density formula. |
| P1-T5 known-channel identification | Boundary priors; affine dependence | Injectivity of the full simplex map is exactly affine independence. Collision witness exists when rank fails. | Local/boundary identifiability can be weaker than global simplex injectivity; conditioning is separate. |
| P1-T6 one-view gauge | Negative transformed prior; fake “continuum” generated only by relabeling | Proposition requires transformed-prior nonnegativity. A genuine local continuum is explicitly constructed for interior `pi` and distinct channel rows. | This is one gauge family, not a classification of NMF ambiguity. |
| P1-T7 two-view rigidity | Zero transformed-prior entries; rank-deficient K; signed A | Proof fails if positivity/rank/nonnegativity assumptions are dropped, exactly as declared. | Gauge-orbit rigidity, not general two-view latent-class identifiability. |

## Independent finite falsification checks

`reproduce.py` uses exact `fractions.Fraction` arithmetic and checks successful and negative cases: clone-count instability, persistent vs redrawn latent examples, exact finite-mixture LR reconstruction, support mismatch, known-channel collisions, valid/invalid gauge transforms, and exhaustive bounded 2-state and 3-state two-view grids. The grid audits are finite falsification aids, not proofs of the universal theorem.

An additional internal implementation audit exercised the 3x3 exact inverse routine on hundreds of nonsingular integer matrices and recovered the identity exactly in rational arithmetic. This is implementation evidence only and is not promoted to a paper theorem.

## Citation and novelty audit

The bibliography is checked against publisher or primary archival metadata where available, with discrepancies preserved in `citation_provenance.json`. The audit corrected Richmond's issue/pages, resolved Franceschi's publisher issue year to 2016 while preserving secondary-index disagreement, and updated Khawaja to final BJPS pages 313--344. A later novelty pass added Bostrom--Kulczycki's 2011 patch paper and Fallis--Lewis's 2023 self-location paper because both are directly relevant to the manuscript's framing.

The paper does **not** claim novelty for equality-of-measures consequences, finite rational additivity, the finite-mixture LR convex-combination identity, known-channel affine-rank identification, generic NMF ambiguity, or generic multiview identification. The claimed contribution is the integrated identifiability-first audit hierarchy for simulation-style anthropic Bayes, its boundary examples, and the auditable synthesis.

## False-positive controls

The manuscript and CI enforce that it does not claim reality is or is not simulated, does not call all simulator hypotheses untestable, does not identify representational refinement with physical observer creation, does not claim probability weight is the unique possible anthropic measure, does not claim generic two-view identification, does not promote bounded computation to a universal theorem, and does not treat within-world repetitions as independent world draws.

## Reproduction contract

A release-quality run must:

1. regenerate `receipt.json` byte-for-byte from `reproduce.py`;
2. pass the paper-specific pytest suite and ordinary repository test matrix;
3. record Python/pdfTeX/BibTeX/Poppler and runner provenance;
4. build via `pdflatex -> bibtex -> pdflatex -> pdflatex`;
5. fail on unresolved references/citations or overfull boxes;
6. preflight title/author PDF metadata;
7. hash source, bibliography, claims/provenance, exact receipt, review/audit artifacts, toolchain record, and release PDF;
8. render and visually inspect every page before freezing a preprint.

The exact JSON receipt is intended to be byte-stable. The PDF receives a release-specific hash and recorded toolchain; the audit does not claim byte-identical PDFs across future TeX distributions or timestamp behavior.

## What still requires human judgment

No automated audit establishes literature novelty, philosophical adequacy of an observer measure, or the truth of a simulation hypothesis. Before journal submission, at least one external reader familiar with anthropic/self-locating inference and one reader familiar with finite-mixture or latent-variable identifiability should independently seek counterexamples or prior work that subsumes the scoped contribution.
