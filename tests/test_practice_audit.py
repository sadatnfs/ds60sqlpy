from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_practice import (
    _markdown_practice_count,
    _sql_practice_count,
    audit,
    count_practice_source,
    practice_targets,
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


@pytest.mark.parametrize("suffix", [".cpp", ".cc", ".cxx", ".hpp", ".scala"])
def test_slash_comment_artifacts_count_distinct_exercise_labels(suffix: str) -> None:
    source = "// Exercise 1: Predict output.\n// Exercise 2: Repair an error.\n"
    source += "// Exercise 2: Repeated label is not a third exercise.\n"
    assert count_practice_source("learner" + suffix, source) == 2
    assert count_practice_source("learner" + suffix, "int count = 3;\n") == 0


@pytest.mark.parametrize("suffix", [".yaml", ".yml"])
def test_yaml_artifacts_count_comment_exercises_not_manifest_values(suffix: str) -> None:
    source = "# Exercise 1: Inspect the replicas.\nreplicas: 3\n"
    source += "# Exercise 2: Explain a failed readiness check.\n"
    assert count_practice_source("learner" + suffix, source) == 2
    assert count_practice_source("learner" + suffix, "replicas: 3\n") == 0


def test_reading_text_accepts_six_markdown_shaped_exercises() -> None:
    source = "## Exercises\n\n" + "\n".join(
        f"{index}. Explain case {index}.\n" for index in range(1, 7)
    )

    assert count_practice_source("learner.txt", source) == 6


def test_reading_text_accepts_distinct_explicit_labels_without_markdown() -> None:
    source = "\n\n".join(f"Exercise {index}: Explain case {index}." for index in range(1, 7))
    source += "\nExercise 6: Repeating a label does not add a seventh task.\n"

    assert count_practice_source("learner.txt", source) == 6
    assert count_practice_source("learner.txt", "1. Introduction step.\n2. Setup step.\n") == 0


def test_practice_baseline_covers_the_catalog() -> None:
    catalog = json.loads((REPO_ROOT / "curriculum" / "catalog.json").read_text(encoding="utf-8"))
    baseline = {"lessons": practice_targets()}

    assert set(baseline["lessons"]) == {lesson["id"] for lesson in catalog["lessons"]}
    assert all(
        value["target"] == max(6, 2 * value["baseline"]) for value in baseline["lessons"].values()
    )


def test_every_lesson_meets_the_practice_doubling_contract() -> None:
    failures = [row for row in audit() if not row.passes]
    assert failures == []
