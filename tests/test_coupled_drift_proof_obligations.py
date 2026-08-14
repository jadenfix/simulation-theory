from pathlib import Path


def test_coupled_drift_proof_obligations_include_dual_and_path_checks():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-proof-obligations.md"
    ).read_text(encoding="utf-8")
    assert "consecutive total-variation" in text
    assert "Complementary slackness" in text
    assert "Primal and dual values agree exactly" in text
