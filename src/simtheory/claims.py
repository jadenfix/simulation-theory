"""Deterministic claim-manifest validation for evidence-bound research."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ALLOWED_KINDS = {"THEOREM", "MODEL_RESULT", "FINITE_CHECK", "OPEN_PROBLEM"}
REQUIRED_FIELDS = {"id", "title", "kind", "scope", "assumptions", "evidence", "nonclaims"}


def validate_claim_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema") != "simulation-theory.claims/v1":
        raise ValueError("unsupported claim-manifest schema")
    claims = manifest.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("manifest must contain a nonempty claims list")
    identifiers: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("every claim must be an object")
        missing = REQUIRED_FIELDS - set(claim)
        if missing:
            raise ValueError(f"claim is missing fields: {sorted(missing)}")
        identifier = claim["id"]
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("claim id must be a nonempty string")
        if identifier in identifiers:
            raise ValueError(f"duplicate claim id: {identifier}")
        identifiers.add(identifier)
        if claim["kind"] not in ALLOWED_KINDS:
            raise ValueError(f"unsupported claim kind: {claim['kind']}")
        if not isinstance(claim["title"], str) or not claim["title"]:
            raise ValueError("claim title must be a nonempty string")
        if not isinstance(claim["scope"], str) or not claim["scope"]:
            raise ValueError("claim scope must be a nonempty string")
        for field in ("assumptions", "evidence", "nonclaims"):
            values = claim[field]
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ValueError(f"claim field {field} must be a list of strings")


def canonical_claim_manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    validate_claim_manifest(manifest)
    return json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_claim_manifest_hash(manifest: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_claim_manifest_bytes(manifest)).hexdigest()


def load_claim_manifest(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    validate_claim_manifest(manifest)
    return manifest


def _markdown_heading_anchors(text: str) -> set[str]:
    """Approximate GitHub-style anchors for the simple headings used here."""
    import re

    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().lower()
        heading = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        heading = re.sub(r"\s+", "-", heading).strip("-")
        occurrence = counts.get(heading, 0)
        counts[heading] = occurrence + 1
        anchors.add(heading if occurrence == 0 else f"{heading}-{occurrence}")
    return anchors


def validate_local_evidence_paths(
    manifest: Mapping[str, Any],
    repository_root: str | Path,
) -> None:
    """Check that local evidence files and declared Markdown anchors exist."""
    validate_claim_manifest(manifest)
    root = Path(repository_root)
    for claim in manifest["claims"]:
        for evidence in claim["evidence"]:
            if evidence.startswith(("http://", "https://")):
                continue
            anchor: str | None = None
            path_text = evidence
            if "#" in path_text:
                path_text, anchor = path_text.split("#", 1)
            elif ":" in path_text:
                path_text, _ = path_text.split(":", 1)
            path = root / path_text
            if not path.is_file():
                raise ValueError(f"missing evidence file for {claim['id']}: {path_text}")
            if anchor is not None:
                anchors = _markdown_heading_anchors(path.read_text(encoding="utf-8"))
                if anchor not in anchors:
                    raise ValueError(
                        f"missing evidence anchor for {claim['id']}: {path_text}#{anchor}"
                    )
