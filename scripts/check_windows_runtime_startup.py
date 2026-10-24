#!/usr/bin/env python3
"""Compare fixed Windows PowerShell startup hypotheses without changing machine policy.

This is a manual diagnostic experiment, not native ACL acceptance. Every child
runs fixed no-op/phase code for at most 15 seconds, followed by bounded reaping.
Only fixed phases, timings, return codes and exception classes leave the owned
temporary directory. No identities, paths, raw output or environment values are
reported. The separate native ACL smoke remains required.
"""

from __future__ import annotations

import argparse
import base64
import json
import ntpath
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ds60sqlpy.kubernetes_module import _windows_powershell_runtime  # noqa: E402

EXECUTION_SECONDS = 15
REAP_SECONDS = 5
PHASES = {"engine-started", "utility-cmdlet-ready"}
EXPANDED_OS_KEYS = (
    "COMPUTERNAME",
    "HOMEDRIVE",
    "HOMEPATH",
    "LOGONSERVER",
    "NUMBER_OF_PROCESSORS",
    "OS",
    "PATHEXT",
    "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_ARCHITEW6432",
    "PROCESSOR_IDENTIFIER",
    "PROCESSOR_LEVEL",
    "PROCESSOR_REVISION",
    "SESSIONNAME",
    "USERNAME",
    "USERDOMAIN",
    "USERDOMAIN_ROAMINGPROFILE",
    "USERDNSDOMAIN",
)
ENGINE = r"""[System.IO.File]::AppendAllText(
    $env:DS60_STARTUP_PHASE_FILE, 'engine-started' + [Environment]::NewLine
)
[Console]::Out.WriteLine('DS60-STARTUP-PHASE:engine-started')
[Console]::Out.Flush()
"""
UTILITY = r"""Write-Output 'DS60-STARTUP-PHASE:utility-cmdlet-ready'
[System.IO.File]::AppendAllText(
    $env:DS60_STARTUP_PHASE_FILE, 'utility-cmdlet-ready' + [Environment]::NewLine
)
"""


@dataclass(frozen=True)
class Variant:
    name: str
    mode: str = "command"
    expanded_environment: bool = False
    trusted_modules: bool = False
    bypass: bool = False
    no_window: bool = False
    probe: str = "utility"


VARIANTS = (
    Variant("current-env-command"),
    Variant("current-env-exit-only", probe="exit"),
    Variant("current-env-dotnet-only", probe="engine"),
    Variant("current-env-encoded", mode="encoded"),
    Variant("trusted-modules-command", trusted_modules=True),
    Variant("expanded-os-env-command", expanded_environment=True),
    Variant(
        "expanded-os-env-trusted-encoded",
        mode="encoded",
        expanded_environment=True,
        trusted_modules=True,
    ),
    Variant("process-policy-bypass", bypass=True),
    Variant("current-env-no-window", no_window=True),
    Variant("encoded-no-window", mode="encoded", no_window=True),
    Variant("fixed-file-bypass", mode="file", bypass=True),
    Variant("current-env-command-repeat"),
)


def phase_labels(data: bytes, *, file_output: bool = False) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    result = []
    for line in text.splitlines():
        if file_output:
            label = line.strip()
        elif line.startswith("DS60-STARTUP-PHASE:"):
            label = line.removeprefix("DS60-STARTUP-PHASE:").strip()
        else:
            continue
        if label in PHASES:
            result.append(label)
    return result


def variant_environment(
    variant: Variant, executable: str, base: Mapping[str, str], ambient: Mapping[str, str]
) -> dict[str, str]:
    result = dict(base)
    if variant.expanded_environment:
        result.update({key: ambient[key] for key in EXPANDED_OS_KEYS if key in ambient})
        result["COMSPEC"] = ntpath.join(base["SYSTEMROOT"], "System32", "cmd.exe")
    if variant.trusted_modules:
        result["PSModulePath"] = ntpath.join(ntpath.dirname(executable), "Modules")
    return result


def command_for(variant: Variant, executable: str, directory: Path) -> list[str]:
    source = "exit 0\n" if variant.probe == "exit" else ENGINE
    if variant.probe == "utility":
        source += UTILITY
    if variant.probe != "exit":
        source += "exit 0\n"
    argv = [executable, "-NoLogo", "-NoProfile", "-NonInteractive"]
    if variant.bypass:
        argv.extend(["-ExecutionPolicy", "Bypass"])
    if variant.mode == "encoded":
        argv.extend(
            ["-EncodedCommand", base64.b64encode(source.encode("utf-16-le")).decode("ascii")]
        )
    elif variant.mode == "file":
        script = directory / "fixed-startup.ps1"
        script.write_text(source, encoding="utf-8", newline="\n")
        argv.extend(["-File", str(script)])
    elif variant.mode == "command":
        argv.extend(["-Command", source])
    else:
        raise ValueError("Unknown fixed diagnostic mode.")
    return argv


def run_variant(
    variant: Variant, executable: str, base: Mapping[str, str], directory: Path
) -> dict[str, Any]:
    directory.mkdir()
    stdout_path, stderr_path = directory / "stdout.bin", directory / "stderr.bin"
    phase_path = directory / "phases.txt"
    environment = variant_environment(variant, executable, base, os.environ)
    environment["DS60_STARTUP_PHASE_FILE"] = str(phase_path)
    argv = command_for(variant, executable, directory)
    record: dict[str, Any] = {
        "variant": variant.name,
        "execution_budget_seconds": EXECUTION_SECONDS,
        "command_mode": variant.mode,
        "trusted_builtin_modules": variant.trusted_modules,
        "expanded_os_environment": variant.expanded_environment,
        "process_only_policy_bypass": variant.bypass,
        "no_console_window": variant.no_window,
        "startup_verified": False,
        "timed_out": False,
        "reaped": False,
        "child_started": False,
    }
    started = time.monotonic()
    process: subprocess.Popen[bytes] | None = None
    try:
        # File-backed capture avoids an unbounded communicate() after a Windows
        # timeout when another process retains an inherited pipe handle.
        with stdout_path.open("wb") as output, stderr_path.open("wb") as errors:
            process = subprocess.Popen(
                argv,
                env=environment,
                cwd=directory,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                if variant.no_window
                else 0,
            )
            record["child_started"] = True
            try:
                record["returncode"] = process.wait(timeout=EXECUTION_SECONDS)
                record["reaped"] = True
            except subprocess.TimeoutExpired:
                record["timed_out"] = True
                process.kill()  # Popen retains the handle of this exact owned child.
                record["returncode"] = process.wait(timeout=REAP_SECONDS)
                record["reaped"] = True
    except Exception as error:
        record["error_class"] = type(error).__name__
    finally:
        if process is not None and process.poll() is None:
            try:
                process.kill()
                record["returncode"] = process.wait(timeout=REAP_SECONDS)
                record["reaped"] = True
            except Exception as error:
                record["cleanup_error_class"] = type(error).__name__
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        with (
            stdout_path.open("rb") if stdout_path.exists() else tempfile.TemporaryFile() as capture
        ):
            raw = capture.read(16384)
        with phase_path.open("rb") if phase_path.exists() else tempfile.TemporaryFile() as capture:
            phases = capture.read(16384)
        record["stdout_phases"] = phase_labels(raw)
        record["file_phases"] = phase_labels(phases, file_output=True)
        record["stderr_present"] = stderr_path.exists() and stderr_path.stat().st_size > 0
    expected = [] if variant.probe == "exit" else ["engine-started"]
    if variant.probe == "utility":
        expected.append("utility-cmdlet-ready")
    record["startup_verified"] = (
        record.get("returncode") == 0
        and record["reaped"]
        and not record["timed_out"]
        and not record.get("error_class")
        and record["file_phases"] == expected
        and (variant.probe == "exit" or record["stdout_phases"] == expected)
    )
    return record


def run_matrix(
    report: dict[str, Any], executable: str, environment: Mapping[str, str], directory: Path
) -> None:
    for index, variant in enumerate(VARIANTS):
        result = run_variant(variant, executable, environment, directory / str(index))
        report["results"].append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
        if result["child_started"] and not result["reaped"]:
            report["failure_class"] = "ChildCleanupUnconfirmed"
            report["unattempted_variants"] = [item.name for item in VARIANTS[index + 1 :]]
            break
    report["diagnosis_complete"] = len(report["results"]) == len(VARIANTS) and all(
        not row["child_started"] or row["reaped"] for row in report["results"]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    if os.name != "nt":
        parser.error("This experiment requires native Windows.")
    root = os.environ.get("RUNNER_TEMP")
    if not root or not Path(root).is_dir():
        parser.error("RUNNER_TEMP must name the existing disposable CI temporary directory.")
    report: dict[str, Any] = {
        "schema_version": 1,
        "diagnosis_complete": False,
        "native_acl_qualified": False,
        "interpretation": "Startup comparisons only; the separate real ACL smoke must pass.",
        "results": [],
    }
    try:
        executable, environment = _windows_powershell_runtime()
        with tempfile.TemporaryDirectory(prefix="ds60-winps-diagnosis-", dir=root) as temporary:
            run_matrix(report, executable, environment, Path(temporary))
        report["temporary_capture_removed"] = True
    except Exception as error:
        report["diagnosis_complete"] = False
        report["failure_class"] = type(error).__name__
    finally:
        report["startup_verified_variants"] = [
            r["variant"] for r in report["results"] if r["startup_verified"]
        ]
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    # Completing the comparisons is distinct from accepting any runtime or ACL.
    return int(not report["diagnosis_complete"])


if __name__ == "__main__":
    raise SystemExit(main())
