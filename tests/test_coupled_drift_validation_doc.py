from pathlib import Path


def test_coupled_drift_validation_document_lists_independent_routes():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-validation.md"
    ).read_text(encoding="utf-8")
    assert "LP dual" in text
    assert "rational grid audit" in text
    assert "fixed-cost drift theorem" in text
