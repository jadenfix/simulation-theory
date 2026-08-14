from pathlib import Path


def test_coupled_drift_lane_readme_points_to_code_tests_and_claims():
    text = (
        Path(__file__).parents[1]
        / "docs"
        / "coupled-drift-readme.md"
    ).read_text(encoding="utf-8")
    assert "src/simtheory/coupled_drift.py" in text
    assert "tests/test_coupled_drift.py" in text
    assert "claims/coupled-drift-code-sequence-claims.json" in text
