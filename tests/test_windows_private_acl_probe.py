"""Phase-safe diagnostics preserve native ACL execution and conceal account data."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts.check_windows_private_acl import instrument_script, observed_phases


def test_native_diagnostics_extract_only_known_fixed_phases() -> None:
    output = (
        "synthetic-account-name\nDS60-ACL-PHASE:startup\nprivate-path-value\n"
        "DS60-ACL-PHASE:read-acl\nDS60-ACL-PHASE:untrusted-value\n"
    )
    assert observed_phases(output) == ["startup", "read-acl"]
    assert observed_phases(output.encode()) == ["startup", "read-acl"]
    assert observed_phases(None) == []


def test_native_phase_instrumentation_preserves_original_statements() -> None:
    source = (
        "\n$sid=identify\nif($env:DS60_PRIVATE_ESTABLISH) {\n  Set-Acl fixture\n}\n$observed=read\n"
    )
    instrumented = instrument_script(source)
    original = "\n".join(
        line
        for line in instrumented.splitlines()
        if not line.startswith("Write-Output 'DS60-ACL-PHASE:")
    )
    assert original == source.rstrip("\n")
    assert instrumented.index("PHASE:identity") < instrumented.index("$sid=identify")
    assert instrumented.index("PHASE:read-acl") < instrumented.index("$observed=read")


def test_runtime_startup_failure_never_claims_or_attempts_acl_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_windows_private_acl as probe

    monkeypatch.setattr(
        "ds60sqlpy.kubernetes_module._windows_powershell_runtime",
        lambda: ("fixed-powershell", {"TEMP": "synthetic-temp"}),
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda argv, **kwargs: subprocess.CompletedProcess(argv, 1, b"", b"private-detail"),
    )

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("ACL verification must not start after failed runtime startup")

    monkeypatch.setattr("ds60sqlpy.kubernetes_module._windows_private_acl", forbidden)
    report: dict[str, Any] = {"checks": [], "commands": []}
    with pytest.raises(RuntimeError, match="powershell-runtime-startup"):
        probe.native_acl_smoke(report, tmp_path)
    assert report["checks"] == []
    assert report["commands"][0]["operation"] == "runtime-startup"
    assert "private-detail" not in json.dumps(report)


def test_runtime_startup_success_is_not_sufficient_for_acl_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_windows_private_acl as probe

    monkeypatch.setattr(
        "ds60sqlpy.kubernetes_module._windows_powershell_runtime",
        lambda: ("fixed-powershell", {}),
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda argv, **kwargs: subprocess.CompletedProcess(
            argv, 0, b"DS60-ACL-PHASE:startup\r\n", b""
        ),
    )
    monkeypatch.setattr(
        "ds60sqlpy.kubernetes_module._windows_private_acl", lambda *args, **kwargs: False
    )
    report: dict[str, Any] = {"checks": [], "commands": []}
    with pytest.raises(RuntimeError, match="establish-private-directory"):
        probe.native_acl_smoke(report, tmp_path)
    assert len(report["checks"]) == 1
    assert "PowerShell runtime" in report["checks"][0]
