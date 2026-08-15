from pathlib import Path

from simtheory.claims import canonical_claim_manifest_hash, load_claim_manifest, validate_local_evidence_paths


def test_bayesian_cost_sensitive_query_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "bayesian-cost-sensitive-query-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    assert len(canonical_claim_manifest_hash(manifest)) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T219", "ST-T220", "ST-M63", "ST-M64", "ST-F38"
    }
