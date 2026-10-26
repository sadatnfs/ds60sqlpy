#!/usr/bin/env python3
"""Execute cataloged references in an explicitly disposable Docker classroom.

The host needs only Python's standard library. Workers perform all compilation
and execution. Persistence mode reads the original receipts without rerunning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "jax-cpu": ("jax", "jax-007"),
    "bayesian-cpu": ("statistics-ml", "statistics-science-009"),
    "r-statistics": ("r", "r-001"),
    "php-cli": ("web-development", "web-031"),
    "python-core": ("llm-theory", "llm-011"),
    "cpp20": ("cpp", "cpp-009"),
    "c17": ("c", "c-001"),
    "go": ("go", "go-001"),
    "csharp-dotnet": ("csharp", "csharp-001"),
    "swift-linux": ("swift", "swift-001"),
    "rust-stable": ("rust", "rust-001"),
    "java21": ("java", "java-001"),
    "javascript-node": ("javascript-typescript", "js-001"),
    "typescript-node": ("javascript-typescript", "js-019"),
    "tensorflow-cpu": ("deep-learning-tensorflow", "tf-018"),
    "llm-torch-cpu": ("deep-learning-pytorch", "torch-018"),
    "scala-jvm": ("scala-spark", "spark-002"),
    "spark-local-scala": ("scala-spark", "spark-013"),
    "spark-local-python": ("scala-spark", "spark-013@pyspark"),
}
# These are outputs from the exact catalog references above, after their own
# assertions. Generic run receipts do not claim independent typed worker checks.
EXPECTED_OUTPUT = {
    "r-statistics": ("r-001 reference checks passed",),
    "jax-cpu": ("jax-007: 8 asserted cases passed",),
    "bayesian-cpu": ("PyMC hierarchy and diagnostic evidence", "max_rhat", "divergences"),
    "php-cli": ("web-031 reference checks passed",),
    "python-core": ("{'checks': 6, 'status': 'passed'}",),
    "java21": ("Hello, Java",),
    "c17": ("All lesson checks passed.",),
    "go": ("All lesson checks passed.",),
    "csharp-dotnet": ("Hello, C#", "csharp-001: passed"),
    "swift-linux": ("Hello, Swift", "swift-001: passed"),
    "rust-stable": ("Hello, Rust", "rust-001: passed"),
    "javascript-node": ('{"checks":6,"status":"passed"}',),
    "typescript-node": ('{"checks":6,"status":"passed"}',),
    "tensorflow-cpu": ("{'checks': 6, 'status': 'passed'}",),
    "llm-torch-cpu": ("{'checks': 6, 'status': 'passed'}",),
    "scala-jvm": ("total=400 remaining=50 message=within budget", "revisedRemaining=-50"),
}
TYPED_VERIFIERS = {
    "cpp20": "cpp-ownership-v1",
    "spark-local-scala": "spark-rows-v1",
    "spark-local-python": "spark-rows-v1",
}
TYPED_PROFILES = set(TYPED_VERIFIERS)
TERMINAL = {"succeeded", "failed", "cancelled", "timed_out", "interrupted", "blocked"}


def classroom_origin(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/", "/classroom", "/classroom/"}
        or parsed.query
        or parsed.fragment
        or (parsed.port is not None and not 1 <= parsed.port <= 65535)
    ):
        raise ValueError("Use the explicit http://127.0.0.1:PORT/classroom test address.")
    return f"http://{parsed.netloc}"


class ClassroomClient:
    def __init__(self, url: str) -> None:
        self.origin = classroom_origin(url)
        # A local classroom must never travel through an inherited HTTP proxy.
        self.opener = build_opener(ProxyHandler({}))
        with self.opener.open(self.origin + "/classroom", timeout=20) as response:
            page = response.read().decode("utf-8")
        token = re.search(r'const SERVER_TOKEN = ("[^"\n]+");', page)
        if token is None:
            raise ValueError("The classroom did not provide its private session token.")
        self.token: str = json.loads(token.group(1))

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        route = "classroom" if action.startswith("classroom-") else "modules"
        request = Request(
            f"{self.origin}/api/{route}",
            data=json.dumps({"action": action, **fields}).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Origin": self.origin,
                "X-DS60-Token": self.token,
            },
        )
        with self.opener.open(request, timeout=45) as response:
            result: dict[str, Any] = json.load(response)
        return result


def reference_source(profile: str, root: Path = ROOT) -> tuple[str, str, str]:
    track, lesson_id = CASES[profile]
    canonical, _, variant = lesson_id.partition("@")
    if track == "statistics-ml":
        data = json.loads((root / "courses/statistics-ml/tutorials/index.json").read_text("utf-8"))
        unit = next(row for row in data["units"] if row["id"] == canonical)
        if unit["profile"] != profile or unit["mode"] != "tutorial" or variant:
            raise ValueError("The Bayesian qualification tutorial changed its runtime contract.")
        source_path = unit["example_paths"][0]
    else:
        data = json.loads((root / "courses" / track / "lessons.json").read_text(encoding="utf-8"))
        lesson = next(row for row in data["lessons"] if row["id"] == canonical)
        if variant:
            lesson = next(row for row in lesson["variants"] if row["id"] == variant)
        if lesson["runtime_profile"] != profile:
            raise ValueError(f"Qualification case {lesson_id} no longer uses {profile}.")
        if lesson.get("verification_id") != TYPED_VERIFIERS.get(profile):
            raise ValueError(f"Qualification case {lesson_id} changed its verification contract.")
        source_path = next(path for path in lesson["solution_paths"] if not path.endswith(".md"))
    resolved = (root / source_path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("The qualification source must stay inside the repository.")
    return lesson_id, source_path, resolved.read_text(encoding="utf-8")


def verify_receipt(job: dict[str, Any], lesson_id: str, profile: str, source: str) -> None:
    if (
        job.get("status") != "succeeded"
        or job.get("returncode") != 0
        or job.get("lesson_id") != lesson_id
        or job.get("profile") != profile
        or job.get("source_sha256") != hashlib.sha256(source.encode("utf-8")).hexdigest()
        or (profile in TYPED_PROFILES and not job.get("checks"))
        or not all(check.get("passed") is True for check in job.get("checks", []))
        or not all(marker in job.get("output", "") for marker in EXPECTED_OUTPUT.get(profile, ()))
    ):
        detail = str(job.get("output", job.get("detail", "")))[-1500:]
        raise ValueError(f"{lesson_id} did not produce a successful source-bound receipt: {detail}")


def qualify(
    client: ClassroomClient,
    profiles: list[str],
    *,
    prior: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    if not profiles or any(profile not in CASES for profile in profiles):
        raise ValueError("Choose one or more registered ordinary runtime profiles.")
    readiness = client.call("module-readiness")["profiles"]
    ready = {row["profile"] for row in readiness if row["ready"]}
    missing = set(profiles) - ready
    if missing:
        raise ValueError("Profiles not ready: " + ", ".join(sorted(missing)))
    if prior is not None and set(prior["profiles"]) != set(profiles):
        raise ValueError("Persistence checks must select the same profiles as the original run.")
    receipts = []
    for profile in dict.fromkeys(profiles):
        lesson_id, source_path, source = reference_source(profile, root)
        if prior is None:
            job_id = uuid.uuid4().hex
            client.call(
                "module-save",
                lesson_id=lesson_id,
                fields={
                    "source": source,
                    "prediction": "Disposable CI fixture: inspect independent checks.",
                    "explanation": "Runtime qualification only, not a learner mastery claim.",
                },
            )
            client.call(
                "module-run",
                lesson_id=lesson_id,
                source=source,
                timeout_seconds=120,
                request_id=job_id,
            )
            deadline = time.monotonic() + 150
            while True:
                job = client.call("module-job", job_id=job_id)
                if job["status"] in TERMINAL:
                    break
                if time.monotonic() >= deadline:
                    client.call("module-cancel", job_id=job_id)
                    raise TimeoutError(
                        f"{lesson_id} did not finish within the qualification budget."
                    )
                time.sleep(0.25)
        else:
            old = next(item for item in prior["receipts"] if item["profile"] == profile)
            job_id = old["job_id"]
            job = client.call("module-job", job_id=job_id)
            saved = client.call("module-lesson", lesson_id=lesson_id)
            if saved["session"].get("source") != source:
                raise ValueError(f"{lesson_id} source did not survive container replacement.")
            if not any(item["job_id"] == job_id for item in saved["history"]):
                raise ValueError(f"{lesson_id} run history did not survive container replacement.")
        verify_receipt(job, lesson_id, profile, source)
        receipts.append(
            {
                "lesson_id": lesson_id,
                "profile": profile,
                "source_path": source_path,
                "source_sha256": job["source_sha256"],
                "job_id": job_id,
                "status": job["status"],
                "typed_worker_checks": len(job["checks"]),
                "reference_execution": "passed",
                "verification_kind": "typed_contract"
                if profile in TYPED_PROFILES
                else "reference_assertions",
            }
        )
        print(
            f"PASS: {profile}: {lesson_id}, source-bound execution; "
            f"{len(job['checks'])} typed worker checks",
            flush=True,
        )
    return {
        "schema_version": 1,
        "profiles": sorted(set(profiles)),
        "receipts": receipts,
        "persistence_verified": prior is not None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--profiles", required=True, help="space-separated ordinary profile names")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--check-persistence", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error(
            "This writes test pads and receipts. Use --confirm-disposable on a test project."
        )
    profiles = args.profiles.split()
    if not profiles or set(profiles) - CASES.keys():
        parser.error("Profiles must be selected from: " + ", ".join(CASES))
    prior = json.loads(args.report.read_text(encoding="utf-8")) if args.check_persistence else None
    result = qualify(ClassroomClient(args.url), profiles, prior=prior)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
