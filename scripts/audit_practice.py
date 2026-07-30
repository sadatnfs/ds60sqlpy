#!/usr/bin/env python3
"""Audit the exercise-doubling contract across every cataloged lesson."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "curriculum" / "catalog.json"
BASELINE_PATH = REPO_ROOT / "curriculum" / "practice_baseline.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "practice-coverage.md"

PRACTICE_WORDS = re.compile(
    r"\b(exercises?|practice|challenges?|project\s+tasks?|tasks?|checkpoints?)\b",
    re.IGNORECASE,
)
MARKDOWN_HEADING = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
NUMBERED_MARKDOWN = re.compile(r"^\s{0,3}(?P<number>\d+)[.)]\s+\S")
CHECKBOX_MARKDOWN = re.compile(r"^\s{0,3}[-*]\s+\[[ xX]\]\s+\S")
NUMBERED_SUBHEADING = re.compile(
    r"^#{3,6}\s+(?:(?:exercise|practice|challenge|task)\s+)?(?P<number>\d+)[.):\s-]",
    re.IGNORECASE,
)
SOLUTION_LABEL = re.compile(
    r"^\s*(?:#{1,6}\s+)?(?:exercise|practice|challenge|task)\s+"
    r"(?P<number>\d+)\b",
    re.IGNORECASE,
)
SQL_PRACTICE_HEADING = re.compile(
    r"^\s*--\s*(?:#+\s*)?.*"
    r"\b(exercises?|practice|challenges?|project\s+tasks?|tasks?|checkpoints?)\b",
    re.IGNORECASE,
)
SQL_NUMBERED_PROMPT = re.compile(r"^\s*--\s*(?P<number>\d+)[.)]\s+\S")
PYTHON_NUMBERED_PROMPT = re.compile(
    r"^\s*#\s*(?:(?:exercise|practice|challenge|task)\s+)?"
    r"(?P<number>\d+)[.):\s-]",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ArtifactCounts:
    """Detected practice prompts for one cataloged lesson."""

    lesson_id: str
    baseline: int
    target: int
    learner: int
    guide: int
    solution: int

    @property
    def passes(self) -> bool:
        """Return whether all learner-facing surfaces meet the target."""

        return (
            self.learner >= self.target
            and self.guide >= self.target
            and self.solution >= self.target
        )


def _source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _markdown_practice_count(source: str, *, solution: bool = False) -> int:
    """Count top-level prompts in explicitly labeled Markdown sections."""

    lines = source.splitlines()
    total = 0
    index = 0
    while index < len(lines):
        heading = MARKDOWN_HEADING.match(lines[index])
        if heading is None or len(heading.group("marks")) > 2:
            index += 1
            continue
        level = len(heading.group("marks"))
        title = heading.group("title")
        if not PRACTICE_WORDS.search(title):
            index += 1
            continue

        end = index + 1
        while end < len(lines):
            next_heading = MARKDOWN_HEADING.match(lines[end])
            if next_heading is not None and len(next_heading.group("marks")) <= level:
                break
            end += 1
        section = lines[index + 1 : end]

        prompt_numbers = {
            match.group("number")
            for line in section
            if (match := NUMBERED_SUBHEADING.match(line)) is not None
        }
        prompt_numbers.update(
            match.group("number")
            for line in section
            if (match := NUMBERED_MARKDOWN.match(line)) is not None
        )
        total += len(prompt_numbers)
        total += sum(CHECKBOX_MARKDOWN.match(line) is not None for line in section)
        index = end

    if solution:
        labels = {
            match.group("number")
            for line in lines
            if (match := SOLUTION_LABEL.match(line)) is not None
        }
        total = max(total, len(labels))
    return total


def _notebook_markdown_source(source: str) -> str:
    payload = json.loads(source)
    cells = payload.get("cells", [])
    blocks: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", [])
        blocks.append("".join(source) if isinstance(source, list) else str(source))
    return "\n\n".join(blocks)


def _notebook_markdown(path: Path) -> str:
    return _notebook_markdown_source(_source_text(path))


def _sql_practice_count(source: str) -> int:
    """Count numbered prompts after SQL practice headings."""

    lines = source.splitlines()
    active = False
    numbers: set[str] = set()
    for line in lines:
        if SQL_PRACTICE_HEADING.match(line):
            active = True
            continue
        if not active:
            continue
        prompt = SQL_NUMBERED_PROMPT.match(line)
        if prompt is not None:
            numbers.add(prompt.group("number"))
            continue
        if re.match(r"^\s*(?:ROLLBACK|COMMIT)\s*;", line, re.IGNORECASE):
            active = False
    return len(numbers)


def count_practice_source(
    path: str | Path,
    source: str,
    *,
    solution: bool = False,
) -> int:
    """Count practice prompts from artifact text without touching the filesystem."""

    suffix = Path(path).suffix.lower()
    if suffix == ".ipynb":
        return _markdown_practice_count(
            _notebook_markdown_source(source),
            solution=solution,
        )
    if suffix == ".md":
        return _markdown_practice_count(source, solution=solution)
    if suffix == ".sql":
        return _sql_practice_count(source)
    if suffix == ".py":
        numbers = {
            match.group("number")
            for line in source.splitlines()
            if (match := PYTHON_NUMBERED_PROMPT.match(line)) is not None
        }
        return len(numbers)
    return 0


def count_practice(path: Path, *, solution: bool = False) -> int:
    """Count practice prompts in a supported lesson artifact."""

    return count_practice_source(path, _source_text(path), solution=solution)


def _load_json(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def audit() -> list[ArtifactCounts]:
    """Audit every catalog lesson against its immutable enrichment target."""

    catalog = _load_json(CATALOG_PATH)
    baseline = _load_json(BASELINE_PATH)
    targets = baseline.get("lessons")
    if not isinstance(targets, dict):
        raise ValueError("practice_baseline.json field 'lessons' must be an object")

    rows: list[ArtifactCounts] = []
    catalog_ids: set[str] = set()
    for lesson in catalog.get("lessons", []):
        lesson_id = str(lesson["id"])
        catalog_ids.add(lesson_id)
        raw_target = targets.get(lesson_id)
        if not isinstance(raw_target, dict):
            raise ValueError(f"practice baseline is missing {lesson_id}")
        baseline_count = int(raw_target["baseline"])
        target = int(raw_target["target"])
        expected_target = max(6, baseline_count * 2)
        if target != expected_target:
            raise ValueError(
                f"{lesson_id} target is {target}; expected max(6, 2 × {baseline_count}) "
                f"= {expected_target}"
            )

        learner_path = REPO_ROOT / str(lesson["lesson_path"])
        guide_path = REPO_ROOT / str(lesson["guide_path"])
        solution_paths = [
            REPO_ROOT / str(relative_path)
            for relative_path in lesson.get("solution_paths", [])
            if Path(str(relative_path)).suffix.lower() in {".md", ".ipynb"}
        ]
        if not solution_paths:
            raise ValueError(f"{lesson_id} has no explanatory solution artifact")
        rows.append(
            ArtifactCounts(
                lesson_id=lesson_id,
                baseline=baseline_count,
                target=target,
                learner=count_practice(learner_path),
                guide=count_practice(guide_path),
                # A lesson can expose both Markdown and notebook explanations.
                # The least-complete explanatory artifact is the honest course
                # surface; using the maximum would allow a sparse duplicate to
                # hide behind its richer counterpart.
                solution=min(count_practice(path, solution=True) for path in solution_paths),
            )
        )

    extra_targets = sorted(set(targets) - catalog_ids)
    if extra_targets:
        raise ValueError(f"practice baseline has unknown lesson IDs: {extra_targets}")
    return rows


def render_report(rows: list[ArtifactCounts]) -> str:
    """Render an evidence report suitable for learners and maintainers."""

    passing = sum(row.passes for row in rows)
    baseline_total = sum(row.baseline for row in rows)
    target_total = sum(row.target for row in rows)
    learner_total = sum(row.learner for row in rows)
    guide_total = sum(row.guide for row in rows)
    solution_total = sum(row.solution for row in rows)
    lines = [
        "# Practice coverage report",
        "",
        "This generated report checks the repository-wide exercise-enrichment",
        "contract recorded in `curriculum/practice_baseline.json`. For every",
        "cataloged lesson, the target is `max(6, 2 × audited baseline)` and must",
        "be visible in the learner artifact, companion guide, and every",
        "explanatory solution artifact.",
        "",
        f"- Lessons passing all three surfaces: **{passing}/{len(rows)}**",
        f"- Audited baseline prompts: **{baseline_total}**",
        f"- Required prompts per surface: **{target_total}**",
        f"- Current learner-artifact prompts: **{learner_total}**",
        f"- Current companion-guide prompts: **{guide_total}**",
        f"- Current explanatory-solution prompts: **{solution_total}**",
        "",
        "| Lesson | Baseline | Target | Learner | Guide | Solution minimum | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        status = "PASS" if row.passes else "NEEDS WORK"
        lines.append(
            f"| `{row.lesson_id}` | {row.baseline} | {row.target} | "
            f"{row.learner} | {row.guide} | {row.solution} | {status} |"
        )
    lines.extend(
        [
            "",
            "Regenerate this report from the repository root:",
            "",
            "```text",
            "python scripts/audit_practice.py --write-report",
            "```",
            "",
            "The count is a coverage guard, not a quality substitute. Authoring review",
            "still checks concept progression, answer separation, edge cases, and",
            "explanatory reasoning.",
            "",
        ]
    )
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable rows.")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write docs/practice-coverage.md before returning the audit status.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the practice audit."""

    args = _parser().parse_args(argv)
    try:
        rows = audit()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Practice audit could not run: {exc}", file=sys.stderr)
        return 2

    if args.write_report:
        DEFAULT_REPORT_PATH.write_text(render_report(rows), encoding="utf-8")
        print(f"Wrote {DEFAULT_REPORT_PATH.relative_to(REPO_ROOT)}")

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "lesson_id": row.lesson_id,
                        "baseline": row.baseline,
                        "target": row.target,
                        "learner": row.learner,
                        "guide": row.guide,
                        "solution": row.solution,
                        "passes": row.passes,
                    }
                    for row in rows
                ],
                indent=2,
            )
        )
    else:
        for row in rows:
            if not row.passes:
                print(
                    f"FAIL {row.lesson_id}: target={row.target}; "
                    f"learner={row.learner}, guide={row.guide}, "
                    f"solution={row.solution}"
                )
        passing = sum(row.passes for row in rows)
        print(f"Practice coverage: {passing}/{len(rows)} lessons pass all surfaces")
    return 0 if all(row.passes for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
