"""Admission and route regressions for current PostgreSQL lessons."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog, Lesson
from ds60sqlpy.catalog_builder import _sql_title
from scripts.audit_lesson_depth import measure_lesson
from scripts.audit_practice import count_practice, practice_targets
from scripts.sql_formatting import sql_for_parser

ROOT = Path(__file__).resolve().parents[1]
RECORDS = json.loads((ROOT / "curriculum/extensions/sql-postgresql17.json").read_text())["lessons"]
LESSONS = [Lesson.from_mapping(record) for record in RECORDS]


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
def test_postgresql17_lessons_have_complete_teaching_and_practice(lesson: Lesson) -> None:
    catalog = Catalog.load(ROOT)
    assert catalog.get(lesson.id) == lesson
    assert not measure_lesson(catalog, lesson).issues
    assert practice_targets()[lesson.id]["target"] == 6
    for name in (lesson.lesson_path, lesson.guide_path, *lesson.solution_paths):
        path = ROOT / name
        assert count_practice(path, solution="solutions/" in name) == 6
        assert "\u2014" not in path.read_text()


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
def test_new_sql_preserves_runtime_boundary_and_valid_pg_syntax(lesson: Lesson) -> None:
    from pglast.parser import parse_sql_json

    for name in (lesson.lesson_path, *lesson.solution_paths):
        if not name.endswith(".sql"):
            continue
        source = (ROOT / name).read_text()
        parse_sql_json(sql_for_parser(source))
        assert "current_database()" in source and "advanced_sql_training" in source
        assert "server_version_num" in source and "170000" in source
        assert "BEGIN;" in source and source.rstrip().endswith("ROLLBACK;")


def test_depth_audit_rejects_a_retired_route_in_learner_sql(tmp_path: Path) -> None:
    lesson = replace(
        Catalog.load(ROOT).get("sql-start-01"),
        lesson_path="learner.sql",
        guide_path="guide.md",
        solution_paths=("solution.md",),
    )
    (tmp_path / "learner.sql").write_text("-- Use Create/open guided SQL notebook.\nSELECT 1;\n")
    (tmp_path / "guide.md").write_text("# Guide\n")
    (tmp_path / "solution.md").write_text("# Solution\n")
    catalog = Catalog(tmp_path, [lesson])
    assert (
        "learner.sql still prescribes a retired native portal action"
        in measure_lesson(catalog, lesson).issues
    )


@pytest.mark.parametrize(
    ("slug", "expected"),
    [
        ("select_where_orderby", "SELECT, WHERE, ORDER BY and LIMIT"),
        ("aggregates_groupby_having", "Aggregates, GROUP BY and HAVING"),
        ("project1_ecommerce_part1", "Project 1 Ecommerce Part 1"),
    ],
)
def test_sql_display_titles_keep_clause_and_number_spacing(slug: str, expected: str) -> None:
    assert _sql_title(slug) == expected
