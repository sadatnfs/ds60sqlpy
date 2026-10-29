#!/usr/bin/env python3
"""Qualify compiler errors and optional timeout recovery in a disposable classroom.

Every selected runtime must produce its real syntax diagnostic. The optional
Python Core timeout uses the supported 15-second worker deadline, followed by
successful reference execution. Submitted source is restored after each case;
notes and previous receipts are never replaced. Reports contain no session token
or saved learner source. No toolchain or external service is installed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.request import OpenerDirector, Request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_classroom_profiles import (  # noqa: E402
    CASES,
    TERMINAL,
    ClassroomClient,
    reference_source,
    verify_receipt,
)

INVALID_SOURCE = {
    "python-web": "def broken(:\n    pass\n",
    "data-engineering": "def broken(:\n    pass\n",
    "data-platforms-python": "def broken(:\n    pass\n",
    "dbt-duckdb": "select from\n",
    "stan-cpu": "parameters { real mu } model { mu ~ normal(0,1); }\n",
    "julia": "broken = )\n",
    "jax-cpu": "def broken(:\n    pass\n",
    "bayesian-cpu": "def broken(:\n    pass\n",
    "r-statistics": "broken <-\n",
    "php-cli": "<?php $broken = ;\n",
    "python-core": "def broken(:\n    pass\n",
    "tensorflow-cpu": "def broken(:\n    pass\n",
    "llm-torch-cpu": "def broken(:\n    pass\n",
    "spark-local-python": "def broken(:\n    pass\n",
    "cpp20": "int main( {\n",
    "c17": "int main( {\n",
    "rust-stable": "fn main() { let broken = ; }\n",
    "go": "package main\nfunc main( {\n",
    "csharp-dotnet": "public class Program { public static void Main() { int broken = ; } }\n",
    "swift-linux": "@main struct LessonMain { static func main() { let broken = } }\n",
    "java21": "public class Main { public static void main(String[] args) { int broken = ; } }\n",
    "javascript-node": "const broken = ;\n",
    "typescript-node": "const broken: = ;\n",
    "scala-jvm": "object Main { def main(args: Array[String]): Unit = { val broken = } }\n",
    "spark-local-scala": "object Main { def main(args: Array[String]): Unit = { val broken = } }\n",
}
DIAGNOSTICS = {
    "python-web": ("main.py", "syntaxerror"),
    "data-engineering": ("main.py", "syntaxerror"),
    "data-platforms-python": ("main.py", "syntaxerror"),
    "dbt-duckdb": ("lesson_model", "error"),
    "stan-cpu": ("main.stan", "syntax error"),
    "julia": ("main.jl", "parseerror"),
    "jax-cpu": ("main.py", "syntaxerror"),
    "bayesian-cpu": ("main.py", "syntaxerror"),
    "r-statistics": ("main.r", "error"),
    "php-cli": ("main.php", "parse error"),
    "python-core": ("main.py", "syntaxerror"),
    "tensorflow-cpu": ("main.py", "syntaxerror"),
    "llm-torch-cpu": ("main.py", "syntaxerror"),
    "spark-local-python": ("main.py", "syntaxerror"),
    "cpp20": ("main.cpp", "error"),
    "c17": ("main.c", "error"),
    "rust-stable": ("main.rs", "error"),
    "go": ("main.go", "syntax error"),
    "csharp-dotnet": ("program.cs", "error cs"),
    "swift-linux": ("main.swift", "error"),
    "java21": ("main.java", "error"),
    "javascript-node": ("main.mjs", "syntaxerror"),
    "typescript-node": ("main.mts", "error ts"),
    "scala-jvm": ("main.scala", "error"),
    "spark-local-scala": ("main.scala", "error"),
}
MAX_OUTPUT_BYTES = 128_000
JOB_WAIT_SECONDS = 90
CLEANUP_SECONDS = 10
TIMEOUT_SOURCE = (
    'import time\nprint("timeout-probe-started", flush=True)\ntime.sleep(60)\n'
    'print("timeout-probe-unexpected-completion", flush=True)\n'
)


class QualificationError(ValueError):
    """A safe, controlled diagnostic suitable for a public CI report."""


class BoundedOpener(OpenerDirector):
    """Keep each HTTP request and the current operation within its budget."""

    def __init__(self, delegate: OpenerDirector) -> None:
        super().__init__()
        self.delegate = delegate
        self.deadline = time.monotonic() + CLEANUP_SECONDS

    def open(self, fullurl: str | Request, data: Any = None, timeout: float | None = None) -> Any:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("The current qualification operation exceeded its budget.")
        return self.delegate.open(fullurl, data=data, timeout=min(timeout or 5, 5, remaining))


def budget(client: ClassroomClient, seconds: float) -> None:
    opener = getattr(client, "opener", None)
    if isinstance(opener, BoundedOpener):
        opener.deadline = time.monotonic() + seconds


def safe_error(exc: Exception) -> dict[str, str]:
    # Transport exceptions can contain private details. Only controlled messages
    # are copied; the exception class remains enough to identify transport loss.
    return {
        "type": type(exc).__name__,
        "detail": str(exc)
        if isinstance(exc, QualificationError)
        else "Qualification request failed.",
    }


def verify_failure(
    job: dict[str, Any],
    *,
    profile: str,
    lesson_id: str,
    job_id: str,
    source: str,
    timeout_case: bool = False,
    observed_seconds: float = 0,
) -> None:
    if (
        job.get("job_id") != job_id
        or job.get("lesson_id") != lesson_id
        or job.get("profile") != profile
        or job.get("source_sha256") != hashlib.sha256(source.encode("utf-8")).hexdigest()
    ):
        raise QualificationError(
            "Failure receipt does not identify the submitted source and context."
        )
    if job.get("status") != ("timed_out" if timeout_case else "failed"):
        raise QualificationError("The worker did not report the required failure status.")
    if type(job.get("returncode")) is not int or job["returncode"] == 0:
        raise QualificationError("Failure requires a real nonzero process return code.")
    output = job.get("output")
    if (
        not isinstance(output, str)
        or not output.strip()
        or len(output.encode("utf-8")) > MAX_OUTPUT_BYTES
        or job.get("truncated") is not False
    ):
        raise QualificationError(
            "The expected short diagnostic is missing, truncated or unbounded."
        )
    if timeout_case:
        if (
            job.get("timeout_seconds") != 15
            or not isinstance(job.get("elapsed_seconds"), (int, float))
            or job["elapsed_seconds"] < 14
            or observed_seconds < 14
            or "timeout-probe-started" not in output
            or "timeout-probe-unexpected-completion" in output
            or "deadline exceeded" not in str(job.get("detail", "")).lower()
        ):
            raise QualificationError("The receipt does not establish the real 15-second timeout.")
    elif not all(marker in output.lower() for marker in DIAGNOSTICS[profile]):
        raise QualificationError(
            "The runtime did not capture its expected source syntax diagnostic."
        )


def confirm_cancellation(client: ClassroomClient, expected: dict[str, Any]) -> str:
    """A successful cancel request is not proof that the worker has stopped."""
    deadline = time.monotonic() + CLEANUP_SECONDS
    client.call("module-cancel", job_id=expected["job_id"])
    while True:
        job = client.call("module-job", job_id=expected["job_id"])
        if any(
            job.get(key) != expected[key]
            for key in ("job_id", "lesson_id", "profile", "source_sha256")
        ):
            raise QualificationError("Cancellation readback belongs to a different submission.")
        if job.get("status") in TERMINAL - {"blocked", "interrupted"}:
            return str(job["status"])
        if time.monotonic() >= deadline:
            raise QualificationError("Cancellation outcome remains unconfirmed after its deadline.")
        time.sleep(0.2)


def exercise_case(
    client: ClassroomClient,
    profile: str,
    record: dict[str, Any],
    checkpoint: Callable[[], None],
    *,
    timeout_case: bool = False,
) -> None:
    lesson_id = CASES[profile][1]
    original: dict[str, Any] | None = None
    active: str | None = None
    terminal = True

    def submit(source: str, seconds: int, purpose: str) -> tuple[dict[str, Any], float]:
        nonlocal active, terminal
        budget(client, JOB_WAIT_SECONDS)
        started = time.monotonic()
        deadline = started + JOB_WAIT_SECONDS
        active, terminal = uuid.uuid4().hex, False
        receipt: dict[str, Any] = {
            "job_id": active,
            "purpose": purpose,
            "lesson_id": lesson_id,
            "profile": profile,
            "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "status": "submitting",
        }
        record["jobs"].append(receipt)
        checkpoint()
        client.call(
            "module-run",
            lesson_id=lesson_id,
            source=source,
            timeout_seconds=seconds,
            request_id=active,
        )
        while True:
            if time.monotonic() >= deadline:
                raise QualificationError(
                    "The worker did not reach a terminal result within 90 seconds."
                )
            job = client.call("module-job", job_id=active)
            if job.get("status") in TERMINAL:
                if any(
                    job.get(key) != receipt[key]
                    for key in ("job_id", "lesson_id", "profile", "source_sha256")
                ):
                    raise QualificationError(
                        "The terminal response belongs to a different submission."
                    )
                if job["status"] in {"interrupted", "blocked"}:
                    raise QualificationError(
                        "The worker result is unresolved; cancellation is required."
                    )
                terminal = True
                receipt.update(
                    {
                        "status": job["status"],
                        "returncode": job.get("returncode"),
                        "output_bytes": len(str(job.get("output", "")).encode("utf-8")),
                        "diagnostic_excerpt": str(job.get("output", ""))[:1200],
                    }
                )
                checkpoint()
                return job, time.monotonic() - started
            time.sleep(0.2)

    try:
        budget(client, 10)
        original = client.call("module-lesson", lesson_id=lesson_id)
        record["original_source_sha256"] = hashlib.sha256(original["source"].encode()).hexdigest()
        source = TIMEOUT_SOURCE if timeout_case else INVALID_SOURCE[profile]
        job, elapsed = submit(
            source, 15 if timeout_case else 60, "timeout" if timeout_case else "syntax"
        )
        verify_failure(
            job,
            profile=profile,
            lesson_id=lesson_id,
            job_id=str(active),
            source=source,
            timeout_case=timeout_case,
            observed_seconds=elapsed,
        )
        if timeout_case:
            recovered_id, _, reference = reference_source("python-core")
            if recovered_id != lesson_id:
                raise QualificationError("Recovery reference changed its lesson identity.")
            recovered, _ = submit(reference, 60, "recovery")
            verify_receipt(recovered, lesson_id, profile, reference)
            record["recovery_verified"] = True
        record["execution_verified"] = True
    except Exception as exc:
        record["errors"].append(safe_error(exc))
    finally:
        budget(client, CLEANUP_SECONDS)
        if active is not None and not terminal:
            try:
                record["cancellation_requested"] = True
                outcome = confirm_cancellation(client, record["jobs"][-1])
                record["cancellation_confirmed"] = True
                record["cancellation_outcome"] = outcome
            except Exception as exc:
                record["errors"].append({"phase": "cancel", **safe_error(exc)})
        if original is not None:
            try:
                client.call(
                    "module-save", lesson_id=lesson_id, fields={"source": original["source"]}
                )
                restored = client.call("module-lesson", lesson_id=lesson_id)
                notes_before = {k: v for k, v in original["session"].items() if k != "source"}
                notes_after = {k: v for k, v in restored["session"].items() if k != "source"}
                if restored["source"] != original["source"] or notes_before != notes_after:
                    raise QualificationError(
                        "The original saved source or notes were not restored."
                    )
                previous = next(
                    (r for r in original["history"] if r["status"] == "succeeded"), None
                )
                if previous is not None:
                    retained = client.call("module-job", job_id=previous["job_id"])
                    if any(
                        retained.get(k) != previous.get(k)
                        for k in (
                            "job_id",
                            "lesson_id",
                            "profile",
                            "source_sha256",
                            "status",
                            "returncode",
                        )
                    ):
                        raise QualificationError(
                            "The previous successful receipt was changed or lost."
                        )
                record["source_and_notes_restored"] = True
                record["previous_receipt_preserved"] = previous is not None
            except Exception as exc:
                record["errors"].append({"phase": "restore", **safe_error(exc)})
        record["passed"] = bool(record.get("execution_verified")) and not record["errors"]
        checkpoint()


def qualify(
    client: ClassroomClient,
    profiles: list[str],
    report: dict[str, Any],
    checkpoint: Callable[[], None],
    *,
    check_timeout: bool = False,
) -> None:
    if not profiles or set(profiles) - INVALID_SOURCE.keys():
        raise QualificationError("Choose registered ordinary profiles only.")
    if check_timeout and "python-core" not in profiles:
        raise QualificationError("Timeout qualification requires the selected Python Core profile.")
    ready = {row["profile"] for row in client.call("module-readiness")["profiles"] if row["ready"]}
    if set(profiles) - ready:
        raise QualificationError(
            "A requested runtime is unavailable; no unavailable profile is skipped."
        )
    # Profile readiness retains ClassroomClient's ordinary 45-second API bound.
    # Only submitted jobs and their cleanup use the stricter operation budget.
    original_opener = client.opener
    client.opener = BoundedOpener(original_opener)
    try:
        cases = [(profile, False) for profile in dict.fromkeys(profiles)]
        if check_timeout:
            cases.append(("python-core", True))
        for position, (profile, timeout_case) in enumerate(cases):
            record: dict[str, Any] = {
                "profile": profile,
                "case": "timeout-and-recovery" if timeout_case else "syntax",
                "jobs": [],
                "errors": [],
                "passed": False,
            }
            report["cases"].append(record)
            checkpoint()
            exercise_case(client, profile, record, checkpoint, timeout_case=timeout_case)
            print(
                f"{'PASS' if record['passed'] else 'FAIL'}: {profile}: {record['case']}", flush=True
            )
            if not record.get("source_and_notes_restored") or any(
                error.get("phase") == "cancel" for error in record["errors"]
            ):
                report["unattempted"] = [profile for profile, _ in cases[position + 1 :]]
                report["errors"].append(
                    {
                        "type": "CleanupUnconfirmed",
                        "detail": "Further cases stopped because cleanup could not be confirmed.",
                    }
                )
                checkpoint()
                return
        report["passed"] = bool(report["cases"]) and all(row["passed"] for row in report["cases"])
        checkpoint()
    finally:
        client.opener = original_opener


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--check-timeout", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error("This submits failing code. Use --confirm-disposable only on a test project.")
    profiles = args.profiles.split()
    if not profiles or set(profiles) - INVALID_SOURCE.keys():
        parser.error("Profiles must be selected from: " + ", ".join(INVALID_SOURCE))
    if args.check_timeout and "python-core" not in profiles:
        parser.error("--check-timeout requires python-core.")
    report: dict[str, Any] = {
        "schema_version": 1,
        "profiles": sorted(set(profiles)),
        "cases": [],
        "errors": [],
        "timeout_requested": args.check_timeout,
        "passed": False,
    }

    def checkpoint() -> None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")

    checkpoint()
    try:
        client = ClassroomClient(args.url)
        qualify(client, profiles, report, checkpoint, check_timeout=args.check_timeout)
    except Exception as exc:
        report["errors"].append(safe_error(exc))
    finally:
        checkpoint()
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
