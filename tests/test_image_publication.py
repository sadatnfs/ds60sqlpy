"""Publication workflow policy, native coverage and bounded credential handoffs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from scripts.ci_profiles import matrix

yaml = pytest.importorskip("yaml", reason="Workflow policy parsing requires PyYAML")
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-images.yml"


def workflow() -> dict[str, Any]:
    value: dict[str, Any] = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)
    return value


def test_only_marked_main_head_pushes_can_reach_the_secret_gate() -> None:
    value = workflow()
    assert value["on"] == {"push": {"branches": ["main"]}}
    guard = value["jobs"]["gate"]["if"]
    assert "github.event_name == 'push'" in guard
    assert "github.ref == 'refs/heads/main'" in guard
    assert "contains(github.event.head_commit.message, '[publish-docker]')" in guard
    assert value["concurrency"] == {
        "group": "classroom-dockerhub-publication",
        "cancel-in-progress": "false",
    }
    assert value["permissions"] == {"contents": "read", "actions": "read"}
    assert "workflow_dispatch" not in value["on"]
    assert "vars." not in WORKFLOW.read_text() and "environment:" not in WORKFLOW.read_text()


def test_gate_waits_for_source_checks_before_receipts_or_native_jobs() -> None:
    jobs = workflow()["jobs"]
    steps = jobs["gate"]["steps"]
    wait = next(i for i, step in enumerate(steps) if "ci_release_status.py" in step.get("run", ""))
    upload = next(
        i
        for i, step in enumerate(steps)
        if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    assert wait < upload
    assert "DOCKERHUB" not in json.dumps(steps[wait].get("env", {}))
    promotion_steps = jobs["promote"]["steps"]
    recheck = next(
        i for i, step in enumerate(promotion_steps) if "ci_release_status.py" in step.get("run", "")
    )
    promote = next(
        i
        for i, step in enumerate(promotion_steps)
        if "docker_release.py promote" in step.get("run", "")
    )
    assert recheck < promote


def test_native_seed_and_workers_cover_both_platforms_and_all_ordinary_profiles() -> None:
    jobs = workflow()["jobs"]
    assert jobs["seed"]["strategy"]["matrix"]["include"] == [
        {"architecture": "amd64", "runner": "ubuntu-24.04"},
        {"architecture": "arm64", "runner": "ubuntu-24.04-arm"},
    ]
    assert jobs["workers"]["needs"] == ["gate", "seed"]
    assert jobs["workers"]["strategy"]["max-parallel"] == "2"
    worker_rows = matrix(native=True, workers_only=True)["include"]
    ordinary = {
        line.split()[0]
        for line in (ROOT / "docker/classroom-images.tsv").read_text().splitlines()
        if line and not line.startswith("#") and line.split()[5] == "ordinary"
    } - {"python-core"}
    for architecture in ("amd64", "arm64"):
        listed = [
            profile
            for row in worker_rows
            if row["architecture"] == architecture
            for profile in row["profiles"].split()
        ]
        assert len(listed) == len(set(listed)) and set(listed) == ordinary
    assert all("cuda" not in row["profiles"] for row in worker_rows)
    assert "--native --workers-only" in json.dumps(jobs["gate"])


def test_inspection_precedes_qualification_and_staging_uses_both_reports() -> None:
    for job_id in ("seed", "workers"):
        job = workflow()["jobs"][job_id]
        commands = [step.get("run", "") for step in job["steps"]]
        prepare = next(
            i for i, command in enumerate(commands) if "ci_classroom.py prepare" in command
        )
        inspect = next(
            i for i, command in enumerate(commands) if "docker_release.py inspect" in command
        )
        qualify = next(
            i for i, command in enumerate(commands) if "ci_classroom.py qualify" in command
        )
        stage = next(
            i for i, command in enumerate(commands) if "docker_release.py stage" in command
        )
        assert prepare < inspect < qualify < stage
        assert "--qualification work/module-reference-results.json" in commands[stage]
        assert "--qualification work/ci-qualification.json" in commands[stage]
        assert "--tested-images work/tested-images.json" in commands[stage]
        assert "secrets" not in json.dumps(job.get("env", {}))
        for step in job["steps"]:
            if "ci_classroom.py" in step.get("run", "") or "docker_release.py inspect" in step.get(
                "run", ""
            ):
                assert "DOCKERHUB" not in json.dumps(step.get("env", {}))


def test_login_is_short_lived_and_never_places_a_token_in_command_arguments() -> None:
    count = 0
    for job in workflow()["jobs"].values():
        for step in job["steps"]:
            command = step.get("run", "")
            if "docker login" in command:
                count += 1
                assert "--password-stdin" in command
                assert "--password " not in command
                assert 'DOCKER_CONFIG="$RUNNER_TEMP/' in command
                assert "docker logout" in command and "trap " in command
                assert step["env"]["DOCKERHUB_TOKEN"] == "${{ secrets.DOCKERHUB_TOKEN }}"
    assert count == 3
    for filename in ("ci.yml", "app-build.yml", "kubernetes.yml"):
        assert "secrets.DOCKERHUB" not in (WORKFLOW.parent / filename).read_text()


def test_only_small_same_run_receipts_cross_jobs() -> None:
    text = WORKFLOW.read_text()
    assert "docker image save" not in text and "docker image load" not in text
    assert "image.tar" not in text and "cache-from" not in text and "buildx" not in text
    assert "ci_release_artifacts.py gate --destination work/release" in text
    assert "ci_release_artifacts.py seed --architecture" in text
    assert "ci_release_artifacts.py receipts --destination work/receipts" in text
    assert "--seed-receipt work/seed/release-receipt.json" in text
    for job in workflow()["jobs"].values():
        for step in job["steps"]:
            if step.get("uses", "").startswith("actions/upload-artifact@"):
                assert all(path.endswith(".json") for path in step["with"]["path"].split())
                assert int(step["with"]["retention-days"]) <= 30


def test_final_promotion_requires_all_jobs_or_verified_existing_release_mode() -> None:
    job = workflow()["jobs"]["promote"]
    assert job["needs"] == ["gate", "seed", "workers"]
    condition = job["if"]
    assert "needs.gate.result == 'success'" in condition
    assert "needs.gate.outputs.mode == 'promote-existing'" in condition
    assert (
        "needs.seed.result == 'success'" in condition
        and "needs.workers.result == 'success'" in condition
    )
    assert "always()" in condition
    assert "docker_release.py promote" in json.dumps(job)
    assert "docker login" not in json.dumps(job)
    assert "continue-on-error" not in WORKFLOW.read_text()


def test_every_publication_checkout_and_action_is_pinned_to_the_exact_source() -> None:
    for job in workflow()["jobs"].values():
        checkout = next(
            step for step in job["steps"] if step.get("uses", "").startswith("actions/checkout@")
        )
        assert checkout["with"] == {"ref": "${{ github.sha }}", "persist-credentials": "false"}
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", step["uses"])
