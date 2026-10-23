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
from ds60sqlpy.journey_design import TRACK_IDS, compile_preview, load_designs
from ds60sqlpy.lab import LabServer


@pytest.fixture
def design_root(tmp_path: Path) -> Path:
    source = Catalog.load().repo_root
    for relative in ("python/ds-60day", "sql/postgres-60day"):
        (tmp_path / relative).mkdir(parents=True)
    for folder in ("docs/expansion/plans", "docs/expansion/samples"):
        shutil.copytree(source / folder, tmp_path / folder)
    for relative in (
        "pyproject.toml",
        "curriculum/catalog.json",
        "src/ds60sqlpy/assets/journey_preview.template.html",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
    return tmp_path


def test_designs_are_distinct_from_published_catalog_and_preview_is_current() -> None:
    root = Catalog.load().repo_root
    before = (root / "curriculum/catalog.json").read_bytes()
    plans = load_designs(root)
    assert tuple(plan["id"] for plan in plans) == TRACK_IDS
    active_ids = {lesson.id for lesson in Catalog.load(root)}
    assert all(plan["status"] == "planned" for plan in plans)
    assert not active_ids.intersection(lesson["id"] for p in plans for lesson in p["lessons"])
    assert (root / "curriculum/catalog.json").read_bytes() == before
    assert compile_preview(root) == (root / "src/ds60sqlpy/assets/journey_preview.html").read_text()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("status", "published", "planned status"),
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
        load_designs(design_root)


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
        load_designs(design_root)


@pytest.mark.parametrize(
    "failure", ["outside", "same-file", "same-canonical-file", "answer", "hints", "lesson-type"]
)
def test_pilot_requires_separate_safe_artifacts_and_real_reasoning_check(
    design_root: Path, failure: str
) -> None:
    target = design_root / "docs/expansion/plans/llm-theory.json"
    plan = json.loads(target.read_text())
    pilot = plan["pilot"]
    if failure == "outside":
        pilot["guide_path"] = "../../private.md"
    elif failure == "same-file":
        pilot["solution_path"] = pilot["guide_path"]
    elif failure == "same-canonical-file":
        path = Path(pilot["guide_path"])
        pilot["solution_path"] = str(path.parent) + "/./" + path.name
    elif failure == "lesson-type":
        pilot["lesson_id"] = {}
    elif failure == "answer":
        pilot["prediction"]["correct_index"] = len(pilot["prediction"]["choices"])
    else:
        pilot["hint_steps"] = ["One hint"]
    target.write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        load_designs(design_root)


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
        load_designs(design_root)


def test_authored_script_text_cannot_escape_json_container(design_root: Path) -> None:
    target = design_root / "docs/expansion/plans/cpp.json"
    plan = json.loads(target.read_text())
    attack = '</script><script>alert("source")</script>\u2028&'
    plan["pilot"]["code"] = attack
    target.write_text(json.dumps(plan))
    html = compile_preview(design_root)
    assert attack not in html
    assert "\\u003c/script\\u003e" in html
    assert "\\u2028" in html
    assert "innerHTML" not in html
    assert "fetch(" not in html


def test_preview_route_preserves_host_boundary_and_does_not_create_progress(
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
            assert "DS60 Studio" in html
            assert "Planned; no code has run here" in html
            assert server.token not in html
        request = Request(server.url + "journey-preview", headers={"Host": "untrusted.example"})
        with pytest.raises(HTTPError) as caught:
            urlopen(request, timeout=5)
        assert caught.value.code == 400
        assert set(tmp_path.rglob("*")) == before
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
