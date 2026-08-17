# Author response to synthetic peer review

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`

This response accompanies `PEER_REVIEW_LOOP.md`. The referee text is preserved there verbatim. The reports are synthetic internal adversarial reviews, not external endorsements or journal peer review.

## Review protocol

For every comment we record:

1. whether it changes mathematical correctness, scope, literature positioning, or reproducibility;
2. whether the requested change is feasible without changing the research question;
3. whether the change is accepted, modified, or rejected;
4. the exact artifact changed;
5. an independent verification target.

A review item is considered resolved only after its verification target passes. The release condition is zero unresolved major items.

---

# Round 1 response

| ID | Impact | Feasible | Action taken | Verification |
|---|---|---:|---|---|
| A1 | Scope precision | Yes | Added declared transcript sigma-field `F_Y`; theorem and classifier are explicitly interface-relative. | Manuscript scope-guard test. |
| A2 | Theorem boundary correctness | Yes | Added component-level absolute-continuity assumption and explicit support-mismatch remark/counterexample. | `claims.json`; exact negative test in `receipt.json`. |
| A3 | Proof completeness | Yes | Promoted known-channel affine-rank identifiability to a formal proposition with both directions proved. | Analytic proof plus rank-deficient exact collision witness. |
| A4 | Factorization scope | Yes | Made transformed-prior validity explicit and described the gauge as constructive, not exhaustive. | Claim nonclaims plus invalid-prior exact example. |
| A5 | Proof readability | Yes | Introduced right inverse `R`, wrote `KR=I`, and performed the cancellation `R^T K^T X K R=X`. | Manuscript proof inspection. |
| A6 | Novelty/scope correctness | Yes | Repeated “inside the row-stochastic gauge” scope in abstract, theorem, discussion, claim ledger, and limitations. | Scope-guard test. |
| B1 | Conceptual correctness | Yes | Defined observational refinement as redescription and separated it from physical creation of additional measure-bearing observers. | Manuscript definition + limitations. |
| B2 | Anthropic scope | Yes | Explicitly stated that the framework does not select SSA/SIA/FNC; added Neal/FNC discussion. | Manuscript related-work section. |
| B3 | Literature positioning | Yes | Added Kipping and deepened Thomas comparison; framed the paper as complementary to Bayesian simulation analyses. | Bibliography + citation provenance. |
| B4 | Contextual authenticity | Yes | Added Schneider--Olum subjectively-identical/anomalous-observer connection. | Bibliography + representation section. |
| B5 | Scholarly tone | Yes | Replaced “central result” rhetoric with “organizing audit order/principle.” | Manuscript text test. |
| C1 | End-to-end reproducibility | Yes | Added dedicated `paper-identifiability` workflow: tests, exact receipt, TeX build, reference checks, PDF preflight, hashes, artifact upload. | GitHub Actions release gate. |
| C2 | Citation authenticity | Yes | Added `citation_provenance.json`; corrected bibliography metadata against publisher/primary records and preserved secondary-index discrepancies. | Provenance test + bibliography audit. |
| C3 | Deterministic artifact | Yes | Receipt now contains canonical payload SHA-256 and must regenerate byte-for-byte. | Paper-specific test + clean-diff CI step. |
| C4 | Stronger finite falsification | Yes | Increased two-state grid to denominator 8 and added exhaustive three-state denominator-3 audit. | Exact receipt: 32/2 and 108/6 admissible/preserving counts. |
| C5 | False-positive resistance | Yes | Added support mismatch, rank-deficient prior collision, invalid transformed prior, and theorem-assumption boundary documentation. | Reproduction suite. |
| C6 | Publication artifact integrity | Yes | Added PDF metadata, undefined-reference, overfull-box, release-hash, artifact-upload gates; human visual check remains explicitly separate. | Paper workflow plus manual release checklist. |

**Round-1 disposition:** all substantive comments accepted. The paper changed materially in scope precision, proof completeness, literature positioning, and reproducibility.

---

# Round 2 — post-revision adversarial read

Round 2 did not seek new research claims. It tried to falsify the revised theorem statements and proof boundaries.

## R2.1 — zero case omitted from rational additivity proof

**Finding:** The theorem's domain included `w=0`, while the written proof explicitly handled only positive rational `p/n`.

**Severity:** minor proof-completeness issue.  
**Impact:** no change to theorem truth, but a literal proof gap.  
**Feasible:** yes.  
**Action:** ACCEPTED and applied. The proof now begins from `0=0+0`, yielding `mu(0)=2mu(0)` and hence `mu(0)=0`, before treating positive rationals.

## R2.2 — avoid formal `0/0` notation in persistent-latent identity

**Finding:** The support condition made the result correct, but the earlier notation summed over all components and treated inactive terms as zero by convention.

**Severity:** minor notation/proof-audit issue.  
**Impact:** removes an unnecessary formal ambiguity.  
**Feasible:** yes.  
**Action:** ACCEPTED and applied. The theorem now defines

`I_b(y) = {m : b_m P_m(y) > 0}`

and sums only over `I_b(y)`. The support condition guarantees every nonzero numerator contribution is in that set.

## R2.3 — verify theorem assumptions are doing real work

**Finding:** The two-view proof uses full row rank to obtain a right inverse, strict positivity to turn a zero sum of nonnegative terms into termwise zeros, and nonnegativity of `A` to prevent cancellation. Removing these assumptions invalidates the proof route.

**Severity:** important scope confirmation, not an error.  
**Action:** no theorem broadening. The assumptions remain prominent in theorem, claim ledger, audit, and limitations.

## R2.4 — citation metadata can fail independently of DOI correctness

**Finding:** Bibliographic metadata errors survived valid DOI fields. Richmond's issue/pages were corrected; the publisher archive for *Philosophiques* places Franceschi's volume 43 issue 2 in 2016 despite some secondary indexes using 2014; the final BJPS record for Khawaja supplies pages 313--344.

**Severity:** major scholarly-provenance issue.  
**Action:** bibliography and `citation_provenance.json` now follow publisher/primary records while explicitly preserving secondary discrepancies.

## R2.5 — CI failures should not be papered over

**Finding:** The new release gate exposed non-mathematical contract defects during iteration: an overly literal test phrase, non-byte-identical JSON formatting despite equal values, and a nonexistent Ubuntu package name.

**Severity:** reproducibility engineering.  
**Action:** fixes were made to the artifacts/workflow rather than weakening the release criteria. The receipt is byte-identical to its generator, the scope test checks semantic containment, and the TeX install uses valid Ubuntu packages.

## R2.6 — novelty statement after literature expansion

**Finding:** The component theorems overlap substantially with established probability, anthropic, finite-mixture, multiview, and NMF literatures.

**Severity:** major publication-positioning issue.  
**Action:** the manuscript explicitly does **not** claim novelty for finite additivity, known-channel affine-rank identification, generic factorization ambiguity, or generic multiview identification. The claimed contribution is the integrated identifiability-first audit framework for simulation-style anthropic Bayes plus its boundary examples and auditable artifact.

**Round-2 disposition:** minor revision. No high-confidence false theorem found inside the final stated assumptions. Two proof/notation issues were found and fixed. No new mathematical claim was added merely to answer review.

---

# Round 3 — production/release review

Round 3 is mechanical and adversarial rather than conceptual. Production failures are recorded as audit evidence rather than hidden.

## R3.1 — author-metadata edit accidentally truncated the manuscript source

**Finding:** An author-name correction was initially made from a partial file fetch. Because the repository write API replaces the whole file, that edit truncated the manuscript after the beginning of the two-view section.

**Severity:** release-blocking source-integrity defect.  
**Impact:** a release built from that commit would have been incomplete even though the intended mathematical revision was only metadata.  
**Action:** the exact pre-edit full manuscript blob was recovered by content SHA, restored in full, and then the author was changed to `Jaden Fix`. The release gate now checks author metadata and the paper tests check the presence of late-manuscript sections so a future truncation cannot silently pass.

## R3.2 — audit documentation diverged from the executable build

**Finding:** `AUDIT.md` described Biber while the workflow actually used BibTeX, and named `citation_audit.json` although the tracked file is `citation_provenance.json`.

**Severity:** reproducibility-documentation defect.  
**Action:** the audit contract was aligned to the executable workflow and actual provenance filename.

## R3.3 — author identity was stale in multiple release artifacts

**Finding:** manuscript metadata was corrected to Jaden Fix while README, claim/review metadata, workflow assertions, and PR text still contained the previous name.

**Severity:** publication-integrity defect.  
**Action:** the bundle is being normalized to `Jaden Fix`; tests reject stale author metadata in release-bearing artifacts.

## R3.4 — primary-source bibliography pass changed final metadata

**Finding:** publisher-level records resolved or sharpened metadata that secondary indexes had obscured: Franceschi's issue year is 2016 in the Érudit archive and Khawaja's final BJPS pages are 313--344.

**Severity:** scholarly-provenance correction.  
**Action:** bibliography and provenance ledger updated; future tests assert these resolved fields.

## Round-3 release checklist

Round 3 is complete only when all of the following are true on the same final commit:

- [ ] paper-specific Python tests pass;
- [ ] `reproduce.py` regenerates `receipt.json` byte-for-byte;
- [ ] ordinary repository CI passes;
- [ ] full LaTeX/BibTeX build succeeds;
- [ ] no unresolved citations/references;
- [ ] no overfull boxes;
- [ ] PDF title and author metadata are correct;
- [ ] source, provenance, receipt, review/audit, and PDF hashes are produced;
- [ ] GitHub Actions uploads the release-candidate PDF artifact;
- [ ] current final PDF receives human visual inspection;
- [ ] PR has no unresolved review threads;
- [ ] zero unresolved major synthetic-review comments.

Until every box is checked on the same commit, the paper remains a release candidate rather than a frozen preprint.

---

# External-review boundary

This loop is intentionally rigorous but it is still an internal synthetic review. It must not be described as journal peer review or independent expert validation. Before external journal submission, the recommended next step is one adversarial read from a specialist in anthropic/self-locating inference and one from a specialist in finite-mixture or latent-variable identifiability. Their comments should be appended as a new, clearly labeled external-review round rather than overwritten.
