# How much evidence can a simulator leave?

*Explicit evidence rates, a one-draw cap, and what the NIST beacon and Delft 2015 data do and do not show*

Jaden Fix, Tempera (Jaden@Tempera.dev). Every result is stated from typed claims in this repository at commit `aa61193` (the results merged in PR #72 and the attribution sweep of PR #73).

**PDF:** [main.pdf](main.pdf) (19 pages).

## What the paper shows

- A simulator that reproduces the base observable law leaves no evidence (ST-T01). The paper asks how much evidence a *restricted* simulator can leave.
- Per-world signal: for the Krichevsky-Trofimov test against fair bits, the expected log Bayes factor is n KL(q || 1/2) - (1/2) ln n plus a constant that stays in an explicit 1.47-nat window for every n (ST-T272, ST-T273); the limit constant is the Clarke-Barron constant (ST-T274, standard). A sufficient power frontier and a Le Cam converse bracket the detectable biases up to a sqrt(ln n) factor; they do not match (ST-T275, ST-T276).
- Weights over one persistent world: no transcript yields more than KL(a || b) nats in expectation (data processing, standard; ST-T277). The shortfall is an exact posterior-disagreement term (ST-T278), bounded by the MAP error with a new (R - 1) factor and a support-mismatch term (ST-T279).
- Real data: the NIST beacon test does not reject fair bits, and the power frontier states which IID biases were excluded (ST-F52 to ST-F54). The Delft 2015 data give S = 2.42 +- 0.20 and fixed-n p = 0.039 (ST-F50, ST-F51), but no mixture of constant bets on the win indicator exceeds 7.78 at any prefix, against a threshold of 20 (ST-F56, a negative result for that class only).

## Status

- Each result block carries its claim type (theorem, model result, finite check, open problem). Classical results restated for this setting are typed as standard results, and results used without proof are typed as cited theorems; each names its source.
- The proofs are written in the repository's derivation documents (`docs/`) and are not formally verified. Finite checks corroborate proofs on bounded instances and are not proofs.
- The manuscript was revised against two referee reports produced inside the authoring workflow. These were synthetic reviews, not external peer review.
- Prior-art searches were not exhaustive. Where the paper says "new", it means no earlier statement was found.

## Files

- `main.typ`: manuscript source (Typst).
- `refs.bib`: bibliography.
- `figures.py`: regenerates every figure in `figures/` (PDF and SVG: fig_beacon, fig_chsh_disk, fig_delft_eprocess, fig_evidence, fig_frontiers, fig_renderers) from the repository's own modules and committed data, and asserts agreement with the committed receipts before drawing.
- `build.py`: compiles `main.typ` to a PDF with typst-py, using only Typst's bundled fonts.
- `main.pdf`: the compiled paper.
- `claims.json`: the paper ledger (below).

## Claim ledger

`claims.json` has 22 entries (6 finite check, 1 model result, 1 open problem, 8 standard result, 6 theorem), one for each result block of the paper. Each entry records the block's type, novelty status, assumptions and nonclaims, and the repository claim IDs it restates (27 distinct IDs). `context_repo_claims` lists the further IDs the paper cites only in prose, tables or the reproduction map.

`uv run python -m simtheory verify` checks that every mapped ID exists and runs `tests/test_paper_evidence_a_simulator_can_leave.py`. That test checks the bundle files and figures, the PDF page count and title metadata, that every claim ID written in the paper is mapped, that each entry's type agrees with the kind of the repository claims it cites, that every citation resolves in `refs.bib`, that the scope qualifiers added in review are still present, and that the sources contain no em dashes.

## Reproduce

From the repository root:

```bash
uv sync && uv run python -m simtheory verify
cd paper/evidence-a-simulator-can-leave
uv run --with matplotlib==3.11.2 --with numpy==2.5.4 python figures.py
uv run --with typst==0.15.0 python build.py /tmp/evidence-a-simulator-can-leave.pdf
uv run --with pypdfium2==5.14.0 python ../../scripts/compare_paper_pdf_text.py main.pdf /tmp/evidence-a-simulator-can-leave.pdf
```

The workflow `.github/workflows/paper-typst.yml` runs the same steps on every pull request that touches this paper or the repository code it imports. It requires the rebuilt PDF to have the same pages and text as `main.pdf` and uploads the rebuilt PDF. PDF bytes are not compared, because figure files carry generated element IDs and the PDF carries a build time.

## Nonclaims

- Nothing in the paper is evidence for or against simulation.
- The sandwich concerns the Krichevsky-Trofimov (Jeffreys) alternative and IID bits; dependent, adaptive or adversarial sources are not covered.
- The beacon frontier is not a randomness certification, and NIST signatures are not checked.
- The Delft ceiling covers constant-bet mixtures on the win indicator only, not adaptive bets or full-data test factors.
