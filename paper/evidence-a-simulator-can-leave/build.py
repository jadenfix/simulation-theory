"""Compile main.typ to a PDF with typst-py, using only Typst's bundled fonts.

Usage: python build.py [output.pdf]   (default: main.pdf next to this file)

The paper workflow pins the typst-py version. System fonts are ignored so that
a build does not depend on the fonts installed on the machine.
"""

import sys
from pathlib import Path

import typst

HERE = Path(__file__).resolve().parent


def main() -> None:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "main.pdf"
    typst.compile(str(HERE / "main.typ"), output=str(output), root=str(HERE), ignore_system_fonts=True)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
