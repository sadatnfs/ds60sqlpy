from __future__ import annotations

import re
from pathlib import Path

from ds60sqlpy.catalog import Catalog, Lesson
from scripts.audit_lesson_depth import (
    _heading_section,
    _practice_blocks,
    _python_fence_errors,
    _repeated_check_lines,
    _solution_structure_issues,
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


def test_repeated_check_lines_detect_template_residue() -> None:
    blocks = [
        "Task A.\n**Verify:** inspect the real topic evidence.",
        "Task B.\n**Verify:** inspect the real topic evidence.",
        "Task C.\n**Verify:** inspect the real topic evidence.",
    ]

    assert _repeated_check_lines(blocks) == {"**Verify:** inspect the real topic evidence.": 3}


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

    assert "repeats authoritative exercise labels 1" in _solution_structure_issues(
        Catalog(tmp_path, [lesson]),
        lesson,
    )[0]


def test_every_cataloged_lesson_meets_the_depth_contract() -> None:
    failures = [row for row in audit() if not row.passes]

    assert failures == []


def test_depth_report_names_the_contract_and_status() -> None:
    rows = audit()
    report = render_report(rows)

    assert "# Lesson depth report" in report
    assert f"**{len(rows)}/{len(rows)}**" in report
    assert "| `python-01` |" in report
    assert "| PASS |" in report
