from pathlib import Path


def test_coupled_drift_frontier_document_is_present_and_scoped():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-research-roadmap.md"
    ).read_text(encoding="utf-8")
    assert "Only the first two are solved" in text
    assert "partial-observation" in text.lower()
    assert "not `q` itself" in text
