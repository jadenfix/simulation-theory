from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_active_experiment_menu_regret_claim_manifest_is_valid_and_evidence_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "active-experiment-menu-regret-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T185",
        "ST-T186",
        "ST-T187",
        "ST-T188",
        "ST-T189",
        "ST-M50",
        "ST-M51",
        "ST-M52",
        "ST-F32",
    }
