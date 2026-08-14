from pathlib import Path


def test_coupled_drift_open_problems_do_not_claim_feedback_is_solved():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-open-problems.md"
    ).read_text(encoding="utf-8")
    assert "Solve full-state feedback" in text
    assert "anytime-valid" in text
