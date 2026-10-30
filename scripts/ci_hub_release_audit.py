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


def preflight(request: recovery.Request, directory: Path, root: Path) -> dict[str, Any]:
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
    parser.add_argument("command", choices=("preflight", "prepare", "accept"))
    parser.add_argument("--published-sha", required=True)
    parser.add_argument("--published-run-id", required=True)
    parser.add_argument("--published-attempt", required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--group")
    parser.add_argument("--architecture", choices=ARCHITECTURES)
    parser.add_argument("--skip-latest", action="store_true")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    try:
        request = recovery.dispatch_request(
            args.published_sha, args.published_run_id, args.published_attempt
        )
        directory = hub.destination(args.directory, ROOT)
        if args.command == "preflight":
            report = preflight(request, directory, ROOT)
            if args.github_output:
                with args.github_output.open("a") as stream:
                    stream.write(
                        "matrix=" + json.dumps(report["matrix"], separators=(",", ":")) + "\n"
                    )
        elif args.command == "prepare":
            prepare(request, directory, ROOT)
        else:
            if args.group is None or args.architecture is None:
                raise ReleaseError("Native acceptance requires an explicit group and architecture")
            accept(request, directory, args.group, args.architecture, not args.skip_latest, ROOT)
        return 0
    except (OSError, ValueError, ReleaseError, subprocess.SubprocessError) as error:
        print("Full-release audit failed: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
