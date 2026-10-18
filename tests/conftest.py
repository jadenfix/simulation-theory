import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip (rather than deselect) slow tests under SIMTHEORY_QUICK=1 so reports show them."""
    if os.environ.get("SIMTHEORY_QUICK") != "1":
        return
    skip = pytest.mark.skip(reason="slow exhaustive check; run `python -m simtheory verify` for the full suite")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
