from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_active_experiment_regret_decomposition_claim_manifest_is_valid_and_evidence_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "active-experiment-regret-decomposition-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T180",
        "ST-T181",
        "ST-T182",
        "ST-T183",
        "ST-T184",
        "ST-M47",
        "ST-M48",
        "ST-M49",
        "ST-F31",
    }
