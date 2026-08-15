from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_finite_mixture_row_uncertainty_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "finite-mixture-row-uncertainty-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T249",
        "ST-T250",
        "ST-T251",
        "ST-T252",
        "ST-T253",
        "ST-M73",
        "ST-M74",
        "ST-F45",
    }
