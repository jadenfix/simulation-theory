from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_active_fixed_model_regret_claim_manifest_is_valid_and_evidence_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "active-fixed-model-minimax-regret-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T175",
        "ST-T176",
        "ST-T177",
        "ST-T178",
        "ST-T179",
        "ST-M44",
        "ST-M45",
        "ST-M46",
        "ST-F30",
    }
