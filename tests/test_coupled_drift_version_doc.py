from pathlib import Path


def test_coupled_drift_version_marks_open_loop_baseline():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-version.md"
    ).read_text(encoding="utf-8")
    assert "open-loop baseline" in text
