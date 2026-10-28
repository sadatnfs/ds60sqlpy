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
    from scripts.ci_source_quality import languages
    from scripts.format_repo import LANGUAGES

    workflow = WORKFLOW.read_text(encoding="utf-8")
    formatting = workflow.split("  source-quality:", 1)[1].split("  core:", 1)[0]
    assert "toolchain: [main, r, julia]" in formatting
    assert 'scripts/ci_source_quality.py --toolchain "$TOOLCHAIN"' in formatting
    assert "run: git diff --exit-code" in formatting
    assigned = [item for shard in ("main", "r", "julia") for item in languages(shard)]
    assert len(assigned) == len(set(assigned)) and set(assigned) == set(LANGUAGES)
    driver = (REPO_ROOT / "scripts/ci_source_quality.py").read_text()
    assert '"scripts/format-repo", "--check"' in driver
    assert '"scripts/lint-repo"' in driver
    assert "ensure_publication_paths(ROOT)" in driver
    assert "scripts/sync_example_fences.py --check" in workflow
    hooks = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "entry: ./scripts/format-repo --check" in hooks
    assert "id: ds60-ruff-format" not in hooks
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "format:\n\t./scripts/format-repo\n" in makefile
    assert "format-check:\n\t./scripts/format-repo --check\n" in makefile
    assert "lint:\n\t./scripts/lint-repo\n" in makefile


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
            assert runners == [
                "ubuntu-24.04",
                "${{ matrix.runner }}",
                "${{ matrix.runner }}",
                "ubuntu-24.04",
                "${{ matrix.runner }}",
            ]
            assert "runner: ubuntu-24.04-arm" in workflow
            assert "runner: ubuntu-24.04" in workflow
            assert "workflow_dispatch:" not in workflow
            assert "branches: [main]" in workflow
            assert "contains(github.event.head_commit.message, '[publish-docker]')" in workflow
        elif path.name == "targeted-images.yml":
            assert runners == [
                "ubuntu-24.04",
                "ubuntu-24.04",
                "${{ matrix.runner }}",
                "${{ matrix.runner }}",
                "ubuntu-24.04",
                "${{ matrix.runner }}",
            ]
            assert "runner: ubuntu-24.04-arm" in workflow
            assert "runner: ubuntu-24.04" in workflow
            assert "workflow_dispatch:" not in workflow
            assert "on:\n  push:" in workflow
        elif path.name == "verify-published-images.yml":
            assert runners == ["${{ matrix.runner }}"]
            assert "runner: ubuntu-24.04-arm" in workflow
            assert "runner: ubuntu-24.04" in workflow
            assert "workflow_dispatch:" in workflow and "  push:" not in workflow
            assert "fetch-depth: 0" in workflow
            assert "docker_release.py promote" not in workflow
            assert "docker_release.py stage" not in workflow
        else:
            assert runners and set(runners) == {"ubuntu-latest"}, path.name
        assert "windows-latest" not in workflow and "macos-latest" not in workflow
        assert "scripts/build_app.py" not in workflow
        assert "scripts/check_windows_private_acl.py" not in workflow
        assert "scripts/check_windows_runtime_startup.py" not in workflow
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert 'python-version: ["3.11", "3.12"]' in workflow
    bootstrap = workflow.split("  developer-bootstrap:", 1)[1].split("  postgres:", 1)[0]
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
    assert starter.index("uv sync --frozen") < starter.index("scripts/build_starter.py")
    assert "--output dist/DS60LearningLab-Docker-Starter.zip" in starter
    assert "path: dist/DS60LearningLab-Docker-Starter.zip" in starter
    assert "if-no-files-found: error" in starter


def test_current_docker_entrypoint_covers_every_profile_and_recreation_receipts() -> None:
    from scripts.check_classroom_profiles import CASES
    from scripts.ci_profiles import groups

    workflow = (WORKFLOW.parent / "app-build.yml").read_text()
    intent = workflow.split("  select-images:", 1)[1].split("  docker-starter:", 1)[0]
    starter = workflow.split("  docker-starter:", 1)[1].split("  docker-matrix:", 1)[0]
    selection = workflow.split("  docker-matrix:", 1)[1].split("  docker:", 1)[0]
    assert "scripts/ci_targeted_images.py app-build-intent" in intent
    assert "mode: ${{ steps.intent.outputs.mode }}" in intent
    assert "needs: select-images" in starter
    assert "if: needs.select-images.outputs.mode != 'build-test'" in starter
    assert "needs: select-images" in selection
    assert "if: needs.select-images.outputs.mode == 'ordinary'" in selection
    assert "  push:" in workflow and "  pull_request:" in workflow
    assert "paths:" not in workflow
    docker = workflow.split("  docker:", 1)[1]
    assert "scripts/ci_classroom.py prepare" in docker
    assert "scripts/ci_classroom.py qualify" in docker
    assert "scripts/ci_classroom.py cleanup" in docker
    assert "max-parallel: 4" in docker
    assert {profile for group in groups() for profile in group["profiles"]} == set(CASES)
    assert "work/*receipts.json" in docker and "work/module-reference-results.json" in docker
    assert "if: always()" in docker
    assert "docker system prune" not in docker and "docker image prune" not in docker
    driver = (REPO_ROOT / "scripts/ci_classroom.py").read_text()
    assert '"--registry",' in driver and '"mirrors"' in driver
    assert '"--no-build"' in driver and '"down", "--volumes", "--remove-orphans"' in driver
    assert "--rebuild" not in driver


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


def test_owned_kubernetes_build_matches_the_selected_overlay_image() -> None:
    workflow = (REPO_ROOT / ".github/workflows/kubernetes.yml").read_text()
    overlay = (REPO_ROOT / "compose.classroom.kubernetes.yaml").read_text()
    built = re.findall(r"-t (ds60sqlpy-worker-k8s-kind:[^\s]+)", workflow)
    selected = re.findall(r"image: (ds60sqlpy-worker-k8s-kind:[^\s]+)", overlay)
    version = tomllib.loads(PYPROJECT.read_text())["project"]["version"]
    assert built == selected == [f"ds60sqlpy-worker-k8s-kind:{version}"]
