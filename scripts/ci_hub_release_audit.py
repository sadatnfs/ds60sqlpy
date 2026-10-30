#!/usr/bin/env python3
"""Audit every canonical full-release profile using the exact published launcher.

This dispatch-only verifier never builds, stages or publishes images. Each native
job pulls one ordinary group plus App/Core, starts a fresh owned classroom and
checks saved selections and stop/resume. Runtime qualification remains the
publisher's separate evidence. Current verifier and published source identities
are recorded independently.
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
import zipfile
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ci_hub_acceptance as hub  # noqa: E402
from scripts import ci_hub_reverify as recovery  # noqa: E402
from scripts import ci_profiles  # noqa: E402
from scripts import ci_release_artifacts as artifacts  # noqa: E402
from scripts.ci_targeted_images import parse_marker  # noqa: E402
from scripts.docker_registry import Manifest, ReleaseError, json_object, sha256  # noqa: E402
from scripts.docker_release import (  # noqa: E402
    ARCHITECTURES,
    Context,
    catalog,
    config_digest,
    context_record,
    latest_tag,
    read_json,
    source_version,
    version_tag,
    write_json,
)

PUBLISH_PATH = ".github/workflows/publish-images.yml"
PROMOTE_JOB = "Promote the complete tested two-platform release"
MAX_SOURCE_BYTES = 512 * 1024 * 1024
MAX_SOURCE_FILE = 16 * 1024 * 1024
MAX_SOURCE_FILES = 30000


def verify_checkout(request: recovery.Request, root: Path) -> str:
    """Trust only a clean dispatched verifier and an ancestor marked publication."""
    if recovery.git(["rev-parse", "HEAD"], root=root).decode() != request.current_sha:
        raise ReleaseError("Verifier checkout differs from the dispatched main revision")
    if recovery.git(["status", "--porcelain", "--untracked-files=normal"], root=root):
        raise ReleaseError("Full-release audit requires a clean verifier checkout")
    recovery.git(["merge-base", "--is-ancestor", request.published_sha, "HEAD"], root=root)
    message = recovery.git(["log", "-1", "--format=%B", request.published_sha], root=root).decode()
    marker = parse_marker(message, root)
    if marker is None or marker.mode != "full":
        raise ReleaseError("Published source is not an exact full-publication commit")
    return recovery.git(["rev-parse", request.published_sha + "^{tree}"], root=root).decode()


def published_run(request: recovery.Request) -> dict[str, int]:
    run = recovery.gh_json(
        ["api", f"repos/{request.source_repository}/actions/runs/{request.published_run_id}"],
        maximum=256 * 1024,
    )
    allowed = {
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
        or run.get("path") not in allowed
        or run.get("status") != "completed"
        or run.get("conclusion") not in {"success", "failure"}
        or type(run.get("run_attempt")) is not int
        or run["run_attempt"] < int(request.published_attempt)
    ):
        raise ReleaseError("Referenced full publisher has not completed at the requested source")
    pages = recovery.gh_pages(
        f"repos/{request.source_repository}/actions/runs/{request.published_run_id}"
        f"/attempts/{request.published_attempt}/jobs?per_page=100"
    )
    jobs = [
        job
        for page in pages
        for job in page.get("jobs", [])
        if isinstance(job, dict) and job.get("name") == PROMOTE_JOB
    ]
    if (
        len(jobs) != 1
        or type(jobs[0].get("id")) is not int
        or jobs[0]["id"] < 1
        or jobs[0].get("status") != "completed"
        or jobs[0].get("conclusion") != "success"
        or jobs[0].get("head_sha", request.published_sha) != request.published_sha
        or jobs[0].get("run_id", int(request.published_run_id)) != int(request.published_run_id)
        or jobs[0].get("run_attempt", int(request.published_attempt))
        != int(request.published_attempt)
    ):
        raise ReleaseError("Selected full-release attempt did not complete canonical promotion")
    return {"run_id": run["id"], "promote_job_id": jobs[0]["id"]}


def validate_receipt(receipt: dict[str, Any], request: recovery.Request) -> Context:
    expected = {
        "schema_version",
        "kind",
        "context",
        "status",
        "version_tags",
        "latest_tags",
        "latest_skipped_newer_release",
    }
    context = context_record(receipt.get("context"))
    if (
        set(receipt) != expected
        or receipt.get("schema_version") != 1
        or receipt.get("kind") != "ds60-release-promotion"
        or receipt.get("status") != "published"
        or type(receipt.get("latest_skipped_newer_release")) is not bool
        or context.source_repository != request.source_repository
        or context.revision != request.published_sha
        or context.run_id != request.published_run_id
        or context.run_attempt != request.published_attempt
    ):
        raise ReleaseError("Full promotion receipt differs from the requested publisher identity")
    return context


def fetch_receipt(request: recovery.Request) -> tuple[dict[str, Any], bytes]:
    pages = recovery.gh_pages(
        f"repos/{request.source_repository}/actions/runs/{request.published_run_id}/artifacts?per_page=100"
    )
    name = "published-release-attempt-" + request.published_attempt
    matches = [
        row
        for page in pages
        for row in page.get("artifacts", [])
        if isinstance(row, dict) and row.get("name") == name and row.get("expired") is False
    ]
    if (
        len(matches) != 1
        or type(matches[0].get("id")) is not int
        or matches[0]["id"] < 1
        or type(matches[0].get("size_in_bytes")) is not int
        or not 0 < matches[0]["size_in_bytes"] <= hub.MAX_ARCHIVE
    ):
        raise ReleaseError("A unique bounded full promotion artifact is required")
    archive = artifacts.gh(
        ["api", f"repos/{request.source_repository}/actions/artifacts/{matches[0]['id']}/zip"],
        maximum=hub.MAX_ARCHIVE,
    )
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            entries = bundle.infolist()
            if (
                len(entries) != 1
                or entries[0].filename != "release.json"
                or not 0 < entries[0].file_size <= hub.MAX_REPORT
                or stat.S_ISLNK(entries[0].external_attr >> 16)
            ):
                raise ReleaseError(
                    "Promotion artifact must contain one ordinary bounded release.json"
                )
            raw = bundle.read(entries[0])
    except (zipfile.BadZipFile, RuntimeError):
        raise ReleaseError("Invalid full promotion artifact ZIP") from None
    receipt = json_object(raw, hub.MAX_REPORT)
    validate_receipt(receipt, request)
    return receipt, raw


def source_entries(bundle: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    entries = bundle.infolist()
    files: list[zipfile.ZipInfo] = []
    seen: set[str] = set()
    total = 0
    if len(entries) > MAX_SOURCE_FILES * 2:
        raise ReleaseError("Published source archive exceeds the entry bound")
    for item in entries:
        name = item.filename
        path = PurePosixPath(name)
        mode = item.external_attr >> 16
        if (
            not name
            or name.startswith("/")
            or "\\" in name
            or "\x00" in name
            or any(part in {"", ".", ".."} for part in name.rstrip("/").split("/"))
            or path.parts[0] in {".git", ".classroom", "work"}
            or name in seen
            or stat.S_ISLNK(mode)
            or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_IFMT(mode) == 0)
        ):
            raise ReleaseError("Published source contains an unsafe or repeated archive path")
        seen.add(name)
        if item.is_dir():
            continue
        total += item.file_size
        if item.file_size > MAX_SOURCE_FILE or total > MAX_SOURCE_BYTES:
            raise ReleaseError("Published source exceeds its bounded extraction size")
        files.append(item)
    if not files or len(files) > MAX_SOURCE_FILES:
        raise ReleaseError("Published source file count exceeds its bound")
    return files


def export_source(request: recovery.Request, directory: Path, root: Path) -> dict[str, Any]:
    source = directory / "source"
    archive = directory / "source.zip"
    if source.exists() or source.is_symlink() or archive.exists() or archive.is_symlink():
        raise ReleaseError("Use a fresh audit source export directory")
    result = subprocess.run(
        ["git", "archive", "--format=zip", "--output=" + str(archive), request.published_sha],
        cwd=root,
        capture_output=True,
        check=False,
        timeout=120,
    )
    if result.returncode or not 0 < archive.stat().st_size <= MAX_SOURCE_BYTES:
        raise ReleaseError("Could not export the bounded exact published source")
    inventory = []
    with zipfile.ZipFile(archive) as bundle:
        entries = source_entries(bundle)
        source.mkdir()
        for item in entries:
            path = source / item.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = bundle.read(item)
            path.write_bytes(raw)
            mode = 0o755 if (item.external_attr >> 16) & 0o111 else 0o644
            path.chmod(mode)
            inventory.append({"path": item.filename, "sha256": sha256(raw), "mode": mode})
    manifest = {
        "schema_version": 1,
        "revision": request.published_sha,
        "files": sorted(inventory, key=lambda row: str(row["path"])),
    }
    write_json(directory / "source-manifest.json", manifest)
    archive.unlink()
    return {
        "files": len(inventory),
        "manifest_sha256": sha256((directory / "source-manifest.json").read_bytes()),
    }


def verify_export(request: recovery.Request, directory: Path) -> None:
    manifest_path = directory / "source-manifest.json"
    if manifest_path.is_symlink() or not 0 < manifest_path.stat().st_size <= 8 * 1024 * 1024:
        raise ReleaseError("Published source manifest is not a bounded ordinary file")
    manifest = json_object(manifest_path.read_bytes(), 8 * 1024 * 1024)
    if (
        manifest.get("schema_version") != 1
        or manifest.get("revision") != request.published_sha
        or not isinstance(manifest.get("files"), list)
        or not 0 < len(manifest["files"]) <= MAX_SOURCE_FILES
    ):
        raise ReleaseError("Published source manifest identity is invalid")
    source = directory / "source"
    seen: set[str] = set()
    for row in manifest["files"]:
        if (
            not isinstance(row, dict)
            or set(row) != {"path", "sha256", "mode"}
            or not isinstance(row["path"], str)
            or row["path"] in seen
        ):
            raise ReleaseError("Published source manifest has invalid or duplicate paths")
        path = source / row["path"]
        if (
            Path(row["path"]).is_absolute()
            or ".." in Path(row["path"]).parts
            or not path.resolve().is_relative_to(source.resolve())
            or any(parent.is_symlink() for parent in (path, *path.parents))
            or not path.is_file()
            or path.stat().st_size > MAX_SOURCE_FILE
            or stat.S_IMODE(path.stat().st_mode) != row["mode"]
            or sha256(path.read_bytes()) != row["sha256"]
        ):
            raise ReleaseError("Exported source changed before published-launcher acceptance")
        seen.add(row["path"])


def receipt_indexes(
    receipt: dict[str, Any], context: Context, source: Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    profiles = catalog(source)
    if source_version(source) != context.version:
        raise ReleaseError("Exported source version differs from the published image version")
    versions = hub.receipt_tags(
        receipt["version_tags"],
        {key: version_tag(profile, context.version) for key, profile in profiles.items()},
    )
    if receipt["latest_skipped_newer_release"]:
        if receipt["latest_tags"] != []:
            raise ReleaseError("Downgrade-protected promotion cannot claim latest aliases")
        aliases = {}
    else:
        aliases = hub.receipt_tags(
            receipt["latest_tags"], {key: latest_tag(profile) for key, profile in profiles.items()}
        )
        for profile in profiles.values():
            if aliases[latest_tag(profile)] != versions[version_tag(profile, context.version)]:
                raise ReleaseError("Recorded alias differs from its canonical version index")
    return profiles, versions, aliases


def verification_identity(request: recovery.Request) -> dict[str, str]:
    return {
        "revision": request.current_sha,
        "run_id": request.current_run_id,
        "run_attempt": request.current_attempt,
    }


def recovery_inputs(value: str, *, cases: bool = False) -> list[str]:
    if not value:
        return []
    items = value.split(",")
    pattern = r"[a-z][a-z0-9-]{0,40}/(?:amd64|arm64)" if cases else r"[1-9][0-9]{0,19}"
    limit = 6 if cases else 12
    if (
        not 1 <= len(items) <= limit
        or len(set(items)) != len(items)
        or any(re.fullmatch(pattern, item) is None for item in items)
    ):
        raise ReleaseError(
            "Recovery inputs need unique bounded run IDs or group/architecture cases"
        )
    return items


def case_identity(group: str, architecture: str) -> str:
    return group + "/" + architecture


def prior_artifact(artifact: dict[str, Any], repository: str) -> dict[str, bytes]:
    if (
        type(artifact.get("id")) is not int
        or artifact["id"] < 1
        or artifact.get("expired") is not False
        or type(artifact.get("size_in_bytes")) is not int
        or not 0 < artifact["size_in_bytes"] <= 2 * 1024 * 1024
    ):
        raise ReleaseError("Recovery requires an unexpired bounded audit artifact")
    raw = artifacts.gh(
        ["api", f"repos/{repository}/actions/artifacts/{artifact['id']}/zip"],
        maximum=2 * 1024 * 1024,
    )
    if artifact.get("digest") != sha256(raw):
        raise ReleaseError("Prior audit archive differs from its GitHub digest")
    result: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
            entries = bundle.infolist()
            if not 1 <= len(entries) <= 64:
                raise ReleaseError("Prior audit artifact has unexpected entry coverage")
            for item in entries:
                path = PurePosixPath(item.filename)
                if (
                    item.is_dir()
                    or path.is_absolute()
                    or ".." in path.parts
                    or "\\" in item.filename
                    or item.filename in result
                    or stat.S_ISLNK(item.external_attr >> 16)
                    or not 0 < item.file_size <= hub.MAX_REPORT
                ):
                    raise ReleaseError("Prior audit artifact has an invalid ordinary JSON entry")
                result[item.filename] = bundle.read(item)
    except (zipfile.BadZipFile, RuntimeError):
        raise ReleaseError("Prior audit artifact is not a valid bounded ZIP") from None
    return result


def validate_prior_acceptance(
    value: dict[str, Any],
    *,
    context: Context,
    source: Path,
    verifier_sha: str,
    run_id: str,
    attempt: str,
    group: str,
    architecture: str,
) -> None:
    workers = ci_profiles.selected(group, source)
    selected = list(dict.fromkeys(["app", "python-core", *workers]))
    profiles = catalog(source)
    if (
        value.get("schema_version") != 1
        or value.get("kind") != "ds60-full-hub-module-audit"
        or value.get("status") != "accepted"
        or value.get("group") != group
        or value.get("architecture") != architecture
        or value.get("published_revision") != context.revision
        or value.get("published_run_id") != context.run_id
        or value.get("version") != context.version
        or value.get("saved_version") != context.version
        or value.get("verification")
        != {"revision": verifier_sha, "run_id": run_id, "run_attempt": attempt}
        or value.get("profiles_pulled") != selected
        or value.get("profiles_started") != workers
    ):
        raise ReleaseError("Prior acceptance does not bind the requested published module case")
    for key in (
        "stop_resume_same_stateful_containers",
        "app_image_unchanged",
        "learning_marker_retained",
        "browser_readback_ok",
    ):
        if value.get(key) is not True:
            raise ReleaseError("Prior acceptance lacks complete saved-state and browser evidence")
    if (
        type(value.get("persistent_volumes")) is not int
        or not 2 <= value["persistent_volumes"] <= 64
        or type(value.get("latest_aliases_checked")) is not bool
        or value.get("latest_resolved") is not value["latest_aliases_checked"]
    ):
        raise ReleaseError("Prior acceptance has incomplete lifecycle or latest selection metadata")
    prepared = value.get("prepared_observation")
    if not isinstance(prepared, dict) or prepared.get("no_runtime_resources") is not True:
        raise ReleaseError("Prior acceptance lacks pull-only preparation evidence")
    images = prepared.get("images")
    if not isinstance(images, list) or len(images) != len(selected):
        raise ReleaseError("Prior acceptance lacks exact selected image coverage")
    for key, image in zip(selected, images, strict=True):
        if (
            not isinstance(image, dict)
            or set(image) != {"profile", "reference", "image_id"}
            or image["profile"] != key
            or image["reference"]
            != context.repository + ":" + version_tag(profiles[key], context.version)
            or not isinstance(image["image_id"], str)
            or re.fullmatch(r"sha256:[a-f0-9]{64}", image["image_id"]) is None
        ):
            raise ReleaseError("Prior acceptance contains an invalid canonical image binding")
    references = {
        context.repository + ":" + version_tag(profiles[key], context.version) for key in selected
    }
    if value["latest_aliases_checked"]:
        references.update(
            context.repository + ":" + latest_tag(profiles[key]) for key in ("app", workers[0])
        )
    observed = prepared.get("release_references")
    if (
        not isinstance(observed, list)
        or len(observed) != len(references)
        or set(observed) != references
    ):
        raise ReleaseError("Prior acceptance contains an unexpected selected pull reference")
    services = sorted(
        {
            "lab",
            "classroom-init",
            "postgres",
            *[service_for_profile(key, source) for key in selected if key != "app"],
        }
    )
    for key in ("started_observation", "resumed_observation"):
        observation = value.get(key)
        if (
            not isinstance(observation, dict)
            or observation.get("profile_images_match_promotion") is not True
            or observation.get("services") != services
        ):
            raise ReleaseError("Prior acceptance lacks exact selected service identity evidence")


def collect_prior_acceptances(
    request: recovery.Request,
    context: Context,
    source: Path,
    directory: Path,
    requested_runs: list[str],
    *,
    root: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Retain raw passed receipts and their original run identities without replay."""
    pending = [(run_id, frozenset()) for run_id in requested_runs]
    visited: set[str] = set()
    accepted: dict[str, dict[str, Any]] = {}
    while pending:
        run_id, ancestry = pending.pop(0)
        if run_id in ancestry or run_id == request.current_run_id:
            raise ReleaseError("Audit recovery ancestry contains a cycle or this active run")
        if run_id in visited:
            continue
        if len(visited) >= 12:
            raise ReleaseError("Audit recovery ancestry exceeds its bounded history")
        visited.add(run_id)
        run = recovery.gh_json(
            ["api", f"repos/{request.source_repository}/actions/runs/{run_id}"], maximum=256 * 1024
        )
        revision = run.get("head_sha")
        path = ".github/workflows/audit-published-release.yml"
        if (
            run.get("id") != int(run_id)
            or run.get("event") != "workflow_dispatch"
            or run.get("head_branch") != "main"
            or not isinstance(revision, str)
            or re.fullmatch(r"[a-f0-9]{40}", revision) is None
            or run.get("path")
            not in {path, path + "@main", path + "@refs/heads/main", path + "@" + revision}
            or run.get("status") != "completed"
            or run.get("conclusion") not in {"success", "failure"}
        ):
            raise ReleaseError("Recovery requires a completed main audit from this repository")
        recovery.git(["merge-base", "--is-ancestor", revision, "HEAD"], root=root)
        pages = recovery.gh_pages(
            f"repos/{request.source_repository}/actions/runs/{run_id}/artifacts?per_page=100"
        )
        artifact_rows = [
            item for page in pages for item in page.get("artifacts", []) if isinstance(item, dict)
        ]
        jobs = [
            job
            for page in recovery.gh_pages(
                f"repos/{request.source_repository}/actions/runs/{run_id}/jobs?filter=all&per_page=100"
            )
            for job in page.get("jobs", [])
            if isinstance(job, dict)
        ]
        preflights = [
            item
            for item in artifact_rows
            if re.fullmatch(
                r"full-hub-audit-preflight-attempt-[1-9][0-9]{0,5}", str(item.get("name", ""))
            )
        ]
        for artifact in preflights:
            attempt = artifact["name"].rsplit("-", 1)[1]
            successful = [
                job
                for job in jobs
                if job.get("name") == "Bind published full source and promotion"
                and str(job.get("run_attempt")) == attempt
                and job.get("conclusion") == "success"
            ]
            if len(successful) != 1:
                continue
            files = prior_artifact(artifact, request.source_repository)
            if "preflight.json" not in files:
                raise ReleaseError("Prior audit preflight artifact is incomplete")
            report = json_object(files["preflight.json"], hub.MAX_REPORT)
            if (
                report.get("kind") != "ds60-full-hub-audit-preflight"
                or report.get("status") != "passed"
                or report.get("verification")
                != {"revision": revision, "run_id": run_id, "run_attempt": attempt}
                or report.get("published") != asdict(context)
            ):
                raise ReleaseError("Prior audit preflight has different publication identity")
            predecessors = report.get("resume_runs", [])
            if not isinstance(predecessors, list) or any(
                not isinstance(value, str) for value in predecessors
            ):
                raise ReleaseError("Prior audit recovery ancestry is malformed")
            recovery_inputs(",".join(predecessors))
            pending.extend((value, ancestry | {run_id}) for value in predecessors)
        pattern = re.compile(
            r"full-hub-audit-([a-z][a-z0-9-]{0,40})-(amd64|arm64)-attempt-([1-9][0-9]{0,5})\Z"
        )
        for artifact in artifact_rows:
            match = pattern.fullmatch(str(artifact.get("name", "")))
            if match is None:
                continue
            group, architecture, attempt = match.groups()
            name = f"Pull selected modules ({group}, {architecture})"
            matching = [
                job
                for job in jobs
                if job.get("name") == name
                and str(job.get("run_attempt")) == attempt
                and job.get("conclusion") == "success"
            ]
            if not matching:
                continue
            if len(matching) != 1 or type(matching[0].get("id")) is not int:
                raise ReleaseError("Prior successful module job identity is ambiguous")
            files = prior_artifact(artifact, request.source_repository)
            if (
                set(files) - {"acceptance.json", "registry-diagnostic.json"}
                or "acceptance.json" not in files
            ):
                raise ReleaseError("Prior successful audit artifact has unexpected contents")
            raw = files["acceptance.json"]
            value = json_object(raw, hub.MAX_REPORT)
            validate_prior_acceptance(
                value,
                context=context,
                source=source,
                verifier_sha=revision,
                run_id=run_id,
                attempt=attempt,
                group=group,
                architecture=architecture,
            )
            expected_tree = recovery.git(
                ["rev-parse", context.revision + "^{tree}"], root=root
            ).decode()
            if value.get("published_tree") != expected_tree:
                raise ReleaseError("Prior acceptance used a different published source tree")
            key = case_identity(group, architecture)
            record = {
                "case": key,
                "run_id": run_id,
                "run_attempt": attempt,
                "verifier_revision": revision,
                "artifact_id": artifact["id"],
                "job_id": matching[0]["id"],
                "receipt_sha256": sha256(raw),
                "published_revision": context.revision,
                "latest_aliases_checked": value["latest_aliases_checked"],
            }
            target = (
                directory
                / "reused"
                / (run_id + "-" + group + "-" + architecture + "-" + attempt + ".json")
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            record["receipt_path"] = target.relative_to(directory).as_posix()
            if key not in accepted or (int(run_id), int(attempt)) > (
                int(accepted[key]["run_id"]),
                int(accepted[key]["run_attempt"]),
            ):
                accepted[key] = record
    return [accepted[key] for key in sorted(accepted)], sorted(visited, key=int)


def execution_selection(
    matrix: dict[str, Any],
    reused: list[dict[str, Any]],
    *,
    resume: bool,
    requested_cases: list[str],
    diagnostic_only: bool,
) -> dict[str, Any]:
    rows = matrix["include"]
    by_case = {case_identity(row["group"], row["architecture"]): row for row in rows}
    accepted = {row["case"] for row in reused}
    if not accepted <= set(by_case):
        raise ReleaseError("Reused receipt is outside the published native matrix")
    unresolved = [key for key in by_case if key not in accepted]
    if requested_cases and not resume:
        raise ReleaseError("Explicit recovery cases require prior audit receipts")
    if any(key not in unresolved for key in requested_cases):
        raise ReleaseError("Recovery may select only unresolved native cases, never accepted ones")
    selected = requested_cases or (unresolved[:1] if resume else unresolved)
    if diagnostic_only:
        selected = []
        for architecture in ARCHITECTURES:
            candidates = [key for key in unresolved if by_case[key]["architecture"] == architecture]
            if candidates:
                selected.append(candidates[0])
    return {
        "expected_cases": list(by_case),
        "accepted_cases": sorted(accepted),
        "unresolved_cases": unresolved,
        "selected_cases": selected,
        "execution_matrix": {"include": [by_case[key] for key in selected]},
        "diagnostic_only": diagnostic_only,
        "scope_complete_before_run": not unresolved,
    }


def diagnose(
    request: recovery.Request,
    directory: Path,
    architecture: str,
    *,
    require_pulls: bool,
    root: Path,
) -> dict[str, Any]:
    from scripts import ci_hub_pull_diagnostics as diagnostics

    diagnostics.hosted_guard()
    report_file = hub.destination(directory, root) / "registry-diagnostic.json"
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-hub-head-diagnostic",
        "status": "checking",
        "verification": verification_identity(request),
        "architecture": architecture,
    }
    try:
        _, _, context = prepared_identity(request, directory, root)
        hub.native_engine(architecture, root)
        report.update(
            diagnostics.inspect_hub(context.namespace, context.version, hub.environment())
        )
        # Only booleans/counts leave Docker info; proxy or mirror URLs are never read.
        raw = (
            hub.run_output(
                [
                    "docker",
                    "info",
                    "--format",
                    "{{if .HTTPProxy}}true{{else}}false{{end}} {{if .HTTPSProxy}}true{{else}}false{{end}} {{len .RegistryConfig.Mirrors}}",
                ],
                root=root,
            )
            .decode("ascii")
            .strip()
            .split()
        )
        if (
            len(raw) == 3
            and raw[0] in {"true", "false"}
            and raw[1] in {"true", "false"}
            and raw[2].isdigit()
        ):
            report["engine_transport"] = {
                "http_proxy_configured": raw[0] == "true",
                "https_proxy_configured": raw[1] == "true",
                "registry_mirror_count": int(raw[2]),
            }
        report["process_transport"] = {
            "http_proxy_configured": bool(
                os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
            ),
            "https_proxy_configured": bool(
                os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
            ),
        }
        report["status"] = "observed" if report["pulls_allowed"] else "blocked"
        if require_pulls and not report["pulls_allowed"]:
            raise ReleaseError(
                "Hosted registry observations block image pulls; inspect the sanitized diagnostic"
            )
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        report.setdefault("pulls_allowed", False)
        report["status"] = "blocked"
        report["error"] = str(error)
        raise
    finally:
        write_json(report_file, report)
    return report


def preflight(
    request: recovery.Request,
    directory: Path,
    root: Path,
    *,
    resume_runs: list[str] | None = None,
    requested_cases: list[str] | None = None,
    diagnostic_only: bool = False,
) -> dict[str, Any]:
    tree = verify_checkout(request, root)
    source_ci = recovery.current_source_jobs(request)
    publication = published_run(request)
    receipt, raw = fetch_receipt(request)
    context = validate_receipt(receipt, request)
    directory = hub.destination(directory, root)
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ReleaseError("Preflight requires a fresh owned evidence directory")
    exported = export_source(request, directory, root)
    receipt_indexes(receipt, context, directory / "source")
    matrix = ci_profiles.matrix(native=True, root=directory / "source")
    reused, prior_runs = collect_prior_acceptances(
        request, context, directory / "source", directory, resume_runs or [], root=root
    )
    selection = execution_selection(
        matrix,
        reused,
        resume=bool(resume_runs),
        requested_cases=requested_cases or [],
        diagnostic_only=diagnostic_only,
    )
    (directory / "release.json").write_bytes(raw)
    report = {
        "schema_version": 1,
        "kind": "ds60-full-hub-audit-preflight",
        "status": "passed",
        "verification": verification_identity(request),
        "published": asdict(context),
        "published_tree": tree,
        "source_ci": source_ci,
        **publication,
        "receipt_sha256": sha256(raw),
        "source_export": exported,
        "matrix": matrix,
        "resume_runs": prior_runs,
        "reused_receipts": reused,
        **selection,
    }
    write_json(directory / "preflight.json", report)
    return report


def prepared_identity(
    request: recovery.Request, directory: Path, root: Path
) -> tuple[dict[str, Any], dict[str, Any], Context]:
    tree = verify_checkout(request, root)
    report = read_json(directory / "preflight.json")
    receipt_file = directory / "release.json"
    if (
        receipt_file.is_symlink()
        or not receipt_file.is_file()
        or not 0 < receipt_file.stat().st_size <= hub.MAX_REPORT
    ):
        raise ReleaseError("Audit requires a bounded ordinary promotion receipt")
    raw = receipt_file.read_bytes()
    receipt = json_object(raw, hub.MAX_REPORT)
    context = validate_receipt(receipt, request)
    if (
        report.get("schema_version") != 1
        or report.get("kind") != "ds60-full-hub-audit-preflight"
        or report.get("status") != "passed"
        or report.get("verification") != verification_identity(request)
        or report.get("published") != asdict(context)
        or report.get("published_tree") != tree
        or report.get("receipt_sha256") != sha256(raw)
    ):
        raise ReleaseError(
            "Audit preflight differs from this dispatch, source or promotion receipt"
        )
    return report, receipt, context


def prepare(request: recovery.Request, directory: Path, root: Path) -> None:
    report, receipt, context = prepared_identity(request, directory, root)
    exported = export_source(request, directory, root)
    if exported != report.get("source_export"):
        raise ReleaseError("Native source export differs from the preflight's exact source")
    receipt_indexes(receipt, context, directory / "source")
    if ci_profiles.matrix(native=True, root=directory / "source") != report.get("matrix"):
        raise ReleaseError("Native group matrix differs from the published catalog")


def release_references(context: Context, source: Path) -> list[str]:
    raw = hub.run_output(
        ["docker", "image", "ls", context.repository, "--format", "{{.Repository}}:{{.Tag}}"],
        root=source,
    )
    values = raw.decode("utf-8", "strict").splitlines()
    if (
        len(values) > 128
        or len(values) != len(set(values))
        or any(
            not value.startswith(context.repository + ":") or any(c.isspace() for c in value)
            for value in values
        )
    ):
        raise ReleaseError("Unexpected bounded local release image inventory")
    return sorted(values)


def selected_image_ids(
    context: Context,
    receipt: dict[str, Any],
    selected: list[str],
    architecture: str,
    check_latest: bool,
    source: Path,
) -> dict[str, str]:
    profiles, versions, aliases = receipt_indexes(receipt, context, source)
    if check_latest and not aliases:
        raise ReleaseError(
            "This promotion did not move latest; audit immutable versions explicitly"
        )
    expected = {}
    for key in selected:
        profile = profiles[key]
        tag = version_tag(profile, context.version)
        natives = hub.inspect_index(
            context.repository + ":" + tag, versions[tag], key, context, None, source
        )
        if check_latest:
            alias = latest_tag(profile)
            hub.inspect_index(
                context.repository + ":" + alias, aliases[alias], key, context, None, source
            )
        native = natives[architecture]
        raw = hub.run_output(
            [
                "docker",
                "buildx",
                "imagetools",
                "inspect",
                "--raw",
                context.repository + "@" + native.digest,
            ],
            root=source,
        )
        body = (
            raw
            if sha256(raw) == native.digest
            else raw[:-1]
            if raw.endswith(b"\n") and sha256(raw[:-1]) == native.digest
            else b""
        )
        if not body or len(body) != native.size:
            raise ReleaseError("Native manifest differs from the published index descriptor")
        expected[key] = config_digest(Manifest(native, json_object(body, hub.MAX_INDEX), body))
    return expected


def service_for_profile(profile: str, source: Path) -> str:
    rows = [
        line.split()
        for line in (source / "docker/classroom-images.tsv").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    matches = [row[1] for row in rows if row[0] == profile]
    if len(matches) != 1:
        raise ReleaseError("Profile has no unique catalog service")
    return matches[0]


def saved_profiles(project: str, workers: list[str], source: Path) -> None:
    file = source / ".classroom" / project / "selection.env"
    if file.is_symlink() or not file.is_file() or file.stat().st_size > 4096:
        raise ReleaseError("Launcher did not save bounded profile selection")
    fields = file.read_text().splitlines()
    expected = "DS60_PROFILES=" + ",".join(dict.fromkeys(["python-core", *workers]))
    if sum(line.startswith("DS60_PROFILES=") for line in fields) != 1 or expected not in fields:
        raise ReleaseError("Launcher saved a different selected module set")


def local_image(
    context: Context, key: str, source: Path, architecture: str, expected: str
) -> dict[str, str]:
    profile = catalog(source)[key]
    reference = context.repository + ":" + version_tag(profile, context.version)
    raw = hub.run_output(
        ["docker", "image", "inspect", "--format", "{{.Os}} {{.Architecture}} {{.Id}}", reference],
        root=source,
    )
    if raw.decode().strip().split() != ["linux", architecture, expected]:
        raise ReleaseError("Pulled canonical image differs from the qualified native image: " + key)
    return {"profile": key, "reference": reference, "image_id": expected}


def accept(
    request: recovery.Request,
    directory: Path,
    group: str,
    architecture: str,
    check_latest: bool,
    root: Path,
) -> dict[str, Any]:
    directory = hub.destination(directory, root)
    report_file = directory / "acceptance.json"
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-full-hub-module-audit",
        "status": "checking",
        "group": group,
        "architecture": architecture,
        "verification": verification_identity(request),
        "published_revision": request.published_sha,
        "published_run_id": request.published_run_id,
    }
    try:
        preflight_report, receipt, context = prepared_identity(request, directory, root)
        selection = preflight_report.get("selected_cases")
        if selection is not None and case_identity(group, architecture) not in selection:
            raise ReleaseError("Native case was not selected by this audit preflight")
        if preflight_report.get("diagnostic_only") is True:
            raise ReleaseError("A diagnostic-only dispatch cannot pull classroom images")
        verify_export(request, directory)
        if (
            sha256((directory / "source-manifest.json").read_bytes())
            != preflight_report["source_export"]["manifest_sha256"]
        ):
            raise ReleaseError("Exact-source manifest differs from the guarded preflight")
        source = directory / "source"
        if context.namespace != os.environ.get("DOCKERHUB_USERNAME"):
            raise ReleaseError("Read credential namespace differs from the published destination")
        workers = list(dict.fromkeys(["python-core", *ci_profiles.selected(group, source)]))
        selected = ["app", *workers]
        hub.native_engine(architecture, source)
        expected = selected_image_ids(
            context, receipt, selected, architecture, check_latest, source
        )
        if release_references(context, source):
            raise ReleaseError(
                "Fresh canonical pull audit requires no preexisting release repository images"
            )
        profiles = catalog(source)
        latest_profile = ci_profiles.selected(group, source)[0] if check_latest else None
        allowed_references = {
            context.repository + ":" + version_tag(profiles[key], context.version)
            for key in selected
        }
        if check_latest:
            allowed_references.update(
                context.repository + ":" + latest_tag(profiles[key])
                for key in ("app", str(latest_profile))
            )

        def prepared(project: str, selected_workers: list[str]) -> dict[str, Any]:
            if any(
                hub.docker_items(kind, project, source)
                for kind in ("container", "volume", "network")
            ):
                raise ReleaseError(
                    "Pull-only setup created runtime resources before strict startup"
                )
            observed = release_references(context, source)
            if set(observed) != allowed_references:
                raise ReleaseError(
                    "Selective setup pulled an unexpected or incomplete release image set"
                )
            saved_profiles(project, selected_workers, source)
            hub.read_selection(project, context, latest_profile, source)
            return {
                "release_references": observed,
                "no_runtime_resources": True,
                "images": [
                    local_image(context, key, source, architecture, expected[key])
                    for key in selected
                ],
            }

        def started(project: str, selected_workers: list[str]) -> dict[str, Any]:
            saved_profiles(project, selected_workers, source)
            expected_services = {
                "lab": "app",
                "classroom-init": "app",
                "postgres": None,
                **{service_for_profile(key, source): key for key in workers},
            }
            observed: dict[str, str] = {}
            for container in hub.docker_items("container", project, source):
                raw = hub.run_output(
                    [
                        "docker",
                        "inspect",
                        "--format",
                        '{{index .Config.Labels "com.docker.compose.service"}} {{.Image}}',
                        container,
                    ],
                    root=source,
                )
                fields = raw.decode().strip().split()
                if len(fields) != 2 or fields[0] not in expected_services or fields[0] in observed:
                    raise ReleaseError("Selected classroom has an unexpected or duplicate service")
                service, identity = fields
                key = expected_services[service]
                if key is not None and identity != expected[key]:
                    raise ReleaseError(
                        "Started service image differs from its pulled canonical profile"
                    )
                observed[service] = identity
            if set(observed) != set(expected_services):
                raise ReleaseError("Selected classroom is missing a required service")
            return {"services": sorted(observed), "profile_images_match_promotion": True}

        project = f"ds60-hub-{architecture}-{request.current_run_id}-{request.current_attempt}"
        report.update(
            {
                "version": context.version,
                "published_tree": preflight_report["published_tree"],
                "profiles_pulled": selected,
                "latest_aliases_checked": check_latest,
                "runtime_qualification": (
                    "Separate publisher evidence; this audit checks canonical pull, "
                    "setup and saved-state resume."
                ),
            }
        )
        report.update(
            hub.launch_and_resume(
                context,
                "partial",
                group,
                not check_latest,
                architecture,
                source / "work/hub-audit-diagnostics.json",
                source,
                project=project,
                pull_first=True,
                prepared_check=prepared,
                started_check=started,
            )
        )
        report["status"] = "accepted"
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        write_json(report_file, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "prepare", "diagnose", "accept"))
    parser.add_argument("--published-sha", required=True)
    parser.add_argument("--published-run-id", required=True)
    parser.add_argument("--published-attempt", required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--group")
    parser.add_argument("--architecture", choices=ARCHITECTURES)
    parser.add_argument("--skip-latest", action="store_true")
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--resume-runs", default="")
    parser.add_argument("--cases", default="")
    parser.add_argument("--diagnostic-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        request = recovery.dispatch_request(
            args.published_sha, args.published_run_id, args.published_attempt
        )
        directory = hub.destination(args.directory, ROOT)
        if args.command == "preflight":
            report = preflight(
                request,
                directory,
                ROOT,
                resume_runs=recovery_inputs(args.resume_runs),
                requested_cases=recovery_inputs(args.cases, cases=True),
                diagnostic_only=args.diagnostic_only,
            )
            if args.github_output:
                with args.github_output.open("a") as stream:
                    stream.write(
                        "matrix="
                        + json.dumps(report["execution_matrix"], separators=(",", ":"))
                        + "\n"
                    )
                    stream.write(
                        "has_cases="
                        + str(bool(report["execution_matrix"]["include"])).lower()
                        + "\n"
                    )
        elif args.command == "prepare":
            prepare(request, directory, ROOT)
        elif args.command == "diagnose":
            if args.architecture is None:
                raise ReleaseError("Registry diagnostics require one native architecture")
            diagnose(request, directory, args.architecture, require_pulls=False, root=ROOT)
        else:
            if args.group is None or args.architecture is None:
                raise ReleaseError("Native acceptance requires an explicit group and architecture")
            diagnose(request, directory, args.architecture, require_pulls=True, root=ROOT)
            accept(request, directory, args.group, args.architecture, not args.skip_latest, ROOT)
        return 0
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        print("Full-release audit failed: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
