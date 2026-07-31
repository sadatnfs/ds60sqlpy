from __future__ import annotations

from pathlib import Path

from ds60sqlpy.catalog import Catalog, find_repo_root


def test_find_repo_root_from_nested_directory() -> None:
    root = find_repo_root(Path(__file__).parent)
    assert (root / "pyproject.toml").is_file()


def test_catalog_has_all_complete_tracks() -> None:
    catalog = Catalog.load()
    assert len(catalog.lessons("python")) == 70
    assert len(catalog.lessons("sql")) == 72
    assert len(catalog.lessons("bridge")) == 12
    assert catalog.by_day("python", 1).id == "python-01"
    assert catalog.by_day("sql", 60).id == "sql-60"
    assert catalog.by_day("bridge", 8).id == "bridge-08"
    assert catalog.by_day("sql", -1).id == "sql-found-01"
    assert catalog.by_day("bridge", 9).id == "bridge-jupyter-01"


def test_bridge_starts_after_python_and_sql_foundations() -> None:
    catalog = Catalog.load()

    assert catalog.by_day("bridge", 1).prerequisites == ("python-15", "sql-15")
    assert catalog.by_day("bridge", 2).prerequisites == ("bridge-01",)


def test_sql_track_starts_with_querying_before_relational_engineering() -> None:
    catalog = Catalog.load()
    sql_ids = [lesson.id for lesson in catalog.lessons("sql")]

    assert catalog.by_day("sql", 1).prerequisites == ()
    assert catalog.by_day("sql", -1).prerequisites == ("sql-15",)
    assert catalog.by_day("sql", 16).prerequisites == ("sql-found-01",)
    assert catalog.by_day("sql", 0).prerequisites == ("sql-found-01", "sql-39")
    assert catalog.by_day("sql", 40).prerequisites == ("sql-found-02",)
    assert sql_ids.index("sql-15") < sql_ids.index("sql-found-01") < sql_ids.index("sql-16")
    assert sql_ids.index("sql-39") < sql_ids.index("sql-found-02") < sql_ids.index("sql-40")


def test_catalog_paths_stay_inside_repository() -> None:
    catalog = Catalog.load()
    for lesson in catalog:
        assert catalog.resolve(lesson.lesson_path).is_relative_to(catalog.repo_root)


def test_catalog_prerequisites_reference_known_lessons() -> None:
    catalog = Catalog.load()
    lesson_ids = {lesson.id for lesson in catalog}

    for lesson in catalog:
        assert set(lesson.prerequisites) <= lesson_ids


def test_catalog_prerequisite_graph_is_acyclic() -> None:
    catalog = Catalog.load()
    graph = {lesson.id: lesson.prerequisites for lesson in catalog}
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(lesson_id: str) -> None:
        if lesson_id in visited:
            return
        if lesson_id in visiting:
            raise AssertionError(f"prerequisite cycle reaches {lesson_id}")
        visiting.add(lesson_id)
        for prerequisite in graph[lesson_id]:
            visit(prerequisite)
        visiting.remove(lesson_id)
        visited.add(lesson_id)

    for lesson_id in graph:
        visit(lesson_id)
