from pathlib import Path

from simtheory.claims import canonical_claim_manifest_hash, load_claim_manifest, validate_local_evidence_paths


def test_bayesian_adaptive_boolean_query_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "bayesian-adaptive-boolean-query-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    assert len(canonical_claim_manifest_hash(manifest)) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T215", "ST-T216", "ST-T217", "ST-T218", "ST-M61", "ST-M62", "ST-F37"
    }
