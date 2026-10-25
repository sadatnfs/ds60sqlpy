from __future__ import annotations

import json
import shutil
import threading
from dataclasses import replace
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lab import LabServer
from ds60sqlpy.module_plans import TRACK_IDS, load_core_plans


@pytest.fixture
def design_root(tmp_path: Path) -> Path:
    source = Catalog.load().repo_root
    for relative in ("python/ds-60day", "sql/postgres-60day"):
        (tmp_path / relative).mkdir(parents=True)
    for folder in ("docs/expansion/plans",):
        shutil.copytree(source / folder, tmp_path / folder)
    for relative in (
        "pyproject.toml",
        "curriculum/catalog.json",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
    return tmp_path


def test_core_plans_keep_separate_stable_ids_without_changing_legacy_catalog() -> None:
    root = Catalog.load().repo_root
    before = (root / "curriculum/catalog.json").read_bytes()
    plans = load_core_plans(root)
    assert tuple(plan["id"] for plan in plans) == TRACK_IDS
    active_ids = {lesson.id for lesson in Catalog.load(root)}
    assert not active_ids.intersection(lesson["id"] for p in plans for lesson in p["lessons"])
    assert (root / "curriculum/catalog.json").read_bytes() == before


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema_version", True, "schema version"),
        ("entry_prerequisites", ["not-an-active-lesson"], "active lessons"),
        ("runtime_profiles", ["arbitrary-shell"], "runtime profile"),
    ],
)
def test_invalid_track_contract_fails(
    design_root: Path, field: str, value: object, message: str
) -> None:
    target = design_root / "docs/expansion/plans/kubernetes.json"
    plan = json.loads(target.read_text())
    plan[field] = value
    target.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match=message):
        load_core_plans(design_root)


@pytest.mark.parametrize("failure", ["unknown", "cycle", "duplicate", "runtime", "minutes"])
def test_invalid_lesson_graph_and_requirements_fail(design_root: Path, failure: str) -> None:
    target = design_root / "docs/expansion/plans/cpp.json"
    plan = json.loads(target.read_text())
    first, second = plan["lessons"][:2]
    if failure == "unknown":
        first["prerequisites"] = ["missing-001"]
    elif failure == "cycle":
        first["prerequisites"] = [second["id"]]
        second["prerequisites"] = [first["id"]]
    elif failure == "duplicate":
        second["id"] = first["id"]
    elif failure == "runtime":
        first["runtime"] = "unregistered-shell"
    else:
        first["minutes"] = True
    target.write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        load_core_plans(design_root)


@pytest.mark.parametrize("failure", ["capstone-level", "source-date", "source-credentials"])
def test_malformed_capstone_and_source_fields_raise_clear_errors(
    design_root: Path, failure: str
) -> None:
    target = design_root / "docs/expansion/plans/kubernetes.json"
    plan = json.loads(target.read_text())
    if failure == "capstone-level":
        plan["capstones"][0]["level"] = ["beginner"]
    elif failure == "source-date":
        plan["sources"][0]["checked"] = "2026-99-99"
    else:
        plan["sources"][0]["url"] = "https://:secret@example.com/reference"
    target.write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        load_core_plans(design_root)


def test_retired_preview_uses_unified_classroom_without_creating_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = Catalog.load()
    lesson = replace(source.get("python-01"), prerequisites=())
    catalog = Catalog(tmp_path, (lesson,))
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(catalog, progress_path=tmp_path / "progress.json")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    before = set(tmp_path.rglob("*"))
    thread.start()
    try:
        with urlopen(server.url + "journey-preview", timeout=5) as response:
            html = response.read().decode()
            assert response.status == 200
            assert "Content-Security-Policy" in response.headers
            assert "no-store" in response.headers["Cache-Control"]
            assert "/assets/classroom.js" in html
            assert "Planned; no code has run here" not in html
            assert server.token in html
        request = Request(server.url + "journey-preview", headers={"Host": "untrusted.example"})
        with pytest.raises(HTTPError) as caught:
            urlopen(request, timeout=5)
        assert caught.value.code == 400
        assert set(tmp_path.rglob("*")) == before
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("lesson_id", [None, {}, "missing-001", "tf-001"])
def test_default_lesson_must_belong_to_its_subject(design_root: Path, lesson_id: object) -> None:
    target = design_root / "docs/expansion/plans/cpp.json"
    plan = json.loads(target.read_text())
    plan["pilot"]["lesson_id"] = lesson_id
    target.write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        load_core_plans(design_root)


def test_core_plan_cannot_follow_a_link_outside_the_repository(
    design_root: Path, tmp_path: Path
) -> None:
    target = design_root / "docs/expansion/plans/cpp.json"
    outside = tmp_path.parent / (tmp_path.name + "-outside.json")
    outside.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(outside)
    with pytest.raises(ValueError):
        load_core_plans(design_root)
