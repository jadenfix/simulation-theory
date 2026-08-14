from pathlib import Path


def test_coupled_drift_abstract_states_temporal_and_simulation_boundaries():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-abstract.md"
    ).read_text(encoding="utf-8")
    assert "temporal consistency" in text
    assert "do not constitute evidence for simulation" in text
