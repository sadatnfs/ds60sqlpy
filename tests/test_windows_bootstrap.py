from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "bootstrap_windows.ps1"
GUIDE = REPO_ROOT / "docs" / "setup" / "windows-bootstrap.md"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_bootstrap_has_explicit_mutation_boundaries() -> None:
    text = script_text()

    assert '$PersistUserPath' in text
    assert "SupportsShouldProcess = $true" in text
    assert "$WhatIfPreference" in text
    assert '[System.EnvironmentVariableTarget]::Process' in text
    assert '[System.EnvironmentVariableTarget]::User' in text
    assert '[System.EnvironmentVariableTarget]::Machine' not in text
    assert re.search(r"\bsetx(?:\.exe)?\b", text, flags=re.IGNORECASE) is None

    assert '$InstallMissingWithWinget' in text
    assert 'Python.Python.3.12' in text
    assert 'PostgreSQL.PostgreSQL.17' in text


def test_bootstrap_never_operates_on_a_database_or_handles_credentials() -> None:
    text = script_text()
    forbidden = (
        "00_setup.sql",
        "CREATE DATABASE",
        "DROP DATABASE",
        "DROP SCHEMA",
        "ALTER ROLE",
        "PGPASSWORD",
        "DS60_DATABASE_URL=",
    )

    for fragment in forbidden:
        assert fragment.lower() not in text.lower()

    assert '-ArgumentList @("--version")' in text
    assert "No database was contacted or modified" in text


def test_bootstrap_discovers_anaconda_and_postgresql_without_path() -> None:
    text = script_text()

    expected_discovery_markers = (
        r"HKCU:\Software\Python\PythonCore",
        r"HKCU:\Software\Python\ContinuumAnalytics",
        r"HKLM:\SOFTWARE\PostgreSQL\Installations",
        r"Programs\Python\Python312\python.exe",
        r"anaconda3\python.exe",
        r"Scripts\conda.exe",
        r"PostgreSQL.PostgreSQL.17",
        r"bin\psql.exe",
    )
    for marker in expected_discovery_markers:
        assert marker in text

    assert "3.11-3.12" in text
    assert "Major -ge 16" in text


def test_bootstrap_installs_both_profiles_and_verifies_notebook_stack() -> None:
    text = script_text()

    for extra in (
        "notebooks",
        "data",
        "quality",
        "bridge",
        "professional",
        "sql-notebooks",
        "ml",
        "production",
        "deep-learning",
        "nlp",
        "geo",
    ):
        assert f'"{extra}"' in text

    for distribution in (
        "IPython",
        "jupyterlab",
        "notebook",
        "ipykernel",
        "jupysql",
        "sqlalchemy",
        "psycopg",
    ):
        assert f'"{distribution}"' in text

    assert '"--name", "ds60sqlpy"' in text
    assert '"--display-name", "Python (ds60sqlpy)"' in text
    assert '"scripts\\course.py", "doctor"' in text
    assert '"kernelspec", "list", "--json"' in text


def test_windows_bootstrap_guide_documents_safe_defaults() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    assert r"& .\scripts\bootstrap_windows.ps1" in text
    assert "-PersistUserPath" in text
    assert "-InstallMissingWithWinget" in text
    assert "-Profile Advanced" in text
    assert "-DependencyMode Locked" in text
    assert "-WhatIf" in text
    assert "process-scoped" in text
    assert "does **not** request or display a PostgreSQL password" in text
    assert "never persists an Anaconda or Miniconda root" in text
    assert "[PostgreSQL in Jupyter](jupyter-postgresql.md)" in text


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is not installed")
def test_powershell_parser_accepts_bootstrap_script() -> None:
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
            str(SCRIPT),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
