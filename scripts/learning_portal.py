#!/usr/bin/env python3
"""Open the private DS60 learning portal from a fresh clone."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.catalog import Catalog  # noqa: E402
from ds60sqlpy.portal import serve_portal  # noqa: E402


def main() -> None:
    """Parse learner-safe options and run the portal."""

    parser = argparse.ArgumentParser(
        description=(
            "Serve START_HERE.html privately on 127.0.0.1, persist progress, "
            "and optionally launch allowlisted VS Code/Jupyter targets."
        )
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Loopback port; 0 chooses a free port (recommended).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL without opening the default browser.",
    )
    parser.add_argument(
        "--no-launches",
        action="store_true",
        help="Disable every native VS Code/Jupyter launch action.",
    )
    args = parser.parse_args()
    serve_portal(
        Catalog.load(REPO_ROOT),
        port=args.port,
        open_browser=not args.no_browser,
        allow_launches=not args.no_launches,
    )


if __name__ == "__main__":
    main()
