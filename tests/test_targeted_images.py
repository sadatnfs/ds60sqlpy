"""Exact marker selection and bounded targeted receipt scope."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts import ci_release_artifacts as release_artifacts
from scripts import ci_targeted_images as targeted
from scripts.ci_profiles import RUNNERS, groups, project_group_slug

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_keeps_build_test_free_of_hub_secrets_and_uploads() -> None:
    yaml = pytest.importorskip("yaml")
    workflow = yaml.load(
        (ROOT / ".github/workflows/targeted-images.yml").read_text(),
        Loader=yaml.BaseLoader,
    )
    jobs = workflow["jobs"]
    concurrency = workflow["concurrency"]
    assert concurrency["cancel-in-progress"] == "false"
    assert "classroom-dockerhub-publication" in concurrency["group"]
    assert "classroom-docker-build-test-{0}" in concurrency["group"]
    assert "contains(github.event.head_commit.message, '[publish-')" in concurrency["group"]
    assert "secrets.DOCKERHUB" not in json.dumps(jobs["intent"])
    assert jobs["publication-gate"]["if"] == "needs.intent.outputs.mode == 'publish'"
    assert "needs.intent.outputs.mode == 'publish'" in jobs["promote"]["if"]
    for job_name in ("seed", "workers"):
        for step in jobs[job_name]["steps"]:
            if "secrets.DOCKERHUB" in json.dumps(step) or step.get("uses", "").startswith(
                "actions/upload-artifact@"
            ):
                assert step.get("if") == "needs.intent.outputs.mode == 'publish'"
    app_build = yaml.load(
        (ROOT / ".github/workflows/app-build.yml").read_text(), Loader=yaml.BaseLoader
    )["jobs"]
    assert app_build["docker-starter"]["if"] == ("needs.select-images.outputs.mode != 'build-test'")
    assert app_build["docker-matrix"]["if"] == ("needs.select-images.outputs.mode == 'ordinary'")


def test_every_ordinary_group_and_profile_alias_selects_the_complete_group() -> None:
    for row in groups():
        for alias in [row["id"], *row["profiles"]]:
            for mode in ("build-test", "publish"):
                assert targeted.parse_marker(f"Source change [{mode}-{alias}]") == targeted.Intent(
                    mode, row["id"], f"[{mode}-{alias}]"
                )
    publish = targeted.parse_marker("[publish-js]")
    build_test = targeted.parse_marker("[build-test-js]")
    assert publish is not None and publish.group == "javascript-typescript"
    assert build_test is not None and build_test.group == "javascript-typescript"
    assert targeted.selected_matrix("javascript-typescript") == {
        "include": [
            {
                "group": "javascript-typescript",
                "profiles": "javascript-node typescript-node",
                "project_group": project_group_slug("javascript-typescript"),
                "architecture": arch,
                "runner": runner,
            }
            for arch, runner in RUNNERS.items()
        ]
    }


@pytest.mark.parametrize(
    "message",
    [
        "[publish-unknown]",
        "[build-test-unknown]",
        "[publish-js] [publish-java]",
        "[publish-docker] [publish-js]",
        "[build-test-js] [publish-js]",
        "[publish-js",
        "[publish-js] [publish-js]",
    ],
)
def test_marker_parser_fails_closed(message: str) -> None:
    with pytest.raises(ValueError):
        targeted.parse_marker(message)


def test_unmarked_and_full_marker_do_not_select_a_targeted_group() -> None:
    assert targeted.parse_marker("Ordinary change") is None
    assert targeted.parse_marker("Release [publish-docker]") == targeted.Intent(
        "full", None, "[publish-docker]"
    )


@pytest.mark.parametrize(
    ("intent", "expected"),
    [
        (None, "ordinary"),
        (targeted.Intent("build-test", "javascript-typescript", "[build-test-js]"), "build-test"),
        (targeted.Intent("publish", "javascript-typescript", "[publish-js]"), "publish"),
        (targeted.Intent("full", None, "[publish-docker]"), "full"),
    ],
)
def test_app_build_intent_routes_exact_marker_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    intent: targeted.Intent | None,
    expected: str,
) -> None:
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setattr(targeted, "push_intent", lambda root: intent)
    output = tmp_path / "github-output"
    targeted.write_app_build_intent(output)
    assert output.read_text() == f"mode={expected}\n"


def test_app_build_tag_push_uses_ordinary_checks_without_branch_marker_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REF", "refs/tags/v1.0.0")
    monkeypatch.setattr(
        targeted,
        "push_intent",
        lambda root: pytest.fail("Tag pushes must not enter branch marker validation"),
    )
    output = tmp_path / "github-output"
    targeted.write_app_build_intent(output)
    assert output.read_text() == "mode=ordinary\n"


def test_build_test_accepts_branch_but_publish_requires_exact_main_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    revision = "a" * 40
    message = "Check JS [build-test-js]"
    event = tmp_path / "event.json"

    def write_event() -> None:
        event.write_text(
            json.dumps(
                {
                    "ref": "refs/heads/feature/js",
                    "deleted": False,
                    "head_commit": {"id": revision, "message": message},
                    "repository": {"full_name": "example/classroom"},
                }
            )
        )

    write_event()
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF": "refs/heads/feature/js",
        "GITHUB_REPOSITORY": "example/classroom",
        "GITHUB_SHA": revision,
        "GITHUB_EVENT_PATH": str(event),
    }.items():
        monkeypatch.setenv(key, value)

    def fake_git(root: Path, args: list[str]) -> str:
        if args[:1] == ["status"]:
            return ""
        if args[:1] == ["log"]:
            return message
        return revision

    monkeypatch.setattr(targeted, "git_output", fake_git)
    assert targeted.push_intent() == targeted.Intent(
        "build-test", "javascript-typescript", "[build-test-js]"
    )
    branch_output = tmp_path / "branch-output"
    targeted.write_app_build_intent(branch_output)
    assert branch_output.read_text() == "mode=build-test\n"
    message = "Release JS [publish-js]"
    write_event()
    with pytest.raises(ValueError, match="requires main"):
        targeted.push_intent()
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    with pytest.raises(ValueError, match="checked-out HEAD"):
        targeted.push_intent()
    monkeypatch.setenv("GITHUB_REF", "refs/heads/feature/js")
    for invalid_message in (
        "[publish-unknown]",
        "[build-test-js] [publish-js]",
        "[build-test-js",
    ):
        message = invalid_message
        write_event()
        with pytest.raises(ValueError):
            targeted.write_app_build_intent(tmp_path / "rejected-output")
        assert not (tmp_path / "rejected-output").exists()


def test_targeted_receipt_download_selects_only_seed_and_requested_group(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for key, value in {
        "GITHUB_REPOSITORY": "example/classroom",
        "GITHUB_SHA": "a" * 40,
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "2",
    }.items():
        monkeypatch.setenv(key, value)
    observed: list[str] = []

    def select(pages: Any, keys: list[str], attempt: int) -> list[release_artifacts.Artifact]:
        assert pages == [] and attempt == 2
        observed.extend(keys)
        return [
            release_artifacts.Artifact(key, 2, index + 1, key) for index, key in enumerate(keys)
        ]

    monkeypatch.setattr(release_artifacts, "gh", lambda args, maximum: b"[]")
    monkeypatch.setattr(release_artifacts, "select_artifacts", select)
    monkeypatch.setattr(release_artifacts, "receipt_bytes", lambda *args, **kwargs: b"{}")
    root = tmp_path / "source"
    root.mkdir()
    (root / "work").mkdir()
    # Group metadata is read from the maintained repository, while receipts are local.
    monkeypatch.setattr(targeted, "groups", lambda root: groups())
    targeted.download_receipts("javascript-typescript", root / "work/receipts", root)
    assert observed == [
        "seed-amd64",
        "seed-arm64",
        "javascript-typescript-amd64",
        "javascript-typescript-arm64",
    ]
    assert len(list((root / "work/receipts").glob("*/release-receipt.json"))) == 4
