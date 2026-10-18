"""Check that a rebuilt paper PDF has the same pages and text as the committed one.

Usage: python scripts/compare_paper_pdf_text.py committed.pdf rebuilt.pdf

Needs pypdfium2 (the paper workflow pins it). PDF bytes are not compared:
figure files carry generated element IDs and the PDF carries a build time, so
the check is on page count and the extracted text of every page.
"""

import sys

import pypdfium2 as pdfium


def page_texts(path: str) -> list[str]:
    document = pdfium.PdfDocument(path)
    try:
        return [document[i].get_textpage().get_text_range() for i in range(len(document))]
    finally:
        document.close()


def main() -> int:
    committed, rebuilt = (page_texts(p) for p in sys.argv[1:3])
    if len(committed) != len(rebuilt):
        print(f"page count differs: committed {len(committed)}, rebuilt {len(rebuilt)}")
        return 1
    differing = [i + 1 for i, (a, b) in enumerate(zip(committed, rebuilt)) if a != b]
    if differing:
        print(f"text differs on pages {differing}; rebuild the PDF with build.py and commit it")
        return 1
    print(f"{len(committed)} pages, text identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
