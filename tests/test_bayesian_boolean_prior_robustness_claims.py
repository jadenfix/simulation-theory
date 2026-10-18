from pathlib import Path

from simtheory.claims import canonical_claim_manifest_hash, load_claim_manifest, validate_local_evidence_paths


def test_bayesian_boolean_prior_robustness_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "bayesian-boolean-prior-robustness-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    assert len(canonical_claim_manifest_hash(manifest)) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T221", "ST-T222", "ST-T223", "ST-T224", "ST-M65", "ST-F39"
    }
