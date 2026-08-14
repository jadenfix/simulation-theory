from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_local_evidence_paths,
)


def test_confusion_graph_claim_manifest_is_valid_and_evidence_bound():
    path = Path(__file__).parents[1] / "claims" / "confusion-graph-claims.json"
    manifest = load_claim_manifest(path)
    validate_local_evidence_paths(manifest, path.parents[1])
    digest = canonical_claim_manifest_hash(manifest)
    assert len(digest) == 64
    assert {claim["id"] for claim in manifest["claims"]} == {
        "ST-T77",
        "ST-T78",
        "ST-T79",
        "ST-T80",
        "ST-T81",
        "ST-T82",
        "ST-T83",
        "ST-T84",
        "ST-M18",
        "ST-F11",
    }
