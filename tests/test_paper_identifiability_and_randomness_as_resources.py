"""Checks for the paper bundle paper/identifiability-and-randomness-as-resources/ ("Identification, evidence caps, and the price of shared randomness").

The shared checks (bundle files, PDF page count and metadata, ledger mapping to
repository claim IDs and claim kinds, citations, no em dashes) live in
tests/typst_paper_checks.py. The paper workflow additionally regenerates the
figures, whose script asserts agreement with the repository receipts, and
rebuilds the PDF.
"""

from typst_paper_checks import ROOT, check_bundle_files, check_citations, check_ledger, check_pdf, check_prose_style

SLUG = "identifiability-and-randomness-as-resources"
TEXT = (ROOT / "paper" / SLUG / "main.typ").read_text(encoding="utf-8")


def test_bundle_files():
    check_bundle_files(SLUG)


def test_pdf_matches_ledger():
    check_pdf(SLUG)


def test_ledger_maps_every_claim_to_repository_ids():
    check_ledger(SLUG)


def test_citations_resolve():
    check_citations(SLUG)


def test_no_em_dashes():
    check_prose_style(SLUG)


def test_scope_qualifiers_present():
    # Qualifiers restored during review; removing one would overclaim.
    for phrase in ['Nothing here is evidence for or against the hypothesis that reality is simulated', '$L >= 2$', 'at least as fast as', 'Henry-Kitamura-Salanié', 'no claim of priority', 'not claimed as new', 'across independent world draws']:
        assert phrase in TEXT, phrase
    for phrase in ['Fáry', 'Fary']:
        assert phrase not in TEXT, phrase
