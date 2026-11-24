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
    outcome_issue,
    prose_paragraphs,
    templated_word_counts,
    term_count,
    track_gap_lines,
)

ROOT = Path(__file__).resolve().parents[1]

# Lesson-foundation gaps may only fall. Lower a ceiling whenever content work
# closes gaps; Phase 3 ends with every ceiling at zero.
FOUNDATION_GAP_CEILING = {"missing-outcome": 0, "weak-outcome": 0, "few-terms": 0}

# Practice-depth gaps may only fall; Phase 4 ends with every ceiling at zero.
PRACTICE_GAP_CEILING = {"thin-guide": 0, "few-examples": 0, "thin-solution": 0}

# Generator boilerplate across all guides and solutions. New prose must be
# specific to its lesson, so this total may not grow; lower it when rewrites
# replace template text.
TEMPLATED_WORDS_CEILING = 835280


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


def test_outcome_issue_requires_an_observable_action() -> None:
    assert outcome_issue("Explain why a left join keeps unmatched rows.") is None
    assert outcome_issue("Jointly fit a mean and a scale parameter.") is None
    assert outcome_issue("") is None
    assert "Understand" in str(outcome_issue("Understand joins and their assumptions."))
    assert "lowercase" in str(outcome_issue("kernel that adds two vectors"))
    assert "'A'" in str(outcome_issue("A domain corpus is a versioned dataset."))
    assert "fewer than" in str(outcome_issue("Plan evidence."))


def test_foundation_gaps_never_grow() -> None:
    rows = json.loads(_built()[0])["lessons"]
    counts = {code: sum(code in row["gaps"] for row in rows) for code in FOUNDATION_GAP_CEILING}
    assert counts == {
        code: min(counts[code], ceiling) for code, ceiling in FOUNDATION_GAP_CEILING.items()
    }


def test_practice_gaps_never_grow() -> None:
    rows = json.loads(_built()[0])["lessons"]
    counts = {code: sum(code in row["gaps"] for row in rows) for code in PRACTICE_GAP_CEILING}
    assert counts == {
        code: min(counts[code], ceiling) for code, ceiling in PRACTICE_GAP_CEILING.items()
    }


def test_templated_prose_never_grows() -> None:
    rows = json.loads(_built()[0])["lessons"]
    assert sum(row["metrics"]["templated_words"] for row in rows) <= TEMPLATED_WORDS_CEILING


def test_prose_paragraphs_skip_code_headings_and_short_text() -> None:
    long = " ".join(f"word{chr(97 + i % 26)}" for i in range(25))
    text = f"# Title\n\n```python\n{long}\n```\n\nToo short.\n\n| {long} |\n\n{long}\n"
    paragraphs = prose_paragraphs(text)
    assert len(paragraphs) == 1
    assert len(paragraphs[0]) == 25


def test_templated_word_counts_need_three_lessons() -> None:
    template = (
        "Restate the expected observation before running anything, then explain"
        " why the check `{name}` decides this case and which input would make it"
        " fail, so the result is a claim you can defend with evidence."
    )
    unique = " ".join(f"topic{index} detail{index}" for index in range(15))
    texts = {
        "a": template.format(name="x") + "\n\n" + unique,
        "b": template.format(name="y"),
        "c": template.format(name="z"),
        "d": template.format(name="w").replace("evidence", "proof"),
    }
    words = len(prose_paragraphs(texts["b"])[0])
    counts = templated_word_counts(texts)
    assert counts["a"] == words
    assert counts["b"] == counts["c"] == words
    assert counts["d"] == len(prose_paragraphs(texts["d"])[0])
    assert templated_word_counts({key: texts[key] for key in ("a", "b")}) == {"a": 0, "b": 0}


def test_track_gap_lines_filter_by_track_and_code() -> None:
    rows = [
        {
            "id": "t-1",
            "track": "t",
            "gaps": ["few-terms", "weak-outcome"],
            "outcome_issue": "starts with 'Understand', not an observable action verb",
            "metrics": {"terms": 1},
            "paths": {"guide": "g.md"},
        },
        {
            "id": "u-1",
            "track": "u",
            "gaps": ["few-terms"],
            "outcome_issue": None,
            "metrics": {"terms": 0},
            "paths": {"guide": "h.md"},
        },
    ]
    assert track_gap_lines(rows, "t", {"few-terms"}) == ["t-1: few-terms; terms=1; guide=g.md"]
    assert "Understand" in track_gap_lines(rows, "t", set())[0]
    assert track_gap_lines(rows, "t", {"thin-guide"}) == []
