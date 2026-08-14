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
