#!/usr/bin/env python3
"""Launch the optional local DS60 tutor MCP adapter from a source checkout."""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.mcp_server import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
