from pathlib import Path

from simtheory.claims import canonical_claim_manifest_hash, load_claim_manifest, validate_local_evidence_paths


def test_persistent_latent_prior_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "persistent-latent-prior-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    assert len(canonical_claim_manifest_hash(manifest)) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T225", "ST-T226", "ST-T227", "ST-T228",
        "ST-M66", "ST-M67", "ST-F40"
    }
