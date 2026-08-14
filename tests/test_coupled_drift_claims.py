from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_coupled_drift_claim_manifest_is_valid_and_bound():
    path = Path(__file__).parents[1] / "claims" / "coupled-drift-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T123",
        "ST-T124",
        "ST-T125",
        "ST-T126",
        "ST-M30",
        "ST-M31",
        "ST-F19",
    }
