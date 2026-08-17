import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "identifiability-before-anthropic-bayes"


def test_paper_bundle_is_complete_and_claims_scoped():
    for name in ("paper.tex", "references.bib", "claims.json", "reproduce.py", "receipt.json", "README.md"):
        assert (PAPER / name).is_file()
    claims = json.loads((PAPER / "claims.json").read_text())
    assert len(claims["claims"]) == 6
    two_view = next(c for c in claims["claims"] if c["id"] == "P1-T6")
    assert "not unrestricted two-view latent-class identifiability" in two_view["nonclaims"]
    persistent = next(c for c in claims["claims"] if c["id"] == "P1-T4")
    assert any("absolute continuity" in x for x in persistent["assumptions"])


def test_paper_reproduction_exact(tmp_path, monkeypatch):
    # Execute a byte-identical temporary copy so the tracked receipt is not mutated.
    script = (PAPER / "reproduce.py").read_text()
    p = tmp_path / "reproduce.py"
    p.write_text(script)
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(p), run_name="__main__")
    generated = json.loads((tmp_path / "receipt.json").read_text())
    expected = json.loads((PAPER / "receipt.json").read_text())
    generated.pop("sha256_without_hash", None)
    assert generated == expected


def test_manuscript_contains_scope_guards_and_all_citations():
    tex = (PAPER / "paper.tex").read_text()
    bib = (PAPER / "references.bib").read_text()
    assert "not unrestricted two-view latent-class identifiability" in tex
    assert "support assumption is essential" in tex
    for key in ("bostrom2003", "weatherson2003", "crawford2013", "franceschi2014", "richmond2017", "thomas2024", "wilson2013", "dizadji2015", "khawaja2026", "allman2009"):
        assert ("{" + key + ",") in bib
        assert key in tex
