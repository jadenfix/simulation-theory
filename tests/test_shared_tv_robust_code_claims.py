from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_shared_tv_robust_code_claim_manifest_is_valid_and_bound():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "shared-tv-robust-code-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T104",
        "ST-T105",
        "ST-T106",
        "ST-T107",
        "ST-T108",
        "ST-T109",
        "ST-T110",
        "ST-M26",
        "ST-M27",
        "ST-F15",
    }
