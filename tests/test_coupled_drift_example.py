import runpy
from pathlib import Path


def test_coupled_drift_example_executes():
    runpy.run_path(
        str(Path(__file__).parents[1] / "examples" / "coupled_drift_demo.py"),
        run_name="__main__",
    )
