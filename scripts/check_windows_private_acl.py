#!/usr/bin/env python3
"""Exercise real Windows runtime ACLs in an owned temporary directory.

Run this native integration check separately from parallel unit tests. It never
creates cluster credentials. Diagnostics expose only fixed operation phases,
return codes and exception classes, never account identities, paths or ACL text.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ds60sqlpy import kubernetes_module  # noqa: E402

PHASES = {
    "DS60-ACL-PHASE:startup",
    "DS60-ACL-PHASE:identity",
    "DS60-ACL-PHASE:establish",
    "DS60-ACL-PHASE:set-acl",
    "DS60-ACL-PHASE:read-acl",
    "DS60-ACL-PHASE:read-rules",
    "DS60-ACL-PHASE:read-owner",
    "DS60-ACL-PHASE:verify",
}


FAILURE_STAGES = frozenset(
    {
        "powershell-runtime-startup",
        "establish-private-directory",
        "private-file-readback",
        "synthetic-broad-acl-setup",
        "broad-file-acl-was-accepted",
        "broad-file-acl-rejection-unverified",
    }
)


def observed_phases(output: str | bytes | None) -> list[str]:
    text = output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output or ""
    return [
        line.strip().removeprefix("DS60-ACL-PHASE:")
        for line in text.splitlines()
        if line.strip() in PHASES
    ]


def instrument_script(source: str) -> str:
    points = (
        ("$sid=", "identity"),
        ("if($env:DS60_PRIVATE_ESTABLISH", "establish"),
        ("  [System.IO.Directory]::SetAccessControl", "set-acl"),
        ("if([System.IO.Directory]::Exists", "read-acl"),
        ("$rules=", "read-rules"),
        ("$owner=", "read-owner"),
        ("if($owner", "verify"),
    )

    def phase(label: str) -> str:
        return f"[Console]::Out.WriteLine('DS60-ACL-PHASE:{label}'); [Console]::Out.Flush()"

    lines = [phase("startup")]
    for line in source.splitlines():
        for prefix, label in points:
            if line.startswith(prefix):
                lines.append(phase(label))
        lines.append(line)
    return "\n".join(lines)


def native_acl_smoke(report: dict[str, Any], directory: Path) -> None:
    original_run = subprocess.run
    executable, startup_environment = kubernetes_module._windows_powershell_runtime()
    prefix = [executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command"]

    def observed_run(argv: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        if list(argv[:-1]) != prefix:
            raise ValueError("Unexpected native ACL command shape.")
        operation = kwargs.pop("probe_operation", "acl")
        command = [*argv[:-1], instrument_script(argv[-1])]
        options = {**kwargs, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
        record: dict[str, Any] = {"operation": operation, "timeout_seconds": kwargs["timeout"]}
        report["commands"].append(record)
        started = time.monotonic()
        try:
            result = original_run(command, **options)
        except subprocess.TimeoutExpired as error:
            record.update(phases=observed_phases(error.stdout), timed_out=True)
            raise
        except OSError as error:
            record.update(phases=[], launch_error=type(error).__name__)
            raise
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        record.update(
            phases=observed_phases(result.stdout),
            returncode=result.returncode,
            stderr_present=bool(result.stderr),
        )
        return result

    startup = observed_run(
        [*prefix, "exit 0"],
        env=startup_environment,
        stdin=subprocess.DEVNULL,
        timeout=15,
        check=False,
        probe_operation="runtime-startup",
    )
    if startup.returncode != 0 or observed_phases(startup.stdout) != ["startup"]:
        raise RuntimeError("powershell-runtime-startup")
    report["checks"].append("Built-in Windows PowerShell runtime starts within its bounded budget")

    with patch("ds60sqlpy.kubernetes_module.subprocess.run", observed_run):
        if not kubernetes_module._windows_private_acl(directory, establish=True):
            raise RuntimeError("establish-private-directory")
        report["checks"].append("Current-user and SYSTEM directory ACL established and verified")
        fixture = directory / "synthetic-runtime.txt"
        fixture.write_bytes(b"synthetic-runtime-fixture")
        if kubernetes_module._private_file(fixture, 100) != b"synthetic-runtime-fixture":
            raise RuntimeError("private-file-readback")
        report["checks"].append("Inherited private file ACL accepted by the runtime boundary")

        # Grant an inheritable broad ACE on an owned synthetic parent, then
        # create a child that inherits it. The private-file boundary must reject
        # inherited broad permissions as well as explicit file permissions.
        broad_parent = directory / "synthetic-broad-parent"
        broad_parent.mkdir()
        script = r"""
$ErrorActionPreference='Stop'
$acl=[System.IO.Directory]::GetAccessControl($env:DS60_PRIVATE_PATH)
$everyone=[Security.Principal.SecurityIdentifier]::new('S-1-1-0')
$rule=[Security.AccessControl.FileSystemAccessRule]::new(
  $everyone,
  [Security.AccessControl.FileSystemRights]::Read,
  [Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit',
  [Security.AccessControl.PropagationFlags]::None,
  [Security.AccessControl.AccessControlType]::Allow
)
$acl.AddAccessRule($rule)
[System.IO.Directory]::SetAccessControl($env:DS60_PRIVATE_PATH,$acl)
"""
        environment = {**startup_environment, "DS60_PRIVATE_PATH": str(broad_parent)}
        grant = observed_run(
            [*prefix, script],
            env=environment,
            stdin=subprocess.DEVNULL,
            timeout=15,
            check=False,
        )
        if grant.returncode:
            raise RuntimeError("synthetic-broad-acl-setup")
        broad_fixture = broad_parent / "synthetic-inherited.txt"
        broad_fixture.write_bytes(b"synthetic-runtime-fixture")
        try:
            kubernetes_module._private_file(broad_fixture, 100)
        except kubernetes_module.KubernetesRefusal:
            rejection = report["commands"][-1]
            if rejection.get("returncode") != 3 or rejection.get("timed_out"):
                raise RuntimeError("broad-file-acl-rejection-unverified") from None
            report["checks"].append(
                "Inherited broad file ACL refused without accepting its contents"
            )
        else:
            raise RuntimeError("broad-file-acl-was-accepted")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    if os.name != "nt":
        parser.error("This check requires native Windows; no ACL result can be inferred here.")
    temporary_root = os.environ.get("RUNNER_TEMP")
    if not temporary_root or not Path(temporary_root).is_dir():
        parser.error("Set RUNNER_TEMP to the existing disposable CI temporary directory.")
    report: dict[str, Any] = {"schema_version": 1, "passed": False, "checks": [], "commands": []}
    try:
        with tempfile.TemporaryDirectory(prefix="ds60-native-acl-", dir=temporary_root) as root:
            native_acl_smoke(report, Path(root))
        report["temporary_workspace_removed"] = True
        report["passed"] = True
    except Exception as error:
        report["failure_type"] = type(error).__name__
        # Only fixed stage labels may enter the public artifact. RuntimeError
        # alone does not establish that a native exception's text is controlled.
        if type(error) is RuntimeError and str(error) in FAILURE_STAGES:
            report["failure_stage"] = str(error)
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        for index, command in enumerate(report["commands"], 1):
            print(f"ACL command {index}: {json.dumps(command, sort_keys=True)}")
        print("Native Windows private ACL check: " + ("PASS" if report["passed"] else "FAIL"))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
