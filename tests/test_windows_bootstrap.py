from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "bootstrap_windows.ps1"
GUIDE = REPO_ROOT / "docs" / "setup" / "windows-bootstrap.md"
VSCODE_TASKS = REPO_ROOT / ".vscode" / "tasks.json"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_bootstrap_has_explicit_mutation_boundaries() -> None:
    text = script_text()

    assert "$PersistUserPath" in text
    assert "SupportsShouldProcess = $true" in text
    assert "$WhatIfPreference" in text
    assert "[System.EnvironmentVariableTarget]::Process" in text
    assert "[System.EnvironmentVariableTarget]::User" in text
    assert "[System.EnvironmentVariableTarget]::Machine" not in text
    assert re.search(r"\bsetx(?:\.exe)?\b", text, flags=re.IGNORECASE) is None

    assert "$InstallMissingWithWinget" in text
    assert "Python.Python.3.12" in text
    assert "PostgreSQL.PostgreSQL.17" in text
    assert '$PSCmdlet.ShouldProcess("astral-sh.uv", "Install with winget")' in text

    # Selected executables must precede stale PATH copies without discarding
    # unrelated entries.
    assert text.index("$RequestedParts =") < text.index("$CurrentParts =")
    assert "Prioritized on $Target PATH" in text


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

    psql_invocations = re.findall(
        r"Invoke-Native -FilePath \$PsqlInfo\.Path -ArgumentList @\((.*?)\)",
        text,
    )
    assert psql_invocations == ['"--version"']
    assert "psycopg.connect" not in text
    assert "create_engine(" not in text
    assert "Invoke-Sqlcmd" not in text
    assert (
        re.search(
            r"(?im)^\s*\$env:(?:PGPASSWORD|DS60_DATABASE_URL)\s*=",
            text,
        )
        is None
    )
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
    assert '$CondaPrefixPython = Join-Path $VenvDirectory "python.exe"' in text
    assert "Find-UsableConda" in text
    assert '"create", "--yes", "--no-default-packages"' in text
    assert '"--prefix", $VenvDirectory, "python=3.12", "pip"' in text
    assert "$VenvPython = $CondaPrefixPython" in text
    assert "$ReadyVenvInfo = Get-PythonInfo -Path $VenvPython" in text
    assert 'Join-Path $VenvDirectory "Library\\bin"' in text


def test_bootstrap_reuses_both_windows_environment_layouts() -> None:
    text = script_text()

    standard_check = "Test-Path -LiteralPath $StandardVenvPython -PathType Leaf"
    conda_check = "Test-Path -LiteralPath $CondaPrefixPython -PathType Leaf"
    assert standard_check in text
    assert conda_check in text
    assert text.index(standard_check) < text.index("$PythonInfo = Find-SupportedPython")
    assert re.search(
        r"\$PythonInfo = \$null\s+"
        r"if \(-not \$ExistingVenvInfo\) {\s+"
        r"\$PythonInfo = Find-SupportedPython",
        text,
    )
    assert "It was not deleted automatically." in text


def test_whatif_exits_before_path_environment_or_package_mutation() -> None:
    text = script_text()

    dry_run = text.index('if ($DryRun) {\n    Write-Step "Dry-run plan"')
    dry_return = text.index("    return", dry_run)
    path_mutation = text.index('Write-Step "Preparing this PowerShell process PATH"')
    environment_mutation = text.index(
        'Write-Step "Creating or reusing the repository virtual environment"'
    )
    package_mutation = text.index('Write-Step "Installing the $Profile dependency profile"')

    assert dry_run < dry_return < path_mutation
    assert dry_return < environment_mutation
    assert dry_return < package_mutation
    assert "What if: conda would create a Python 3.12 environment" in text
    assert "Dry run complete; no PATH, environment, package, kernel" in text


def test_locked_and_project_modes_target_the_selected_environment() -> None:
    text = script_text()

    assert '$ResolvedDependencyMode -eq "Locked"' in text
    assert '@("sync", "--locked", "--python", $VenvPython)' in text
    assert '"UV_PROJECT_ENVIRONMENT"' in text
    assert "$VenvDirectory," in text
    assert '"-m", "ensurepip", "--upgrade"' in text
    assert '"install", "-e", $ExtraSpec' in text
    assert "Locked mode requires uv" in text


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
    assert 'Write-Host "  & `"$VenvPython`" -m jupyter lab"' in text


def test_vscode_tasks_use_the_selected_cross_platform_interpreter() -> None:
    task_data = json.loads(VSCODE_TASKS.read_text(encoding="utf-8"))
    python_tasks = [task for task in task_data["tasks"] if task["label"] != "Course: Setup"]

    assert python_tasks
    assert all(task["command"] == "${command:python.interpreterPath}" for task in python_tasks)
    assert all("windows" not in task for task in python_tasks)


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
    assert r".venv\Scripts\python.exe" in text
    assert r".venv\python.exe" in text
    assert "$CoursePython" in text
    assert "[PostgreSQL in Jupyter](jupyter-postgresql.md)" in text


def test_script_uses_only_windows_powershell_51_syntax_markers() -> None:
    text = script_text()

    assert text.startswith("#Requires -Version 5.1")
    assert "Set-StrictMode -Version Latest" in text
    assert "$IsWindows" not in text
    assert "ForEach-Object -Parallel" not in text
    assert "ConvertFrom-Json -AsHashtable" not in text
    assert "??" not in text
    assert "?." not in text


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
