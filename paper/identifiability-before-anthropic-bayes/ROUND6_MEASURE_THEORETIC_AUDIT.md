# Round 6 adversarial review: measure theory, theorem scope, and release semantics

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Status:** synthetic internal review, not independent peer review.

## Review objective

Round 6 independently re-derived the seven formal claims after the Round-5 revisions. It targeted issues that often survive algebraic checking: density-version dependence, mismatch between abstract and theorem scope, hidden conditional-independence assumptions, priority inflation, and release claims that are stronger than the artifacts actually support.

The review found **no high-confidence false theorem within the currently stated assumptions**. It found several clarifications that materially reduce false-positive interpretations and should remain pinned in the claim ledger and release tests.

## Findings, impact, feasibility, and disposition

| ID | Finding | Severity | Impact if applied | Feasible? | Disposition |
|---|---|---|---|---|---|
| R6.1 | In the dominated continuous case, pointwise densities are defined only up to null sets. The persistent-latent density identity is therefore a statement for chosen Radon--Nikodym versions, equivalently almost everywhere under the declared dominating measure. | Moderate mathematical scope | Prevents a null-set-dependent density value from being treated as invariant evidence. | Yes | **Applied to `claims.json`; manuscript wording remains explicitly dominated and is interpreted almost everywhere.** |
| R6.2 | For a finite family of component probability laws, a common dominating finite measure always exists, for example `lambda = sum_m P_m`. Domination is therefore a representation device, not an additional empirical restriction on finite mixtures. | Minor clarification | Makes the theorem neither artificially narrow nor mysterious. | Yes | **Applied to `claims.json` and audit documentation.** |
| R6.3 | The refinement proof uses `K^{\otimes T}` and therefore establishes the displayed finite-view result for conditionally independent same-channel observations sharing one latent component. | Moderate abstract/proof alignment | Prevents readers from inferring a tensor-product result for arbitrary dependent or view-specific observation processes. | Yes | **Applied to the claim ledger and manuscript scope tests.** |
| R6.4 | The permutation conclusion in the repeated-view theorem is elementary rigidity inside the declared row-stochastic gauge. The paper should not imply an independent priority claim for the algebraic monomiality step. | Moderate novelty control | Preserves the integrated contribution while reducing novelty inflation. | Yes | **Applied to `claims.json` and the novelty audit.** |
| R6.5 | The internal BibTeX key `franceschi2014` no longer matches the publisher issue year 2016. The printed record is correct; renaming the key would be repository hygiene rather than a scholarly correction. | Minor bibliographic hygiene | Reduces possible provenance confusion. | Yes | **Documented but not renamed in this release candidate to avoid a citation-key-only migration.** |
| R6.6 | Journal submission usually requires explicit code/materials availability, funding, and competing-interest declarations. These require author-confirmed facts and should not be fabricated by the audit process. | Minor publication preparation | Avoids unsupported disclosures while identifying a real submission task. | Yes, with author confirmation | **Deferred to venue preparation; not a mathematical preprint blocker.** |
| R6.7 | The author identity must be consistent across source, PDF metadata, workflow gates, review artifacts, and claim ledger. | Release blocking if violated | Prevents misattribution. | Yes | **Verified as `Jaden Fix` in all release-bearing files and the GitHub-built PDF.** |
| R6.8 | Exact-rational JSON can be byte-stable; TeX-generated PDF bytes can vary across toolchains and timestamps. | Major reproducibility semantics | Prevents an impossible cross-toolchain bit-reproducibility claim. | Yes | **Already applied and reverified: the receipt is byte-identical, while the PDF is release-hashed with toolchain provenance.** |

## Independent mathematical re-derivation

### Observable equivalence

If `P_B=P_S` on the complete declared transcript sigma-field, every measurable statistic has the same pushforward law. The Radon--Nikodym derivative `dP_S/dP_B` is one `P_B`-almost surely, and equal-prior optimal classification accuracy is exactly one half. No issue found.

### Representational refinement

For the declared conditional-IID same-channel shared-latent experiment, replacing `(w,K)` by `(w_j,K)` with `sum_j w_j=w` changes the component contribution from `w K^{\otimes T}` to `sum_j w_j K^{\otimes T}=w K^{\otimes T}`. This does not cover physical creation of additional observers unless that operation is separately declared measure-neutral. No issue found.

### Rational split additivity

The proof correctly derives `mu(0)=0`, then `mu(1/n)=1/n`, and finally `mu(p/n)=p/n`. The theorem is exact for a local rule on nonnegative rational weights and is not a uniqueness theorem for observer measures that use additional structure. No issue found.

### Persistent latent likelihood ratio

For finite component laws and a common dominating measure, the density identity

```text
p_a(y)/p_b(y)
  = sum_m P_b(M=m | y) * a_m/b_m
```

holds almost everywhere wherever the active denominator terms and support condition make the component ratios well-defined. Under global support inclusion, the likelihood ratio is bounded almost surely by the relevant component weight ratios. The support-mismatch counterexample correctly lies outside the finite-ceiling theorem. No issue found.

### Known-channel affine identification

The map `pi -> pi K` is injective on the complete latent simplex exactly when the probability rows of `K` are affinely independent. The converse collision construction from a nonzero zero-sum affine dependence and an interior prior is correct. No issue found.

### One-view gauge

For invertible nonnegative row-stochastic `A`, `A 1=1` implies `A^{-1}1=1`; therefore `pi A^{-1}` automatically sums to one, and nonnegativity is the substantive validity condition. `K'=AK` is row-stochastic and `pi'K'=pi K`. The path `A_t=(1-t)I+tB` yields a genuine local continuum under the manuscript's interiority and nondegeneracy assumptions. No issue found.

### Same-channel repeated-view rigidity

Full row rank supplies a right inverse converting `K^T X K=0` to `X=0`. Strict positivity of `pi'` and nonnegativity of `A` force every off-diagonal summand in `A^T D_{pi'}A` to vanish separately. Each row of `A` therefore has at most one positive entry; row stochasticity and invertibility make `A` a permutation. The proof is correct inside the declared same-channel gauge and does not establish arbitrary multiview latent-class identification.

## Artifact and citation checks

Round 6 rechecked the closest release claims and current artifacts:

- the author is `Jaden Fix` in source, claims, workflow, review artifacts, and PDF metadata;
- the paper-specific and complete Python 3.11/3.12/3.13 workflow families have previously passed on one audited commit;
- the GitHub-built ten-page PDF was rendered at 200 DPI and visually inspected without clipping, overlap, broken glyphs, unresolved references, or stale metadata;
- publisher-level corrections for Richmond, Franceschi, Fallis--Lewis, Thomas, Bostrom--Kulczycki, and Khawaja remain preserved in the bibliography/provenance ledger;
- the synthetic reviews remain labeled internal and are not represented as journal peer review.

## Round-6 decision

**Decision: pass the mathematics as an internally audited repository preprint candidate, subject to a fresh final-commit CI and PDF inspection.**

There is no unresolved high-confidence mathematical false positive in the seven scoped claims. Remaining tasks are editorial declarations requiring author-confirmed facts, independent external novelty/counterexample review, and a final fail-closed release run on the exact commit proposed for freezing.
