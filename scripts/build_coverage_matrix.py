#!/usr/bin/env python3
"""Build the catalog-wide lesson coverage matrix.

The matrix is an honest inventory of every core and module lesson: its source,
mode, execution kind, runtime, dependencies, verification and the teaching
signals a reviewer needs before changing content. Gaps are recorded, never
hidden; ``--check`` fails only when the committed outputs drift from the
catalogs or when a cataloged lesson is missing from the matrix.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
for _path in (SRC, REPO_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ds60sqlpy.catalog import Catalog, Lesson  # noqa: E402
from ds60sqlpy.curriculum_framework import RUNNERS  # noqa: E402
from ds60sqlpy.modules import ModuleCatalog  # noqa: E402
from scripts.audit_lesson_depth import (  # noqa: E402
    DEFINITION,
    MIN_DEFINITIONS,
    MIN_GUIDE_CODE_BLOCKS,
    MIN_GUIDE_WORDS,
    MIN_SOLUTION_WORDS,
    _code_block_count,
    _practice_blocks,
    _word_count,
)
from scripts.audit_practice import count_practice  # noqa: E402

MATRIX_PATH = REPO_ROOT / "curriculum" / "coverage-matrix.json"
REPORT_PATH = REPO_ROOT / "docs" / "coverage-matrix.md"
SCHEMA_VERSION = 1
MIN_EXERCISES = 6

GAP_CODES: dict[str, str] = {
    "missing-path": "A cataloged lesson, guide or solution file does not exist.",
    "missing-outcome": "The catalog entry has no learner-facing outcome.",
    "unknown-prerequisite": "A prerequisite names an id that is not in either catalog.",
    "guide-no-orientation": (
        "The guide states neither prerequisites nor objectives in its own text."
    ),
    "thin-guide": f"The guide has fewer than {MIN_GUIDE_WORDS} words.",
    "few-examples": f"The guide has fewer than {MIN_GUIDE_CODE_BLOCKS} fenced examples.",
    "few-terms": f"The guide defines fewer than {MIN_DEFINITIONS} terms.",
    "few-exercises": f"A practice lesson has fewer than {MIN_EXERCISES} exercises.",
    "missing-solution": "A practice lesson has no solution artifact.",
    "thin-solution": (
        f"A practice lesson's Markdown solution has fewer than {MIN_SOLUTION_WORDS} words."
    ),
}

PRACTICE_ONLY_GAPS = frozenset({"few-exercises", "missing-solution", "thin-solution"})

HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
PREREQUISITE_HEADING = re.compile(
    r"prerequisite|before you (?:start|begin)|you should (?:already )?know|"
    r"starting point|what you need",
    re.IGNORECASE,
)
PREREQUISITE_LINE = re.compile(r"^\s*(?:[-*]\s*)?\*\*prerequisites?:?\*\*", re.IGNORECASE)
OBJECTIVE_HEADING = re.compile(
    r"objective|outcome|you will (?:learn|be able)|goal|learning target|"
    r"starting point and result|question and mechanism",
    re.IGNORECASE,
)
OBJECTIVE_LINE = re.compile(
    r"^\s*(?:[-*]\s*)?\*\*(?:objectives?|outcomes?|goals?):?\*\*",
    re.IGNORECASE,
)
VOCABULARY_HEADING = re.compile(
    r"vocabulary|terms|glossary|key concepts|definitions|mental model",
    re.IGNORECASE,
)
VOCABULARY_ITEM = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+\S|^\|(?!\s*-)(?!\s*:?-).+\|")
LABEL_TERM = re.compile(
    r"(?:expected|verify|verification|hints?|progressive|reasoning|why|observe|"
    r"independent|prompt|check|self[- ]check|alternative|edge case|level|learner|"
    r"outcome|how to|direct prerequisites?|prerequisites?|starting|context|"
    r"hand[- ]derived|inputs?|artifacts?|exercise|answer|solution|note|tip|"
    r"common|evidence|clause|intermediate|step|result|output|goal|objective|task|"
    r"question|example|warning|important|caution|recap|takeaway|summary|run|try|"
    r"source|reference|book|chapter|interview|what|when|where|which|who|how|"
    r"does|is|are|can|should|test|mistake|diagnosis|fix|repair|limit|caveat)\b",
    re.IGNORECASE,
)
STANDALONE_BOLD = re.compile(r"^\s*\*\*([^*\n]{2,60})\*\*\s*$", re.MULTILINE)
INLINE_BOLD = re.compile(r"\*\*([^*\n]{2,40})\*\*")
EXERCISE_LABEL = re.compile(
    r"\b(?:exercise|todo|task|practice|challenge|problem)\s*(\d{1,2})\b",
    re.IGNORECASE,
)
NUMBERED_HEADING = re.compile(r"^#{2,6}\s+(\d{1,2})[.)]\s")
PRACTICE_HEADING_SEARCH = re.compile(
    r"(?:exercise|practice|challenge|project task|checkpoint)", re.IGNORECASE
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _sections(source: str) -> list[tuple[str, int, list[str]]]:
    """Split Markdown into (heading, level, body lines) outside code fences."""

    sections: list[tuple[str, int, list[str]]] = [("", 0, [])]
    fenced = False
    for line in source.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        match = None if fenced else HEADING_LINE.match(line)
        if match is not None:
            sections.append((match.group(2), len(match.group(1)), []))
            continue
        sections[-1][2].append(line)
    return sections


def _section_lines(source: str, pattern: re.Pattern[str]) -> list[str]:
    """Return body lines of every heading matching pattern, including subsections."""

    lines: list[str] = []
    active_level = 0
    for title, level, body in _sections(source):
        if active_level and level and level <= active_level:
            active_level = 0
        if level and pattern.search(title):
            active_level = level
        if active_level:
            lines.extend(body)
    return lines


def orientation(source: str) -> dict[str, bool]:
    """Report whether a guide states prerequisites, objectives and vocabulary."""

    titles = [title for title, level, _ in _sections(source) if level]
    lines = source.splitlines()
    return {
        "states_prerequisites": any(PREREQUISITE_HEADING.search(t) for t in titles)
        or any(PREREQUISITE_LINE.match(line) for line in lines),
        "states_objectives": any(OBJECTIVE_HEADING.search(t) for t in titles)
        or any(OBJECTIVE_LINE.match(line) for line in lines),
        "has_vocabulary": any(VOCABULARY_HEADING.search(t) for t in titles),
    }


def _is_label(term: str) -> bool:
    return LABEL_TERM.match(term.strip()) is not None


def term_count(source: str) -> int:
    """Count defined terms, ignoring instructional labels such as hints.

    A term is a bold definition lead-in, a standalone bold concept line, a
    bold phrase inside a vocabulary section or a vocabulary list/table item.
    """

    terms = {
        match.group("term").strip().lower()
        for match in DEFINITION.finditer(source)
        if not _is_label(match.group("term"))
    }
    terms |= {
        match.group(1).strip().lower()
        for match in STANDALONE_BOLD.finditer(source)
        if not _is_label(match.group(1))
    }
    vocabulary = _section_lines(source, VOCABULARY_HEADING)
    for line in vocabulary:
        terms |= {
            match.group(1).strip().lower()
            for match in INLINE_BOLD.finditer(line)
            if not _is_label(match.group(1))
        }
        if VOCABULARY_ITEM.match(line):
            terms.add(line.strip().lower())
    return len(terms)


def module_exercise_count(texts: Iterable[str]) -> int:
    """Count module exercises from labels, numbered practice headings or items."""

    best = 0
    for text in texts:
        labels = {int(match.group(1)) for match in EXERCISE_LABEL.finditer(text)}
        numbered = {
            int(match.group(1))
            for line in _section_lines(text, PRACTICE_HEADING_SEARCH)
            if (match := NUMBERED_HEADING.match(line)) is not None
        }
        best = max(best, len(labels), len(numbered), len(_practice_blocks(text)))
    return best


def _solution_words(paths: Sequence[Path]) -> int | None:
    counts = [_word_count(_read(path)) for path in paths if path.suffix == ".md"]
    return min(counts) if counts else None


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _gaps(row: Mapping[str, Any]) -> list[str]:
    metrics = row["metrics"]
    gaps: list[str] = []
    if row["paths"]["missing"]:
        gaps.append("missing-path")
    if not row["outcome"]:
        gaps.append("missing-outcome")
    if row["unknown_prerequisites"]:
        gaps.append("unknown-prerequisite")
    if row["paths"]["guide"]:
        if not (metrics["states_prerequisites"] or metrics["states_objectives"]):
            gaps.append("guide-no-orientation")
        if metrics["guide_words"] < MIN_GUIDE_WORDS:
            gaps.append("thin-guide")
        if metrics["examples"] < MIN_GUIDE_CODE_BLOCKS:
            gaps.append("few-examples")
        if metrics["terms"] < MIN_DEFINITIONS:
            gaps.append("few-terms")
    if row["learning_mode"] == "practice":
        if metrics["exercises"] < MIN_EXERCISES:
            gaps.append("few-exercises")
        if not row["paths"]["solutions"]:
            gaps.append("missing-solution")
        elif (
            metrics["solution_words"] is not None and metrics["solution_words"] < MIN_SOLUTION_WORDS
        ):
            gaps.append("thin-solution")
    return gaps


def _guide_metrics(guide_text: str) -> dict[str, Any]:
    return {
        "guide_words": _word_count(guide_text),
        "examples": _code_block_count(guide_text),
        "terms": term_count(guide_text),
        **orientation(guide_text),
    }


def _existing(paths: Iterable[Path]) -> list[str]:
    return [_rel(path) for path in paths if not path.exists()]


def _core_execution(lesson: Lesson) -> str:
    runner = RUNNERS.get(lesson.runner)
    kind = runner.kind if runner is not None else "code"
    return {"code": "runnable", "reading": "reading"}.get(kind, kind)


def core_rows(catalog: Catalog) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sequence, lesson in enumerate(
        sorted(catalog.lessons(), key=lambda item: (item.track, item.day, item.id)),
        start=1,
    ):
        lesson_path = catalog.resolve(lesson.lesson_path)
        guide_path = catalog.resolve(lesson.guide_path) if lesson.guide_path else None
        solutions = [catalog.resolve(path) for path in lesson.solution_paths]
        guide_text = _read(guide_path) if guide_path else ""
        dependencies = [
            value for value in (lesson.dependency_group, lesson.stateful_group) if value
        ]
        row: dict[str, Any] = {
            "id": lesson.id,
            "family": "core",
            "track": lesson.track,
            "track_title": catalog.tracks.get(lesson.track, {}).get("title", lesson.track),
            "sequence": sequence,
            "stage": lesson.phase,
            "level": lesson.level,
            "title": lesson.title,
            "status": "authored",
            "learning_mode": "practice",
            "execution": _core_execution(lesson),
            "runtime": lesson.runner,
            "language": lesson.runner if _core_execution(lesson) == "runnable" else None,
            "network": lesson.network,
            "dependencies": dependencies,
            "prerequisites": list(lesson.prerequisites),
            "unknown_prerequisites": [],
            "outcome": bool(lesson.outcome),
            "paths": {
                "lesson": _rel(lesson_path),
                "guide": _rel(guide_path) if guide_path else None,
                "solutions": [_rel(path) for path in solutions],
                "missing": _existing([lesson_path, *solutions, *filter(None, [guide_path])]),
            },
            "verification": "course-check",
            "artifacts": [],
            "variants": [],
            "metrics": {
                **_guide_metrics(guide_text),
                "exercises": count_practice(lesson_path) if lesson_path.exists() else 0,
                "solution_words": _solution_words(solutions),
            },
        }
        rows.append(row)
    return rows


def _module_execution(runtime: str) -> str:
    if runtime == "reading":
        return "reading"
    if runtime == "k8s-kind":
        return "operations"
    return "runnable"


def module_rows(modules: ModuleCatalog) -> list[dict[str, Any]]:
    index = modules.index()
    indexed = {lesson["id"]: lesson for track in index["tracks"] for lesson in track["lessons"]}
    rows: list[dict[str, Any]] = []
    for plan in sorted(modules.plans, key=lambda item: str(item["id"])):
        for sequence, planned in enumerate(plan["lessons"], start=1):
            lesson_id = str(planned["id"])
            lesson = modules.lessons.get(lesson_id)
            entry = indexed.get(lesson_id, {})
            guide_path = REPO_ROOT / lesson.guide_path if lesson else None
            source_path = REPO_ROOT / lesson.source_path if lesson else None
            solutions = [REPO_ROOT / path for path in (lesson.solution_paths if lesson else ())]
            guide_text = _read(guide_path) if guide_path else ""
            source_text = _read(source_path) if source_path else ""
            runtime = str(lesson.runtime_profile if lesson else planned.get("runtime", ""))
            mode = lesson.learning_mode if lesson else str(entry.get("learning_mode", "tutorial"))
            practice = mode == "practice"
            artifacts = [str(item) for item in planned.get("expected_outputs", []) or []]
            row: dict[str, Any] = {
                "id": lesson_id,
                "family": "module",
                "track": str(plan["id"]),
                "track_title": str(plan["title"]),
                "sequence": sequence,
                "stage": str(planned.get("level", "")),
                "level": str(planned.get("level", "")),
                "title": str(planned.get("title", "")),
                "status": str(entry.get("status", "authored" if lesson else "planned")),
                "learning_mode": mode,
                "execution": _module_execution(runtime),
                "runtime": runtime,
                "language": lesson.language if lesson else None,
                "network": None,
                "dependencies": [str(item) for item in planned.get("dependencies", []) or []],
                "prerequisites": [str(item) for item in planned.get("prerequisites", [])],
                "unknown_prerequisites": [],
                "outcome": bool(planned.get("outcome")),
                "paths": {
                    "lesson": _rel(source_path) if source_path else None,
                    "guide": _rel(guide_path) if guide_path else None,
                    "solutions": [_rel(path) for path in solutions],
                    "missing": _existing([*filter(None, [guide_path, source_path]), *solutions]),
                },
                "verification": (lesson.verification_id if lesson else None)
                or ("reading-check" if runtime == "reading" else "module-check"),
                "artifacts": artifacts,
                "variants": [str(item["id"]) for item in entry.get("variants", [])],
                "metrics": {
                    **_guide_metrics(guide_text),
                    "exercises": module_exercise_count([source_text, guide_text])
                    if practice
                    else 0,
                    "solution_words": _solution_words(solutions),
                },
            }
            rows.append(row)
    return rows


def build_rows(catalog: Catalog, modules: ModuleCatalog) -> list[dict[str, Any]]:
    rows = core_rows(catalog) + module_rows(modules)
    known = {row["id"] for row in rows} | set(modules.lessons)
    for row in rows:
        row["unknown_prerequisites"] = [item for item in row["prerequisites"] if item not in known]
        row["gaps"] = _gaps(row)
    return rows


def coverage_problems(
    rows: Sequence[Mapping[str, Any]], catalog: Catalog, modules: ModuleCatalog
) -> list[str]:
    """Return lessons that are absent from or duplicated in the matrix."""

    counts = Counter(str(row["id"]) for row in rows)
    expected = {lesson.id for lesson in catalog.lessons()} | set(modules.canonical_ids)
    problems = [f"duplicate row: {lesson_id}" for lesson_id, n in counts.items() if n > 1]
    problems += [f"uncovered lesson: {lesson_id}" for lesson_id in sorted(expected - set(counts))]
    problems += [f"unexpected row: {lesson_id}" for lesson_id in sorted(set(counts) - expected)]
    for row in rows:
        unknown = set(row["gaps"]) - set(GAP_CODES)
        if unknown:
            problems.append(f"unknown gap code on {row['id']}: {sorted(unknown)}")
    return problems


def render_json(rows: Sequence[Mapping[str, Any]]) -> str:
    header = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "scripts/build_coverage_matrix.py",
        "thresholds": {
            "guide_words": MIN_GUIDE_WORDS,
            "examples": MIN_GUIDE_CODE_BLOCKS,
            "terms": MIN_DEFINITIONS,
            "exercises": MIN_EXERCISES,
            "solution_words": MIN_SOLUTION_WORDS,
        },
        "gap_codes": GAP_CODES,
        "lesson_count": len(rows),
    }
    head = json.dumps(header, indent=2, ensure_ascii=False)
    body = ",\n".join(
        "    " + json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
    )
    return head[:-2] + ',\n  "lessons": [\n' + body + "\n  ]\n}\n"


def _median(values: Sequence[int]) -> int:
    ordered = sorted(values)
    if not ordered:
        return 0
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def _track_summaries(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["family"]), str(row["track"]))].append(row)
    summaries = []
    for (family, track), items in sorted(grouped.items()):
        gap_counts = Counter(gap for item in items for gap in item["gaps"])
        modes = Counter(str(item["learning_mode"]) for item in items)
        execution = Counter(str(item["execution"]) for item in items)
        words = [int(item["metrics"]["guide_words"]) for item in items]
        summaries.append(
            {
                "family": family,
                "track": track,
                "title": items[0]["track_title"],
                "lessons": len(items),
                "authored": sum(item["status"] == "authored" for item in items),
                "practice": modes.get("practice", 0),
                "tutorial": modes.get("tutorial", 0),
                "execution": execution,
                "median_words": _median(words),
                "min_words": min(words) if words else 0,
                "gap_counts": gap_counts,
                "clean": sum(not item["gaps"] for item in items),
            }
        )
    return summaries


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|")


def render_report(rows: Sequence[Mapping[str, Any]], capstones: Mapping[str, int]) -> str:
    summaries = _track_summaries(rows)
    total_gaps = Counter(gap for row in rows for gap in row["gaps"])
    clean = sum(not row["gaps"] for row in rows)
    folded = sum(max(len(row["variants"]) - 1, 0) for row in rows)
    lines = [
        "# Catalog coverage matrix",
        "",
        "Generated by `scripts/build_coverage_matrix.py` from `curriculum/catalog.json`",
        "inputs and the module manifests. Do not edit by hand; run",
        "`make generate` or `python scripts/build_coverage_matrix.py --write`.",
        "The machine-readable rows live in `curriculum/coverage-matrix.json`.",
        "",
        "Every core lesson and every canonical module lesson appears exactly once.",
        "Gaps describe what a lesson still lacks against the shared teaching",
        "contract; they are a work queue, not a failure. CI fails only when this",
        "file drifts from the catalogs or a cataloged lesson is missing.",
        "",
        "## Totals",
        "",
        f"- Lessons: {len(rows)}"
        f" ({sum(row['family'] == 'core' for row in rows)} core,"
        f" {sum(row['family'] == 'module' for row in rows)} module)",
        f"- Tracks: {len(summaries)}",
        f"- Authored: {sum(row['status'] == 'authored' for row in rows)};"
        f" planned: {sum(row['status'] != 'authored' for row in rows)}",
        f"- Execution: {sum(row['execution'] == 'runnable' for row in rows)} runnable,"
        f" {sum(row['execution'] == 'reading' for row in rows)} reading,"
        f" {sum(row['execution'] == 'operations' for row in rows)} operations",
        f"- Module variants folded into canonical rows: {folded}"
        f" across {sum(len(row['variants']) > 1 for row in rows)} lessons",
        f"- Lessons with no recorded gap: {clean}",
        "",
        "## Gap codes",
        "",
        "| Code | Meaning | Lessons |",
        "| --- | --- | ---: |",
    ]
    for code, meaning in GAP_CODES.items():
        lines.append(f"| `{code}` | {meaning} | {total_gaps.get(code, 0)} |")
    lines += [
        "",
        "Exercise and solution gaps apply only to practice lessons. Tutorial",
        "lessons are complete worked chapters and carry no exercise contract.",
        "",
        "## Tracks",
        "",
        "| Family | Track | Lessons | Practice | Tutorial | Runnable | Reading |"
        " Operations | Capstones | Median words | No gaps |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        execution = summary["execution"]
        lines.append(
            f"| {summary['family']} | {_cell(summary['title'])} (`{summary['track']}`) |"
            f" {summary['lessons']} | {summary['practice']} | {summary['tutorial']} |"
            f" {execution.get('runnable', 0)} | {execution.get('reading', 0)} |"
            f" {execution.get('operations', 0)} | {capstones.get(summary['track'], 0)} |"
            f" {summary['median_words']} | {summary['clean']} |"
        )
    lines += [
        "",
        "## Gaps by track",
        "",
        "Counts of lessons per gap code. Tracks with no gaps are omitted.",
        "",
        "| Track | " + " | ".join(f"`{code}`" for code in GAP_CODES) + " |",
        "| --- |" + " ---: |" * len(GAP_CODES),
    ]
    for summary in summaries:
        counts = summary["gap_counts"]
        if not counts:
            continue
        lines.append(
            f"| `{summary['track']}` | "
            + " | ".join(str(counts.get(code, 0)) for code in GAP_CODES)
            + " |"
        )
    lines += [
        "",
        "## Reading a row",
        "",
        "Each JSON row records the lesson id, family, track, sequence, stage,",
        "level, status, learning mode, execution kind (runnable, reading or",
        "operations), runtime, dependencies, prerequisites, source/guide/solution",
        "paths, verification, expected artifacts, variants, measured teaching",
        "signals and gap codes. Guide orientation is measured from the guide",
        "text itself; the classroom also shows catalog outcomes and prerequisites.",
        "",
    ]
    return "\n".join(lines)


def build() -> tuple[str, str, list[str]]:
    catalog = Catalog.load(REPO_ROOT)
    modules = ModuleCatalog(REPO_ROOT)
    rows = build_rows(catalog, modules)
    capstones = {str(plan["id"]): len(plan.get("capstones", [])) for plan in modules.plans}
    problems = coverage_problems(rows, catalog, modules)
    return render_json(rows), render_report(rows, capstones), problems


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Write the matrix and report.")
    mode.add_argument("--check", action="store_true", help="Fail when outputs drift.")
    mode.add_argument("--json", action="store_true", help="Print the matrix JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    matrix, report, problems = build()
    for problem in problems:
        print(f"FAIL {problem}", file=sys.stderr)
    if args.json:
        print(matrix, end="")
    elif args.write:
        MATRIX_PATH.write_text(matrix, encoding="utf-8")
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Wrote {_rel(MATRIX_PATH)} and {_rel(REPORT_PATH)}")
    elif args.check:
        stale = [
            _rel(path)
            for path, text in ((MATRIX_PATH, matrix), (REPORT_PATH, report))
            if _read(path) != text
        ]
        for path in stale:
            print(
                f"FAIL {path} is stale; run scripts/build_coverage_matrix.py --write",
                file=sys.stderr,
            )
        if stale:
            return 1
        print("Coverage matrix is current")
    else:
        rows = json.loads(matrix)["lessons"]
        print(
            f"Coverage matrix: {len(rows)} lessons, "
            f"{sum(not row['gaps'] for row in rows)} with no recorded gap"
        )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
