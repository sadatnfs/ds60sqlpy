#!/usr/bin/env python3
"""Create a guided learner-local notebook for one cataloged SQL artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.catalog import Catalog  # noqa: E402
from ds60sqlpy.sql_notebook import (  # noqa: E402
    SqlNotebookError,
    generate_sql_notebook,
)


def parse_args() -> argparse.Namespace:
    """Parse the catalog-only notebook selection."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson_id", help="For example: sql-01 or sql-ops-01.")
    parser.add_argument(
        "--artifact",
        choices=("lesson", "solution"),
        default="lesson",
    )
    parser.add_argument("--solution-index", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    """Generate missing workspace files and print their paths."""

    args = parse_args()
    try:
        workspace = generate_sql_notebook(
            Catalog.load(REPO_ROOT),
            args.lesson_id,
            args.artifact,
            args.solution_index,
        )
    except SqlNotebookError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Guided notebook: {workspace.notebook_path}")
    print(f"Editable SQL:    {workspace.sql_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
