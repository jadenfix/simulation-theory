from pathlib import Path


def test_coupled_drift_examples_document_keeps_exact_values():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-examples.md"
    ).read_text(encoding="utf-8")
    for value in ("7/4", "5/4", "23/6", "11/3"):
        assert value in text
