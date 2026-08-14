from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_stabilizer_relational_claim_manifest_is_valid_and_bound_to_local_evidence():
    path = Path(__file__).parents[1] / "claims" / "stabilizer-relational-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T15",
        "ST-T16",
        "ST-T17",
        "ST-T18",
        "ST-T19",
        "ST-M06",
    }
