"""Persisted browser output is bounded observation, never trusted execution evidence."""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.browser_runs import (
    BROWSER_HISTORY_LIMIT,
    MAX_BROWSER_OUTPUT_BYTES,
    MAX_BROWSER_RECORD_BYTES,
    BrowserRunStore,
)
from ds60sqlpy.catalog import Catalog
from ds60sqlpy.module_service import ModuleService
from ds60sqlpy.modules import MAX_SOURCE_BYTES, ModuleCatalog, ModuleState

ROOT = Path(__file__).resolve().parents[1]
BROWSER_LESSON = "js-043"
OTHER_BROWSER_LESSON = "js-044"


@pytest.fixture(scope="module")
def browser_catalog() -> ModuleCatalog:
    return ModuleCatalog(ROOT)


@pytest.fixture
def browser_store(tmp_path: Path, browser_catalog: ModuleCatalog) -> BrowserRunStore:
    return BrowserRunStore(ModuleState(browser_catalog, tmp_path / "modules"))


def observation(**changes: Any) -> dict[str, Any]:
    return {
        "source": "console.log('observed');",
        "output": "observed\n",
        "status": "succeeded",
        "elapsed_seconds": 0.25,
        **changes,
    }


def record_path(store: BrowserRunStore, receipt: dict[str, Any]) -> Path:
    lesson_id, job_id = receipt["lesson_id"], receipt["job_id"]
    assert isinstance(lesson_id, str) and isinstance(job_id, str)
    return store.state.directory / "browser-runs" / lesson_id / (job_id + ".json")


def test_round_trip_preserves_exact_source_without_claiming_verified_execution(
    browser_store: BrowserRunStore,
) -> None:
    fields = observation(source="const chart = 'é';\nconsole.log(chart);", output="é\n")
    receipt = browser_store.record(BROWSER_LESSON, fields)
    reopened = BrowserRunStore(browser_store.state).get(BROWSER_LESSON, receipt["job_id"])
    assert reopened == receipt
    assert reopened["source_sha256"] == hashlib.sha256(fields["source"].encode()).hexdigest()
    assert reopened["kind"] == reopened["verification_kind"] == "browser_observation"
    assert reopened["verified"] is False
    assert reopened["checks"] == []
    assert reopened["returncode"] is None
    assert reopened["lesson_id"] == BROWSER_LESSON
    assert reopened["profile"] == "javascript-browser"
    assert not browser_store.state.path.exists()


def test_utf8_limits_accept_the_boundary_and_reject_one_extra_byte(
    browser_store: BrowserRunStore,
) -> None:
    fields = observation(
        source="é" * (MAX_SOURCE_BYTES // 2),
        output="😀" * (MAX_BROWSER_OUTPUT_BYTES // 4),
    )
    receipt = browser_store.record(BROWSER_LESSON, fields)
    assert browser_store.get(BROWSER_LESSON, receipt["job_id"])["source"] == fields["source"]
    before = record_path(browser_store, receipt).read_bytes()
    for key in ("source", "output"):
        with pytest.raises(ValueError, match="UTF-8"):
            browser_store.record(BROWSER_LESSON, {**fields, key: fields[key] + "x"})
    assert record_path(browser_store, receipt).read_bytes() == before
    assert len(browser_store.history(BROWSER_LESSON)) == 1


@pytest.mark.parametrize(
    "extra",
    [
        {"verified": True},
        {"checks": [{"name": "forged", "passed": True}]},
        {"returncode": 0},
        {"source_sha256": "0" * 64},
        {"lesson_id": OTHER_BROWSER_LESSON},
        {"profile": "python-core"},
        {"created_at": "2099-01-01T00:00:00+00:00"},
        {"job_id": "a" * 32},
    ],
)
def test_clients_cannot_supply_trusted_identity_or_check_fields(
    browser_store: BrowserRunStore, extra: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="only"):
        browser_store.record(BROWSER_LESSON, observation(**extra))
    assert not browser_store.state.directory.exists()


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "running"},
        {"status": True},
        {"elapsed_seconds": True},
        {"elapsed_seconds": float("nan")},
        {"elapsed_seconds": float("inf")},
        {"elapsed_seconds": -0.01},
        {"elapsed_seconds": 3600.01},
        {"source": ["not text"]},
        {"output": {"not": "text"}},
    ],
)
def test_invalid_client_observations_leave_no_history(
    browser_store: BrowserRunStore, changes: dict[str, Any]
) -> None:
    with pytest.raises(ValueError):
        browser_store.record(BROWSER_LESSON, observation(**changes))
    assert not browser_store.state.directory.exists()


@pytest.mark.parametrize("status", ["succeeded", "failed", "cancelled"])
def test_terminal_client_status_never_inflates_verification(
    browser_store: BrowserRunStore, status: str
) -> None:
    record = browser_store.record(BROWSER_LESSON, observation(status=status))
    assert record["status"] == status
    assert record["verified"] is False and record["checks"] == []
    assert record["returncode"] is None


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "changed without updating the hash"},
        {"source_sha256": "0" * 64},
        {"lesson_id": OTHER_BROWSER_LESSON},
        {"profile": "javascript-node"},
        {"language": "python"},
        {"library": "unreviewed-library"},
        {"verified": True},
        {"checks": [{"passed": True}]},
        {"returncode": 0},
        {"schema_version": True},
        {"job_id": "f" * 32},
        {"created_at": "2025-01-01T00:00:00"},
        {"elapsed_seconds": float("nan")},
        {"unexpected": "preserve me"},
    ],
)
def test_corrupt_history_blocks_reads_and_writes_without_erasing_evidence(
    browser_store: BrowserRunStore, changes: dict[str, Any]
) -> None:
    receipt = browser_store.record(BROWSER_LESSON, observation())
    path = record_path(browser_store, receipt)
    path.write_text(json.dumps({**receipt, **changes}), encoding="utf-8")
    corrupted = path.read_bytes()
    with pytest.raises(ValueError):
        browser_store.get(BROWSER_LESSON, receipt["job_id"])
    with pytest.raises(ValueError):
        browser_store.history(BROWSER_LESSON)
    with pytest.raises(ValueError):
        browser_store.record(BROWSER_LESSON, observation(output="new"))
    assert path.read_bytes() == corrupted
    assert list(path.parent.glob("*.json")) == [path]


@pytest.mark.parametrize("malformed", [b"{partial", b"\xff", b"x" * (MAX_BROWSER_RECORD_BYTES + 1)])
def test_unreadable_or_oversized_history_is_preserved(
    browser_store: BrowserRunStore, malformed: bytes
) -> None:
    receipt = browser_store.record(BROWSER_LESSON, observation())
    path = record_path(browser_store, receipt)
    path.write_bytes(malformed)
    with pytest.raises(ValueError):
        browser_store.record(BROWSER_LESSON, observation())
    assert path.read_bytes() == malformed
    assert len(list(path.parent.glob("*.json"))) == 1


def test_history_and_receipts_stay_bound_to_the_selected_lesson(
    browser_store: BrowserRunStore,
) -> None:
    first = browser_store.record(BROWSER_LESSON, observation(source="first"))
    second = browser_store.record(OTHER_BROWSER_LESSON, observation(source="second"))
    assert [row["job_id"] for row in browser_store.history(BROWSER_LESSON)] == [first["job_id"]]
    with pytest.raises(FileNotFoundError):
        browser_store.get(OTHER_BROWSER_LESSON, first["job_id"])
    copied = record_path(browser_store, second).with_name(first["job_id"] + ".json")
    copied.write_bytes(record_path(browser_store, first).read_bytes())
    with pytest.raises(ValueError, match="identity"):
        browser_store.get(OTHER_BROWSER_LESSON, first["job_id"])
    with pytest.raises(ValueError):
        browser_store.record("java-001", observation())
    with pytest.raises(ValueError):
        browser_store.record("../../outside", observation())


@pytest.mark.parametrize("identity", ["../sessions", "a" * 31, "A" * 32, "a" * 32 + ".json", 1])
def test_receipt_lookup_rejects_noncanonical_names(
    browser_store: BrowserRunStore, identity: object
) -> None:
    with pytest.raises(ValueError, match="ID"):
        browser_store.get(BROWSER_LESSON, identity)
    assert not browser_store.state.directory.exists()


def test_next_save_prunes_valid_interruption_leftovers_without_touching_unknown_files(
    browser_store: BrowserRunStore,
) -> None:
    template = browser_store.record(BROWSER_LESSON, observation())
    directory = record_path(browser_store, template).parent
    record_path(browser_store, template).unlink()
    # Model a previous write completing before pruning was interrupted. All
    # receipts remain independently valid, including those beyond the UI window.
    for index in range(25):
        identity = f"{index:032x}"
        record = {
            **template,
            "job_id": identity,
            "created_at": f"2025-01-{index + 1:02d}T00:00:00+00:00",
        }
        (directory / (identity + ".json")).write_text(json.dumps(record), encoding="utf-8")
    orphan = directory / ".interrupted-write.tmp"
    orphan.write_text("recoverable unknown bytes", encoding="utf-8")
    assert len(browser_store.history(BROWSER_LESSON)) == BROWSER_HISTORY_LIMIT
    assert len(list(directory.glob("*.json"))) == 25  # Reading must not prune.
    latest = browser_store.record(BROWSER_LESSON, observation(output="latest"))
    history = browser_store.history(BROWSER_LESSON)
    assert len(history) == len(list(directory.glob("*.json"))) == BROWSER_HISTORY_LIMIT
    assert history[0]["job_id"] == latest["job_id"]
    assert {row["job_id"] for row in history[1:]} == {f"{i:032x}" for i in range(6, 25)}
    assert orphan.read_text() == "recoverable unknown bytes"


def test_excessive_history_is_not_silently_pruned(browser_store: BrowserRunStore) -> None:
    template = browser_store.record(BROWSER_LESSON, observation())
    directory = record_path(browser_store, template).parent
    record_path(browser_store, template).unlink()
    for index in range(101):
        identity = f"{index:032x}"
        (directory / (identity + ".json")).write_text(
            json.dumps({**template, "job_id": identity}), encoding="utf-8"
        )
    before = {path.name: path.read_bytes() for path in directory.glob("*.json")}
    with pytest.raises(ValueError, match="record limit"):
        browser_store.record(BROWSER_LESSON, observation())
    assert {path.name: path.read_bytes() for path in directory.glob("*.json")} == before


@pytest.mark.parametrize("part", ["modules", "browser-runs", BROWSER_LESSON, ".history.lock"])
def test_browser_history_rejects_symlinked_storage_and_lock_paths(
    browser_store: BrowserRunStore, tmp_path: Path, part: str
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "sentinel"
    sentinel.write_text("keep", encoding="utf-8")
    directory = browser_store.state.directory / "browser-runs" / BROWSER_LESSON
    target = {
        "modules": browser_store.state.directory,
        "browser-runs": browser_store.state.directory / "browser-runs",
        BROWSER_LESSON: directory,
        ".history.lock": directory / ".history.lock",
    }[part]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(sentinel if part == ".history.lock" else outside)
    with pytest.raises(ValueError, match="symbolic link"):
        browser_store.record(BROWSER_LESSON, observation())
    assert sentinel.read_text() == "keep"
    assert sorted(path.name for path in outside.iterdir()) == ["sentinel"]


def test_receipt_symlink_cannot_read_or_overwrite_an_outside_file(
    browser_store: BrowserRunStore, tmp_path: Path
) -> None:
    receipt = browser_store.record(BROWSER_LESSON, observation())
    path = record_path(browser_store, receipt)
    outside = tmp_path / "private.json"
    outside.write_bytes(path.read_bytes())
    before = outside.read_bytes()
    path.unlink()
    path.symlink_to(outside)
    with pytest.raises(ValueError, match="symbolic link"):
        browser_store.get(BROWSER_LESSON, receipt["job_id"])
    with pytest.raises(ValueError, match="symbolic link"):
        browser_store.record(BROWSER_LESSON, observation())
    assert outside.read_bytes() == before


@pytest.fixture
def browser_service(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleService]:
    monkeypatch.setattr("ds60sqlpy.module_service.rendered_targets", lambda _: {})
    service = ModuleService(Catalog.load(), tmp_path / "modules")

    def forbidden_execution(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("Browser history or lesson reads must not submit worker jobs")

    monkeypatch.setattr(service.jobs, "start", forbidden_execution)
    monkeypatch.setattr(service.jobs.client, "readiness", forbidden_execution)
    try:
        yield service
    finally:
        service.close()


def test_service_history_never_overwrites_a_draft_or_runs_saved_source(
    browser_service: ModuleService,
) -> None:
    service = browser_service
    draft = {"source": "const currentDraft = true;", "prediction": "retained notes"}
    service.action({"action": "module-save", "lesson_id": BROWSER_LESSON, "fields": draft})
    before = service.state.path.read_bytes()
    receipt = service.action(
        {"action": "module-browser-record", "lesson_id": BROWSER_LESSON, "fields": observation()}
    )["receipt"]
    history = service.action({"action": "module-browser-history", "lesson_id": BROWSER_LESSON})
    restored = service.action(
        {
            "action": "module-browser-result",
            "lesson_id": BROWSER_LESSON,
            "receipt_id": receipt["job_id"],
        }
    )["receipt"]
    lesson = service.action({"action": "module-lesson", "lesson_id": BROWSER_LESSON})
    assert history["history"] == [restored]
    assert restored["source"] == observation()["source"]
    assert lesson["source"] == draft["source"]
    assert lesson["session"] == draft
    assert lesson["capability"]["execution_location"] == "browser"
    assert service.state.path.read_bytes() == before
    with pytest.raises(ValueError, match="browser preview"):
        service.action({"action": "module-run", "lesson_id": BROWSER_LESSON, "source": "alert(1)"})
    assert service.state.path.read_bytes() == before


def test_history_read_survives_concurrent_twenty_first_save_and_pruning(
    browser_store: BrowserRunStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    for index in range(BROWSER_HISTORY_LIMIT):
        browser_store.record(BROWSER_LESSON, observation(output=f"observation {index}"))
    oldest = browser_store.history(BROWSER_LESSON)[-1]
    old_path = record_path(browser_store, oldest)
    entered = threading.Event()
    release = threading.Event()
    original_read = browser_store._read

    def pause_oldest_read(path: Path, lesson_id: str) -> dict[str, Any]:
        if (
            threading.current_thread().name.startswith("browser-history-reader")
            and path == old_path
        ):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("The test did not release the paused history read.")
        return original_read(path, lesson_id)

    monkeypatch.setattr(browser_store, "_read", pause_oldest_read)
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="browser-history-reader") as pool:
        pending = pool.submit(browser_store.history, BROWSER_LESSON)
        try:
            assert entered.wait(10)
            latest = browser_store.record(BROWSER_LESSON, observation(output="newest"))
            assert not old_path.exists()
        finally:
            release.set()
        observed = pending.result(timeout=10)

    # The reader may observe a bounded older snapshot, but it must not fail
    # because the successful writer removed one of its previously listed rows.
    assert len(observed) == BROWSER_HISTORY_LIMIT - 1
    assert oldest["job_id"] not in {row["job_id"] for row in observed}
    assert all(row["verified"] is False and row["checks"] == [] for row in observed)
    current = browser_store.history(BROWSER_LESSON)
    assert len(current) == BROWSER_HISTORY_LIMIT
    assert current[0] == latest


def test_library_upgrade_reads_old_observations_without_relabeling_them(
    browser_store: BrowserRunStore,
) -> None:
    old = browser_store.record(BROWSER_LESSON, observation())
    old["library"] = "d3@7.9.0"
    path = record_path(browser_store, old)
    original = json.dumps(old).encode()
    path.write_bytes(original)
    restored = browser_store.get(BROWSER_LESSON, old["job_id"])
    assert restored["library"] == "d3@7.9.0"
    new = browser_store.record(BROWSER_LESSON, observation(source="console.log(Plotly.version)"))
    assert new["library"] == "d3@7.9.0+plotly@4.1.2"
    assert path.read_bytes() == original
    assert len(browser_store.history(BROWSER_LESSON)) == 2
