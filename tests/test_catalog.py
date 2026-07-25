from __future__ import annotations

from pathlib import Path

from ds60sqlpy.catalog import Catalog, find_repo_root


def test_find_repo_root_from_nested_directory() -> None:
    root = find_repo_root(Path(__file__).parent)
    assert (root / "pyproject.toml").is_file()


def test_catalog_has_all_complete_tracks() -> None:
    catalog = Catalog.load()
    assert len(catalog.lessons("python")) == 60
    assert len(catalog.lessons("sql")) == 60
    assert len(catalog.lessons("bridge")) == 8
    assert catalog.by_day("python", 1).id == "python-01"
    assert catalog.by_day("sql", 60).id == "sql-60"
    assert catalog.by_day("bridge", 8).id == "bridge-08"


def test_bridge_starts_after_python_and_sql_foundations() -> None:
    catalog = Catalog.load()

    assert catalog.by_day("bridge", 1).prerequisites == ("python-15", "sql-15")
    assert catalog.by_day("bridge", 2).prerequisites == ("bridge-01",)


def test_catalog_paths_stay_inside_repository() -> None:
    catalog = Catalog.load()
    for lesson in catalog:
        assert catalog.resolve(lesson.lesson_path).is_relative_to(catalog.repo_root)


def test_catalog_prerequisites_reference_known_lessons() -> None:
    catalog = Catalog.load()
    lesson_ids = {lesson.id for lesson in catalog}

    for lesson in catalog:
        assert set(lesson.prerequisites) <= lesson_ids
