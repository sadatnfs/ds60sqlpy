#!/usr/bin/env python3
"""Record app-build CI runtime evidence in the track qualification ledger.

Reads one GitHub Actions run of `.github/workflows/app-build.yml` with
`gh run view RUN --repo REPO --json headSha,conclusion,jobs,workflowName`.
Each ordinary CI group runs as the job `Docker classroom (<group>)`, whose
`Qualify complete references...` step runs `scripts/ci_classroom.py qualify`
(the reference corpus, including walkthrough `expected_output` assertions).

A track gains `runtime.evidence`, `walkthrough_outputs_checked: true` and an
R10 `pass` only when the job and qualify step of every ordinary CI group it
uses concluded `success`. Nothing is recorded for any other track. The run's
commit must be available locally, and the course content and reference checker
in the working tree must equal that commit, so the evidence applies to the
walkthroughs being recorded. Use `--dry-run` to print the plan without writing.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts import check_track_qualification as qualification  # noqa: E402
from scripts.ci_profiles import groups  # noqa: E402

REPO = "sadatnfs/ds60sqlpy"
WORKFLOW_NAME = "Application builds"
JOB_NAME = re.compile(r"Docker classroom \(([a-z][a-z0-9-]{0,40})\)")
QUALIFY_STEP_PREFIX = "Qualify complete references"
RUN_ID = re.compile(r"[0-9]{1,20}")
# Inputs the qualify jobs execute for walkthrough assertions; they must match the run commit.
SOURCE_PATHS = (
    "courses",
    "scripts/check_module_references.py",
    "src/ds60sqlpy/walkthroughs.py",
)
PRINT_WIDTH = 80


def fetch_run(run_id: str, repo: str = REPO) -> dict[str, Any]:
    """Read-only `gh run view` call; never triggers or changes a run."""
    result = subprocess.run(
        [
            "gh",
            "run",
            "view",
            run_id,
            "--repo",
            repo,
            "--json",
            "headSha,conclusion,jobs,workflowName",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh run view {run_id} failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("gh run view returned an unexpected payload.")
    return payload


def parse_run(payload: dict[str, Any], known_groups: set[str]) -> tuple[str, dict[str, str]]:
    """Return the run commit and the outcome of each known group's qualify job.

    An outcome is `success` only when the group job and its qualify step both
    concluded `success`; repeated jobs for one group must all succeed.
    """
    if payload.get("workflowName") != WORKFLOW_NAME:
        raise ValueError(f"Run is not from the {WORKFLOW_NAME!r} workflow (app-build.yml).")
    commit = payload.get("headSha")
    if not isinstance(commit, str) or qualification.COMMIT.fullmatch(commit) is None:
        raise ValueError("Run headSha is not a 40 character lowercase hex commit.")
    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("Run payload has no job list.")
    outcomes: dict[str, str] = {}
    for job in jobs:
        if not isinstance(job, dict):
            continue
        match = JOB_NAME.fullmatch(str(job.get("name", "")))
        if match is None or match.group(1) not in known_groups:
            continue
        group = match.group(1)
        steps = [
            step
            for step in job.get("steps") or []
            if isinstance(step, dict) and str(step.get("name", "")).startswith(QUALIFY_STEP_PREFIX)
        ]
        if job.get("conclusion") != "success":
            outcome = f"job {job.get('conclusion') or job.get('status') or 'unknown'}"
        elif len(steps) != 1:
            outcome = "qualify step not found"
        elif steps[0].get("conclusion") != "success":
            outcome = f"qualify step {steps[0].get('conclusion') or 'unknown'}"
        else:
            outcome = "success"
        if outcomes.get(group, "success") == "success":
            outcomes[group] = outcome
    return commit, outcomes


def plan_updates(
    ledger: dict[str, Any], run_id: str, commit: str, outcomes: dict[str, str]
) -> tuple[dict[str, Any], list[str]]:
    """Return an updated ledger copy and one human-readable line per affected track."""
    updated = copy.deepcopy(ledger)
    lines: list[str] = []
    for record in updated["tracks"]:
        required = qualification.required_ci_groups(record)
        if not required:
            continue
        failing = {group: outcomes.get(group, "no job in run") for group in required}
        failing = {group: outcome for group, outcome in failing.items() if outcome != "success"}
        track = record["track"]
        if failing:
            detail = ", ".join(f"{group} ({outcome})" for group, outcome in sorted(failing.items()))
            lines.append(f"SKIP {track}: {detail}")
            continue
        runtime = record["runtime"]
        runtime["walkthrough_outputs_checked"] = True
        runtime["evidence"] = {"ci_run": run_id, "commit": commit, "groups": required}
        record["criteria"]["R10"] = {"status": "pass"}
        lines.append(f"RECORD {track}: run {run_id}, commit {commit}, groups {required}")
    return updated, lines


def source_matches_commit(root: Path, commit: str) -> str | None:
    """Return a problem message unless the working tree inputs equal the run commit."""
    known = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=root, capture_output=True
    )
    if known.returncode != 0:
        return f"Commit {commit} is not available locally; run git fetch first."
    diff = subprocess.run(
        ["git", "diff", "--quiet", commit, "--", *SOURCE_PATHS], cwd=root, capture_output=True
    )
    if diff.returncode != 0:
        return (
            f"The working tree differs from {commit} in {', '.join(SOURCE_PATHS)}; "
            "the run does not cover the current walkthroughs."
        )
    return None


def _scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def dump_json(value: Any, indent: int = 0, used: int = 0) -> str:
    """Serialize like Prettier: objects expanded, scalar arrays inline when they fit.

    `used` is the width already taken on the current line (indent and key); a
    trailing comma is counted so a fitting inline array never exceeds 80 columns.
    """
    pad = " " * indent
    inner = " " * (indent + 2)
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for key, item in value.items():
            head = f"{inner}{_scalar(key)}: "
            items.append(head + dump_json(item, indent + 2, len(head)))
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        if all(not isinstance(item, (dict, list)) for item in value):
            flat = "[" + ", ".join(_scalar(item) for item in value) + "]"
            if max(used, indent) + len(flat) + 1 <= PRINT_WIDTH:
                return flat
        items = [inner + dump_json(item, indent + 2, indent + 2) for item in value]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return _scalar(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", required=True, help="app-build.yml run database ID")
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--dry-run", action="store_true", help="Print the plan; write nothing.")
    args = parser.parse_args(argv)
    if RUN_ID.fullmatch(args.run) is None:
        print("FAIL --run must be a numeric run ID.", file=sys.stderr)
        return 2
    known = {row["id"] for row in groups(args.root)}
    try:
        commit, outcomes = parse_run(fetch_run(args.run, args.repo), known)
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    problem = source_matches_commit(args.root, commit)
    if problem:
        print(f"FAIL {problem}", file=sys.stderr)
        return 1
    ledger = qualification.load_ledger(args.root)
    updated, lines = plan_updates(ledger, args.run, commit, outcomes)
    for line in lines:
        print(line)
    matrix = qualification.load_matrix(args.root)
    problems = [
        message
        for record in updated["tracks"]
        for message in qualification.evaluate_track(matrix, record, args.root)
    ]
    if problems:
        for message in problems:
            print(f"FAIL {message}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("Dry run: the ledger was not written.")
        return 0
    path = args.root / qualification.LEDGER
    path.write_text(dump_json(updated) + "\n", encoding="utf-8")
    print(f"Wrote {qualification.LEDGER}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
