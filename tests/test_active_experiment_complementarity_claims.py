from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_active_experiment_complementarity_claim_manifest_is_valid_and_evidence_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "active-experiment-complementarity-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T190",
        "ST-T191",
        "ST-T192",
        "ST-T193",
        "ST-M53",
        "ST-M54",
        "ST-F33",
    }
