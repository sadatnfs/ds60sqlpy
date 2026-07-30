from __future__ import annotations

import json
from pathlib import Path

from scripts.audit_practice import (
    _markdown_practice_count,
    _sql_practice_count,
    audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_markdown_counter_uses_explicit_practice_sections() -> None:
    source = """\
# Lesson

1. This numbered introduction is not practice.

## Exercises

1. Predict the result.
2. Implement the change.

### 3. Debug the edge case

## Self-check

1. This belongs to a different section.
"""

    assert _markdown_practice_count(source) == 3


def test_solution_counter_accepts_labeled_exercises() -> None:
    source = """\
# Solutions

## Exercise 1 — Prediction

Reasoning.

Exercise 2: Implementation

Reasoning.
"""

    assert _markdown_practice_count(source, solution=True) == 2


def test_sql_counter_stops_at_transaction_end() -> None:
    source = """\
-- Exercises
-- 1. Predict NULL behavior.
-- 2. Write the query.
ROLLBACK;
-- 3. This is outside the practice transaction.
"""

    assert _sql_practice_count(source) == 2


def test_practice_baseline_covers_the_catalog() -> None:
    catalog = json.loads(
        (REPO_ROOT / "curriculum" / "catalog.json").read_text(encoding="utf-8")
    )
    baseline = json.loads(
        (REPO_ROOT / "curriculum" / "practice_baseline.json").read_text(
            encoding="utf-8"
        )
    )

    assert set(baseline["lessons"]) == {lesson["id"] for lesson in catalog["lessons"]}
    assert all(
        value["target"] == max(6, 2 * value["baseline"])
        for value in baseline["lessons"].values()
    )


def test_every_lesson_meets_the_practice_doubling_contract() -> None:
    failures = [row for row in audit() if not row.passes]
    assert failures == []
