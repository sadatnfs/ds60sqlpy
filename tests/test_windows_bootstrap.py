from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "bootstrap_windows.ps1"
GUIDE = REPO_ROOT / "docs" / "setup" / "windows-bootstrap.md"
VSCODE_TASKS = REPO_ROOT / ".vscode" / "tasks.json"
SETUP_SCRIPT = REPO_ROOT / "scripts" / "setup.ps1"


def powershell_parser() -> str | None:
    if os.name == "nt":
        system_root = Path(os.environ.get("SYSTEMROOT", r"C:\Windows"))
        windows_powershell = (
            system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        )
        if windows_powershell.is_file():
            return str(windows_powershell)
    return shutil.which("pwsh")


POWERSHELL_PARSER = powershell_parser()


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


def test_discovery_helpers_accept_initially_empty_mutable_lists() -> None:
    text = script_text()

    for parameter_name in ("Candidates", "Directories"):
        assert re.search(
            rf"\[AllowEmptyCollection\(\)\]\s+"
            rf"\[System\.Collections\.Generic\.List\[string\]\]\${parameter_name}",
            text,
        )
    assert re.search(
        r"\[AllowEmptyCollection\(\)\]\s+\[string\[\]\]\$Entries",
        text,
    )


def test_command_discovery_handles_multiple_path_matches() -> None:
    text = script_text()
    python_lookup_start = text.index('foreach ($Name in @("python", "python3"))')
    python_lookup_end = text.index(
        "# Ask every discoverable conda installation",
        python_lookup_start,
    )
    python_lookup = text[python_lookup_start:python_lookup_end]
    setup = SETUP_SCRIPT.read_text(encoding="utf-8")

    assert "$Command = Get-Command $Name" not in python_lookup
    assert "$Command in @(" in python_lookup
    assert "-Path $Command.Source" in python_lookup
    assert "$PythonCommands = @(" in setup
    assert "foreach ($Python in $PythonCommands)" in setup
    assert "Invoke-Native -FilePath $PythonPath" in setup


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
    assert '"scripts\\course.py", "doctor", "--no-database"' in text
    assert '"kernelspec", "list", "--json"' in text
    assert 'Write-Host "  & `"$VenvPython`" -m jupyter lab"' in text


def test_vscode_tasks_use_the_selected_cross_platform_interpreter() -> None:
    task_data = json.loads(VSCODE_TASKS.read_text(encoding="utf-8"))
    non_python_tasks = {"Course: Setup", "Course: Guided start (Windows)"}
    python_tasks = [task for task in task_data["tasks"] if task["label"] not in non_python_tasks]

    assert python_tasks
    assert all(task["command"] == "${command:python.interpreterPath}" for task in python_tasks)
    assert all("windows" not in task for task in python_tasks)

    guided = next(
        task for task in task_data["tasks"] if task["label"] == "Course: Guided start (Windows)"
    )
    assert guided["command"] == "powershell.exe"
    assert r"${workspaceFolder}\scripts\start_ds60.ps1" in guided["args"]


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


def test_python_probes_avoid_legacy_native_quote_serialization() -> None:
    text = script_text()

    assert "function Invoke-PythonSource" in text
    assert "[IO.File]::WriteAllText(" in text
    assert '@("-c", $Probe)' not in text
    assert '@("-c", $ImportProbe)' not in text
    assert "Remove-Item -LiteralPath $ProbePath" in text
    assert '$ErrorActionPreference = "Continue"' in text
    assert "2> $ErrorPath" in text


@pytest.mark.skipif(POWERSHELL_PARSER is None, reason="PowerShell is not installed")
def test_powershell_parser_accepts_bootstrap_script() -> None:
    parser_command = (
        "$tokens = $null; $errors = $null; "
        "[System.Management.Automation.Language.Parser]::ParseFile("
        "$env:DS60_SCRIPT_TO_PARSE, [ref]$tokens, [ref]$errors) | Out-Null; "
        "if ($errors.Count -gt 0) { "
        "$errors | ForEach-Object { Write-Error $_.Message }; exit 1 }"
    )
    result = subprocess.run(
        [
            POWERSHELL_PARSER or "pwsh",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            parser_command,
        ],
        check=False,
        capture_output=True,
        env={**os.environ, "DS60_SCRIPT_TO_PARSE": str(SCRIPT)},
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
