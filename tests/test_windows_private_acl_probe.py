"""Phase-safe diagnostics preserve native ACL execution and conceal account data."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy import kubernetes_module
from scripts.check_windows_private_acl import FAILURE_STAGES, instrument_script, observed_phases


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
        "\n$sid=identify\nif($env:DS60_PRIVATE_ESTABLISH) {\n"
        "  [System.IO.Directory]::SetAccessControl($p,$acl)\n}\n"
        "if([System.IO.Directory]::Exists($p)) {\n  $observed=read\n}\n"
    )
    instrumented = instrument_script(source)
    original = "\n".join(
        line
        for line in instrumented.splitlines()
        if not line.startswith("[Console]::Out.WriteLine('DS60-ACL-PHASE:")
    )
    assert original == source.rstrip("\n")
    assert "Write-Output" not in instrumented
    assert "[Console]::Out.Flush()" in instrumented
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


@pytest.mark.parametrize("stage", [*sorted(FAILURE_STAGES), "unexpected private runtime detail"])
def test_public_report_allows_only_controlled_runtime_failure_stages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stage: str,
) -> None:
    from scripts import check_windows_private_acl as probe

    # Simulate the probe's Windows eligibility without changing pathlib's host
    # behavior or invoking any native ACL command.
    monkeypatch.setattr(
        probe, "os", SimpleNamespace(name="nt", environ={"RUNNER_TEMP": str(tmp_path)})
    )

    def fail(report: dict[str, Any], directory: Path) -> None:
        raise RuntimeError(stage)

    monkeypatch.setattr(probe, "native_acl_smoke", fail)
    destination = tmp_path / "report.json"
    assert probe.main(["--report", str(destination)]) == 1
    text = destination.read_text(encoding="utf-8")
    report = json.loads(text)
    assert report["passed"] is False and report["failure_type"] == "RuntimeError"
    assert report["checks"] == [] and report["commands"] == []
    if stage in FAILURE_STAGES:
        assert report["failure_stage"] == stage
    else:
        assert "failure_stage" not in report and stage not in text
        captured = capsys.readouterr()
        assert stage not in captured.out and stage not in captured.err


@pytest.mark.parametrize(
    ("rejection_code", "expected_stage"),
    [
        (3, None),
        (2, "broad-file-acl-rejection-unverified"),
        (None, "broad-file-acl-rejection-unverified"),
    ],
)
def test_native_negative_case_requires_confirmed_broad_rule_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rejection_code: int | None,
    expected_stage: str | None,
) -> None:
    from scripts import check_windows_private_acl as probe

    report: dict[str, Any] = {"checks": [], "commands": []}
    monkeypatch.setattr(
        kubernetes_module, "_windows_powershell_runtime", lambda: ("fixed-powershell", {})
    )

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        if "DS60_PRIVATE_PATH" in kwargs["env"]:
            parent = Path(kwargs["env"]["DS60_PRIVATE_PATH"])
            assert parent.is_dir()
            # The child must be created after the parent receives its inheritable
            # rule, so the native test exercises inheritance rather than a broad
            # ACE installed directly on the child.
            assert not list(parent.iterdir())
            assert "New-Object" not in argv[-1] and "Set-Acl" not in argv[-1]
        return subprocess.CompletedProcess(argv, 0, b"DS60-ACL-PHASE:startup\n", b"")

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(kubernetes_module, "_windows_private_acl", lambda *a, **k: True)

    def private_file(path: Path, maximum: int) -> bytes:
        if path.parent == tmp_path:
            return path.read_bytes()
        assert path.parent.name == "synthetic-broad-parent" and path.exists()
        report["commands"].append(
            {"returncode": rejection_code, "timed_out": rejection_code is None}
        )
        raise kubernetes_module.KubernetesRefusal("synthetic refusal")

    monkeypatch.setattr(kubernetes_module, "_private_file", private_file)
    if expected_stage is None:
        probe.native_acl_smoke(report, tmp_path)
        assert len(report["checks"]) == 4
        assert "Inherited broad file ACL refused" in report["checks"][-1]
    else:
        with pytest.raises(RuntimeError, match=expected_stage):
            probe.native_acl_smoke(report, tmp_path)
        assert len(report["checks"]) == 3
