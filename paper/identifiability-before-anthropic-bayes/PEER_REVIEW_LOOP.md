# Synthetic peer-review loop

**Paper:** *Identifiability Before Anthropic Bayes: Representation Invariance, Persistent Latents, and Observable Equivalence in Simulation Arguments*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Purpose:** internal adversarial review before external circulation. These are simulated referee reports, not external endorsements.

**Preservation note:** the referee comments below are preserved as originally written. Only administrative author metadata has been corrected.

The loop is intentionally fail-closed: comments are preserved even when rejected; every comment receives a severity, expected impact, feasibility assessment, disposition, and post-change verification target.

---

# Round 1 — independent referee reports

## Referee A — statistics / latent-variable identifiability

### A1 — State the sigma-field/interface in the observable-equivalence result
**Severity:** minor but important scope guard.  
**Comment:** The statement that no classifier can distinguish the hypotheses should explicitly say that the classifier is measurable with respect to the declared allowed transcript. Otherwise the sentence can be read as claiming metaphysical indistinguishability rather than statistical indistinguishability under a fixed experiment.

**Impact if applied:** improves theorem precision; no mathematical change.  
**Feasibility:** immediate.  
**Disposition:** ACCEPT.

### A2 — Strengthen the support statement in the persistent-latent likelihood-ratio theorem
**Severity:** major boundary condition.  
**Comment:** The convex-combination identity is clean only when the denominator component weights are positive on every component that can contribute to the realized numerator likelihood. The paper should distinguish (i) a finite ratio under common component support from (ii) support mismatch, where the Bayes factor can be infinite. The latter is not a counterexample; it is outside the theorem.

**Impact if applied:** prevents a genuine false-positive interpretation of the likelihood-ratio ceiling.  
**Feasibility:** immediate; add an explicit corollary/counterexample.  
**Disposition:** ACCEPT.

### A3 — Promote known-channel affine-rank identifiability from prose to a proved proposition
**Severity:** major exposition/proof completeness issue.  
**Comment:** The paper currently says that the latent prior is identifiable given known channel `K` iff channel rows are affinely independent, but does not prove it. Since later factorization claims depend on distinguishing conditional from joint identifiability, this result deserves a formal proposition and proof.

**Impact if applied:** closes a logical gap and makes the conditional-vs-joint distinction auditable.  
**Feasibility:** high; elementary finite-dimensional linear algebra.  
**Disposition:** ACCEPT.

### A4 — Clarify the one-view gauge assumptions
**Severity:** major scope guard.  
**Comment:** `A` being invertible and row-stochastic does not imply `pi A^{-1}` is a probability vector. The manuscript already mentions validity, but the condition should be visually prominent and the result should be presented as a constructive family of nonidentifiabilities, not as a classification of all stochastic factorizations.

**Impact if applied:** prevents overclaiming.  
**Feasibility:** immediate.  
**Disposition:** ACCEPT.

### A5 — Expand the two-view proof step that cancels `K`
**Severity:** moderate proof readability issue.  
**Comment:** The proof says “a right inverse” but does not show the multiplication. For readers checking dimensions, explicitly let `R` satisfy `KR=I` and multiply `K^T X K=0` by `R^T` and `R` to obtain `X=0`.

**Impact if applied:** removes an avoidable proof-audit stumbling block.  
**Feasibility:** immediate.  
**Disposition:** ACCEPT.

### A6 — Do not advertise the two-view theorem as generic latent-class identifiability
**Severity:** major novelty/scope issue.  
**Comment:** Two-view identification is delicate in general latent models. The actual theorem is narrower and cleaner: within the declared nonnegative row-stochastic gauge orbit, preservation of the two-view shared-latent law forces a permutation under full-row-rank and positive-prior assumptions. State that in the theorem title, abstract, novelty paragraph, and conclusion.

**Impact if applied:** materially improves correctness of the novelty claim.  
**Feasibility:** immediate.  
**Disposition:** ACCEPT.

---

## Referee B — philosophy of probability / anthropic reasoning

### B1 — Distinguish representational cloning from physically adding observers
**Severity:** major conceptual issue.  
**Comment:** The clone-counting example is strong only if the operation is explicitly a redescription of one measure-bearing state, not the creation of additional conscious observers or observer-moments. Otherwise a defender of counting can correctly reply that physical duplication should change measure.

**Impact if applied:** turns a potentially misleading example into a clean invariance test.  
**Feasibility:** immediate; define “observational refinement” and “physical duplication” separately.  
**Disposition:** ACCEPT.

### B2 — Avoid presenting the hierarchy as a replacement for all self-locating theories
**Severity:** moderate scope issue.  
**Comment:** SSA, SIA, FNC, reference-class approaches, and other anthropic frameworks disagree about how self-location should be represented. The paper’s contribution is a set of preconditions any numerical scheme must make explicit, not a proof that one self-locating framework is uniquely correct.

**Impact if applied:** broadens relevance while reducing philosophical overclaim.  
**Feasibility:** high; add a paragraph and cite Neal plus existing reference-class literature.  
**Disposition:** ACCEPT.

### B3 — Engage modern Bayesian simulation-argument work directly
**Severity:** major literature-positioning issue.  
**Comment:** The paper should compare its “identifiability before Bayes” thesis with Kipping’s model-uncertainty treatment and Thomas’s Simulation Expectation. The manuscript should explain that model averaging still presupposes identifiable/stipulated likelihood-bearing models and a defined sampling unit.

**Impact if applied:** materially improves novelty positioning and reduces straw-man risk.  
**Feasibility:** high.  
**Disposition:** ACCEPT.

### B4 — Add subjectively identical/anomalous-observer literature
**Severity:** moderate literature issue.  
**Comment:** The refinement argument is adjacent to the problem of subjectively indistinguishable or anomalous observers, including simulations/replays/records. The paper should cite this connection while making clear that its refinement theorem is a formal representation test rather than a theory of consciousness.

**Impact if applied:** strengthens contextual authenticity.  
**Feasibility:** high.  
**Disposition:** ACCEPT.

### B5 — Soften “central result” language
**Severity:** minor rhetoric issue.  
**Comment:** The sequence `observation model -> representation/measure -> sampling hierarchy -> identifiability -> Bayesian update` is a framework/synthesis, not one theorem. Call it the paper’s “organizing principle” or “audit order.”

**Impact if applied:** improves scholarly tone.  
**Feasibility:** immediate.  
**Disposition:** ACCEPT.

---

## Referee C — reproducibility / scholarly provenance

### C1 — General repository CI is insufficient for a paper release
**Severity:** major reproducibility issue.  
**Comment:** A release candidate should compile the manuscript in CI, verify that bibliography references resolve, run the exact reproduction suite, compare the generated receipt to the tracked receipt, and upload the PDF as an artifact.

**Impact if applied:** makes the public repository reproduce the paper end to end.  
**Feasibility:** high if TeX is available through a standard action/container.  
**Disposition:** ACCEPT, with a dedicated paper workflow.

### C2 — Preserve citation provenance, not just BibTeX
**Severity:** major authenticity issue.  
**Comment:** A DOI-bearing `.bib` file can still contain wrong year/issue/page metadata. Add a machine-readable provenance file recording the source used to verify each central citation and whether metadata is publisher-verified, repository-verified, or preprint-only.

**Impact if applied:** catches exactly the sort of Richmond/Franceschi metadata errors already discovered during audit.  
**Feasibility:** high.  
**Disposition:** ACCEPT.

### C3 — Receipt generation must be byte-for-byte deterministic
**Severity:** major reproducibility issue.  
**Comment:** `reproduce.py` and `receipt.json` must agree exactly. Include a canonical payload hash inside the receipt and test regeneration in a temporary directory or compare after regeneration.

**Impact if applied:** converts examples from “code that usually runs” into a stable audit object.  
**Feasibility:** high.  
**Disposition:** ACCEPT.

### C4 — Strengthen finite falsification around the two-view theorem
**Severity:** moderate audit issue.  
**Comment:** The 2-state denominator-4 grid is useful but narrow. Add at least one 3-state exhaustive rational grid and record the number of admissible transformations and preserving transformations. This remains a finite audit, not proof.

**Impact if applied:** significantly improves confidence against implementation/sign mistakes.  
**Feasibility:** high; the bounded grid is small.  
**Disposition:** ACCEPT.

### C5 — Include negative/boundary tests, not only successful examples
**Severity:** major falsification issue.  
**Comment:** Reproduction should include at least: support mismatch for the persistent theorem; affine-rank failure with two distinct priors producing the same observed law; an invalid gauge whose transformed prior exits the simplex; and a note that removing positivity/full-rank assumptions invalidates the two-view proof.

**Impact if applied:** high; directly targets false positives.  
**Feasibility:** high.  
**Disposition:** ACCEPT.

### C6 — The PDF itself should be audited as an artifact
**Severity:** moderate publication issue.  
**Comment:** Record page count, unresolved-reference checks, overfull-box checks, PDF metadata, source/receipt/PDF hashes, and a human visual-inspection checklist. Automated checks do not replace visual inspection.

**Impact if applied:** makes “publication ready” auditable rather than aesthetic assertion.  
**Feasibility:** high locally; most checks can be CI-enforced.  
**Disposition:** ACCEPT.

---

# Round 1 impact summary

| ID | Severity | Expected impact | Feasible? | Decision |
|---|---|---|---|---|
| A1 | Minor | scope precision | Yes | Apply |
| A2 | Major | theorem boundary correctness | Yes | Apply |
| A3 | Major | closes proof gap | Yes | Apply |
| A4 | Major | prevents factorization overclaim | Yes | Apply |
| A5 | Moderate | proof auditability | Yes | Apply |
| A6 | Major | novelty/scope correctness | Yes | Apply |
| B1 | Major | removes physical-vs-representational ambiguity | Yes | Apply |
| B2 | Moderate | anthropic scope correctness | Yes | Apply |
| B3 | Major | literature positioning | Yes | Apply |
| B4 | Moderate | literature authenticity | Yes | Apply |
| B5 | Minor | scholarly tone | Yes | Apply |
| C1 | Major | end-to-end reproducibility | Yes | Apply |
| C2 | Major | citation authenticity | Yes | Apply |
| C3 | Major | deterministic receipt | Yes | Apply |
| C4 | Moderate | stronger finite falsification | Yes | Apply |
| C5 | Major | false-positive resistance | Yes | Apply |
| C6 | Moderate | publication artifact integrity | Yes | Apply |

**Round-1 editor decision:** major revision, with every substantive comment feasible and accepted.

---

# Response / implementation ledger

This is the frozen Round-1 planning ledger. Final dispositions, post-revision findings, and production incidents are recorded in `PEER_REVIEW_RESPONSE.md`.

| ID | Planned change | Verification target | Status at Round-1 freeze |
|---|---|---|---|
| A1 | qualify classifier/statistic by declared transcript sigma-field | theorem text + claims ledger | pending |
| A2 | explicit common-support assumption and support-mismatch example | proof + reproduction boundary test | pending |
| A3 | formal known-channel affine-rank proposition and proof | manuscript theorem + exact collision witness | pending |
| A4 | emphasize transformed-prior validity and constructive-not-exhaustive gauge claim | proposition/nonclaims | pending |
| A5 | write right-inverse cancellation step dimensionally | proof text | pending |
| A6 | repeat gauge-orbit scope in abstract/theorem/conclusion | manuscript + claims ledger | pending |
| B1 | distinguish redescription/refinement from physical duplication | definitions + discussion | pending |
| B2 | explicitly treat SSA/SIA/FNC/etc. as downstream choices | related work/scope | pending |
| B3 | add Kipping and deepen Thomas comparison | bibliography + related work | pending |
| B4 | add anomalous/subjectively identical observer connection | bibliography + discussion | pending |
| B5 | replace “central result” rhetoric with “organizing audit order” | conclusion | pending |
| C1 | add dedicated paper CI build and PDF artifact | GitHub Actions green | pending |
| C2 | add citation provenance JSON | provenance audit script | pending |
| C3 | canonical receipt hash and byte-for-byte regeneration check | paper-specific test | pending |
| C4 | add exact 3-state finite rational two-view audit | receipt + tests | pending |
| C5 | add negative/boundary falsification cases | receipt + tests | pending |
| C6 | add PDF preflight + visual inspection checklist + hashes | release audit record | pending |

---

# Round 2 — to be performed after Round-1 revisions

Round 2 must not introduce a new research direction. It asks only:

1. Did any accepted Round-1 revision create a new mathematical ambiguity?
2. Are any theorem statements stronger than their proofs?
3. Are any examples being presented as evidence rather than diagnostics?
4. Do citation claims match what cited sources actually establish?
5. Can a clean checkout reproduce the receipt and PDF?
6. Are there any unresolved major-review comments?

The release gate is **zero unresolved major comments**. Minor stylistic issues may remain only if explicitly documented as non-substantive.
