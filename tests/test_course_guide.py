from __future__ import annotations

import json
from pathlib import Path

from scripts.build_course_guide import _catalog_payload, build_html

REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE = REPO_ROOT / "START_HERE.html"


def test_portable_course_guide_matches_catalog() -> None:
    payload = _catalog_payload()
    rendered = build_html(payload)

    assert GUIDE.read_text(encoding="utf-8") == rendered
    assert (
        f"<strong>{len(payload['lessons'])}</strong><span>cataloged lessons</span>"
        in rendered
    )
    for lesson in payload["lessons"]:
        assert f'"id":"{lesson["id"]}"' in rendered


def test_portable_course_guide_has_no_remote_runtime_dependencies() -> None:
    rendered = GUIDE.read_text(encoding="utf-8")

    assert '<script src="' not in rendered
    assert '<link rel="stylesheet"' not in rendered
    assert "connect-src 'none'" in rendered
    assert "localStorage" in rendered
    assert "DS60_DATABASE_URL" in rendered


def test_embedded_catalog_is_valid_json() -> None:
    rendered = GUIDE.read_text(encoding="utf-8")
    prefix = "const course = "
    start = rendered.index(prefix) + len(prefix)
    end = rendered.index(";\n    const lessons", start)

    payload = json.loads(rendered[start:end])
    assert payload == _catalog_payload()
