from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CMD_LAUNCHER = REPO_ROOT / "START_DS60.cmd"
POWERSHELL_LAUNCHER = REPO_ROOT / "scripts" / "start_ds60.ps1"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def powershell_text() -> str:
    return POWERSHELL_LAUNCHER.read_text(encoding="utf-8")


def test_double_click_launcher_is_location_and_space_safe() -> None:
    text = CMD_LAUNCHER.read_text(encoding="utf-8")

    assert 'pushd "%~dp0"' in text
    assert '-File "%~dp0scripts\\start_ds60.ps1"' in text
    assert "-PauseOnError %*" in text
    assert "DS60_EXIT_CODE=%ERRORLEVEL%" in text
    assert "popd" in text


def test_startup_supports_both_windows_environment_layouts() -> None:
    text = powershell_text()

    standard = '$StandardVenvPython = Join-Path $RepoRoot ".venv\\Scripts\\python.exe"'
    conda = '$CondaPrefixPython = Join-Path $RepoRoot ".venv\\python.exe"'
    assert standard in text
    assert conda in text
    assert text.index(standard) < text.index(conda)
    assert "Get-CoursePython" in text
    assert "Python 3.11-3.12" in text
    assert 'get_kernel_spec("ds60sqlpy")' in text


def test_startup_bootstraps_only_when_setup_or_repair_is_needed() -> None:
    text = powershell_text()

    assert "$BootstrapRequested = (" in text
    assert "$NeedsBootstrap = $BootstrapRequested -or -not $StackReady" in text
    assert "CONNECTED FIRST SETUP" in text
    assert "Type SETUP to continue" in text
    assert "-AcceptConnectedSetup" in text
    assert "Connected setup is required, but this run is noninteractive." in text
    assert "Invoke-Bootstrap" in text
    assert "Existing course environment is ready" in text


def test_startup_runs_readiness_doctor_and_private_portal() -> None:
    text = powershell_text()

    for module in (
        "IPython",
        "ipykernel",
        "jupyterlab",
        "notebook",
        "psycopg",
        "sql",
        "sqlalchemy",
    ):
        assert f"import {module}" in text

    assert '@("scripts\\course.py", "doctor")' in text
    assert "$PortalScript = Join-Path $PSScriptRoot" in text
    assert '"--no-browser"' in text
    assert '"--no-launches"' in text
    assert "private 127.0.0.1 learning portal" in text


def test_startup_rediscovers_psql_without_persisted_path() -> None:
    text = powershell_text()

    assert "Get-CoursePsql" in text
    assert r"HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\psql.exe" in text
    assert r"HKLM:\SOFTWARE\PostgreSQL\Installations\*" in text
    assert r'"bin\psql.exe"' in text
    assert "[int]$Matches.major -ge 16" in text
    assert "Add-ProcessToolDirectory -ExecutablePath $PsqlPath" in text
    assert "-SkipPostgreSql for an intentional Python-only start" in text
    assert "PostgreSQL 16+ client tools are required for full-course readiness" in text


def test_startup_discovers_visual_studio_code_outside_path() -> None:
    text = powershell_text()

    assert "Get-CourseVsCode" in text
    assert r'"Programs\Microsoft VS Code\Code.exe"' in text
    assert r'"Microsoft VS Code\bin\code.cmd"' in text
    assert "Add-ProcessToolDirectory -ExecutablePath $VsCodePath" in text
    assert "the browser and Jupyter actions can still work" in text


def test_diagnostics_and_whatif_do_not_start_or_install() -> None:
    text = powershell_text()

    diagnostics = text.index("if ($DiagnosticsOnly) {")
    diagnostics_return = text.index("return 1", diagnostics)
    needs_bootstrap = text.index("$NeedsBootstrap =", diagnostics_return)
    portal_start = text.index('Write-Step "Starting the private learning portal"')

    assert diagnostics < diagnostics_return < needs_bootstrap < portal_start
    assert "[CmdletBinding(SupportsShouldProcess = $true" in text
    assert "$WhatIfPreference" in text
    assert '$Parameters["WhatIf"] = $true' in text
    assert "Dry run complete; the portal was not started." in text


def test_startup_never_handles_credentials_or_resets_data() -> None:
    text = powershell_text()
    forbidden = (
        "00_setup.sql",
        "CREATE DATABASE",
        "DROP DATABASE",
        "DROP SCHEMA",
        "ALTER ROLE",
        "PGPASSWORD",
        "DS60_DATABASE_URL=",
        "psycopg.connect",
        "create_engine(",
    )

    for fragment in forbidden:
        assert fragment.lower() not in text.lower()

    assert (
        re.search(
            r"(?im)^\s*\$env:(?:PGPASSWORD|DS60_DATABASE_URL)\s*=",
            text,
        )
        is None
    )


def test_startup_uses_only_windows_powershell_51_syntax_markers() -> None:
    text = powershell_text()

    assert text.startswith("#Requires -Version 5.1")
    assert "Set-StrictMode -Version Latest" in text
    assert "$IsWindows" not in text
    assert "ForEach-Object -Parallel" not in text
    assert "ConvertFrom-Json -AsHashtable" not in text
    assert "??" not in text
    assert "?." not in text


def test_ci_executes_native_windows_startup_diagnostics() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "Exercise guided Windows startup diagnostics" in text
    assert r".\scripts\start_ds60.ps1 `" in text
    assert "-DiagnosticsOnly -NonInteractive -SkipPostgreSql" in text


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is not installed")
def test_powershell_parser_accepts_startup_script() -> None:
    parser_command = (
        "$tokens = $null; $errors = $null; "
        "[System.Management.Automation.Language.Parser]::ParseFile("
        "(Resolve-Path $args[0]), [ref]$tokens, [ref]$errors) | Out-Null; "
        "if ($errors.Count -gt 0) { "
        "$errors | ForEach-Object { Write-Error $_.Message }; exit 1 }"
    )
    result = subprocess.run(
        [
            shutil.which("pwsh") or "pwsh",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            parser_command,
            str(POWERSHELL_LAUNCHER),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
