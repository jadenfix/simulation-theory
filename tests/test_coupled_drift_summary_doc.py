from pathlib import Path


def test_coupled_drift_summary_lists_core_artifacts():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-summary.md"
    ).read_text(encoding="utf-8")
    assert "path optimizer" in text
    assert "dual receipt" in text
    assert "code-sequence optimizer" in text
