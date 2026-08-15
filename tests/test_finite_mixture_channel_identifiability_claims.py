from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_finite_mixture_channel_identifiability_claim_manifest_is_valid_and_evidence_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "finite-mixture-channel-identifiability-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T238",
        "ST-T239",
        "ST-T240",
        "ST-T241",
        "ST-T242",
        "ST-T243",
        "ST-M69",
        "ST-M70",
        "ST-F43",
    }
