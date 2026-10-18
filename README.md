# simulation-theory

What can an observer inside a world actually learn about whether that world is
simulated? This repository answers that question with proofs, exact
computations, and machine-checked claim manifests, and it says exactly where
the answer stops.

It does not assume that reality is simulated, and nothing in it is evidence
that it is or is not.

## The core result

If a simulation produces exactly the same observable probability law as an
ordinary physical model,

```text
P_sim = P_base,
```

then every statistic an internal observer can compute has the same
distribution under both, every test has power equal to its size, and

```text
BF_sim:base = 1   on every possible data set.
```

Posterior odds equal prior odds. No amount of data, computation, or cleverness
recovers information that is absent from the observable law
([formal-results.md](docs/formal-results.md#unrestricted-indistinguishability),
claim ST-T01).

So the generic hypothesis "some external process generates our observations"
is not identifiable. Everything else in the repository works on the other side
of that boundary: declare a *restricted* simulator (finite memory, finite
precision, coarsened observations, bounded communication, a classical stand-in
for a quantum system), derive the law it can produce, and ask how fast, if at
all, an observer could tell it apart. For example:

- **Evidence grows at a KL rate.** A simulated bit source with bias q is
  separated from fair bits at expected log Bayes factor at least
  `n KL(q || 1/2) - (1/2) ln n - ln 2` (ST-T271, the expectation of the
  classical Krichevsky-Trofimov regret bound). If its output is viewed through
  a binary symmetric channel with flip probability f, the bias shrinks by the
  channel's Dobrushin coefficient 1 - 2f, so the rate drops to
  `KL(f + (1-2f) q || 1/2)` and the detection frontier widens by 1/(1-2f)
  (ST-M14, ST-M83, ST-M84).
- **Evidence has a ceiling.** If the likelihood ratio is confined to
  `[e^-eps, e^eps]`, the posterior log odds move by at most `eps` (ST-T02).
- **A local classical simulator cannot reproduce Bell correlations.** On the
  canonical CHSH schedule the quantum family is a disk with an exact predictive
  metric, `TV = ||q - q'||_inf / (2 sqrt 2)` (ST-T12), and the local bound
  `S <= 2` is a chord across it. The released data of the Delft 2015
  loophole-free Bell test recompute to `S = 2.42 +- 0.20`, `p = 0.039`, a point
  right of that chord (ST-F50, ST-F51). Read anytime-validly, the same 245
  trials are weak evidence: no mixture of constant bets on the CHSH win
  indicator reaches the 5% threshold at any prefix, so the anytime-valid
  confidence sets for the signalling and setting-dependence budgets built from
  that class are the full ranges; other e-processes are not covered (ST-F56, a
  negative result).
- **Rendering on demand is not a signature by itself.** Lazy generation that
  samples each answer from the exact conditional law has the same transcript
  law as a pre-generated world
  ([formal-results.md](docs/formal-results.md#exact-lazy-rendering-equivalence)).
  Approximate rendering costs at most `1 - prod_t (1 - eps_t)` in transcript TV
  (ST-T04), and any renderer within `eps` of `K` future laws separated by more
  than `2 eps` needs at least `K` states (ST-T05).

## Results by type

Every result carries a stable ID, a type, a scope, assumptions, evidence paths,
and explicit nonclaims in a manifest under [`claims/`](claims/). There are 465
claims in 60 manifests:

| type | count | meaning |
| --- | --- | --- |
| Theorem (`ST-T`) | 304 | follows from the stated assumptions |
| Model result (`ST-M`) | 93 | exact inside one declared model or finite example |
| Finite check (`ST-F`) | 60 | reproducible computation on an explicitly bounded domain or fixed data set |
| Open problem (`ST-O`) | 8 | a research target, not a conclusion |

Theorems that restate or specialize known results (for example the
data-processing inequality, the Clarke-Barron constant, Knuth-Yao sampling, the
Le Cam randomization criterion, Fano, Dobrushin, Blackwell, Witsenhausen,
Knill-Laflamme or Nayak) are meant to say so in their title or nonclaims, with
citations in the derivation doc. The attribution sweep
covered the mixture-conditioning lanes, the lanes added with the evidence-scaling
results, and the classical results a recheck found in the older lanes. An older
lane may still contain an unmarked standard result; that is a ledger bug, not a
novelty claim.

A passing test validates code and a bounded receipt. It never promotes a finite
check into a universal theorem.

| lane | what it establishes | derivation | manifest |
| --- | --- | --- | --- |
| identification and evidence | indistinguishability, evidence ceilings, Le Cam and Fano bounds, anytime-valid e-processes, observer-measure Jensen gap | [formal-results](docs/formal-results.md) | [claims-v1](claims/claims-v1.json) |
| real data | Delft 2015 CHSH recomputation, CHSH-disk placement, NIST beacon precommitments, KL detection rate | [real-data-checks](docs/real-data-checks.md) | [real-data](claims/real-data-claims.json) |
| evidence scaling | two-sided pathwise KT sandwich and the Clarke-Barron constant, NIST beacon power frontier and converse, the KL cap for one persistent latent draw and its saturation gap | [evidence-scaling-dichotomy](docs/evidence-scaling-dichotomy.md) | [evidence-scaling](claims/evidence-scaling-dichotomy-claims.json) |
| Bell simulator resources | exact CHSH escape-route frontiers and the negative anytime-valid Delft check, finite-precision renderers and the dithering boundary, renderer memory on the Bell disk, Le Cam deficiency of a noisy simulator | [bell-escape-route-frontiers](docs/bell-escape-route-frontiers.md), [finite-precision-renderer-identifiability](docs/finite-precision-renderer-identifiability.md), [bell-disk-renderer-memory](docs/bell-disk-renderer-memory.md), [le-cam-deficiency-bell-simulator](docs/le-cam-deficiency-bell-simulator.md) | [escape-routes](claims/bell-escape-route-frontier-claims.json), [finite-precision](claims/finite-precision-renderer-claims.json), [disk-memory](claims/bell-disk-renderer-memory-claims.json), [le-cam](claims/le-cam-deficiency-claims.json) |
| Bell and quantum geometry | Werner and visibility-phase predictive laws, the canonical CHSH disk, quadratic packings | [bell-predictive-bounds](docs/bell-predictive-bounds.md), [canonical-chsh-disk-geometry](docs/canonical-chsh-disk-geometry.md), [quantum-phase-predictive-bounds](docs/quantum-phase-predictive-bounds.md) | [quantum-phase](claims/quantum-phase-claims.json) |
| relational information and codes | graph-state and cat-state consistency, noisy parity rate-distortion, stabilizer-code locality | [stabilizer-relational-consistency](docs/stabilizer-relational-consistency.md), [noisy-relational-rate-distortion](docs/noisy-relational-rate-distortion.md), [stabilizer-code-locality](docs/stabilizer-code-locality.md) | [stabilizer-relational](claims/stabilizer-relational-claims.json), [noisy-relational](claims/noisy-relational-claims.json), [stabilizer-code](claims/stabilizer-code-claims.json) |
| causal cuts and communication | random-access message bounds, quantum causal cuts, progressive query revelation, distributed consistency | [quantum-causal-cut-random-access](docs/quantum-causal-cut-random-access.md), [progressive-query-revelation](docs/progressive-query-revelation.md), [distributed-causal-consistency](docs/distributed-causal-consistency.md) | [quantum-causal-cut](claims/quantum-causal-cut-claims.json), [progressive-query](claims/progressive-query-claims.json), [distributed-consistency](claims/distributed-consistency-claims.json) |
| predictive state and channels | stochastic covers, ternary centers, Dobrushin contraction, observation-channel value | [stochastic-predictive-covers](docs/stochastic-predictive-covers.md), [ternary-predictive-centers](docs/ternary-predictive-centers.md), [stochastic-channel-contraction](docs/stochastic-channel-contraction.md), [observation-channel-information-value](docs/observation-channel-information-value.md) | [stochastic-predictive](claims/stochastic-predictive-claims.json), [ternary-predictive](claims/ternary-predictive-claims.json), [stochastic-channel](claims/stochastic-channel-claims.json), [observation-channel](claims/observation-channel-information-claims.json) |
| networks | predictive min-cuts, multicast network coding, sink-specific function computation | [predictive-network-mincuts](docs/predictive-network-mincuts.md), [multicast-network-coding](docs/multicast-network-coding.md), [functional-network-computation](docs/functional-network-computation.md) | [predictive-network](claims/predictive-network-claims.json), [multicast](claims/multicast-network-coding-claims.json), [functional-network](claims/functional-network-claims.json) |
| zero-error coding | confusion graphs and chromatic number, prior-weighted Huffman optima, finite-prior and TV-ball robust codes, shared randomness and its random-bit price | [nonlinear-confusion-graphs](docs/nonlinear-confusion-graphs.md), [prior-weighted-zero-error-coding](docs/prior-weighted-zero-error-coding.md), [finite-prior-robust-coding](docs/finite-prior-robust-coding.md), [distributionally-robust-tv-coding](docs/distributionally-robust-tv-coding.md), [shared-randomness-tv-robust-coding](docs/shared-randomness-tv-robust-coding.md), [random-bit-price-shared-randomness](docs/random-bit-price-shared-randomness.md) | [confusion-graph](claims/confusion-graph-claims.json), [prior-weighted](claims/prior-weighted-code-claims.json), [robust-prior](claims/robust-prior-code-claims.json), [distributionally-robust](claims/distributionally-robust-code-claims.json), [shared-tv](claims/shared-tv-robust-code-claims.json), [random-bit-price](claims/random-bit-price-claims.json) |
| robust priors and drift | polyhedral duals and regret confidence, prior drift, coupled drift sequences, adaptive drift information | [polyhedral-dual-certificates](docs/polyhedral-dual-certificates.md), [polyhedral-regret-confidence](docs/polyhedral-regret-confidence.md), [prior-drift-path-robustness](docs/prior-drift-path-robustness.md), [coupled-drift-code-sequences](docs/coupled-drift-code-sequences.md), [adaptive-drift-information-patterns](docs/adaptive-drift-information-patterns.md) | [polyhedral-dual](claims/polyhedral-dual-claims.json), [polyhedral-regret](claims/polyhedral-regret-confidence-claims.json), [prior-drift](claims/prior-drift-claims.json), [coupled-drift](claims/coupled-drift-code-sequence-claims.json), [adaptive-drift](claims/adaptive-drift-information-claims.json) |
| regret and active experiments | pathwise and feedback regret, observed-law coding, coarsened and stochastic law observation, fixed-model ambiguity, active experiment value, menu-expansion regret shifts, experiment complementarity, observation-lattice interactions | [pathwise-dynamic-regret](docs/pathwise-dynamic-regret.md), [feedback-information-regret](docs/feedback-information-regret.md), [observed-law-dynamic-coding](docs/observed-law-dynamic-coding.md), [coarsened-law-observation-games](docs/coarsened-law-observation-games.md), [stochastic-law-observation-beliefs](docs/stochastic-law-observation-beliefs.md), [fixed-model-ambiguity-frontiers](docs/fixed-model-ambiguity-frontiers.md), [active-fixed-model-experiments](docs/active-fixed-model-experiments.md), [active-fixed-model-minimax-regret](docs/active-fixed-model-minimax-regret.md), [active-experiment-regret-value-decomposition](docs/active-experiment-regret-value-decomposition.md), [active-experiment-menu-regret-shifts](docs/active-experiment-menu-regret-shifts.md), [active-experiment-complementarity](docs/active-experiment-complementarity.md), [experiment-observation-lattice-interactions](docs/experiment-observation-lattice-interactions.md) | [pathwise-regret](claims/pathwise-regret-claims.json), [feedback-regret](claims/feedback-information-regret-claims.json), [observed-law](claims/observed-law-dynamic-coding-claims.json), [coarsened-law](claims/coarsened-law-observation-claims.json), [stochastic-law](claims/stochastic-law-observation-belief-claims.json), [fixed-model-ambiguity](claims/fixed-model-ambiguity-claims.json), [active-experiment](claims/active-fixed-model-experiment-claims.json), [active-regret](claims/active-fixed-model-minimax-regret-claims.json), [active-decomposition](claims/active-experiment-regret-decomposition-claims.json), [menu-regret](claims/active-experiment-menu-regret-claims.json), [complementarity](claims/active-experiment-complementarity-claims.json), [observation-lattice](claims/experiment-observation-lattice-claims.json) |
| Bayesian Boolean experiments | K3 Bayes gap as posterior minority mass, influence and Walsh-Fourier bounds, adaptive query option value, cost-sensitive stopping, prior-robust value and ranking | [bayesian-boolean-experiment-geometry](docs/bayesian-boolean-experiment-geometry.md), [bayesian-boolean-fourier-geometry](docs/bayesian-boolean-fourier-geometry.md), [bayesian-adaptive-boolean-queries](docs/bayesian-adaptive-boolean-queries.md), [bayesian-cost-sensitive-query-stopping](docs/bayesian-cost-sensitive-query-stopping.md), [bayesian-boolean-prior-robustness](docs/bayesian-boolean-prior-robustness.md) | [boolean-experiment](claims/bayesian-boolean-experiment-claims.json), [boolean-fourier](claims/bayesian-boolean-fourier-claims.json), [adaptive-query](claims/bayesian-adaptive-boolean-query-claims.json), [cost-sensitive](claims/bayesian-cost-sensitive-query-claims.json), [prior-robustness](claims/bayesian-boolean-prior-robustness-claims.json) |
| latent priors and mixtures | evidence ceilings for one persistent latent draw, confidence from independent latent draws, binary and finite-mixture identifiability with known channels, the exact TV conditioning modulus and its row-uncertainty bounds, the prior-channel gauge and its two-view rigidity inside the nonnegative gauge class, the orthogonal two-view fiber and its identified set, refinement invariance | [persistent-latent-prior-evidence-ceilings](docs/persistent-latent-prior-evidence-ceilings.md), [independent-latent-prior-confidence](docs/independent-latent-prior-confidence.md), [binary-latent-mixture-identifiability](docs/binary-latent-mixture-identifiability.md), [finite-mixture-channel-identifiability](docs/finite-mixture-channel-identifiability.md), [finite-mixture-global-tv-modulus](docs/finite-mixture-global-tv-modulus.md), [finite-mixture-row-uncertainty](docs/finite-mixture-row-uncertainty.md), [latent-mixture-gauge-nonidentifiability](docs/latent-mixture-gauge-nonidentifiability.md), [latent-mixture-two-view-rigidity](docs/latent-mixture-two-view-rigidity.md), [two-view-orthogonal-fiber](docs/two-view-orthogonal-fiber.md), [latent-refinement-invariance](docs/latent-refinement-invariance.md), [refinement-measure-uniqueness](docs/refinement-measure-uniqueness.md) | [persistent-latent](claims/persistent-latent-prior-claims.json), [latent-confidence](claims/independent-latent-prior-confidence-claims.json), [binary-mixture](claims/binary-latent-mixture-identifiability-claims.json), [finite-mixture](claims/finite-mixture-channel-identifiability-claims.json), [global-tv](claims/finite-mixture-global-tv-claims.json), [row-uncertainty](claims/finite-mixture-row-uncertainty-claims.json), [gauge](claims/latent-mixture-gauge-claims.json), [two-view](claims/latent-mixture-two-view-claims.json), [two-view-fiber](claims/two-view-orthogonal-fiber-claims.json), [refinement](claims/latent-refinement-claims.json), [refinement-measure](claims/refinement-measure-claims.json) |

Four papers are written from these claims, each with its own ledger in
`paper/<slug>/claims.json` that `verify` checks against the repository claim IDs
and the paper's tests:

- [Identifiability Before Anthropic Bayes](paper/identifiability-before-anthropic-bayes/) (8 claims).
- [How much evidence can a simulator leave?](paper/evidence-a-simulator-can-leave/main.pdf):
  explicit Krichevsky-Trofimov evidence rates, the one-draw cap on evidence about
  world-level weights, and what the NIST beacon and Delft 2015 data do and do not show
  ([source and ledger](paper/evidence-a-simulator-can-leave/)).
- [Pricing a Bell simulator](paper/pricing-a-bell-simulator/main.pdf): precision,
  memory, communication and noise costs of reproducing CHSH statistics
  ([source and ledger](paper/pricing-a-bell-simulator/)).
- [Identification, evidence caps, and the price of shared randomness](paper/identifiability-and-randomness-as-resources/main.pdf):
  the orthogonal two-view fiber, the persistent-latent cap, and exact fair-bit
  costs in finite games ([source and ledger](paper/identifiability-and-randomness-as-resources/)).

The three Typst papers were revised against synthetic referee reports, not
external peer review; `.github/workflows/paper-typst.yml` regenerates their
figures and rebuilds their PDFs on every pull request that touches them. An
adversarial review of the mathematics and its publication readiness, with a record
of how each finding was addressed, is in
[docs/math-audit-publication-readiness.md](docs/math-audit-publication-readiness.md).

A guided tour of the mathematics, with the main formulas, is in
[docs/result-map.md](docs/result-map.md). The open problems (ST-O01 to ST-O08)
are stated in their lanes' derivations, and the research agenda is in
[docs/research-program.md](docs/research-program.md) and
[formal-results.md](docs/formal-results.md#current-open-problems).

## Reproduce

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11 or newer. The
mathematical core uses only the standard library; pytest is the only
development dependency.

```bash
uv sync
uv run python -m simtheory verify          # everything, about 12 minutes
uv run python -m simtheory verify --quick  # skips 9 slow exhaustive tests, under a minute
make verify                                # same as the first command
```

`verify` runs, in order:

1. byte-compilation of `src/`;
2. validation of every `claims/*.json`: schema, globally unique IDs, evidence
   files (inside the repository) and Markdown anchors, and every
   `file.py:symbol` reference;
3. the real-data receipts: the Delft 2015 statistic recomputed from the
   committed trials, whose digest is pinned in code, and checked against the
   published `S = 2.42 +- 0.20`, `p = 0.039` (also pinned in code), and the
   hash-chain consistency of all 256 links of the pinned NIST beacon pulse list
   (consistency, not authenticity: NIST signatures are not checked);
4. the deterministic experiment suite, compared with
   [`receipts/experiments.txt`](receipts/experiments.txt);
5. the test suite, then a per-claim report that every test file each claim
   cites has passed. The suite includes the receipts of the newer lanes under
   [`receipts/`](receipts/) and regression tests showing that hand-built
   forged certificates fail validation: certificate `valid` properties rebind
   the certificate to its stored instance by recomputation
   ([math audit](docs/math-audit-publication-readiness.md#second-audit-2026-10-18)).

`--online` also downloads the Delft archive (hash-checked) and the beacon
pulses again and confirms they reduce to the committed summaries in
[`data/real/`](data/real/). CI runs `verify` on Python 3.11, 3.12, and 3.13.

## Scope

- Results concern **observable laws available to an internal investigator**.
  No theorem assumes a simulator exists, and none estimates the probability
  that one does.
- Theorems hold under their stated assumptions. Model results hold inside one
  declared model. Finite checks hold on their declared domain or data set.
  Nonclaims in each manifest say what does not follow.
- Internal physical quantities (mass, energy, Hilbert-space dimension) are not
  converted into costs for a parent substrate without an explicit
  implementation map; see
  [formal-results.md](docs/formal-results.md#local-physics-versus-parent-physics).
- Quantization, randomness, Bell violation, entanglement, error-correcting
  structure, and information bounds are not evidence of simulation. Ordinary
  physics and ordinary distributed systems contain all of them.
- The real-data checks reproduce one published Bell statistic and test one
  public random source under one composite hypothesis. They test the
  machinery, not the world.

## What would count as evidence

Evidence must favor a **restricted simulator model** over serious alternative
physical, measurement, selection, and intervention models. A useful proposal
must declare in advance:

1. null and alternative observable laws;
2. nuisance parameters;
3. measurement and selection channels;
4. the query or intervention protocol;
5. the inferential rule (likelihood, e-process, confidence sequence);
6. calibration, power, and stopping behavior;
7. the ordinary-physics alternatives and how they are excluded;
8. which broader simulator classes remain untouched.

## Repository layout

```text
src/simtheory/   theorem models, exact algorithms, real-data reductions, verify entry point
tests/           unit, property, exhaustive, and real-data checks
claims/          machine-readable scope, evidence, assumptions, and nonclaims
docs/            derivations, examples, scope boundaries, and the research program
data/real/       committed real-data summaries with provenance and hashes
receipts/        expected output of the deterministic experiment suite
paper/           paper sources, compiled PDFs, and per-paper claim ledgers
```

## Data credits

- B. Hensen et al. (2015): Loophole-free Bell-inequality violation using
  electron spins separated by 1.3 kilometres. 4TU.ResearchData.
  https://doi.org/10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31. Used under
  the 4TU General Terms of Use (attribution, non-commercial reuse); any further
  distribution of `data/real/delft2015-bell-trials.json` must carry this
  acknowledgement. Paper: Nature 526, 682-686 (2015).
- NIST Randomness Beacon 2.0, chain 2, pulses 1987000 to 1987256,
  https://beacon.nist.gov/.

## Related

`tempera-math` may be used as an external content-addressed proof and receipt
harness; see [docs/tempera-math-bridge.md](docs/tempera-math-bridge.md). This
repository remains the canonical research home. A script run, CI pass, or
content hash never promotes a bounded result into an unbounded theorem.

Code is MIT licensed ([LICENSE](LICENSE)); the data files under `data/real/`
keep their sources' terms.
