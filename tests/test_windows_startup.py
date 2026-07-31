from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CMD_LAUNCHER = REPO_ROOT / "START_DS60.cmd"
POWERSHELL_LAUNCHER = REPO_ROOT / "scripts" / "start_ds60.ps1"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
README = REPO_ROOT / "README.md"
OFFLINE_GUIDE = REPO_ROOT / "docs" / "setup" / "offline.md"
WINDOWS_GUIDE = REPO_ROOT / "docs" / "setup" / "windows.md"
GUIDED_SQL_GUIDE = REPO_ROOT / "docs" / "guided-sql-notebooks.md"
PORTAL_GUIDE = REPO_ROOT / "docs" / "learning-portal.md"
MACOS_GUIDE = REPO_ROOT / "docs" / "setup" / "macos.md"
LINUX_GUIDE = REPO_ROOT / "docs" / "setup" / "linux.md"
DEPENDENCY_PROFILES = REPO_ROOT / "docs" / "dependency-profiles.md"
CURRICULUM_MAP = REPO_ROOT / "docs" / "curriculum-map.md"
VALIDATION_GUIDE = REPO_ROOT / "docs" / "validation.md"
PROFESSIONAL_PATHS = REPO_ROOT / "docs" / "professional-paths.md"
CONTENT_AUTHORING = REPO_ROOT / "docs" / "content-authoring.md"
TROUBLESHOOTING = REPO_ROOT / "docs" / "troubleshooting.md"
JUPYSQL_GUIDE = (
    REPO_ROOT
    / "bridge"
    / "professional"
    / "companion-guides"
    / "bridge_jupyter_01_postgresql_magics.md"
)


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
    startup_step = text.split(
        "- name: Exercise guided Windows startup diagnostics",
        maxsplit=1,
    )[1].split("- name: Offline notebook smoke execution", maxsplit=1)[0]
    bootstrap_step = text.split(
        "- name: Exercise the Windows discovery bootstrap",
        maxsplit=1,
    )[1].split("- name: Run the Windows learner setup", maxsplit=1)[0]

    assert "Exercise guided Windows startup diagnostics" in text
    assert "powershell.exe -NoProfile -ExecutionPolicy Bypass" in startup_step
    assert r"-File .\scripts\start_ds60.ps1 `" in startup_step
    assert "-DiagnosticsOnly -NonInteractive -SkipPostgreSql" in startup_step
    assert "powershell.exe -NoProfile -ExecutionPolicy Bypass" in bootstrap_step
    assert r"-File .\scripts\bootstrap_windows.ps1" in bootstrap_step
    assert "-SkipPostgreSql -WhatIf" in bootstrap_step


def test_windows_commands_document_both_repository_environment_layouts() -> None:
    documents = (
        DEPENDENCY_PROFILES,
        CURRICULUM_MAP,
        VALIDATION_GUIDE,
        PROFESSIONAL_PATHS,
        CONTENT_AUTHORING,
        TROUBLESHOOTING,
        JUPYSQL_GUIDE,
    )

    for document in documents:
        text = document.read_text(encoding="utf-8")
        assert r"Test-Path .\.venv\Scripts\python.exe" in text, document
        assert r"Resolve-Path .\.venv\python.exe" in text, document
        assert "$CoursePython" in text, document
        assert (
            re.search(
                r"(?m)^\s*\.\\\.venv\\Scripts\\python\.exe(?:\s|$)",
                text,
            )
            is None
        ), document


def test_advanced_windows_docs_use_discovery_bootstrap() -> None:
    for document in (DEPENDENCY_PROFILES, JUPYSQL_GUIDE):
        text = document.read_text(encoding="utf-8")
        assert r"& .\scripts\bootstrap_windows.ps1 -Profile Advanced" in text
        assert "setup.ps1 -Advanced" not in text


def test_windows_troubleshooting_discovers_before_install_advice() -> None:
    text = TROUBLESHOOTING.read_text(encoding="utf-8")
    section = text.split("## `python` or `py` is not found", maxsplit=1)[1].split(
        "## Virtual environment creation fails",
        maxsplit=1,
    )[0]

    assert section.index("bootstrap_windows.ps1 -SkipPostgreSql -WhatIf") < section.index(
        "install Python 3.12"
    )


def test_beginner_sql_start_uses_day_one_before_foundation_milestones() -> None:
    text = README.read_text(encoding="utf-8")
    sql_start = text.index("\nSQL:\n")
    sql_end = text.index("\nPython + PostgreSQL engineering bridge:", sql_start)
    sql_steps = text[sql_start:sql_end]

    assert "Open [SQL Day 1](lesson-pages/sql-01.html)" in sql_steps
    assert "**Create/open guided SQL notebook**" in sql_steps
    assert ".learning/sql/sql-01/" in sql_steps
    assert sql_steps.index("Open [SQL Day 1]") < sql_steps.index("between Days 15 and 16")
    assert sql_steps.index("between Days 15 and 16") < sql_steps.index("between Days 39 and 40")


def test_offline_windows_path_supports_both_repository_environment_layouts() -> None:
    text = OFFLINE_GUIDE.read_text(encoding="utf-8")

    assert r"& .\scripts\bootstrap_windows.ps1" in text
    assert r".venv\Scripts\python.exe" in text
    assert r".venv\python.exe" in text
    assert "$CoursePython" in text
    assert r"scripts\setup.ps1" not in text
    assert "Windows `Core` bootstrap or macOS/Linux advanced setup" in text


def test_posix_setup_guides_offer_the_private_portal_and_explain_static_mode() -> None:
    for guide in (MACOS_GUIDE, LINUX_GUIDE):
        text = guide.read_text(encoding="utf-8")
        assert ".venv/bin/python scripts/learning_portal.py" in text
        assert "read-only course navigator" in text
        assert "**Create/open guided SQL notebook**" in text
        assert ".learning/sql/sql-01/" in text


def test_setup_guides_have_a_copy_ready_clone_command() -> None:
    clone = "git clone https://github.com/sadatnfs/ds60sqlpy.git ds60sqlpy"

    for guide in (WINDOWS_GUIDE, MACOS_GUIDE, LINUX_GUIDE):
        text = guide.read_text(encoding="utf-8")
        assert clone in text
        assert "git clone <repository-url>" not in text


def test_native_windows_guided_sql_authentication_is_explicit_and_secret_free() -> None:
    windows = WINDOWS_GUIDE.read_text(encoding="utf-8")
    guided = GUIDED_SQL_GUIDE.read_text(encoding="utf-8")
    portal = PORTAL_GUIDE.read_text(encoding="utf-8")

    assert "Let the guided notebook authenticate without a hidden prompt" in windows
    assert r'Join-Path $env:APPDATA "postgresql"' in windows
    assert "pgpass.conf" in windows
    assert (
        '$env:DS60_DATABASE_URL = "postgresql://postgres@localhost:5432/advanced_sql_training"'
    ) in windows
    assert "YOUR_LOCAL_POSTGRES_PASSWORD" in windows
    assert "Never copy, commit, paste into Codex, or share it." in windows
    assert "same PowerShell window" in windows

    assert "authenticate-without-a-hidden-prompt" in guided
    assert "password-free local `DS60_DATABASE_URL`" in guided
    posix_start = guided.split("## macOS and Linux path", maxsplit=1)[1].split(
        "## Generate without the portal",
        maxsplit=1,
    )[0]
    assert "bash scripts/setup.sh\n" in posix_start
    assert "scripts/setup.sh --advanced" not in posix_start
    assert "Use `--advanced` only for the separate JupySQL" in " ".join(posix_start.split())
    assert "password-file handoff" in portal
    assert "portal never" in portal
    assert "asks for or stores a database password" in portal


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is not installed")
def test_powershell_parser_accepts_startup_script() -> None:
    parser_command = (
        "$tokens = $null; $errors = $null; "
        "[System.Management.Automation.Language.Parser]::ParseFile("
        "$env:DS60_SCRIPT_TO_PARSE, [ref]$tokens, [ref]$errors) | Out-Null; "
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
        ],
        check=False,
        capture_output=True,
        env={**os.environ, "DS60_SCRIPT_TO_PARSE": str(POWERSHELL_LAUNCHER)},
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
