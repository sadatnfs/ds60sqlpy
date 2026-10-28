#!/usr/bin/env python3
"""Verify promoted OCI indexes and a fresh native Docker Hub classroom install.

This runs only after the publisher reports ``published``. Its receipt is a
separate pull-and-resume acceptance result, never a substitute for promotion.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import platform
import re
import stat
import subprocess
import sys
import zipfile
from contextlib import suppress
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ci_release_artifacts as artifacts  # noqa: E402
from scripts.ci_profiles import selected as group_profiles  # noqa: E402
from scripts.ci_targeted_images import parse_marker  # noqa: E402
from scripts.docker_registry import (  # noqa: E402
    OCI_INDEX,
    Descriptor,
    Manifest,
    ReleaseError,
    descriptor,
    json_object,
    sha256,
)
from scripts.docker_release import (  # noqa: E402
    ARCHITECTURES,
    catalog,
    context_record,
    github_context,
    latest_tag,
    published_index,
    read_json,
    require_scope,
    selected_release_profiles,
    version_tag,
    write_json,
)

MAX_ARCHIVE = 512 * 1024
MAX_REPORT = 256 * 1024
MAX_INDEX = 64 * 1024
PROJECT = re.compile(r"ds60-hub-(amd64|arm64)-([1-9][0-9]{0,19})-([1-9][0-9]{0,5})\Z")


def environment() -> dict[str, str]:
    """Pass Docker's auth-file path, never publication secrets, to child tools."""
    return {
        key: value
        for key, value in os.environ.items()
        if key
        not in {
            "DOCKERHUB_USERNAME",
            "DOCKERHUB_TOKEN",
            "GH_TOKEN",
            "GITHUB_TOKEN",
            "DOCKER_DEFAULT_PLATFORM",
        }
    }


def run_output(args: list[str], *, timeout: int = 120, root: Path = ROOT) -> bytes:
    result = subprocess.run(
        args, cwd=root, env=environment(), capture_output=True, check=False, timeout=timeout
    )
    if result.returncode:
        raise ReleaseError("Hosted Docker command failed: " + " ".join(args[:3]))
    if len(result.stdout) > MAX_INDEX:
        raise ReleaseError("Hosted Docker metadata exceeds its bound")
    return result.stdout


def run_visible(args: list[str], *, timeout: int, root: Path = ROOT) -> None:
    print("Running hosted classroom step: " + args[0] + " " + args[1], flush=True)
    result = subprocess.run(args, cwd=root, env=environment(), check=False, timeout=timeout)
    if result.returncode:
        raise ReleaseError("Hosted classroom command failed")


def artifact_name(mode: str) -> str:
    if mode == "partial":
        return "published-targeted-release"
    if mode == "full":
        return "published-release"
    raise ReleaseError("Choose full or partial hosted acceptance")


def github_identity() -> tuple[str, str, str, int]:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    revision = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_EVENT_NAME") != "push"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None
        or re.fullmatch(r"[a-f0-9]{40}", revision) is None
        or re.fullmatch(r"[1-9][0-9]{0,19}", run_id) is None
        or re.fullmatch(r"[1-9][0-9]{0,5}", attempt) is None
    ):
        raise ReleaseError("Hosted acceptance requires an exact main push run")
    return repository, revision, run_id, int(attempt)


def destination(path: Path, root: Path = ROOT) -> Path:
    resolved = path if path.is_absolute() else root / path
    if not resolved.absolute().is_relative_to(root / "work"):
        raise ReleaseError("Keep hosted acceptance evidence beneath work/")
    for parent in (resolved, *resolved.parents):
        if parent.is_symlink():
            raise ReleaseError("Hosted acceptance evidence path must not contain links")
        if parent == root:
            break
    return resolved


def fetch_receipt(mode: str, output: Path, root: Path = ROOT) -> dict[str, Any]:
    """Select one bounded, unexpired promotion artifact from this exact run."""
    repository, revision, run_id, current_attempt = github_identity()
    prefix = artifact_name(mode)
    pages = json.loads(
        artifacts.gh(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/actions/runs/{run_id}/artifacts?per_page=100",
            ],
            maximum=8 * 1024 * 1024,
        )
    )
    if not isinstance(pages, list) or not 1 <= len(pages) <= 100:
        raise ReleaseError("Invalid promotion artifact listing")
    candidates: list[tuple[int, int]] = []
    pattern = re.compile(re.escape(prefix) + r"-attempt-([1-9][0-9]{0,5})\Z")
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("artifacts"), list):
            raise ReleaseError("Invalid promotion artifact page")
        for item in page["artifacts"]:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise ReleaseError("Invalid promotion artifact metadata")
            match = pattern.fullmatch(item["name"])
            if match is None or item.get("expired") is not False:
                continue
            attempt = int(match[1])
            if attempt > current_attempt:
                continue
            if (
                type(item.get("id")) is not int
                or item["id"] < 1
                or type(item.get("size_in_bytes")) is not int
                or not 0 < item["size_in_bytes"] <= MAX_ARCHIVE
            ):
                raise ReleaseError("Promotion artifact has invalid bounded identity")
            candidates.append((attempt, item["id"]))
    if not candidates:
        raise ReleaseError("No published promotion receipt exists for this run")
    latest = max(attempt for attempt, _ in candidates)
    matches = [identifier for attempt, identifier in candidates if attempt == latest]
    if len(matches) != 1:
        raise ReleaseError("Ambiguous latest published promotion artifact")
    archive = artifacts.gh(
        ["api", f"repos/{repository}/actions/artifacts/{matches[0]}/zip"], maximum=MAX_ARCHIVE
    )
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            entries = bundle.infolist()
            if (
                len(entries) != 1
                or entries[0].filename != "release.json"
                or entries[0].file_size > MAX_REPORT
            ):
                raise ReleaseError("Promotion artifact must contain one bounded release.json")
            if stat.S_ISLNK(entries[0].external_attr >> 16):
                raise ReleaseError("Promotion receipt must not be a symbolic link")
            raw = bundle.read(entries[0])
    except (zipfile.BadZipFile, RuntimeError):
        raise ReleaseError("Promotion artifact is not a valid ZIP") from None
    receipt = json_object(raw, MAX_REPORT)
    context = context_record(receipt.get("context"))
    if (
        context.source_repository != repository
        or context.revision != revision
        or context.run_id != run_id
        or int(context.run_attempt) != latest
        or receipt.get("status") != "published"
    ):
        raise ReleaseError("Promotion receipt does not bind this published run")
    target = destination(output, root)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise ReleaseError("Choose an unused hosted acceptance receipt path")
    target.write_bytes(raw)
    print(f"Selected published {mode} receipt from attempt {latest}")
    return receipt


def release_selection(
    receipt: dict[str, Any], mode: str, root: Path = ROOT
) -> tuple[Any, dict[str, Any], set[str], str | None, bool]:
    namespace = os.environ.get("DOCKERHUB_USERNAME", "")
    marker = parse_marker(
        subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout,
        root,
    )
    group = marker.group if marker is not None and marker.mode == "publish" else None
    if (mode == "partial" and group is None) or (
        mode == "full" and (marker is None or marker.mode != "full")
    ):
        raise ReleaseError("Hosted acceptance mode differs from the exact HEAD marker")
    current = github_context(root, namespace, target_group=group)
    stored = context_record(receipt.get("context"))
    if any(
        getattr(stored, field) != getattr(current, field)
        for field in (
            "namespace",
            "repository",
            "source_repository",
            "version",
            "revision",
            "run_id",
        )
    ) or int(stored.run_attempt) > int(current.run_attempt):
        raise ReleaseError("Published receipt differs from this source, version or workflow run")
    profiles = catalog(root)
    selected = selected_release_profiles(profiles, group, root)
    base = {
        "schema_version",
        "kind",
        "context",
        "status",
        "version_tags",
        "latest_tags",
        "latest_skipped_newer_release",
    }
    if mode == "partial":
        if (
            set(receipt) != base | {"scope", "group", "profiles"}
            or receipt["scope"] != "partial"
            or receipt["group"] != group
            or receipt["profiles"] != sorted(selected)
        ):
            raise ReleaseError("Partial promotion receipt has the wrong selected group")
    elif set(receipt) != base:
        raise ReleaseError("Full promotion receipt has unexpected fields")
    if (
        receipt.get("schema_version") != 1
        or receipt.get("kind") != "ds60-release-promotion"
        or receipt.get("status") != "published"
        or type(receipt.get("latest_skipped_newer_release")) is not bool
    ):
        raise ReleaseError("Hosted acceptance requires a completed promotion receipt")
    skip_latest = receipt["latest_skipped_newer_release"]
    return current, profiles, selected, group, skip_latest


def receipt_tags(rows: Any, expected: dict[str, str]) -> dict[str, Descriptor]:
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ReleaseError("Published receipt has incomplete selected tag coverage")
    result: dict[str, Descriptor] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"tag", "mediaType", "digest", "size"}:
            raise ReleaseError("Published receipt has invalid tag metadata")
        tag = row["tag"]
        if not isinstance(tag, str) or tag not in expected.values() or tag in result:
            raise ReleaseError("Published receipt has an unexpected or repeated tag")
        value = descriptor(row)
        if value.media_type != OCI_INDEX:
            raise ReleaseError("Published release tag is not an OCI index")
        result[tag] = value
    if set(result) != set(expected.values()) or rows[-1]["tag"] != expected["app"]:
        raise ReleaseError("Published app pointer must follow every selected worker")
    return result


def inspect_index(
    reference: str,
    expected: Descriptor,
    profile: str,
    context: Any,
    group: str | None,
    root: Path = ROOT,
) -> dict[str, Descriptor]:
    raw = run_output(["docker", "buildx", "imagetools", "inspect", "--raw", reference], root=root)
    body = (
        raw
        if sha256(raw) == expected.digest
        else raw[:-1]
        if raw.endswith(b"\n") and sha256(raw[:-1]) == expected.digest
        else b""
    )
    if not body or len(body) != expected.size:
        raise ReleaseError("Canonical tag content differs from its published receipt")
    manifest = Manifest(expected, json_object(body, MAX_INDEX), body)
    version, revision, natives = published_index(manifest, profile, context.source_repository)
    require_scope(manifest, group)
    if (
        version != context.version
        or revision != context.revision
        or set(natives) != set(ARCHITECTURES)
    ):
        raise ReleaseError("Canonical index differs from the qualified source or native platforms")
    return natives


def verify_indexes(
    receipt: dict[str, Any], mode: str, root: Path = ROOT, *, architecture: str = "amd64"
) -> tuple[Any, dict[str, Any], set[str], str | None, bool]:
    if architecture not in ARCHITECTURES:
        raise ReleaseError("Choose one native release architecture")
    context, profiles, selected, group, skip_latest = release_selection(receipt, mode, root)
    ordered = {key: profiles[key] for key in profiles if key in selected}
    version_tags = {key: version_tag(profile, context.version) for key, profile in ordered.items()}
    version_rows = receipt_tags(receipt.get("version_tags"), version_tags)
    latest_tags = {key: latest_tag(profile) for key, profile in ordered.items()}
    if skip_latest:
        if receipt.get("latest_tags") != []:
            raise ReleaseError("A downgrade-protected release cannot claim latest aliases")
        latest_rows: dict[str, Descriptor] = {}
    else:
        latest_rows = receipt_tags(receipt.get("latest_tags"), latest_tags)
    # Every full-release index carries both native descriptors. The AMD64 job
    # reads the complete canonical set; ARM64 independently validates the
    # complete receipt and directly inspects/pulls App and Core. Both native
    # worker sets were qualified before promotion. This limits Hub metadata
    # reads for a free account without implying all ARM workers were pulled.
    inspected = selected if mode == "partial" or architecture == "amd64" else {"app", "python-core"}
    for key in ordered:
        if key not in inspected:
            continue
        tag = version_tags[key]
        inspect_index(context.repository + ":" + tag, version_rows[tag], key, context, group, root)
        if not skip_latest:
            alias = latest_tags[key]
            if latest_rows[alias] != version_rows[tag]:
                raise ReleaseError("Published latest alias differs from the immutable version")
            inspect_index(
                context.repository + ":" + alias, latest_rows[alias], key, context, group, root
            )
    print(
        f"Verified {len(inspected)} published two-platform indexes on native {architecture}; "
        f"validated {len(selected)} selected receipt entries"
    )
    return context, profiles, selected, group, skip_latest


def project_name(architecture: str) -> str:
    _, _, run_id, attempt = github_identity()
    value = f"ds60-hub-{architecture}-{run_id}-{attempt}"
    if len(value) > 49 or PROJECT.fullmatch(value) is None:
        raise ReleaseError("Hosted disposable project identity exceeds launcher limits")
    return value


def native_engine(architecture: str, root: Path = ROOT) -> None:
    machine = platform.machine().lower()
    host = (
        "arm64"
        if machine in {"arm64", "aarch64"}
        else "amd64"
        if machine in {"amd64", "x86_64"}
        else ""
    )
    info = (
        run_output(["docker", "info", "--format", "{{.OSType}} {{.Architecture}}"], root=root)
        .decode()
        .strip()
        .split()
    )
    engine = (
        "arm64"
        if info == ["linux", "aarch64"] or info == ["linux", "arm64"]
        else "amd64"
        if info == ["linux", "x86_64"] or info == ["linux", "amd64"]
        else ""
    )
    if host != architecture or engine != architecture:
        raise ReleaseError("Hosted acceptance requires a native Linux runner and engine")


def docker_items(kind: str, project: str, root: Path = ROOT) -> list[str]:
    if kind == "container":
        args = [
            "docker",
            "ps",
            "--all",
            "--quiet",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ]
    elif kind == "volume":
        args = [
            "docker",
            "volume",
            "ls",
            "--quiet",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ]
    else:
        args = [
            "docker",
            "network",
            "ls",
            "--quiet",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ]
    values = run_output(args, root=root).decode().splitlines()
    if (
        len(values) > 64
        or len(values) != len(set(values))
        or any(not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value) for value in values)
    ):
        raise ReleaseError("Disposable project inventory is invalid")
    return values


def assert_new_project(project: str, root: Path = ROOT) -> None:
    if (root / ".classroom" / project).exists() or any(
        docker_items(kind, project, root) for kind in ("container", "volume", "network")
    ):
        raise ReleaseError("Hosted acceptance project already exists; preserve it for inspection")


def compose_ids(project: str, service: str, root: Path = ROOT) -> str:
    args = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--project-name",
        project,
        "-f",
        str(root / "compose.classroom.yaml"),
        "--profile",
        "*",
        "ps",
        "--all",
        "--quiet",
        service,
    ]
    value = run_output(args, root=root).decode().strip()
    if re.fullmatch(r"[a-f0-9]{12,64}", value) is None:
        raise ReleaseError("Expected one owned classroom container for " + service)
    return value


def cleanup_project(project: str, root: Path = ROOT) -> None:
    if PROJECT.fullmatch(project) is None:
        raise ReleaseError("Refusing to clean an unrecognized hosted project")
    for kind in ("container", "volume", "network"):
        for value in docker_items(kind, project, root):
            labels = ".Config.Labels" if kind == "container" else ".Labels"
            inspected = (
                run_output(
                    [
                        "docker",
                        kind,
                        "inspect",
                        "--format",
                        "{{index " + labels + ' "com.docker.compose.project"}}',
                        value,
                    ],
                    root=root,
                )
                .decode()
                .strip()
            )
            if inspected != project:
                raise ReleaseError("Refusing to clean a resource outside the owned project")
    command = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--project-name",
        project,
        "-f",
        str(root / "compose.classroom.yaml"),
        "--profile",
        "*",
        "down",
        "--volumes",
        "--remove-orphans",
        "--timeout",
        "20",
    ]
    run_visible(command, timeout=120, root=root)


def save_diagnostics(project: str, output: Path, root: Path = ROOT) -> None:
    """Retain bounded owned Compose evidence before failed-project cleanup."""
    compose = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--project-name",
        project,
        "-f",
        str(root / "compose.classroom.yaml"),
        "--profile",
        "*",
    ]
    sections = []
    for title, command in (
        ("service states", [*compose, "ps", "--all"]),
        ("recent owned logs", [*compose, "logs", "--no-color", "--tail", "80"]),
    ):
        try:
            result = subprocess.run(
                command,
                cwd=root,
                env=environment(),
                capture_output=True,
                check=False,
                timeout=30,
            )
            content = (result.stdout + result.stderr).decode("utf-8", "replace")
            for key in ("DOCKERHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
                secret = os.environ.get(key, "")
                if secret:
                    content = content.replace(secret, "[redacted]")
            content = re.sub(r"(?im)authorization:\s*\S+", "Authorization: [redacted]", content)
            sections.append(f"## {title} (exit {result.returncode})\n{content[:24_000]}")
        except (OSError, subprocess.SubprocessError) as error:
            sections.append(f"## {title}\nDiagnostics unavailable: {type(error).__name__}")
    target = destination(output, root)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        raise ReleaseError("Diagnostic output must not be a link")
    write_json(
        target,
        {
            "schema_version": 1,
            "kind": "ds60-hub-diagnostics",
            "project": project,
            "sections": sections,
        },
    )


def read_selection(
    project: str, context: Any, latest_profile: str | None, root: Path = ROOT
) -> None:
    file = root / ".classroom" / project / "images.env"
    if file.is_symlink() or not file.is_file() or file.stat().st_size > 4096:
        raise ReleaseError("Hosted launcher did not save bounded image selection")
    fields: dict[str, str] = {}
    for line in file.read_text().splitlines():
        if "=" not in line:
            raise ReleaseError("Hosted launcher saved malformed image selection")
        key, value = line.split("=", 1)
        if key in fields:
            raise ReleaseError("Hosted launcher saved repeated image selection")
        fields[key] = value
    if (
        fields.get("DS60_IMAGE_SOURCE") != "hub"
        or fields.get("DS60_IMAGE_NAMESPACE") != context.namespace
        or fields.get("DS60_IMAGE_TAG") != context.version
    ):
        raise ReleaseError("Hosted launcher did not pin the exact published App release")
    if (
        latest_profile is not None
        and fields.get("DS60_IMAGE_TAG_" + latest_profile) != context.version
    ):
        raise ReleaseError("Hosted launcher did not resolve and pin the worker latest alias")


def launch_and_resume(
    context: Any,
    mode: str,
    group: str | None,
    skip_latest: bool,
    architecture: str,
    diagnostics: Path,
    root: Path = ROOT,
) -> dict[str, Any]:
    project = project_name(architecture)
    assert_new_project(project, root)
    workers = (
        ["python-core"]
        if mode == "full" or group == "python-core"
        else group_profiles(str(group), root)
    )
    latest_profile = None if skip_latest else workers[0]
    command = ["bash", "classroom"]
    if mode == "full" or group == "python-core":
        command.append("--starter")
    else:
        for worker in workers:
            command.extend(["--profile", worker])
    command.extend(["--from-hub", context.namespace])
    if skip_latest:
        command.extend(["--tag", context.version])
    else:
        command.extend(["--image-tag", f"{latest_profile}=latest"])
    command.extend(["--project", project, "--port", "0", "--database-port", "0", "--no-browser"])
    primary_error: Exception | None = None
    try:
        run_visible(command, timeout=2700, root=root)
        read_selection(project, context, latest_profile, root)
        before = {
            service: compose_ids(project, service, root)
            for service in [
                "postgres",
                "lab",
                *[
                    "python-core-worker"
                    if worker == "python-core"
                    else next(
                        line.split()[1]
                        for line in (root / "docker/classroom-images.tsv").read_text().splitlines()
                        if line.startswith(worker + " ")
                    )
                    for worker in workers
                ],
            ]
        }
        volumes_before = docker_items("volume", project, root)
        if len(volumes_before) < 2:
            raise ReleaseError(
                "Hosted classroom did not create persistent learning and database volumes"
            )
        run_visible(["bash", "classroom", "stop", "--project", project], timeout=180, root=root)
        run_visible(
            ["bash", "classroom", "resume", "--project", project, "--no-browser"],
            timeout=600,
            root=root,
        )
        after = {service: compose_ids(project, service, root) for service in before}
        if before != after or docker_items("volume", project, root) != volumes_before:
            raise ReleaseError("Hosted stop/resume replaced a worker, database or learning volume")
        read_selection(project, context, latest_profile, root)
        return {
            "profiles_started": workers,
            "saved_version": context.version,
            "latest_resolved": not skip_latest,
            "stop_resume_same_containers": True,
            "persistent_volumes": len(volumes_before),
        }
    except Exception as error:
        primary_error = error
        try:
            save_diagnostics(project, diagnostics, root)
        except Exception:
            print("Owned diagnostics could not be retained before cleanup", file=sys.stderr)
        raise
    finally:
        try:
            cleanup_project(project, root)
        except Exception as error:
            if primary_error is None:
                with suppress(Exception):
                    save_diagnostics(project, diagnostics, root)
                raise
            print(
                "Owned project cleanup also failed: " + type(error).__name__,
                file=sys.stderr,
            )


def accept(
    mode: str, receipt_path: Path, architecture: str, report_path: Path, root: Path = ROOT
) -> None:
    if architecture not in ARCHITECTURES:
        raise ReleaseError("Choose one native release architecture")
    report_file = destination(report_path, root)
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-hub-acceptance",
        "architecture": architecture,
        "mode": mode,
        "status": "checking",
    }
    try:
        receipt = read_json(receipt_path)
        native_engine(architecture, root)
        context, _, selected, group, skip_latest = verify_indexes(
            receipt, mode, root, architecture=architecture
        )
        report.update(
            {
                "revision": context.revision,
                "version": context.version,
                "run_id": context.run_id,
                "selected_profiles": sorted(selected),
                "index_profiles_inspected": sorted(
                    selected
                    if mode == "partial" or architecture == "amd64"
                    else {"app", "python-core"}
                ),
                "latest_skipped_newer_release": skip_latest,
            }
        )
        report.update(
            launch_and_resume(
                context,
                mode,
                group,
                skip_latest,
                architecture,
                report_file.with_name("hub-acceptance-diagnostics.json"),
                root,
            )
        )
        report["status"] = "accepted"
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        write_json(report_file, report)
    print(f"Hosted {mode} pull acceptance passed on native {architecture}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("--mode", choices=("full", "partial"), required=True)
    fetch.add_argument("--destination", type=Path, required=True)
    verify = sub.add_parser("accept")
    verify.add_argument("--mode", choices=("full", "partial"), required=True)
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--architecture", choices=ARCHITECTURES, required=True)
    verify.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "fetch":
            fetch_receipt(args.mode, args.destination)
        else:
            accept(args.mode, args.receipt, args.architecture, args.report)
        return 0
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        print("Hosted pull acceptance failed: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
