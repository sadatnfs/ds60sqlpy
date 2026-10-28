"""Published-tag pull acceptance remains separate from promotion evidence."""

from __future__ import annotations

import io
import json
import subprocess
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from scripts import ci_hub_acceptance as hub
from scripts import ci_release_artifacts as artifacts
from scripts.docker_registry import OCI_MANIFEST, Descriptor, ReleaseError, descriptor, sha256
from scripts.docker_release import Context, catalog, index_body, latest_tag, version_tag

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40


def context() -> Context:
    return Context(
        namespace="example",
        repository="example/ds60sqlpy",
        source_repository="example/classroom",
        version="1.0.0",
        revision=REVISION,
        run_id="12345",
        run_attempt="2",
    )


def receipt(mode: str, *, skipped_latest: bool = False) -> tuple[dict[str, Any], dict[str, bytes]]:
    current = context()
    profiles = catalog(ROOT)
    selected = (
        {"app", "python-core", "javascript-node", "typescript-node"}
        if mode == "partial"
        else set(profiles)
    )
    group = "javascript-typescript" if mode == "partial" else None
    bodies = {}
    version_rows = []
    latest_rows = []
    for key in [item for item in profiles if item in selected and item != "app"] + ["app"]:
        natives = {
            "amd64": Descriptor(OCI_MANIFEST, "sha256:" + "1" * 64, 128),
            "arm64": Descriptor(OCI_MANIFEST, "sha256:" + "2" * 64, 128),
        }
        body = index_body(current, key, natives, target_group=group)
        immutable = version_tag(profiles[key], current.version)
        alias = latest_tag(profiles[key])
        bodies[immutable] = body
        bodies[alias] = body
        fields = {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": sha256(body),
            "size": len(body),
        }
        version_rows.append({"tag": immutable, **fields})
        if not skipped_latest:
            latest_rows.append({"tag": alias, **fields})
    value: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-release-promotion",
        "context": asdict(current),
        "status": "published",
        "version_tags": version_rows,
        "latest_tags": latest_rows,
        "latest_skipped_newer_release": skipped_latest,
    }
    if group is not None:
        value.update({"scope": "partial", "group": group, "profiles": sorted(selected)})
    return value, bodies


def github_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": "example/classroom",
        "GITHUB_SHA": REVISION,
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "2",
        "DOCKERHUB_USERNAME": "example",
    }.items():
        monkeypatch.setenv(key, value)


def test_workflows_keep_promotion_and_native_pull_acceptance_distinct() -> None:
    yaml = pytest.importorskip("yaml")
    for name, mode in (("targeted-images.yml", "partial"), ("publish-images.yml", "full")):
        workflow = yaml.load(
            (ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader
        )
        jobs = workflow["jobs"]
        acceptance = jobs["hub-acceptance"]
        assert "promote" in acceptance["needs"]
        assert "needs.promote.result == 'success'" in acceptance["if"]
        assert {
            row["architecture"]: row["runner"]
            for row in acceptance["strategy"]["matrix"]["include"]
        } == {"amd64": "ubuntu-24.04", "arm64": "ubuntu-24.04-arm"}
        steps = acceptance["steps"]
        assert f"fetch --mode {mode}" in json.dumps(steps)
        assert f"accept --mode {mode}" in json.dumps(steps)
        assert "work/hub-acceptance-diagnostics.json" in json.dumps(steps[-1])
        assert steps[-1]["if"] == "always()"
        assert "secrets.DOCKERHUB_TOKEN" not in json.dumps(steps[:-2])
    targeted = yaml.load(
        (ROOT / ".github/workflows/targeted-images.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert "needs.intent.outputs.mode == 'publish'" in targeted["jobs"]["hub-acceptance"]["if"]


def test_fetch_receipt_uses_latest_published_attempt_from_exact_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    github_environment(monkeypatch)
    value, _ = receipt("partial")
    document = json.dumps(value).encode()
    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("release.json", document)
    pages = [
        {
            "artifacts": [
                {
                    "name": "published-targeted-release-attempt-1",
                    "id": 10,
                    "expired": False,
                    "size_in_bytes": 100,
                },
                {
                    "name": "published-targeted-release-attempt-2",
                    "id": 11,
                    "expired": False,
                    "size_in_bytes": 100,
                },
                {
                    "name": "published-release-attempt-2",
                    "id": 12,
                    "expired": False,
                    "size_in_bytes": 100,
                },
            ]
        }
    ]

    def gh(args: list[str], *, maximum: int) -> bytes:
        if "artifacts?per_page=100" in args[-1]:
            return json.dumps(pages).encode()
        assert args[-1].endswith("/11/zip")
        return bundle.getvalue()

    monkeypatch.setattr(artifacts, "gh", gh)
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    target = root / "work/release.json"
    assert hub.fetch_receipt("partial", target, root)["status"] == "published"
    assert target.read_bytes() == document


def test_fetch_receipt_rejects_stage_or_wrong_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    github_environment(monkeypatch)
    value, _ = receipt("partial")
    value["context"]["revision"] = "b" * 40
    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("release.json", json.dumps(value))
    pages = [
        {
            "artifacts": [
                {
                    "name": "published-targeted-release-attempt-2",
                    "id": 11,
                    "expired": False,
                    "size_in_bytes": 100,
                }
            ]
        }
    ]
    monkeypatch.setattr(
        artifacts,
        "gh",
        lambda args, maximum: (
            json.dumps(pages).encode()
            if "artifacts?per_page=100" in args[-1]
            else bundle.getvalue()
        ),
    )
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    with pytest.raises(ReleaseError, match="published run"):
        hub.fetch_receipt("partial", root / "work/release.json", root)
    assert not (root / "work/release.json").exists()


def test_partial_index_inspection_checks_every_selected_version_and_latest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, bodies = receipt("partial")
    monkeypatch.setattr(
        hub,
        "release_selection",
        lambda receipt, mode, root: (
            context(),
            catalog(ROOT),
            set(value["profiles"]),
            "javascript-typescript",
            False,
        ),
    )
    seen: list[str] = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        tag = args[-1].split(":", 1)[1]
        seen.append(tag)
        return bodies[tag]

    monkeypatch.setattr(hub, "run_output", output)
    current, _, selected, group, skipped = hub.verify_indexes(value, "partial")
    assert current == context() and group == "javascript-typescript" and not skipped
    assert selected == set(value["profiles"])
    assert set(seen) == set(bodies)
    assert len(seen) == 8


def test_index_inspection_rejects_content_swap_and_wrong_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, bodies = receipt("partial")
    tag = "1.0.0"
    expected = descriptor(value["version_tags"][-1])
    monkeypatch.setattr(hub, "run_output", lambda *args, **kwargs: bodies[tag] + b"tampered")
    with pytest.raises(ReleaseError, match="content differs"):
        hub.inspect_index(
            "example/ds60sqlpy:" + tag, expected, "app", context(), "javascript-typescript"
        )
    monkeypatch.setattr(hub, "run_output", lambda *args, **kwargs: bodies[tag])
    with pytest.raises(ReleaseError, match="partial version tag"):
        hub.inspect_index("example/ds60sqlpy:" + tag, expected, "app", context(), None)


def test_skipped_latest_checks_only_immutable_version_indexes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, bodies = receipt("partial", skipped_latest=True)
    monkeypatch.setattr(
        hub,
        "release_selection",
        lambda receipt, mode, root: (
            context(),
            catalog(ROOT),
            set(value["profiles"]),
            "javascript-typescript",
            True,
        ),
    )
    seen: list[str] = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        tag = args[-1].split(":", 1)[1]
        seen.append(tag)
        return bodies[tag]

    monkeypatch.setattr(hub, "run_output", output)
    hub.verify_indexes(value, "partial")
    assert len(seen) == 4 and all(tag.startswith("1.0.0") for tag in seen)


def test_full_publication_inspects_every_ordinary_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, bodies = receipt("full")
    monkeypatch.setattr(
        hub,
        "release_selection",
        lambda receipt, mode, root: (context(), catalog(ROOT), set(catalog(ROOT)), None, False),
    )
    seen: list[str] = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        tag = args[-1].split(":", 1)[1]
        seen.append(tag)
        return bodies[tag]

    monkeypatch.setattr(hub, "run_output", output)
    hub.verify_indexes(value, "full")
    assert len(seen) == len(catalog(ROOT)) * 2
    assert set(seen) == set(bodies)


def test_full_arm_validates_complete_receipt_but_inspects_only_app_and_core(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value, bodies = receipt("full")
    monkeypatch.setattr(
        hub,
        "release_selection",
        lambda receipt, mode, root: (context(), catalog(ROOT), set(catalog(ROOT)), None, False),
    )
    seen: list[str] = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        tag = args[-1].split(":", 1)[1]
        seen.append(tag)
        return bodies[tag]

    monkeypatch.setattr(hub, "run_output", output)
    hub.verify_indexes(value, "full", architecture="arm64")
    profiles = catalog(ROOT)
    assert set(seen) == {
        version_tag(profiles[key], context().version) for key in ("app", "python-core")
    } | {latest_tag(profiles[key]) for key in ("app", "python-core")}
    assert len(value["version_tags"]) == len(profiles)
    value["version_tags"] = value["version_tags"][:-1]
    with pytest.raises(ReleaseError, match="incomplete selected tag coverage"):
        hub.verify_indexes(value, "full", architecture="arm64")


def test_disposable_cleanup_refuses_unowned_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = "ds60-hub-amd64-12345-2"
    monkeypatch.setattr(hub, "docker_items", lambda kind, project, root: ["abc123"])
    monkeypatch.setattr(hub, "run_output", lambda *args, **kwargs: b"unrelated\n")
    seen: list[list[str]] = []
    monkeypatch.setattr(hub, "run_visible", lambda args, **kwargs: seen.append(args))
    with pytest.raises(ReleaseError, match="outside the owned project"):
        hub.cleanup_project(project)
    assert seen == []


def test_disposable_cleanup_checks_container_label_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = "ds60-hub-arm64-12345-2"
    monkeypatch.setattr(hub, "docker_items", lambda kind, project, root: ["abc123"])
    formats: list[str] = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        formats.append(args[4])
        return (project + "\n").encode()

    monkeypatch.setattr(hub, "run_output", output)
    seen: list[list[str]] = []
    monkeypatch.setattr(hub, "run_visible", lambda args, **kwargs: seen.append(args))
    hub.cleanup_project(project)
    assert ".Config.Labels" in formats[0]
    assert formats[1:] == ['{{index .Labels "com.docker.compose.project"}}'] * 2
    assert len(seen) == 1 and seen[0][-4:] == ["--volumes", "--remove-orphans", "--timeout", "20"]


def test_partial_hub_start_resolves_latest_and_checks_app_worker_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    github_environment(monkeypatch)
    root = tmp_path / "repo"
    root.mkdir()
    (root / "docker").mkdir()
    (root / "docker/classroom-images.tsv").write_bytes(
        (ROOT / "docker/classroom-images.tsv").read_bytes()
    )
    monkeypatch.setattr(hub, "group_profiles", lambda *args: ["javascript-node", "typescript-node"])
    monkeypatch.setattr(hub, "assert_new_project", lambda *args: None)
    monkeypatch.setattr(hub, "read_selection", lambda *args: None)
    monkeypatch.setattr(
        hub,
        "docker_items",
        lambda kind, project, root: ["learning", "database"] if kind == "volume" else [],
    )
    services: list[str] = []

    def compose_id(project: str, service: str, root: Path) -> str:
        services.append(service)
        return service + "-id"

    monkeypatch.setattr(hub, "compose_ids", compose_id)
    commands: list[list[str]] = []
    monkeypatch.setattr(hub, "run_visible", lambda args, **kwargs: commands.append(args))
    monkeypatch.setattr(
        hub, "cleanup_project", lambda project, root: commands.append(["cleanup", project])
    )
    result = hub.launch_and_resume(
        context(), "partial", "javascript-typescript", False, "amd64", root / "work/diag.txt", root
    )
    assert result["stop_resume_same_containers"] is True
    assert (
        "--profile" in commands[0]
        and "javascript-node" in commands[0]
        and "typescript-node" in commands[0]
    )
    assert "javascript-node=latest" in commands[0]
    assert services.count("lab") == 2 and services.count("postgres") == 2
    assert commands[1][:3] == ["bash", "classroom", "stop"]
    assert commands[2][:3] == ["bash", "classroom", "resume"]
    assert commands[3][0] == "cleanup"


def test_failed_start_retains_diagnostics_before_owned_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    github_environment(monkeypatch)
    monkeypatch.setattr(hub, "assert_new_project", lambda *args: None)
    actions: list[str] = []

    def fail_start(*args: Any, **kwargs: Any) -> None:
        actions.append("start")
        raise ReleaseError("synthetic startup failure")

    monkeypatch.setattr(hub, "run_visible", fail_start)
    monkeypatch.setattr(hub, "save_diagnostics", lambda *args: actions.append("diagnostics"))
    monkeypatch.setattr(hub, "cleanup_project", lambda *args: actions.append("cleanup"))
    with pytest.raises(ReleaseError, match="synthetic startup failure"):
        hub.launch_and_resume(
            context(), "full", None, False, "amd64", tmp_path / "work/diag.txt", tmp_path
        )
    assert actions == ["start", "diagnostics", "cleanup"]


def test_sensitive_env_is_removed_from_child_processes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCKERHUB_TOKEN", "private")
    monkeypatch.setenv("GH_TOKEN", "private-gh")
    monkeypatch.setenv("DOCKER_DEFAULT_PLATFORM", "linux/amd64")
    monkeypatch.setenv("DOCKER_CONFIG", "/tmp/ci-docker-config")
    child = hub.environment()
    assert "DOCKERHUB_TOKEN" not in child and "GH_TOKEN" not in child
    assert "DOCKER_DEFAULT_PLATFORM" not in child
    assert child["DOCKER_CONFIG"] == "/tmp/ci-docker-config"


def test_diagnostics_redact_token_before_bounded_export(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    monkeypatch.setenv("DOCKERHUB_TOKEN", "secret-token-value")

    def completed(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            args,
            0,
            stdout=b"x" * 23_997
            + b"secret-token-value\nAuthorization: Bearer secret-token-value\n",
            stderr=b"",
        )

    monkeypatch.setattr(subprocess, "run", completed)
    target = root / "work/hub-acceptance-diagnostics.json"
    hub.save_diagnostics("ds60-hub-amd64-12345-2", target, root)
    document = json.loads(target.read_text())
    assert document["kind"] == "ds60-hub-diagnostics"
    assert "secret-token-value" not in target.read_text()
    assert "Authorization: [redacted]" not in target.read_text()
    assert all(len(section) <= 24_100 for section in document["sections"])
