"""Rebuild or re-check the committed real-data summaries from their public sources.

Usage::

    python -m simtheory.real_data_fetch delft  [--write]
    python -m simtheory.real_data_fetch beacon [--write] [--start N] [--count K]

Without ``--write`` the downloaded data are reduced again and compared with the
committed summaries under ``data/real/``; any difference is an error. Downloads
are hash-checked (Delft) or precommitment-checked (beacon) before use. Only
the standard library is used, and the Delft archive (about 150 KB) is read in
memory one line at a time.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from .real_data import (
    BEACON_PULSE_URL,
    BEACON_SUMMARY_PATH,
    DELFT_RAW_MEMBER,
    DELFT_SUMMARY_PATH,
    DELFT_ZIP_MD5,
    DELFT_ZIP_SHA256,
    DELFT_ZIP_URL,
    chsh_summary,
    delft_valid_trials,
    trial_digest,
    verify_beacon_precommitments,
)

USER_AGENT = "simulation-theory-real-data-check/1"
BEACON_CHAIN = 2
BEACON_START = 1987000
BEACON_COUNT = 257

DELFT_SOURCE = {
    "dataset_title": "Loophole-free Bell-inequality violation using electron spins separated by 1.3 kilometres",
    "creators": "B. Hensen, H. Bernien, A. E. Dreau, A. Reiserer, N. Kalb, M. S. Blok, J. Ruitenberg, "
    "R. F. L. Vermeulen, R. N. Schouten, C. Abellan, W. Amaya, V. Pruneri, M. W. Mitchell, M. Markham, "
    "D. J. Twitchen, D. Elkouss, S. Wehner, T. H. Taminiau, R. Hanson",
    "publisher": "4TU.ResearchData (Delft University of Technology)",
    "dataset_doi": "10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31",
    "dataset_url": "https://data.4tu.nl/datasets/e8cf2991-3153-48ad-b67d-dfd7d7d97fd3",
    "paper": "Hensen et al., Nature 526, 682-686 (2015), doi:10.1038/nature15759",
    "license": "4TU General Terms of Use (doi:10.4121/resource:terms_of_use): attribution to the creators "
    "is required, redistribution must carry this acknowledgement, and reuse is non-commercial only",
    "published_values": {"trials": 245, "S": 2.42, "S_error": 0.20, "p_value": 0.039},
}

BEACON_SOURCE = {
    "service": "NIST Randomness Beacon, version 2.0",
    "url": "https://beacon.nist.gov/",
    "api": "https://beacon.nist.gov/beacon/2.0/chain/{chain}/pulse/{index}",
    "field": "localRandomValue: 512 bits from NIST's hardware entropy sources, conditioned by SHA-512",
    "license": "Work of the U.S. National Institute of Standards and Technology; cite the NIST Randomness Beacon",
    "verification": "SHA-512(localRandomValue[i+1]) equals precommitmentValue[i] for every consecutive pair",
}


def _download(url: str, timeout: float = 60.0) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https URLs
        return response.read()


def build_delft_summary(archive: bytes) -> dict[str, Any]:
    if hashlib.md5(archive).hexdigest() != DELFT_ZIP_MD5:  # noqa: S324 - matches the repository's published md5
        raise ValueError("Delft archive md5 does not match the 4TU record")
    if hashlib.sha256(archive).hexdigest() != DELFT_ZIP_SHA256:
        raise ValueError("Delft archive sha256 does not match the committed value")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        raw = bundle.read(DELFT_RAW_MEMBER)
    rows = raw.decode("ascii").splitlines()
    trials = delft_valid_trials(rows)
    summary = chsh_summary(trials)
    return {
        "schema": "simulation-theory.real-data.bell-trials/v1",
        "source": DELFT_SOURCE,
        "raw": {
            "archive_url": DELFT_ZIP_URL,
            "archive_md5": DELFT_ZIP_MD5,
            "archive_sha256": DELFT_ZIP_SHA256,
            "member": DELFT_RAW_MEMBER,
            "member_sha256": hashlib.sha256(raw).hexdigest(),
            "rows": len(rows),
        },
        "reduction": "simtheory.real_data.delft_valid_trials: the authors' published valid-trial filter",
        "columns": ["timestamp", "a", "b", "x", "y"],
        "trials_sha256": trial_digest(trials),
        "recomputed": {
            "trials": summary.trials,
            "wins": summary.wins,
            "S": summary.s_value,
            "S_error": summary.s_error,
        },
        "trials": [[t.timestamp, t.a, t.b, t.x, t.y] for t in trials],
    }


def fetch_beacon_pulses(start: int, count: int, pause: float = 0.15) -> list[dict[str, Any]]:
    pulses: list[dict[str, Any]] = []
    for index in range(start, start + count):
        url = BEACON_PULSE_URL.format(chain=BEACON_CHAIN, index=index)
        for attempt in range(4):
            try:
                pulse = json.loads(_download(url, timeout=30.0))["pulse"]
                break
            except Exception:  # pragma: no cover - network retry
                if attempt == 3:
                    raise
                time.sleep(2.0)
        if int(pulse["statusCode"]) != 0:
            raise ValueError(f"pulse {index} has nonzero status code {pulse['statusCode']}")
        pulses.append(
            {
                "pulseIndex": int(pulse["pulseIndex"]),
                "timeStamp": pulse["timeStamp"],
                "localRandomValue": pulse["localRandomValue"],
                "precommitmentValue": pulse["precommitmentValue"],
            }
        )
        time.sleep(pause)
    verify_beacon_precommitments(pulses)
    return pulses


def build_beacon_summary(pulses: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "simulation-theory.real-data.nist-beacon/v1",
        "source": BEACON_SOURCE,
        "chain": BEACON_CHAIN,
        "first_pulse": pulses[0]["pulseIndex"],
        "count": len(pulses),
        "note": "the last pulse is kept only to verify the previous pulse's precommitment",
        "pulses": pulses,
    }


def _write_or_compare(payload: dict[str, Any], path: Path, write: bool) -> int:
    text = json.dumps(payload, indent=1, ensure_ascii=True) + "\n"
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path} ({len(text)} bytes)")
        return 0
    committed = json.loads(path.read_text(encoding="utf-8"))
    if committed != json.loads(text):
        print(f"MISMATCH: rebuilt data differ from {path}", file=sys.stderr)
        return 1
    print(f"ok: rebuilt data match {path.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", choices=("delft", "beacon"))
    parser.add_argument("--write", action="store_true", help="overwrite the committed summary")
    parser.add_argument("--start", type=int, default=BEACON_START)
    parser.add_argument("--count", type=int, default=BEACON_COUNT)
    args = parser.parse_args(argv)
    if args.source == "delft":
        return _write_or_compare(build_delft_summary(_download(DELFT_ZIP_URL)), DELFT_SUMMARY_PATH, args.write)
    pulses = fetch_beacon_pulses(args.start, args.count)
    return _write_or_compare(build_beacon_summary(pulses), BEACON_SUMMARY_PATH, args.write)


if __name__ == "__main__":
    raise SystemExit(main())
