# Publication audit: Identifiability Before Anthropic Bayes

**Author:** Jaden Figgs, Tempera — `Jaden@Tempera.dev`  
**Audit status:** preprint-candidate, adversarial internal audit completed; external expert review still recommended before journal submission.

## Audit philosophy

This paper is intentionally easier to falsify than a broad simulation hypothesis. Every formal claim has a narrow interface, explicit assumptions, and a corresponding nonclaim. The code reproduces finite examples; it is not used as a substitute for the universal proofs in the manuscript. Literature claims are separated from mathematical claims, and elementary results are labeled elementary rather than promoted as novel theorems.

## Theorem-by-theorem adversarial audit

| ID | Attack attempted | Result | Remaining scope risk |
|---|---|---|---|
| P1-T1 observable equivalence | Zero-probability transcripts; adaptive interventions | Holds on common positive support when the **complete allowed transcript law** is equal. | Do not state BF=1 on undefined 0/0 events. Restricted simulator alternatives can remain testable. |
| P1-T2 refinement invariance | Reinterpret clones as newly created conscious observers | The algebra holds for representational refinement. Physical duplication is a different model. | This distinction must remain explicit to avoid straw-manning observer-count arguments. |
| P1-T3 split additivity | Allow negative weights; nonlocal measures; irrational domain | Proof is exact on nonnegative rational weights for a local weight-only rule. | Not a uniqueness theorem for all anthropic measures. |
| P1-T4 persistent latent LR | Denominator support mismatch; different component likelihoods | Convex-mixture identity holds under common component laws and denominator support. Support mismatch can make BF infinite. | Long transcripts may identify active component; theorem only limits evidence about the **mixing weights** under shared components. |
| P1-T5 known-channel identification | Boundary priors; affine dependence | Injectivity of the full simplex map is exactly affine independence. Collision witness exists when rank fails. | Local/boundary identifiability questions can be weaker than global simplex injectivity. |
| P1-T6 one-view gauge | A inverse has negative entries; transformed prior invalid | Proposition assumes transformed prior is valid; K'=AK remains stochastic because A is nonnegative row-stochastic. | This is one gauge family, not a classification of NMF ambiguity. |
| P1-T7 two-view rigidity | Zero transformed prior entries; rank-deficient K; signed A | Proof fails if positivity/rank/nonnegativity assumptions are dropped, exactly as declared. | The result is gauge-orbit rigidity, not general two-view latent-class identifiability. |

## Independent finite falsification checks

`reproduce.py` uses only exact `fractions.Fraction` arithmetic and performs:

- observable-equivalence TV/Bayes-factor check;
- clone-count checks at `r = 1,2,3,5,20,100`;
- finite rational additivity checks through denominator 24;
- exact persistent-world vs independent-redraw BF comparison at `T=100`;
- multiple exact convex-mixture LR reconstructions;
- support-boundary counterexample where the finite BF ceiling intentionally fails;
- affine-rank identifiable and collision examples;
- multiple one-view gauge examples;
- exhaustive 2x2 row-stochastic grid audit through denominator 8;
- exhaustive 3x3 row-stochastic grid audit through denominator 3;
- exact checking of every displayed numerical assertion in the manuscript.

The grid audits are deliberately labeled finite checks. The universal two-view theorem is established by the proof in `paper.tex`.

## Citation audit findings

The bibliography was checked against journal/publisher or archival metadata. Two issues in the first draft were caught:

1. Richmond was initially entered with the wrong issue/pages. Correct journal metadata is **Ratio 30(3), 221-238 (2017)**; first published online 22 March 2016.
2. Franceschi metadata is unusually inconsistent across indexes: PhilPapers/PhilArchive identify the article as 2014 and list 2016 as a reprint year, while secondary issue metadata often gives the volume 43(2) version as 2016. The paper records that discrepancy rather than silently treating it as settled.

`citation_audit.json` records the verification source and the specific proposition for which each citation is used.

## Novelty audit

The paper **does not** claim novelty for:

- equality-of-measures / TV-zero classification consequences;
- finite rational additivity;
- the finite-mixture likelihood-ratio convex-combination identity;
- affine-rank identifiability of a known finite channel;
- generic nonuniqueness of nonnegative factorizations;
- the general idea that multiview moments can identify latent models.

The claimed contribution is the integrated identifiability-first hierarchy applied to simulation-style anthropic Bayes, plus the explicit representational-refinement diagnostic, persistent-latent sampling audit, and the scoped two-view gauge-rigidity lemma presented with an auditable artifact.

## False-positive controls

The manuscript and CI enforce the following language boundaries:

- no statement that the paper proves reality is or is not simulated;
- no statement that all simulator hypotheses are untestable;
- no statement that arbitrary observer duplication is representationally null;
- no claim that probability weight is the unique possible observer measure;
- no claim that two views identify arbitrary latent-class models;
- no promotion of bounded computation to an unbounded theorem;
- no use of within-world repetitions as if they were independent world draws.

## Reproduction contract

A release-quality run must pass, in order:

1. `python reproduce.py`
2. `python audit.py`
3. compare the regenerated receipt with the tracked `receipt.json`
4. build the PDF with `pdflatex -> biber -> pdflatex -> pdflatex`
5. verify no unresolved references/citations and no overfull boxes
6. render every PDF page and inspect for clipping, overlap, or broken glyphs
7. archive the source hash, receipt hash, PDF hash, and Git commit.

## What still requires human judgment

No automated audit establishes literature novelty, philosophical adequacy of an observer measure, or the truth of a simulation hypothesis. Before journal submission, at least one external reader familiar with anthropic reasoning and one reader familiar with statistical latent-variable identifiability should be asked specifically to find counterexamples or prior results that subsume the scoped contribution.
