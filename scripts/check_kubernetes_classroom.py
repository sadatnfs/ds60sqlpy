#!/usr/bin/env python3
"""Qualify the optional owned Kubernetes worker through a disposable classroom.

This probe never chooses a kubeconfig, creates a cluster or installs tools. The
separate host preparation helper owns those actions. Only reviewed fixed fixture
sources are submitted, and saved reports contain no session credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_classroom_failures import BoundedOpener, budget  # noqa: E402
from scripts.check_classroom_profiles import TERMINAL, ClassroomClient  # noqa: E402

CANCEL_SECONDS = 15


@dataclass(frozen=True)
class Case:
    name: str
    lesson_id: str
    source_path: str
    status: str = "succeeded"
    required_checks: tuple[str, ...] = ()
    timeout_seconds: int = 120
    cancel_after_submission: bool = False
    unready: bool = False


HELLO = "courses/kubernetes/solutions/k8s-008_solution.yaml"
ROUTING = ("controller-and-pods", "ready-service-backends", "in-cluster-version")
REFERENCE_CHECKS = {
    "k8s-003": ("controller-and-pods",),
    "k8s-005": ("controller-and-pods",),
    "k8s-006": ("controller-and-pods",),
    "k8s-007": ROUTING,
    "k8s-008": ROUTING,
    "k8s-009": (*ROUTING, "configmap-environment", "configmap-mounted-file"),
    "k8s-010": ("controller-and-pods",),
    "k8s-011": ("owned-finite-task",),
    "k8s-014": (*ROUTING, "configmap-environment", "configmap-mounted-file"),
    "k8s-015": ROUTING,
    "k8s-017": ("controller-and-pods",),
    "k8s-020": ROUTING,
}


def reference_cases(root: Path = ROOT) -> tuple[Case, ...]:
    manifest = json.loads((root / "courses/kubernetes/lessons.json").read_text(encoding="utf-8"))
    lessons = [row for row in manifest["lessons"] if row["runtime_profile"] == "k8s-kind"]
    if {row["id"] for row in lessons} != REFERENCE_CHECKS.keys():
        raise ValueError(
            "Review the Kubernetes CI observations for every registered runnable lesson."
        )
    return tuple(
        Case(
            "reference-" + row["id"],
            row["id"],
            next(path for path in row["solution_paths"] if path.endswith(".yaml")),
            required_checks=REFERENCE_CHECKS[row["id"]],
        )
        for row in lessons
    )


CASES = (
    *reference_cases(),
    Case(
        "finite-job-failure",
        "k8s-011",
        "courses/kubernetes/fixtures/hello-task-failure.yaml",
        status="failed",
    ),
    Case("unready-timeout", "k8s-008", HELLO, "timed_out", timeout_seconds=15, unready=True),
    Case(
        "cancel-created-resources",
        "k8s-008",
        HELLO,
        "cancelled",
        cancel_after_submission=True,
        unready=True,
    ),
    Case("recovery-after-cleanup", "k8s-008", HELLO, required_checks=ROUTING),
)

SUBMITTED = "Submitted only the validated fixed-name owned lesson resources."


def source_for(case: Case, root: Path = ROOT) -> str:
    manifest = json.loads((root / "courses/kubernetes/lessons.json").read_text(encoding="utf-8"))
    lesson = next(row for row in manifest["lessons"] if row["id"] == case.lesson_id)
    expected_verifier = "k8s-readiness-v1" if case.lesson_id == "k8s-008" else None
    if (
        lesson["runtime_profile"] != "k8s-kind"
        or lesson.get("verification_id") != expected_verifier
    ):
        raise ValueError("The Kubernetes qualification lesson changed its runtime contract.")
    path = (root / case.source_path).resolve()
    if not path.is_relative_to((root / "courses/kubernetes").resolve()):
        raise ValueError("Kubernetes qualification sources must stay in their course directory.")
    source = path.read_text(encoding="utf-8")
    if case.unready:
        if source.count("path: /ready") != 1:
            raise ValueError("The reviewed single readiness probe changed; review this mutation.")
        source = source.replace("path: /ready", "path: /missing")
    return source


def verify_receipt(case: Case, job: dict[str, Any], source: str, job_id: str) -> dict[str, Any]:
    if (
        job.get("job_id") != job_id
        or job.get("lesson_id") != case.lesson_id
        or job.get("profile") != "k8s-kind"
        or job.get("source_sha256") != hashlib.sha256(source.encode()).hexdigest()
        or job.get("status") != case.status
        or job.get("returncode") != (0 if case.status == "succeeded" else 1)
        or job.get("truncated") is True
    ):
        raise ValueError(f"{case.name}: missing matching source-bound terminal receipt.")
    checks = job.get("checks")
    if not isinstance(checks, list) or any(not isinstance(check, dict) for check in checks):
        raise ValueError(f"{case.name}: missing typed Kubernetes observations.")
    names = [check.get("name") for check in checks]
    if any(not isinstance(name, str) for name in names) or len(names) != len(set(names)):
        raise ValueError(f"{case.name}: invalid or duplicate check identities.")
    by_name = {check["name"]: check for check in checks}
    for name in (*case.required_checks, "owned-cleanup"):
        if by_name.get(name, {}).get("passed") is not True:
            raise ValueError(f"{case.name}: {name} was not proved.")
    failures = [check for check in checks if check.get("passed") is not True]
    if case.status == "succeeded":
        if failures:
            raise ValueError(f"{case.name}: a successful operation contains failed checks.")
    elif case.status == "failed":
        if (
            len(failures) != 1
            or failures[0].get("name") != "operation"
            or not str(failures[0].get("detail", "")).startswith(
                "The bounded owned Job reached a Failed condition;"
            )
        ):
            raise ValueError(f"{case.name}: the deliberate finite Job failure was not observed.")
    elif (
        len(failures) != 1
        or failures[0].get("name") != "operation-interrupted"
        or failures[0].get("detail") != case.status
    ):
        raise ValueError(f"{case.name}: the expected interruption was not observed.")
    return {
        "case": case.name,
        "lesson_id": case.lesson_id,
        "profile": "k8s-kind",
        "source_path": case.source_path,
        "source_sha256": job["source_sha256"],
        "job_id": job_id,
        "status": job["status"],
        "check_names": sorted(by_name),
        "owned_cleanup_verified": True,
    }


def confirm_cancelled_submission(
    client: ClassroomClient, case: Case, source: str, job_id: str
) -> None:
    budget(client, CANCEL_SECONDS)
    deadline = time.monotonic() + CANCEL_SECONDS
    client.call("module-cancel", job_id=job_id)
    expected = {
        "job_id": job_id,
        "lesson_id": case.lesson_id,
        "profile": "k8s-kind",
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
    }
    while True:
        job = client.call("module-job", job_id=job_id)
        if any(job.get(key) != value for key, value in expected.items()):
            raise ValueError("Kubernetes cancellation returned a different submission.")
        if job.get("status") in TERMINAL - {"blocked", "interrupted"}:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError("Kubernetes cancellation did not reach a confirmed terminal state.")
        time.sleep(0.25)


def run_case(client: ClassroomClient, case: Case) -> dict[str, Any]:
    source = source_for(case)
    job_id = uuid.uuid4().hex
    deadline = time.monotonic() + case.timeout_seconds + 45
    budget(client, case.timeout_seconds + 45)
    cancelled = False
    try:
        # The POST may commit before its response is lost. Its known request ID
        # must remain eligible for bounded cancellation in the exception path.
        client.call(
            "module-run",
            lesson_id=case.lesson_id,
            source=source,
            timeout_seconds=case.timeout_seconds,
            request_id=job_id,
        )
        while True:
            job = client.call("module-job", job_id=job_id)
            if job.get("status") in TERMINAL:
                break
            if (
                case.cancel_after_submission
                and not cancelled
                and SUBMITTED in job.get("output", "")
            ):
                client.call("module-cancel", job_id=job_id)
                cancelled = True
            if time.monotonic() >= deadline:
                raise TimeoutError(f"{case.name}: no terminal receipt within the bounded budget.")
            time.sleep(0.25)
        if case.cancel_after_submission and not cancelled:
            raise ValueError("Cancellation did not occur after actual resource submission.")
        receipt = verify_receipt(case, job, source, job_id)
        print(
            f"PASS: {case.name}: {case.status}, source-bound result and owned cleanup", flush=True
        )
        return receipt
    except BaseException:
        # Terminal readback proves this exact job stopped; cluster release still
        # belongs to the separate explicit host workflow. Never replay source.
        try:
            confirm_cancelled_submission(client, case, source, job_id)
        except Exception as cleanup_error:
            raise RuntimeError(
                f"{case.name}: submitted job cleanup could not be confirmed."
            ) from cleanup_error
        raise


def qualify(client: ClassroomClient, report: Path) -> None:
    receipts: list[dict[str, Any]] = []
    failed_case: str | None = "readiness"
    failure_type: str | None = None
    complete = False
    report.parent.mkdir(parents=True, exist_ok=True)

    def checkpoint() -> None:
        report.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "complete": complete,
                    "failed_case": failed_case,
                    "failure_type": failure_type,
                    "receipts": receipts,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    checkpoint()
    original_opener = client.opener
    try:
        # Readiness can probe several absent profiles. Preserve the ordinary
        # bounded API request budget before applying the stricter job transport.
        readiness = client.call("module-readiness").get("profiles", [])
        if not any(
            row.get("profile") == "k8s-kind" and row.get("ready") is True for row in readiness
        ):
            raise ValueError("The explicitly prepared owned Kubernetes worker is not ready.")
        client.opener = BoundedOpener(original_opener)
        for case in CASES:
            failed_case = case.name
            receipts.append(run_case(client, case))
            checkpoint()
        failed_case = None
        complete = True
    except BaseException as error:
        failure_type = type(error).__name__
        raise
    finally:
        client.opener = original_opener
        checkpoint()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--confirm-disposable", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error(
            "This creates owned test resources and saved jobs; use a disposable CI project."
        )
    client = ClassroomClient(args.url)
    qualify(client, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
