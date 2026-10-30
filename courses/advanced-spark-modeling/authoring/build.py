#!/usr/bin/env python3
"""Publish complete tutorial sources; never execute lesson programs."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))
from scripts.normalize_math_prose import prose_parts  # noqa: E402


def published_package_links(text: str) -> str:
    """Relocate only prose links from authored sources to published guides."""
    return "".join(
        part.replace("](../../../../packages/", "](../../../packages/")
        if protected and part.startswith(("[", "!["))
        else part
        for protected, part in prose_parts(text)
    )


def outputs() -> dict[Path, str]:
    units = json.loads((BASE / "authoring/units.json").read_text("utf-8"))
    if [u["id"] for u in units] != [f"asm-{i:03}" for i in range(1, 39)]:
        raise ValueError("Keep all 38 stable tutorial identities in order")
    if len({u["id"] for u in units}) != len(units):
        raise ValueError("Duplicate tutorial identity")
    result: dict[Path, str] = {}
    rows = []
    lessons = []
    for unit in units:
        key = unit["id"]
        prose = (BASE / "authoring/chapters" / (key + ".md")).read_text("utf-8").strip()
        program = (BASE / "authoring/programs" / (key + unit["suffix"])).read_text("utf-8")
        prose = published_package_links(prose)
        if unit["runtime"] == "reading" and unit["language"] == "markdown":
            program = published_package_links(program)
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
        reading = unit["runtime"] == "reading"
        setup = (
            "This is a complete reading/project reference. It has no ordinary pad Run action. "
            "Prepare and execute any linked project through its own documented entrypoint. "
            "A command reference or hand calculation is not an execution receipt."
            if reading
            else "Run this complete source in its declared prepared Spark profile. "
            "The fixture is tiny, deterministic and offline. Scala sources are compiled "
            "before execution; Python sources use the prepared PySpark environment. "
            "These are worked tutorials with no hidden solutions or exams."
        )
        header = (
            f"# {key}: {unit['title']}\n\nTutorial mode. Stage: {unit['level']}. "
            "Direct prerequisites: " + ", ".join(f"`{x}`" for x in unit["prerequisites"]) + ".\n\n"
        )
        refs = "\n".join(f"- [{label}]({url})" for label, url in unit["sources"])
        example = (
            program.rstrip() if reading else f"```{unit['language']}\n" + program.rstrip() + "\n```"
        )
        text = (
            header
            + prose
            + (
                "\n\n## Worked project reference\n\n"
                if reading
                else "\n\n## Complete reproducible program\n\n"
            )
            + setup
            + f" Runtime: `{unit['runtime']}`.\n\n"
            + example
            + "\n\n## Primary references\n\n"
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
                    "or execution diagnostics; no mastery grade."
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
        + "\n\nSee [authoring ownership](authoring/README.md), [coverage](coverage.json), "
        + "and [qualification boundaries](QUALIFICATION.md).\n"
    )
    result[BASE / "coverage.json"] = (BASE / "authoring/coverage.json").read_text("utf-8")
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
