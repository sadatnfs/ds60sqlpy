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
    for lesson in payload["lessons"]:
        assert f'"id":"{lesson["id"]}"' in rendered
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
    assert "Double-click" in rendered
    assert "You are in portable reading mode." in rendered
    assert "Private launcher mode is active." in rendered
    assert 'id="run-sql"' in rendered
    assert "Open SQL workspace" in rendered
    assert 'launchNative("jupyter-sql"' in rendered
    assert 'launchNative("jupyter-lesson"' in rendered
    assert "Open PostgreSQL magics lab" in rendered
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
