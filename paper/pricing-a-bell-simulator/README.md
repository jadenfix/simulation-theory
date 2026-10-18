# Pricing a Bell simulator

*Precision, memory, communication and noise costs of reproducing CHSH statistics, stated from typed, test-backed claims*

Jaden Fix, Tempera (Jaden@Tempera.dev). Every result is stated from typed claims in this repository at commit `aa61193` (the results merged in PR #72 and the attribution sweep of PR #73).

**PDF:** [main.pdf](main.pdf) (17 pages).

## What the paper shows

- The paper restricts a simulation hypothesis to a classical renderer of the canonical CHSH Bell experiment and prices each resource it might economize: how much must be spent to reproduce the statistics, and how many trials it takes to notice when it was not.
- Precision: a renderer that may dither is untestable (ST-T286, standard, Madow's construction). On commensurable schedules, CHSH included, a 1/D-grid renderer is indistinguishable from the Werner family under unknown visibility once 4 | D and D exceeds an explicit threshold (ST-T287). Settings 0 and pi/4 identify it with Theta(D^4 log(1/eps)) trials for designs restricted to cosines in {0, +-1, +-1/sqrt(2)} (ST-T288); known unit visibility (v = 1) with the adapted angle cos theta = 1 - 2/D and even D gives Theta(D log(1/eps)) (ST-T289).
- Memory: an eps-accurate one-trial renderer needs at least pi / (A_w eps^2) states (ST-T290); the constant is exactly pi/32 for CHSH (ST-T291). Among schedules with at most three direction classes the regular three-direction schedule forces the most memory (ST-T294), and the regular four-direction schedule forces more (ST-T295; the upper bracket uses Rogers' covering theorem and Fejes Toth's lattice covering bound, both cited).
- Leaks and noise: exact certificates reproduce the classical communication (Pironio), measurement-dependence (Putz et al.) and detection (Garg-Mermin) frontiers (ST-T282, ST-T283, ST-M85). On the one-trial interface with equal correlation magnitudes C and central post-processing, a visibility-lambda simulator has Le Cam deficiency C(1 - lambda) / (2(2 - C lambda)) (ST-T306), strictly below every deterministic setting-preserving relabeling for 0 < C < 1 and 0 <= lambda < 1 (ST-T309).

## Status

- Each result block carries its claim type (theorem, model result, finite check, open problem). Classical results restated for this setting are typed as standard results, and results used without proof are typed as cited theorems; each names its source.
- The proofs are written in the repository's derivation documents (`docs/`) and are not formally verified. Finite checks corroborate proofs on bounded instances and are not proofs.
- The manuscript was revised against two referee reports produced inside the authoring workflow. These were synthetic reviews, not external peer review.
- Prior-art searches were not exhaustive. Where the paper says "new", it means no earlier statement was found.

## Files

- `main.typ`: manuscript source (Typst).
- `refs.bib`: bibliography.
- `figures.py`: regenerates every figure in `figures/` (PDF and SVG: fig1_disk, fig2_precision, fig3_zonoid, fig4_frontiers, fig5_lecam, fig6_delft) from the repository's own modules and committed data, and asserts agreement with the committed receipts before drawing.
- `build.py`: compiles `main.typ` to a PDF with typst-py, using only Typst's bundled fonts.
- `main.pdf`: the compiled paper.
- `claims.json`: the paper ledger (below).

## Claim ledger

`claims.json` has 26 entries (5 finite check, 1 model result, 4 standard result, 16 theorem), one for each result block of the paper. Each entry records the block's type, novelty status, assumptions and nonclaims, and the repository claim IDs it restates (27 distinct IDs). `context_repo_claims` lists the further IDs the paper cites only in prose, tables or the reproduction map.

`uv run python -m simtheory verify` checks that every mapped ID exists and runs `tests/test_paper_pricing_a_bell_simulator.py`. That test checks the bundle files and figures, the PDF page count and title metadata, that every claim ID written in the paper is mapped, that each entry's type agrees with the kind of the repository claims it cites, that every citation resolves in `refs.bib`, that the scope qualifiers added in review are still present, and that the sources contain no em dashes.

## Reproduce

From the repository root:

```bash
uv sync && uv run python -m simtheory verify
cd paper/pricing-a-bell-simulator
uv run --with matplotlib==3.11.2 --with numpy==2.5.4 python figures.py
uv run --with typst==0.15.0 python build.py /tmp/pricing-a-bell-simulator.pdf
uv run --with pypdfium2==5.14.0 python ../../scripts/compare_paper_pdf_text.py main.pdf /tmp/pricing-a-bell-simulator.pdf
```

The workflow `.github/workflows/paper-typst.yml` runs the same steps on every pull request that touches this paper or the repository code it imports. It requires the rebuilt PDF to have the same pages and text as `main.pdf` and uploads the rebuilt PDF. PDF bytes are not compared, because figure files carry generated element IDs and the PDF carries a build time.

## Nonclaims

- Nothing in the paper is evidence for or against simulation; a Bell violation is not evidence for simulation.
- Internal states and grid denominators are representational resources of a hypothetical renderer, not claims about parent hardware.
- Precision rates assume a declared D and exactly known cosines; for odd D, or D below the threshold, no separation rate is claimed.
- Memory results are one-trial bounds for the two-parameter coplanar family.
- The Delft negative result concerns constant-bet mixtures on the win indicator only.
