from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_observed_law_dynamic_coding_claim_manifest_is_valid():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "observed-law-dynamic-coding-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T127",
        "ST-T128",
        "ST-T129",
        "ST-T130",
        "ST-M31",
        "ST-F20",
    }
