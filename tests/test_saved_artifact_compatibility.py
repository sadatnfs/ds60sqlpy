"""Historical Plotly readback retains exact data without weakening new writes."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom_runs import ClassroomRunStore
from ds60sqlpy.module_jobs import ModuleJobs, WorkerClient
from ds60sqlpy.modules import ModuleCatalog, ModuleState
from ds60sqlpy.plot_artifacts import (
    MAX_ARTIFACT_BYTES,
    MAX_PLOT_BYTES,
    publish_artifact,
    read_saved_artifacts,
    validate_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]
UNSAFE = 9_007_199_254_740_993


def chart(value: Any = 7, location: str = "table") -> dict[str, Any]:
    figure: dict[str, Any] = {
        "data": [{"type": "scatter", "x": [0], "y": [1]}],
        "layout": {
            "meta": {
                "description": "Saved exact values",
                "table": {"columns": ["record_id"], "rows": [[7]]},
            }
        },
    }
    if location == "table":
        figure["layout"]["meta"]["table"]["rows"] = [[value]]
    elif location == "trace":
        figure["data"][0]["customdata"] = [value]
    elif location == "frame":
        figure["frames"] = [
            {
                "name": "saved",
                "data": [
                    {
                        "type": "scatter",
                        "x": [0],
                        "y": [1],
                        "customdata": [value],
                    }
                ],
            }
        ]
    else:
        raise AssertionError(location)
    return {"kind": "plotly", "figure": figure}


@pytest.mark.parametrize("value", [UNSAFE, -UNSAFE])
@pytest.mark.parametrize("location", ["trace", "table", "frame"])
def test_historical_integer_is_downloaded_as_exact_numeric_text(value: int, location: str) -> None:
    original = chart(value, location)
    before = copy.deepcopy(original)
    visible, withheld = read_saved_artifacts([original])
    assert visible == [] and len(withheld) == 1
    assert original == before
    assert withheld[0]["position"] == 1
    assert "not rendered" in withheld[0]["reason"]
    expected = json.dumps(original["figure"], ensure_ascii=True, allow_nan=False)
    assert withheld[0]["raw_json"] == expected
    assert str(value) in withheld[0]["raw_json"]
    assert json.loads(withheld[0]["raw_json"]) == original["figure"]
    assert len(withheld[0]["raw_json"].encode()) <= MAX_PLOT_BYTES
    with pytest.raises(ValueError, match="integer"):
        validate_artifacts([original])


@pytest.mark.parametrize(
    "value", [9_007_199_254_740_991, -9_007_199_254_740_991, str(UNSAFE), 1e20]
)
def test_existing_safe_numbers_and_string_identifiers_are_not_modified(value: Any) -> None:
    artifact = chart(value)
    expected = validate_artifacts([artifact])
    visible, withheld = read_saved_artifacts([artifact])
    assert visible == expected and withheld == []
    assert visible[0]["table"]["rows"] == [[value]]


@pytest.mark.parametrize("bad_position", [0, 1])
def test_safe_sibling_survives_and_original_position_remains_visible(bad_position: int) -> None:
    artifacts = [chart(3), chart(4)]
    artifacts[bad_position] = chart(UNSAFE)
    visible, withheld = read_saved_artifacts(artifacts)
    assert visible == validate_artifacts([artifacts[1 - bad_position]])
    assert withheld[0]["position"] == bad_position + 1


@pytest.mark.parametrize(
    "fault",
    [
        "external-image",
        "frame-image",
        "trace-source",
        "unsupported-trace",
        "bad-table",
        "nan",
        "count",
        "size",
        "unknown-kind",
        "json-unsafe",
    ],
)
def test_unsafe_integer_does_not_hide_other_invalid_artifact_content(fault: str) -> None:
    bad = chart(UNSAFE)
    artifacts = [bad]
    if fault == "external-image":
        bad["figure"]["layout"]["images"] = [{"source": "https://example.invalid/image"}]
    elif fault == "frame-image":
        bad["figure"]["frames"] = [{"layout": {"images": [{"source": "https://example.invalid/"}]}}]
    elif fault == "trace-source":
        bad["figure"]["data"][0]["source"] = "https://example.invalid/image"
    elif fault == "unsupported-trace":
        bad["figure"]["data"][0]["type"] = "scatter3d"
    elif fault == "bad-table":
        bad["figure"]["layout"]["meta"]["table"]["rows"].append([1, 2])
    elif fault == "nan":
        bad["figure"]["data"][0]["y"] = [float("nan")]
    elif fault == "count":
        artifacts = [bad, chart(2), chart(3)]
    elif fault == "size":
        bad["figure"]["layout"]["extra"] = "x" * MAX_PLOT_BYTES
    elif fault == "unknown-kind":
        artifacts.append({"kind": "unknown", "data": "unsupported"})
    else:
        artifacts.append({"kind": "json", "description": "New report", "data": {"id": UNSAFE}})
    with pytest.raises(ValueError):
        read_saved_artifacts(artifacts)


def test_original_budgets_apply_before_download_text_is_escaped_in_response() -> None:
    artifact = chart(UNSAFE, "trace")
    # Many backslashes expand again when raw JSON becomes a JSON string.
    artifact["figure"]["layout"]["title"] = "\\" * 80_000
    encoded = json.dumps(artifact["figure"], allow_nan=False)
    assert 150_000 < len(encoded.encode()) < MAX_PLOT_BYTES
    visible, withheld = read_saved_artifacts([artifact])
    assert visible == []
    assert withheld[0]["raw_json"] == encoded
    assert len(json.dumps(withheld).encode()) > MAX_PLOT_BYTES
    assert sum(len(item["raw_json"].encode()) for item in withheld) <= MAX_ARTIFACT_BYTES


@pytest.fixture(scope="module")
def catalogs() -> tuple[Catalog, ModuleCatalog]:
    return Catalog.load(ROOT), ModuleCatalog(ROOT)


def result() -> dict[str, Any]:
    return {
        "language": "python",
        "returncode": 0,
        "output": "Retained computation\n",
        "elapsed_seconds": 0.125,
        "stopped": None,
        "output_truncated": False,
        "figures": [],
    }


def write_legacy(store: ClassroomRunStore, directory: Path) -> tuple[dict[str, Any], Path]:
    store.record("python-01", "python", "snippet", "print('Retained computation')\n", result())
    path = next(directory.rglob("*.json"))
    data = json.loads(path.read_text())
    data["result"]["artifacts"] = [chart(UNSAFE), chart(8)]
    path.write_text(json.dumps(data))
    return data, path


def write_module(directory: Path, *, status: str = "succeeded") -> tuple[dict[str, Any], Path]:
    directory.mkdir(parents=True, exist_ok=True)
    source = "print('Retained computation')\n"
    data: dict[str, Any] = {
        "schema_version": 1,
        "job_id": "a" * 32,
        "lesson_id": "llm-002",
        "profile": "python-core",
        "source": source,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "verification_id": None,
        "status": status,
        "returncode": 0,
        "output": "Retained computation\n",
        "checks": [],
        "truncated": False,
        "elapsed_seconds": 0.125,
        "timeout_seconds": 60,
        "created_at": "2026-10-01T00:00:00+00:00",
        "artifacts": [chart(UNSAFE), chart(8)],
    }
    path = directory / (data["job_id"] + ".json")
    path.write_text(json.dumps(data))
    return data, path


class NeverExecute(WorkerClient):
    def __init__(self) -> None:
        super().__init__({})
        self.calls: list[str] = []

    def call(
        self, profile: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.calls.append(path)
        raise AssertionError("Saved completed receipts must not contact a worker")

    def readiness(self, profile: str) -> dict[str, Any]:
        raise AssertionError("Saved completed receipts must not probe a worker")


def test_legacy_get_and_history_retain_source_output_identity_and_original_bytes(
    tmp_path: Path, catalogs: tuple[Catalog, ModuleCatalog]
) -> None:
    store = ClassroomRunStore(catalogs[0], tmp_path)
    original, path = write_legacy(store, tmp_path)
    before = path.read_bytes()
    saved = store.get("python-01", "python", "snippet", original["id"])
    assert saved["source"] == original["source"]
    assert saved["source_sha256"] == original["source_sha256"]
    assert saved["result"]["output"] == original["result"]["output"]
    assert saved["result"]["returncode"] == 0
    assert saved["result"]["artifacts"] == validate_artifacts([chart(8)])
    assert len(saved["result"]["withheld_artifacts"]) == 1
    assert store.history("python-01", "python", "snippet")[0]["id"] == original["id"]
    assert path.read_bytes() == before
    with pytest.raises(ValueError, match="integer"):
        store.record(
            "python-01", "python", "snippet", "new", {**result(), "artifacts": [chart(UNSAFE)]}
        )


def test_module_reconstruction_idempotency_and_unrelated_history_are_read_only(
    tmp_path: Path, catalogs: tuple[Catalog, ModuleCatalog]
) -> None:
    state = ModuleState(catalogs[1], tmp_path / "modules")
    original, path = write_module(state.directory / "jobs")
    before = path.read_bytes()
    client = NeverExecute()
    jobs = ModuleJobs(catalogs[1], state, client)
    saved = jobs.get(original["job_id"])
    assert saved["source"] == original["source"]
    assert saved["output"] == original["output"]
    assert saved["status"] == original["status"]
    assert saved["artifacts"] == validate_artifacts([chart(8)])
    assert len(saved["withheld_artifacts"]) == 1
    assert jobs.history("cpp-009") == []
    assert jobs.history("llm-002")[0] == saved
    assert jobs.start("llm-002", original["source"], 60, original["job_id"]) == saved
    assert jobs.cancel(original["job_id"]) == saved
    assert jobs.recover(original["job_id"], None) == saved
    assert client.calls == []
    assert path.read_bytes() == before
    assert not state.path.exists()


def test_status_update_keeps_raw_artifacts_and_does_not_persist_projection(
    tmp_path: Path, catalogs: tuple[Catalog, ModuleCatalog]
) -> None:
    state = ModuleState(catalogs[1], tmp_path / "modules")
    jobs = ModuleJobs(catalogs[1], state, NeverExecute())
    original, path = write_module(state.directory / "jobs", status="interrupted")
    response = jobs._update(original["job_id"], {"detail": "Reviewed status only"})
    stored = json.loads(path.read_text())
    assert stored["artifacts"] == original["artifacts"]
    assert stored["source_sha256"] == original["source_sha256"]
    assert "withheld_artifacts" not in stored
    assert response["withheld_artifacts"][0]["position"] == 1
    assert response["artifacts"] == validate_artifacts([chart(8)])
    with pytest.raises(ValueError, match="cannot be written"):
        jobs._update(original["job_id"], {"withheld_artifacts": []})
    with pytest.raises(ValueError, match="integer"):
        jobs._update(original["job_id"], {"artifacts": [chart(UNSAFE)]})


def test_new_worker_snapshot_and_publisher_stay_strict(
    tmp_path: Path, catalogs: tuple[Catalog, ModuleCatalog], monkeypatch: pytest.MonkeyPatch
) -> None:
    state = ModuleState(catalogs[1], tmp_path / "modules")
    jobs = ModuleJobs(catalogs[1], state, NeverExecute())
    original, _ = write_module(state.directory / "jobs")
    with pytest.raises(ValueError, match="integer"):
        jobs._snapshot(original, original["job_id"])
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="integer"):
        publish_artifact(chart(UNSAFE))
    assert not (tmp_path / "ds60-figures.json").exists()


@pytest.mark.parametrize("kind", ["legacy", "module"])
def test_malformed_saved_artifact_still_rejects_without_rewriting(
    kind: str, tmp_path: Path, catalogs: tuple[Catalog, ModuleCatalog]
) -> None:
    if kind == "legacy":
        store = ClassroomRunStore(catalogs[0], tmp_path)
        record, path = write_legacy(store, tmp_path)
        target = record["result"]
    else:
        state = ModuleState(catalogs[1], tmp_path / "modules")
        record, path = write_module(state.directory / "jobs")
        target = record
    target["artifacts"][0]["figure"]["layout"]["images"] = [{"source": "https://example.invalid/"}]
    path.write_text(json.dumps(record))
    before = path.read_bytes()
    with pytest.raises(ValueError, match="images"):
        if kind == "legacy":
            store.get("python-01", "python", "snippet", record["id"])
        else:
            ModuleJobs(catalogs[1], state, NeverExecute())
    assert path.read_bytes() == before


@pytest.mark.parametrize("kind", ["legacy", "module"])
def test_derived_download_metadata_is_never_trusted_from_storage(
    kind: str, tmp_path: Path, catalogs: tuple[Catalog, ModuleCatalog]
) -> None:
    if kind == "legacy":
        store = ClassroomRunStore(catalogs[0], tmp_path)
        record, path = write_legacy(store, tmp_path)
        record["result"]["withheld_artifacts"] = [{"raw_json": "forged"}]
    else:
        state = ModuleState(catalogs[1], tmp_path / "modules")
        record, path = write_module(state.directory / "jobs")
        record["withheld_artifacts"] = [{"raw_json": "forged"}]
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="derived"):
        if kind == "legacy":
            store.get("python-01", "python", "snippet", record["id"])
        else:
            ModuleJobs(catalogs[1], state, NeverExecute())


def test_original_raw_json_download_uses_real_browser_bytes() -> None:
    api = pytest.importorskip(
        "playwright.sync_api", reason="Requires the separately prepared Chromium environment"
    )
    source = (ROOT / "src/ds60sqlpy/assets/classroom.js").read_text()
    helper = source.split("// BEGIN SAVED FIGURE DOWNLOAD HELPERS", 1)[1].split(
        "// END SAVED FIGURE DOWNLOAD HELPERS", 1
    )[0]
    artifacts = [chart(UNSAFE, "trace"), chart(-UNSAFE, "table")]
    _, withheld = read_saved_artifacts(artifacts)
    withheld[0]["reason"] += ' Literal text: <img src="https://example.invalid/">'
    with api.sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True, channel="chromium")
        context = browser.new_context(accept_downloads=True)
        requests: list[str] = []
        context.on("request", lambda request: requests.append(request.url))
        page = context.new_page()
        try:
            page.set_content('<main><div id="figures"></div></main>')
            page.add_script_tag(
                content="""
                const $ = id => document.getElementById(id);
                function node(tag, text, className) {
                  const element = document.createElement(tag);
                  if (text !== undefined) element.textContent = text;
                  if (className) element.className = className;
                  return element;
                }
            """
                + helper
            )
            page.evaluate("records => showWithheldArtifacts(records)", withheld)
            assert page.locator(".withheld-figure").count() == 2
            assert page.locator("#figures img, #figures iframe").count() == 0
            for index, record in enumerate(withheld):
                button = page.locator(".withheld-figure button").nth(index)
                button.scroll_into_view_if_needed()
                with page.expect_download() as download:
                    button.click()
                value = download.value
                assert value.suggested_filename == f"saved-figure-{index + 1}.json"
                raw = Path(value.path()).read_bytes()
                assert raw == record["raw_json"].encode()
                assert json.loads(raw) == artifacts[index]["figure"]
                assert str(UNSAFE).encode() in raw
            assert not requests
        finally:
            context.close()
            browser.close()
