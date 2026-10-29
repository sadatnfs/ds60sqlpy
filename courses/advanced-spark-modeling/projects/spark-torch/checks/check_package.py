"""Aggregate exact installed-wheel, numerical, Spark and ML evidence without masking failures."""

from __future__ import annotations

import contextlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command, *, seconds=900):
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True
        )
        started = time.monotonic()
        try:
            while process.poll() is None:
                if time.monotonic() - started > seconds:
                    raise TimeoutError("Standalone package acceptance exceeded its time bound")
                if os.fstat(log.fileno()).st_size > 32 * 1024 * 1024:
                    raise RuntimeError("Standalone package log exceeded its output bound")
                time.sleep(0.1)
            log.seek(0)
            output = log.read(32 * 1024 * 1024 + 1)
            if len(output) > 32 * 1024 * 1024:
                raise RuntimeError("Standalone package log exceeded its output bound")
            text = output.decode("utf-8", errors="replace")
            for line in text.splitlines():
                print("[package-child] " + line, file=sys.stderr)
            if process.returncode:
                raise RuntimeError(
                    f"Standalone package child failed with exit {process.returncode}"
                )
            return [json.loads(line) for line in text.splitlines() if line.startswith("{")]
        finally:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGTERM)
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=5)
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main():
    entry = str(ROOT / "package_entry.py")
    identities = run([sys.executable, "-I", entry, "identity"], seconds=60)
    assert len(identities) == 1 and identities[0]["isolated_python"] is True
    identity = identities[0]
    spark = [
        "/opt/spark/bin/spark-submit",
        "--driver-memory",
        "768m",
        "--conf",
        "spark.jars.ivy=/tmp/ivy",
        entry,
    ]
    workers = run([*spark, "workers"], seconds=180)
    assert len(workers) == 1 and workers[0]["passed"] is True
    for worker in workers[0]["records"]:
        for key in (
            "distribution",
            "version",
            "package_path",
            "installed_source",
            "classroom_imported",
            "r_dependency_required",
        ):
            assert worker[key] == identity[key]
    observations = {
        "numerical": run([sys.executable, "-I", entry, "numerical"]),
        "spark": run([*spark, "spark"]),
        "ml": run([*spark, "ml"]),
    }
    assert all(record.get("passed") is True for rows in observations.values() for record in rows)
    print(
        json.dumps(
            {
                "case": "standalone-package",
                "schema_version": 1,
                "passed": True,
                "isolated_wheel_install": True,
                "r_dependency_required": False,
                "identity": identity,
                "executor_imports": workers[0],
                "observations": observations,
            },
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
