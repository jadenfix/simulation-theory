from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_distributionally_robust_code_claim_manifest_is_valid_and_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "distributionally-robust-code-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T98",
        "ST-T99",
        "ST-T100",
        "ST-T101",
        "ST-T102",
        "ST-T103",
        "ST-M24",
        "ST-M25",
        "ST-F14",
    }
