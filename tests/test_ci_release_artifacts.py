"""Successful logical jobs can be reused only within the exact workflow run and source."""

from __future__ import annotations

import io
import json
import stat
import subprocess
import time
import zipfile
from typing import Any

import pytest

from scripts import ci_release_artifacts as gate
from scripts.ci_release_artifacts import Artifact, logical_keys, receipt_bytes, select_artifacts

SHA = "a" * 40


def item(
    key: str, attempt: int, *, expired: bool = False, identifier: int | None = None
) -> dict[str, Any]:
    prefix = "release-gate" if key == "gate" else "release-receipt-" + key
    return {
        "id": identifier or attempt,
        "name": f"{prefix}-attempt-{attempt}",
        "expired": expired,
        "size_in_bytes": 2000,
    }


def test_latest_unique_unexpired_prior_attempt_is_selected_per_group() -> None:
    pages = [
        {"artifacts": [item("seed-amd64", 1), item("seed-arm64", 1), item("seed-amd64", 2)]},
        {"artifacts": [item("seed-amd64", 3, expired=True), item("seed-arm64", 5)]},
    ]
    actual = select_artifacts(pages, ["seed-amd64", "seed-arm64"], 3)
    assert [(row.key, row.attempt) for row in actual] == [("seed-amd64", 2), ("seed-arm64", 1)]


def test_missing_or_ambiguous_receipts_fail_instead_of_guessing() -> None:
    with pytest.raises(ValueError, match="No unexpired"):
        select_artifacts([{"artifacts": [item("seed-amd64", 1, expired=True)]}], ["seed-amd64"], 2)
    with pytest.raises(ValueError, match="Ambiguous"):
        select_artifacts(
            [{"artifacts": [item("seed-amd64", 2), item("seed-amd64", 2, identifier=9)]}],
            ["seed-amd64"],
            2,
        )


def test_large_archives_and_nonpositive_ids_are_rejected() -> None:
    for field, value in (("size_in_bytes", 10**9), ("id", -1)):
        bad = {**item("gate", 1), field: value}
        with pytest.raises(ValueError):
            select_artifacts([{"artifacts": [bad]}], ["gate"], 1)


def seed_document() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "ds60-staged-images",
        "architecture": "arm64",
        "context": {
            "source_repository": "example/classroom",
            "revision": SHA,
            "run_id": "123",
            "run_attempt": "1",
        },
        "images": [{"profile": "app"}, {"profile": "python-core"}],
    }


def archive(raw: bytes, name: str = "release-receipt.json", *, linked: bool = False) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as bundle:
        entry = zipfile.ZipInfo(name)
        if linked:
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        bundle.writestr(entry, raw)
    return stream.getvalue()


def read(value: bytes) -> bytes:
    return receipt_bytes(
        value,
        Artifact("seed-arm64", 1, 7, "release-receipt-seed-arm64-attempt-1"),
        repository="example/classroom",
        revision=SHA,
        run_id="123",
    )


def test_prior_receipt_preserves_original_attempt_and_bytes() -> None:
    raw = json.dumps(seed_document()).encode()
    assert read(archive(raw)) == raw


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_repository", "another/repository"),
        ("revision", "b" * 40),
        ("run_id", "999"),
        ("run_attempt", "2"),
    ],
)
def test_cross_run_revision_repository_and_artifact_attempt_are_rejected(
    field: str, value: str
) -> None:
    document = seed_document()
    document["context"][field] = value
    with pytest.raises(ValueError, match="selected run, revision and attempt"):
        read(archive(json.dumps(document).encode()))


def test_logical_seed_identity_cannot_hide_another_architecture_or_worker() -> None:
    document = seed_document()
    document["architecture"] = "amd64"
    with pytest.raises(ValueError, match="architecture"):
        read(archive(json.dumps(document).encode()))
    document = seed_document()
    document["images"] = [{"profile": "rust-stable"}]
    with pytest.raises(ValueError, match="logical CI group"):
        read(archive(json.dumps(document).encode()))


def test_archive_paths_links_and_ambiguous_json_are_rejected() -> None:
    raw = json.dumps(seed_document()).encode()
    for content in (archive(raw, "../release-receipt.json"), archive(raw, linked=True)):
        with pytest.raises(ValueError, match="artifact member"):
            read(content)
    with pytest.raises(ValueError, match="Duplicate"):
        read(archive(b'{"kind":"one","kind":"two"}'))


def test_complete_receipt_selection_contains_both_seeds_and_every_worker_group() -> None:
    keys = logical_keys("receipts")
    from scripts.ci_profiles import groups

    expected = {"seed-amd64", "seed-arm64"} | {
        group["id"] + "-" + architecture
        for group in groups()
        if group["id"] != "python-core"
        for architecture in ("amd64", "arm64")
    }
    assert len(keys) == len(set(keys))
    assert set(keys) == expected
    assert {"seed-amd64", "seed-arm64", "data-engineering-amd64", "data-engineering-arm64"} <= set(
        keys
    )
    assert not any("python-core" in key or "cuda" in key for key in keys)


@pytest.mark.parametrize(
    "diagnostic",
    [
        b"gh: HTTP 429: too many requests",
        b"gh: HTTP 502: bad gateway",
        b"gh: HTTP 403: secondary rate limit exceeded",
        b"read: connection reset by peer",
    ],
)
def test_known_transient_artifact_reads_retry_then_recover(
    monkeypatch: pytest.MonkeyPatch, diagnostic: bytes
) -> None:
    secret = b"Bearer private-token https://signed.example/secret"
    responses = iter(
        [
            subprocess.CompletedProcess([], 1, b"", diagnostic + secret),
            subprocess.CompletedProcess([], 0, b"valid", b""),
        ]
    )
    calls: list[float] = []
    sleeps: list[float] = []

    def run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(kwargs["timeout"])
        return next(responses)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(time, "sleep", sleeps.append)
    assert gate.gh(["api", "repos/example/repo/actions/runs/1/artifacts"], maximum=100) == b"valid"
    assert len(calls) == 2 and sleeps == [5]


def test_transport_timeout_retries_without_exposing_exception_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise subprocess.TimeoutExpired("signed-secret-command", kwargs["timeout"])
        return subprocess.CompletedProcess([], 0, b"ok", b"")

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(time, "sleep", lambda _: None)
    assert gate.gh(["api", "repos/example/repo/actions/artifacts/1/zip"], maximum=100) == b"ok"
    assert calls == 2


def test_transient_read_exhaustion_is_bounded_and_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    sleeps: list[float] = []

    def run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            [], 1, b"", b"gh: HTTP 503: private-token https://signed.example/secret"
        )

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(time, "sleep", sleeps.append)
    with pytest.raises(ValueError, match="transient read exhausted") as captured:
        gate.gh(["api", "repos/example/repo/actions/runs/1/artifacts"], maximum=100)
    assert calls == gate.READ_ATTEMPTS == 4 and sleeps == [5, 15, 30]
    assert "http_5xx" in str(captured.value) and "attempts=4" in str(captured.value)
    assert "private-token" not in str(captured.value) and "signed.example" not in str(
        captured.value
    )


def test_timeout_retries_respect_one_total_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [0.0]
    timeouts: list[float] = []

    def run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        duration = kwargs["timeout"]
        timeouts.append(duration)
        clock[0] += duration
        raise subprocess.TimeoutExpired("secret-command", duration)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(time, "sleep", lambda duration: clock.__setitem__(0, clock[0] + duration))
    with pytest.raises(ValueError, match="transient read exhausted") as captured:
        gate.gh(["api", "repos/example/repo/actions/runs/1/artifacts"], maximum=100)
    assert len(timeouts) == 3
    assert timeouts == [20, 20, 15]
    assert all(0 < duration <= gate.READ_ATTEMPT_SECONDS for duration in timeouts)
    assert clock[0] == gate.READ_DEADLINE_SECONDS
    assert "secret-command" not in str(captured.value)


@pytest.mark.parametrize(
    "diagnostic",
    [
        b"gh: HTTP 401: bad credentials private-token",
        b"gh: HTTP 403: permission denied private-token",
        b"gh: HTTP 403: permission denied; rate limit not involved",
        b"gh: HTTP 404: missing private-token",
        b"gh: unknown failure private-token",
    ],
)
def test_auth_permission_missing_and_unknown_fail_without_retry_or_secret_leak(
    monkeypatch: pytest.MonkeyPatch, diagnostic: bytes
) -> None:
    calls = 0

    def run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess([], 1, b"", diagnostic)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(time, "sleep", lambda _: pytest.fail("Nontransient failure slept"))
    with pytest.raises(ValueError, match="Artifact API read failed") as captured:
        gate.gh(["api", "repos/example/repo/actions/runs/1/artifacts"], maximum=100)
    assert calls == 1 and "private-token" not in str(captured.value)


@pytest.mark.parametrize("returncode", [0, 1])
def test_oversized_artifact_response_is_fatal_without_retry(
    monkeypatch: pytest.MonkeyPatch, returncode: int
) -> None:
    calls = 0

    def run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            [], returncode, b"x" * 101, b"gh: HTTP 503 private-token"
        )

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(time, "sleep", lambda _: pytest.fail("Oversize failure slept"))
    with pytest.raises(ValueError, match="byte bound") as captured:
        gate.gh(["api", "repos/example/repo/actions/runs/1/artifacts"], maximum=100)
    assert calls == 1 and "private-token" not in str(captured.value)


def test_mutating_api_flags_are_not_retried_or_invoked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: pytest.fail("Mutating call ran"))
    with pytest.raises(ValueError, match="read-only"):
        gate.gh(["api", "-X", "POST", "repos/example/repo"], maximum=100)


@pytest.mark.parametrize(
    "arguments",
    [
        ["api", "--input", "payload.json", "repos/example/repo/actions/runs/1/artifacts"],
        ["api", "--field=x=y", "repos/example/repo/actions/runs/1/artifacts"],
        ["api", "-Ffoo=bar", "repos/example/repo/actions/runs/1/artifacts"],
        ["api", "-XPOST", "repos/example/repo/actions/runs/1/artifacts"],
        ["api", "--method=GET", "repos/example/repo/actions/runs/1/artifacts"],
        ["api", "graphql"],
    ],
)
def test_only_closed_release_read_shapes_are_invoked(
    monkeypatch: pytest.MonkeyPatch, arguments: list[str]
) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("Unexpected API call"))
    with pytest.raises(ValueError, match="read-only"):
        gate.gh(arguments, maximum=100)
