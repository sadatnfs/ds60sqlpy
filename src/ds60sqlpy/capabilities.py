"""Bounded local backend discovery, distinct from full lesson verification."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Mapping
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import RUNNERS
from ds60sqlpy.execution import (
    ALLOWED_TIMEOUT_SECONDS,
    COURSE_ROLE_QUERY,
    MAX_CODE_BYTES,
    MAX_OUTPUT_BYTES,
)
from ds60sqlpy.runtime_environment import external_dll_directory, external_program_environment
from ds60sqlpy.sql_lesson import lesson_source_policy
from ds60sqlpy.sql_notebook import (
    SqlNotebookError,
    course_psql_environment,
    validate_course_database_target,
)
from ds60sqlpy.sql_runner import default_course_database_url

PROFILE_MODULES: dict[str, tuple[str, ...]] = {
    "core": (),
    "data": (
        "altair",
        "joblib",
        "matplotlib",
        "numpy",
        "pandas",
        "pandera",
        "plotly",
        "requests",
        "sklearn",
        "scipy",
        "seaborn",
        "statsmodels",
    ),
    "bridge": ("psycopg",),
    "professional": ("build", "duckdb", "pyarrow", "hypothesis", "pip", "setuptools", "wheel"),
    "quality": ("pytest", "hypothesis", "mypy", "ruff"),
    "sql-notebooks": ("sql", "sqlalchemy", "pandas", "psycopg"),
    "postgres": ("psycopg",),
    "geo": ("geopandas", "geodatasets", "contextily", "shapely", "networkx"),
    "ml": ("xgboost", "lightgbm", "shap", "lime", "pmdarima", "imblearn", "numba"),
    "production": ("fastapi", "dask", "mlflow", "prefect", "pydantic", "uvicorn"),
    "deep-learning": ("torch", "torchvision"),
    "nlp": ("transformers", "datasets", "evaluate", "spacy", "accelerate"),
}
PROFILE_MODULES["advanced"] = tuple(
    sorted(
        {
            module
            for name in ("geo", "ml", "production", "deep-learning", "nlp")
            for module in PROFILE_MODULES[name]
        }
    )
)

SQL_PREFLIGHT = (
    "COURSE_ROLE_QUERY = "
    + repr(COURSE_ROLE_QUERY)
    + "\n"
    + """
import json
try:
    import psycopg
    with psycopg.connect('',
            options='-c statement_timeout=2000 -c lock_timeout=1000') as connection:
        privileged = connection.execute(COURSE_ROLE_QUERY).fetchone()
        safe = (connection.info.dbname == 'advanced_sql_training'
            and privileged is not None and not privileged[0])
        print(json.dumps({'connected': True, 'limited_role': safe}))
except Exception:
    print(json.dumps({'connected': False, 'limited_role': False}))
"""
)


def _probe(python: str, code: str, environment: Mapping[str, str]) -> dict[str, Any]:
    """Run only a fixed discovery script with closed stdin and a hard deadline."""

    try:
        with external_dll_directory():
            result = subprocess.run(
                [python, "-I", "-c", code],
                env=dict(environment),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=4,
                check=False,
            )
        value = json.loads(result.stdout) if result.returncode == 0 else {}
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {}


def probe_python(python: str | None, modules: tuple[str, ...]) -> dict[str, Any]:
    if python is None:
        return {"available": False, "missing_modules": list(modules)}
    # find_spec on these curated top-level names does not import optional model
    # libraries, load native DLLs, download assets, or run learner source.
    code = (
        "import importlib.util,json,sys\n"
        f"modules={list(modules)!r}\n"
        "missing=[name for name in modules if importlib.util.find_spec(name) is None]\n"
        "print(json.dumps({'available':sys.version_info[:2] in ((3,11),(3,12)),"
        "'python_version':sys.version.split()[0],'missing_modules':missing}))\n"
    )
    return _probe(python, code, external_program_environment())


def probe_sql(python: str | None) -> tuple[bool, str]:
    if python is None:
        return False, "SQL pads need the selected Python backend and its psycopg driver."
    try:
        target = validate_course_database_target(
            os.environ.get("DS60_DATABASE_URL") or default_course_database_url()
        )
        database = course_psql_environment(
            target, application_name="ds60-readiness", connect_timeout=2
        )
    except SqlNotebookError:
        return False, "Select only the local disposable advanced_sql_training database."
    environment = external_program_environment()
    for name in tuple(environment):
        if name.startswith("PG"):
            environment.pop(name)
    environment.update({name: value for name, value in database.items() if name.startswith("PG")})
    result = _probe(python, SQL_PREFLIGHT, environment)
    if not result.get("connected"):
        return False, "The local course database is not reachable with the selected driver/login."
    if not result.get("limited_role"):
        return (
            False,
            "SQL pads require a limited course login, separate from the bootstrap administrator.",
        )
    return True, "The local course database and limited SQL login are ready."


def _setup(group: str) -> str:
    if group not in PROFILE_MODULES:
        return (
            "This custom dependency label has no built-in installer profile. "
            "Follow its authored setup guide; no package or command is installed automatically."
        )
    if group in {"core", "data", "bridge", "professional", "quality", "sql-notebooks", "postgres"}:
        return (
            "Use the normal Core setup with the selected Python interpreter. "
            "For SQL, start the local course database and use its limited login. "
            "See docs/setup/postgresql.md and docs/dependency-profiles.md."
        )
    return (
        f"Install the {group} lesson profile in the selected Python environment. "
        "Native: use Advanced setup or the documented exact optional extra. "
        f"Docker: build with DS60_DOCKER_PROFILES={group}, then restart the lab. "
        "Package installation does not prepare model/data caches or provide a GPU. "
        "See docs/dependency-profiles.md and docs/offline-app.md."
    )


class CapabilityService:
    """Describe implemented backends and optional profiles without installing them."""

    def __init__(self, catalog: Catalog, python: str | None, *, timeout_seconds: int = 15):
        self.catalog = catalog
        self.python = python
        self.timeout_seconds = timeout_seconds

    def runner(self, lesson_id: str, runner_id: str) -> dict[str, Any]:
        lesson = self.catalog.get(lesson_id)
        definition = RUNNERS.get(runner_id)
        if definition is None:
            raise ValueError("Choose a registered lesson runner.")
        primary = runner_id == lesson.runner
        group = lesson.dependency_group if primary else ("bridge" if runner_id == "sql" else "core")
        descriptor: dict[str, Any] = {
            "id": definition.id,
            "title": definition.title,
            "file_suffix": definition.file_suffix,
            "kind": definition.kind,
            "executor": definition.executor,
            "implemented": definition.executor in {"python", "sql"},
            "available": False,
            "can_run": False,
            "profile_ready": True,
            "dependency_group": group,
            "missing_modules": [],
            "reason": "",
            "setup": "",
            "timeout_seconds": self.timeout_seconds,
            "allowed_timeout_seconds": list(ALLOWED_TIMEOUT_SECONDS),
            "max_code_bytes": MAX_CODE_BYTES,
            "max_output_bytes": MAX_OUTPUT_BYTES,
            "network_hint": lesson.network,
            "verification": (
                "Interpreter/package discovery; actual Run verifies code and native imports."
            ),
        }
        if definition.executor is None:
            descriptor.update(
                available=definition.kind == "reading",
                profile_ready=definition.kind == "reading",
                reason=(
                    "Read the lesson and record your reasoning in the guided phases."
                    if definition.kind == "reading"
                    else "Source can be saved here; this execution adapter is not implemented."
                ),
                setup="Follow this lesson's external toolchain or infrastructure instructions.",
            )
            return descriptor
        notebook = definition.executor == "python" and lesson.lesson_path.endswith(".ipynb")
        modules = PROFILE_MODULES.get(group, ())
        if notebook:
            modules = tuple(dict.fromkeys((*modules, "IPython")))
        python = probe_python(self.python, modules)
        missing = python.get("missing_modules", list(modules))
        descriptor.update(
            available=bool(python.get("available")),
            profile_ready=group in PROFILE_MODULES and not missing,
            missing_modules=missing,
            python_version=python.get("python_version"),
        )
        if not descriptor["available"]:
            descriptor["reason"] = "Select a usable Python 3.11 or 3.12 backend with DS60_PYTHON."
            descriptor["setup"] = _setup(group)
            return descriptor
        descriptor["reason"] = "The Python backend is ready. Each Run starts a fresh process."
        if not descriptor["profile_ready"]:
            descriptor["reason"] += " This lesson's optional package profile is incomplete."
            descriptor["setup"] = _setup(group)
        if definition.executor == "sql":
            descriptor["available"], descriptor["reason"] = probe_sql(self.python)
            descriptor.update(sql_max_rows=100, sql_statement_timeout_seconds=5)
            if not descriptor["available"]:
                descriptor["setup"] = _setup("postgres")
            descriptor["default_mode"] = "snippet"
            descriptor["modes"] = [
                {
                    "id": "snippet",
                    "title": "SQL snippet",
                    "available": descriptor["available"],
                    "can_run": descriptor["available"],
                    "reason": descriptor["reason"],
                    "timeout_seconds": self.timeout_seconds,
                    "allowed_timeout_seconds": list(ALLOWED_TIMEOUT_SECONDS),
                }
            ]
            if primary and lesson.lesson_path.endswith(".sql"):
                supported = (
                    shutil.which("psql", path=external_program_environment().get("PATH"))
                    is not None
                )
                reason = (
                    "Runs the guarded learner SQL file, fixed psql directives and includes."
                    if descriptor["available"]
                    else descriptor["reason"]
                )
                if not supported:
                    reason = (
                        "Whole SQL mode needs psql. Use Docker or install PostgreSQL client tools."
                    )
                try:
                    lesson_source_policy(self.catalog, lesson_id)
                except (ValueError, OSError, SqlNotebookError) as exc:
                    supported = False
                    reason = str(exc)
                available = descriptor["available"] and supported
                descriptor["default_mode"] = "lesson"
                descriptor["modes"].append(
                    {
                        "id": "lesson",
                        "title": "Whole SQL lesson (psql)",
                        "available": available,
                        "can_run": available,
                        "reason": reason,
                        "timeout_seconds": 60,
                        "allowed_timeout_seconds": list(ALLOWED_TIMEOUT_SECONDS),
                        "transaction": (
                            "Statements may commit independently; the script controls transactions."
                        ),
                    }
                )
        elif notebook:
            descriptor["notebook_cells_ready"] = "IPython" not in missing
            descriptor["notebook_guidance"] = (
                "Notebook starters keep # %% cell boundaries. With IPython installed, "
                "Run executes those cells and IPython magics in order with shared state "
                "inside one fresh process, including inline PNG plots. Ordinary scripts "
                "run as Python. Interactive event loops, long training and persistent "
                "kernels still use the lesson's Jupyter or external workflow."
            )
            if "IPython" in missing:
                descriptor["notebook_guidance"] += (
                    " Install the notebooks profile in the selected Python backend for "
                    "cells and magics; ordinary standard-library snippets can run now."
                )
        descriptor["can_run"] = descriptor["available"]
        return descriptor

    def lesson(self, lesson_id: str) -> dict[str, Any]:
        lesson = self.catalog.get(lesson_id)
        runners = ("python", "sql") if lesson.runner in {"python", "sql"} else (lesson.runner,)
        return {
            "default_runner": lesson.runner,
            "runners": [self.runner(lesson_id, runner_id) for runner_id in runners],
        }
