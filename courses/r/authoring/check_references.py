#!/usr/bin/env python3
"""Run owned R course programs in an existing offline image, with scoped cleanup."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import tomllib
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def program_records():
    records = []
    for path in sorted((HERE / "units").glob("r-*.json")):
        unit = json.loads(path.read_text())
        key = unit["id"]
        for kind, source in [
            ("starter", ROOT / f"courses/r/lessons/{key}.R"),
            ("reference", ROOT / f"courses/r/solutions/{key}_reference.R"),
        ]:
            records.append({"lesson": key, "kind": kind, "source": source.read_text()})
        records.extend(
            {"lesson": key, "kind": f"example-{i}", "source": example["code"]}
            for i, example in enumerate(unit["worked_examples"], 1)
        )
    return records


def run_program(record, image_id, timeout):
    name = "ds60-r-reference-" + uuid.uuid4().hex
    command = [
        "docker",
        "run",
        "--rm",
        "--pull",
        "never",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "128",
        "--memory",
        "1024m",
        "--cpus",
        "1",
        "--user",
        "10001:10001",
        "--tmpfs",
        "/tmp:rw,nosuid,nodev,noexec,size=268435456,mode=1777",
        "--workdir",
        "/tmp",
        "--env",
        "HOME=/tmp",
        "--env",
        "TMPDIR=/tmp",
        "--env",
        "OMP_NUM_THREADS=1",
        "--env",
        "OPENBLAS_NUM_THREADS=1",
        "-i",
        "--entrypoint",
        "Rscript",
        image_id,
        "--vanilla",
        "-",
    ]
    started = time.monotonic()
    result = {
        "lesson": record["lesson"],
        "kind": record["kind"],
        "source_sha256": hashlib.sha256(record["source"].encode()).hexdigest(),
    }
    try:
        completed = subprocess.run(
            command,
            input=record["source"],
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        result.update(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
        )
        result["passed"] = completed.returncode == 0
        if record["kind"] == "reference":
            marker = record["lesson"] + " reference checks passed"
            result["passed"] = result["passed"] and marker in completed.stdout
    except subprocess.TimeoutExpired:
        result.update(
            exit_code=None, stdout="", stderr="Program timeout", timed_out=True, passed=False
        )
    finally:
        # The UUID name belongs only to this invocation. Never prune shared state.
        subprocess.run(
            ["docker", "rm", "--force", name],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    result["seconds"] = round(time.monotonic() - started, 3)
    return result


def main():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default=f"ds60sqlpy-worker-r-statistics:{version}")
    parser.add_argument("--workers", type=int, choices=[1, 2], default=2)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300:
        parser.error("timeout must be from1 to300 seconds")
    subprocess.run([sys.executable, str(HERE / "build.py"), "--check"], check=True)
    inspected = subprocess.run(
        ["docker", "image", "inspect", args.image], capture_output=True, text=True, check=True
    )
    image = json.loads(inspected.stdout)[0]
    image_id = image["Id"]
    programs = program_records()
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(
            lambda item: run_program(item, image_id, args.timeout), programs
        ):
            results.append(result)
            state = "passed" if result["passed"] else "FAILED"
            print(f"{result['lesson']} {result['kind']}: {state}", flush=True)
    report = {
        "schema_version": 1,
        "evidence": "actual-offline-Rscript-programs",
        "image_requested": args.image,
        "image_id": image_id,
        "architecture": image["Architecture"],
        "programs": len(results),
        "passed": sum(r["passed"] for r in results),
        "results": results,
        "limits": [
            "Plain Rscript checks do not prove browser display or persistence.",
            "Graphics production must also be checked through the worker capture path.",
            "No image build, pull, registry publication or learner-volume operation occurs.",
        ],
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(f"R programs passed: {report['passed']}/{report['programs']}")
    return int(report["passed"] != report["programs"])


if __name__ == "__main__":
    raise SystemExit(main())
