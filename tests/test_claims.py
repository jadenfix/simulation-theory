import json
from pathlib import Path

from simtheory.claims import (
    canonical_claim_manifest_hash,
    load_claim_manifest,
    validate_claim_manifest,
    validate_local_evidence_paths,
)


def test_claim_manifest_is_valid_and_deterministic():
    path = Path(__file__).parents[1] / "claims" / "claims-v1.json"
    manifest = load_claim_manifest(path)
    first = canonical_claim_manifest_hash(manifest)
    reordered = json.loads(json.dumps(manifest, sort_keys=False))
    validate_claim_manifest(reordered)
    assert first == canonical_claim_manifest_hash(reordered)
    assert len(first) == 64
    validate_local_evidence_paths(manifest, path.parents[1])
