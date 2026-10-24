#!/usr/bin/env python3
"""Synchronize complete statistics-book examples after source formatting.

Only manifest-declared statistics chapter/example pairs participate. A unique
Python fence must independently match the example AST before its layout changes.
This never scans or updates frozen fences in another subject.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.source_format_parity import semantic_sha256  # noqa: E402

BOOK = Path("courses/statistics-ml")
OPENING = re.compile(r"(?m)^(?P<marker>`{3,}|~{3,})[ \t]*(?P<language>[^\r\n]*)\r?\n")


class Fence(NamedTuple):
    start: int
    end: int
    source: str


def python_fences(document: str) -> list[Fence]:
    """Read complete top-level fences, leaving nested examples and fragments alone."""
    result: list[Fence] = []
    cursor = 0
    while opening := OPENING.search(document, cursor):
        marker = opening["marker"]
        closing = re.compile(
            rf"(?m)^{re.escape(marker[0])}{{{len(marker)},}}[ \t]*(?:\r?\n|$)"
        ).search(document, opening.end())
        if closing is None:
            break
        if opening["language"].strip() in {"python", "py"}:
            result.append(
                Fence(opening.end(), closing.start(), document[opening.end() : closing.start()])
            )
        cursor = closing.end()
    return result


def owned_path(root: Path, relative: str, directory: str, suffix: str) -> Path:
    name = Path(relative)
    expected = BOOK / directory
    if (
        name.is_absolute()
        or ".." in name.parts
        or not name.is_relative_to(expected)
        or name.suffix != suffix
    ):
        raise ValueError(
            f"Example synchronization path is outside its owned source directory: {relative}"
        )
    for index in range(1, len(name.parts) + 1):
        if (root / Path(*name.parts[:index])).is_symlink():
            raise ValueError(f"Example synchronization cannot follow symlinks: {relative}")
    path = root / name
    if not path.is_file():
        raise ValueError(f"Example synchronization source is missing: {relative}")
    return path


def planned_changes(root: Path) -> dict[Path, str]:
    manifest = owned_path(root, str(BOOK / "manifest.json"), "", ".json")
    chapters = json.loads(manifest.read_text(encoding="utf-8"))["chapters"]
    changes: dict[Path, str] = {}
    seen_chapters: set[Path] = set()
    for chapter in chapters:
        path = owned_path(root, chapter["chapter_path"], "chapters", ".md")
        if path in seen_chapters:
            raise ValueError(f"Duplicate example chapter: {chapter['chapter_path']}")
        seen_chapters.add(path)
        document = path.read_text(encoding="utf-8")
        candidates: list[tuple[Fence, str]] = []
        for fence in python_fences(document):
            try:
                candidates.append((fence, semantic_sha256(fence.source.encode("utf-8"))))
            except (SyntaxError, ValueError):
                # An intentional error, partial program or unrelated fragment is
                # not a complete example eligible for automatic synchronization.
                continue
        replacements: dict[tuple[int, int], str] = {}
        for relative in chapter["example_paths"]:
            example = owned_path(root, relative, "examples", ".py")
            program = example.read_text(encoding="utf-8")
            digest = semantic_sha256(program.encode("utf-8"))
            matching = [fence for fence, value in candidates if value == digest]
            if len(matching) != 1:
                raise ValueError(
                    f"Expected one AST-equivalent complete fence for {relative} in "
                    f"{chapter['chapter_path']}; found {len(matching)}. "
                    "Review the source and chapter together; no files were written."
                )
            fence = matching[0]
            key = (fence.start, fence.end)
            if key in replacements:
                raise ValueError(f"Multiple examples own the same chapter fence: {relative}")
            replacements[key] = program.rstrip("\n") + "\n"
        updated = document
        for (start, end), replacement in sorted(replacements.items(), reverse=True):
            updated = updated[:start] + replacement + updated[end:]
        if updated != document:
            changes[path] = updated
    return changes


def synchronize(root: Path, *, check: bool) -> list[str]:
    # Validate all pairs first. A mismatching later chapter must not permit
    # earlier chapters to be silently rewritten during an unsuccessful run.
    changes = planned_changes(root)
    if not check:
        for path, document in changes.items():
            path.write_text(document, encoding="utf-8", newline="\n")
    return [str(path.relative_to(root)) for path in changes]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="report drift without writing chapters"
    )
    args = parser.parse_args(argv)
    try:
        changes = synchronize(ROOT, check=args.check)
    except (OSError, ValueError, KeyError, SyntaxError) as exc:
        print(f"Example synchronization failed: {exc}", file=sys.stderr)
        return 2
    for path in changes:
        print(
            f"{'Needs example synchronization' if args.check else 'Synchronized examples'}: {path}"
        )
    if args.check and changes:
        return 1
    print(f"Statistics complete-example fences are current ({len(changes)} changed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
