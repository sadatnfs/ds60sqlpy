#!/usr/bin/env python3
"""Generate or verify the portable HTML lesson readers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.catalog import Catalog  # noqa: E402
from ds60sqlpy.lesson_reader import (  # noqa: E402
    build_reader_files,
    build_reference_files,
    reader_drift,
    reference_drift,
    write_reader_files,
    write_reference_files,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without changing generated files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="write/check another directory (useful for tests and previews)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Generate lesson pages or check that the tracked copies are current."""

    args = _parser().parse_args(argv)
    catalog = Catalog.load(REPO_ROOT)
    expected_lessons = build_reader_files(catalog)
    expected_references = build_reference_files(catalog)
    output_dir = args.output_dir.resolve() if args.output_dir else None
    lesson_output = output_dir / "lesson-pages" if output_dir else None
    reference_output = output_dir / "reference-pages" if output_dir else None
    if args.check:
        failures = reader_drift(
            expected_lessons,
            repo_root=REPO_ROOT,
            output_dir=lesson_output,
        )
        failures.extend(
            reference_drift(
                expected_references,
                repo_root=REPO_ROOT,
                output_dir=reference_output,
            )
        )
        if failures:
            print("Rendered lesson/reference drift detected:")
            for failure in failures:
                print(f"- {failure}")
            print("Run: python scripts/build_lesson_readers.py")
            return 1
        print(
            "Rendered pages are current "
            f"({len(expected_lessons)} lessons, {len(expected_references)} references)."
        )
        return 0

    write_reader_files(
        expected_lessons,
        repo_root=REPO_ROOT,
        output_dir=lesson_output,
    )
    write_reference_files(
        expected_references,
        repo_root=REPO_ROOT,
        output_dir=reference_output,
    )
    destination = output_dir or REPO_ROOT
    print(
        f"Wrote {len(expected_lessons)} lesson readers and "
        f"{len(expected_references)} rendered references below {destination}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
