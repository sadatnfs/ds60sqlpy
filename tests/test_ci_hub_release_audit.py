"""Exact published-source and selective canonical-image audit boundaries."""

from __future__ import annotations

import io
import json
import stat
import subprocess
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from scripts import ci_hub_acceptance as hub
from scripts import ci_hub_release_audit as audit
from scripts import ci_hub_reverify as recovery
from scripts import ci_profiles
from scripts import ci_release_artifacts as artifacts
from scripts.docker_registry import OCI_MANIFEST, Descriptor, ReleaseError, sha256
from scripts.docker_release import Context, catalog, index_body, latest_tag, version_tag, write_json

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = "a" * 40
CURRENT = "b" * 40


def request() -> recovery.Request:
    return recovery.Request("example/classroom", CURRENT, "12345", "2", PUBLISHED, "10000", "1")


def context() -> Context:
    return Context(
        "example", "example/ds60sqlpy", "example/classroom", "1.1.0", PUBLISHED, "10000", "1"
    )


def full_receipt() -> tuple[dict[str, Any], dict[str, bytes]]:
    value: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-release-promotion",
        "context": asdict(context()),
        "status": "published",
        "version_tags": [],
        "latest_tags": [],
        "latest_skipped_newer_release": False,
    }
    bodies: dict[str, bytes] = {}
    profiles = catalog(ROOT)
    for key in [item for item in profiles if item != "app"] + ["app"]:
        natives = {}
        for architecture, letter in (("amd64", "1"), ("arm64", "2")):
            body = json.dumps(
                {
                    "schemaVersion": 2,
                    "mediaType": OCI_MANIFEST,
                    "config": {"digest": "sha256:" + letter * 64},
                    "layers": [],
                }
            ).encode()
            digest = sha256(body)
            bodies[context().repository + "@" + digest] = body
            natives[architecture] = Descriptor(OCI_MANIFEST, digest, len(body))
        body = index_body(context(), key, natives)
        for kind, tag in (
            ("version_tags", version_tag(profiles[key], context().version)),
            ("latest_tags", latest_tag(profiles[key])),
        ):
            value[kind].append(
                {
                    "tag": tag,
                    "mediaType": "application/vnd.oci.image.index.v1+json",
                    "digest": sha256(body),
                    "size": len(body),
                }
            )
            bodies[context().repository + ":" + tag] = body
    return value, bodies


@pytest.mark.parametrize("change", ["partial", "staging", "revision", "run", "attempt", "status"])
def test_full_receipt_rejects_wrong_publication_identity(change: str) -> None:
    receipt, _ = full_receipt()
    if change == "partial":
        receipt.update(scope="partial", profiles=["app", "python-core"])
    elif change == "staging":
        receipt["kind"] = "ds60-staged-images"
    elif change in {"revision", "run", "attempt"}:
        field = {"revision": "revision", "run": "run_id", "attempt": "run_attempt"}[change]
        receipt["context"][field] = CURRENT if change == "revision" else "99"
    else:
        receipt["status"] = "promoting"
    with pytest.raises(ReleaseError, match="differs"):
        audit.validate_receipt(receipt, request())


def test_full_receipt_covers_every_profile_and_matches_exported_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt, _ = full_receipt()
    monkeypatch.setattr(audit, "source_version", lambda root: context().version)
    profiles, versions, aliases = audit.receipt_indexes(receipt, context(), ROOT)
    assert len(profiles) == len(versions) == len(aliases) == 26
    receipt["version_tags"].pop(0)
    with pytest.raises(ReleaseError, match="incomplete"):
        audit.receipt_indexes(receipt, context(), ROOT)
    receipt, _ = full_receipt()
    monkeypatch.setattr(audit, "source_version", lambda root: "1.1.1")
    with pytest.raises(ReleaseError, match="source version"):
        audit.receipt_indexes(receipt, context(), ROOT)


def archive(entries: list[tuple[str, bytes, int]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        for name, body, mode in entries:
            item = zipfile.ZipInfo(name)
            item.external_attr = mode << 16
            bundle.writestr(item, body)
    return buffer.getvalue()


@pytest.mark.parametrize(
    "name,mode",
    [
        ("../escape", stat.S_IFREG | 0o644),
        ("/escape", stat.S_IFREG | 0o644),
        ("nested/../escape", stat.S_IFREG | 0o644),
        ("nested\\escape", stat.S_IFREG | 0o644),
        (".git/config", stat.S_IFREG | 0o644),
        (".classroom/settings", stat.S_IFREG | 0o644),
        ("work/state", stat.S_IFREG | 0o644),
        ("link", stat.S_IFLNK | 0o777),
        ("fifo", stat.S_IFIFO | 0o600),
    ],
)
def test_archive_rejects_unsafe_source_entries(name: str, mode: int) -> None:
    with (
        zipfile.ZipFile(io.BytesIO(archive([(name, b"fixture", mode)]))) as bundle,
        pytest.raises(ReleaseError, match="unsafe"),
    ):
        audit.source_entries(bundle)


def test_archive_rejects_duplicate_paths_and_bounded_size(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.warns(UserWarning, match="Duplicate"):
        data = archive(
            [("file", b"one", stat.S_IFREG | 0o644), ("file", b"two", stat.S_IFREG | 0o644)]
        )
    with zipfile.ZipFile(io.BytesIO(data)) as bundle, pytest.raises(ReleaseError, match="repeated"):
        audit.source_entries(bundle)
    monkeypatch.setattr(audit, "MAX_SOURCE_FILE", 2)
    with (
        zipfile.ZipFile(io.BytesIO(archive([("file", b"long", stat.S_IFREG | 0o644)]))) as bundle,
        pytest.raises(ReleaseError, match="bounded extraction"),
    ):
        audit.source_entries(bundle)


@pytest.mark.parametrize("tamper", ["bytes", "mode", "link"])
def test_export_preserves_executable_source_and_refuses_tampering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tamper: str
) -> None:
    directory = tmp_path / "export"
    directory.mkdir()
    data = archive(
        [
            ("classroom", b"#!/bin/sh\nexit 0\n", stat.S_IFREG | 0o755),
            ("docker/catalog.txt", b"reviewed\n", stat.S_IFREG | 0o644),
        ]
    )

    def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert args[-1] == PUBLISHED
        Path(args[3].removeprefix("--output=")).write_bytes(data)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", run)
    exported = audit.export_source(request(), directory, tmp_path)
    assert exported["files"] == 2
    assert (directory / "source/classroom").stat().st_mode & 0o111
    audit.verify_export(request(), directory)
    file = directory / "source/classroom"
    if tamper == "bytes":
        file.write_bytes(b"changed\n")
    elif tamper == "mode":
        file.chmod(0o644)
    else:
        file.unlink()
        file.symlink_to(directory / "source/docker/catalog.txt")
    with pytest.raises(ReleaseError, match="changed"):
        audit.verify_export(request(), directory)


def test_published_run_requires_exact_successful_promotion_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = {
        "id": 10000,
        "event": "push",
        "head_branch": "main",
        "head_sha": PUBLISHED,
        "path": audit.PUBLISH_PATH,
        "status": "completed",
        "conclusion": "failure",
        "run_attempt": 2,
    }
    job = {
        "id": 77,
        "name": audit.PROMOTE_JOB,
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
        "head_sha": PUBLISHED,
        "run_id": 10000,
    }
    monkeypatch.setattr(recovery, "gh_json", lambda *args, **kwargs: run)
    paths = []

    def pages(path: str) -> list[dict[str, Any]]:
        paths.append(path)
        return [{"jobs": [job]}]

    monkeypatch.setattr(recovery, "gh_pages", pages)
    assert audit.published_run(request())["promote_job_id"] == 77
    assert "/attempts/1/jobs?" in paths[0]
    job["run_attempt"] = 2
    with pytest.raises(ReleaseError, match="attempt"):
        audit.published_run(request())
    run["status"] = "in_progress"
    with pytest.raises(ReleaseError, match="has not completed"):
        audit.published_run(request())


@pytest.mark.parametrize("architecture,letter", [("amd64", "1"), ("arm64", "2")])
def test_selected_native_images_bind_canonical_indexes_and_exact_config_ids(
    monkeypatch: pytest.MonkeyPatch, architecture: str, letter: str
) -> None:
    receipt, bodies = full_receipt()
    monkeypatch.setattr(audit, "source_version", lambda root: context().version)
    references = []

    def output(args: list[str], **kwargs: Any) -> bytes:
        references.append(args[-1])
        return bodies[args[-1]]

    monkeypatch.setattr(hub, "run_output", output)
    selected = ["app", "python-core", "r-statistics"]
    result = audit.selected_image_ids(context(), receipt, selected, architecture, True, ROOT)
    assert result == dict.fromkeys(selected, "sha256:" + letter * 64)
    assert any(value.endswith(":1.1.0-worker-r-statistics") for value in references)
    assert any(value.endswith(":latest-worker-r-statistics") for value in references)
    assert not any("javascript" in value or ":ci-" in value for value in references)
    native = next(value for value in references if "@" in value)
    bodies[native] = b"{}"
    with pytest.raises(ReleaseError, match="Native manifest differs"):
        audit.selected_image_ids(context(), receipt, selected, architecture, True, ROOT)


def test_saved_profiles_requires_exact_selected_set(tmp_path: Path) -> None:
    project = "ds60-hub-amd64-12345-2"
    state = tmp_path / ".classroom" / project
    state.mkdir(parents=True)
    file = state / "selection.env"
    file.write_text("DS60_PROFILES=python-core,r-statistics\nDS60_REGISTRY=default\n")
    audit.saved_profiles(project, ["r-statistics"], tmp_path)
    file.write_text("DS60_PROFILES=python-core,r-statistics,java21\nDS60_REGISTRY=default\n")
    with pytest.raises(ReleaseError, match="different selected"):
        audit.saved_profiles(project, ["r-statistics"], tmp_path)


@pytest.mark.parametrize(
    "defect", [None, "extra-image", "missing-image", "wrong-native", "extra-service"]
)
def test_module_audit_checks_actual_selective_pull_and_service_identities(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str | None
) -> None:
    directory = tmp_path / "work/audit"
    source = directory / "source"
    (source / "docker").mkdir(parents=True)
    (source / "docker/classroom-images.tsv").write_bytes(
        (ROOT / "docker/classroom-images.tsv").read_bytes()
    )
    (source / "docker/ci-profile-groups.json").write_bytes(
        (ROOT / "docker/ci-profile-groups.json").read_bytes()
    )
    (directory / "source-manifest.json").write_bytes(b"{}")
    manifest_hash = sha256(b"{}")
    receipt, _ = full_receipt()
    preflight = {"published_tree": "c" * 40, "source_export": {"manifest_sha256": manifest_hash}}
    monkeypatch.setattr(audit, "prepared_identity", lambda *args: (preflight, receipt, context()))
    monkeypatch.setattr(audit, "verify_export", lambda *args: None)
    monkeypatch.setattr(hub, "native_engine", lambda *args: None)
    expected = dict.fromkeys(["app", "python-core", "r-statistics"], "sha256:" + "1" * 64)
    monkeypatch.setattr(audit, "selected_image_ids", lambda *args: expected)
    monkeypatch.setattr(hub, "read_selection", lambda *args: None)
    monkeypatch.setenv("DOCKERHUB_USERNAME", "example")
    phase = {"prepared": False, "started": False}
    references = [
        "example/ds60sqlpy:" + tag
        for tag in (
            "1.1.0",
            "1.1.0-worker-python-core",
            "1.1.0-worker-r-statistics",
            "latest",
            "latest-worker-r-statistics",
        )
    ]

    def refs(*args: Any) -> list[str]:
        if not phase["prepared"]:
            return []
        if defect == "extra-image":
            return references + ["example/ds60sqlpy:1.1.0-worker-java21"]
        if defect == "missing-image":
            return references[:-1]
        return references

    monkeypatch.setattr(audit, "release_references", refs)
    services = ["lab", "classroom-init", "postgres", "python-core-worker", "r-worker"]
    if defect == "extra-service":
        services.append("java-worker")
    monkeypatch.setattr(
        hub,
        "docker_items",
        lambda kind, *args: services if kind == "container" and phase["started"] else [],
    )

    def output(args: list[str], **kwargs: Any) -> bytes:
        if args[:3] == ["docker", "image", "inspect"]:
            letter = "2" if defect == "wrong-native" else "1"
            return ("linux amd64 sha256:" + letter * 64).encode()
        if args[:2] == ["docker", "inspect"]:
            return (args[-1] + " sha256:" + "1" * 64).encode()
        raise AssertionError(args)

    monkeypatch.setattr(hub, "run_output", output)

    def lifecycle(*args: Any, **kwargs: Any) -> dict[str, Any]:
        assert args[1:5] == ("partial", "r", False, "amd64")
        assert kwargs["pull_first"] is True
        project = kwargs["project"]
        state = source / ".classroom" / project
        state.mkdir(parents=True)
        (state / "selection.env").write_text(
            "DS60_PROFILES=python-core,r-statistics\nDS60_REGISTRY=default\n"
        )
        phase["prepared"] = True
        prepared = kwargs["prepared_check"](project, ["r-statistics"])
        phase["started"] = True
        started = kwargs["started_check"](project, ["r-statistics"])
        return {
            "prepared_observation": prepared,
            "started_observation": started,
            "resumed_observation": kwargs["started_check"](project, ["r-statistics"]),
        }

    monkeypatch.setattr(hub, "launch_and_resume", lifecycle)
    if defect is None:
        result = audit.accept(request(), directory, "r", "amd64", True, tmp_path)
        assert result["status"] == "accepted"
        assert result["profiles_pulled"] == ["app", "python-core", "r-statistics"]
        assert result["started_observation"]["services"] == sorted(services)
    else:
        with pytest.raises(ReleaseError):
            audit.accept(request(), directory, "r", "amd64", True, tmp_path)
        assert json.loads((directory / "acceptance.json").read_text())["status"] == "failed"


def test_workflow_is_dispatch_only_and_never_builds_or_publishes() -> None:
    workflow = (ROOT / ".github/workflows/audit-published-release.yml").read_text()
    assert "workflow_dispatch:" in workflow and "  push:" not in workflow
    assert "contents: read" in workflow and "actions: read" in workflow
    assert "classroom-dockerhub-publication" in workflow
    assert "fromJSON(needs.preflight.outputs.matrix)" in workflow
    assert "max-parallel: 4" in workflow
    assert "ci_hub_release_audit.py preflight" in workflow
    assert "ci_hub_release_audit.py prepare" in workflow
    assert "operation=accept" in workflow
    assert 'ci_hub_release_audit.py "$operation"' in workflow
    assert "docker build" not in workflow and "docker push" not in workflow
    assert "--password-stdin" in workflow


@pytest.mark.parametrize("defect", [None, "wrong-head", "dirty", "unmarked"])
def test_checkout_binds_clean_verifier_and_marked_published_ancestor(
    monkeypatch: pytest.MonkeyPatch, defect: str | None
) -> None:
    operations: list[list[str]] = []

    def git(args: list[str], **kwargs: Any) -> bytes:
        operations.append(args)
        if args == ["rev-parse", "HEAD"]:
            return (PUBLISHED if defect == "wrong-head" else CURRENT).encode()
        if args[0] == "status":
            return b" M scripts/classroom.sh" if defect == "dirty" else b""
        if args[0] == "log":
            return b"checkpoint" if defect == "unmarked" else b"Release [publish-docker]"
        if args[:2] == ["merge-base", "--is-ancestor"]:
            return b""
        if args == ["rev-parse", PUBLISHED + "^{tree}"]:
            return b"c" * 40
        raise AssertionError(args)

    monkeypatch.setattr(recovery, "git", git)
    if defect is None:
        assert audit.verify_checkout(request(), ROOT) == "c" * 40
        assert ["merge-base", "--is-ancestor", PUBLISHED, "HEAD"] in operations
    else:
        with pytest.raises(ReleaseError):
            audit.verify_checkout(request(), ROOT)


def test_preflight_source_guard_rejects_swapped_receipt_or_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    receipt, _ = full_receipt()
    raw = json.dumps(receipt).encode()
    (tmp_path / "release.json").write_bytes(raw)
    report = {
        "schema_version": 1,
        "kind": "ds60-full-hub-audit-preflight",
        "status": "passed",
        "verification": audit.verification_identity(request()),
        "published": asdict(context()),
        "published_tree": "c" * 40,
        "receipt_sha256": sha256(raw),
    }
    write_json(tmp_path / "preflight.json", report)
    monkeypatch.setattr(audit, "verify_checkout", lambda *args: "c" * 40)
    assert audit.prepared_identity(request(), tmp_path, ROOT)[2] == context()
    monkeypatch.setattr(audit, "verify_checkout", lambda *args: "d" * 40)
    with pytest.raises(ReleaseError, match="preflight differs"):
        audit.prepared_identity(request(), tmp_path, ROOT)
    monkeypatch.setattr(audit, "verify_checkout", lambda *args: "c" * 40)
    (tmp_path / "release.json").write_bytes(raw + b"\n")
    with pytest.raises(ReleaseError, match="preflight differs"):
        audit.prepared_identity(request(), tmp_path, ROOT)


def prior_acceptance(group: str = "cpp", architecture: str = "amd64") -> dict[str, Any]:
    current = context()
    profiles = catalog(ROOT)
    workers = ci_profiles.selected(group, ROOT)
    selected = list(dict.fromkeys(["app", "python-core", *workers]))
    services = sorted(
        {
            "lab",
            "postgres",
            "classroom-init",
            *[audit.service_for_profile(key, ROOT) for key in selected if key != "app"],
        }
    )
    references = {
        current.repository + ":" + version_tag(profiles[key], current.version) for key in selected
    }
    references.update(
        current.repository + ":" + latest_tag(profiles[key]) for key in ("app", workers[0])
    )
    return {
        "schema_version": 1,
        "kind": "ds60-full-hub-module-audit",
        "status": "accepted",
        "group": group,
        "architecture": architecture,
        "version": current.version,
        "saved_version": current.version,
        "published_revision": current.revision,
        "published_run_id": current.run_id,
        "published_tree": "d" * 40,
        "verification": {"revision": "c" * 40, "run_id": "9000", "run_attempt": "1"},
        "profiles_pulled": selected,
        "profiles_started": workers,
        "persistent_volumes": 3,
        "latest_aliases_checked": True,
        "latest_resolved": True,
        "stop_resume_same_stateful_containers": True,
        "app_image_unchanged": True,
        "learning_marker_retained": True,
        "browser_readback_ok": True,
        "prepared_observation": {
            "no_runtime_resources": True,
            "release_references": sorted(references),
            "images": [
                {
                    "profile": key,
                    "reference": current.repository
                    + ":"
                    + version_tag(profiles[key], current.version),
                    "image_id": "sha256:" + "1" * 64,
                }
                for key in selected
            ],
        },
        "started_observation": {"services": services, "profile_images_match_promotion": True},
        "resumed_observation": {"services": services, "profile_images_match_promotion": True},
    }


@pytest.mark.parametrize(
    "mutation",
    [None, "status", "source", "verifier", "image", "service", "marker", "reference", "profiles"],
)
def test_prior_acceptance_retains_exact_published_and_lifecycle_identity(
    mutation: str | None,
) -> None:
    value = prior_acceptance()
    if mutation == "status":
        value["status"] = "failed"
    elif mutation == "source":
        value["published_revision"] = "e" * 40
    elif mutation == "verifier":
        value["verification"]["revision"] = "e" * 40
    elif mutation == "image":
        value["prepared_observation"]["images"][0]["image_id"] = "unbound"
    elif mutation == "service":
        value["started_observation"]["services"] = ["lab"]
    elif mutation == "marker":
        value["learning_marker_retained"] = False
    elif mutation == "reference":
        value["prepared_observation"]["release_references"].append(
            "example/ds60sqlpy:ci-unqualified"
        )
    elif mutation == "profiles":
        value["profiles_pulled"] = ["app", "python-core"]

    def validate() -> None:
        audit.validate_prior_acceptance(
            value,
            context=context(),
            source=ROOT,
            verifier_sha="c" * 40,
            run_id="9000",
            attempt="1",
            group="cpp",
            architecture="amd64",
        )

    if mutation is None:
        validate()
    else:
        with pytest.raises(ReleaseError):
            validate()


def test_recovery_defaults_to_one_unresolved_canary_and_never_repeats_passed_cases() -> None:
    matrix = ci_profiles.matrix(native=True, root=ROOT)
    reused = [{"case": "python-core/amd64"}, {"case": "python-core/arm64"}]
    report = audit.execution_selection(
        matrix, reused, resume=True, requested_cases=[], diagnostic_only=False
    )
    assert report["selected_cases"] == ["python-web/amd64"]
    assert len(report["unresolved_cases"]) == len(matrix["include"]) - 2
    assert not set(report["selected_cases"]) & set(report["accepted_cases"])
    explicit = audit.execution_selection(
        matrix,
        reused,
        resume=True,
        requested_cases=["python-web/arm64", "r/amd64"],
        diagnostic_only=False,
    )
    assert explicit["selected_cases"] == ["python-web/arm64", "r/amd64"]
    with pytest.raises(ReleaseError, match="never accepted"):
        audit.execution_selection(
            matrix,
            reused,
            resume=True,
            requested_cases=["python-core/amd64"],
            diagnostic_only=False,
        )
    diagnostic = audit.execution_selection(
        matrix, reused, resume=True, requested_cases=[], diagnostic_only=True
    )
    assert len(diagnostic["selected_cases"]) == 2
    assert {row["architecture"] for row in diagnostic["execution_matrix"]["include"]} == {
        "amd64",
        "arm64",
    }


@pytest.mark.parametrize("text", ["0", "123,123", "../123", "1;command", "1, 2"])
def test_recovery_inputs_are_bounded_data_not_commands(text: str) -> None:
    with pytest.raises(ReleaseError):
        audit.recovery_inputs(text)


def test_explicit_recovery_case_limit_is_bounded() -> None:
    assert audit.recovery_inputs("r/amd64,scala-spark/arm64", cases=True) == [
        "r/amd64",
        "scala-spark/arm64",
    ]
    with pytest.raises(ReleaseError):
        audit.recovery_inputs(",".join(f"group-{i}/amd64" for i in range(7)), cases=True)


def zip_report(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        for name, raw in files.items():
            bundle.writestr(name, raw)
    return buffer.getvalue()


def test_recovery_preserves_raw_passed_receipt_and_does_not_fetch_failed_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    value = prior_acceptance()
    raw = json.dumps(value, indent=3).encode() + b"\n"
    preflight = {
        "kind": "ds60-full-hub-audit-preflight",
        "status": "passed",
        "verification": {"revision": "c" * 40, "run_id": "9000", "run_attempt": "1"},
        "published": asdict(context()),
        "resume_runs": [],
    }
    blobs = {
        "77": zip_report({"preflight.json": json.dumps(preflight).encode()}),
        "78": zip_report({"acceptance.json": raw}),
    }
    artifacts_list = [
        {
            "id": int(identifier),
            "name": name,
            "expired": False,
            "size_in_bytes": len(blobs[identifier]),
            "digest": sha256(blobs[identifier]),
        }
        for identifier, name in (
            ("77", "full-hub-audit-preflight-attempt-1"),
            ("78", "full-hub-audit-cpp-amd64-attempt-1"),
        )
    ]
    artifacts_list.append({"id": 79, "name": "full-hub-audit-r-arm64-attempt-1"})
    jobs = [
        {
            "id": 100,
            "name": "Bind published full source and promotion",
            "run_attempt": 1,
            "conclusion": "success",
        },
        {
            "id": 101,
            "name": "Pull selected modules (cpp, amd64)",
            "run_attempt": 1,
            "conclusion": "success",
        },
        {
            "id": 102,
            "name": "Pull selected modules (r, arm64)",
            "run_attempt": 1,
            "conclusion": "failure",
        },
    ]
    for job in jobs:
        job.update(status="completed", head_sha="c" * 40, run_id=9000)
    run = {
        "id": 9000,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": "c" * 40,
        "path": ".github/workflows/audit-published-release.yml",
        "status": "completed",
        "conclusion": "failure",
    }
    monkeypatch.setattr(recovery, "gh_json", lambda *args, **kwargs: run)
    monkeypatch.setattr(
        recovery,
        "gh_pages",
        lambda path: [{"artifacts": artifacts_list}] if "/artifacts?" in path else [{"jobs": jobs}],
    )
    monkeypatch.setattr(
        recovery, "git", lambda args, **kwargs: b"" if args[0] == "merge-base" else b"d" * 40
    )
    fetched = []

    def gh(args: list[str], **kwargs: Any) -> bytes:
        identifier = args[-1].split("/")[-2]
        fetched.append(identifier)
        assert identifier != "79"
        return blobs[identifier]

    monkeypatch.setattr(artifacts, "gh", gh)
    receipts, runs = audit.collect_prior_acceptances(
        request(), context(), ROOT, tmp_path, ["9000"], root=ROOT
    )
    assert runs == ["9000"] and len(receipts) == 1
    assert receipts[0]["case"] == "cpp/amd64" and receipts[0]["receipt_sha256"] == sha256(raw)
    assert (tmp_path / receipts[0]["receipt_path"]).read_bytes() == raw
    assert fetched == ["77", "78"]
    tampered = dict(artifacts_list[1], digest="sha256:" + "0" * 64)
    with pytest.raises(ReleaseError, match="GitHub digest"):
        audit.prior_artifact(tampered, "example/classroom")


def test_accept_command_checks_registry_before_any_classroom_pull(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(recovery, "dispatch_request", lambda *args: request())
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    calls = []

    def blocked(*args: Any, **kwargs: Any) -> dict[str, Any]:
        assert kwargs["require_pulls"] is True
        calls.append("diagnostic")
        raise ReleaseError("quota exhausted")

    monkeypatch.setattr(audit, "diagnose", blocked)
    monkeypatch.setattr(
        audit, "accept", lambda *args: pytest.fail("Blocked quota reached classroom pull")
    )
    assert (
        audit.main(
            [
                "accept",
                "--published-sha",
                PUBLISHED,
                "--published-run-id",
                "10000",
                "--published-attempt",
                "1",
                "--directory",
                "work/audit",
                "--group",
                "r",
                "--architecture",
                "arm64",
            ]
        )
        == 2
    )
    assert calls == ["diagnostic"]
