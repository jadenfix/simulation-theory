"""Command-line entry: ``python -m simtheory verify`` or ``python -m simtheory experiments``."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = args.pop(0) if args else "verify"
    if command == "verify":
        from .verify import main as verify_main

        return verify_main(args)
    if command == "experiments":
        from .experiments import main as experiments_main

        experiments_main()
        return 0
    print("usage: python -m simtheory [verify [--quick] [--online] [--no-tests] | experiments]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
