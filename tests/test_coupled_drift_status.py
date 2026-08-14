from pathlib import Path


def test_coupled_drift_status_keeps_unsolved_feedback_explicit():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-status.md"
    ).read_text(encoding="utf-8")
    assert "feedback policies" in text
    assert "Not implemented" in text
