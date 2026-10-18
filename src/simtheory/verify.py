"""One entry point for every reproducible check in the repository.

Run ``python -m simtheory verify`` (or ``make verify``). The steps are:

1. byte-compile ``src``;
2. validate every ``claims/*.json`` manifest: schema, globally unique IDs,
   evidence files, Markdown anchors, and ``file.py:symbol`` references; and
   every ``paper/*/claims.json`` ledger: unique IDs, assumptions, nonclaims,
   and a ``tests/test_paper_*`` file that checks it;
3. recompute the real-data receipts (Delft 2015 CHSH statistic and NIST beacon
   precommitments) from the committed summaries;
4. rerun the deterministic experiment suite and compare it with
   ``receipts/experiments.txt``;
5. run the test suite once and report, per claim, whether every test file it
   cites passed.

``--quick`` skips tests marked ``slow`` (about ten minutes of exhaustive checks);
claims citing those files are then reported as partially checked. ``--online`` also downloads the public data
again and checks that it reduces to the committed summaries.
"""

from __future__ import annotations

import argparse
import compileall
import contextlib
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from pathlib import Path

from .claims import load_claim_manifest, validate_local_evidence_paths

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "receipts" / "experiments.txt"
_NUMBER = re.compile(r"-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def step(self, name: str) -> None:
        print(f"\n== {name} ==", flush=True)

    def ok(self, message: str) -> None:
        print(f"  ok    {message}", flush=True)

    def fail(self, message: str) -> None:
        print(f"  FAIL  {message}", flush=True)
        self.failures.append(message)


def _symbol_defined(path: Path, symbol: str) -> bool:
    text = path.read_text(encoding="utf-8")
    name = re.escape(symbol.split(".")[-1])
    pattern = rf"^\s*(?:async\s+def|def|class)\s+{name}\b|^{name}\s*(?::[^=]*)?="
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def check_manifests(report: Report) -> dict[str, list[str]]:
    """Validate all manifests; return claim id -> cited test files."""

    report.step("claim manifests")
    seen: dict[str, str] = {}
    cited_tests: dict[str, list[str]] = {}
    kinds: dict[str, int] = defaultdict(int)
    paths = sorted((ROOT / "claims").glob("*.json"))
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        try:
            manifest = load_claim_manifest(path)
            validate_local_evidence_paths(manifest, ROOT)
        except (ValueError, json.JSONDecodeError) as error:
            report.fail(f"{name}: {error}")
            continue
        for claim in manifest["claims"]:
            identifier = claim["id"]
            if identifier in seen:
                report.fail(f"{identifier} appears in both {seen[identifier]} and {name}")
            seen[identifier] = name
            kinds[claim["kind"]] += 1
            if not claim["nonclaims"]:
                report.fail(f"{identifier} has no nonclaims")
            tests: list[str] = []
            for evidence in claim["evidence"]:
                if evidence.startswith(("http://", "https://")) or "#" in evidence:
                    continue
                file_part, _, symbol = evidence.partition(":")
                if symbol and not _symbol_defined(ROOT / file_part, symbol):
                    report.fail(f"{identifier}: {file_part} does not define {symbol}")
                if file_part.startswith("tests/") and file_part.endswith(".py"):
                    tests.append(file_part)
            if not tests and claim["kind"] != "OPEN_PROBLEM":
                report.fail(f"{identifier} cites no test file")
            cited_tests[identifier] = tests
    summary = ", ".join(f"{count} {kind.lower()}" for kind, count in sorted(kinds.items()))
    report.ok(f"{len(paths)} manifests, {len(seen)} claims ({summary})")
    cited_tests.update(check_paper_ledgers(report, seen))
    return cited_tests


def check_paper_ledgers(report: Report, repository_ids: dict[str, str]) -> dict[str, list[str]]:
    """Validate each paper/<name>/claims.json against the tests/test_paper_* files that check it."""

    cited: dict[str, list[str]] = {}
    for path in sorted((ROOT / "paper").glob("*/claims.json")):
        name = path.relative_to(ROOT).as_posix()
        slug = path.parent.name.replace("-", "_")
        found = {p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob(f"test_paper_{slug}*.py")}
        # A paper's own workflow names every test file that checks it.
        for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
            text = workflow.read_text(encoding="utf-8")
            if f"paper/{path.parent.name}" in text:
                found.update(f"tests/{m}" for m in re.findall(r"(test_paper_\w+\.py)", text))
        tests = sorted(t for t in found if (ROOT / t).is_file())
        try:
            claims = json.loads(path.read_text(encoding="utf-8"))["claims"]
        except (OSError, ValueError, KeyError) as error:
            report.fail(f"{name}: {error}")
            continue
        if not isinstance(claims, list) or not claims:
            report.fail(f"{name}: no claims")
            continue
        if not tests:
            report.fail(f"{name}: no tests/test_paper_* file checks this ledger")
        local: set[str] = set()
        for claim in claims:
            identifier = claim.get("id") if isinstance(claim, dict) else None
            if not isinstance(identifier, str) or not identifier:
                report.fail(f"{name}: claim without an id")
                continue
            if identifier in local or identifier in repository_ids:
                report.fail(f"{name}: duplicate claim id {identifier}")
            local.add(identifier)
            if not claim.get("assumptions") or not claim.get("nonclaims"):
                report.fail(f"{name}: {identifier} needs assumptions and nonclaims")
            cited[f"{path.parent.name}:{identifier}"] = tests
        report.ok(f"{name}: {len(local)} paper claims, checked by {', '.join(tests) or 'no tests'}")
    return cited


def check_real_data(report: Report, online: bool) -> None:
    from .real_data import (
        beacon_bits,
        binomial_upper_tail,
        canonical_disk_point,
        chsh_summary,
        kt_log_bayes_factor_path,
        load_beacon_summary,
        load_delft_summary,
        local_win_probability_bound,
    )

    report.step("real-data receipts")
    try:
        payload, trials = load_delft_summary()
        summary = chsh_summary(trials)
        published = payload["source"]["published_values"]
        p_value = binomial_upper_tail(summary.wins, summary.trials, local_win_probability_bound())
        matches = (
            summary.trials == published["trials"]
            and round(summary.s_value, 2) == published["S"]
            and round(summary.s_error, 2) == published["S_error"]
            and round(p_value, 3) == published["p_value"]
        )
        x, y = canonical_disk_point(summary.correlations)
        message = (
            f"Delft 2015: n={summary.trials} k={summary.wins} S={summary.s_value:.3f}+-{summary.s_error:.3f} "
            f"p={p_value:.4f} disk q=({x:.3f},{y:.3f}) [published S=2.42+-0.20, p=0.039]"
        )
        (report.ok if matches else report.fail)(message)
    except (OSError, ValueError, KeyError) as error:
        report.fail(f"Delft summary: {error}")
    try:
        beacon, pulses = load_beacon_summary()
        bits = beacon_bits(pulses[:-1])
        path = kt_log_bayes_factor_path(bits)
        below = max(path) < math.log(100)
        message = (
            f"NIST beacon: {len(pulses) - 1} precommitment links verified, {len(bits)} bits, "
            f"max log BF {max(path):.2f} < ln 100"
        )
        (report.ok if below else report.fail)(message)
    except (OSError, ValueError, KeyError) as error:
        report.fail(f"beacon summary: {error}")
    if online:
        for source in ("delft", "beacon"):
            result = subprocess.run(
                [sys.executable, "-m", "simtheory.real_data_fetch", source],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            text = (result.stdout + result.stderr).strip()
            (report.ok if result.returncode == 0 else report.fail)(f"online {source}: {text}")


def _lines_match(expected: str, actual: str) -> bool:
    if _NUMBER.sub("#", expected) != _NUMBER.sub("#", actual):
        return False
    for a, b in zip(_NUMBER.findall(expected), _NUMBER.findall(actual)):
        if not math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-12):
            return False
    return True


def check_experiments(report: Report, update: bool) -> None:
    from . import experiments

    report.step("deterministic experiments")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        experiments.main()
    output = buffer.getvalue()
    if update:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(output, encoding="utf-8")
        report.ok(f"wrote {RECEIPT.relative_to(ROOT)}")
        return
    if not RECEIPT.is_file():
        report.fail(f"missing receipt {RECEIPT.relative_to(ROOT)}; run with --update-receipt")
        return
    expected = RECEIPT.read_text(encoding="utf-8").splitlines()
    actual = output.splitlines()
    if len(expected) != len(actual):
        report.fail(f"experiment output has {len(actual)} lines, receipt has {len(expected)}")
        return
    bad = [i + 1 for i, (e, a) in enumerate(zip(expected, actual)) if not _lines_match(e, a)]
    if bad:
        report.fail(f"experiment output differs from receipt on lines {bad[:10]}")
    else:
        report.ok(f"{len(actual)} lines match {RECEIPT.relative_to(ROOT)} (relative tolerance 1e-9)")


def run_tests(report: Report, quick: bool, cited_tests: dict[str, list[str]]) -> None:
    report.step("test suite" + (" (quick: slow tests skipped)" if quick else ""))
    with tempfile.TemporaryDirectory() as directory:
        junit = Path(directory) / "junit.xml"
        command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"]
        environment = dict(os.environ, SIMTHEORY_QUICK="1" if quick else "0")
        result = subprocess.run(command, cwd=ROOT, env=environment)
        if not junit.is_file():
            report.fail("pytest did not run; install the dev group with `uv sync`")
            return
        per_file: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for case in ElementTree.parse(junit).getroot().iter("testcase"):
            module = case.get("classname", "").split(".")
            path = "/".join(module[: module.index(next(m for m in module if m.startswith("test_"))) + 1]) + ".py"
            status = "passed"
            for child in case:
                if child.tag in ("failure", "error"):
                    status = "failed"
                elif child.tag == "skipped" and status == "passed":
                    status = "skipped"
            per_file[path][status] += 1
    passed = sum(c["passed"] for c in per_file.values())
    failed = sum(c["failed"] for c in per_file.values())
    skipped = sum(c["skipped"] for c in per_file.values())
    message = f"{passed} passed, {failed} failed, {skipped} skipped across {len(per_file)} files"
    (report.ok if result.returncode == 0 and failed == 0 else report.fail)(message)

    report.step("claims against their cited tests")
    full, partial, broken = 0, [], []
    for identifier, files in sorted(cited_tests.items()):
        if not files:
            continue
        states = [per_file.get(f) for f in files]
        if any(state is None or state["passed"] == 0 for state in states):
            broken.append(identifier)
        elif any(state["failed"] for state in states):
            broken.append(identifier)
        elif any(state["skipped"] for state in states):
            partial.append(identifier)
        else:
            full += 1
    if broken:
        report.fail(f"claims whose cited tests failed or did not run: {', '.join(broken)}")
    note = f"; {len(partial)} partially checked because slow tests were skipped" if partial else ""
    report.ok(f"{full} claims have every cited test file passing{note}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m simtheory verify", description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="skip tests marked slow")
    parser.add_argument("--online", action="store_true", help="also re-download and re-reduce public data")
    parser.add_argument("--no-tests", action="store_true", help="skip the test suite")
    parser.add_argument("--update-receipt", action="store_true", help="rewrite receipts/experiments.txt")
    args = parser.parse_args(argv)

    report = Report()
    report.step("byte-compile src")
    if compileall.compile_dir(str(ROOT / "src"), quiet=1):
        report.ok("src compiles")
    else:
        report.fail("compileall reported errors")
    cited = check_manifests(report)
    check_real_data(report, args.online)
    check_experiments(report, args.update_receipt)
    if not args.no_tests:
        run_tests(report, args.quick, cited)

    print()
    if report.failures:
        print(f"verify: {len(report.failures)} failure(s)")
        return 1
    print("verify: all checks passed")
    return 0
