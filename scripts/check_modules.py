#!/usr/bin/env python3
"""Validate authored module manifests and print a derived implementation inventory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ds60sqlpy.modules import ModuleCatalog  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print derived counts and authored IDs")
    args = parser.parse_args()
    try:
        catalog = ModuleCatalog(ROOT)
        tracks = [
            {
                "id": plan["id"],
                "planned": len(plan["lessons"]),
                "authored_ids": [
                    lesson.id
                    for lesson in catalog.lessons.values()
                    if lesson.track_id == plan["id"] and lesson.id in catalog.canonical_ids
                ],
            }
            for plan in catalog.plans
        ]
    except (OSError, ValueError, KeyError) as exc:
        print(f"Module validation failed: {exc}", file=sys.stderr)
        return 1
    report = {
        "schema_version": 1,
        "authored": len(catalog.canonical_ids.intersection(catalog.lessons)),
        "planned": len(catalog.canonical_ids),
        "tracks": tracks,
        "publication": "Authored modules and tutorial books; published legacy catalog remains separate.",
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Validated {report['authored']} authored lessons across {len(tracks)} subject tracks.")
        for track in tracks:
            print(f"{track['id']}: {len(track['authored_ids'])}/{track['planned']} authored")
        print(report["publication"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
