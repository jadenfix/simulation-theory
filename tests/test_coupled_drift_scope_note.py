from pathlib import Path


def test_coupled_drift_scope_note_is_bounded():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-license-note.md"
    ).read_text(encoding="utf-8")
    assert "bounded instances" in text
    assert "not to replace industrial" in text
