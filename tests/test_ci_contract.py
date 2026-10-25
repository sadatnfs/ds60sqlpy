from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def test_core_matrix_overrides_project_python_default_and_asserts_version() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    core_job = workflow.split("  developer-bootstrap:", maxsplit=1)[0]

    assert "UV_PYTHON: ${{ matrix.python-version }}" in workflow
    assert "DS60_EXPECTED_PYTHON: ${{ matrix.python-version }}" in workflow
    assert "- name: Verify the matrix interpreter" in workflow
    assert "actual = sys.version_info[:2]" in workflow
    assert "assert actual == expected" in workflow
    assert "timeout-minutes: 30" in core_job


def test_source_quality_runs_once_with_the_shared_docker_entrypoints() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    formatting = workflow.split("  source-quality:", maxsplit=1)[1].split("  core:", maxsplit=1)[0]
    assert "runs-on: ubuntu-latest" in formatting
    assert "matrix:" not in formatting
    assert "run: ./scripts/format-repo --check" in formatting
    assert "run: ./scripts/lint-repo" in formatting
    assert "run: git diff --exit-code" in formatting
    assert workflow.count("./scripts/format-repo --check") == 1
    assert "ruff format --check" not in workflow
    hooks = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "entry: ./scripts/format-repo --check" in hooks
    assert "id: ds60-ruff-format" not in hooks
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "format:\n\t./scripts/format-repo\n" in makefile
    assert "format-check:\n\t./scripts/format-repo --check\n" in makefile
    assert "lint:\n\t./scripts/lint-repo\n" in makefile
    assert "check: format-check lint\n" in makefile


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
    core_job = workflow.split("  developer-bootstrap:", maxsplit=1)[0]

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


def test_lock_resolution_matches_the_linux_validation_platform() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    core_job = workflow.split("  developer-bootstrap:", maxsplit=1)[0]

    assert "- name: Verify Linux optional dependency resolution" in core_job
    assert re.findall(r"--python-platform (\S+)", core_job) == ["x86_64-unknown-linux-gnu"]
    assert "uv sync --quiet --frozen --all-extras --dry-run" in core_job


def test_advanced_imports_are_manual_or_scheduled_on_linux() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    advanced_job = workflow.split("  advanced-imports:", maxsplit=1)[1]

    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert (
        "if: github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'"
    ) in advanced_job
    assert "runs-on: ubuntu-latest" in advanced_job
    assert 'python-version: "3.12"' in advanced_job
    assert 'UV_PYTHON: "3.12"' in advanced_job
    assert "uv sync --frozen --all-extras" in advanced_job
    assert "scripts/check_advanced_imports.py" in advanced_job


def test_release_jobs_target_linux_containers_and_contributor_tooling() -> None:
    assert not (WORKFLOW.parent / "windows-runtime.yml").exists()
    for path in WORKFLOW.parent.glob("*.yml"):
        workflow = path.read_text(encoding="utf-8")
        runners = re.findall(r"(?m)^    runs-on: (.+)$", workflow)
        if path.name == "publish-images.yml":
            reviewed_native_runner = (
                "${{ inputs.architecture == 'arm64' && 'ubuntu-24.04-arm' || 'ubuntu-24.04' }}"
            )
            assert runners == ["ubuntu-latest", reviewed_native_runner, reviewed_native_runner]
            architecture = workflow.split("      architecture:", maxsplit=1)[1].split(
                "      publish:", maxsplit=1
            )[0]
            assert re.findall(r"(?m)^        type: (.+)$", architecture) == ["choice"]
            assert re.findall(r"(?m)^        options: (.+)$", architecture) == ["[amd64, arm64]"]
            assert re.findall(r"(?m)^        default: (.+)$", architecture) == ["amd64"]
            assert "  workflow_dispatch:" in workflow
            assert not re.search(r"(?m)^  (push|pull_request|schedule):", workflow)
        else:
            assert runners and set(runners) == {"ubuntu-latest"}, path.name
        assert "windows-latest" not in workflow and "macos-latest" not in workflow
        assert "scripts/build_app.py" not in workflow
        assert "scripts/check_windows_private_acl.py" not in workflow
        assert "scripts/check_windows_runtime_startup.py" not in workflow

    workflow = WORKFLOW.read_text(encoding="utf-8")
    core = workflow.split("  developer-bootstrap:", maxsplit=1)[0]
    assert 'python-version: ["3.11", "3.12"]' in core
    bootstrap = workflow.split("  developer-bootstrap:", maxsplit=1)[1].split(
        "  postgres:", maxsplit=1
    )[0]
    assert "Linux contributor bootstrap" in bootstrap
    assert 'UV_PYTHON: "3.12"' in bootstrap
    assert "bash scripts/setup.sh --dependency-mode locked" in bootstrap
    assert ".venv/bin/python scripts/course.py doctor" in bootstrap
    assert ".venv/bin/python scripts/validate_notebooks.py --smoke --smoke-days 1" in bootstrap


def test_ci_installs_renderer_before_sql_or_starter_checks() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    postgres = workflow.split("  postgres:", maxsplit=1)[1].split("  advanced-imports:")[0]
    assert postgres.index("uv sync --frozen") < postgres.index("scripts/course.py sql")
    assert "DS60_TEST_DATABASE_URL:" in postgres
    assert "DS60_SQL_EXPANSION_TEST_URL:" in postgres
    assert "tests/test_execution.py tests/test_sql_expansion_live.py" in postgres
    app = (WORKFLOW.parent / "app-build.yml").read_text(encoding="utf-8")
    starter = app.split("  docker-starter:", maxsplit=1)[1].split("  docker:", maxsplit=1)[0]
    assert starter.index("uv sync --frozen") < starter.index("scripts/build_windows_starter.py")
    assert "--output dist/DS60LearningLab-Docker-Starter.zip" in starter
    assert "path: dist/DS60LearningLab-Docker-Starter.zip" in starter
    assert "if-no-files-found: error" in starter


def test_current_docker_entrypoint_covers_every_profile_and_recreation_receipts() -> None:
    from scripts.check_classroom_profiles import CASES

    workflow = (WORKFLOW.parent / "app-build.yml").read_text(encoding="utf-8")
    docker = workflow.split("  docker:", maxsplit=1)[1]
    matrix = docker.split("    env:", maxsplit=1)[0]
    assert "paths:" not in workflow
    assert "  push:" in workflow and "  pull_request:" in workflow
    assert "bash classroom --registry upstream --rebuild --no-browser" in docker
    assert "scripts/docker_lab.sh" not in docker
    assert "compose.classroom.yaml" in docker
    assert "work/runtime-receipts.json" in docker and "--check-persistence" in docker
    assert "python-core $DS60_PROFILES" in docker
    for command in (
        "scripts/check_lab_http.py",
        "scripts/check_classroom_profiles.py",
        "scripts/check_classroom_failures.py",
        "scripts/check_module_references.py",
        "scripts/check_classroom_browser.py",
        "scripts/check_d3_browser.py",
    ):
        assert command in docker
    assert "--check-timeout" in docker
    assert "scripts/course.py sql --quiet all --reset" in docker
    assert "scripts/course.py sql --quiet solutions --reset" in docker
    assert "max-parallel: 4" in matrix
    for profile in CASES.keys() - {"python-core"}:
        assert profile in matrix
    assert "--profile '*' down\n" in docker
    assert "if: always()" in docker and "--volumes --remove-orphans" in docker
    assert "docker system prune" not in docker and "docker image prune" not in docker


def test_workflows_pin_actions_and_install_node_explicitly() -> None:
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
