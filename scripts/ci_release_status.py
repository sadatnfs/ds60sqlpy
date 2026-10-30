"""Wait for successful source and starter checks at the exact marked main revision."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

WORKFLOWS = {
    ".github/workflows/ci.yml": (
        "Source formatting and lint (main, Linux Docker)",
        "Source formatting and lint (r, Linux Docker)",
        "Source formatting and lint (julia, Linux Docker)",
        "Core checks (Linux, Python 3.11)",
        "Core checks (Linux, Python 3.12)",
        "Linux contributor bootstrap (Python 3.12)",
        "PostgreSQL 17 end-to-end",
    ),
    ".github/workflows/app-build.yml": ("Portable Docker classroom starter",),
    ".github/workflows/verify-torch-package.yml": (
        "Independent Spark PyTorch (amd64)",
        "Independent Spark PyTorch (arm64)",
    ),
}
TORCH_WORKFLOW = ".github/workflows/verify-torch-package.yml"


def selected_runs(pages: Any, revision: str) -> dict[str, dict[str, Any]]:
    if not isinstance(pages, list) or not pages or len(pages) > 100:
        raise ValueError("Invalid exact-revision workflow listing")
    all_runs = []
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("workflow_runs"), list):
            raise ValueError("Invalid workflow response")
        all_runs.extend(page["workflow_runs"])
    result = {}
    for path in WORKFLOWS:
        required_event = "workflow_dispatch" if path == TORCH_WORKFLOW else "push"
        allowed = {path, path + "@main", path + "@refs/heads/main", path + "@" + revision}
        matches = [
            run
            for run in all_runs
            if isinstance(run, dict)
            and run.get("path") in allowed
            and run.get("event") == required_event
            and run.get("head_branch") == "main"
            and run.get("head_sha") == revision
        ]
        if not matches:
            continue
        if any(
            type(row.get("id")) is not int
            or type(row.get("run_attempt")) is not int
            or row["id"] < 1
            or row["run_attempt"] < 1
            for row in matches
        ):
            raise ValueError("Invalid qualification run identity")
        latest = max(matches, key=lambda row: (row["id"], row["run_attempt"]))
        if latest.get("status") == "completed" and latest.get("conclusion") != "success":
            raise ValueError("Exact-revision qualification is not successful: " + path)
        result[path] = latest
    return result


def successful_jobs(pages: Any, required: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(pages, list) or not pages or len(pages) > 100:
        raise ValueError("Invalid qualification job listing")
    jobs = []
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("jobs"), list):
            raise ValueError("Invalid qualification job response")
        jobs.extend(page["jobs"])
    accepted = []
    for name in required:
        matches = [row for row in jobs if isinstance(row, dict) and row.get("name") == name]
        if not matches or any(type(row.get("id")) is not int or row["id"] < 1 for row in matches):
            raise ValueError("A required qualification job is missing: " + name)
        latest_id = max(row["id"] for row in matches)
        latest = [row for row in matches if row["id"] == latest_id]
        if (
            len(latest) != 1
            or latest[0].get("status") != "completed"
            or latest[0].get("conclusion") != "success"
        ):
            raise ValueError("A required qualification job did not succeed: " + name)
        accepted.append({"id": latest_id, "name": name, "conclusion": "success"})
    return accepted


def api(path: str) -> Any:
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", path],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode or len(result.stdout.encode()) > 8 * 1024 * 1024:
        raise ValueError("Could not read bounded GitHub qualification metadata")
    return json.loads(result.stdout)


def wait_for_qualification(
    repository: str, revision: str, *, timeout_seconds: float = 5400
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        runs = selected_runs(
            api(f"repos/{repository}/actions/runs?head_sha={revision}&per_page=100"), revision
        )
        if set(runs) == set(WORKFLOWS) and all(
            run.get("status") == "completed" for run in runs.values()
        ):
            proofs = []
            for path, run in runs.items():
                # filter=all retains successful jobs when only failed jobs were rerun.
                jobs = successful_jobs(
                    api(
                        f"repos/{repository}/actions/runs/{run['id']}/jobs?filter=all&per_page=100"
                    ),
                    WORKFLOWS[path],
                )
                proofs.append(
                    {
                        "path": path,
                        "run_id": run["id"],
                        "run_attempt": run["run_attempt"],
                        "jobs": jobs,
                    }
                )
            return {
                "schema_version": 1,
                "repository": repository,
                "revision": revision,
                "complete": True,
                "passed": True,
                "workflows": proofs,
            }
        if time.monotonic() >= deadline:
            raise TimeoutError(
                "Exact-revision qualification did not complete within the gate budget"
            )
        print(
            "Waiting for source and Docker starter checks for this exact main revision.", flush=True
        )
        time.sleep(min(30, max(0, deadline - time.monotonic())))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--timeout-minutes", type=int, default=90)
    args = parser.parse_args()
    repository, revision = os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_SHA", "")
    if (
        re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None
        or re.fullmatch(r"[a-f0-9]{40}", revision) is None
        or not 1 <= args.timeout_minutes <= 100
    ):
        parser.error("Supply a bounded GitHub repository/revision qualification context")
    report = wait_for_qualification(repository, revision, timeout_seconds=args.timeout_minutes * 60)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("Exact-revision source and Docker starter qualification passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TimeoutError, subprocess.SubprocessError) as error:
        print("Release qualification gate failed: " + str(error))
        raise SystemExit(1) from None
