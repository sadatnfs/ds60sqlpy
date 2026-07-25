#!/usr/bin/env python3
"""Validate all course notebooks and optionally execute a fast offline subset."""

from __future__ import annotations

import argparse
import ast
import re
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Final

import nbformat
from nbformat import NotebookNode

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
COURSE_ROOT_RELATIVE: Final = Path("python") / "ds-60day"
DAY_PATTERN: Final = re.compile(r"day(?P<day>\d{2})_")
DEFAULT_SMOKE_DAYS: Final = (1, 3, 5, 8, 10, 12, 13, 16, 21, 31, 33, 34, 35)
SKIP_SMOKE_TAGS: Final = frozenset({"network", "slow", "gpu", "geo", "docker"})


def notebook_paths(repo_root: Path) -> Iterable[Path]:
    return sorted((repo_root / COURSE_ROOT_RELATIVE).rglob("*.ipynb"))


def _clean_python_source(source: str) -> str:
    lines = source.splitlines()
    if lines and lines[0].lstrip().startswith("%%"):
        lines = lines[1:]
    return "\n".join(line for line in lines if not line.lstrip().startswith(("%", "!")))


def _validate_one(path: Path, repo_root: Path) -> list[str]:
    relative = path.relative_to(repo_root).as_posix()
    failures: list[str] = []
    try:
        notebook = nbformat.read(path, as_version=4)  # type: ignore[no-untyped-call]
        nbformat.validate(notebook)
    except Exception as exc:
        return [f"{relative}: nbformat validation failed: {exc}"]

    if notebook.nbformat != 4 or notebook.nbformat_minor != 5:
        failures.append(
            f"{relative}: expected nbformat 4.5, got {notebook.nbformat}.{notebook.nbformat_minor}"
        )
    kernelspec = notebook.metadata.get("kernelspec", {})
    if kernelspec.get("name") != "ds60sqlpy":
        failures.append(f"{relative}: kernelspec.name must be ds60sqlpy")
    if notebook.metadata.get("language_info", {}).get("name") != "python":
        failures.append(f"{relative}: language_info.name must be python")

    course = notebook.metadata.get("course", {})
    for field in ("artifact", "day", "lesson_id", "tags", "track"):
        if field not in course:
            failures.append(f"{relative}: course metadata lacks {field}")

    ids: set[str] = set()
    for index, cell in enumerate(notebook.cells, start=1):
        cell_id = cell.get("id")
        if not cell_id:
            failures.append(f"{relative}: cell {index} lacks an id")
        elif cell_id in ids:
            failures.append(f"{relative}: duplicate cell id {cell_id}")
        else:
            ids.add(cell_id)

        if cell.cell_type != "code":
            continue
        if cell.get("execution_count") is not None or cell.get("outputs"):
            failures.append(f"{relative}: code cell {index} contains saved execution state")
        source = _clean_python_source(str(cell.source))
        if not source.strip() or "skip-static-validation" in cell.metadata.get("tags", []):
            continue
        try:
            ast.parse(source, filename=f"{relative}:cell-{index}")
        except SyntaxError as exc:
            failures.append(
                f"{relative}: code cell {index} has invalid Python: {exc.msg} (line {exc.lineno})"
            )
    return failures


def validate_all(repo_root: Path) -> tuple[int, list[str]]:
    paths = list(notebook_paths(repo_root))
    failures = [failure for path in paths for failure in _validate_one(path, repo_root)]
    return len(paths), failures


def _day(path: Path) -> int | None:
    match = DAY_PATTERN.search(path.name)
    return int(match.group("day")) if match else None


def _smoke_candidates(repo_root: Path, days: set[int]) -> list[Path]:
    return [
        path
        for path in sorted((repo_root / COURSE_ROOT_RELATIVE / "notebooks").glob("*.ipynb"))
        if _day(path) in days
    ]


def smoke_execute(
    *,
    repo_root: Path,
    days: set[int],
    kernel_name: str,
    timeout: int,
) -> tuple[int, list[str]]:
    try:
        from nbclient.client import NotebookClient
    except ImportError as exc:
        return 0, [f"nbclient is required for --smoke: {exc}"]

    executed = 0
    failures: list[str] = []
    for path in _smoke_candidates(repo_root, days):
        relative = path.relative_to(repo_root).as_posix()
        notebook: NotebookNode = nbformat.read(  # type: ignore[no-untyped-call]
            path, as_version=4
        )
        tags = set(notebook.metadata.get("course", {}).get("tags", []))
        excluded = sorted(tags & SKIP_SMOKE_TAGS)
        if excluded:
            failures.append(f"{relative}: selected smoke notebook has excluded tags {excluded}")
            continue

        try:
            with tempfile.TemporaryDirectory(prefix="ds60-notebook-") as temp_dir:
                client = NotebookClient(
                    notebook,
                    timeout=timeout,
                    kernel_name=kernel_name,
                    resources={"metadata": {"path": temp_dir}},
                    allow_errors=False,
                )
                client.execute()
            executed += 1
        except Exception as exc:
            failures.append(f"{relative}: smoke execution failed: {type(exc).__name__}: {exc}")
    return executed, failures


def _parse_days(raw: str) -> set[int]:
    days = {int(value.strip()) for value in raw.split(",") if value.strip()}
    invalid = sorted(day for day in days if day < 1 or day > 60)
    if invalid:
        raise argparse.ArgumentTypeError(f"Days must be in 1..60; got {invalid}")
    return days


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--smoke-days",
        type=_parse_days,
        default=set(DEFAULT_SMOKE_DAYS),
        help="Comma-separated learner days (default: dependency-light offline subset).",
    )
    parser.add_argument("--kernel-name", default="ds60sqlpy")
    parser.add_argument("--timeout", type=int, default=90)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    checked, failures = validate_all(repo_root)
    print(f"Notebook structure and syntax checked: {checked}")

    if args.smoke:
        executed, smoke_failures = smoke_execute(
            repo_root=repo_root,
            days=args.smoke_days,
            kernel_name=args.kernel_name,
            timeout=args.timeout,
        )
        failures.extend(smoke_failures)
        print(f"Offline smoke notebooks executed: {executed}/{len(args.smoke_days)}")

    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
