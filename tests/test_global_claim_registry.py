import json
from collections import defaultdict
from pathlib import Path


def test_all_machine_readable_claim_ids_are_globally_unique():
    root = Path(__file__).parents[1]
    claims_directory = root / "claims"
    locations: dict[str, list[str]] = defaultdict(list)

    for path in sorted(claims_directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for claim in payload.get("claims", ()):
            claim_id = claim.get("id")
            assert isinstance(claim_id, str) and claim_id, (
                f"{path.relative_to(root)} contains a claim without a nonempty ID"
            )
            locations[claim_id].append(str(path.relative_to(root)))

    duplicates = {
        claim_id: tuple(paths)
        for claim_id, paths in locations.items()
        if len(paths) > 1
    }
    assert not duplicates, f"claim IDs must be globally unique: {duplicates}"


def test_every_manifest_validates_with_existing_evidence():
    from simtheory.claims import load_claim_manifest, validate_local_evidence_paths

    root = Path(__file__).parents[1]
    paths = sorted((root / "claims").glob("*.json"))
    assert paths
    for path in paths:
        validate_local_evidence_paths(load_claim_manifest(path), root)
