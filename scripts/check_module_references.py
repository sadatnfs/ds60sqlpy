#!/usr/bin/env python3
"""Run every selected authored module reference through a disposable classroom.

Only Python's standard library is needed on the host. The catalog chooses the
profile and source; compilation, assertions and typed checks run in the actual
packaged workers. Reading lessons and owned-cluster operations are reported
separately, never advertised as successful ordinary-runtime execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ds60sqlpy.modules import LANGUAGES, MAX_SOURCE_BYTES, ModuleCatalog, ModuleLesson  # noqa: E402
from scripts.check_classroom_profiles import TERMINAL, ClassroomClient  # noqa: E402

ORDINARY_PROFILES = frozenset(LANGUAGES) - {"reading", "k8s-kind"}
EXTERNAL_REASONS = {
    "reading": "Reading or separately documented manual workflow; no ordinary worker execution.",
    "k8s-kind": "Owned-cluster operation; qualified by the separate Kubernetes workflow.",
}


class Client(Protocol):
    def call(self, action: str, **fields: Any) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ReferenceCase:
    lesson_id: str
    subject: str
    profile: str
    language: str
    learning_mode: str
    verification_id: str | None
    source_path: str
    source: str

    @property
    def source_sha256(self) -> str:
        return hashlib.sha256(self.source.encode("utf-8")).hexdigest()

    def metadata(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "subject": self.subject,
            "profile": self.profile,
            "language": self.language,
            "learning_mode": self.learning_mode,
            "verification_id": self.verification_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
        }


def reference_case(catalog: ModuleCatalog, lesson: ModuleLesson) -> ReferenceCase:
    """Choose the admitted worked example or separate executable reference."""
    paths = (
        [lesson.source_path]
        if lesson.learning_mode == "tutorial"
        else [path for path in lesson.solution_paths if Path(path).suffix != ".md"]
    )
    if len(paths) != 1:
        raise ValueError(f"{lesson.id} must declare exactly one executable reference per variant.")
    source_path = paths[0]
    source = catalog.content_path(source_path, MAX_SOURCE_BYTES).read_text(encoding="utf-8")
    if not source.strip() or len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError(f"{lesson.id} has an empty or oversized executable reference.")
    return ReferenceCase(
        lesson.id,
        lesson.track_id,
        lesson.runtime_profile,
        lesson.language,
        lesson.learning_mode,
        lesson.verification_id,
        source_path,
        source,
    )


def collect_cases(root: Path, profiles: list[str]) -> tuple[list[ReferenceCase], dict[str, Any]]:
    if not profiles or set(profiles) - ORDINARY_PROFILES:
        raise ValueError("Select registered ordinary profiles; cluster operations are separate.")
    catalog = ModuleCatalog(root)
    cases = []
    exclusions = []
    inventory: Counter[str] = Counter()
    for lesson in sorted(catalog.lessons.values(), key=lambda item: item.id):
        inventory[lesson.runtime_profile] += 1
        if lesson.runtime_profile in EXTERNAL_REASONS:
            exclusions.append(
                {
                    "lesson_id": lesson.id,
                    "profile": lesson.runtime_profile,
                    "reason": EXTERNAL_REASONS[lesson.runtime_profile],
                }
            )
        elif lesson.runtime_profile in profiles:
            cases.append(reference_case(catalog, lesson))
    empty = set(profiles) - {case.profile for case in cases}
    if empty:
        raise ValueError("No admitted executable cases for: " + ", ".join(sorted(empty)))
    return cases, {
        "schema_version": 1,
        "profiles": sorted(set(profiles)),
        "inventory_by_profile": dict(sorted(inventory.items())),
        "selected_cases": len(cases),
        "excluded_external_or_reading": exclusions,
        "unselected_ordinary_profiles": sorted(ORDINARY_PROFILES - set(profiles)),
        "results": [{**case.metadata(), "status": "pending"} for case in cases],
        "complete": False,
        "passed": False,
    }


def validate_remote_lesson(case: ReferenceCase, lesson: dict[str, Any]) -> None:
    expected = {
        "id": case.lesson_id,
        "runtime_profile": case.profile,
        "language": case.language,
        "learning_mode": case.learning_mode,
        "verification_id": case.verification_id,
    }
    if any(lesson.get(key) != value for key, value in expected.items()):
        raise ValueError(f"{case.lesson_id} served metadata differs from the selected source.")


def verify_result(case: ReferenceCase, job_id: str, job: dict[str, Any]) -> None:
    checks = job.get("checks")
    if (
        job.get("job_id") != job_id
        or job.get("lesson_id") != case.lesson_id
        or job.get("profile") != case.profile
        or job.get("source_sha256") != case.source_sha256
        or job.get("status") != "succeeded"
        or job.get("returncode") != 0
        or job.get("truncated") is not False
        or not isinstance(checks, list)
        or (case.verification_id is not None and not checks)
        or not all(isinstance(check, dict) and check.get("passed") is True for check in checks)
    ):
        raise ValueError(f"{case.lesson_id} did not produce a successful source-bound receipt.")


def wait_for_job(client: Client, job_id: str, deadline: float) -> dict[str, Any]:
    while True:
        job = client.call("module-job", job_id=job_id)
        if job.get("status") in TERMINAL:
            return job
        if time.monotonic() >= deadline:
            client.call("module-cancel", job_id=job_id)
            cleanup_deadline = time.monotonic() + 15
            while time.monotonic() < cleanup_deadline:
                job = client.call("module-job", job_id=job_id)
                if job.get("status") in TERMINAL:
                    raise TimeoutError("Reference exceeded its bounded execution deadline.")
                time.sleep(0.25)
            raise TimeoutError("Reference deadline expired; cancellation outcome remains unknown.")
        time.sleep(0.25)


def cancel_unconfirmed_job(client: Client, job_id: str) -> dict[str, Any]:
    """Bound recovery of this test's job without replaying its source."""
    try:
        job = client.call("module-cancel", job_id=job_id)
        deadline = time.monotonic() + 15
        while job.get("status") not in TERMINAL:
            if time.monotonic() >= deadline:
                return {"confirmed": False, "outcome": "unknown"}
            time.sleep(0.25)
            job = client.call("module-job", job_id=job_id)
        if job.get("job_id") != job_id:
            return {"confirmed": False, "outcome": "unknown"}
        return {"confirmed": True, "outcome": job["status"]}
    except (OSError, ValueError, KeyError, TypeError):
        return {"confirmed": False, "outcome": "unknown"}


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_cases(
    client: Client,
    cases: list[ReferenceCase],
    report: dict[str, Any],
    report_path: Path,
    *,
    timeout_seconds: int = 120,
    max_seconds: float = 2700,
) -> bool:
    deadline = time.monotonic() + max_seconds
    write_report(report_path, report)
    readiness = client.call("module-readiness")["profiles"]
    ready = {row["profile"] for row in readiness if row.get("ready") is True}
    missing = {case.profile for case in cases} - ready
    if missing:
        raise ValueError("Profiles not ready: " + ", ".join(sorted(missing)))
    for index, case in enumerate(cases):
        if time.monotonic() >= deadline:
            report["failure"] = "Overall qualification deadline reached; pending cases did not run."
            break
        result = report["results"][index]
        job: dict[str, Any] = {}
        job_id: str | None = None
        stop_after_failure = False
        started = time.monotonic()
        try:
            validate_remote_lesson(case, client.call("module-lesson", lesson_id=case.lesson_id))
            client.call(
                "module-save",
                lesson_id=case.lesson_id,
                fields={
                    "source": case.source,
                    "prediction": "Disposable CI reference execution, not a learner assessment.",
                    "explanation": "Exercise the authored assertions in its declared runtime.",
                },
            )
            job_id = uuid.uuid4().hex
            result["job_id"] = job_id
            submitted = client.call(
                "module-run",
                lesson_id=case.lesson_id,
                source=case.source,
                timeout_seconds=timeout_seconds,
                request_id=job_id,
            )
            if submitted.get("job_id") != job_id:
                raise ValueError("The submitted job identity was not preserved.")
            job = wait_for_job(
                client, job_id, min(deadline, time.monotonic() + timeout_seconds + 30)
            )
            verify_result(case, job_id, job)
            result.update(
                status="passed",
                returncode=job["returncode"],
                typed_worker_checks=len(job["checks"]),
                verification_kind="typed_contract_and_reference_execution"
                if case.verification_id
                else "reference_execution",
            )
        except (OSError, ValueError, KeyError, TypeError) as error:
            result.update(status="failed", failure=f"{type(error).__name__}: {error}")
            if job_id is not None and job.get("status") not in TERMINAL:
                result["cleanup"] = cancel_unconfirmed_job(client, job_id)
                if not result["cleanup"]["confirmed"]:
                    report["failure"] = "Job outcome remains unknown; later cases were not started."
                    stop_after_failure = True
        result["seconds"] = round(time.monotonic() - started, 3)
        result["worker_status"] = job.get("status")
        result["truncated"] = job.get("truncated")
        result["output_tail"] = str(job.get("output", ""))[-2000:]
        write_report(report_path, report)
        print(
            f"{result['status'].upper()}: {case.profile}: {case.lesson_id} "
            f"({result['seconds']} seconds)",
            flush=True,
        )
        if stop_after_failure:
            break
    statuses = Counter(item["status"] for item in report["results"])
    report["summary"] = dict(statuses)
    report["complete"] = not statuses["pending"]
    report["passed"] = report["complete"] and not statuses["failed"]
    write_report(report_path, report)
    return bool(report["passed"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profiles", required=True, help="space-separated ordinary profile names")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--url")
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--list-only", action="store_true", help="derive inventory without HTTP")
    parser.add_argument("--max-minutes", type=int, default=45)
    args = parser.parse_args(argv)
    if not 1 <= args.max_minutes <= 120:
        parser.error("The qualification budget must be between 1 and 120 minutes.")
    if not args.list_only and (not args.confirm_disposable or not args.url):
        parser.error("Execution needs --url and --confirm-disposable for an owned test project.")
    report: dict[str, Any] = {}
    try:
        cases, report = collect_cases(args.root, args.profiles.split())
        if args.list_only:
            write_report(args.report, report)
            print(f"Selected {len(cases)} executable module implementations; nothing executed.")
            return 0
        return int(
            not run_cases(
                ClassroomClient(args.url),
                cases,
                report,
                args.report,
                max_seconds=args.max_minutes * 60,
            )
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        report.update(passed=False, complete=False, failure=f"{type(error).__name__}: {error}")
        write_report(args.report, report)
        print(f"Module reference qualification failed: {type(error).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
