from pathlib import Path


def test_coupled_drift_nonclaims_preserve_resource_boundaries():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-nonclaims.md"
    ).read_text(encoding="utf-8")
    assert "does not claim" in text.lower()
    assert "external memory" in text
    assert "empirical evidence for simulation" in text
