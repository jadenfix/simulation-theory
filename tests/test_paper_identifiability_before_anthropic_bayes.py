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
        "ROUND6_MEASURE_THEORETIC_AUDIT.md",
        "citation_provenance.json",
    ):
        assert (PAPER / name).is_file()
    claims = json.loads((PAPER / "claims.json").read_text())
    assert claims["author"] == "Jaden Fix"
    assert claims["email"] == "Jaden@Tempera.dev"
    assert len(claims["claims"]) == 7

    refinement = next(c for c in claims["claims"] if c["id"] == "P1-T2")
    assert any("conditionally independent same-channel" in x for x in refinement["assumptions"])
    assert any("tensor-product" in x for x in refinement["nonclaims"])

    persistent = next(c for c in claims["claims"] if c["id"] == "P1-T4")
    assert any("absolute continuity" in x for x in persistent["assumptions"])
    assert any("dominating finite measure exists" in x for x in persistent["assumptions"])
    assert any("almost everywhere" in x for x in persistent["assumptions"])
    assert any("null set" in x for x in persistent["nonclaims"])

    affine = next(c for c in claims["claims"] if c["id"] == "P1-T5")
    assert any("known channel" in x for x in affine["assumptions"])
    assert any("robust posterior" in x or "identified sets" in x for x in affine["nonclaims"])
    assert any("finite-sample conditioning" in x for x in affine["nonclaims"])

    gauge = next(c for c in claims["claims"] if c["id"] == "P1-T6")
    assert any("interior prior" in x for x in gauge["nonclaims"])

    two_view = next(c for c in claims["claims"] if c["id"] == "P1-T7")
    assert "not unrestricted two-view latent-class identifiability" in two_view["nonclaims"]
    assert any("same channel K" in x for x in two_view["assumptions"])
    assert any("different view-specific channels" in x for x in two_view["nonclaims"])
    assert "no independent priority claim" in two_view["status"]


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


def test_manuscript_contains_scope_guards_core_citations_and_review_fixes():
    tex = (PAPER / "paper.tex").read_text()
    bib = (PAPER / "references.bib").read_text()
    assert "\\author{Jaden Fix" in tex
    assert "pdfauthor={Jaden Fix}" in tex
    assert "\\frac{dP_S}{dP_B}=1" in tex
    assert "does \\emph{not} state that arbitrary two-view latent-class models are globally identifiable" in tex
    assert "Support mismatch" in tex
    assert "Physical duplication" in tex
    assert "Known-channel affine-rank identifiability" in tex
    assert "organizing principle" in tex
    assert "I_b(y)=\\{m:b_mp_m(y)>0\\}" in tex
    assert "common $\\sigma$-finite measure" in tex
    assert "Radon--Nikodym density" in tex
    assert "almost everywhere" in tex
    assert "First split $0=0+0$" in tex
    assert "Data cannot point-identify a mixture parameter" in tex
    assert "not estimable before it is identifiable" not in tex
    assert "A^{-1}\\mathbf 1=\\mathbf 1" in tex
    assert "A_t=(1-t)I+tB" in tex
    assert "both observations use the same channel $K$" in tex
    assert "same-channel repeated-view rigidity" in tex
    assert "Robust Bayesian methods for set-identified models" in tex
    assert "receipt.json` is required to regenerate byte-for-byte" in tex
    assert "does not claim that PDF bytes must remain invariant" in tex
    # Source-integrity guards: these late sections must survive whole-file replacements.
    assert "\\section{Limitations}" in tex
    assert "\\section{Conclusion}" in tex
    assert "\\bibliography{references}" in tex
    assert tex.rstrip().endswith("\\end{document}")
    for key in (
        "bostrom2003",
        "bostromkulczycki2011",
        "weatherson2003",
        "crawford2013",
        "franceschi2014",
        "richmond2017",
        "kipping2020",
        "thomas2024",
        "fallislewis2023",
        "giacomini2021",
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
    assert "year={2016}" in bib.split("@article{franceschi2014", 1)[1].split("@article{richmond2017", 1)[0]
    assert "pages={313--344}" in bib.split("@article{khawaja2026", 1)[1].split("@article{allman2009", 1)[0]
    fallis = bib.split("@article{fallislewis2023", 1)[1].split("@article{giacomini2021", 1)[0]
    assert "author={Peter J. Lewis and Don Fallis}" in fallis
    assert "pages={180}" in fallis
    assert "number={6}" not in fallis
    giacomini = bib.split("@article{giacomini2021", 1)[1].split("@misc{neal2006", 1)[0]
    assert "volume={89}" in giacomini and "number={4}" in giacomini
    assert "pages={1519--1556}" in giacomini


def test_release_bearing_artifacts_use_correct_author_identity():
    release_files = (
        "paper.tex",
        "README.md",
        "AUDIT.md",
        "PEER_REVIEW_LOOP.md",
        "PEER_REVIEW_RESPONSE.md",
        "ROUND6_MEASURE_THEORETIC_AUDIT.md",
        "claims.json",
    )
    for name in release_files:
        text = (PAPER / name).read_text()
        assert "Jaden Figgs" not in text
        assert "Jaden Fix" in text


def test_citation_provenance_covers_core_references():
    provenance = json.loads((PAPER / "citation_provenance.json").read_text())
    entries = {entry["key"]: entry for entry in provenance["entries"]}
    for key in (
        "bostrom2003",
        "bostromkulczycki2011",
        "richmond2017",
        "kipping2020",
        "thomas2024",
        "fallislewis2023",
        "giacomini2021",
        "allman2009",
        "gillis2020",
    ):
        assert key in entries
        assert entries[key]["verification_status"] in {"publisher_verified", "primary_repository_verified"}
        assert entries[key]["source"]
    assert entries["franceschi2014"]["verification_status"] == "publisher_verified_with_secondary_discrepancy"
    assert "2016" in entries["franceschi2014"]["notes"]
    assert "313-344" in entries["khawaja2026"]["notes"]
    assert "article 180" in entries["fallislewis2023"]["notes"]
    assert "1519-1556" in entries["giacomini2021"]["notes"]


def test_peer_review_artifacts_preserve_reports_and_applied_response_loop():
    review = (PAPER / "PEER_REVIEW_LOOP.md").read_text()
    response = (PAPER / "PEER_REVIEW_RESPONSE.md").read_text()
    round6 = (PAPER / "ROUND6_MEASURE_THEORETIC_AUDIT.md").read_text()
    assert "Round 1" in review
    assert "major revision" in review.lower()
    assert "preserved as originally written" in review
    assert "Round 1 response" in response
    assert "Round 2" in response
    assert "R2.1" in response and "R2.2" in response
    assert "R3.1" in response and "truncated" in response.lower()
    assert "Round 4" in response
    for item in ("R4.1", "R4.2", "R4.3", "R4.4", "R4.5", "R4.6"):
        assert item in response
    assert "Round 5" in response
    for item in ("R5.1", "R5.2", "R5.3", "R5.4"):
        assert item in response
    assert "Round 6" in response
    for item in ("R6.1", "R6.2", "R6.3", "R6.4", "R6.5", "R6.6", "R6.7", "R6.8"):
        assert item in response
        assert item in round6
    assert "zero unresolved major items" in response
    assert "synthetic" in response.lower()
    assert "not independent peer review" in round6


def test_workflow_records_source_toolchain_and_checks_correct_author():
    workflow = (ROOT / ".github" / "workflows" / "paper-identifiability.yml").read_text()
    assert "Record toolchain and source provenance" in workflow
    assert "git rev-parse HEAD" in workflow
    assert "toolchain.txt" in workflow
    assert "Author:.*Jaden Fix" in workflow
    assert "paper.tex" in workflow and "references.bib" in workflow
    assert "paper.bbl" in workflow and "paper.log" in workflow
    assert "test_paper_identifiability_before_anthropic_bayes.py" in workflow
    assert "ROUND6_MEASURE_THEORETIC_AUDIT.md" in workflow
    assert "Jaden Figgs" not in workflow
