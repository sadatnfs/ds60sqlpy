from __future__ import annotations

import base64
import hashlib
import json
import ntpath
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom_runs import MAX_RECEIPT_BYTES, ClassroomRunStore
from ds60sqlpy.execution import MAX_CODE_BYTES, MAX_OUTPUT_BYTES


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return Catalog.load()


@pytest.fixture
def result() -> dict[str, Any]:
    return {
        "language": "python",
        "returncode": 0,
        "output": "42\n",
        "elapsed_seconds": 0.125,
        "stopped": None,
        "output_truncated": False,
        "figures": [],
        "error_line": None,
    }


def files(directory: Path) -> list[Path]:
    return sorted(directory.rglob("*.json"))


def test_construction_and_empty_reads_create_nothing(tmp_path: Path, catalog: Catalog) -> None:
    directory = tmp_path / "not-created" / "runs"
    store = ClassroomRunStore(catalog, directory)
    assert store.history("python-01", "python", "snippet") == []
    with pytest.raises(ValueError, match="not found"):
        store.get("python-01", "python", "snippet", "a" * 32)
    assert not list(tmp_path.iterdir())


def test_roundtrip_after_restart_preserves_exact_source_and_result(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    source = "print('42')\n"
    png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nfixture").decode()
    result.update(
        {
            "figures": [png],
            "tables": [{"columns": ["value"], "rows": [[42, None]]}],
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        }
    )
    expected = deepcopy(result)
    store = ClassroomRunStore(catalog, tmp_path)
    receipt = store.record("python-01", "python", "snippet", source, result)
    result["tables"][0]["rows"][0][0] = "later mutation"
    receipt["result"]["output"] = "caller changed return object"
    restored = ClassroomRunStore(catalog, tmp_path).get(
        "python-01", "python", "snippet", receipt["id"]
    )
    assert restored["source"] == source and restored["result"] == expected
    assert restored["saved_at"].endswith("+00:00")
    assert restored["source_sha256"] == hashlib.sha256(source.encode()).hexdigest()
    history = store.history("python-01", "python", "snippet")
    assert history[0]["id"] == receipt["id"] and history[0]["status"] == "succeeded"
    assert history[0]["returncode"] == 0
    assert "result" not in history[0] and "source" not in history[0]


def test_language_mode_and_lesson_histories_are_isolated(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    contexts = [
        ("sql-01", "python", "snippet"),
        ("sql-01", "sql", "snippet"),
        ("sql-01", "sql", "lesson"),
        ("python-01", "python", "snippet"),
    ]
    receipts = []
    for lesson, language, mode in contexts:
        receipts.append(
            store.record(lesson, language, mode, "source", {**result, "language": language})
        )
    for context, receipt in zip(contexts, receipts, strict=True):
        assert [item["id"] for item in store.history(*context)] == [receipt["id"]]
        assert store.get(*context, receipt["id"])["source"] == "source"
    with pytest.raises(ValueError, match="not found"):
        store.get("sql-01", "sql", "snippet", receipts[0]["id"])


@pytest.mark.parametrize(
    "code,stopped,status",
    [
        (0, None, "succeeded"),
        (1, None, "failed"),
        (-9, "time limit", "timed_out"),
        (0, "output limit", "failed"),
    ],
)
def test_status_derives_from_actual_execution(
    tmp_path: Path,
    catalog: Catalog,
    result: dict[str, Any],
    code: int,
    stopped: str | None,
    status: str,
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    store.record(
        "python-01", "python", "snippet", "x", {**result, "returncode": code, "stopped": stopped}
    )
    assert store.history("python-01", "python", "snippet")[0]["status"] == status


def test_concurrent_append_is_immutable_and_history_limit_never_deletes(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    def record(number: int) -> dict[str, Any]:
        return ClassroomRunStore(catalog, tmp_path).record(
            "python-01", "python", "snippet", f"print({number})", {**result, "output": str(number)}
        )

    with ThreadPoolExecutor(max_workers=6) as executor:
        receipts = list(executor.map(record, range(16)))
    assert len({row["id"] for row in receipts}) == 16 and len(files(tmp_path)) == 16
    store = ClassroomRunStore(catalog, tmp_path)
    history = store.history("python-01", "python", "snippet", limit=3)
    assert len(history) == 3 and len(files(tmp_path)) == 16
    assert [item["saved_at"] for item in history] == sorted(
        (item["saved_at"] for item in receipts), reverse=True
    )[:3]
    for receipt in receipts:
        assert store.get("python-01", "python", "snippet", receipt["id"]) == receipt


def test_mocked_uuid_collision_refuses_to_overwrite(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "ds60sqlpy.classroom_runs.uuid.uuid4", lambda: SimpleNamespace(hex="a" * 32)
    )
    store = ClassroomRunStore(catalog, tmp_path)
    first = store.record("python-01", "python", "snippet", "first", result)
    content = files(tmp_path)[0].read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        store.record("python-01", "python", "snippet", "second", result)
    assert len(files(tmp_path)) == 1 and files(tmp_path)[0].read_bytes() == content
    assert store.get("python-01", "python", "snippet", first["id"])["source"] == "first"


@pytest.mark.parametrize(
    "lesson,language,mode",
    [
        ("unknown", "python", "snippet"),
        ("../python-01", "python", "snippet"),
        ("python-01", "cpp", "snippet"),
        ("python-01", "none", "snippet"),
        ("python-01", "../../sql", "snippet"),
        ("python-01", "python", "../snippet"),
        ("python-01", "python", "lesson"),
        ("python-01", "sql", "lesson"),
    ],
)
def test_invalid_context_never_creates_storage(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], lesson: str, language: str, mode: str
) -> None:
    store = ClassroomRunStore(catalog, tmp_path / "runs")
    with pytest.raises((ValueError, KeyError)):
        store.record(lesson, language, mode, "x", result)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("limit", [0, 51, -1, True, 1.5, "5"])
def test_history_limits_are_strict_and_read_only(
    tmp_path: Path, catalog: Catalog, limit: Any
) -> None:
    store = ClassroomRunStore(catalog, tmp_path / "runs")
    with pytest.raises(ValueError, match="limit"):
        store.history("python-01", "python", "snippet", limit)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("identifier", ["../secret", "a" * 31, "a" * 33, "A" * 32, "*", "", None])
def test_bad_receipt_ids_never_read_arbitrary_files(
    tmp_path: Path, catalog: Catalog, identifier: Any
) -> None:
    with pytest.raises(ValueError, match="receipt ID"):
        ClassroomRunStore(catalog, tmp_path / "runs").get(
            "python-01", "python", "snippet", identifier
        )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "change",
    [
        {"returncode": True},
        {"returncode": 2**40},
        {"stopped": []},
        {"elapsed_seconds": 10**500},
        {"output": "a" * (MAX_OUTPUT_BYTES + 1)},
        {"output": "🙂" * (MAX_OUTPUT_BYTES // 4 + 1)},
        {"elapsed_seconds": float("nan")},
        {"elapsed_seconds": float("inf")},
        {"elapsed_seconds": -1},
        {"elapsed_seconds": True},
        {"language": "sql"},
        {"stopped": "unknown"},
        {"source_sha256": "0" * 64},
        {"mode": "lesson"},
        {"figures": ["https://example.invalid/track.png"]},
        {"figures": ["data:image/png;base64,invalid!"]},
        {"figures": ["data:image/png;base64,YmFk"]},
        {"figures": [None]},
        {"output_truncated": "yes"},
        {"extra": "a" * 2_000_001},
        {"invalid": {1: "not a string key"}},
    ],
)
def test_result_bounds_and_integrity_are_validated_before_write(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], change: dict[str, Any]
) -> None:
    with pytest.raises(ValueError):
        ClassroomRunStore(catalog, tmp_path / "runs").record(
            "python-01", "python", "snippet", "x", {**result, **change}
        )
    assert not list(tmp_path.iterdir())


def test_source_size_is_utf8_bounded(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    source = "🙂" * (MAX_CODE_BYTES // 4)
    assert store.record("python-01", "python", "snippet", source, result)["source"] == source
    with pytest.raises(ValueError, match="source"):
        store.record("python-01", "python", "snippet", source + "x", result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("lesson_id", "sql-01"),
        ("language", "sql"),
        ("mode", "lesson"),
        ("id", "b" * 32),
        ("source_sha256", "f" * 64),
        ("saved_at", "2020-01-01T00:00:00"),
        ("schema_version", True),
    ],
)
def test_tampered_receipt_is_reported_and_preserved(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], field: str, value: Any
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    receipt = store.record("python-01", "python", "snippet", "x", result)
    path = files(tmp_path)[0]
    payload = json.loads(path.read_text())
    payload[field] = value
    path.write_text(json.dumps(payload))
    original = path.read_bytes()
    with pytest.raises(ValueError):
        store.get("python-01", "python", "snippet", receipt["id"])
    with pytest.raises(ValueError):
        store.history("python-01", "python", "snippet")
    assert path.read_bytes() == original


def test_corrupt_and_oversized_files_fail_before_being_removed_or_loaded(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    receipt = store.record("python-01", "python", "snippet", "x", result)
    path = files(tmp_path)[0]
    path.write_text("{corrupt")
    with pytest.raises(ValueError, match="corrupt"):
        store.history("python-01", "python", "snippet")
    assert path.read_text() == "{corrupt"
    with path.open("wb") as stream:
        stream.truncate(MAX_RECEIPT_BYTES + 1)
    monkeypatch.setattr(
        "ds60sqlpy.classroom_runs.json.loads", lambda _x: pytest.fail("oversized JSON loaded")
    )
    with pytest.raises(ValueError, match="oversized"):
        store.get("python-01", "python", "snippet", receipt["id"])
    assert path.stat().st_size == MAX_RECEIPT_BYTES + 1


@pytest.mark.parametrize("location", ["directory", "lesson", "language", "mode", "lock"])
def test_directory_and_mutation_lock_symlinks_are_blocked(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], location: str
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    directory = tmp_path / "runs"
    components = {
        "directory": directory,
        "lesson": directory / "python-01",
        "language": directory / "python-01" / "python",
        "mode": directory / "python-01" / "python" / "snippet",
        "lock": directory / "python-01" / "python" / "snippet" / ".write.lock",
    }
    link = components[location]
    link.parent.mkdir(parents=True, exist_ok=True)
    target = outside if location != "lock" else outside / "lock"
    if location == "lock":
        target.write_text("keep")
    try:
        link.symlink_to(target, target_is_directory=location != "lock")
    except OSError:
        pytest.skip("Symbolic links are unavailable on this host")
    store = ClassroomRunStore(catalog, directory)
    with pytest.raises(ValueError, match="symbolic"):
        store.record("python-01", "python", "snippet", "x", result)
    assert list(outside.iterdir()) == ([target] if location == "lock" else [])


def test_receipt_symlink_and_duplicate_identity_are_not_followed(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    store = ClassroomRunStore(catalog, tmp_path / "runs")
    receipt = store.record("python-01", "python", "snippet", "x", result)
    path = files(tmp_path)[0]
    original = path.read_bytes()
    outside = tmp_path / "private.json"
    outside.write_bytes(original)
    path.unlink()
    try:
        path.symlink_to(outside)
    except OSError:
        pytest.skip("Symbolic links are unavailable on this host")
    with pytest.raises(ValueError, match="symbolic"):
        store.get("python-01", "python", "snippet", receipt["id"])
    assert outside.read_bytes() == original
    path.unlink()
    path.write_bytes(original)
    duplicate = path.with_name("19990101T000000000000Z_" + receipt["id"] + ".json")
    duplicate.write_bytes(original)
    with pytest.raises(ValueError, match="uniquely"):
        store.get("python-01", "python", "snippet", receipt["id"])
    with pytest.raises(ValueError, match="duplicate"):
        store.history("python-01", "python", "snippet")


def test_write_failure_retains_previous_history_and_is_not_swallowed(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    first = store.record("python-01", "python", "snippet", "first", result)
    before = files(tmp_path)[0].read_bytes()

    def fail_write(_path: Path, _payload: dict[str, Any]) -> None:
        raise OSError("simulated disk failure")

    monkeypatch.setattr("ds60sqlpy.classroom_runs.atomic_json_write", fail_write)
    with pytest.raises(OSError, match="disk failure"):
        store.record("python-01", "python", "snippet", "second", result)
    assert len(files(tmp_path)) == 1 and files(tmp_path)[0].read_bytes() == before
    assert store.get("python-01", "python", "snippet", first["id"])["source"] == "first"


def test_deeply_corrupt_json_is_reported_without_rewriting(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    store = ClassroomRunStore(catalog, tmp_path)
    receipt = store.record("python-01", "python", "snippet", "x", result)
    path = files(tmp_path)[0]
    damaged = "[" * 2000 + "]" * 2000
    path.write_text(damaged)
    with pytest.raises(ValueError, match="corrupt"):
        store.get("python-01", "python", "snippet", receipt["id"])
    assert path.read_text() == damaged


def test_largest_execution_figures_and_escaped_transcript_fit_storage(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    png = b"\x89PNG\r\n\x1a\n" + bytes(2_000_000 - 8)
    figure = "data:image/png;base64," + base64.b64encode(png).decode()
    data = {**result, "figures": [figure] * 4, "output": "\0" * MAX_OUTPUT_BYTES}
    store = ClassroomRunStore(catalog, tmp_path)
    receipt = store.record("python-01", "python", "snippet", "\0" * MAX_CODE_BYTES, data)
    restored = store.get("python-01", "python", "snippet", receipt["id"])
    assert restored["result"] == data
    assert files(tmp_path)[0].stat().st_size < MAX_RECEIPT_BYTES


def test_configured_parent_traversal_is_rejected_without_creation(
    tmp_path: Path, catalog: Catalog
) -> None:
    with pytest.raises(ValueError, match="parent traversal"):
        ClassroomRunStore(catalog, tmp_path / "a" / ".." / "runs")
    assert not list(tmp_path.iterdir())


def test_missing_path_checks_resolve_only_existing_ancestors_without_creating_them(
    tmp_path: Path, catalog: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "absent"
    original = Path.resolve
    calls: list[tuple[Path, bool]] = []

    def observed(path: Path, strict: bool = False) -> Path:
        if path.is_relative_to(missing):
            calls.append((path, strict))
            assert strict, "Missing descendants must not use non-strict Windows resolution."
        return original(path, strict=strict)

    monkeypatch.setattr(Path, "resolve", observed)
    store = ClassroomRunStore(catalog, missing / "runs")
    target = store.directory / "python-01/python/snippet/.write"
    assert store._safe_path(target) == target
    assert calls and all(strict for _, strict in calls)
    assert not missing.exists()


@pytest.mark.skipif(os.name != "nt", reason="Exercises Windows GetFinalPathName error transitions")
def test_parent_creation_during_windows_resolution_does_not_change_containment_anchor(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = tmp_path / "runs"
    context = directory / "python-01/python/snippet"
    resolver = getattr(ntpath, "_getfinalpathname", None)
    assert callable(resolver), "CPython Windows final-path resolution is unavailable."
    original = cast(Callable[[str], str], resolver)
    created = False

    def create_parent_between_probes(path: str) -> str:
        nonlocal created
        if ntpath.normcase(path) == ntpath.normcase(str(context)) and not created:
            try:
                return original(path)
            except FileNotFoundError as error:
                assert (
                    getattr(error, "winerror", None) == 3
                )  # ERROR_PATH_NOT_FOUND before parent creation.
                context.parent.mkdir(parents=True)
                created = True
                # A second probe now reports ERROR_FILE_NOT_FOUND (2), which can
                # make non-strict realpath retain a different extended-path anchor.
                with pytest.raises(FileNotFoundError) as next_probe:
                    original(path)
                assert getattr(next_probe.value, "winerror", None) == 2
                raise
        return original(path)

    monkeypatch.setattr(ntpath, "_getfinalpathname", create_parent_between_probes)
    store = ClassroomRunStore(catalog, directory)
    saved = store.record("python-01", "python", "snippet", "print(42)", result)
    assert created
    assert store.get("python-01", "python", "snippet", saved["id"]) == saved


def test_changed_parent_cannot_redirect_history_outside_its_original_boundary(
    tmp_path: Path, catalog: Catalog, result: dict[str, Any]
) -> None:
    parent = tmp_path / "parent"
    outside = tmp_path / "outside"
    parent.mkdir()
    outside.mkdir()
    store = ClassroomRunStore(catalog, parent / "runs")
    parent.rename(tmp_path / "retained-parent")
    try:
        parent.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symbolic links are unavailable on this host")
    with pytest.raises(ValueError, match="escaped"):
        store.record("python-01", "python", "snippet", "print(42)", result)
    assert list(outside.iterdir()) == []


def test_link_created_during_resolution_is_rechecked_before_storage(
    tmp_path: Path, catalog: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy import classroom_runs
    from ds60sqlpy.state_files import resolve_existing_ancestor

    directory = tmp_path / "runs"
    outside = tmp_path / "outside"
    directory.mkdir()
    outside.mkdir()
    store = ClassroomRunStore(catalog, directory)
    original = resolve_existing_ancestor
    target = directory / "python-01/python/snippet/.write"

    def introduce_link(path: Path) -> Path:
        resolved = original(path)
        try:
            (directory / "python-01").symlink_to(outside, target_is_directory=True)
        except OSError:
            pytest.skip("Symbolic links are unavailable on this host")
        return resolved

    monkeypatch.setattr(classroom_runs, "_resolve_existing_ancestor", introduce_link)
    with pytest.raises(ValueError, match="symbolic"):
        store._safe_path(target)
    assert list(outside.iterdir()) == []
