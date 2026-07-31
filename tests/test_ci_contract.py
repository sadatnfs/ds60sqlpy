from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def test_core_matrix_overrides_learner_python_default_and_asserts_version() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    core_job = workflow.split("  learner-bootstrap:", maxsplit=1)[0]

    assert "UV_PYTHON: ${{ matrix.python-version }}" in workflow
    assert "DS60_EXPECTED_PYTHON: ${{ matrix.python-version }}" in workflow
    assert "- name: Verify the matrix interpreter" in workflow
    assert "actual = sys.version_info[:2]" in workflow
    assert "assert actual == expected" in workflow
    assert "timeout-minutes: 30" in core_job


def test_pytest_console_entrypoint_can_import_repository_scripts() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert project["tool"]["pytest"]["ini_options"]["pythonpath"] == ["."]
    assert (REPO_ROOT / "scripts" / "__init__.py").is_file()


def test_sql_notebook_profile_is_self_contained_for_dataframe_conversion() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    requirements = project["project"]["optional-dependencies"]["sql-notebooks"]

    assert any(requirement.startswith("jupysql") for requirement in requirements)
    assert any(requirement.startswith("pandas") for requirement in requirements)
    assert any(requirement.startswith("psycopg") for requirement in requirements)
    assert any(requirement.startswith("sqlalchemy") for requirement in requirements)
