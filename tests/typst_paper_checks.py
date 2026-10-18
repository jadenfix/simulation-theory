"""Shared checks for the Typst paper bundles under paper/<slug>/.

Each bundle holds main.typ, refs.bib, figures.py, build.py, the generated
figures, the compiled main.pdf, a README and a claims.json ledger that maps
every result block of the paper to repository claim IDs. These checks use only
the standard library; the paper workflow additionally regenerates the figures
and rebuilds the PDF.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Ledger type -> repository claim kinds an entry of that type may cite.
KINDS_FOR_TYPE = {
    "theorem": {"THEOREM"},
    "standard result": {"THEOREM"},
    "cited theorem": set(),
    "model result": {"MODEL_RESULT"},
    # A finite check either has its own FINITE_CHECK record or is a boundary
    # witness recorded under a THEOREM record.
    "finite check": {"FINITE_CHECK", "THEOREM"},
    "open problem": {"OPEN_PROBLEM"},
}
NOVELTY_WORDS = ("new", "standard", "classical", "cited", "elementary", "reproduces", "known", "exact", "bounded",
                 "open", "heuristic", "corollary", "finite check")

_ID = re.compile(r"ST-([TMFO])(\d+)((?:\s*(?:/|,|–|-|to)\s*(?:ST-)?[TMFO]?\d+)*)")
_TAIL = re.compile(r"\s*(/|,|–|-|to)\s*(ST-)?([TMFO]?)(\d+)")


def _claim_id(letter: str, number: int) -> str:
    return f"ST-{letter}{number:02d}"


def mentioned_claim_ids(text: str) -> set[str]:
    """Claim IDs written in the text, with ranges such as "ST-T290 to T296" or "ST-T297–ST-T305" expanded."""

    out: set[str] = set()
    for match in _ID.finditer(text):
        letter, previous = match.group(1), int(match.group(2))
        out.add(_claim_id(letter, previous))
        for separator, prefix, next_letter, number in _TAIL.findall(match.group(3)):
            if separator == "," and not (prefix or next_letter):
                break  # a bare number after a comma is not a claim ID
            next_letter, value = next_letter or letter, int(number)
            if separator not in (",", "/") and next_letter == letter and previous < value <= previous + 20:
                out.update(_claim_id(next_letter, k) for k in range(previous + 1, value + 1))
            else:
                out.add(_claim_id(next_letter, value))
            letter, previous = next_letter, value
    return out


def repository_claim_kinds() -> dict[str, str]:
    kinds: dict[str, str] = {}
    for path in sorted((ROOT / "claims").glob("*.json")):
        for claim in json.loads(path.read_text(encoding="utf-8"))["claims"]:
            kinds[claim["id"]] = claim["kind"]
    return kinds


def load_ledger(slug: str) -> dict:
    return json.loads((ROOT / "paper" / slug / "claims.json").read_text(encoding="utf-8"))


def check_bundle_files(slug: str) -> None:
    paper = ROOT / "paper" / slug
    for name in ("main.typ", "refs.bib", "figures.py", "build.py", "README.md", "claims.json", "main.pdf"):
        assert (paper / name).is_file(), f"{slug}: missing {name}"
    text = (paper / "main.typ").read_text(encoding="utf-8")
    images = re.findall(r'image\("([^"]+)"', text)
    assert images, f"{slug}: no figures referenced"
    for image in images:
        assert (paper / image).is_file(), f"{slug}: missing figure {image}"
    # Both vector formats are committed for every figure.
    for figure in (paper / "figures").glob("*.pdf"):
        assert figure.with_suffix(".svg").is_file(), f"{slug}: {figure.name} has no SVG twin"
    # The figure script imports the repository at the root, not a private clone.
    script = (paper / "figures.py").read_text(encoding="utf-8")
    assert '"repo"' not in script, f"{slug}: figures.py still points at a private ./repo clone"


def check_pdf(slug: str) -> None:
    ledger = load_ledger(slug)
    raw = (ROOT / "paper" / slug / ledger["pdf"]).read_bytes()
    assert raw.startswith(b"%PDF-"), f"{slug}: main.pdf is not a PDF"
    pages = len(re.findall(rb"/Type\s*/Page(?![s\w])", raw))
    assert pages == ledger["pages"], f"{slug}: main.pdf has {pages} pages, ledger says {ledger['pages']}"
    title = ledger["paper"].encode("utf-8")
    assert b'<rdf:li xml:lang="x-default">' + title + b"</rdf:li>" in raw, f"{slug}: PDF title metadata"
    text = (ROOT / "paper" / slug / "main.typ").read_text(encoding="utf-8")
    assert f'title: "{ledger["paper"]}"' in text, f"{slug}: document title in main.typ"
    assert f'author: "{ledger["author"]}"' in text, f"{slug}: document author in main.typ"


def check_ledger(slug: str) -> None:
    ledger = load_ledger(slug)
    kinds = repository_claim_kinds()
    text = (ROOT / "paper" / slug / "main.typ").read_text(encoding="utf-8")
    assert ledger["schema"] == "simulation-theory/paper-ledger-v1"
    assert ledger["slug"] == slug
    assert set(ledger["types"]) == set(KINDS_FOR_TYPE)
    seen: set[str] = set()
    cited: set[str] = set()
    for entry in ledger["claims"]:
        identifier = entry["id"]
        assert re.fullmatch(r"P\d+-\d{2}", identifier), identifier
        assert identifier not in seen and identifier not in kinds, identifier
        seen.add(identifier)
        assert entry["type"] in KINDS_FOR_TYPE, (identifier, entry["type"])
        assert entry["name"] and entry["section"], identifier
        assert entry["assumptions"] and all(isinstance(x, str) and x for x in entry["assumptions"]), identifier
        assert entry["nonclaims"] and all(isinstance(x, str) and x for x in entry["nonclaims"]), identifier
        status = entry["status"].lower()
        assert any(word in status for word in NOVELTY_WORDS), (identifier, entry["status"])
        repo = entry["repo_claims"]
        if entry["type"] == "cited theorem":
            assert "cited" in status, identifier
        elif entry["type"] == "standard result":
            assert any(w in status for w in ("standard", "classical", "elementary", "not new")), identifier
        if not repo:
            # Only cited theorems and standard results may stand without a repository record of their own.
            assert entry["type"] in ("cited theorem", "standard result"), identifier
        for claim in repo:
            assert claim in kinds, f"{identifier}: unknown repository claim {claim}"
            assert kinds[claim] in KINDS_FOR_TYPE[entry["type"]], (identifier, claim, kinds[claim], entry["type"])
        cited.update(repo)
    context = set(ledger["context_repo_claims"])
    for claim in context:
        assert claim in kinds, f"context claim {claim} is not a repository claim"
    assert not (context & cited), sorted(context & cited)
    # Every claim ID written in the paper is mapped, and the ledger maps nothing the paper does not mention.
    literal = set(re.findall(r"ST-[TMFO]\d+", text))
    assert literal <= cited | context, sorted(literal - cited - context)
    assert cited | context <= mentioned_claim_ids(text), sorted((cited | context) - mentioned_claim_ids(text))
    assert ledger["paper_nonclaims"]
    assert any("evidence for or against simulation" in x for x in ledger["paper_nonclaims"])


def check_citations(slug: str) -> None:
    paper = ROOT / "paper" / slug
    text = (paper / "main.typ").read_text(encoding="utf-8")
    bib = (paper / "refs.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))
    labels = set(re.findall(r"<([A-Za-z][\w:.-]*)>", text))
    body = re.sub(r'"[^"\n]*"', '""', text)  # strings (link targets, paths) are not citations
    body = re.sub(r"^\s*//.*$", "", body, flags=re.MULTILINE)
    used = {m.rstrip(".:-") for m in re.findall(r"(?<![\w\\])@([A-Za-z][\w:.-]*)", body)}
    missing = sorted(u for u in used if u not in keys and u not in labels)
    assert not missing, f"{slug}: unresolved citations or references {missing}"


def check_prose_style(slug: str) -> None:
    paper = ROOT / "paper" / slug
    for name in ("main.typ", "figures.py", "README.md", "claims.json", "build.py"):
        assert "—" not in (paper / name).read_text(encoding="utf-8"), f"{slug}/{name} contains an em dash"


def check_all(slug: str) -> None:
    check_bundle_files(slug)
    check_pdf(slug)
    check_ledger(slug)
    check_citations(slug)
    check_prose_style(slug)
