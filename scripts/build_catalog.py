#!/usr/bin/env python3
"""Regenerate the machine-readable course catalog."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.catalog_builder import write_catalog  # noqa: E402

if __name__ == "__main__":
    path = write_catalog(REPO_ROOT)
    print(path.relative_to(REPO_ROOT))
