from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_latent_mixture_two_view_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "latent-mixture-two-view-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T259",
        "ST-T260",
        "ST-T261",
        "ST-T262",
        "ST-T263",
        "ST-M77",
        "ST-M78",
        "ST-M79",
        "ST-F47",
    }
