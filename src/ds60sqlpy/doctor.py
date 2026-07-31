"""Cross-platform environment diagnostics for learners."""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Literal

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.sql_notebook import (
    SqlNotebookError,
    course_psql_environment,
    validate_course_database_target,
)
from ds60sqlpy.sql_runner import DEFAULT_DATABASE_URL

Status = Literal["pass", "warn", "fail"]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One environment diagnostic."""

    status: Status
    name: str
    detail: str


def _version(command: list[str], timeout: float = 4.0) -> str | None:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0] if result.returncode == 0 and output else None


def _course_database_diagnostic(psql: str) -> Diagnostic:
    """Check the disposable course database without prompting or changing it."""

    database_url = os.environ.get("DS60_DATABASE_URL") or DEFAULT_DATABASE_URL
    try:
        database_target = validate_course_database_target(database_url)
    except SqlNotebookError:
        return Diagnostic(
            "warn",
            "Course database",
            "connection setting is not the disposable advanced_sql_training database; "
            "the database was not contacted",
        )
    environment = course_psql_environment(
        database_target,
        application_name="ds60sqlpy-doctor",
        connect_timeout=5,
    )
    try:
        result = subprocess.run(
            [
                psql,
                "-X",
                "-w",
                "-v",
                "ON_ERROR_STOP=1",
                "--tuples-only",
                "--no-align",
                "--command",
                "SELECT current_database();",
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            env=environment,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result and result.returncode == 0 and result.stdout.strip() == "advanced_sql_training":
        return Diagnostic(
            "pass",
            "Course database",
            "advanced_sql_training is reachable",
        )
    return Diagnostic(
        "warn",
        "Course database",
        "not reachable without prompting; complete the SQL setup guide before SQL lessons",
    )


def diagnose(
    catalog: Catalog,
    *,
    check_database: bool = True,
) -> tuple[Diagnostic, ...]:
    """Inspect the local machine without changing it.

    ``check_database=False`` keeps setup/bootstrap diagnostics entirely local.
    The default performs one bounded, read-only reachability query, but only
    when the configured target is the disposable course database.
    """

    diagnostics: list[Diagnostic] = []
    current = sys.version_info[:2]
    if current < (3, 11):
        diagnostics.append(
            Diagnostic(
                "fail",
                "Python",
                f"{platform.python_version()} found; Python 3.11+ required",
            )
        )
    elif current == (3, 12):
        diagnostics.append(
            Diagnostic("pass", "Python", f"{platform.python_version()} (recommended baseline)")
        )
    elif current >= (3, 13):
        diagnostics.append(
            Diagnostic(
                "fail",
                "Python",
                f"{platform.python_version()} can inspect the repository, but the supported "
                "course environment is Python 3.11-3.12",
            )
        )
    else:
        diagnostics.append(Diagnostic("pass", "Python", platform.python_version()))

    in_virtual_environment = sys.prefix != sys.base_prefix
    diagnostics.append(
        Diagnostic(
            "pass" if in_virtual_environment else "warn",
            "Virtual environment",
            (
                f"active ({sys.prefix})"
                if in_virtual_environment
                else "not active; use the repository .venv interpreter"
            ),
        )
    )

    diagnostics.append(Diagnostic("pass", "Repository", str(catalog.repo_root)))
    for executable in ("git", "docker", "psql", "code"):
        path = shutil.which(executable)
        if path is None:
            status: Status = "warn" if executable in {"docker", "psql", "code"} else "fail"
            diagnostics.append(Diagnostic(status, executable, "not found on PATH"))
            continue
        version = _version([executable, "--version"])
        diagnostics.append(Diagnostic("pass", executable, version or path))

    psql = shutil.which("psql")
    if psql and check_database:
        diagnostics.append(_course_database_diagnostic(psql))

    if shutil.which("docker"):
        server = _version(["docker", "info", "--format", "{{.ServerVersion}}"])
        diagnostics.append(
            Diagnostic(
                "pass" if server else "warn",
                "Docker daemon",
                f"running ({server})" if server else "CLI found, daemon not reachable",
            )
        )

    core_imports = (
        "IPython",
        "ipykernel",
        "jupyterlab",
        "notebook",
        "numpy",
        "pandas",
        "sklearn",
        "matplotlib",
        "seaborn",
        "sql",
        "sqlalchemy",
        "psycopg",
    )
    for module in core_imports:
        available = importlib.util.find_spec(module) is not None
        diagnostics.append(
            Diagnostic(
                "pass" if available else "warn",
                f"Python package: {module}",
                "available" if available else "not installed (run a setup script)",
            )
        )

    catalog_file = catalog.repo_root / "curriculum" / "catalog.json"
    diagnostics.append(
        Diagnostic(
            "pass" if catalog_file.is_file() else "fail",
            "Course catalog",
            str(catalog_file.relative_to(catalog.repo_root)),
        )
    )
    return tuple(diagnostics)
