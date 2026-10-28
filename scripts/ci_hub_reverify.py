#!/usr/bin/env python3
"""Read-only native verification of an already promoted partial Hub release.

This is a manual recovery check for immutable tags after a verifier-only fix.
It never stages or promotes images. The old publication and the new pull
acceptance have separate receipts and source revisions.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import stat
import subprocess
import sys
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ci_hub_acceptance as hub  # noqa: E402
from scripts import ci_release_artifacts as artifacts  # noqa: E402
from scripts import ci_release_status as source_ci  # noqa: E402
from scripts.docker_registry import ReleaseError, json_object, sha256  # noqa: E402
from scripts.docker_release import (  # noqa: E402
    ARCHITECTURES,
    Context,
    catalog,
    context_record,
    latest_tag,
    read_json,
    source_version,
    version_tag,
    write_json,
)

PUBLISHED_VERSION = "1.0.0"
PUBLISHED_GROUP = "javascript-typescript"
SELECTED = frozenset({"app", "python-core", "javascript-node", "typescript-node"})
SOURCE_JOB_PATH = ".github/workflows/ci.yml"
PUBLISH_PATH = ".github/workflows/targeted-images.yml"
PROMOTE_JOB = "Promote only the selected two-platform images"
MAX_ARCHIVE = 512 * 1024
MAX_REPORT = 256 * 1024
MAX_API = 8 * 1024 * 1024
ALLOWED_DIFF = frozenset(
    {
        "scripts/ci_hub_acceptance.py",
        "tests/test_ci_hub_acceptance.py",
        "scripts/ci_hub_reverify.py",
        "tests/test_ci_hub_reverify.py",
        ".github/workflows/verify-published-images.yml",
        "tests/test_ci_contract.py",
    }
)
SHA = re.compile(r"[a-f0-9]{40}\Z")
IDENTITY = re.compile(r"[1-9][0-9]{0,19}\Z")
ATTEMPT = re.compile(r"[1-9][0-9]{0,5}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


@dataclass(frozen=True)
class Request:
    source_repository: str
    current_sha: str
    current_run_id: str
    current_attempt: str
    published_sha: str
    published_run_id: str
    published_attempt: str


def dispatch_request(published_sha: str, published_run_id: str, published_attempt: str) -> Request:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    current_sha = os.environ.get("GITHUB_SHA", "")
    current_run_id = os.environ.get("GITHUB_RUN_ID", "")
    current_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or REPOSITORY.fullmatch(repository) is None
        or SHA.fullmatch(current_sha) is None
        or IDENTITY.fullmatch(current_run_id) is None
        or ATTEMPT.fullmatch(current_attempt) is None
        or SHA.fullmatch(published_sha) is None
        or IDENTITY.fullmatch(published_run_id) is None
        or ATTEMPT.fullmatch(published_attempt) is None
    ):
        raise ReleaseError("Reverification requires one exact main workflow dispatch")
    return Request(
        repository,
        current_sha,
        current_run_id,
        current_attempt,
        published_sha,
        published_run_id,
        published_attempt,
    )


def git(args: list[str], *, root: Path = ROOT) -> bytes:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False, timeout=30)
    if result.returncode:
        raise ReleaseError("Could not verify exact checkout or published ancestor")
    return result.stdout.strip()


def verify_checkout(request: Request, root: Path = ROOT) -> list[str]:
    if git(["rev-parse", "HEAD"], root=root).decode() != request.current_sha:
        raise ReleaseError("Checkout differs from dispatched main revision")
    if git(["status", "--porcelain", "--untracked-files=normal"], root=root):
        raise ReleaseError("Reverification requires a clean checkout")
    git(["merge-base", "--is-ancestor", request.published_sha, "HEAD"], root=root)
    changed = git(["diff", "--name-only", "-z", request.published_sha, "HEAD"], root=root)
    paths = [item.decode("utf-8") for item in changed.split(b"\0") if item]
    if not paths or set(paths) - ALLOWED_DIFF:
        raise ReleaseError(
            "Only the allowlisted verifier files may differ from the published source"
        )
    if source_version(root) != PUBLISHED_VERSION:
        raise ReleaseError("The verifier checkout no longer matches the published launcher version")
    old = git(["show", request.published_sha + ":pyproject.toml"], root=root)
    import tomllib

    if tomllib.loads(old.decode("utf-8"))["project"]["version"] != PUBLISHED_VERSION:
        raise ReleaseError("Published source used a different checked-in version")
    return paths


def gh_json(args: list[str], *, maximum: int = MAX_API) -> dict[str, Any]:
    return json_object(artifacts.gh(args, maximum=maximum), maximum)


def gh_pages(path: str) -> list[dict[str, Any]]:
    raw = artifacts.gh(["api", "--paginate", "--slurp", path], maximum=MAX_API)
    try:
        value = json.loads(raw, object_pairs_hook=artifacts.unique_fields)
    except (ValueError, UnicodeError):
        raise ReleaseError("Invalid bounded GitHub listing") from None
    if (
        not isinstance(value, list)
        or not 1 <= len(value) <= 100
        or any(not isinstance(page, dict) for page in value)
    ):
        raise ReleaseError("Invalid GitHub pagination")
    return value


def select_course_run(pages: list[dict[str, Any]], revision: str) -> dict[str, Any] | None:
    allowed = {
        SOURCE_JOB_PATH,
        SOURCE_JOB_PATH + "@main",
        SOURCE_JOB_PATH + "@refs/heads/main",
        SOURCE_JOB_PATH + "@" + revision,
    }
    matches = [
        run
        for page in pages
        for run in page.get("workflow_runs", [])
        if isinstance(run, dict)
        and run.get("path") in allowed
        and run.get("event") == "push"
        and run.get("head_branch") == "main"
        and run.get("head_sha") == revision
    ]
    if not matches:
        return None
    if any(
        type(run.get("id")) is not int
        or run["id"] < 1
        or type(run.get("run_attempt")) is not int
        or run["run_attempt"] < 1
        for run in matches
    ):
        raise ReleaseError("Invalid current Course validation run identity")
    latest = max(matches, key=lambda run: (run["id"], run["run_attempt"]))
    if latest.get("status") == "completed" and latest.get("conclusion") != "success":
        raise ReleaseError("Current Course validation did not succeed")
    return latest


def current_source_jobs(request: Request, *, timeout_seconds: int = 5400) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        pages = gh_pages(
            f"repos/{request.source_repository}/actions/runs?head_sha={request.current_sha}&per_page=100"
        )
        if any(not isinstance(page.get("workflow_runs"), list) for page in pages):
            raise ReleaseError("Invalid Course validation listing")
        current = select_course_run(pages, request.current_sha)
        if current is not None and current.get("status") == "completed":
            if current.get("conclusion") != "success":
                raise ReleaseError("Current source validation did not succeed")
            jobs = gh_pages(
                f"repos/{request.source_repository}/actions/runs/{current['id']}/jobs?filter=all&per_page=100"
            )
            accepted = source_ci.successful_jobs(jobs, source_ci.WORKFLOWS[SOURCE_JOB_PATH])
            return {
                "run_id": current["id"],
                "run_attempt": current["run_attempt"],
                "jobs": accepted,
            }
        if time.monotonic() >= deadline:
            raise ReleaseError("Current source validation did not finish within the bounded wait")
        print("Waiting for current exact-revision Course validation.", flush=True)
        time.sleep(min(30, max(0, deadline - time.monotonic())))


def published_run(request: Request) -> dict[str, Any]:
    run = gh_json(
        ["api", f"repos/{request.source_repository}/actions/runs/{request.published_run_id}"],
        maximum=256 * 1024,
    )
    allowed_paths = {
        PUBLISH_PATH,
        PUBLISH_PATH + "@main",
        PUBLISH_PATH + "@refs/heads/main",
        PUBLISH_PATH + "@" + request.published_sha,
    }
    if (
        run.get("id") != int(request.published_run_id)
        or run.get("event") != "push"
        or run.get("head_branch") != "main"
        or run.get("head_sha") != request.published_sha
        or run.get("path") not in allowed_paths
        or run.get("status") != "completed"
        or run.get("conclusion") not in {"failure", "success"}
        or type(run.get("run_attempt")) is not int
        or run["run_attempt"] < int(request.published_attempt)
    ):
        raise ReleaseError("The referenced run is not the completed marked main publication")
    jobs = gh_pages(
        f"repos/{request.source_repository}/actions/runs/{request.published_run_id}/jobs?filter=all&per_page=100"
    )
    selected = [
        item
        for page in jobs
        for item in page.get("jobs", [])
        if isinstance(item, dict) and item.get("name") == PROMOTE_JOB
    ]
    if (
        len(selected) != 1
        or type(selected[0].get("id")) is not int
        or selected[0]["id"] < 1
        or selected[0].get("status") != "completed"
        or selected[0].get("conclusion") != "success"
        or selected[0].get("run_id", int(request.published_run_id)) != int(request.published_run_id)
        or selected[0].get("head_sha", request.published_sha) != request.published_sha
        or selected[0].get("run_attempt", int(request.published_attempt))
        != int(request.published_attempt)
    ):
        raise ReleaseError("The referenced publisher did not complete selected promotion")
    return {"run_id": run["id"], "promote_job_id": selected[0]["id"]}


def published_receipt(request: Request) -> tuple[dict[str, Any], bytes]:
    pages = gh_pages(
        f"repos/{request.source_repository}/actions/runs/{request.published_run_id}/artifacts?per_page=100"
    )
    name = "published-targeted-release-attempt-" + request.published_attempt
    candidates = [
        item
        for page in pages
        for item in page.get("artifacts", [])
        if isinstance(item, dict) and item.get("name") == name and item.get("expired") is False
    ]
    if (
        len(candidates) != 1
        or type(candidates[0].get("id")) is not int
        or candidates[0]["id"] < 1
        or type(candidates[0].get("size_in_bytes")) is not int
        or not 0 < candidates[0]["size_in_bytes"] <= MAX_ARCHIVE
    ):
        raise ReleaseError("Missing unique bounded published artifact for the selected attempt")
    archive = artifacts.gh(
        ["api", f"repos/{request.source_repository}/actions/artifacts/{candidates[0]['id']}/zip"],
        maximum=MAX_ARCHIVE,
    )
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            entries = bundle.infolist()
            if (
                len(entries) != 1
                or entries[0].filename != "release.json"
                or entries[0].file_size > MAX_REPORT
                or stat.S_ISLNK(entries[0].external_attr >> 16)
            ):
                raise ReleaseError("Published artifact must contain one bounded release.json")
            raw = bundle.read(entries[0])
    except (zipfile.BadZipFile, RuntimeError):
        raise ReleaseError("Published artifact ZIP is invalid") from None
    receipt = json_object(raw, MAX_REPORT)
    validate_receipt(receipt, request)
    return receipt, raw


def validate_receipt(receipt: dict[str, Any], request: Request) -> Context:
    context = context_record(receipt.get("context"))
    expected_fields = {
        "schema_version",
        "kind",
        "context",
        "status",
        "version_tags",
        "latest_tags",
        "latest_skipped_newer_release",
        "scope",
        "group",
        "profiles",
    }
    if (
        set(receipt) != expected_fields
        or receipt.get("schema_version") != 1
        or receipt.get("kind") != "ds60-release-promotion"
        or receipt.get("status") != "published"
        or receipt.get("scope") != "partial"
        or receipt.get("group") != PUBLISHED_GROUP
        or receipt.get("profiles") != sorted(SELECTED)
        or receipt.get("latest_skipped_newer_release") is not False
        or context.source_repository != request.source_repository
        or context.version != PUBLISHED_VERSION
        or context.revision != request.published_sha
        or context.run_id != request.published_run_id
        or context.run_attempt != request.published_attempt
    ):
        raise ReleaseError(
            "Published partial receipt does not match the requested source and selection"
        )
    profiles = catalog(ROOT)
    version_names = {key: version_tag(profiles[key], context.version) for key in SELECTED}
    latest_names = {key: latest_tag(profiles[key]) for key in SELECTED}
    hub.receipt_tags(receipt["version_tags"], version_names)
    hub.receipt_tags(receipt["latest_tags"], latest_names)
    return context


def bounded_path(path: Path, root: Path = ROOT) -> Path:
    return hub.destination(path, root)


def preflight(
    request: Request, receipt_path: Path, report_path: Path, root: Path = ROOT
) -> dict[str, Any]:
    changed = verify_checkout(request, root)
    source = current_source_jobs(request)
    old = published_run(request)
    receipt, raw = published_receipt(request)
    context = validate_receipt(receipt, request)
    target = bounded_path(receipt_path, root)
    if target.exists() or target.is_symlink():
        raise ReleaseError("Choose an unused old-release receipt path")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    report = {
        "schema_version": 1,
        "kind": "ds60-hub-reverify-preflight",
        "status": "passed",
        "verification": {
            "revision": request.current_sha,
            "run_id": request.current_run_id,
            "run_attempt": request.current_attempt,
        },
        "published": asdict(context),
        "source_ci": source,
        "promote_job_id": old["promote_job_id"],
        "changed_files": sorted(changed),
        "receipt_sha256": sha256(raw),
    }
    write_json(bounded_path(report_path, root), report)
    return report


def inspect_published_indexes(
    context: Context, receipt: dict[str, Any], root: Path = ROOT
) -> list[str]:
    profiles = catalog(root)
    version_names = {key: version_tag(profiles[key], context.version) for key in SELECTED}
    latest_names = {key: latest_tag(profiles[key]) for key in SELECTED}
    versions = hub.receipt_tags(receipt["version_tags"], version_names)
    latest = hub.receipt_tags(receipt["latest_tags"], latest_names)
    for key in sorted(SELECTED):
        immutable = version_names[key]
        alias = latest_names[key]
        if versions[immutable] != latest[alias]:
            raise ReleaseError("Latest alias differs from the immutable selected version")
        hub.inspect_index(
            context.repository + ":" + immutable,
            versions[immutable],
            key,
            context,
            PUBLISHED_GROUP,
            root,
        )
        hub.inspect_index(
            context.repository + ":" + alias, latest[alias], key, context, PUBLISHED_GROUP, root
        )
    return sorted(SELECTED)


def accept(
    request: Request,
    receipt_path: Path,
    preflight_path: Path,
    architecture: str,
    report_path: Path,
    root: Path = ROOT,
) -> dict[str, Any]:
    if architecture not in ARCHITECTURES:
        raise ReleaseError("Choose one native Linux architecture")
    report_file = bounded_path(report_path, root)
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-hub-reverify-acceptance",
        "status": "checking",
        "architecture": architecture,
        "published_revision": request.published_sha,
        "verification_revision": request.current_sha,
        "published_run_id": request.published_run_id,
        "verification_run_id": request.current_run_id,
    }
    try:
        changed = verify_checkout(request, root)
        preflight_report = read_json(bounded_path(preflight_path, root))
        receipt_file = bounded_path(receipt_path, root)
        if (
            receipt_file.is_symlink()
            or not receipt_file.is_file()
            or receipt_file.stat().st_size > MAX_REPORT
        ):
            raise ReleaseError("Reverification requires one bounded ordinary promotion receipt")
        with receipt_file.open("rb") as stream:
            receipt_raw = stream.read(MAX_REPORT + 1)
        if len(receipt_raw) > MAX_REPORT:
            raise ReleaseError("Promotion receipt exceeds its bound")
        receipt = json_object(receipt_raw, MAX_REPORT)
        context = validate_receipt(receipt, request)
        if (
            preflight_report.get("kind") != "ds60-hub-reverify-preflight"
            or preflight_report.get("status") != "passed"
            or preflight_report.get("verification")
            != {
                "revision": request.current_sha,
                "run_id": request.current_run_id,
                "run_attempt": request.current_attempt,
            }
            or preflight_report.get("changed_files") != sorted(changed)
            or preflight_report.get("published") != asdict(context)
            or preflight_report.get("receipt_sha256") != sha256(receipt_raw)
        ):
            raise ReleaseError("Reverification preflight differs from this dispatch and receipt")
        namespace = os.environ.get("DOCKERHUB_USERNAME", "")
        if namespace != context.namespace:
            raise ReleaseError("Docker Hub read credential differs from the published namespace")
        hub.native_engine(architecture, root)
        report["indexes_inspected"] = inspect_published_indexes(context, receipt, root)
        project = f"ds60-hub-{architecture}-{request.current_run_id}-{request.current_attempt}"
        if len(project) > 49:
            raise ReleaseError("Reverification project exceeds launcher length limit")
        report.update(
            hub.launch_and_resume(
                context,
                "partial",
                PUBLISHED_GROUP,
                False,
                architecture,
                report_file.with_name("hub-reverify-diagnostics.json"),
                root,
                project=project,
            )
        )
        report["status"] = "accepted"
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        write_json(report_file, report)
    print(f"Read-only published 1.0.0 acceptance passed on native {architecture}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "accept"):
        command = sub.add_parser(name)
        command.add_argument("--published-run-id", required=True)
        command.add_argument("--published-sha", required=True)
        command.add_argument("--published-attempt", required=True)
        command.add_argument("--receipt", type=Path, required=True)
        command.add_argument("--preflight", type=Path, required=True)
        if name == "accept":
            command.add_argument("--architecture", choices=ARCHITECTURES, required=True)
            command.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        request = dispatch_request(
            args.published_sha, args.published_run_id, args.published_attempt
        )
        if args.command == "preflight":
            preflight(request, args.receipt, args.preflight)
        else:
            accept(request, args.receipt, args.preflight, args.architecture, args.report)
        return 0
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        print("Published image reverification failed: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
