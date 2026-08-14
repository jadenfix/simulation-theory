from pathlib import Path


def test_coupled_drift_checklist_guards_adaptive_and_parent_claims():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-checklist.md"
    ).read_text(encoding="utf-8")
    assert "not called adaptive" in text
    assert "not called parent hardware" in text
