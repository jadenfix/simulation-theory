from pathlib import Path


def test_coupled_drift_design_matrix_does_not_conflate_feedback():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-design-matrix.md"
    ).read_text(encoding="utf-8")
    assert "Open-loop sequence" in text
    assert "Full-state feedback" in text
    assert "No" in text
