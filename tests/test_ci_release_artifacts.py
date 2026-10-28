"""Successful logical jobs can be reused only within the exact workflow run and source."""

from __future__ import annotations

import io
import json
import stat
import zipfile
from typing import Any

import pytest

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
