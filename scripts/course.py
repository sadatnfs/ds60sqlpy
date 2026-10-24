#!/usr/bin/env python3
"""Run the DS60 CLI directly from a fresh clone."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
