#!/usr/bin/env python3
"""Validate, report and rebind authored walkthroughs (courses/<track>/walkthroughs.json).

--check            validate every track's walkthroughs; exit 1 on any error
--track TRACK      report one track's walkthroughs, stages and expected outputs
--track T --rebind refresh source_sha256 only when every excerpt still matches

Nothing here executes code. The CI reference corpus checks expected_output
against real runs (scripts/check_module_references.py).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ds60sqlpy.modules import ModuleCatalog  # noqa: E402
from ds60sqlpy.walkthroughs import index_path, validate_index  # noqa: E402


def load_catalog(root: Path) -> ModuleCatalog:
    return ModuleCatalog(root)


def tracks_with_walkthroughs(root: Path) -> list[str]:
    return sorted(path.parent.name for path in (root / "courses").glob("*/walkthroughs.json"))


def check(root: Path) -> int:
    catalog = load_catalog(root)
    total = 0
    failed = False
    tracks = tracks_with_walkthroughs(root)
    for track in tracks:
        clean, errors = validate_index(root, catalog, track)
        for error in errors:
            print(f"{track}: {error}")
        failed = failed or bool(errors)
        total += len(clean)
    if failed:
        print("Walkthrough validation failed.")
        return 1
    print(f"OK: {total} authored walkthroughs across {len(tracks)} tracks; nothing executed.")
    return 0


def report(root: Path, track: str) -> int:
    catalog = load_catalog(root)
    clean, errors = validate_index(root, catalog, track)
    for error in errors:
        print(f"ERROR {error}")
    stages: Counter[str] = Counter()
    for lesson_id, item in sorted(clean.items()):
        stage = str(catalog.planned.get(lesson_id, {}).get("level", "unknown"))
        stages[stage] += 1
        print(
            f"{lesson_id}  stage={stage}  steps={len(item['steps'])}  "
            f"expected_output={len(item['expected_output'])}"
        )
    known = sorted(
        {
            str(catalog.planned[key].get("level", "unknown"))
            for key, lesson in catalog.lessons.items()
            if lesson.track_id == track and key in catalog.planned
        }
    )
    missing = [stage for stage in known if not stages[stage]]
    print(
        f"{track}: {len(clean)} walkthroughs; stages covered "
        f"{sorted(stages)}; stages without one {missing}"
    )
    return 1 if errors else 0


def rebind(root: Path, track: str) -> int:
    catalog = load_catalog(root)
    clean, errors = validate_index(root, catalog, track, check_hash=False)
    if errors:
        for error in errors:
            print(error)
        print("Refusing to rebind: re-author the steps whose excerpts no longer match.")
        return 1
    path = root / index_path(track)
    text = path.read_text(encoding="utf-8")
    order = [item["lesson_id"] for item in json.loads(text)["walkthroughs"]]
    pattern = re.compile(r'("source_sha256"\s*:\s*")([0-9a-f]{64})"')
    if len(pattern.findall(text)) != len(order):
        print("Refusing to rebind: expected one source_sha256 per walkthrough.")
        return 1
    # Entries may share identical source bytes, so substitute by position, not by value.
    positions = iter(order)
    changed: list[str] = []

    def substitute(match: re.Match[str]) -> str:
        lesson_id = next(positions)
        new = str(clean[lesson_id]["current_sha256"])
        if match.group(2) != new:
            changed.append(lesson_id)
        return match.group(1) + new + '"'

    text = pattern.sub(substitute, text)
    if changed:
        path.write_text(text, encoding="utf-8")
    print(f"Rebound {len(changed)} walkthroughs: {', '.join(changed) or 'none needed'}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate every track")
    mode.add_argument("--track", help="report or rebind one track")
    parser.add_argument("--rebind", action="store_true", help="refresh hashes for --track")
    args = parser.parse_args(argv)
    if args.rebind and not args.track:
        parser.error("--rebind requires --track.")
    root = args.root.resolve()
    if args.check:
        return check(root)
    if args.rebind:
        return rebind(root, args.track)
    return report(root, args.track)


if __name__ == "__main__":
    raise SystemExit(main())
