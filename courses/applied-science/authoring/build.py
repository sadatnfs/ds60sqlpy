#!/usr/bin/env python3
"""Publish complete tutorial sources; never execute lesson programs."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]


def outputs() -> dict[Path, str]:
    units = json.loads((BASE / "authoring/units.json").read_text("utf-8"))
    if len({u["id"] for u in units}) != len(units):
        raise ValueError("Duplicate tutorial identity")
    result: dict[Path, str] = {}
    rows = []
    lessons = []
    for unit in units:
        key = unit["id"]
        prose = (BASE / "authoring/chapters" / (key + ".md")).read_text("utf-8").strip()
        program = (BASE / "authoring/programs" / (key + unit["suffix"])).read_text("utf-8")
        if unit["language"] == "python":
            ast.parse(program, filename=key + ".py")
        if len(program.encode("utf-8")) > 48_000:
            raise ValueError(key + " exceeds the published source limit")
        if len(prose.split()) < 500 or prose.count("## Worked case") < 2:
            raise ValueError(key + " needs developed, distinct worked treatments")
        if "\u2014" in prose:
            raise ValueError("Use professional prose without em dashes")
        prefix = f"courses/{BASE.name}"
        guide = f"{prefix}/guides/{key}.md"
        source = f"{prefix}/examples/{key}{unit['suffix']}"
        setup = (
            "The prepared Stan pad compiles and samples `main.stan` with fixed bounded settings. "
            "Its tiny data are declared in `transformed data`; "
            "this pad has no separate JSON editor. "
            "The linked project explains standard data-block workflows."
            if unit["language"] == "stan"
            else "Run the complete program in the classroom's declared prepared profile. "
            "Every run starts a fresh process with tiny offline synthetic data. "
            "This is a worked tutorial, with no exam or hidden solution."
        )
        header = (
            f"# {key}: {unit['title']}\n\nTutorial mode. Stage: {unit['level']}. "
            "Direct prerequisites: " + ", ".join(f"`{x}`" for x in unit["prerequisites"]) + ".\n\n"
        )
        refs = "\n".join(f"- [{label}]({url})" for label, url in unit["sources"])
        text = (
            header
            + prose
            + "\n\n## Complete reproducible program\n\n"
            + setup
            + f" Runtime: `{unit['runtime']}`.\n\n```{unit['language']}\n"
            + program.rstrip()
            + "\n```\n\n## Primary references\n\n"
            + refs
            + "\n"
        )
        result[ROOT / guide] = text
        result[ROOT / source] = program
        rows.append(
            {
                k: unit[k]
                for k in (
                    "id",
                    "title",
                    "level",
                    "minutes",
                    "prerequisites",
                    "runtime",
                    "concepts",
                    "outcome",
                )
            }
            | {
                "lab": (
                    "Read the two complete worked cases, reproduce their evidence "
                    "and compare their assumptions."
                ),
                "verification": (
                    f"Complete source-bound {key} investigation with explicit numerical "
                    "or sampler diagnostics; no mastery grade."
                ),
            }
        )
        lessons.append(
            {
                "id": key,
                "status": "authored",
                "language": unit["language"],
                "runtime_profile": unit["runtime"],
                "guide_path": guide,
                "source_path": source,
                "solution_paths": [],
                "verification_id": None,
            }
        )
    config = json.loads((BASE / "authoring/course.json").read_text("utf-8"))
    result[BASE / "track.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": BASE.name,
                "title": config["title"],
                "summary": config["summary"],
                "learning_mode": "tutorial",
                "lessons": rows,
            },
            indent=2,
        )
        + "\n"
    )
    result[BASE / "lessons.json"] = (
        json.dumps({"schema_version": 1, "track_id": BASE.name, "lessons": lessons}, indent=2)
        + "\n"
    )
    index = "\n".join(
        f"| [{u['id']}](guides/{u['id']}.md) | {u['title']} | {u['runtime']} |" for u in units
    )
    result[BASE / "README.md"] = (
        f"# {config['title']}\n\n{config['summary']}\n\n"
        + config["introduction"]
        + "\n\nStart with the [classroom installation guide](../../README.md). "
        + (
            "These are complete worked tutorials. Sources and notes are saved; "
            "reading markers do not certify mastery.\n\n"
            "| Unit | Topic | Runtime |\n| --- | --- | --- |\n"
        )
        + index
        + "\n\nSee [authoring ownership](authoring/README.md) and [coverage](coverage.json).\n"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for path, text in outputs().items():
        if not path.exists() or path.read_text("utf-8") != text:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    if args.check and changed:
        print("Stale tutorial outputs: " + ", ".join(changed))
        return 1
    print(BASE.name + ": " + str(len(outputs())) + " maintained outputs verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
