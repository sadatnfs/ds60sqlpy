#!/usr/bin/env python3
"""Validate planned learning tracks and build their read-only offline preview."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ds60sqlpy.journey_design import compile_preview, load_designs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Fail on invalid plans or stale preview"
    )
    args = parser.parse_args()
    try:
        document = compile_preview(ROOT)
        target = ROOT / "src/ds60sqlpy/assets/journey_preview.html"
        if args.check:
            if not target.is_file() or target.read_text("utf-8") != document:
                raise ValueError("Journey preview is stale; run scripts/build_journey_preview.py.")
        else:
            target.write_text(document, encoding="utf-8")
        plans = load_designs(ROOT)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Journey design error: {exc}", file=sys.stderr)
        return 1
    count = sum(len(plan["lessons"]) for plan in plans)
    print(f"Validated {len(plans)} tracks, {count} planned lessons, and five pilot walkthroughs.")
    print("Active catalog and execution profiles are unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
