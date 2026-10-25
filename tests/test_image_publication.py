"""Test manual publication gates and artifact handoff without Docker or network writes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml", reason="Workflow contract parsing requires PyYAML.")
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-images.yml"
REVISION = "a" * 40
IMAGE_ID = "sha256:" + "d" * 64


def workflow() -> dict[str, Any]:
    # BaseLoader retains the YAML key "on" and boolean input defaults as strings.
    result: dict[str, Any] = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)
    return result


def step(job: str, name: str) -> dict[str, Any]:
    result: dict[str, Any] = next(
        item for item in workflow()["jobs"][job]["steps"] if item.get("name") == name
    )
    return result


def python_block(job: str, name: str) -> str:
    script: str = step(job, name)["run"]
    return script.split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]


def execute_block(job: str, name: str) -> None:
    exec(compile(python_block(job, name), f"{job}:{name}", "exec"), {"__name__": "__main__"})


GATE = "Check version, bounded inputs and exact-revision CI"
EXPORT = "Export the tested immutable image and platform metadata"
DOWNLOAD = "Download only this workflow run's qualified image"
VERIFY = "Verify archive, provenance, immutable ID and platform before login"


@pytest.fixture
def publication(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docker").mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.4.0"\n')
    (tmp_path / "docker/classroom-images.tsv").write_text(
        "# profile service repository suffix variable kind\n"
        "app lab ds60sqlpy-lab lab DS60_LAB_IMAGE app\n"
        "python-core python-core-worker ds60sqlpy-worker-python-core "
        "worker-python-core DS60_WORKER_PYTHON_CORE_IMAGE ordinary\n"
        "cuda-python cuda-python-worker ds60sqlpy-worker-cuda-python "
        "worker-cuda-python DS60_WORKER_CUDA_PYTHON_IMAGE gpu\n"
    )
    values = {
        "PROFILE": "python-core",
        "RELEASE_VERSION": "0.4.0",
        "ARCHITECTURE": "amd64",
        "HUB_USER": "exampleuser",
        "REPOSITORY": "exampleuser/classroom",
        "REVISION": REVISION,
        "RUN_ID": "12345",
        "RUN_ATTEMPT": "2",
        "ARTIFACT_ATTEMPT": "2",
        "PUBLISH": "false",
        "ENABLED": "",
        "GITHUB_OUTPUT": str(tmp_path / "github-output"),
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return tmp_path


def successful_runs() -> list[dict[str, Any]]:
    return [
        {
            "id": index,
            "run_attempt": 1,
            "path": path,
            "name": "Display names are intentionally irrelevant",
            "event": "push",
            "head_branch": "main",
            "head_sha": REVISION,
            "status": "completed",
            "conclusion": "success",
        }
        for index, path in enumerate(
            [".github/workflows/ci.yml", ".github/workflows/app-build.yml"], 1
        )
    ]


def mock_runs(monkeypatch: pytest.MonkeyPatch, runs: list[dict[str, Any]]) -> None:
    def output(args: list[str], **kwargs: Any) -> bytes:
        assert args[:4] == ["gh", "api", "--paginate", "--slurp"]
        assert args[-1].startswith("repos/exampleuser/classroom/actions/runs?")
        assert "head_sha=" + REVISION in args[-1]
        return json.dumps([{"workflow_runs": runs}]).encode()

    monkeypatch.setattr(subprocess, "check_output", output)


def test_manual_publish_requires_all_image_jobs_and_keeps_credentials_out_of_builds() -> None:
    data = workflow()
    assert set(data["on"]) == {"workflow_dispatch"}
    assert data["on"]["workflow_dispatch"]["inputs"]["publish"]["default"] == "false"
    assert data["permissions"] == {"contents": "read", "actions": "read"}
    jobs = data["jobs"]
    assert set(jobs) == {"gate", "images", "publish"}
    assert jobs["gate"]["if"] == "github.ref == 'refs/heads/main'"
    assert jobs["images"]["needs"] == "gate"
    assert jobs["publish"]["needs"] == ["gate", "images"]
    condition = jobs["publish"]["if"]
    assert "inputs.publish" in condition
    assert "needs.gate.result == 'success'" in condition
    assert "needs.images.result == 'success'" in condition
    assert "environment" not in jobs["images"]
    assert jobs["publish"]["environment"] == "dockerhub"
    assert "DOCKERHUB_TOKEN" not in json.dumps(jobs["gate"])
    assert "DOCKERHUB_TOKEN" not in json.dumps(jobs["images"])
    assert "docker login" not in json.dumps(jobs["images"])
    assert "--push" not in json.dumps(jobs["images"])
    checks = step("images", "Build and exercise this image through the classroom")["run"]
    assert '--report "work/runtime-receipts-$PROFILE.json"' in checks
    names = [item.get("name") for item in jobs["publish"]["steps"]]
    assert names.index(VERIFY) < names.index("Authenticate to Docker Hub after every image passed")
    assert names.index("Authenticate to Docker Hub after every image passed") < names.index(
        "Publish the verified native architecture image"
    )
    assert (
        "--password-stdin"
        in step("publish", "Authenticate to Docker Hub after every image passed")["run"]
    )
    for job in jobs.values():
        checkout = next(
            item for item in job["steps"] if item.get("uses", "").startswith("actions/checkout@")
        )
        assert checkout["with"]["ref"] == "${{ github.sha }}"
        assert checkout["with"]["persist-credentials"] == "false"


def test_dry_run_has_no_image_export_upload_or_login_and_archives_expire_in_one_day() -> None:
    export = step("images", EXPORT)
    upload = step("images", "Retain the checked image for the gated publish phase")
    assert export["if"] == upload["if"] == "inputs.publish"
    assert upload["with"]["retention-days"] == "1"
    assert upload["with"]["compression-level"] == "0"
    assert upload["with"]["if-no-files-found"] == "error"
    assert upload["with"]["path"].split() == [
        "work/release-image/image.tar",
        "work/release-image/metadata.json",
    ]
    assert "github.run_attempt" in upload["with"]["name"]
    assert "actions/download-artifact" not in WORKFLOW.read_text()
    assert "actions: write" not in WORKFLOW.read_text()


def test_exact_path_main_revision_gate_builds_only_the_ordinary_matrix(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_runs(monkeypatch, successful_runs())
    execute_block("gate", GATE)
    saved = (publication / "github-output").read_text().removeprefix("matrix=")
    assert json.loads(saved) == {"include": [{"profile": "app"}, {"profile": "python-core"}]}


@pytest.mark.parametrize(
    "field,value",
    [
        ("path", ".github/workflows/pretend-ci.yml"),
        ("event", "workflow_dispatch"),
        ("head_branch", "feature"),
        ("head_sha", "b" * 40),
    ],
)
def test_gate_rejects_success_from_wrong_workflow_event_branch_or_revision(
    publication: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: str
) -> None:
    runs = successful_runs()
    runs[0][field] = value
    mock_runs(monkeypatch, runs)
    with pytest.raises(AssertionError, match="No main-branch push qualification"):
        execute_block("gate", GATE)
    assert not (publication / "github-output").exists()


@pytest.mark.parametrize("suffix", ["@main", "@refs/heads/main", "@" + REVISION])
def test_gate_accepts_only_documented_main_or_exact_revision_workflow_path_suffixes(
    publication: Path, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    runs = successful_runs()
    for run in runs:
        run["path"] += suffix
    mock_runs(monkeypatch, runs)
    execute_block("gate", GATE)
    assert (publication / "github-output").is_file()


def test_gate_rejects_a_different_workflow_source_ref(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = successful_runs()
    runs[0]["path"] += "@unreviewed"
    mock_runs(monkeypatch, runs)
    with pytest.raises(AssertionError, match="No main-branch push qualification"):
        execute_block("gate", GATE)


def test_latest_matching_ci_failure_blocks_an_older_success(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = successful_runs()
    runs.append({**runs[0], "run_attempt": 2, "conclusion": "failure"})
    mock_runs(monkeypatch, runs)
    with pytest.raises(AssertionError, match="not successful"):
        execute_block("gate", GATE)


@pytest.mark.parametrize(
    "key,value", [("ARCHITECTURE", "s390x"), ("PUBLISH", "yes"), ("RELEASE_VERSION", "latest")]
)
def test_invalid_release_inputs_fail_before_api_access(
    publication: Path, monkeypatch: pytest.MonkeyPatch, key: str, value: str
) -> None:
    monkeypatch.setenv(key, value)
    monkeypatch.setattr(
        subprocess, "check_output", lambda *a, **k: pytest.fail("No API call expected")
    )
    with pytest.raises(AssertionError):
        execute_block("gate", GATE)


def test_publish_true_requires_deliberate_repository_enable_flag(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PUBLISH", "true")
    monkeypatch.setattr(
        subprocess, "check_output", lambda *a, **k: pytest.fail("No API call expected")
    )
    with pytest.raises(AssertionError, match="Publishing is disabled"):
        execute_block("gate", GATE)


def test_export_saves_the_inspected_immutable_id_and_hashes_actual_bytes(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved: list[list[str]] = []

    def output(args: list[str], **kwargs: Any) -> str | bytes:
        if args == ["git", "rev-parse", "HEAD"]:
            return REVISION + "\n"
        assert args[-1] == "ds60sqlpy-worker-python-core:0.4.0"
        return json.dumps({"Id": IMAGE_ID, "Os": "linux", "Architecture": "amd64"}).encode()

    def run(args: list[str], **kwargs: Any) -> None:
        saved.append(args)
        assert args == [
            "docker",
            "image",
            "save",
            "--output",
            "work/release-image/image.tar",
            IMAGE_ID,
        ]
        Path(args[4]).write_bytes(b"bounded fake image archive")

    monkeypatch.setattr(subprocess, "check_output", output)
    monkeypatch.setattr(subprocess, "run", run)
    execute_block("images", EXPORT)
    metadata = json.loads((publication / "work/release-image/metadata.json").read_text())
    assert metadata["image_id"] == IMAGE_ID
    assert metadata["run_id"] == "12345" and metadata["run_attempt"] == "2"
    assert metadata["archive_sha256"] == hashlib.sha256(b"bounded fake image archive").hexdigest()
    assert metadata["archive_bytes"] == len(b"bounded fake image archive")
    assert len(saved) == 1


def test_download_selects_latest_unexpired_attempt_from_the_exact_run(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifacts = [
        {"name": "qualified-image-python-core-amd64-attempt-1", "expired": False},
        {"name": "qualified-image-python-core-amd64-attempt-2", "expired": False},
        {"name": "qualified-image-python-core-amd64-attempt-3", "expired": False},
        {"name": "qualified-image-python-core-arm64-attempt-2", "expired": False},
        {"name": "qualified-image-app-amd64-attempt-2", "expired": False},
    ]
    calls: list[list[str]] = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        assert args == [
            "gh",
            "api",
            "--paginate",
            "--slurp",
            "repos/exampleuser/classroom/actions/runs/12345/artifacts?per_page=100",
        ]
        return json.dumps([{"artifacts": artifacts}]).encode()

    def run(args: list[str], **kwargs: Any) -> None:
        calls.append(args)

    monkeypatch.setattr(subprocess, "check_output", output)
    monkeypatch.setattr(subprocess, "run", run)
    execute_block("publish", DOWNLOAD)
    assert calls == [
        [
            "gh",
            "run",
            "download",
            "12345",
            "--repo",
            "exampleuser/classroom",
            "--name",
            "qualified-image-python-core-amd64-attempt-2",
            "--dir",
            "work/checked-image",
        ]
    ]
    assert (publication / "github-output").read_text() == "attempt=2\n"


@pytest.mark.parametrize(
    "artifacts",
    [
        [],
        [{"name": "qualified-image-python-core-amd64-attempt-2", "expired": True}],
        [
            {"name": "qualified-image-python-core-amd64-attempt-2", "expired": False},
            {"name": "qualified-image-python-core-amd64-attempt-2", "expired": False},
        ],
    ],
)
def test_missing_expired_or_ambiguous_artifact_never_downloads(
    publication: Path, monkeypatch: pytest.MonkeyPatch, artifacts: list[dict[str, Any]]
) -> None:
    monkeypatch.setattr(
        subprocess, "check_output", lambda *a, **k: json.dumps([{"artifacts": artifacts}]).encode()
    )
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("No download expected"))
    with pytest.raises(AssertionError):
        execute_block("publish", DOWNLOAD)


def checked_archive(publication: Path) -> tuple[Path, dict[str, Any]]:
    folder = publication / "work/checked-image"
    folder.mkdir(parents=True)
    payload = b"small checked image fixture"
    (folder / "image.tar").write_bytes(payload)
    metadata = {
        "schema_version": 1,
        "repository": "exampleuser/classroom",
        "revision": REVISION,
        "run_id": "12345",
        "run_attempt": "2",
        "profile": "python-core",
        "release_version": "0.4.0",
        "namespace": "exampleuser",
        "source_image": "ds60sqlpy-worker-python-core:0.4.0",
        "image_id": IMAGE_ID,
        "os": "linux",
        "architecture": "amd64",
        "archive_sha256": hashlib.sha256(payload).hexdigest(),
        "archive_bytes": len(payload),
    }
    (folder / "metadata.json").write_text(json.dumps(metadata))
    return folder, metadata


def test_verified_handoff_loads_then_checks_identity_before_restoring_local_tag(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checked_archive(publication)
    calls: list[list[str]] = []

    def run(args: list[str], **kwargs: Any) -> None:
        calls.append(args)

    def output(args: list[str], **kwargs: Any) -> bytes:
        calls.append(args)
        assert args[-1] == IMAGE_ID
        return json.dumps({"Id": IMAGE_ID, "Os": "linux", "Architecture": "amd64"}).encode()

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", output)
    execute_block("publish", VERIFY)
    assert calls[0] == ["docker", "image", "load", "--input", "work/checked-image/image.tar"]
    assert calls[1][:3] == ["docker", "image", "inspect"]
    assert calls[2] == ["docker", "image", "tag", IMAGE_ID, "ds60sqlpy-worker-python-core:0.4.0"]
    assert not any("push" in call or "login" in call for call in calls)


@pytest.mark.parametrize(
    "field,value",
    [
        ("repository", "someone/else"),
        ("revision", "b" * 40),
        ("run_id", "98765"),
        ("run_attempt", "1"),
        ("profile", "app"),
        ("release_version", "0.3.0"),
        ("namespace", "elsewhere"),
        ("architecture", "arm64"),
        ("os", "windows"),
        ("source_image", "unrelated:0.4.0"),
        ("image_id", "mutable-tag"),
        ("archive_sha256", "0" * 64),
        ("archive_bytes", 1),
    ],
)
def test_artifact_identity_or_integrity_mismatch_refuses_docker_load(
    publication: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: Any
) -> None:
    folder, metadata = checked_archive(publication)
    metadata[field] = value
    (folder / "metadata.json").write_text(json.dumps(metadata))
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: pytest.fail("Must reject before Docker load")
    )
    monkeypatch.setattr(
        subprocess, "check_output", lambda *a, **k: pytest.fail("Must reject before Docker inspect")
    )
    with pytest.raises(AssertionError):
        execute_block("publish", VERIFY)


def test_changed_archive_bytes_refuse_docker_load(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder, _ = checked_archive(publication)
    payload = (folder / "image.tar").read_bytes()
    (folder / "image.tar").write_bytes(b"X" + payload[1:])
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("No Docker call expected"))
    with pytest.raises(AssertionError, match="SHA-256 mismatch"):
        execute_block("publish", VERIFY)


def test_loaded_image_platform_mismatch_prevents_tagging(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checked_archive(publication)
    calls: list[list[str]] = []
    monkeypatch.setattr(subprocess, "run", lambda args, **k: calls.append(args))
    monkeypatch.setattr(
        subprocess,
        "check_output",
        lambda *a, **k: json.dumps(
            {"Id": IMAGE_ID, "Os": "linux", "Architecture": "arm64"}
        ).encode(),
    )
    with pytest.raises(AssertionError, match="Loaded image identity/platform mismatch"):
        execute_block("publish", VERIFY)
    assert len(calls) == 1 and calls[0][:3] == ["docker", "image", "load"]


def test_duplicate_metadata_fields_and_symlinked_payloads_refuse_loading(
    publication: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder, metadata = checked_archive(publication)
    metadata_text = json.dumps(metadata)
    (folder / "metadata.json").write_text(metadata_text[:-1] + ', "profile": "python-core"}')
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("No Docker call expected"))
    with pytest.raises(AssertionError, match="Duplicate artifact metadata field"):
        execute_block("publish", VERIFY)
    (folder / "metadata.json").write_text(metadata_text)
    archive = folder / "image.tar"
    archive.rename(publication / "actual-image.tar")
    archive.symlink_to(publication / "actual-image.tar")
    with pytest.raises(AssertionError):
        execute_block("publish", VERIFY)
