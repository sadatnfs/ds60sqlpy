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


def test_core_workflow_runs_every_generated_curriculum_gate() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    core_job = workflow.split("  learner-bootstrap:", maxsplit=1)[0]

    required_commands = (
        "scripts/build_catalog.py",
        "scripts/audit_practice.py --write-report",
        "scripts/audit_lesson_depth.py --write-report",
        "scripts/build_course_guide.py --check",
        "scripts/build_lesson_readers.py --check",
        "pytest",
        "scripts/course.py validate",
        "scripts/validate_notebooks.py",
        "scripts/validate_notebooks.py --smoke",
    )
    for command in required_commands:
        assert command in core_job


def test_lock_portability_is_resolved_for_supported_binary_platforms() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    core_job = workflow.split("  learner-bootstrap:", maxsplit=1)[0]

    assert "- name: Verify all-extras lock portability" in core_job
    for platform in (
        "x86_64-pc-windows-msvc",
        "x86_64-unknown-linux-gnu",
        "aarch64-apple-darwin",
        "x86_64-apple-darwin",
    ):
        assert f"--python-platform {platform}" in core_job


def test_advanced_imports_are_manual_or_scheduled_and_cross_platform() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    advanced_job = workflow.split("  advanced-imports:", maxsplit=1)[1]

    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert (
        "if: github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'"
    ) in advanced_job
    for operating_system in (
        "ubuntu-latest",
        "windows-latest",
        "macos-latest",
    ):
        assert f"- {operating_system}" in advanced_job
    assert "- name: Install the macOS OpenMP runtime" in advanced_job
    assert "if: runner.os == 'macOS'" in advanced_job
    assert "run: brew install libomp" in advanced_job
    assert "uv sync --frozen --all-extras" in advanced_job
    assert "scripts/check_advanced_imports.py" in advanced_job
