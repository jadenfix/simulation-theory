# Round 5 adversarial review: measure theory, scope, and release semantics

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Status:** synthetic internal review, not independent peer review.

## Review objective

Round 5 re-derived the seven formal claims after the Round-4 revisions, inspected the GitHub-built PDF rather than a local stale copy, rechecked citation metadata for the most adjacent literature, and looked specifically for claims that are technically true only after choosing a density version, a transcript interface, a cloning semantics, or a novelty interpretation.

The review found **no high-confidence false theorem within the currently stated assumptions**. It did find several scope and publication-quality clarifications that should remain explicit in the machine-readable ledger and final editorial pass.

## Findings, impact, feasibility, and disposition

| ID | Finding | Severity | Impact if applied | Feasible? | Disposition |
|---|---|---|---|---|---|
| R5.1 | In the dominated continuous case, pointwise densities are defined only up to null sets. The persistent-latent density identity should be interpreted for chosen density versions, equivalently almost everywhere under the declared dominating measure. | Moderate measure-theoretic scope | Prevents readers from treating a null-set-dependent density value as an invariant evidential fact. | Yes | **Applied to `claims.json` and audit language; queued for the next prose-only manuscript polish.** |
| R5.2 | For a finite family of component probability laws, a common dominating finite measure always exists, e.g. `lambda = sum_m P_m`. The domination clause is therefore a representation choice, not a substantive restriction on finite mixtures. | Minor clarification | Makes the theorem look neither narrower nor more exotic than it is. | Yes | **Applied to the claim ledger and audit commentary.** |
| R5.3 | The abstract says refinement preserves “every finite shared-latent observation law,” while the displayed proof specializes to conditionally independent views with law `K^{\otimes T}`. The theorem is sound as written, but the abstract should be read under that declared tensor-product experiment unless the theorem is generalized to an arbitrary cloned conditional transcript law. | Moderate scope alignment | Avoids an abstract/proof mismatch. | Yes | **Recorded as an editorial item; no universal theorem is inferred beyond the displayed experiment.** |
| R5.4 | The two-view monomial/permutation conclusion is elementary linear-algebraic rigidity inside the declared gauge. The paper should not imply a priority claim for the algebraic lemma itself. | Moderate novelty control | Reduces novelty inflation while preserving the integrated methodological contribution. | Yes | **Applied to `claims.json` and the novelty audit.** |
| R5.5 | The internal BibTeX key `franceschi2014` no longer matches the publisher issue year `2016`. The rendered citation is correct, but the key can confuse provenance readers. | Minor bibliographic hygiene | Improves repository readability; no effect on the paper’s printed bibliography. | Yes | **Documented, not renamed in this release candidate to avoid a noisy citation-key-only diff.** |
| R5.6 | A journal submission should contain explicit code/materials availability, competing-interests, and funding statements even though the reproducibility section already gives the substance. | Minor publication preparation | Reduces venue-specific editorial friction. | Yes | **Recommended before journal submission; not a mathematical release blocker for a repository preprint.** |
| R5.7 | The author identity must be consistent in manuscript source, PDF metadata, workflow gates, review artifacts, and claims. | Release blocking if violated | Prevents misattribution. | Yes | **Verified: all release-bearing files and the current GitHub-built PDF use `Jaden Fix`.** |
| R5.8 | Reproducibility claims must distinguish byte-stable exact JSON from toolchain-dependent PDF bytes. | Major reproducibility semantics | Prevents an impossible cross-toolchain bit-reproducibility claim. | Yes | **Already applied in Round 4 and reverified in Round 5.** |

## Independent mathematical re-derivation

### Observable equivalence

If `P_B = P_S` on the complete declared transcript sigma-field, every measurable statistic has equal pushforward law. The Radon–Nikodym derivative `dP_S/dP_B` is one `P_B`-almost surely, and equal-prior Bayes classification accuracy is exactly one half. No issue found.

### Representational refinement

For the paper's declared conditional-IID shared-latent experiment, replacing `(w,K)` by `(w_j,K)` with `sum_j w_j=w` changes the contribution from `w K^{\otimes T}` to `sum_j w_j K^{\otimes T}=w K^{\otimes T}`. The result does not cover physical creation of additional observers unless that operation is separately declared measure-neutral. No issue found.

### Rational split additivity

The proof correctly handles zero via `0=0+0`, then obtains `mu(1/n)=1/n` and `mu(p/n)=p/n`. The result is exact on nonnegative rational weights for a local weight-only rule. It is not a uniqueness theorem for all observer measures. No issue found.

### Persistent latent likelihood ratio

For finite component laws with chosen densities `p_m=dP_m/dlambda`, the identity

```text
p_a(y)/p_b(y)
  = sum_m P_b(M=m | y) * a_m/b_m
```

holds wherever the active denominator terms and support condition make the ratios well-defined. The expression is invariant only almost everywhere in the continuous case because density versions may differ on null sets. Under global support inclusion, the likelihood ratio is bounded almost surely by the relevant component weight ratios. The support-mismatch counterexample correctly lies outside the finite-ceiling theorem.

### Known-channel affine identification

The map `pi -> pi K` is injective on the simplex iff the probability rows of `K` are affinely independent. The converse collision construction using an interior prior and a small zero-sum affine dependence is correct. No issue found.

### One-view gauge

For invertible nonnegative row-stochastic `A`, `A 1=1` implies `A^{-1}1=1`; therefore `pi A^{-1}` automatically sums to one, and nonnegativity is the substantive validity condition. `K'=AK` is row-stochastic and `pi'K'=pi K`. The local path `A_t=(1-t)I+tB` is valid for sufficiently small `t` under the stated interiority and nondegeneracy assumptions. No issue found.

### Two-view rigidity

With full-row-rank `K`, a right inverse `R` converts `K^T X K=0` to `X=0`. Positivity of `pi'` and nonnegativity of `A` force every off-diagonal summand in `A^T D_{pi'}A` to vanish separately, so each row has at most one positive entry; row stochasticity and invertibility make `A` a permutation. The proof is correct inside the declared gauge and does not establish unrestricted two-view latent-class identification.

## Citation and artifact checks

Round 5 rechecked the closest bibliographic claims against publisher or primary records where available:

- Bostrom--Kulczycki: *Analysis* 71(1), 54--61, DOI `10.1093/analys/anq107`.
- Fallis--Lewis: *Synthese* 202(6), DOI `10.1007/s11229-023-04413-x`.
- Thomas: online publication 9 December 2024; volume 91, 427--444, issue date 2026.
- Richmond: *Ratio* 30, 221--238; online-first 2016, issue year 2017.
- Khawaja: final BJPS volume 77(2), 313--344 (2026), DOI `10.1086/726282`.
- Franceschi: publisher issue year 2016; some secondary indexes retain a 2014 label, which remains recorded as a discrepancy.

The current GitHub-built release artifact was rendered at 200 DPI and visually inspected across all ten pages. No clipping, overlap, broken glyphs, missing references, or stale author metadata was observed. Both the dedicated paper workflow and the complete Python 3.11/3.12/3.13 repository matrix passed at commit `5674a7f0f59e6670dfbab86008d1e85642651e27`.

## Round-5 decision

**Decision: pass as an internally audited repository preprint candidate, not as externally peer-reviewed work.**

There is no unresolved high-confidence mathematical false positive in the seven scoped claims. The remaining items are editorial precision, venue declarations, and independent external novelty/counterexample review. The paper should remain a draft until a final commit again passes both workflow families and the rebuilt PDF receives a fresh page-by-page visual check.
