"""Read-only recovery of an already published partial multiarch release."""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from scripts import ci_hub_acceptance as hub
from scripts import ci_hub_reverify as verify
from scripts import ci_release_artifacts as artifacts
from scripts import ci_release_status as source_ci
from scripts.docker_registry import OCI_MANIFEST, Descriptor, ReleaseError, sha256
from scripts.docker_release import Context, catalog, index_body, latest_tag, version_tag

ROOT = Path(__file__).resolve().parents[1]
OLD_SHA = "a" * 40
NEW_SHA = "b" * 40


def request() -> verify.Request:
    return verify.Request("example/classroom", NEW_SHA, "99999", "2", OLD_SHA, "12345", "1")


def context() -> Context:
    return Context(
        "example", "example/ds60sqlpy", "example/classroom", "1.0.0", OLD_SHA, "12345", "1"
    )


def published_receipt() -> tuple[dict[str, Any], dict[str, bytes]]:
    current = context()
    profiles = catalog(ROOT)
    version_rows = []
    latest_rows = []
    bodies: dict[str, bytes] = {}
    order = [key for key in profiles if key in verify.SELECTED and key != "app"] + ["app"]
    for key in order:
        natives = {
            "amd64": Descriptor(OCI_MANIFEST, "sha256:" + "1" * 64, 128),
            "arm64": Descriptor(OCI_MANIFEST, "sha256:" + "2" * 64, 128),
        }
        body = index_body(current, key, natives, target_group=verify.PUBLISHED_GROUP)
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
        latest_rows.append({"tag": alias, **fields})
    return (
        {
            "schema_version": 1,
            "kind": "ds60-release-promotion",
            "context": asdict(current),
            "status": "published",
            "version_tags": version_rows,
            "latest_tags": latest_rows,
            "latest_skipped_newer_release": False,
            "scope": "partial",
            "group": verify.PUBLISHED_GROUP,
            "profiles": sorted(verify.SELECTED),
        },
        bodies,
    )


def github_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": "example/classroom",
        "GITHUB_SHA": NEW_SHA,
        "GITHUB_RUN_ID": "99999",
        "GITHUB_RUN_ATTEMPT": "2",
        "DOCKERHUB_USERNAME": "example",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_workflow_is_dispatch_only_native_and_cannot_publish() -> None:
    yaml = pytest.importorskip("yaml")
    path = ROOT / ".github/workflows/verify-published-images.yml"
    text = path.read_text()
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert set(workflow["on"]["workflow_dispatch"]["inputs"]) == {
        "published_run_id",
        "published_sha",
        "published_attempt",
    }
    assert workflow["permissions"] == {"contents": "read", "actions": "read"}
    assert workflow["concurrency"] == {
        "group": "classroom-dockerhub-publication",
        "cancel-in-progress": "false",
    }
    job = workflow["jobs"]["native-pull"]
    assert {
        item["architecture"]: item["runner"] for item in job["strategy"]["matrix"]["include"]
    } == {"amd64": "ubuntu-24.04", "arm64": "ubuntu-24.04-arm"}
    checkout = job["steps"][0]
    assert checkout["with"] == {
        "ref": "${{ github.sha }}",
        "fetch-depth": "0",
        "persist-credentials": "false",
    }
    first, second = job["steps"][2:4]
    assert "GH_TOKEN" in first["env"] and "secrets.DOCKERHUB" not in json.dumps(first)
    assert "DOCKERHUB_TOKEN" in second["env"] and "--password-stdin" in second["run"]
    assert '--published-run-id "$PUBLISHED_RUN_ID"' in first["run"]
    assert '--published-sha "$PUBLISHED_SHA"' in first["run"]
    assert '--published-attempt "$PUBLISHED_ATTEMPT"' in first["run"]
    assert "docker_release.py" not in text and "docker push" not in text
    assert "imagetools create" not in text and "workflow_dispatch" in text
    assert job["steps"][-1]["if"] == "always()"


def test_dispatch_requires_exact_main_context(monkeypatch: pytest.MonkeyPatch) -> None:
    github_environment(monkeypatch)
    assert verify.dispatch_request(OLD_SHA, "12345", "1") == request()
    monkeypatch.setenv("GITHUB_REF", "refs/heads/feature")
    with pytest.raises(ReleaseError, match="exact main"):
        verify.dispatch_request(OLD_SHA, "12345", "1")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    with pytest.raises(ReleaseError, match="exact main"):
        verify.dispatch_request("bad", "12345", "1")
    with pytest.raises(ReleaseError, match="exact main"):
        verify.dispatch_request(OLD_SHA, "12345", "0")


def test_checkout_allows_only_verifier_delta_and_requires_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fake_git(args: list[str], *, root: Path) -> bytes:
        calls.append(args)
        if args[:2] == ["rev-parse", "HEAD"]:
            return NEW_SHA.encode()
        if args[:2] == ["status", "--porcelain"]:
            return b""
        if args[:2] == ["diff", "--name-only"]:
            return b"scripts/ci_hub_acceptance.py\0scripts/ci_hub_reverify.py\0"
        if args[:1] == ["show"]:
            return b"[project]\nversion = '1.0.0'\n"
        return b""

    monkeypatch.setattr(verify, "git", fake_git)
    monkeypatch.setattr(verify, "source_version", lambda root: "1.0.0")
    assert verify.verify_checkout(request(), tmp_path) == [
        "scripts/ci_hub_acceptance.py",
        "scripts/ci_hub_reverify.py",
    ]
    assert ["merge-base", "--is-ancestor", OLD_SHA, "HEAD"] in calls

    def bad_git(args: list[str], *, root: Path) -> bytes:
        if args[:2] == ["diff", "--name-only"]:
            return b"src/ds60sqlpy/lab.py\0"
        return fake_git(args, root=root)

    monkeypatch.setattr(verify, "git", bad_git)
    with pytest.raises(ReleaseError, match="allowlisted"):
        verify.verify_checkout(request(), tmp_path)


def test_course_selection_ignores_unrelated_app_build_failure() -> None:
    pages = [
        {
            "workflow_runs": [
                {
                    "id": 10,
                    "run_attempt": 1,
                    "path": ".github/workflows/app-build.yml",
                    "event": "push",
                    "head_branch": "main",
                    "head_sha": NEW_SHA,
                    "status": "completed",
                    "conclusion": "failure",
                },
                {
                    "id": 11,
                    "run_attempt": 1,
                    "path": verify.SOURCE_JOB_PATH,
                    "event": "push",
                    "head_branch": "main",
                    "head_sha": NEW_SHA,
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        }
    ]
    chosen = verify.select_course_run(pages, NEW_SHA)
    assert chosen is not None and chosen["id"] == 11


def test_current_source_requires_all_seven_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    run = {
        "id": 11,
        "run_attempt": 1,
        "path": verify.SOURCE_JOB_PATH,
        "event": "push",
        "head_branch": "main",
        "head_sha": NEW_SHA,
        "status": "completed",
        "conclusion": "success",
    }
    jobs = [
        {"id": i, "name": name, "status": "completed", "conclusion": "success"}
        for i, name in enumerate(source_ci.WORKFLOWS[verify.SOURCE_JOB_PATH], 1)
    ]
    monkeypatch.setattr(
        verify,
        "gh_pages",
        lambda path: [{"workflow_runs": [run]}] if "head_sha=" in path else [{"jobs": jobs}],
    )
    proof = verify.current_source_jobs(request(), timeout_seconds=1)
    assert len(proof["jobs"]) == 7
    jobs[-1]["conclusion"] = "failure"
    with pytest.raises(ValueError, match="required qualification job"):
        verify.current_source_jobs(request(), timeout_seconds=1)


def test_published_run_requires_successful_promotion(monkeypatch: pytest.MonkeyPatch) -> None:
    old = {
        "id": 12345,
        "event": "push",
        "head_branch": "main",
        "head_sha": OLD_SHA,
        "path": verify.PUBLISH_PATH,
        "status": "completed",
        "conclusion": "failure",
        "run_attempt": 1,
    }
    jobs = [{"id": 31, "name": verify.PROMOTE_JOB, "status": "completed", "conclusion": "success"}]
    monkeypatch.setattr(verify, "gh_json", lambda args, maximum: old)
    monkeypatch.setattr(verify, "gh_pages", lambda path: [{"jobs": jobs}])
    assert verify.published_run(request())["promote_job_id"] == 31
    jobs[0]["conclusion"] = "failure"
    with pytest.raises(ReleaseError, match="promotion"):
        verify.published_run(request())


def test_receipt_requires_exact_partial_tag_set_and_attempt() -> None:
    value, _ = published_receipt()
    assert verify.validate_receipt(value, request()) == context()
    wrong = json.loads(json.dumps(value))
    wrong["context"]["run_attempt"] = "2"
    with pytest.raises(ReleaseError, match="requested source"):
        verify.validate_receipt(wrong, request())
    wrong = json.loads(json.dumps(value))
    wrong["profiles"].remove("typescript-node")
    with pytest.raises(ReleaseError, match="requested source"):
        verify.validate_receipt(wrong, request())
    wrong = json.loads(json.dumps(value))
    wrong["latest_tags"] = []
    with pytest.raises(ReleaseError, match="coverage"):
        verify.validate_receipt(wrong, request())


def test_fetches_only_exact_bounded_promotion_artifact(monkeypatch: pytest.MonkeyPatch) -> None:
    value, _ = published_receipt()
    document = json.dumps(value).encode()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("release.json", document)
    pages = [
        {
            "artifacts": [
                {
                    "id": 31,
                    "name": "published-targeted-release-attempt-1",
                    "size_in_bytes": 300,
                    "expired": False,
                },
                {
                    "id": 32,
                    "name": "published-targeted-release-attempt-2",
                    "size_in_bytes": 300,
                    "expired": False,
                },
            ]
        }
    ]
    monkeypatch.setattr(verify, "gh_pages", lambda path: pages)
    monkeypatch.setattr(artifacts, "gh", lambda args, maximum: archive.getvalue())
    receipt, raw = verify.published_receipt(request())
    assert receipt["status"] == "published" and raw == document
    pages[0]["artifacts"].append(dict(pages[0]["artifacts"][0]))
    with pytest.raises(ReleaseError, match="unique"):
        verify.published_receipt(request())


def test_preflight_binds_source_run_receipt_and_diff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    value, _ = published_receipt()
    raw = json.dumps(value).encode()
    monkeypatch.setattr(
        verify, "verify_checkout", lambda request, root: ["scripts/ci_hub_acceptance.py"]
    )
    monkeypatch.setattr(
        verify,
        "current_source_jobs",
        lambda request: {"jobs": [{"name": "required"}], "run_id": 12},
    )
    monkeypatch.setattr(verify, "published_run", lambda request: {"promote_job_id": 31})
    monkeypatch.setattr(verify, "published_receipt", lambda request: (value, raw))
    result = verify.preflight(
        request(), root / "work/release.json", root / "work/preflight.json", root
    )
    assert result["status"] == "passed"
    assert result["receipt_sha256"] == sha256(raw)
    assert (root / "work/release.json").read_bytes() == raw


def test_index_inspection_matches_receipt_version_and_latest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    value, _ = published_receipt()
    seen: list[str] = []

    def inspect(
        reference: str, expected: Any, profile: str, context: Context, group: str | None, root: Path
    ) -> dict[str, Any]:
        seen.append(reference)
        assert group == verify.PUBLISHED_GROUP
        return {}

    monkeypatch.setattr(hub, "inspect_index", inspect)
    assert verify.inspect_published_indexes(context(), value, ROOT) == sorted(verify.SELECTED)
    assert len(seen) == 8
    assert all(reference.startswith("example/ds60sqlpy:") for reference in seen)


def test_accept_rechecks_checkout_and_rejects_oversize_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    receipt_file = root / "work/release.json"
    preflight_file = root / "work/preflight.json"
    report_file = root / "work/acceptance.json"
    value, _ = published_receipt()
    raw = json.dumps(value).encode()
    receipt_file.write_bytes(raw)
    preflight_file.write_text(
        json.dumps(
            {
                "kind": "ds60-hub-reverify-preflight",
                "status": "passed",
                "verification": {"revision": NEW_SHA, "run_id": "99999", "run_attempt": "2"},
                "changed_files": ["scripts/ci_hub_acceptance.py"],
                "published": asdict(context()),
                "receipt_sha256": sha256(raw),
            }
        )
    )
    monkeypatch.setenv("DOCKERHUB_USERNAME", "example")
    monkeypatch.setattr(
        verify, "verify_checkout", lambda request, root: ["scripts/ci_hub_acceptance.py"]
    )
    monkeypatch.setattr(hub, "native_engine", lambda architecture, root: None)
    monkeypatch.setattr(
        verify, "inspect_published_indexes", lambda context, receipt, root: sorted(verify.SELECTED)
    )
    calls: list[str] = []

    def launch(*args: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs["project"])
        return {"browser_readback_ok": True}

    monkeypatch.setattr(hub, "launch_and_resume", launch)
    result = verify.accept(request(), receipt_file, preflight_file, "arm64", report_file, root)
    assert result["status"] == "accepted"
    assert calls == ["ds60-hub-arm64-99999-2"]
    assert json.loads(report_file.read_text())["indexes_inspected"] == sorted(verify.SELECTED)
    receipt_file.write_bytes(b" " * (verify.MAX_REPORT + 1))
    with pytest.raises(ReleaseError, match="bounded ordinary"):
        verify.accept(request(), receipt_file, preflight_file, "arm64", report_file, root)
    assert len(calls) == 1


def test_accept_rejects_linked_receipt_before_hub_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    value, _ = published_receipt()
    document = json.dumps(value).encode()
    actual = root / "work/release.json"
    actual.write_bytes(document)
    target = root / "work/link.json"
    target.symlink_to(actual)
    preflight = root / "work/preflight.json"
    preflight.write_text(
        json.dumps(
            {
                "kind": "ds60-hub-reverify-preflight",
                "status": "passed",
                "verification": {"revision": NEW_SHA, "run_id": "99999", "run_attempt": "2"},
                "changed_files": ["scripts/ci_hub_acceptance.py"],
                "published": asdict(context()),
                "receipt_sha256": sha256(document),
            }
        )
    )
    monkeypatch.setattr(
        verify, "verify_checkout", lambda request, root: ["scripts/ci_hub_acceptance.py"]
    )
    with pytest.raises(ReleaseError, match="links"):
        verify.accept(request(), target, preflight, "amd64", root / "work/out.json", root)
