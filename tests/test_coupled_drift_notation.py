from pathlib import Path


def test_coupled_drift_notation_states_the_envelope_as_an_inequality():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-notation.md"
    ).read_text(encoding="utf-8")
    assert "V(g_{1:T})\\le M(g_{1:T})" in text
    assert "simultaneous-attainability" in text
