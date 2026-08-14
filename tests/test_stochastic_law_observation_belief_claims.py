from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_stochastic_observation_belief_claim_manifest_is_valid():
    path = (
        Path(__file__).parents[1]
        / "claims"
        / "stochastic-law-observation-belief-claims.json"
    )
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T136",
        "ST-T137",
        "ST-T138",
        "ST-T139",
        "ST-M34",
        "ST-M35",
        "ST-F22",
    }
