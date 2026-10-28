"""Publish this data-engineering path from its maintained sources."""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def build() -> int:
    sys.path.insert(0, str(BASE.parents[1] / "courses/ml-engineering/authoring"))
    from publish import main

    return int(main(BASE))


if __name__ == "__main__":
    raise SystemExit(build())
