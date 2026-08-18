# Round 9 — contemporaneous prior art and self-location scope audit

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Status:** synthetic internal review, not independent peer review.

## Review objective

Round 9 attacked the self-location extension after the xerographic-distribution correction. The review targeted three failure modes that can survive otherwise correct algebra:

1. a corollary stated more broadly than its likelihood assumptions permit;
2. language that accidentally reifies a physical random selector after warning against the selection fallacy;
3. conceptual novelty inflation relative to a very recent independent observer-measure manuscript.

The round found **no false core theorem**, but it found one real scope ambiguity and one material novelty-positioning omission. Both were feasible to fix and were applied.

## Findings, impact, feasibility, and disposition

| ID | Finding | Severity | Impact if applied | Feasible? | Disposition |
|---|---|---|---|---|---|
| R9.1 | The nonuniform-kernel statement in Proposition T8 could be read as saying within-world odds always equal `s(F|w)/s(G|w)`. That is false when the evidence likelihood varies across candidate centers. The mass-ratio corollary requires the same fixed-world, nondiscriminating-evidence condition as the uniform count-ratio corollary. | **Major theorem-scope ambiguity** | Prevents a correct Bayes decomposition from being overread as a likelihood-free calibration theorem. | Yes | **Applied.** The proposition, proof, limitations, and claim ledger now state the constant-likelihood/positive-denominator condition explicitly. |
| R9.2 | Repeated use of “sampling kernel” can sound like a literal physical selector, despite the manuscript's explicit use of Hartle--Srednicki's selection-fallacy warning. | Moderate conceptual scope | Keeps a centered credence rule distinct from a causal data-generating sampler. | Yes | **Applied.** The manuscript now prefers “self-location kernel” or “conditional kernel” and describes changes as changes in the self-location rule. |
| R9.3 | Tomoyuki Uchida's June-2026 manuscript *The Measure Problem for Observers: Probability, Typicality, and Self-Location Without a Global Sampler* independently develops a closely overlapping measure-specification thesis: observer measure, self-location, probability-role separation, and rejection of an implicit global sampler must be stated explicitly. The bibliography already contained the work but the manuscript did not cite or engage it. | **Major novelty-positioning correction** | Omitting the closest contemporaneous conceptual overlap could make the integrated-framework novelty claim look insufficiently researched. | Yes | **Applied.** The introduction, contribution statement, self-location section, relation-to-literature section, limitations, and claim ledger now cite and distinguish Uchida. |
| R9.4 | Uchida's manuscript is recent and non-peer-reviewed. It should constrain novelty positioning without being used as authority for the paper's mathematical theorems. | Moderate provenance scope | Avoids replacing one literature problem with another by treating a contemporaneous manuscript as settled doctrine. | Yes | **Already satisfied and reverified.** `citation_provenance.json` marks the source as primary-repository verified and non-peer-reviewed. |
| R9.5 | The self-location odds formula needs an explicit positive denominator. The phrase “positive denominator probability” is less precise than `P(G,e)>0`. | Minor mathematical hygiene | Removes ambiguity at a zero-denominator boundary. | Yes | **Applied.** The proposition now states `P(G,e)>0`, and the mass-ratio corollary requires positive denominator mass. |

## Independent re-derivation of the self-location corollaries

Let

```text
P(w,c,e) = rho(w) s(c|w) L(e|w,c).
```

For disjoint centered categories `F` and `G`, summing gives

```text
P(F,e) = sum_w rho(w) sum_{c in F_w} s(c|w)L(e|w,c)
P(G,e) = sum_w rho(w) sum_{c in G_w} s(c|w)L(e|w,c).
```

Whenever `P(G,e)>0`, their ratio is exactly the posterior odds `P(F|e)/P(G|e)`.

### Uniform count calibration

Fix a world `w`, let `s(c|w)=1/|C_w|`, and suppose `L(e|w,c)=ell_w(e)` for every candidate center in the declared class. Then

```text
P(F,e|w) / P(G,e|w)
  = [|F_w| ell_w(e)/|C_w|] / [|G_w| ell_w(e)/|C_w|]
  = |F_w|/|G_w|.
```

The likelihood-constancy assumption is essential.

### Nonuniform mass calibration

Under the same fixed-world and constant-likelihood condition,

```text
P(F,e|w) / P(G,e|w)
  = s(F_w|w) / s(G_w|w),
```

provided `s(G_w|w)>0`.

Without constant likelihood, the correct expression is the likelihood-weighted mass ratio

```text
[sum_{c in F_w} s(c|w)L(e|w,c)] /
[sum_{c in G_w} s(c|w)L(e|w,c)],
```

not the bare kernel-mass ratio. This was the substantive scope correction in R9.1.

### Representation refinement

If one centered possibility is replaced by observationally identical clones with the same evidence likelihood and self-location masses summing to the parent's mass, the relevant joint-mass term is unchanged. Re-uniformizing over the enlarged label set instead changes `s`; it is a model change, not an evidence update.

## Primary-source literature check

Round 9 rechecked the closest sources rather than relying only on secondary summaries.

- **Srednicki and Hartle (2010/2013)** explicitly define a xerographic distribution as a probability distribution for our location among otherwise compatible instances. This remains direct prior art for the finite conditional kernel.
- **Hartle and Srednicki (2007)** distinguish an explicit typicality assumption from a literal random-selection story; this supports the manuscript's refusal to reify a global chooser.
- **Thomas (online 2024; issue 2026)** develops `Simulation Expectation` and an explicit calibration principle. The manuscript's finite count-calibration result is positioned as an assumption-explicating construction, not a refutation.
- **Kipping (2020)** performs Bayesian model averaging over simulation feasibility; model averaging and structural identifiability remain distinct questions.
- **Neal (2006)** advocates conditioning on full non-indexical evidence; the manuscript therefore does not equate every self-location theory with a uniform kernel.
- **Schneider and Olum (2013)** directly discuss simulations, replays, stored computations, and the difficulty of subjectively identical reference classes, making them close conceptual prior work for representation boundaries.
- **Uchida (2026)** independently develops a typed observer-measure/self-location specification framework without a global sampler. This is the closest contemporaneous overlap with the manuscript's measure-specification motivation and is now explicitly acknowledged.

## Novelty decision after Round 9

The paper should **not** claim novelty for:

- observer-measure versus self-location role separation;
- the idea that there is no required literal global observer sampler;
- a probability distribution over centered locations;
- ordinary count calibration under a uniform centered distribution;
- finite additivity;
- known-channel affine-rank identification;
- generic latent-factorization nonuniqueness.

The defensible contribution remains the integrated, simulation-specific audit connecting:

```text
observation interface
  -> measure/self-location rule
  -> representation invariance
  -> persistent-versus-redrawn latent hierarchy
  -> conditional and joint identifiability
  -> Bayesian update.
```

The strongest technical value is not that each arrow is individually unprecedented. It is that the manuscript makes the arrows explicit in one auditable generative hierarchy, supplies exact boundary examples, and prevents numerical simulation posteriors from silently changing statistical experiments between steps.

## Round-9 decision

**Decision: pass with applied revision.**

No high-confidence mathematical false positive was found. The self-location proposition is now more precisely scoped, the physical-sampler language is less misleading, and the closest contemporaneous conceptual prior art is explicitly engaged. The manuscript should not add another mathematical section before release; the remaining work is release verification and independent external specialist review.
