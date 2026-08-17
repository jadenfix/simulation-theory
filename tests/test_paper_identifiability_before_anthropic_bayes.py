import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "identifiability-before-anthropic-bayes"


def test_paper_bundle_is_complete_and_claims_scoped():
    for name in (
        "paper.tex",
        "references.bib",
        "claims.json",
        "reproduce.py",
        "receipt.json",
        "README.md",
        "AUDIT.md",
        "PEER_REVIEW_LOOP.md",
        "PEER_REVIEW_RESPONSE.md",
        "citation_provenance.json",
    ):
        assert (PAPER / name).is_file()
    claims = json.loads((PAPER / "claims.json").read_text())
    assert len(claims["claims"]) == 7
    two_view = next(c for c in claims["claims"] if c["id"] == "P1-T7")
    assert "not unrestricted two-view latent-class identifiability" in two_view["nonclaims"]
    persistent = next(c for c in claims["claims"] if c["id"] == "P1-T4")
    assert any("absolute continuity" in x for x in persistent["assumptions"])
    affine = next(c for c in claims["claims"] if c["id"] == "P1-T5")
    assert any("known channel" in x for x in affine["assumptions"])


def test_paper_reproduction_is_byte_identical(tmp_path, monkeypatch):
    script = (PAPER / "reproduce.py").read_text()
    p = tmp_path / "reproduce.py"
    p.write_text(script)
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(p), run_name="__main__")
    generated_bytes = (tmp_path / "receipt.json").read_bytes()
    expected_bytes = (PAPER / "receipt.json").read_bytes()
    assert generated_bytes == expected_bytes

    receipt = json.loads(generated_bytes)
    assert receipt["two_view_grid_audit_2state"] == {
        "admissible_count": 32,
        "denominator": 8,
        "only_permutations": True,
        "preserving_count": 2,
    }
    assert receipt["two_view_grid_audit_3state"] == {
        "admissible_count": 108,
        "denominator": 3,
        "only_permutations": True,
        "preserving_count": 6,
    }
    assert receipt["support_mismatch_boundary"]["finite_ceiling_applies"] is False
    assert receipt["known_channel_identifiability"]["rank_deficient_collision_prior_a"] != receipt["known_channel_identifiability"]["rank_deficient_collision_prior_b"]


def test_manuscript_contains_scope_guards_core_citations_and_round_two_fixes():
    tex = (PAPER / "paper.tex").read_text()
    bib = (PAPER / "references.bib").read_text()
    assert "does \\emph{not} state that arbitrary two-view latent-class models are globally identifiable" in tex
    assert "Support mismatch" in tex
    assert "Physical duplication" in tex
    assert "Known-channel affine-rank identifiability" in tex
    assert "organizing principle" in tex
    assert "I_b(y)=\\{m:b_mP_m(y)>0\\}" in tex
    assert "First split $0=0+0$" in tex
    for key in (
        "bostrom2003",
        "weatherson2003",
        "crawford2013",
        "franceschi2014",
        "richmond2017",
        "kipping2020",
        "thomas2024",
        "neal2006",
        "schneiderolum2013",
        "wilson2013",
        "dizadji2015",
        "khawaja2026",
        "allman2009",
        "gillis2020",
    ):
        assert ("{" + key + ",") in bib
        assert key in tex


def test_citation_provenance_covers_core_references():
    provenance = json.loads((PAPER / "citation_provenance.json").read_text())
    entries = {entry["key"]: entry for entry in provenance["entries"]}
    for key in (
        "bostrom2003",
        "richmond2017",
        "kipping2020",
        "thomas2024",
        "allman2009",
        "gillis2020",
    ):
        assert key in entries
        assert entries[key]["verification_status"] in {"publisher_verified", "primary_repository_verified"}
        assert entries[key]["source"]


def test_peer_review_artifacts_preserve_reports_and_applied_response_loop():
    review = (PAPER / "PEER_REVIEW_LOOP.md").read_text()
    response = (PAPER / "PEER_REVIEW_RESPONSE.md").read_text()
    assert "Round 1" in review
    assert "major revision" in review.lower()
    assert "Round 1 response" in response
    assert "Round 2" in response
    assert "R2.1" in response and "R2.2" in response
    assert "zero unresolved major items" in response
    assert "synthetic" in response.lower()
