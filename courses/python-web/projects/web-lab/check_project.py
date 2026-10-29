"""Qualify one fresh owned web-lab copy, then retain evidence/data and remove its containers."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

SOURCE = Path(__file__).resolve().parent

IGNORED_SOURCE_NAMES = {
    ".workshop",
    "__pycache__",
    "collected-static",
    ".DS_Store",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "node_modules",
}


DIAGNOSTIC_TAIL_BYTES = 4096
DIAGNOSTIC_TOTAL_BYTES = 16384
DIAGNOSTIC_LOG_NAMES = (
    "start.log",
    "services.log",
    "cleanup.log",
    "prepare.log",
    "http-check.log",
    "pending-create.log",
    "worker-stop.log",
    "pending-release.log",
    "worker-resume.log",
    "pending-reconciled.log",
    "stop.log",
    "resume.log",
    "resume-readback.log",
    "replace.log",
    "replace-readback.log",
    "browser.log",
    "shipped-source.log",
)
CREDENTIAL_LINE = re.compile(
    r"(?i)\b[\w-]*(?:password|passwd|passphrase|signing[_-]?key|secret|token|csrf|"
    r"cookie|authorization|signature|credential)[\w-]*[\\\"' \t]*[:=]"
)


def regular_file_bytes(path: Path, maximum: int, *, tail: bool = False) -> tuple[bytes, int]:
    """Read only a bounded ordinary file, refusing links and special files."""
    if path.is_symlink():
        raise ValueError("Diagnostic files must not be links")
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
    )
    with os.fdopen(descriptor, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Diagnostics require ordinary files")
        size = metadata.st_size
        if tail:
            stream.seek(max(0, size - maximum))
            data = stream.read(maximum)
            if size > maximum:
                # A truncated header/assignment must not leave an unlabelled secret suffix.
                data = data.partition(b"\n")[2]
            return data, size
        data = stream.read(maximum + 1)
        if len(data) > maximum:
            raise ValueError("Private redaction input exceeds its fixed bound")
        return data, size


def diagnostic_secrets(workspace: Path) -> list[str]:
    private = workspace / ".workshop"
    if workspace.is_symlink() or private.is_symlink():
        raise ValueError("Private redaction inputs must not follow links")
    values = []
    for name in ("password", "signing-key"):
        path = private / name
        if not path.exists() and not path.is_symlink():
            raise ValueError("Private redaction inputs are incomplete")
        data, _ = regular_file_bytes(path, 4096)
        value = data.decode("utf-8").strip()
        if not value:
            raise ValueError("Private redaction inputs are empty")
        values.append(value)
    return sorted(set(values), key=len, reverse=True)


def redact_diagnostic_text(text: str, secrets: list[str]) -> str:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    for value in secrets:
        text = text.replace(value, "[REDACTED]")
    lines = []
    for line in text.splitlines():
        if CREDENTIAL_LINE.search(line) or re.search(r"\bfill\([\"']", line):
            lines.append("[REDACTED credential-bearing log line]")
            continue
        line = re.sub(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9+/_=.:-]+", r"\1 [REDACTED]", line)
        line = re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^/\s:@]+:[^@\s/]+@", r"\1[REDACTED]@", line)
        # Signed download query strings are unnecessary for startup diagnosis.
        line = re.sub(r"https?://[^\s<>\"']*\?[^\s<>\"']+", "[REDACTED query URL]", line)
        lines.append(line)
    return "\n".join(lines)


def collect_failure_diagnostics(evidence: Path, workspace: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "scope": "bounded-redacted-owned-project-logs",
        "per_log_tail_bytes": DIAGNOSTIC_TAIL_BYTES,
        "maximum_total_text_bytes": DIAGNOSTIC_TOTAL_BYTES,
        "logs": [],
        "omitted_logs": [],
    }
    if (
        evidence.absolute() != (workspace / ".workshop/evidence").absolute()
        or evidence.is_symlink()
    ):
        result["warning"] = "Withheld diagnostics from an unexpected evidence path"
        return result
    try:
        secrets = diagnostic_secrets(workspace)
    except (OSError, ValueError, UnicodeError):
        result["warning"] = "Withheld log text because private redaction inputs were unavailable"
        return result
    remaining = DIAGNOSTIC_TOTAL_BYTES
    for name in DIAGNOSTIC_LOG_NAMES:
        path = evidence / name
        if not path.exists() and not path.is_symlink():
            continue
        if remaining == 0:
            result["omitted_logs"].append(name)
            continue
        try:
            data, size = regular_file_bytes(path, DIAGNOSTIC_TAIL_BYTES, tail=True)
            text = redact_diagnostic_text(data.decode("utf-8", errors="replace"), secrets)
            encoded = text.encode("utf-8")
            budget = min(remaining, DIAGNOSTIC_TAIL_BYTES)
            truncated = size > DIAGNOSTIC_TAIL_BYTES or len(encoded) > budget
            # Ignore an incomplete UTF-8 character at the already-redacted budget boundary.
            text = encoded[:budget].decode("utf-8", errors="ignore")
            remaining -= len(text.encode("utf-8"))
            result["logs"].append(
                {"name": name, "text": text, "bytes_on_disk": size, "truncated": truncated}
            )
        except (OSError, ValueError):
            result["omitted_logs"].append(name)
    return result


def retain_failure_diagnostics(record: dict[str, Any], evidence: Path, workspace: Path) -> None:
    if record.get("accepted") is True:
        return
    previous = record.get("failure_diagnostics", {})
    latest = collect_failure_diagnostics(evidence, workspace)
    # Preserve already-redacted startup evidence even if cleanup removed its log file.
    remembered = {
        item["name"]: item
        for item in previous.get("logs", [])
        if isinstance(item, dict) and item.get("name") in DIAGNOSTIC_LOG_NAMES
    }
    remembered.update({item["name"]: item for item in latest["logs"]})
    remaining = DIAGNOSTIC_TOTAL_BYTES
    latest["logs"] = []
    for name in DIAGNOSTIC_LOG_NAMES:
        if name not in remembered or remaining == 0:
            continue
        item = dict(remembered[name])
        encoded = item["text"].encode("utf-8")
        budget = min(remaining, DIAGNOSTIC_TAIL_BYTES)
        item["text"] = encoded[:budget].decode("utf-8", errors="ignore")
        item["truncated"] = item["truncated"] or len(encoded) > budget
        remaining -= len(item["text"].encode("utf-8"))
        latest["logs"].append(item)
    record["failure_diagnostics"] = latest
    try:
        secrets = diagnostic_secrets(workspace)
    except (OSError, ValueError, UnicodeError):
        secrets = []
        safe = False
    else:
        safe = True
    for field in ("failure", "cleanup_failure", "service_log_failure"):
        if isinstance(record.get(field), dict) and isinstance(record[field].get("message"), str):
            record[field]["message"] = (
                redact_diagnostic_text(record[field]["message"], secrets)[:2048]
                if safe
                else "Diagnostic message withheld because redaction inputs were unavailable"
            )


def clean_environment() -> dict[str, str]:
    excluded = {
        "DOCKERHUB_USERNAME",
        "DOCKERHUB_TOKEN",
        "HUB_USER",
        "HUB_TOKEN",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "DOCKER_CONFIG",
        "DOCKER_DEFAULT_PLATFORM",
        "ACTIONS_RUNTIME_TOKEN",
    }
    return {
        key: value
        for key, value in os.environ.items()
        if key not in excluded and not key.startswith(("DS60_", "COMPOSE_", "WORKSHOP_"))
    }


def browser_interpreter(path: Path) -> Path:
    # Preserve a venv's lexical path; resolving its symlink can lose site-packages.
    absolute = path.absolute()
    if not absolute.is_file():
        raise ValueError("Use an explicitly prepared browser Python interpreter")
    return absolute


def require_native_image(identity: dict[str, str], architecture: str) -> None:
    if (
        architecture not in {"arm64", "amd64"}
        or identity["system"] != "linux"
        or identity["architecture"] != architecture
    ):
        raise ValueError("Use images matching the supported native Linux engine; no emulation")


def run(
    command: list[str],
    *,
    cwd: Path,
    log: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    timeout: int = 240,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=clean_environment() if env is None else env,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        if log is not None:
            partial = []
            for value in (error.stdout, error.stderr):
                partial.append(
                    value.decode("utf-8", errors="replace")
                    if isinstance(value, bytes)
                    else value or ""
                )
            # A diagnostic write must not replace the operation's original timeout.
            with contextlib.suppress(OSError):
                log.write_text("".join(partial))
        raise
    if log is not None:
        log.write_text(result.stdout + result.stderr)
    if check and result.returncode:
        raise RuntimeError(
            f"Command failed with exit {result.returncode}; see {log.name if log else command[0]}"
        )
    return result


def digest_tree(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if (
            any(part in IGNORED_SOURCE_NAMES for part in path.relative_to(root).parts)
            or path.suffix == ".pyc"
        ):
            continue
        if path.is_symlink():
            raise ValueError("Project source must not contain symlinks")
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def image_identity(reference: str, cwd: Path) -> dict[str, str]:
    result = run(
        ["docker", "image", "inspect", "--format", "{{.Id}} {{.Os}} {{.Architecture}}", reference],
        cwd=cwd,
    )
    identifier, system, architecture = result.stdout.strip().split()
    return {"id": identifier, "system": system, "architecture": architecture}


def inspect_containers(project: str, cwd: Path) -> dict[str, dict[str, str]]:
    result = run(
        [
            "docker",
            "ps",
            "--all",
            "--filter",
            "label=com.docker.compose.project=" + project,
            "--format",
            "{{.ID}}",
        ],
        cwd=cwd,
    )
    rows = {}
    for identifier in result.stdout.split():
        value = run(
            [
                "docker",
                "inspect",
                "--format",
                '{{index .Config.Labels "com.docker.compose.service"}} '
                '{{index .Config.Labels "ds60.workshop"}} {{.Id}} {{.Image}}',
                identifier,
            ],
            cwd=cwd,
        )
        service, owner, full_id, image = value.stdout.strip().split()
        if owner != "python-web-lab":
            raise RuntimeError("Refusing resources without exact workshop ownership")
        rows[service] = {"id": full_id, "image": image}
    return rows


def free_ports() -> list[int]:
    sockets = []
    try:
        for _ in range(3):
            handle = socket.socket()
            handle.bind(("127.0.0.1", 0))
            sockets.append(handle)
        return [handle.getsockname()[1] for handle in sockets]
    finally:
        for handle in sockets:
            handle.close()


def write_report(path: Path, record: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".pending")
    if temporary.is_symlink():
        raise ValueError("Refusing a symlink report staging path")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def qualify(args: argparse.Namespace) -> dict[str, Any]:
    workspace = args.workspace.absolute()
    report = args.report.absolute()
    if not args.confirm_disposable:
        raise ValueError("Pass --confirm-disposable for this new synthetic project")
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("--workspace must be a fresh nonexistent owned copy path")
    if report.exists() or report.is_symlink() or not report.parent.is_dir():
        raise ValueError("--report must be a new file in an existing evidence directory")
    if not workspace.parent.is_dir():
        raise ValueError("Prepare the workspace parent before this check")
    browser_python = browser_interpreter(args.browser_python)
    source_hashes = digest_tree(SOURCE)
    project = "ds60-pyweb-check-" + uuid.uuid4().hex[:12]
    existing = inspect_containers(project, SOURCE)
    if existing:
        raise RuntimeError("Refusing an already used Compose project")
    for kind, name in (("volume", project + "_postgres-data"), ("network", project + "_default")):
        if run(["docker", kind, "inspect", name], cwd=SOURCE, check=False).returncode == 0:
            raise RuntimeError("Refusing an already used project resource")
    daemon = (
        run(["docker", "info", "--format", "{{.OSType}} {{.Architecture}}"], cwd=SOURCE)
        .stdout.strip()
        .split()
    )
    aliases = {"aarch64": "arm64", "x86_64": "amd64"}
    architecture = aliases.get(daemon[1], daemon[1])
    base = image_identity(args.image, SOURCE)
    postgres = image_identity(args.postgres_image, SOURCE)
    if daemon[0] != "linux":
        raise ValueError("Use a Linux Docker engine")
    for identity in (base, postgres):
        require_native_image(identity, architecture)
    shutil.copytree(
        SOURCE,
        workspace,
        ignore=shutil.ignore_patterns(*IGNORED_SOURCE_NAMES, "*.pyc"),
    )
    if digest_tree(workspace) != source_hashes:
        raise RuntimeError("Fresh project copy differs from public source")
    evidence = workspace / ".workshop" / "evidence"
    evidence.mkdir(parents=True, mode=0o700)
    ports = dict(zip(("flask", "fastapi", "django"), free_ports(), strict=True))
    environment = clean_environment()
    environment.update(
        {
            "WORKSHOP_PROJECT": project,
            "WORKSHOP_BASE_IMAGE": args.image,
            "WORKSHOP_POSTGRES_IMAGE": args.postgres_image,
        }
    )
    environment.update(
        {"WORKSHOP_" + key.upper() + "_PORT": str(value) for key, value in ports.items()}
    )
    compose = [
        "docker",
        "compose",
        "--project-name",
        project,
        "--env-file",
        ".workshop/settings.env",
        "-f",
        "compose.yaml",
    ]
    record: dict[str, Any] = {
        "schema_version": 1,
        "kind": "python-web-project",
        "accepted": False,
        "project": project,
        "native_architecture": architecture,
        "base_image": base,
        "postgres_image": postgres,
        "source_sha256": source_hashes,
        "checks": [],
        "learner_resources_used": False,
        "volume_preserved": False,
        "ports": ports,
    }
    started = time.monotonic()
    failure: BaseException | None = None
    final_report_retained = False

    def save_report(phase: str, *, provisional: bool = False) -> bool:
        nonlocal failure
        payload = (
            {**record, "accepted": False, "finalization": "owned-cleanup-pending"}
            if provisional
            else record
        )
        try:
            write_report(report, payload)
        except OSError as error:
            record.setdefault("diagnostic_warnings", []).append(
                {"phase": phase, "type": type(error).__name__}
            )
            record["accepted"] = False
            if failure is None:
                failure = error
                record["failure"] = {
                    "type": type(error).__name__,
                    "message": "Could not retain the " + phase + " evidence report",
                }
            return False
        return True

    try:
        run(
            ["./workshop", "prepare"],
            cwd=workspace,
            env=environment,
            log=evidence / "prepare.log",
            timeout=300,
        )
        built = image_identity(project + "-image:1.0", workspace)
        require_native_image(built, architecture)
        record["workshop_image"] = built
        probe = (
            "import json,hashlib,sys;from pathlib import Path;r=Path('/opt/web-lab');"
            "expected=json.load(sys.stdin);"
            "actual={k:hashlib.sha256((r/k).read_bytes()).hexdigest() for k in expected};"
            "assert actual==expected;print(json.dumps(actual,sort_keys=True))"
        )
        verified = run(
            [
                "docker",
                "run",
                "--rm",
                "--pull",
                "never",
                "--network",
                "none",
                "--read-only",
                "--memory",
                "128m",
                "--cpus",
                "1",
                "--entrypoint",
                "python",
                "-i",
                built["id"],
                "-c",
                probe,
            ],
            cwd=workspace,
            input_text=json.dumps(source_hashes),
            log=evidence / "shipped-source.log",
        )
        record["shipped_source_sha256"] = json.loads(verified.stdout)
        record["checks"].append("native-image-and-shipped-source")
        run(["./workshop", "start"], cwd=workspace, env=environment, log=evidence / "start.log")
        before = inspect_containers(project, workspace)
        if set(before) != {"postgres", "flask", "fastapi", "django", "worker"}:
            raise AssertionError("Expected exactly five owned persistent containers")
        run(
            ["./workshop", "check"], cwd=workspace, env=environment, log=evidence / "http-check.log"
        )
        accepted = json.loads((workspace / ".workshop/acceptance.json").read_text())
        if accepted["status"] != "passed":
            raise AssertionError("Service receipt did not pass")
        record["service"] = accepted
        record["checks"].append("real-http-websocket-sse-postgresql")
        execute_api = compose + ["exec", "-T"]
        for name, port in ports.items():
            execute_api += ["-e", "WORKSHOP_" + name.upper() + "_PORT=" + str(port)]
        execute_api += ["fastapi", "python", "check_api.py"]
        pending = run(
            execute_api + ["--pending-create"], cwd=workspace, log=evidence / "pending-create.log"
        )
        pending_record = json.loads(pending.stdout)
        run(compose + ["stop", "worker"], cwd=workspace, log=evidence / "worker-stop.log")
        run(
            execute_api + ["--pending-release"],
            cwd=workspace,
            input_text=json.dumps(pending_record),
            log=evidence / "pending-release.log",
        )
        run(compose + ["start", "worker"], cwd=workspace, log=evidence / "worker-resume.log")
        reconciled = run(
            execute_api + ["--pending-verify"],
            cwd=workspace,
            input_text=json.dumps(pending_record),
            log=evidence / "pending-reconciled.log",
        )
        record["worker_reconciliation"] = json.loads(reconciled.stdout)
        record["checks"].append("stopped-worker-durable-job-reconciliation")
        run(["./workshop", "stop"], cwd=workspace, env=environment, log=evidence / "stop.log")
        run(["./workshop", "resume"], cwd=workspace, env=environment, log=evidence / "resume.log")
        after = inspect_containers(project, workspace)
        if before != after:
            raise AssertionError("Stop/resume changed container or image identity")
        record["resume_containers"] = {"before": before, "after": after}
        run(
            ["./workshop", "verify"],
            cwd=workspace,
            env=environment,
            log=evidence / "resume-readback.log",
        )
        record["resume_readback"] = json.loads((workspace / ".workshop/readback.json").read_text())
        record["checks"].append("exact-five-container-resume-and-saved-records")
        run(["./workshop", "replace"], cwd=workspace, env=environment, log=evidence / "replace.log")
        replaced = inspect_containers(project, workspace)
        if replaced["postgres"] != before["postgres"] or any(
            replaced[name]["id"] == before[name]["id"]
            for name in ("flask", "fastapi", "django", "worker")
        ):
            raise AssertionError("Replacement did not preserve only the database container")
        record["replacement_containers"] = replaced
        run(
            ["./workshop", "verify"],
            cwd=workspace,
            env=environment,
            log=evidence / "replace-readback.log",
        )
        record["replacement_readback"] = json.loads(
            (workspace / ".workshop/readback.json").read_text()
        )
        record["checks"].append("app-replacement-and-saved-records")
        browser_command = [
            str(browser_python),
            str(workspace / "check_browser.py"),
            "--output",
            str(evidence / "browser"),
        ]
        for name, port in ports.items():
            browser_command += ["--" + name, f"http://127.0.0.1:{port}"]
        run(
            browser_command,
            cwd=workspace,
            env=environment,
            log=evidence / "browser.log",
            timeout=240,
        )
        record["browser"] = json.loads((evidence / "browser/browser-acceptance.json").read_text())
        record["checks"].append("actual-three-framework-browser-and-offline-docs")
        record["accepted"] = True
    except BaseException as error:
        failure = error
        record["failure"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        record["seconds"] = time.monotonic() - started
        # Save all observations before removing only this newly owned synthetic topology.
        if (workspace / ".workshop/settings.env").is_file():
            try:
                run(
                    compose + ["logs", "--no-color", "--tail", "200"],
                    cwd=workspace,
                    log=evidence / "services.log",
                    timeout=30,
                    check=False,
                )
            except Exception as error:
                record["service_log_failure"] = {
                    "type": type(error).__name__,
                    "message": str(error),
                }
                record.setdefault("diagnostic_warnings", []).append(
                    {"phase": "service-logs", "type": type(error).__name__}
                )
        retain_failure_diagnostics(record, evidence, workspace)
        save_report("initial", provisional=True)
        try:
            inspect_containers(project, workspace)  # Refuse cleanup if ownership no longer matches.
            if (workspace / ".workshop/settings.env").is_file():
                run(
                    compose + ["down", "--remove-orphans"],
                    cwd=workspace,
                    log=evidence / "cleanup.log",
                )
            if inspect_containers(project, workspace):
                raise AssertionError("Owned containers remain after cleanup")
            volume = run(
                [
                    "docker",
                    "volume",
                    "inspect",
                    "--format",
                    '{{index .Labels "ds60.workshop"}}',
                    project + "_postgres-data",
                ],
                cwd=workspace,
                check=False,
            )
            record["volume_preserved"] = (
                volume.returncode == 0 and volume.stdout.strip() == "python-web-lab"
            )
            record["containers_cleaned"] = True
        except BaseException as error:
            record["cleanup_failure"] = {"type": type(error).__name__, "message": str(error)}
            record["accepted"] = False
            if failure is None:
                failure = error
        if record["accepted"] and not record["volume_preserved"]:
            record["accepted"] = False
            failure = AssertionError("Expected preserved synthetic database volume")
        record["evidence_directory"] = str(evidence)
        # Keep bounded startup/service and cleanup evidence in the top-level artifact itself.
        retain_failure_diagnostics(record, evidence, workspace)
        final_report_retained = save_report("final")
        if not final_report_retained:
            # This small warning is safe even when the filesystem cannot retain a report.
            with contextlib.suppress(OSError):
                print(
                    json.dumps(
                        {
                            "kind": "python-web-report-unavailable",
                            "diagnostic_warnings": record.get("diagnostic_warnings", []),
                            "accepted": False,
                        },
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                )
    if failure is not None:
        detail = (
            f"retained report: {report}"
            if final_report_retained
            else f"final report unavailable; private evidence directory: {evidence}"
        )
        raise RuntimeError("Web project qualification failed; " + detail) from failure
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--image", required=True)
    parser.add_argument("--postgres-image", default="mirror.gcr.io/library/postgres:17")
    parser.add_argument("--browser-python", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    result = qualify(parser.parse_args())
    print(
        json.dumps(
            {
                "accepted": result["accepted"],
                "checks": result["checks"],
                "volume_preserved": result["volume_preserved"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
