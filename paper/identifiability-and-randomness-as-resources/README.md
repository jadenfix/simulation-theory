# Identification, evidence caps, and the price of shared randomness

*Orthogonal two-view fibers, persistent-latent evidence, and exact fair-bit costs in finite games*

Jaden Fix, Tempera (Jaden@Tempera.dev). Every result is stated from typed claims in this repository at commit `aa61193` (the results merged in PR #72 and the attribution sweep of PR #73).

**PDF:** [main.pdf](main.pdf) (19 pages).

## What the paper shows

- Three exact finite results that separate what an observable law identifies from what evidence or randomness can buy. (The directory keeps its working slug; the paper was retitled during review.)
- Identification: given the population law, across independent world draws, of two views of one persistent latent state through a common channel, the consistent models form an orthogonal fiber (ST-T297), a stochastic reparametrization of the standard orthogonal ambiguity of symmetric factorizations. A strictly positive channel leaves the prior not even locally identified (ST-T298). For two latent states the identified set has a closed form (ST-T301) that specializes the Henry-Kitamura-Salanie bounds to a shared channel; no priority is claimed.
- Evidence: hypotheses that differ only in world-level weights over a shared kernel yield at most KL(a || b) nats of expected evidence per world draw (ST-T277, data processing, standard); the shortfall is bounded by the MAP error (ST-T279).
- Randomness: the mixed value of a finite rational game is reached by finitely many public fair bits iff some optimal mixture is dyadic (ST-T310, elementary); otherwise the b-bit gap is Theta(2^-b) (ST-T311), and the least expected cost is the Knuth-Yao cost (cited) minimized over the optimal set (ST-T312). Coins with L >= 2 sides are covered by ST-T313.

## Status

- Each result block carries its claim type (theorem, model result, finite check, open problem). Classical results restated for this setting are typed as standard results, and results used without proof are typed as cited theorems; each names its source.
- The proofs are written in the repository's derivation documents (`docs/`) and are not formally verified. Finite checks corroborate proofs on bounded instances and are not proofs.
- The manuscript was revised against two referee reports produced inside the authoring workflow. These were synthetic reviews, not external peer review.
- Prior-art searches were not exhaustive. Where the paper says "new", it means no earlier statement was found.

## Files

- `main.typ`: manuscript source (Typst).
- `refs.bib`: bibliography.
- `figures.py`: regenerates every figure in `figures/` (PDF and SVG: fig_bits, fig_evidence, fig_fiber_k2, fig_fiber_k3) from the repository's own modules and committed data, and asserts agreement with the committed receipts before drawing.
- `build.py`: compiles `main.typ` to a PDF with typst-py, using only Typst's bundled fonts.
- `main.pdf`: the compiled paper.
- `claims.json`: the paper ledger (below).

## Claim ledger

`claims.json` has 33 entries (1 cited theorem, 3 finite check, 8 model result, 2 open problem, 5 standard result, 14 theorem), one for each result block of the paper. Each entry records the block's type, novelty status, assumptions and nonclaims, and the repository claim IDs it restates (36 distinct IDs). `context_repo_claims` lists the further IDs the paper cites only in prose, tables or the reproduction map.

`uv run python -m simtheory verify` checks that every mapped ID exists and runs `tests/test_paper_identifiability_and_randomness_as_resources.py`. That test checks the bundle files and figures, the PDF page count and title metadata, that every claim ID written in the paper is mapped, that each entry's type agrees with the kind of the repository claims it cites, that every citation resolves in `refs.bib`, that the scope qualifiers added in review are still present, and that the sources contain no em dashes.

## Reproduce

From the repository root:

```bash
uv sync && uv run python -m simtheory verify
cd paper/identifiability-and-randomness-as-resources
uv run --with matplotlib==3.11.2 --with numpy==2.5.4 python figures.py
uv run --with typst==0.15.0 python build.py /tmp/identifiability-and-randomness-as-resources.pdf
uv run --with pypdfium2==5.14.0 python ../../scripts/compare_paper_pdf_text.py main.pdf /tmp/identifiability-and-randomness-as-resources.pdf
```

The workflow `.github/workflows/paper-typst.yml` runs the same steps on every pull request that touches this paper or the repository code it imports. It requires the rebuilt PDF to have the same pages and text as `main.pdf` and uploads the rebuilt PDF. PDF bytes are not compared, because figure files carry generated element IDs and the PDF carries a build time.

## Nonclaims

- Nothing in the paper is evidence for or against simulation; reading a latent state as simulated versus base is an interpretation of the mixture model.
- The fiber results assume finite alphabets, k known, a full-row-rank channel and the exact two-view population law; an observer of a single world draw never sees that law.
- Kruskal's three-view theorem and the Giacomini-Kitagawa limit are cited, not proved. The Knuth-Yao theorem and the 8/3-bit cost of a uniform ternary choice are classical; the repository reproves the former and does not claim it as new.
- Fair, independent, public bits are assumed; extracting them from a physical source is not addressed.
