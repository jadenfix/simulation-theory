from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_prior_weighted_code_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "prior-weighted-code-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T85",
        "ST-T86",
        "ST-T87",
        "ST-T88",
        "ST-T89",
        "ST-T90",
        "ST-T91",
        "ST-M19",
        "ST-M20",
        "ST-F12",
    }
