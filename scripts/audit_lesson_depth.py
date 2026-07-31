#!/usr/bin/env python3
"""Audit beginner-facing teaching depth across Python and SQL lessons."""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.catalog import Catalog, Lesson  # noqa: E402

DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "lesson-depth-report.md"

MIN_GUIDE_WORDS = 1_050
MIN_GUIDE_CODE_BLOCKS = 2
MIN_DEFINITIONS = 3
MIN_SOLUTION_WORDS = 700
MIN_NOTEBOOK_CELLS = 8
MIN_NOTEBOOK_CODE_CELLS = 3
MIN_NOTEBOOK_MARKDOWN_WORDS = 550

WORD = re.compile(r"\b[\w'-]+\b")
HEADING = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*$", re.MULTILINE)
DEFINITION = re.compile(
    r"^\s*(?:[-*]\s+)?\*\*(?P<term>[^*\n:]{1,80})(?::\*\*|\*\*:)",
    re.MULTILINE,
)
NUMBERED_ITEM = re.compile(r"^\s{0,3}(?P<number>\d+)[.)]\s+(?P<body>.+)$")
SOLUTION_LABEL = re.compile(
    r"^\s*(?:#{1,6}\s+)?(?:exercise|practice|challenge|task)\s+"
    r"(?P<number>\d+)\b",
    re.IGNORECASE | re.MULTILINE,
)
EXPLICIT_CHECK = re.compile(
    r"\*\*(?:expected(?:\s+(?:result|behavior|shape|output))?|verify|verification|"
    r"success(?:\s+check)?|check)\s*:\*\*",
    re.IGNORECASE,
)
VERIFY_LINE = re.compile(
    r"^\s*\*\*Verify:\*\*\s*(?P<body>.+)$",
    re.IGNORECASE | re.MULTILINE,
)
FINAL_ORDER = re.compile(
    r"\bthe\s+final\s+order\s+is\s+`(?P<order>[^`\n]+)`",
    re.IGNORECASE,
)
NESTED_SQL_IN_FINAL_ORDER = re.compile(
    r"\b(?:select|from|where|group\s+by|having|over|rows\s+between|"
    r"range\s+between)\b|(?:\)\s+as\b)",
    re.IGNORECASE,
)
OBSERVABLE_EVIDENCE = re.compile(
    r"\b(?:assert(?:ion|ions)?|expected|equals?|matches?|contains?|returns?|"
    r"prints?|reports?|records?|shows?|proves?|inspects?|compares?|counts?|"
    r"rows?|columns?|shapes?|types?|values?|outputs?|results?|evidence|artifacts?|"
    r"exceptions?|exit|status|files?|paths?|hash(?:es)?|metrics?|scores?|"
    r"thresholds?|seeds?|repeats?|overlap|ranks?|tests?|checks?|logs?|"
    r"checklists?|owners?|transcripts?|plots?|figures?|tables?|matri(?:x|ces)|"
    r"notebooks?|readme|"
    r"seconds?|bytes?|percent|warnings?|messages?)\b",
    re.IGNORECASE,
)
GENERIC_AUTHORING_RESIDUE = (
    "key or group explicitly named in the prompt",
    "grouping key explicitly named in the prompt",
    "requested calendar/cohort bucket and grouping key",
    "the statement's declared columns/object",
    "operation being learned",
    "demonstrate the concrete requirement",
    "use identical data, split, metric, and budget for both sides",
    "assert the return type/shape/value for the stated valid input",
    "produce the requested artifact with every named field/control",
    "record the seed, resampling unit, run count, estimate",
    "state one precise claim, the evidence supporting it",
    "record the exact command/input, terminal result or returned value",
    "reproduce the failure first, capture its smallest observable symptom",
    "report row/feature shapes, seed/splitter",
    "retain concrete output/assertion evidence",
    "preserve observed values or named failures",
    "is complete when a deterministic return value, exception, recorded call "
    "sequence, or inspected query demonstrates",
    "apply this constraint while checking it",
    "is complete when sentinel input and captured output/call history prove the security boundary",
    "is complete offline with fake-backed evidence",
    "is complete when deterministic normal, edge, and failure checks demonstrate",
    "is complete when the prediction is written before execution and the observed "
    "result is compared with this contract",
    "is complete when the failure is reproduced first, the repair is applied, and "
    "before/after evidence demonstrates",
    "is complete when a short written artifact addresses every named decision",
    "with the prompt's exact filter, time window, and transaction boundary",
    "distinguish `null`, zero, and no row, and make ranked/limited output "
    "deterministic with a unique tie-breaker",
    "compare key set, totals, `null` placement, and final order",
    "explain `from`/`join` and `on`, `where`, grouping/aggregate, window, "
    "projection, and final ordering in logical order",
    "joins, subqueries, ctes, conditional aggregates, or windows are "
    "interchangeable only when they preserve",
    "inspect each join/cte stage over",
    "versus numeric zero and an absent row",
    "the expected contract is that the result must preserve the row grain "
    "described in the walkthrough and expose every named key or measure",
    "the answer's named identity",
    "the demonstrated identity",
    "intended the answer",
    "the fields explicitly named in the answer",
    "each of the derived value",
    "one row per the answer",
    "unique the answer",
    "the intended accepted, ignored, updated, or rejected outcome",
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
)
TRUNCATED_TASK_LABEL = re.compile(r"for\s+task\s+`[^`\n]*\.\.\.`", re.IGNORECASE)
PRACTICE_HEADING = re.compile(
    r"^(?:(?:additional|extended|guided|independent|learner|mastery|professional)\s+)*"
    r"(?:exercises?|practice(?:\s+(?:set|problems?|tasks?|lab))?|"
    r"challenges?|project\s+tasks?|checkpoints?)"
    r"(?:\s+(?:and|with)\s+(?:progressive\s+)?hints?)?"
    r"(?:\s*[:—-].*)?$",
    re.IGNORECASE,
)

REQUIRED_GUIDE_SECTIONS: dict[str, re.Pattern[str]] = {
    "learning objectives": re.compile(r"\b(?:learning\s+)?objectives?\b", re.IGNORECASE),
    "how to run": re.compile(
        r"\b(?:how\s+to\s+run|run\s+this\s+lesson|start\s+and\s+run)\b",
        re.IGNORECASE,
    ),
    "vocabulary or mental model": re.compile(
        r"\b(?:vocabulary|mental\s+model|core\s+concepts?|conceptual\s+model)\b",
        re.IGNORECASE,
    ),
    "worked examples": re.compile(
        r"\b(?:worked\s+examples?|examples?\s+and\s+walkthrough|"
        r"walkthrough|syntax\s+anatomy)\b",
        re.IGNORECASE,
    ),
    "exercises": re.compile(
        r"\b(?:exercises?|practice|challenges?|project\s+tasks?|checkpoints?)\b",
        re.IGNORECASE,
    ),
    "self-check": re.compile(
        r"\b(?:self[- ]check|check\s+your\s+understanding|retrieval\s+practice)\b",
        re.IGNORECASE,
    ),
    "common mistakes": re.compile(
        r"\b(?:common\s+(?:mistakes|pitfalls|errors)|pitfalls|anti-patterns|"
        r"diagnos(?:is|ing)|troubleshooting)\b",
        re.IGNORECASE,
    ),
    "Ask Codex": re.compile(r"\bask\s+codex\b", re.IGNORECASE),
}


@dataclass(frozen=True, slots=True)
class NotebookDepth:
    """Teaching-density measurements for one notebook."""

    cells: int
    code_cells: int
    markdown_words: int


@dataclass(frozen=True, slots=True)
class LessonDepth:
    """Teaching-depth measurements and failures for one cataloged lesson."""

    lesson_id: str
    track: str
    level: str
    guide_words: int
    guide_code_blocks: int
    definitions: int
    practice_prompts: int
    explicit_checks: int
    solution_words: int
    notebook: NotebookDepth | None
    issues: tuple[str, ...]

    @property
    def passes(self) -> bool:
        """Return whether the lesson meets the complete-amateur depth gate."""

        return not self.issues


def _word_count(source: str) -> int:
    return len(WORD.findall(source))


def _code_block_count(source: str) -> int:
    return sum(line.lstrip().startswith("```") for line in source.splitlines()) // 2


def _python_fence_errors(source: str) -> list[str]:
    """Return syntax errors from blocks labeled as runnable Python."""

    errors: list[str] = []
    pattern = re.compile(
        r"^```python[^\n]*\n(?P<body>.*?)^```\s*$",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    for index, match in enumerate(pattern.finditer(source), start=1):
        try:
            ast.parse(match.group("body"), filename=f"python-fence-{index}")
        except SyntaxError as exc:
            errors.append(f"Python fence {index}, line {exc.lineno}: {exc.msg}")
    return errors


def _heading_titles(source: str) -> list[str]:
    return [match.group("title").strip() for match in HEADING.finditer(source)]


def _heading_section(source: str, title_pattern: re.Pattern[str]) -> str:
    """Return the body of the first Markdown section whose heading matches."""

    lines = source.splitlines()
    active = False
    section_level = 0
    body: list[str] = []
    for line in lines:
        heading = re.match(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", line)
        if heading is not None:
            level = len(heading.group("marks"))
            if active and level <= section_level:
                break
            if not active and title_pattern.search(heading.group("title")):
                active = True
                section_level = level
                continue
        if active:
            body.append(line)
    return "\n".join(body)


def _practice_blocks(source: str) -> list[str]:
    """Return complete numbered items from practice-like Markdown sections."""

    lines = source.splitlines()
    blocks: list[str] = []
    in_practice = False
    practice_level = 0
    current: list[str] = []

    for line in lines:
        heading = re.match(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", line)
        if heading is not None:
            level = len(heading.group("marks"))
            title = heading.group("title")
            practice_heading = PRACTICE_HEADING.fullmatch(title.strip())
            if practice_heading:
                if current:
                    blocks.append("\n".join(current))
                    current = []
                in_practice = True
                practice_level = level
                continue
            if in_practice and re.fullmatch(
                r"(?:progressive\s+)?hints?",
                title.strip(),
                re.IGNORECASE,
            ):
                if current:
                    blocks.append("\n".join(current))
                    current = []
                in_practice = False
                continue
            if in_practice and level <= practice_level:
                if current:
                    blocks.append("\n".join(current))
                    current = []
                in_practice = False

        if not in_practice:
            continue
        item = NUMBERED_ITEM.match(line)
        if item is not None:
            if current:
                blocks.append("\n".join(current))
            current = [item.group("body")]
        elif current:
            current.append(line)

    if current:
        blocks.append("\n".join(current))
    return blocks


def _repeated_check_lines(blocks: list[str]) -> dict[str, int]:
    """Return repeated Expected/Verify lines that indicate template residue."""

    counts: dict[str, int] = {}
    display: dict[str, str] = {}
    for block in blocks:
        for line in block.splitlines():
            if EXPLICIT_CHECK.search(line) is None:
                continue
            compact = " ".join(line.split())
            normalized = compact.casefold()
            counts[normalized] = counts.get(normalized, 0) + 1
            display.setdefault(normalized, compact)
    return {display[normalized]: count for normalized, count in counts.items() if count >= 3}


def _weak_verify_lines(blocks: list[str]) -> tuple[str, ...]:
    """Return Verify contracts that do not name observable completion evidence."""

    weak: list[str] = []
    for block in blocks:
        for match in VERIFY_LINE.finditer(block):
            body = match.group("body").strip()
            if OBSERVABLE_EVIDENCE.search(body) is None:
                weak.append(body)
    return tuple(weak)


def _contract_text(source: str) -> str:
    """Normalize Markdown contract prose for near-duplicate comparisons."""

    source = re.sub(r"^\s*\*\*[^*\n]{1,80}:\*\*\s*", "", source.strip())
    return " ".join(re.findall(r"[a-z0-9]+", source.casefold()))


def _restated_verify_lines(blocks: list[str]) -> tuple[str, ...]:
    """Return Verify lines that mostly repeat the exercise instead of testing it."""

    restated: list[str] = []
    for block in blocks:
        verify = VERIFY_LINE.search(block)
        if verify is None:
            continue
        prompt = block[: verify.start()]
        hint = re.search(
            r"(?im)^\s*\*\*(?:progressive\s+)?hint:\*\*",
            prompt,
        )
        if hint:
            prompt = prompt[: hint.start()]
        prompt_text = _contract_text(prompt)
        verify_text = _contract_text(verify.group("body"))
        if len(prompt_text.split()) < 6 or not verify_text:
            continue
        length_ratio = len(prompt_text.split()) / len(verify_text.split())
        similarity = difflib.SequenceMatcher(None, prompt_text, verify_text).ratio()
        prompt_is_most_of_verify = prompt_text in verify_text and length_ratio >= 0.65
        if prompt_is_most_of_verify or similarity >= 0.84:
            restated.append(verify.group("body").strip())
    return tuple(restated)


def _template_residue(source: str) -> tuple[str, ...]:
    """Return generic authoring phrases that must be replaced with lesson facts."""

    folded = " ".join(source.casefold().split())
    residue = [
        phrase
        for phrase in GENERIC_AUTHORING_RESIDUE
        if " ".join(phrase.casefold().split()) in folded
    ]
    if TRUNCATED_TASK_LABEL.search(source):
        residue.append("truncated `For task ...` label")
    return tuple(residue)


def _malformed_final_orders(source: str) -> tuple[str, ...]:
    """Return SQL contracts that confuse nested clauses with outer result order."""

    return tuple(
        match.group("order")
        for match in FINAL_ORDER.finditer(source)
        if len(match.group("order")) > 160
        or NESTED_SQL_IN_FINAL_ORDER.search(match.group("order")) is not None
    )


def _notebook_depth(path: Path) -> NotebookDepth:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} notebook root must be an object")
    raw_cells = payload.get("cells")
    if not isinstance(raw_cells, list):
        raise ValueError(f"{path} notebook cells must be an array")

    code_cells = 0
    markdown: list[str] = []
    for raw_cell in raw_cells:
        if not isinstance(raw_cell, dict):
            continue
        cell_type = raw_cell.get("cell_type")
        raw_source = raw_cell.get("source", [])
        if isinstance(raw_source, list):
            source = "".join(str(part) for part in raw_source)
        else:
            source = str(raw_source)
        if cell_type == "code":
            code_cells += 1
        elif cell_type == "markdown":
            markdown.append(source)
    return NotebookDepth(
        cells=len(raw_cells),
        code_cells=code_cells,
        markdown_words=_word_count("\n\n".join(markdown)),
    )


def _notebook_markdown(path: Path) -> str:
    """Return all Markdown teaching text from a notebook."""

    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    raw_cells = payload.get("cells", []) if isinstance(payload, dict) else []
    blocks: list[str] = []
    for raw_cell in raw_cells:
        if not isinstance(raw_cell, dict) or raw_cell.get("cell_type") != "markdown":
            continue
        raw_source = raw_cell.get("source", [])
        blocks.append(
            "".join(str(part) for part in raw_source)
            if isinstance(raw_source, list)
            else str(raw_source)
        )
    return "\n\n".join(blocks)


def _artifact_text(path: Path) -> str:
    """Return searchable teaching text from a notebook or plain-text artifact."""

    if path.suffix.lower() != ".ipynb":
        return path.read_text(encoding="utf-8")
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    raw_cells = payload.get("cells", []) if isinstance(payload, dict) else []
    blocks: list[str] = []
    for raw_cell in raw_cells:
        if not isinstance(raw_cell, dict):
            continue
        raw_source = raw_cell.get("source", [])
        blocks.append(
            "".join(str(part) for part in raw_source)
            if isinstance(raw_source, list)
            else str(raw_source)
        )
    return "\n\n".join(blocks)


def _solution_markdown(catalog: Catalog, lesson: Lesson) -> tuple[int, int]:
    """Return the least-complete explanatory solution's words and code blocks."""

    measurements: list[tuple[int, int]] = []
    for relative_path in lesson.solution_paths:
        if Path(relative_path).suffix.lower() != ".md":
            continue
        source = catalog.resolve(relative_path).read_text(encoding="utf-8")
        measurements.append((_word_count(source), _code_block_count(source)))
    if not measurements:
        return 0, 0
    return min(measurements)


def _solution_structure_issues(catalog: Catalog, lesson: Lesson) -> list[str]:
    """Catch ambiguous duplicate answers and malformed runnable examples."""

    issues: list[str] = []
    for relative_path in lesson.solution_paths:
        source = catalog.resolve(relative_path).read_text(encoding="utf-8")
        residue = _template_residue(source)
        if residue:
            issues.append(
                f"{relative_path} contains generic authoring residue "
                f"{', '.join(repr(phrase) for phrase in residue)}; replace it with "
                "the exercise's actual concept, grain, objects, and evidence"
            )
        if lesson.track == "sql":
            malformed_orders = _malformed_final_orders(source)
            if malformed_orders:
                issues.append(
                    f"{relative_path} contains {len(malformed_orders)} SQL exercise "
                    "contracts that confuse a nested window/subquery clause with "
                    "the final ORDER BY"
                )
        if Path(relative_path).suffix.lower() != ".md":
            continue
        counts = Counter(match.group("number") for match in SOLUTION_LABEL.finditer(source))
        duplicates = sorted(number for number, count in counts.items() if count > 1)
        if duplicates:
            issues.append(
                f"{relative_path} repeats authoritative exercise labels "
                f"{', '.join(duplicates)}; consolidate each answer under one numbered section"
            )
        if lesson.track in {"python", "bridge"}:
            python_errors = _python_fence_errors(source)
            if python_errors:
                issues.append(
                    f"{relative_path} contains invalid runnable Python: {python_errors[0]}"
                )
    return issues


def _guide_issues(
    lesson: Lesson,
    source: str,
    *,
    solution_words: int,
    solution_code_blocks: int,
) -> list[str]:
    issues: list[str] = []
    guide_words = _word_count(source)
    code_blocks = _code_block_count(source)
    definitions = len({match.group("term").casefold() for match in DEFINITION.finditer(source)})
    headings = _heading_titles(source)
    practice_blocks = _practice_blocks(source)
    explicit_checks = sum(EXPLICIT_CHECK.search(block) is not None for block in practice_blocks)

    if guide_words < MIN_GUIDE_WORDS:
        issues.append(f"guide has {guide_words} words; needs at least {MIN_GUIDE_WORDS}")
    if code_blocks < MIN_GUIDE_CODE_BLOCKS:
        issues.append(
            f"guide has {code_blocks} fenced examples; needs at least {MIN_GUIDE_CODE_BLOCKS}"
        )
    if definitions < MIN_DEFINITIONS:
        issues.append(f"guide defines {definitions} terms; needs at least {MIN_DEFINITIONS}")
    if lesson.track in {"python", "bridge"}:
        python_errors = _python_fence_errors(source)
        if python_errors:
            issues.append(f"guide contains invalid runnable Python: {python_errors[0]}")

    for label, pattern in REQUIRED_GUIDE_SECTIONS.items():
        if not any(pattern.search(title) for title in headings):
            issues.append(f"guide is missing a {label} section")

    ask_codex = _heading_section(source, REQUIRED_GUIDE_SECTIONS["Ask Codex"])
    codex_markers = {
        lesson.id: "the stable lesson ID",
        lesson.guide_path: "the exact companion-guide path",
        lesson.lesson_path: "the exact learner-artifact path",
        "guide-ds60sqlpy-learning": "the repository tutoring skill",
        "solutions/": "the no-solution boundary",
    }
    for marker, label in codex_markers.items():
        if marker.casefold() not in ask_codex.casefold():
            issues.append(f"Ask Codex prompt does not name {label}")
    for prerequisite in lesson.prerequisites:
        if prerequisite.casefold() not in ask_codex.casefold():
            issues.append(f"Ask Codex prompt does not name catalog prerequisite {prerequisite}")
    if "```text" not in ask_codex.casefold():
        issues.append("Ask Codex section does not contain a fenced text prompt")
    for marker in ("predict", "attempt", "hint", "evidence", "retrieval"):
        if marker not in ask_codex.casefold():
            issues.append(f"Ask Codex prompt does not include the {marker} coaching phase")
    if (
        re.search(
            r"\b(?:done\s+when|finish\s+only\s+when|"
            r"consider\s+the\s+lesson\s+complete\s+when)\b",
            ask_codex,
            re.IGNORECASE,
        )
        is None
    ):
        issues.append("Ask Codex prompt does not define an evidence-based done condition")

    if practice_blocks and explicit_checks != len(practice_blocks):
        issues.append(
            f"{len(practice_blocks) - explicit_checks}/{len(practice_blocks)} "
            "guide exercises lack an explicit Expected or Verify line"
        )
    weak_verify_lines = _weak_verify_lines(practice_blocks)
    if weak_verify_lines:
        issues.append(
            f"{len(weak_verify_lines)} guide Verify lines do not name observable "
            "evidence such as an assertion, expected value, output, row/shape, "
            "file/hash, metric, transcript, or test result"
        )
    restated_verify_lines = _restated_verify_lines(practice_blocks)
    if restated_verify_lines:
        issues.append(
            f"{len(restated_verify_lines)} guide Verify lines merely restate the "
            "exercise; add an independent, topic-specific acceptance check"
        )
    repeated_checks = _repeated_check_lines(practice_blocks)
    if repeated_checks:
        worst_line, worst_count = max(repeated_checks.items(), key=lambda item: item[1])
        issues.append(
            f"guide repeats one Expected/Verify contract {worst_count} times; "
            f"make each exercise's evidence topic-specific: {worst_line}"
        )
    residue = _template_residue(source)
    if residue:
        issues.append(
            "guide contains generic authoring residue "
            f"{', '.join(repr(phrase) for phrase in residue)}; replace it with the "
            "lesson's actual concept, grain, objects, and evidence"
        )

    if lesson.track == "sql":
        malformed_orders = _malformed_final_orders(source)
        if malformed_orders:
            issues.append(
                f"{len(malformed_orders)} SQL exercise contracts confuse a nested "
                "window/subquery clause with the final ORDER BY; state only the "
                "outer result order"
            )
        workspace_path = f".learning/sql/{lesson.id}/lesson/workspace/{lesson.lesson_path}"
        required_sql_text = {
            "advanced_sql_training": "the disposable course database",
            "Create/open guided SQL notebook": "the guided SQL notebook action",
            "psql": "a manual psql fallback",
            workspace_path: "the exact ignored learner SQL working copy",
        }
        for marker, label in required_sql_text.items():
            if marker.casefold() not in source.casefold():
                issues.append(f"SQL guide does not name {label}")

    if solution_words < MIN_SOLUTION_WORDS:
        issues.append(
            f"solution explanation has {solution_words} words; needs at least {MIN_SOLUTION_WORDS}"
        )
    if solution_code_blocks < 1:
        issues.append("solution explanation has no fenced code or query example")
    return issues


def measure_lesson(catalog: Catalog, lesson: Lesson) -> LessonDepth:
    """Measure one Python or SQL lesson against the depth standard."""

    guide_source = catalog.resolve(lesson.guide_path).read_text(encoding="utf-8")
    solution_words, solution_code_blocks = _solution_markdown(catalog, lesson)
    practice_blocks = _practice_blocks(guide_source)
    notebook: NotebookDepth | None = None
    issues = _guide_issues(
        lesson,
        guide_source,
        solution_words=solution_words,
        solution_code_blocks=solution_code_blocks,
    )
    issues.extend(_solution_structure_issues(catalog, lesson))

    lesson_path = catalog.resolve(lesson.lesson_path)
    learner_residue = _template_residue(_artifact_text(lesson_path))
    if learner_residue:
        issues.append(
            f"{lesson.lesson_path} contains generic authoring residue "
            f"{', '.join(repr(phrase) for phrase in learner_residue)}; replace it "
            "with the exercise's actual concept, grain, objects, and evidence"
        )
    if lesson.track == "sql":
        malformed_orders = _malformed_final_orders(_artifact_text(lesson_path))
        if malformed_orders:
            issues.append(
                f"{lesson.lesson_path} contains {len(malformed_orders)} SQL exercise "
                "contracts that confuse a nested window/subquery clause with the "
                "final ORDER BY"
            )
    if (
        lesson.track == "python"
        and 1 <= lesson.day <= 60
        and lesson_path.suffix.lower() == ".ipynb"
    ):
        notebook = _notebook_depth(lesson_path)
        repeated_notebook_checks = _repeated_check_lines([_notebook_markdown(lesson_path)])
        if repeated_notebook_checks:
            repeated_line, repeated_count = max(
                repeated_notebook_checks.items(),
                key=lambda item: item[1],
            )
            issues.append(
                f"learner notebook repeats one Expected/Verify contract "
                f"{repeated_count} times; make exercise evidence topic-specific: "
                f"{repeated_line}"
            )
        if notebook.cells < MIN_NOTEBOOK_CELLS:
            issues.append(
                f"learner notebook has {notebook.cells} cells; needs at least {MIN_NOTEBOOK_CELLS}"
            )
        if notebook.code_cells < MIN_NOTEBOOK_CODE_CELLS:
            issues.append(
                f"learner notebook has {notebook.code_cells} code cells; "
                f"needs at least {MIN_NOTEBOOK_CODE_CELLS}"
            )
        if notebook.markdown_words < MIN_NOTEBOOK_MARKDOWN_WORDS:
            issues.append(
                f"learner notebook has {notebook.markdown_words} Markdown words; "
                f"needs at least {MIN_NOTEBOOK_MARKDOWN_WORDS}"
            )

    return LessonDepth(
        lesson_id=lesson.id,
        track=lesson.track,
        level=lesson.level,
        guide_words=_word_count(guide_source),
        guide_code_blocks=_code_block_count(guide_source),
        definitions=len(
            {match.group("term").casefold() for match in DEFINITION.finditer(guide_source)}
        ),
        practice_prompts=len(practice_blocks),
        explicit_checks=sum(EXPLICIT_CHECK.search(block) is not None for block in practice_blocks),
        solution_words=solution_words,
        notebook=notebook,
        issues=tuple(issues),
    )


def audit(catalog: Catalog | None = None) -> list[LessonDepth]:
    """Measure every cataloged lesson in catalog order."""

    active_catalog = catalog or Catalog.load(REPO_ROOT)
    return [measure_lesson(active_catalog, lesson) for lesson in active_catalog]


def render_report(rows: list[LessonDepth]) -> str:
    """Render a checked-in review report."""

    passing = sum(row.passes for row in rows)
    lines = [
        "# Lesson depth report",
        "",
        "This generated report enforces the complete-amateur teaching standard in",
        "`docs/content-authoring.md`. It checks structure and minimum depth; human",
        "review must still judge technical accuracy, progression, and whether the",
        "examples actually teach the named topic.",
        "",
        f"- Cataloged lessons passing: **{passing}/{len(rows)}**",
        f"- Minimum guide words: **{MIN_GUIDE_WORDS}**",
        f"- Minimum worked-example fences: **{MIN_GUIDE_CODE_BLOCKS}**",
        f"- Minimum explicitly defined terms: **{MIN_DEFINITIONS}**",
        f"- Minimum explanatory-solution words: **{MIN_SOLUTION_WORDS}**",
        "- Generic or truncated authoring placeholders: **not allowed**",
        "- Verify contracts without observable, topic-specific evidence: **not allowed**",
        "- Duplicate authoritative numbered solution sections: **not allowed**",
        "- SQL wildcard result columns or nested-query text presented as final order: "
        "**not allowed**",
        (
            "- Historical Python notebook minimum: "
            f"**{MIN_NOTEBOOK_CELLS} cells**, **{MIN_NOTEBOOK_CODE_CELLS} code cells**, "
            f"and **{MIN_NOTEBOOK_MARKDOWN_WORDS} Markdown words**"
        ),
        "",
        "| Lesson | Guide words | Examples | Terms | Exercises checked | "
        "Solution words | Notebook | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        notebook = (
            f"{row.notebook.cells} cells / {row.notebook.code_cells} code / "
            f"{row.notebook.markdown_words} words"
            if row.notebook is not None
            else "notebook gate n/a"
        )
        status = "PASS" if row.passes else "NEEDS WORK"
        lines.append(
            f"| `{row.lesson_id}` | {row.guide_words} | {row.guide_code_blocks} | "
            f"{row.definitions} | {row.explicit_checks}/{row.practice_prompts} | "
            f"{row.solution_words} | {notebook} | {status} |"
        )

    failures = [row for row in rows if not row.passes]
    if failures:
        lines.extend(["", "## Remaining issues", ""])
        for row in failures:
            lines.append(f"### `{row.lesson_id}`")
            lines.extend(f"- {issue}" for issue in row.issues)
            lines.append("")

    lines.extend(
        [
            "",
            "Regenerate from the repository root:",
            "",
            "```text",
            "python scripts/audit_lesson_depth.py --write-report",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _json_rows(rows: list[LessonDepth]) -> list[dict[str, Any]]:
    return [
        {
            "lesson_id": row.lesson_id,
            "track": row.track,
            "level": row.level,
            "guide_words": row.guide_words,
            "guide_code_blocks": row.guide_code_blocks,
            "definitions": row.definitions,
            "practice_prompts": row.practice_prompts,
            "explicit_checks": row.explicit_checks,
            "solution_words": row.solution_words,
            "notebook": (
                {
                    "cells": row.notebook.cells,
                    "code_cells": row.notebook.code_cells,
                    "markdown_words": row.notebook.markdown_words,
                }
                if row.notebook is not None
                else None
            ),
            "issues": list(row.issues),
            "passes": row.passes,
        }
        for row in rows
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable results.")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write docs/lesson-depth-report.md before returning the audit status.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the lesson-depth audit."""

    args = _parser().parse_args(argv)
    try:
        rows = audit()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Lesson-depth audit could not run: {exc}", file=sys.stderr)
        return 2

    if args.write_report:
        DEFAULT_REPORT_PATH.write_text(render_report(rows), encoding="utf-8")
        print(f"Wrote {DEFAULT_REPORT_PATH.relative_to(REPO_ROOT)}")
    if args.json:
        print(json.dumps(_json_rows(rows), indent=2))
    else:
        for row in rows:
            if not row.passes:
                print(f"FAIL {row.lesson_id}: {'; '.join(row.issues)}")
        print(f"Lesson depth: {sum(row.passes for row in rows)}/{len(rows)} lessons pass")
    return 0 if all(row.passes for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
