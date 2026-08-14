from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_quantum_causal_cut_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "quantum-causal-cut-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T36",
        "ST-T37",
        "ST-T38",
        "ST-T39",
        "ST-T40",
        "ST-M10",
        "ST-F02",
    }
