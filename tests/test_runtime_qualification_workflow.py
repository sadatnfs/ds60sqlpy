"""Contract for the dispatch-only two-architecture runtime qualification workflow."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml  # type: ignore[import-untyped]

from scripts.ci_profiles import RUNNERS, matrix

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "runtime-qualification.yml"
NATIVE_RUNNERS = {"ubuntu-24.04", "ubuntu-24.04-arm"}
CI_PROJECT_RE = re.compile(r"ds60-(?:ci|pub)-[a-z0-9][a-z0-9-]{0,80}")
P7_PROJECT_RE = re.compile(r"^ds60-p7-[a-z0-9-]+$")
PROJECT_LIMIT = 49


def text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def workflow() -> dict[str, Any]:
    loaded = yaml.safe_load(text())
    assert isinstance(loaded, dict)
    return loaded


def triggers(data: dict[str, Any]) -> dict[str, Any]:
    # PyYAML 1.1 reads the bare key "on" as boolean True.
    raw: dict[Any, Any] = data
    value = raw.get("on", raw.get(True))
    assert isinstance(value, dict)
    return value


def job(name: str) -> dict[str, Any]:
    jobs = workflow()["jobs"]
    assert name in jobs, sorted(jobs)
    found = jobs[name]
    assert isinstance(found, dict)
    return found


def steps(name: str) -> list[dict[str, Any]]:
    return list(job(name)["steps"])


def step_index(items: list[dict[str, Any]], needle: str) -> int:
    matches = [i for i, step in enumerate(items) if needle in str(step.get("run", ""))]
    assert len(matches) == 1, (needle, matches)
    return matches[0]


def test_only_trigger_is_manual_dispatch_with_optional_groups_input() -> None:
    on = triggers(workflow())
    assert set(on) == {"workflow_dispatch"}
    inputs = on["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"groups"}
    assert inputs["groups"]["type"] == "string"
    assert inputs["groups"]["required"] is False
    assert inputs["groups"].get("default", "") == ""


def test_read_only_token_no_secrets_and_pinned_actions() -> None:
    data = workflow()
    assert data["permissions"] == {"contents": "read"}
    assert data["env"]["PYTHONUTF8"] == "1"
    assert data["concurrency"]["cancel-in-progress"] is False
    assert "runtime-qualification-" in data["concurrency"]["group"]
    for name, body in data["jobs"].items():
        assert "permissions" not in body, name
    assert "secrets." not in text()
    uses = re.findall(r"uses:\s+(\S+)", text())
    assert uses
    for action in uses:
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", action), action
    checkouts = [
        step
        for body in data["jobs"].values()
        for step in body["steps"]
        if str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    assert len(checkouts) == len(data["jobs"])
    assert all(step["with"]["persist-credentials"] is False for step in checkouts)


def test_native_runners_only_without_emulation() -> None:
    body = text()
    for forbidden in ("setup-qemu", "qemu", "binfmt", "--platform", "prune"):
        assert forbidden not in body.lower(), forbidden
    assert job("matrix")["runs-on"] == "ubuntu-24.04"
    for name in ("groups", "lifecycle"):
        assert job(name)["runs-on"] == "${{ matrix.runner }}"
        assert job(name)["strategy"]["fail-fast"] is False
    assert set(RUNNERS.values()) == NATIVE_RUNNERS
    rows = matrix(native=True)["include"]
    assert len(rows) == 38
    assert {row["runner"] for row in rows} == NATIVE_RUNNERS
    lifecycle = job("lifecycle")["strategy"]["matrix"]["include"]
    assert {(row["architecture"], row["runner"]) for row in lifecycle} == set(RUNNERS.items())


def test_groups_job_builds_verifies_revision_then_qualifies_and_cleans_up() -> None:
    groups = job("groups")
    assert groups["needs"] == "matrix"
    assert groups["timeout-minutes"] == 180
    assert groups["strategy"]["max-parallel"] == 8
    assert groups["strategy"]["matrix"] == "${{ fromJSON(needs.matrix.outputs.matrix) }}"
    env = groups["env"]
    assert env["CI_ARCH"] == "${{ matrix.architecture }}"
    assert env["CI_PROFILES"] == "${{ matrix.profiles }}"
    assert env["RELEASE_VERSION"] == "${{ needs.matrix.outputs.version }}"
    items = steps("groups")
    prepare = step_index(items, "scripts/ci_classroom.py prepare")
    revision = step_index(items, "scripts/verify_image_revision.py")
    qualify = step_index(items, "scripts/ci_classroom.py qualify")
    diagnostics = step_index(items, "scripts/ci_classroom.py diagnostics")
    cleanup = step_index(items, "scripts/ci_classroom.py cleanup")
    assert prepare < revision < qualify < diagnostics < cleanup
    assert items[diagnostics]["if"] == "failure()"
    assert items[cleanup]["if"] == "always()"
    verify = items[revision]["run"]
    assert '--revision "$GITHUB_SHA"' in verify
    assert '--tag "$RELEASE_VERSION"' in verify
    assert '--architecture "$CI_ARCH"' in verify
    assert "--report work/image-revision.json" in verify
    assert "read -ra" in verify and "--profile" in verify
    for index in (prepare, qualify, diagnostics, cleanup):
        run = items[index]["run"]
        assert '--architecture "$CI_ARCH"' in run and "--confirm-disposable" in run
        assert '--project "$CI_PROJECT"' in run


def test_groups_job_builds_through_the_launcher_driver_without_direct_builds() -> None:
    for step in steps("groups"):
        run = str(step.get("run", ""))
        assert "docker build" not in run and "compose build" not in run
        assert "docker buildx" not in run


def test_project_names_fit_driver_and_harness_rules() -> None:
    run_id, attempt = "9" * 15, "99"
    template = job("groups")["env"]["CI_PROJECT"]
    assert template == (
        "ds60-ci-${{ matrix.project_group }}-${{ matrix.architecture }}"
        "-${{ github.run_id }}-${{ github.run_attempt }}"
    )
    for row in matrix(native=True)["include"]:
        name = f"ds60-ci-{row['project_group']}-{row['architecture']}-{run_id}-{attempt}"
        assert CI_PROJECT_RE.fullmatch(name), name
        assert len(name) <= PROJECT_LIMIT, name
    run = next(
        step["run"]
        for step in steps("lifecycle")
        if "check_classroom_lifecycle.py" in step.get("run", "")
    )
    project = re.search(r'--project "([^"]+)"', run)
    assert project is not None
    for arch in RUNNERS:
        name = (
            project.group(1)
            .replace("${{ matrix.architecture }}", arch)
            .replace("${{ github.run_id }}", run_id)
            .replace("${{ github.run_attempt }}", attempt)
        )
        assert P7_PROJECT_RE.fullmatch(name), name
        assert len(name) <= PROJECT_LIMIT, name


def test_lifecycle_job_runs_full_transitions_on_each_architecture() -> None:
    lifecycle = job("lifecycle")
    assert "needs" not in lifecycle
    assert lifecycle["timeout-minutes"] == 150
    checkout = next(
        step
        for step in steps("lifecycle")
        if str(step.get("uses", "")).startswith("actions/checkout@")
    )
    assert checkout["with"]["fetch-depth"] == 2
    run = next(
        step["run"]
        for step in steps("lifecycle")
        if "check_classroom_lifecycle.py" in step.get("run", "")
    )
    assert "--base HEAD~1 --target HEAD" in run
    assert "--architecture ${{ matrix.architecture }}" in run
    assert "--report work/p7-lifecycle-${{ matrix.architecture }}.json" in run
    assert "--seed-images" not in run and "--steps" not in run and "--keep" not in run


def test_artifacts_are_named_per_architecture_and_always_uploaded() -> None:
    def upload(name: str) -> dict[str, Any]:
        found = [
            step
            for step in steps(name)
            if str(step.get("uses", "")).startswith("actions/upload-artifact@")
        ]
        assert len(found) == 1
        assert found[0]["if"] == "always()"
        return dict(found[0]["with"])

    groups = upload("groups")
    assert groups["name"] == "runtime-${{ matrix.architecture }}-${{ matrix.group }}"
    assert groups["retention-days"] == 14
    for path in (
        "work/*receipts.json",
        "work/runtime-failures.json",
        "work/module-reference-results.json",
        "work/scientist-browser.json",
        "work/ci-qualification.json",
        "work/image-revision.json",
        "work/browser-screenshots/*.png",
    ):
        assert path in groups["path"].split(), path
    lifecycle = upload("lifecycle")
    assert lifecycle["name"] == "lifecycle-${{ matrix.architecture }}"
    assert "work/p7-lifecycle-*.json" in lifecycle["path"].split()
    assert lifecycle["retention-days"] == 14


def test_groups_input_reaches_shell_only_through_env() -> None:
    data = workflow()
    for body in data["jobs"].values():
        for step in body["steps"]:
            assert "inputs." not in str(step.get("run", ""))
    selection = [step for step in steps("matrix") if "GROUPS_FILTER" in step.get("env", {})]
    assert len(selection) == 1
    assert selection[0]["env"]["GROUPS_FILTER"] == "${{ inputs.groups }}"
    assert "scripts/ci_profiles.py --native" in selection[0]["run"]
    assert text().count("${{ inputs.groups }}") == 1
    outputs = job("matrix")["outputs"]
    assert set(outputs) == {"matrix", "version"}


def run_selection(tmp_path: Path, groups: str) -> tuple[int, dict[str, str], str]:
    step = next(step for step in steps("matrix") if "GROUPS_FILTER" in step.get("env", {}))
    output = tmp_path / "github-output"
    output.write_text("")
    env = {
        **os.environ,
        "GROUPS_FILTER": groups,
        "GITHUB_OUTPUT": str(output),
        "PYTHONPATH": str(REPO_ROOT),
    }
    shell = Path(sys.executable).parent
    env["PATH"] = f"{shell}{os.pathsep}{env.get('PATH', '')}"
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", step["run"]],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    values = dict(line.split("=", 1) for line in output.read_text().splitlines() if "=" in line)
    return result.returncode, values, result.stderr


def test_selection_without_filter_emits_all_native_rows_and_version(tmp_path: Path) -> None:
    code, values, stderr = run_selection(tmp_path, "")
    assert code == 0, stderr
    assert json.loads(values["matrix"]) == matrix(native=True)
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", values["version"])


def test_selection_filters_groups_on_both_architectures(tmp_path: Path) -> None:
    code, values, stderr = run_selection(tmp_path, "  python-core  ")
    assert code == 0, stderr
    rows = json.loads(values["matrix"])["include"]
    assert {(row["group"], row["runner"]) for row in rows} == {
        ("python-core", runner) for runner in NATIVE_RUNNERS
    }


@pytest.mark.parametrize("value", ["python-core nope", "$(touch pwned)", "python-core;id"])
def test_selection_rejects_unknown_or_hostile_groups(tmp_path: Path, value: str) -> None:
    code, values, _ = run_selection(tmp_path, value)
    assert code != 0
    assert "matrix" not in values
    assert not (REPO_ROOT / "pwned").exists()
