#!/usr/bin/env python3
"""Build the generated Day 46-60 solution notebooks from Markdown guides.

Python code fences become executable cells. Other fenced blocks remain Markdown
so shell, Dockerfile, YAML, and prose examples are never executed accidentally.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import nbformat
from nbformat import NotebookNode
from normalize_notebooks import normalize_notebook

REPO_ROOT = Path(__file__).resolve().parents[1]
SOLUTIONS_ROOT = REPO_ROOT / "python" / "ds-60day" / "solutions"
GENERATED_DAYS = range(46, 61)
PYTHON_FENCE_LANGUAGES = frozenset({"python", "py"})
FENCE_PATTERN = re.compile(r"^(?P<marker>`{3,}|~{3,})(?P<language>[\w+-]*)\s*$")


def _flush_markdown(cells: list[NotebookNode], lines: list[str]) -> None:
    source = "".join(lines).strip()
    if source:
        cells.append(
            nbformat.v4.new_markdown_cell(  # type: ignore[no-untyped-call]
                f"{source}\n"
            )
        )
    lines.clear()


def _flush_python(cells: list[NotebookNode], lines: list[str]) -> None:
    source = "".join(lines).strip("\n")
    if source:
        cells.append(
            nbformat.v4.new_code_cell(  # type: ignore[no-untyped-call]
                f"{source}\n"
            )
        )
    lines.clear()


def markdown_to_cells(source: str) -> list[NotebookNode]:
    """Convert Markdown into prose cells and executable Python-fence cells."""

    cells: list[NotebookNode] = []
    markdown_lines: list[str] = []
    python_lines: list[str] = []
    active_marker: str | None = None
    active_language: str | None = None

    source_lines = source.splitlines(keepends=True)
    for line in source_lines:
        stripped = line.strip()
        fence = FENCE_PATTERN.fullmatch(stripped)

        if active_marker is None:
            if fence is None:
                markdown_lines.append(line)
                continue

            active_marker = fence.group("marker")
            active_language = fence.group("language").lower()
            if active_language in PYTHON_FENCE_LANGUAGES:
                _flush_markdown(cells, markdown_lines)
            else:
                markdown_lines.append(line)
            continue

        is_closing_fence = (
            stripped and set(stripped) == {active_marker[0]} and len(stripped) >= len(active_marker)
        )
        if is_closing_fence:
            if active_language in PYTHON_FENCE_LANGUAGES:
                _flush_python(cells, python_lines)
            else:
                markdown_lines.append(line)
            active_marker = None
            active_language = None
            continue

        if active_language in PYTHON_FENCE_LANGUAGES:
            python_lines.append(line)
        else:
            markdown_lines.append(line)

    if active_marker is not None:
        raise ValueError(
            f"Unclosed {active_language or 'plain'} fence near line {len(source_lines)}"
        )

    _flush_markdown(cells, markdown_lines)
    return cells


def _solution_markdown(day: int, solutions_root: Path) -> Path:
    matches = sorted(solutions_root.glob(f"day{day:02d}_*/day{day:02d}_solutions.md"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected one Markdown solution for Day {day:02d}; found {len(matches)}"
        )
    return matches[0]


def build_notebook(markdown_path: Path, repo_root: Path) -> NotebookNode:
    """Build one deterministic notebook from its Markdown source."""

    day_match = re.search(r"day(?P<day>\d{2})_", markdown_path.name)
    if day_match is None:
        raise ValueError(f"Cannot determine day from {markdown_path}")
    relative_source = markdown_path.relative_to(repo_root)
    relative_notebook = markdown_path.with_suffix(".ipynb").relative_to(repo_root)
    cells = markdown_to_cells(markdown_path.read_text(encoding="utf-8"))

    notice = (
        "> Generated from "
        f"`{relative_source.as_posix()}` by `scripts/build_solution_notebooks.py`. "
        "Edit the Markdown source, then regenerate this notebook.\n"
    )
    if cells and cells[0].cell_type == "markdown":
        cells[0].source = f"{cells[0].source.rstrip()}\n\n{notice}"
    else:
        cells.insert(
            0,
            nbformat.v4.new_markdown_cell(notice),  # type: ignore[no-untyped-call]
        )

    notebook, _ = normalize_notebook(
        nbformat.v4.new_notebook(cells=cells),  # type: ignore[no-untyped-call]
        relative_path=relative_notebook,
    )
    return notebook


def generate(
    *,
    repo_root: Path,
    check: bool,
    days: range = GENERATED_DAYS,
) -> tuple[int, int]:
    """Generate notebooks and return ``(changed, checked)``."""

    solutions_root = repo_root / "python" / "ds-60day" / "solutions"
    changed = 0
    checked = 0
    for day in days:
        markdown_path = _solution_markdown(day, solutions_root)
        notebook_path = markdown_path.with_suffix(".ipynb")
        notebook = build_notebook(markdown_path, repo_root)
        rendered = nbformat.writes(notebook, version=4)  # type: ignore[no-untyped-call]
        checked += 1

        current = notebook_path.read_text(encoding="utf-8") if notebook_path.exists() else None
        if current == rendered:
            continue
        changed += 1
        if not check:
            notebook_path.write_text(rendered, encoding="utf-8", newline="\n")

    return changed, checked


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (defaults to the parent of scripts/).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report generated-notebook drift without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed, checked = generate(repo_root=args.repo_root.resolve(), check=args.check)
    action = "would change" if args.check else "changed"
    print(f"Solution notebooks checked: {checked}; {action}: {changed}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
