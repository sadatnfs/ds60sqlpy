from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.modules import ModuleCatalog
from scripts.build_coverage_matrix import (
    GAP_CODES,
    MATRIX_PATH,
    REPORT_PATH,
    build,
    build_rows,
    coverage_problems,
    module_exercise_count,
    orientation,
    term_count,
)

ROOT = Path(__file__).resolve().parents[1]


@cache
def _built() -> tuple[str, str, tuple[str, ...]]:
    matrix, report, problems = build()
    return matrix, report, tuple(problems)


def test_committed_matrix_and_report_are_current() -> None:
    matrix, report, problems = _built()
    assert not problems
    assert MATRIX_PATH.read_text(encoding="utf-8") == matrix
    assert REPORT_PATH.read_text(encoding="utf-8") == report


def test_every_cataloged_lesson_has_exactly_one_known_row() -> None:
    catalog = Catalog.load(ROOT)
    modules = ModuleCatalog(ROOT)
    rows = json.loads(_built()[0])["lessons"]
    assert len(rows) == len(catalog.lessons()) + len(modules.canonical_ids)
    assert len({row["id"] for row in rows}) == len(rows)
    assert all(set(row["gaps"]) <= set(GAP_CODES) for row in rows)
    assert all(row["execution"] in {"runnable", "reading", "operations"} for row in rows)


def test_coverage_problems_report_missing_and_duplicate_rows() -> None:
    catalog = Catalog.load(ROOT)
    modules = ModuleCatalog(ROOT)
    rows = build_rows(catalog, modules)
    damaged = [rows[0], rows[0], *rows[2:]]
    problems = coverage_problems(damaged, catalog, modules)
    assert f"duplicate row: {rows[0]['id']}" in problems
    assert f"uncovered lesson: {rows[1]['id']}" in problems


def test_practice_gaps_apply_only_to_practice_lessons() -> None:
    rows = json.loads(_built()[0])["lessons"]
    practice_only = {"few-exercises", "missing-solution", "thin-solution"}
    assert all(
        not practice_only & set(row["gaps"]) for row in rows if row["learning_mode"] != "practice"
    )


def test_orientation_reads_headings_and_lead_in_lines() -> None:
    guide = """# Lesson

## Level and prerequisites

Finish the first lesson.

## Learning objectives

- Explain a join.

```markdown
## Vocabulary
```
"""
    assert orientation(guide) == {
        "states_prerequisites": True,
        "states_objectives": True,
        "has_vocabulary": False,
    }
    assert orientation("**Prerequisites:** none.\n")["states_prerequisites"]
    assert not any(orientation("# Lesson\n\nPlain prose.\n").values())


def test_term_count_ignores_instructional_labels() -> None:
    guide = """**Expected:** 3 rows.
**Hint:** start small.
**Primary key:** a column set that identifies a row.

**Causal inference**

## Vocabulary

- grain
| foreign key | references another table |
"""
    assert term_count(guide) == 4


def test_module_exercise_count_uses_the_strongest_signal() -> None:
    labels = "TODO 1 and TODO 2, then Exercise 3."
    headings = "## Practice\n\n### 1. Read\n\n### 2. Write\n"
    assert module_exercise_count([labels]) == 3
    assert module_exercise_count([headings, labels]) == 3
    assert module_exercise_count(["No exercises here."]) == 0
