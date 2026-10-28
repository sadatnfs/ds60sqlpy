#!/usr/bin/env python3
"""Execute the Julia course in an explicitly prepared offline Julia environment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

COURSE = Path(__file__).resolve().parents[1]
ROOT = COURSE.parents[1]


def expected_figures(number: int, kind: str) -> int:
    if number not in {20, 24, 32}:
        return 0
    if kind == "reference":
        return 1
    if number == 24:
        return int(kind in {"worked_a", "learner"})
    return int(kind == "worked_b")


def validate_figures(payload: Any, expected: int) -> None:
    if not isinstance(payload, list) or len(payload) != expected:
        raise ValueError(f"Expected {expected} captured figures")
    for artifact in payload:
        if artifact.get("kind") != "plotly" or not artifact.get("description"):
            raise ValueError("Plotly kind and description are required")
        figure = artifact.get("figure", {})
        metadata = figure.get("layout", {}).get("meta", {})
        table = metadata.get("table", {})
        columns, rows = table.get("columns"), table.get("rows")
        if not metadata.get("description") or not columns or not rows:
            raise ValueError("Exact table and accessible description are required")
        if any(len(row) != len(columns) for row in rows):
            raise ValueError("Figure table columns and rows disagree")
        if not figure.get("data"):
            raise ValueError("Captured chart has no data")


def execute(
    source: Path,
    command: list[str],
    expected: int,
    marker: str | None,
    *,
    stage: bool = True,
) -> dict[str, Any]:
    environment = dict(os.environ, JULIA_PKG_OFFLINE="true", JULIA_NUM_THREADS="2")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="julia-course-check-") as temporary:
        folder = Path(temporary)
        submitted = folder / "main.jl" if stage else source
        if stage:
            submitted.write_bytes(source.read_bytes())
        process = subprocess.run(
            [*command, str(submitted)],
            cwd=folder,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        artifact_path = folder / "ds60-figures.json"
        payload = json.loads(artifact_path.read_text()) if artifact_path.exists() else []
        error = ""
        try:
            if process.returncode:
                raise ValueError(f"Julia exited {process.returncode}")
            if marker is not None and marker not in process.stdout:
                raise ValueError("Expected completion marker is absent")
            validate_figures(payload, expected)
        except ValueError as exception:
            error = str(exception)
        return {
            "source": str(source.relative_to(COURSE)),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "returncode": process.returncode,
            "seconds": round(time.monotonic() - started, 3),
            "stdout": process.stdout,
            "stderr": process.stderr,
            "artifacts": payload,
            "error": error,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--julia", default="julia")
    parser.add_argument("--project", type=Path, default=Path("/opt/julia-env"))
    parser.add_argument("--helper", type=Path, default=ROOT / "src/ds60sqlpy/worker_figures.jl")
    parser.add_argument("--all-worked", action="store_true")
    parser.add_argument("--learners", action="store_true")
    parser.add_argument("--independent-only", action="store_true")
    args = parser.parse_args()
    if not args.helper.is_file() or not (args.project / "Project.toml").is_file():
        parser.error("Prepare the locked Julia project and classroom figure helper first")
    command = [
        args.julia,
        "--startup-file=no",
        "--history-file=no",
        "--color=no",
        "--compiled-modules=existing",
        f"--project={args.project.resolve()}",
        "--threads=2",
        "-L",
        str(args.helper.resolve()),
    ]
    failures = 0
    if not args.independent_only:
        kinds = ["reference"]
        if args.all_worked:
            kinds.extend(["worked_a", "worked_b"])
        if args.learners:
            kinds.append("learner")
        for number in range(1, 33):
            for kind in kinds:
                key = f"julia-{number:03}"
                source = COURSE / "authoring/programs" / f"{key}_{kind}.jl"
                marker = f"{key}: all reference checks passed" if kind == "reference" else None
                row = execute(source, command, expected_figures(number, kind), marker)
                failures += bool(row["error"])
                print(json.dumps(row), flush=True)
    row = execute(
        COURSE / "authoring/independent_checks.jl",
        command,
        0,
        "Julia independent contracts passed",
        stage=False,
    )
    failures += bool(row["error"])
    print(json.dumps(row), flush=True)
    row = execute(
        COURSE / "authoring/formatter_contract.jl",
        command,
        0,
        "Julia formatter semantic contracts passed",
        stage=False,
    )
    failures += bool(row["error"])
    print(json.dumps(row), flush=True)
    return int(failures != 0)


if __name__ == "__main__":
    raise SystemExit(main())
