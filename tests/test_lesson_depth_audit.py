from __future__ import annotations

import re
from pathlib import Path

from ds60sqlpy.catalog import Catalog, Lesson
from scripts.audit_lesson_depth import (
    _guide_issues,
    _heading_section,
    _practice_blocks,
    _python_fence_errors,
    _repeated_check_lines,
    _restated_verify_lines,
    _solution_structure_issues,
    _template_residue,
    _weak_verify_lines,
    audit,
    render_report,
)


def test_practice_blocks_require_an_actual_exercise_heading() -> None:
    source = """\
# Lesson

## Practice assumptions and review method

1. This procedural list is not a learner exercise.

## Exercises

1. Trace the normal case.

   **Expected result:** three values remain.

2. Diagnose the empty case.

   **Verify:** the result is an empty list.

## Self-check

1. This retrieval question belongs to another section.
"""

    blocks = _practice_blocks(source)

    assert len(blocks) == 2
    assert "three values remain" in blocks[0]
    assert "empty list" in blocks[1]


def test_practice_blocks_include_advanced_exercise_heading_variants() -> None:
    source = """\
## Learner exercises and progressive hints

1. Trace the first example.

**Verify:** Assert the output equals 3.

### Progressive hints

1. This numbered hint is not another exercise.

### Additional mastery practice

2. Transfer the idea to a second input.

**Verify:** Assert the output equals 5.

## Self-check
"""

    blocks = _practice_blocks(source)

    assert len(blocks) == 2
    assert "output equals 3" in blocks[0]
    assert "output equals 5" in blocks[1]


def test_repeated_check_lines_detect_template_residue() -> None:
    blocks = [
        "Task A.\n**Verify:** inspect the real topic evidence.",
        "Task B.\n**Verify:** inspect the real topic evidence.",
        "Task C.\n**Verify:** inspect the real topic evidence.",
    ]

    assert _repeated_check_lines(blocks) == {"**Verify:** inspect the real topic evidence.": 3}


def test_verify_contracts_must_name_observable_evidence() -> None:
    blocks = [
        "1. Finalize the training pipeline.\n"
        "**Verify:** Finalize the training and evaluation pipeline.",
        "2. Return normalized values.\n**Verify:** Assert the result equals [0.0, 0.5, 1.0].",
    ]

    assert _weak_verify_lines(blocks) == ("Finalize the training and evaluation pipeline.",)


def test_verify_contracts_cannot_merely_restate_the_exercise() -> None:
    blocks = [
        "Build a report with three metrics and one limitation.\n"
        "**Verify:** Report — build a report with three metrics and one limitation.",
        "Return normalized values without mutating the input.\n"
        "**Verify:** Assert the result equals [0.0, 0.5, 1.0] and the input is unchanged.",
    ]

    assert _restated_verify_lines(blocks) == (
        "Report — build a report with three metrics and one limitation.",
    )


def test_template_residue_rejects_unresolved_authoring_placeholders() -> None:
    source = (
        "Return one result row per key or group explicitly\nnamed in the prompt, "
        "then explain the operation being learned. "
        "Retain concrete output/assertion evidence that it worked. "
        "Preserve observed values or named failures. "
        "Apply this constraint while checking it. "
        "Keep the answer's named identity and the demonstrated identity visible. "
        "Materialize the intended the answer target set with the fields explicitly "
        "named in the answer. Compare each of the derived value entries, require "
        "unique the answer keys, return at most 1 rows, and say the final columns "
        "are `*`. Reuse the exercise's documented row-grain key, the exercise's "
        "stated secondary order, the row-grain key, and the intended the exercise's "
        "target. Refer "
        "to a business sort value, a qualifying group, and values named in the "
        "prompt, then request one labeled matrix/checklist entry for every mechanism "
        "and preserve the stated grain. Build exactly one summary row containing "
        "generic values, run a single-purpose aggregate, compare before and after "
        "each join among generic relations, and claim the requested join grain. "
        "Test one value exactly on each stated time/range boundary, use fewer source "
        "rows than the limit, then more than the limit, and report the documented "
        "grain and requested order. Follow this exercise's stated policy and use an "
        "empty qualifying set, then check a decision matrix against every noun in "
        "the prompt. Test a key with no related rows and one with tied candidate "
        "rows, tied on the leading `ORDER BY` expression, then refer to the `WHERE` "
        "predicate and the outer predicate. Keep a tuple that survives the filter "
        "and report the first group's measure as `result_value`, the complete "
        "projected row, or before/after rows keyed by a placeholder. "
        "**Verify:** For task `Explain the important concep...`, inspect it."
    )

    assert _template_residue(source) == (
        "key or group explicitly named in the prompt",
        "operation being learned",
        "retain concrete output/assertion evidence",
        "preserve observed values or named failures",
        "apply this constraint while checking it",
        "the answer's named identity",
        "the demonstrated identity",
        "intended the answer",
        "the fields explicitly named in the answer",
        "each of the derived value",
        "unique the answer",
        "at most 1 rows",
        "the final columns are `*`",
        "the exercise's documented",
        "the exercise's stated secondary order",
        "the row-grain key",
        "the intended the exercise's",
        "named in the prompt",
        "business sort value",
        "qualifying group",
        "one labeled matrix/checklist entry for every mechanism",
        "preserve the stated grain",
        "build exactly one summary row containing",
        "run a single-purpose aggregate",
        "before and after each join among",
        "requested join grain",
        "test one value exactly on each stated time/range boundary",
        "use fewer source rows than the limit, then more than the limit",
        "documented grain",
        "requested order",
        "this exercise's stated",
        "empty qualifying set",
        "against every noun in the prompt",
        "with no related rows and one with tied candidate rows",
        "leading `order by` expression",
        "the `where` predicate",
        "outer predicate",
        "survives the filter",
        "the first group's measure",
        "result_value",
        "the complete projected row",
        "before/after rows keyed by",
        "truncated `For task ...` label",
    )


def test_sql_guide_rejects_nested_order_by_as_the_outer_result_order() -> None:
    lesson = Lesson(
        id="sql-17",
        track="sql",
        day=17,
        title="Window ranks",
        level="intermediate",
        phase="Test",
        estimated_minutes=10,
        prerequisites=(),
        lesson_path="lesson.sql",
        guide_path="guide.md",
        solution_paths=("solution.md",),
        dependency_group="core",
        network="offline",
    )
    broken_order = "price DESC) AS rank_value FROM products ORDER BY category, rank_value"
    source = f"""\
# Window ranks

## Learning objectives
## How to run
## Vocabulary and mental model
## Worked examples
## Exercises

1. Rank each product.
   **Verify:** Compare each rank with the expected row values.
   **Expected result/shape:** The final order is `{broken_order}`.

## Ask Codex about this lesson

```text
Use guide-ds60sqlpy-learning for sql-17 with guide.md and lesson.sql.
Keep solutions/ closed. Predict, attempt, hint, evidence, and retrieval.
Done when the verification passes.
```
"""

    issues = _guide_issues(
        lesson,
        source,
        solution_words=700,
        solution_code_blocks=1,
    )

    assert any("confuse a nested window/subquery clause" in issue for issue in issues)


def test_heading_section_stops_at_the_next_peer_heading() -> None:
    source = """\
## Ask Codex about this lesson

```text
Use the lesson prompt.
```

## Continue

Not part of the prompt.
"""

    section = _heading_section(source, re.compile(r"ask codex", re.IGNORECASE))

    assert "Use the lesson prompt" in section
    assert "Not part of the prompt" not in section


def test_ask_codex_prompt_names_direct_catalog_prerequisites() -> None:
    lesson = Lesson(
        id="python-02",
        track="python",
        day=2,
        title="Example",
        level="beginner",
        phase="Test",
        estimated_minutes=10,
        prerequisites=("python-01",),
        lesson_path="lesson.ipynb",
        guide_path="guide.md",
        solution_paths=("solutions/example.md",),
        dependency_group="core",
        network="offline",
    )
    source = """\
# Example

## Ask Codex about this lesson

```text
Use guide-ds60sqlpy-learning for python-02 with guide.md and lesson.ipynb.
Keep solutions/ closed. Predict, attempt, hint, evidence, and retrieval.
Done when the verification passes.
```
"""

    assert "Ask Codex prompt does not name catalog prerequisite python-01" in _guide_issues(
        lesson,
        source,
        solution_words=700,
        solution_code_blocks=1,
    )


def test_python_fence_errors_reject_malformed_runnable_examples() -> None:
    source = """\
```python
for value in values:
print(value)
```
"""

    assert "expected an indented block" in _python_fence_errors(source)[0]


def test_solution_structure_rejects_duplicate_authoritative_labels(
    tmp_path: Path,
) -> None:
    path = tmp_path / "solution.md"
    path.write_text(
        "# Solution\n\n## Exercise 1 — first\n\nText.\n\nExercise 1 — second\n",
        encoding="utf-8",
    )
    lesson = Lesson(
        id="python-01",
        track="python",
        day=1,
        title="Example",
        level="beginner",
        phase="Test",
        estimated_minutes=10,
        prerequisites=(),
        lesson_path="lesson.ipynb",
        guide_path="guide.md",
        solution_paths=("solution.md",),
        dependency_group="core",
        network="offline",
    )

    assert (
        "repeats authoritative exercise labels 1"
        in _solution_structure_issues(
            Catalog(tmp_path, [lesson]),
            lesson,
        )[0]
    )


def test_solution_structure_checks_non_markdown_solution_residue(
    tmp_path: Path,
) -> None:
    path = tmp_path / "solution.sql"
    path.write_text(
        "-- Verify the answer's named identity.\n"
        "-- The final order is `score DESC) AS rank_value FROM rows`.\n"
        "SELECT 1;\n",
        encoding="utf-8",
    )
    lesson = Lesson(
        id="sql-01",
        track="sql",
        day=1,
        title="Example",
        level="beginner",
        phase="Test",
        estimated_minutes=10,
        prerequisites=(),
        lesson_path="lesson.sql",
        guide_path="guide.md",
        solution_paths=("solution.sql",),
        dependency_group="core",
        network="offline",
    )

    issues = _solution_structure_issues(Catalog(tmp_path, [lesson]), lesson)

    assert any("solution.sql contains generic authoring residue" in issue for issue in issues)
    assert any("solution.sql contains 1 SQL exercise contracts" in issue for issue in issues)


def test_every_cataloged_lesson_meets_the_depth_contract() -> None:
    failures = [row for row in audit() if not row.passes]

    assert failures == []


def test_depth_report_names_the_contract_and_status() -> None:
    rows = audit()
    report = render_report(rows)

    assert "# Lesson depth report" in report
    assert f"**{len(rows)}/{len(rows)}**" in report
    assert "Verify contracts without observable, topic-specific evidence" in report
    assert "SQL wildcard result columns or nested-query text" in report
    assert "| `python-01` |" in report
    assert "| PASS |" in report
