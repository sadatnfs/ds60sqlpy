"""Tutorial metadata, publication and local-content boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.module_extensions import load_book, load_extra_plans, validate_graph


def book(root: Path) -> tuple[Path, dict[str, Any]]:
    folder = root / "courses/statistics-ml"
    folder.mkdir(parents=True)
    value = {
        "schema_version": 1,
        "id": "statistics-ml",
        "title": "Statistics",
        "mode": "tutorial",
        "chapters": [
            {
                "id": "statistics-001",
                "title": "Inference",
                "chapter_path": "courses/statistics-ml/one.md",
                "example_paths": ["courses/statistics-ml/one.py"],
                "topic_ids": ["stat-01-01"],
                "prerequisites": [],
                "level": "foundation",
                "minutes": 90,
            }
        ],
    }
    path = folder / "manifest.json"
    path.write_text(json.dumps(value))
    return path, value


def test_unwritten_chapter_is_planned_until_guide_and_example_exist(tmp_path: Path) -> None:
    path, _ = book(tmp_path)
    result = load_book(tmp_path)
    assert result is not None and result[0]["lessons"][0]["learning_mode"] == "tutorial"
    assert result[1]["lessons"] == []
    (path.parent / "one.md").write_text("# Inference\nA worked explanation.")
    assert load_book(tmp_path)[1]["lessons"] == []  # type: ignore[index]
    (path.parent / "one.py").write_text("print(42)\n")
    result = load_book(tmp_path)
    assert result is not None
    lesson = result[1]["lessons"][0]
    assert lesson["solution_paths"] == [] and lesson["verification_id"] is None
    assert lesson["runtime_profile"] == "python-core"


@pytest.mark.parametrize(
    "field,value",
    [
        ("chapter_path", "../outside.md"),
        ("chapter_path", "/tmp/private.md"),
        ("chapter_path", "courses/cpp/guide.md"),
        ("chapter_path", "courses/statistics-ml/../cpp/guide.md"),
        ("example_paths", ["courses/statistics-ml/main.sh"]),
        ("example_paths", []),
        ("minutes", True),
        ("level", "expertish"),
    ],
)
def test_book_rejects_invalid_paths_and_unusable_metadata(
    tmp_path: Path, field: str, value: Any
) -> None:
    path, payload = book(tmp_path)
    payload["chapters"][0][field] = value
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_book(tmp_path)


def test_book_refuses_even_in_repo_symlink(tmp_path: Path) -> None:
    path, _ = book(tmp_path)
    (path.parent / "actual.md").write_text("private")
    (path.parent / "one.md").symlink_to("actual.md")
    with pytest.raises(ValueError, match="symbolic"):
        load_book(tmp_path)


def test_prerequisite_graph_refuses_cycles_missing_and_duplicates() -> None:
    plan: dict[str, Any] = {
        "id": "new",
        "lessons": [
            {"id": "new-001", "prerequisites": ["legacy"]},
            {"id": "new-002", "prerequisites": ["new-001"]},
        ],
    }
    validate_graph([plan], {"legacy"})
    for parents in (["missing"], ["new-002"]):
        plan["lessons"][0]["prerequisites"] = parents
        with pytest.raises(ValueError, match="prerequisite"):
            validate_graph([plan], {"legacy"})
    with pytest.raises(ValueError, match="Duplicate subject"):
        validate_graph([plan, plan], {"legacy"})


def test_new_subject_rejects_unregistered_runtime(tmp_path: Path) -> None:
    folder = tmp_path / "courses/java"
    folder.mkdir(parents=True)
    rows = [
        {
            "id": f"java-{i:03d}",
            "title": "Types",
            "outcome": "Understand values",
            "lab": "Compile example",
            "verification": "Expected result",
            "level": level,
            "minutes": 60,
            "runtime": "shell-command",
            "prerequisites": [],
            "concepts": ["types"],
        }
        for i, level in enumerate(("beginner", "intermediate", "advanced"), 1)
    ]
    (folder / "track.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "java",
                "title": "Java",
                "summary": "Java learning",
                "lessons": rows,
            }
        )
    )
    with pytest.raises(ValueError, match="runtime"):
        load_extra_plans(tmp_path, {"java21"})


def test_registered_languages_have_source_admission_rules() -> None:
    from ds60sqlpy.modules import LANGUAGES, SOURCE_SUFFIXES

    languages = {language for supported in LANGUAGES.values() for language in supported}
    assert languages <= SOURCE_SUFFIXES.keys()
    assert SOURCE_SUFFIXES["dax"] == {".dax"}
    assert ".R" in SOURCE_SUFFIXES["r"]
