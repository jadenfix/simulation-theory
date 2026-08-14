from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_robust_prior_code_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "robust-prior-code-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T92",
        "ST-T93",
        "ST-T94",
        "ST-T95",
        "ST-T96",
        "ST-T97",
        "ST-M21",
        "ST-M22",
        "ST-M23",
        "ST-F13",
    }
