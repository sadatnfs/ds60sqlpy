"""The native differential probe is fixed, bounded and cannot report private text."""

from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import check_windows_runtime_startup as probe

EXE = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
BASE = {"SYSTEMROOT": r"C:\Windows", "TEMP": "synthetic-temp", "PATH": "trusted-system-path"}


def test_fixed_variants_include_repeated_baseline_without_inventing_acl_acceptance() -> None:
    assert len(probe.VARIANTS) == 12
    assert len({item.name for item in probe.VARIANTS}) == 12
    first, last = probe.VARIANTS[0], probe.VARIANTS[-1]
    assert first.name == "current-env-command" and last.name == "current-env-command-repeat"
    assert (
        first.mode,
        first.expanded_environment,
        first.trusted_modules,
        first.bypass,
        first.no_window,
        first.probe,
    ) == (
        last.mode,
        last.expanded_environment,
        last.trusted_modules,
        last.bypass,
        last.no_window,
        last.probe,
    )


@pytest.mark.parametrize("variant", probe.VARIANTS, ids=lambda variant: variant.name)
def test_variant_environment_never_inherits_module_hooks_or_credentials(
    variant: probe.Variant,
) -> None:
    ambient = {
        "GITHUB_TOKEN": "must-not-copy",
        "KUBECONFIG": "must-not-copy",
        "PSModulePath": "untrusted-modules",
        "PSExecutionPolicyPreference": "untrusted-policy",
        "PATH": "untrusted-tools",
        "USERNAME": "synthetic-account",
        "NUMBER_OF_PROCESSORS": "4",
        "COMSPEC": "untrusted-shell",
    }
    result = probe.variant_environment(variant, EXE, BASE, ambient)
    assert result["PATH"] == BASE["PATH"]
    assert not {"GITHUB_TOKEN", "KUBECONFIG", "PSExecutionPolicyPreference"} & result.keys()
    assert ("USERNAME" in result) is variant.expanded_environment
    if variant.trusted_modules:
        assert result["PSModulePath"] == r"C:\Windows\System32\WindowsPowerShell\v1.0\Modules"
    else:
        assert "PSModulePath" not in result
    assert "untrusted" not in json.dumps(result)


def test_command_forms_preserve_fixed_program_and_process_only_flags(tmp_path: Path) -> None:
    encoded = probe.command_for(
        probe.Variant("test", mode="encoded", bypass=True, no_window=True), EXE, tmp_path
    )
    assert encoded[:4] == [EXE, "-NoLogo", "-NoProfile", "-NonInteractive"]
    assert encoded[4:6] == ["-ExecutionPolicy", "Bypass"]
    decoded = base64.b64decode(encoded[-1]).decode("utf-16-le")
    assert decoded == probe.ENGINE + probe.UTILITY + "exit 0\n"
    file_command = probe.command_for(probe.Variant("test", mode="file"), EXE, tmp_path)
    assert file_command[-2] == "-File"
    assert Path(file_command[-1]).read_text() == decoded
    assert "Set-ExecutionPolicy" not in decoded and "Set-Acl" not in decoded


def test_phase_filter_never_reproduces_unrecognized_output() -> None:
    raw = b"private-value\nDS60-STARTUP-PHASE:engine-started\nDS60-STARTUP-PHASE:private-value\n"
    assert probe.phase_labels(raw) == ["engine-started"]
    assert probe.phase_labels(b"engine-started\nprivate-value\n", file_output=True) == [
        "engine-started"
    ]


@pytest.mark.parametrize("timed_out", [False, True])
def test_child_result_is_bounded_and_report_contains_no_raw_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, timed_out: bool
) -> None:
    waits: list[float] = []
    processes: list[Any] = []

    class Process:
        def __init__(self, argv: list[str], **kwargs: Any) -> None:
            self.returncode: int | None = None
            self.killed = False
            processes.append(self)
            kwargs["stdout"].write(
                b"private-output\nDS60-STARTUP-PHASE:engine-started\n"
                b"DS60-STARTUP-PHASE:utility-cmdlet-ready\n"
            )
            kwargs["stderr"].write(b"private-error")
            Path(kwargs["env"]["DS60_STARTUP_PHASE_FILE"]).write_text(
                "engine-started\nutility-cmdlet-ready\n"
            )
            assert kwargs["stdin"] == subprocess.DEVNULL

        def wait(self, timeout: float) -> int:
            waits.append(timeout)
            if timed_out and not self.killed:
                raise subprocess.TimeoutExpired("fixed-child", timeout)
            self.returncode = -9 if self.killed else 0
            return self.returncode

        def kill(self) -> None:
            self.killed = True

        def poll(self) -> int | None:
            return self.returncode

    monkeypatch.setattr("scripts.check_windows_runtime_startup.subprocess.Popen", Process)
    result = probe.run_variant(probe.VARIANTS[0], EXE, BASE, tmp_path / "child")
    assert result["timed_out"] is timed_out
    assert result["startup_verified"] is (not timed_out)
    assert result["reaped"] is True and result["child_started"] is True
    assert waits == ([15, 5] if timed_out else [15])
    assert processes[0].killed is timed_out
    assert "private-output" not in json.dumps(result) and "private-error" not in json.dumps(result)


def test_unconfirmed_child_cleanup_stops_remaining_variants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def unresolved(variant: probe.Variant, *args: Any) -> dict[str, Any]:
        calls.append(variant.name)
        return {
            "variant": variant.name,
            "child_started": True,
            "reaped": False,
            "startup_verified": False,
        }

    monkeypatch.setattr(probe, "run_variant", unresolved)
    report: dict[str, Any] = {"results": []}
    probe.run_matrix(report, EXE, BASE, tmp_path)
    assert calls == [probe.VARIANTS[0].name]
    assert report["diagnosis_complete"] is False
    assert report["failure_class"] == "ChildCleanupUnconfirmed"
    assert len(report["unattempted_variants"]) == 11
