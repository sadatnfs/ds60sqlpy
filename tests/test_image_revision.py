"""Bind classroom images to their source commit: verifier, launcher build args, Dockerfiles."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from scripts import verify_image_revision as verifier
from tests.test_classroom_launchers import RELEASE_VERSION, launcher  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
SHA = "0123456789abcdef0123456789abcdef01234567"
TAG = RELEASE_VERSION + "-p7deadbeef"
SOURCE_URL = "https://github.com/sadatnfs/ds60sqlpy"
WORKER_DOCKERFILES = sorted((ROOT / "docker/workers").glob("Dockerfile.*"))


def good_inspect(**overrides: Any) -> dict[str, Any]:
    labels = {
        verifier.REVISION: SHA,
        verifier.VERSION: RELEASE_VERSION,
        verifier.SOURCE: SOURCE_URL,
    }
    labels.update(overrides.pop("labels", {}))
    raw: dict[str, Any] = {
        "Id": "sha256:" + "a" * 64,
        "Os": "linux",
        "Architecture": "amd64",
        "Config": {"Labels": labels},
    }
    raw.update(overrides)
    return raw


class FakeDocker:
    def __init__(self, images: dict[str, dict[str, Any] | None], engine: str = "x86_64"):
        self.images = images
        self.engine = engine
        self.commands: list[list[str]] = []

    def __call__(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        args = list(command)
        self.commands.append(args)
        if args[:2] == ["docker", "info"]:
            return subprocess.CompletedProcess(args, 0, self.engine + "\n", "")
        assert args[:4] == ["docker", "image", "inspect", "--format"]
        raw = self.images.get(args[-1])
        if raw is None:
            return subprocess.CompletedProcess(args, 1, "", "No such image")
        return subprocess.CompletedProcess(args, 0, json.dumps(raw) + "\n", "")


def starter_images(core: dict[str, Any] | None = None) -> dict[str, dict[str, Any] | None]:
    return {
        f"ds60sqlpy-lab:{TAG}": good_inspect(),
        f"ds60sqlpy-worker-python-core:{TAG}": good_inspect() if core is None else core,
    }


def test_verifier_accepts_matching_labels_and_writes_report(tmp_path: Path) -> None:
    docker = FakeDocker(starter_images())
    report_path = tmp_path / "report.json"
    code = verifier.main(["--revision", SHA, "--tag", TAG, "--report", str(report_path)], docker)
    assert code == 0
    report = json.loads(report_path.read_text())
    assert report["passed"] is True and report["architecture"] == "amd64"
    assert report["schema_version"] == 1 and report["revision"] == SHA
    assert [image["profile"] for image in report["images"]] == ["app", "python-core"]
    for image in report["images"]:
        assert image["image_id"] == "sha256:" + "a" * 64 and image["errors"] == []
        assert image["labels"] == {
            "revision": SHA,
            "version": RELEASE_VERSION,
            "source": SOURCE_URL,
        }
    inspects = [c for c in docker.commands if c[:3] == ["docker", "image", "inspect"]]
    assert len(inspects) == 2


@pytest.mark.parametrize(
    ("core", "field"),
    [
        (good_inspect(labels={verifier.REVISION: ""}), "revision label is empty"),
        (good_inspect(labels={verifier.REVISION: SHA + "-dirty"}), "dirty tree"),
        (good_inspect(labels={verifier.REVISION: "f" * 40}), "revision label " + "f" * 40),
        (good_inspect(labels={verifier.VERSION: ""}), "version label"),
        (good_inspect(labels={verifier.SOURCE: "https://example.invalid"}), "source label"),
        (good_inspect(Architecture="arm64"), "architecture"),
        (good_inspect(Os="windows"), "operating system"),
        (None, "is missing"),
    ],
)
def test_verifier_rejects_each_bad_field(core: dict[str, Any] | None, field: str) -> None:
    images = starter_images()
    images[f"ds60sqlpy-worker-python-core:{TAG}"] = core
    report = verifier.verify(SHA, TAG, architecture="amd64", runner=FakeDocker(images))
    assert report["passed"] is False
    app, worker = report["images"]
    assert app["passed"] is True
    assert worker["passed"] is False
    assert any(e.startswith("python-core:") and field in e for e in worker["errors"])


def test_verifier_rejects_missing_labels_block() -> None:
    images = starter_images(
        core={"Id": "sha256:" + "b" * 64, "Os": "linux", "Architecture": "amd64"}
    )
    report = verifier.verify(SHA, TAG, architecture="amd64", runner=FakeDocker(images))
    errors = report["images"][1]["errors"]
    assert {"revision", "version", "source"} <= {
        field for field in ("revision", "version", "source") for e in errors if field in e
    }


@pytest.mark.parametrize("revision", ["", SHA[:12], SHA.upper(), SHA + "-dirty", "g" * 40])
def test_verifier_refuses_bad_revision_before_docker(revision: str, tmp_path: Path) -> None:
    docker = FakeDocker(starter_images())
    code = verifier.main(
        ["--revision", revision, "--tag", TAG, "--report", str(tmp_path / "r.json")], docker
    )
    assert code == 2 and docker.commands == [] and not (tmp_path / "r.json").exists()


def test_verifier_refuses_bad_tag_unknown_and_gpu_profiles() -> None:
    docker = FakeDocker(starter_images())
    with pytest.raises(verifier.VerificationError):
        verifier.verify(SHA, "latest", runner=docker)
    with pytest.raises(verifier.VerificationError, match="Unknown"):
        verifier.verify(SHA, TAG, ["not-a-profile"], runner=docker)
    with pytest.raises(verifier.VerificationError, match="GPU"):
        verifier.verify(SHA, TAG, ["cuda-python"], runner=docker)
    assert docker.commands == []


def test_verifier_maps_engine_architecture_and_always_includes_app() -> None:
    docker = FakeDocker(
        {
            f"ds60sqlpy-lab:{TAG}": good_inspect(Architecture="arm64"),
            f"ds60sqlpy-worker-go:{TAG}": good_inspect(Architecture="arm64"),
        },
        engine="aarch64",
    )
    report = verifier.verify(SHA, TAG, ["go"], runner=docker)
    assert report["passed"] is True and report["architecture"] == "arm64"
    assert [image["profile"] for image in report["images"]] == ["app", "go"]


def build_rows(calls: list[dict[str, Any]]) -> list[list[str]]:
    return [call["args"] for call in calls if "build" in call["args"]]


def build_arg(args: list[str], name: str) -> str:
    values = [
        args[i + 1][len(name) + 1 :]
        for i, value in enumerate(args[:-1])
        if value == "--build-arg" and args[i + 1].startswith(name + "=")
    ]
    assert len(values) == 1, args
    return values[0]


def run_build(harness: Any) -> list[list[str]]:
    result = harness.run("build", "--starter", "--local-build", "--tag", TAG, "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    rows = build_rows(harness.calls())
    assert len(rows) == 3, rows
    assert any(row[0] == "build" for row in rows), "python-core uses docker build"
    compose_targets = sorted(row[-1] for row in rows if row[0] == "compose")
    # The DS60 database image is built locally like the app (it is not pulled).
    assert compose_targets == ["lab", "postgres"], rows
    for row in rows:
        assert build_arg(row, "DS60_RELEASE_VERSION") == RELEASE_VERSION
    return rows


def git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", *args],
        cwd=directory,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_launcher_without_own_repository_passes_empty_revision(launcher: Any) -> None:  # noqa: F811
    launcher.set(missing_images=True)
    rows = run_build(launcher)
    assert all(build_arg(row, "DS60_SOURCE_REVISION") == "" for row in rows)


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_launcher_passes_clean_then_dirty_revision(launcher: Any) -> None:  # noqa: F811
    root = launcher.directory
    (root / ".gitignore").write_text(".classroom/\n")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    sha = git(root, "rev-parse", "HEAD")
    assert re.fullmatch(r"[0-9a-f]{40}", sha)
    launcher.set(missing_images=True)
    rows = run_build(launcher)
    assert all(build_arg(row, "DS60_SOURCE_REVISION") == sha for row in rows)

    (root / "pyproject.toml").write_text((root / "pyproject.toml").read_text() + "\n# edit\n")
    (launcher.config.parent / "calls.jsonl").unlink()
    launcher.set(missing_images=True)
    rows = run_build(launcher)
    assert all(build_arg(row, "DS60_SOURCE_REVISION") == sha + "-dirty" for row in rows)


def final_stage(path: Path) -> str:
    text = path.read_text()
    starts = [m.start() for m in re.finditer(r"^FROM\s", text, re.M)]
    assert starts, path
    return text[starts[-1] :]


def instructions(stage: str) -> list[str]:
    joined = re.sub(r"\\\n", " ", stage)
    return [
        line.strip()
        for line in joined.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


@pytest.mark.parametrize("path", [ROOT / "Dockerfile", *WORKER_DOCKERFILES], ids=lambda p: p.name)
def test_revision_arg_and_label_close_the_final_stage(path: Path) -> None:
    lines = instructions(final_stage(path))
    arg = 'ARG DS60_SOURCE_REVISION=""'
    assert arg in lines, path
    tail = lines[lines.index(arg) :]
    assert tail[-1].startswith("LABEL "), tail
    assert all(line.split()[0] in {"ARG", "LABEL"} for line in tail), tail
    assert 'org.opencontainers.image.revision="${DS60_SOURCE_REVISION}"' in tail[-1]


@pytest.mark.parametrize("path", WORKER_DOCKERFILES, ids=lambda p: p.name)
def test_worker_label_sets_revision_version_and_source(path: Path) -> None:
    lines = instructions(final_stage(path))
    assert 'ARG DS60_RELEASE_VERSION=""' in lines, path
    label = lines[-1]
    assert 'org.opencontainers.image.version="${DS60_RELEASE_VERSION}"' in label
    assert f'org.opencontainers.image.source="{SOURCE_URL}"' in label


def test_root_dockerfile_has_no_empty_literal_revision() -> None:
    text = (ROOT / "Dockerfile").read_text()
    assert 'org.opencontainers.image.revision=""' not in text
    assert 'org.opencontainers.image.version="' + RELEASE_VERSION + '"' in text


def test_every_worker_dockerfile_is_covered() -> None:
    assert len(WORKER_DOCKERFILES) == 22


def test_planning_notes_never_enter_the_build_context() -> None:
    entries = [line.strip() for line in (ROOT / ".dockerignore").read_text().splitlines()]
    assert ".planning" in entries
