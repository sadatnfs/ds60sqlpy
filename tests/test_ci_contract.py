from __future__ import annotations

import os
import shlex
import subprocess
import sys
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
        "scripts/check_public_release.py",
        "scripts/check_published_links.py",
        "scripts/normalize_lesson_prose.py",
        "scripts/check_content_rendering.py",
        "scripts/check_modules.py",
        "scripts/check_classroom_ui.mjs",
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


def test_ci_installs_renderer_before_sql_or_starter_checks() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    postgres = workflow.split("  postgres:", maxsplit=1)[1].split("  advanced-imports:")[0]
    assert postgres.index("uv sync --frozen") < postgres.index("scripts/course.py sql")
    assert "DS60_TEST_DATABASE_URL:" in postgres
    assert "DS60_SQL_EXPANSION_TEST_URL:" in postgres
    assert "tests/test_execution.py tests/test_sql_expansion_live.py" in postgres
    app = (WORKFLOW.parent / "app-build.yml").read_text(encoding="utf-8")
    starter = app.split("  windows-starter:", maxsplit=1)[1].split("  native:")[0]
    assert starter.index("uv sync --frozen") < starter.index("scripts/build_windows_starter.py")


def test_current_docker_entrypoint_covers_every_profile_and_recreation_receipts() -> None:
    from scripts.check_classroom_profiles import CASES

    workflow = (WORKFLOW.parent / "app-build.yml").read_text(encoding="utf-8")
    docker = workflow.split("  docker:", maxsplit=1)[1]
    matrix = docker.split("    env:", maxsplit=1)[0]
    assert "paths:" not in workflow
    assert "  push:" in workflow and "  pull_request:" in workflow
    assert "bash classroom --registry upstream --no-browser" in docker
    assert "scripts/docker_lab.sh" not in docker
    assert "compose.classroom.yaml" in docker
    assert "work/runtime-receipts.json" in docker and "--check-persistence" in docker
    assert "python-core $DS60_PROFILES" in docker
    for profile in CASES.keys() - {"python-core"}:
        assert profile in matrix
    assert "--profile '*' down\n" in docker
    assert "if: always()" in docker and "--volumes --remove-orphans" in docker
    assert "docker system prune" not in docker and "docker image prune" not in docker


def test_workflows_pin_actions_and_install_node_explicitly() -> None:
    import re

    for path in WORKFLOW.parent.glob("*.yml"):
        workflow = path.read_text(encoding="utf-8")
        for action in re.findall(r"uses:\s+(\S+)", workflow):
            assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", action), action
        assert "contents: read" in workflow and "persist-credentials: false" in workflow
    core = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/setup-node@" in core
    assert 'node-version: "24"' in core
    assert "pytest -n 4 --dist loadgroup" in core
    assert "--basetemp=work/test-tmp" in core


def test_core_test_command_works_in_a_fresh_checkout_without_work_directory(
    tmp_path: Path,
) -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    preparation = workflow.split("- name: Prepare test workspace", maxsplit=1)[1].split(
        "- name:", maxsplit=1
    )[0]
    prepare_command = shlex.split(preparation.split("run:", maxsplit=1)[1].strip())
    assert prepare_command[:2] == ["python", "-c"]
    test_step = workflow.split("- name: Unit tests (four grouped workers)", maxsplit=1)[1].split(
        "- name:", maxsplit=1
    )[0]
    command = shlex.split(" ".join(test_step.split("run: >-", maxsplit=1)[1].split()))
    pytest_arguments = command[command.index("pytest") + 1 :]
    checkout = tmp_path / "fresh-checkout"
    checkout.mkdir()
    assert not (checkout / "work").exists()
    subprocess.run([sys.executable, *prepare_command[1:]], cwd=checkout, check=True, timeout=15)
    assert (checkout / "work/test-results").is_dir()
    (checkout / "test_workspace.py").write_text(
        "from pathlib import Path\n"
        "def test_worker_temp_directory(tmp_path):\n"
        "    assert tmp_path.is_dir()\n"
        "    assert tmp_path.is_relative_to(Path.cwd() / 'work' / 'test-tmp')\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *pytest_arguments, "test_workspace.py"],
        cwd=checkout,
        env={**os.environ, "PYTEST_ADDOPTS": ""},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (checkout / "work/test-results/core.xml").is_file()
    assert (checkout / "work/test-tmp").is_dir()
