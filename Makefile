.PHONY: verify verify-quick verify-online test experiments

verify:
	uv run python -m simtheory verify

verify-quick:
	uv run python -m simtheory verify --quick

verify-online:
	uv run python -m simtheory verify --online

test:
	uv run python -m pytest

experiments:
	uv run python -m simtheory experiments
