# Author response to synthetic peer review

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`

This response accompanies `PEER_REVIEW_LOOP.md`. The referee text is preserved there verbatim. The reports are synthetic internal adversarial reviews, not external endorsements or journal peer review.

## Review protocol

For every comment we record whether it changes mathematical correctness, scope, literature positioning, or reproducibility; whether the requested change is feasible without changing the research question; the disposition; the exact artifact changed; and an independent verification target. A review item is resolved only after its verification target passes. The release condition is zero unresolved major items.

---

# Round 1 response

All substantive Round-1 comments were accepted. The revisions added the declared transcript sigma-field, the persistent-latent support boundary, a formal known-channel affine-rank proposition, explicit gauge assumptions, a dimensionally explicit right-inverse step, the narrow gauge-orbit scope of the two-view theorem, the representational-versus-physical duplication distinction, modern anthropic literature, citation provenance, deterministic receipt regeneration, stronger finite falsification, and a dedicated PDF-building release workflow. The full original referee comments and item-level Round-1 plan remain preserved in `PEER_REVIEW_LOOP.md`.

---

# Round 2 — post-revision adversarial read

## R2.1 — zero case omitted from rational additivity proof
The theorem included `w=0`, while the proof initially treated positive rationals. **Accepted and fixed:** `0=0+0` gives `mu(0)=2mu(0)`, hence `mu(0)=0`.

## R2.2 — avoid formal `0/0` notation in persistent-latent identity
The earlier notation formally ranged over inactive components. **Accepted and fixed:** the theorem defines an active set and sums only over components with positive denominator contribution.

## R2.3 — theorem assumptions do real work
Full row rank, strict transformed-prior positivity, and nonnegativity of `A` are essential to the two-view proof route. **Disposition:** no broadening; assumptions remain explicit.

## R2.4 — citation metadata can fail independently of DOI correctness
Publisher-level checking corrected Richmond and later resolved Franceschi/Khawaja metadata. **Disposition:** bibliography and provenance follow publisher/primary records while preserving secondary discrepancies.

## R2.5 — CI failures should not be papered over
Release engineering exposed phrase-matching, JSON-format, package-name, and typography issues. **Disposition:** artifacts/workflow were fixed rather than weakening gates.

## R2.6 — novelty statement after literature expansion
The component results overlap established literatures. **Disposition:** novelty claims remain limited to the integrated identifiability-first synthesis, boundary examples, and auditable artifact.

**Round-2 disposition:** minor revision. No high-confidence false theorem found within final stated assumptions.

---

# Round 3 — production/release review

## R3.1 — author-metadata edit accidentally truncated manuscript source
A partial file fetch was accidentally used for a whole-file replacement. **Release-blocking.** The exact pre-edit blob was recovered, the complete source restored, and tests now require late sections, bibliography, and `\end{document}`.

## R3.2 — audit documentation diverged from executable build
`AUDIT.md` said Biber and named the wrong provenance file. **Fixed:** documentation now matches BibTeX and `citation_provenance.json`.

## R3.3 — stale author identity across artifacts
The author correction initially existed only in part of the bundle. **Fixed:** release-bearing artifacts are normalized to **Jaden Fix** and tests reject the old name.

## R3.4 — publisher bibliography corrections
Publisher records fixed Franceschi to volume 43(2), 2016 and Khawaja to pages 313--344. **Fixed and pinned in tests.**

---

# Round 4 — probability foundations, novelty, and reproducibility semantics

Round 4 targeted conceptual overreach after the production layer was stable.

## R4.1 — “not estimable before identifiable” was too strong
**Finding:** Bayesian procedures can produce posterior distributions for nonidentified parameters; the actual problem is lack of point-identification from the declared observation law.

**Severity:** important statistical wording correction.  
**Action:** replaced the sentence with: data cannot point-identify a mixture parameter when distinct parameter values induce the same declared observation law.

## R4.2 — pointwise likelihood notation needed a declared representation
**Finding:** Writing `P_m(y)` is naturally valid for discrete transcripts but, for continuous transcripts, a pointwise density requires a common dominating measure. Without that declaration, the theorem mixed mass-function and measure notation.

**Severity:** mathematical scope clarification.  
**Action:** the manuscript now assumes either a discrete transcript or component laws dominated by one common sigma-finite measure, writes `p_m(y)` for mass/density, and records the domination condition in `claims.json`, `README.md`, `AUDIT.md`, and the limitations section. The observable-equivalence theorem was also upgraded to the representation-free Radon--Nikodym statement `dP_S/dP_B=1` almost surely.

## R4.3 — local “continuous gauge” claim needed a constructive argument
**Finding:** the pointwise gauge proposition did not by itself prove that a nontrivial continuum of valid factorizations exists around every intended example.

**Severity:** scope/proof-support issue.  
**Action:** the manuscript now explicitly constructs `A_t=(1-t)I+tB` for a strictly positive prior and a channel with at least two distinct rows, choosing a row-stochastic `B` with `BK != K`. For sufficiently small positive `t`, invertibility and transformed-prior positivity follow by continuity.

## R4.4 — transformed prior normalization can be stated more sharply
**Finding:** if `A` is invertible and row-stochastic, `A 1=1` implies `A^{-1}1=1`; therefore `pi A^{-1}` automatically sums to one. Nonnegativity, not normalization, is the substantive validity condition.

**Action:** proof and audit wording corrected.

## R4.5 — directly adjacent simulation literature was missing
**Finding:** Bostrom--Kulczycki (2011) explicitly patches a mathematical non sequitur in the original simulation argument, and Fallis--Lewis (2023) directly analyzes simulation as self-location. Both are close to this paper's methodological thesis.

**Severity:** major literature-positioning issue.  
**Action:** both were publisher-verified, added to the bibliography/provenance ledger, and engaged in the introduction/related-work discussion.

## R4.6 — exact receipt reproducibility differs from PDF reproducibility
**Finding:** the exact rational JSON receipt can and should be byte-identical. A PDF generated by TeX may contain version/timestamp-dependent bytes, so demanding cross-environment byte identity would overstate reproducibility.

**Severity:** reproducibility semantics.  
**Action:** CI now records Python/pdfTeX/BibTeX/Poppler and runner provenance in `toolchain.txt`, hashes the release-specific PDF, and continues to require byte-identical regeneration only for `receipt.json`.

**Round-4 disposition:** minor-to-moderate revision. All six findings were feasible and applied. No new substantive simulation-theory claim was introduced.

---

# Release checklist

The release remains fail-closed. On one final commit it must satisfy:

- [ ] paper-specific tests and exact receipt regeneration;
- [ ] ordinary Python 3.11/3.12/3.13 repository CI;
- [ ] full LaTeX/BibTeX build;
- [ ] zero unresolved citations/references and zero overfull boxes;
- [ ] correct title/author PDF metadata;
- [ ] toolchain provenance and release hashes;
- [ ] uploaded release-candidate artifact;
- [ ] fresh human visual inspection of every page;
- [ ] zero unresolved GitHub review threads;
- [ ] zero unresolved major synthetic-review findings.

Until every item holds on the same final commit, the paper remains a release candidate rather than a frozen preprint.

---

# External-review boundary

This loop is rigorous but internal and synthetic. It must not be described as journal peer review or independent expert validation. Before journal submission, the recommended next step remains one adversarial read from a specialist in anthropic/self-locating inference and one from a specialist in finite-mixture or latent-variable identifiability. Their comments should be appended as a clearly labeled external-review round rather than overwriting this audit history.
