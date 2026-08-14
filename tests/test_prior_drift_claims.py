from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_prior_drift_claim_manifest_is_valid_and_bound():
    path = Path(__file__).parents[1] / "claims" / "prior-drift-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T120",
        "ST-T121",
        "ST-T122",
        "ST-M29",
        "ST-F18",
    }
