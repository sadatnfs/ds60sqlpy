from __future__ import annotations

import json
import re
from pathlib import Path

from ds60sqlpy.lesson_reader import COURSE_GUIDE_REFERENCE_PATHS, reference_relative_path
from scripts.build_course_guide import _catalog_payload, build_html, main

REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE = REPO_ROOT / "START_HERE.html"
RAW_LOCAL_ARTIFACT_HREF = re.compile(
    r'href="(?!https?://|mailto:|#)[^"]+\.(?:md|sql|ipynb|py)(?:[?#][^"]*)?"',
    flags=re.IGNORECASE,
)


def test_portable_course_guide_matches_catalog() -> None:
    payload = _catalog_payload()
    rendered = build_html(payload)

    assert GUIDE.read_text(encoding="utf-8") == rendered
    assert f"<strong>{len(payload['lessons'])}</strong><span>cataloged lessons</span>" in rendered
    assert all(lesson.get("tutor_prompt") for lesson in payload["lessons"])
    for lesson in payload["lessons"]:
        assert f'"id":"{lesson["id"]}"' in rendered
        guide_source = (REPO_ROOT / lesson["guide_path"]).read_text(encoding="utf-8")
        assert lesson["tutor_prompt"] in guide_source
    assert "lesson-pages/${lesson.id}.html" in rendered


def test_portable_course_guide_has_no_remote_runtime_dependencies() -> None:
    rendered = GUIDE.read_text(encoding="utf-8")

    assert '<script src="' not in rendered
    assert '<link rel="stylesheet"' not in rendered
    assert "connect-src 'self'" in rendered
    assert 'const SERVER_TOKEN = "";' in rendered
    assert "void loadServerProgress();" in rendered
    assert "localStorage" in rendered
    assert "DS60_DATABASE_URL" in rendered
    assert "START_DS60.cmd" in rendered
    assert "double-click" in rendered.casefold()
    assert "You are in portable reading mode." in rendered
    assert "rendered here as read-only" in rendered
    assert "Private launcher mode is active." in rendered
    assert "[hidden] { display: none !important; }" in rendered
    assert 'id="run-sql"' in rendered
    assert "Open SQL workspace" in rendered
    assert 'launchNative("jupyter-sql"' in rendered
    assert 'launchNative("jupyter-lesson"' in rendered
    assert "Open PostgreSQL magics lab" in rendered
    assert "What the guide gives you before you ask for help" in rendered
    assert "evidence-based done condition" in rendered
    assert 'href="lesson-pages/sql-start-01.html">Start the first SQL lab' in rendered
    assert "Extract All, then double-click <code>START_DOCKER_LAB.cmd</code>" in rendered
    assert "relational design between Days 15–16" in rendered
    assert "Companion guide: ${lesson.guide_path}" in rendered
    assert "Answer-free learner artifact: ${lesson.lesson_path}" in rendered
    assert "Treat every path under solutions/ as closed" in rendered
    assert "Done when:" in rendered
    assert "if (lesson.tutor_prompt)" in rendered
    assert "eager collection building, and lazy generators" in rendered
    assert "Projection, Predicate, Deterministic ordering" in rendered
    assert ".topbar nav {" in rendered
    assert "grid-template-columns: repeat(3, minmax(0, 1fr));" in rendered
    assert "overflow-x: auto; flex-wrap: nowrap;" not in rendered
    assert RAW_LOCAL_ARTIFACT_HREF.search(rendered) is None
    for source_path in COURSE_GUIDE_REFERENCE_PATHS:
        assert f'href="{reference_relative_path(source_path)}"' in rendered


def test_portable_course_guide_has_runnable_windows_resolver() -> None:
    rendered = GUIDE.read_text(encoding="utf-8")

    assert (
        "$CoursePython = if (Test-Path .\\.venv\\Scripts\\python.exe) {\n"
        "    (Resolve-Path .\\.venv\\Scripts\\python.exe).Path\n"
        "} else {\n"
        "    (Resolve-Path .\\.venv\\python.exe).Path\n"
        "}"
    ) in rendered
    assert "$CoursePython = if (Test-Path .\\.venv\\Scripts\\python.exe) {{" not in rendered


def test_registered_tracks_appear_in_filters_progress_and_inventory() -> None:
    payload = _catalog_payload()
    payload["tracks"]["cpp"] = {"title": "C++ systems <practice>", "plan": "README.md"}
    rendered = build_html(payload)

    assert "<strong>4</strong><span>connected tracks</span>" in rendered
    assert '<option value="cpp">C++ systems &lt;practice&gt;</option>' in rendered
    assert 'data-progress-track="cpp"><strong><a href="reference-pages/README.md.html">' in rendered
    assert ">C++ systems &lt;practice&gt;</a></strong>" in rendered
    assert "Object.keys(course.tracks).forEach" in rendered
    assert "trackLessons.length\n          ?" in rendered


def test_embedded_catalog_is_valid_json() -> None:
    rendered = GUIDE.read_text(encoding="utf-8")
    prefix = "const course = "
    start = rendered.index(prefix) + len(prefix)
    end = rendered.index(";\n    const lessons", start)

    payload = json.loads(rendered[start:end])
    assert payload == _catalog_payload()


def test_course_guide_can_write_and_check_an_external_output(tmp_path: Path) -> None:
    output = tmp_path / "portable-course.html"

    assert main(["--output", str(output)]) == 0
    assert main(["--output", str(output), "--check"]) == 0
    assert output.read_text(encoding="utf-8") == build_html(_catalog_payload())
