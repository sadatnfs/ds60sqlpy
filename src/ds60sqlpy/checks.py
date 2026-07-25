"""Structural repository validation used locally and in CI."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.catalog_builder import build_catalog

Severity = Literal["pass", "warn", "fail"]


@dataclass(frozen=True, slots=True)
class CheckResult:
    """One validation result."""

    severity: Severity
    code: str
    message: str
    path: str | None = None


def _result(
    severity: Severity,
    code: str,
    message: str,
    path: Path | None = None,
    root: Path | None = None,
) -> CheckResult:
    display_path: str | None = None
    if path is not None:
        display_path = (
            path.relative_to(root).as_posix()
            if root is not None and path.is_relative_to(root)
            else path.as_posix()
        )
    return CheckResult(severity, code, message, display_path)


def check_catalog(catalog: Catalog) -> list[CheckResult]:
    """Check catalog coverage, references, and generated-file drift."""

    root = catalog.repo_root
    results: list[CheckResult] = []
    expected_counts = {"python": 60, "sql": 60, "bridge": 8}
    for track, expected in expected_counts.items():
        count = len(catalog.lessons(track))  # type: ignore[arg-type]
        severity: Severity = "pass" if count == expected else "fail"
        results.append(
            _result(
                severity,
                f"catalog.{track}.count",
                f"{track} catalog has {count}/{expected} lessons",
            )
        )

    lesson_ids = {lesson.id for lesson in catalog}
    for lesson in catalog:
        missing_prerequisites = [
            prerequisite for prerequisite in lesson.prerequisites if prerequisite not in lesson_ids
        ]
        if missing_prerequisites:
            results.append(
                _result(
                    "fail",
                    "catalog.prerequisite",
                    f"{lesson.id} has unknown prerequisites: {missing_prerequisites}",
                )
            )
        for field, relative_path in (
            ("lesson", lesson.lesson_path),
            ("guide", lesson.guide_path),
        ):
            path = catalog.resolve(relative_path)
            if not path.is_file():
                results.append(
                    _result(
                        "fail",
                        "catalog.missing",
                        f"{lesson.id} references missing {field}",
                        path,
                        root,
                    )
                )
        for relative_path in lesson.solution_paths:
            path = catalog.resolve(relative_path)
            if not path.is_file():
                results.append(
                    _result(
                        "fail",
                        "catalog.solution.missing",
                        f"{lesson.id} references a missing solution",
                        path,
                        root,
                    )
                )
        if len(lesson.solution_paths) != 2:
            results.append(
                _result(
                    "fail",
                    "catalog.solution.coverage",
                    f"{lesson.id} has {len(lesson.solution_paths)}/2 solution artifacts",
                )
            )

    checked_path = root / "curriculum" / "catalog.json"
    checked_payload = json.loads(checked_path.read_text(encoding="utf-8"))
    if checked_payload != build_catalog(root):
        results.append(
            _result(
                "fail",
                "catalog.drift",
                "Catalog is stale; run python scripts/build_catalog.py",
                checked_path,
                root,
            )
        )
    else:
        results.append(_result("pass", "catalog.drift", "Catalog matches course artifacts"))
    return results


def _clean_notebook_source(source: str) -> str:
    lines = []
    for line in source.splitlines():
        if line.lstrip().startswith(("%", "!")):
            continue
        lines.append(line)
    return "\n".join(lines)


def check_notebooks(catalog: Catalog) -> list[CheckResult]:
    """Validate notebook JSON, format metadata, and ordinary Python syntax."""

    root = catalog.repo_root
    notebook_paths = sorted((root / "python" / "ds-60day").rglob("*.ipynb"))
    results: list[CheckResult] = []
    invalid = 0
    syntax_errors = 0
    metadata_warnings = 0
    format_errors = 0
    cell_id_errors = 0
    saved_state_errors = 0

    for path in notebook_paths:
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            invalid += 1
            results.append(
                _result("fail", "notebook.json", f"Invalid notebook JSON: {exc}", path, root)
            )
            continue

        if notebook.get("nbformat") != 4 or notebook.get("nbformat_minor") != 5:
            format_errors += 1
            results.append(
                _result(
                    "fail",
                    "notebook.nbformat",
                    "Notebook must use nbformat 4.5",
                    path,
                    root,
                )
            )
        metadata = notebook.get("metadata", {})
        kernelspec = metadata.get("kernelspec") if isinstance(metadata, dict) else None
        if not isinstance(kernelspec, dict) or kernelspec.get("name") != "ds60sqlpy":
            metadata_warnings += 1
            results.append(
                _result(
                    "warn",
                    "notebook.kernelspec",
                    "Notebook lacks the standard ds60sqlpy kernelspec",
                    path,
                    root,
                )
            )

        course_metadata = metadata.get("course") if isinstance(metadata, dict) else None
        required_course_fields = {"artifact", "day", "lesson_id", "tags", "track"}
        if not isinstance(course_metadata, dict) or not required_course_fields.issubset(
            course_metadata
        ):
            metadata_warnings += 1
            results.append(
                _result(
                    "warn",
                    "notebook.course_metadata",
                    "Notebook lacks complete course metadata",
                    path,
                    root,
                )
            )

        cells = notebook.get("cells")
        if not isinstance(cells, list):
            format_errors += 1
            results.append(
                _result(
                    "fail",
                    "notebook.cells",
                    "Notebook cells must be a list",
                    path,
                    root,
                )
            )
            continue

        seen_cell_ids: set[str] = set()
        for index, cell in enumerate(cells, start=1):
            cell_id = cell.get("id")
            if not isinstance(cell_id, str) or not cell_id or cell_id in seen_cell_ids:
                cell_id_errors += 1
                results.append(
                    _result(
                        "fail",
                        "notebook.cell_id",
                        f"Cell {index} has a missing or duplicate ID",
                        path,
                        root,
                    )
                )
            else:
                seen_cell_ids.add(cell_id)

            if cell.get("cell_type") != "code":
                continue
            if cell.get("execution_count") is not None or cell.get("outputs"):
                saved_state_errors += 1
                results.append(
                    _result(
                        "fail",
                        "notebook.saved_state",
                        f"Code cell {index} contains saved execution state",
                        path,
                        root,
                    )
                )
            source = _clean_notebook_source("".join(cell.get("source", [])))
            if not source.strip():
                continue
            try:
                ast.parse(source)
            except SyntaxError as exc:
                syntax_errors += 1
                results.append(
                    _result(
                        "fail",
                        "notebook.syntax",
                        f"Code cell {index} is not valid Python: {exc.msg}",
                        path,
                        root,
                    )
                )

    results.append(
        _result(
            "pass" if len(notebook_paths) == 120 else "fail",
            "notebook.count",
            f"Notebook artifacts: {len(notebook_paths)}/120",
        )
    )
    results.append(
        _result(
            "pass" if invalid == 0 else "fail",
            "notebook.json.summary",
            f"{len(notebook_paths) - invalid}/{len(notebook_paths)} notebooks are valid JSON",
        )
    )
    results.append(
        _result(
            "pass" if format_errors == 0 else "fail",
            "notebook.nbformat.summary",
            f"Notebook format errors: {format_errors}",
        )
    )
    results.append(
        _result(
            "pass" if cell_id_errors == 0 else "fail",
            "notebook.cell_id.summary",
            f"Notebook cell-ID errors: {cell_id_errors}",
        )
    )
    results.append(
        _result(
            "pass" if saved_state_errors == 0 else "fail",
            "notebook.saved_state.summary",
            f"Code cells with saved execution state: {saved_state_errors}",
        )
    )
    results.append(
        _result(
            "pass" if syntax_errors == 0 else "fail",
            "notebook.syntax.summary",
            f"Notebook syntax errors: {syntax_errors}",
        )
    )
    if metadata_warnings == 0:
        results.append(
            _result(
                "pass",
                "notebook.kernelspec.summary",
                "Notebook metadata is uniform",
            )
        )
    return results


def check_sql(catalog: Catalog) -> list[CheckResult]:
    """Check SQL lesson wrappers and session setup."""

    root = catalog.repo_root
    results: list[CheckResult] = []
    scripts = sorted((root / "sql" / "postgres-60day").glob("day*.sql"))
    for script in scripts:
        source = script.read_text(encoding="utf-8")
        if not re.search(r"(?im)^BEGIN\s*;", source):
            results.append(_result("fail", "sql.transaction.begin", "Missing BEGIN", script, root))
        if "SET search_path TO" not in source:
            results.append(
                _result("fail", "sql.search_path", "Missing explicit search_path", script, root)
            )
        expected_end = "COMMIT;" if script.name.startswith("day52_") else "ROLLBACK;"
        if not re.search(rf"(?im)^{expected_end[:-1]}\s*;", source):
            results.append(
                _result(
                    "fail",
                    "sql.transaction.end",
                    f"Expected {expected_end} for this lesson",
                    script,
                    root,
                )
            )

    solution_scripts = sorted(
        (root / "sql" / "postgres-60day" / "solutions").glob("day*_solutions.sql")
    )
    missing_search_path = [
        path
        for path in solution_scripts
        if "SET search_path TO" not in path.read_text(encoding="utf-8")
    ]
    for path in missing_search_path:
        results.append(
            _result(
                "fail",
                "sql.solution.search_path",
                "Executable solution lacks an explicit search_path",
                path,
                root,
            )
        )
    results.append(
        _result(
            "pass" if len(scripts) == 60 else "fail",
            "sql.lesson.count",
            f"SQL lesson scripts: {len(scripts)}/60",
        )
    )
    results.append(
        _result(
            "pass" if not missing_search_path else "fail",
            "sql.solution.search_path.summary",
            f"Executable SQL solutions missing search_path: {len(missing_search_path)}",
        )
    )
    results.append(
        _result(
            "pass" if len(solution_scripts) == 60 else "fail",
            "sql.solution.count",
            f"Executable SQL solutions: {len(solution_scripts)}/60",
        )
    )
    return results


SQL_GUIDE_REQUIRED_SECTIONS = (
    "Level and prerequisites",
    "Learning objectives",
    "Vocabulary and concepts",
    "Worked example / walkthrough",
    "Exercises",
    "Self-check",
    "Next step",
)
MARKDOWN_H2 = re.compile(r"(?m)^## (?P<title>[^\n]+)\s*$")


def _markdown_h2_sections(source: str) -> dict[str, list[str]]:
    """Return second-level Markdown section bodies, preserving duplicate headings."""

    matches = list(MARKDOWN_H2.finditer(source))
    sections: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        sections.setdefault(match.group("title").strip(), []).append(
            source[match.end() : end].strip()
        )
    return sections


def check_sql_guide_contract(catalog: Catalog) -> list[CheckResult]:
    """Require the learner-facing authoring contract in every SQL guide."""

    root = catalog.repo_root
    lessons = catalog.lessons("sql")
    results: list[CheckResult] = []
    contract_errors = 0

    for index, lesson in enumerate(lessons):
        path = catalog.resolve(lesson.guide_path)
        if not path.is_file():
            continue  # check_catalog reports the missing artifact.

        source = path.read_text(encoding="utf-8")
        sections = _markdown_h2_sections(source)
        heading_positions = {
            heading: source.find(f"## {heading}\n") for heading in SQL_GUIDE_REQUIRED_SECTIONS
        }

        for heading in SQL_GUIDE_REQUIRED_SECTIONS:
            bodies = sections.get(heading, [])
            if len(bodies) != 1:
                contract_errors += 1
                results.append(
                    _result(
                        "fail",
                        "sql.guide.section",
                        f"{lesson.id} needs exactly one '## {heading}' section",
                        path,
                        root,
                    )
                )
                continue
            minimum_characters = 30 if heading == "Next step" else 60
            if len(re.sub(r"\s+", " ", bodies[0]).strip()) < minimum_characters:
                contract_errors += 1
                results.append(
                    _result(
                        "fail",
                        "sql.guide.section.content",
                        f"{lesson.id} section '## {heading}' is too thin",
                        path,
                        root,
                    )
                )

        if all(position >= 0 for position in heading_positions.values()):
            ordered_positions = [heading_positions[name] for name in SQL_GUIDE_REQUIRED_SECTIONS]
            if ordered_positions != sorted(ordered_positions):
                contract_errors += 1
                results.append(
                    _result(
                        "fail",
                        "sql.guide.section.order",
                        f"{lesson.id} guide-contract sections are out of order",
                        path,
                        root,
                    )
                )

        overview = sections.get("Level and prerequisites", [""])[0]
        level_match = re.search(r"(?im)^- \*\*Level:\*\*\s+(.+)$", overview)
        if level_match is None or not level_match.group(1).casefold().startswith(
            lesson.level.casefold()
        ):
            contract_errors += 1
            results.append(
                _result(
                    "fail",
                    "sql.guide.level",
                    f"{lesson.id} level must begin with catalog level '{lesson.level}'",
                    path,
                    root,
                )
            )

        expected_prerequisite = (
            "../README.md" if lesson.day == 1 else Path(lessons[index - 1].guide_path).name
        )
        if expected_prerequisite not in overview:
            contract_errors += 1
            results.append(
                _result(
                    "fail",
                    "sql.guide.prerequisite",
                    f"{lesson.id} must link prerequisite {expected_prerequisite}",
                    path,
                    root,
                )
            )

        lesson_filename = Path(lesson.lesson_path).name
        if lesson_filename not in overview:
            contract_errors += 1
            results.append(
                _result(
                    "fail",
                    "sql.guide.artifact",
                    f"{lesson.id} must link learner artifact {lesson_filename}",
                    path,
                    root,
                )
            )

        for heading, minimum_items in (
            ("Learning objectives", 2),
            ("Vocabulary and concepts", 2),
            ("Self-check", 2),
        ):
            body = sections.get(heading, [""])[0]
            if len(re.findall(r"(?m)^- ", body)) < minimum_items:
                contract_errors += 1
                results.append(
                    _result(
                        "fail",
                        "sql.guide.section.items",
                        f"{lesson.id} section '## {heading}' needs {minimum_items} list items",
                        path,
                        root,
                    )
                )

        next_target = (
            Path(lessons[index + 1].guide_path).name
            if index + 1 < len(lessons)
            else "../../../bridge/README.md"
        )
        next_body = sections.get("Next step", [""])[0]
        if next_target not in next_body:
            contract_errors += 1
            results.append(
                _result(
                    "fail",
                    "sql.guide.next",
                    f"{lesson.id} must link next target {next_target}",
                    path,
                    root,
                )
            )

    results.append(
        _result(
            "pass" if len(lessons) == 60 else "fail",
            "sql.guide.count",
            f"SQL companion guides: {len(lessons)}/60",
        )
    )
    results.append(
        _result(
            "pass" if contract_errors == 0 else "fail",
            "sql.guide.contract.summary",
            f"SQL companion-guide contract errors: {contract_errors}",
        )
    )
    return results


def check_bridge(catalog: Catalog) -> list[CheckResult]:
    """Check bridge artifact coverage and Python syntax without requiring PostgreSQL."""

    root = catalog.repo_root
    bridge_root = root / "bridge"
    groups = {
        "lesson": sorted((bridge_root / "lessons").glob("day*.py")),
        "guide": sorted((bridge_root / "companion-guides").glob("day*.md")),
        "solution_python": sorted((bridge_root / "solutions").glob("day*_solution.py")),
        "solution_markdown": sorted((bridge_root / "solutions").glob("day*_solutions.md")),
    }
    results: list[CheckResult] = []
    for artifact, paths in groups.items():
        results.append(
            _result(
                "pass" if len(paths) == 8 else "fail",
                f"bridge.{artifact}.count",
                f"Bridge {artifact.replace('_', ' ')} artifacts: {len(paths)}/8",
            )
        )

    syntax_errors = 0
    for path in [*groups["lesson"], *groups["solution_python"]]:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            syntax_errors += 1
            results.append(
                _result(
                    "fail",
                    "bridge.syntax",
                    f"Invalid Python: {exc.msg} (line {exc.lineno})",
                    path,
                    root,
                )
            )
    results.append(
        _result(
            "pass" if syntax_errors == 0 else "fail",
            "bridge.syntax.summary",
            f"Bridge Python syntax errors: {syntax_errors}",
        )
    )
    return results


MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")


def check_markdown_links(catalog: Catalog) -> list[CheckResult]:
    """Check repository-local Markdown links."""

    root = catalog.repo_root
    results: list[CheckResult] = []
    checked = 0
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv"} for part in path.parts):
            continue
        source = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(source):
            target = match.group("target").strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            checked += 1
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                results.append(
                    _result(
                        "fail",
                        "markdown.link",
                        f"Broken link target: {target}",
                        path,
                        root,
                    )
                )
    results.append(
        _result(
            "pass" if not any(result.code == "markdown.link" for result in results) else "fail",
            "markdown.link.summary",
            f"Checked {checked} local Markdown links",
        )
    )
    return results


def run_checks(catalog: Catalog) -> tuple[CheckResult, ...]:
    """Run every fast, dependency-free repository check."""

    groups: Iterable[Iterable[CheckResult]] = (
        check_catalog(catalog),
        check_notebooks(catalog),
        check_sql(catalog),
        check_sql_guide_contract(catalog),
        check_bridge(catalog),
        check_markdown_links(catalog),
    )
    return tuple(result for group in groups for result in group)
