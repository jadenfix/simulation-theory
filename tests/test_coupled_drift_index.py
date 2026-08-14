from pathlib import Path


def test_coupled_drift_index_targets_exist():
    root = Path(__file__).parents[1] / "docs"
    text = (root / "coupled-drift-index.md").read_text(encoding="utf-8")
    for name in (
        "coupled-drift-code-sequences.md",
        "coupled-drift-proof-obligations.md",
        "coupled-drift-examples.md",
        "coupled-drift-design-matrix.md",
        "coupled-drift-research-roadmap.md",
        "coupled-drift-nonclaims.md",
    ):
        assert name in text
        assert (root / name).is_file()
