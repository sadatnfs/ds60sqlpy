#!/usr/bin/env python3
"""Build this subject's guides and sources, with explicit complete-route admission."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]


def outputs(*, admit: bool = False) -> dict[Path, str]:
    plan = json.loads((BASE / "authoring/chapter-map.json").read_text("utf-8"))["units"]
    if [unit["id"] for unit in plan] != [f"apache-{n:03d}" for n in range(1, 89)]:
        raise ValueError("The complete stable apache-001..088 design is required")
    result: dict[Path, str] = {}
    rows: list[dict[str, Any]] = []
    lessons: list[dict[str, Any]] = []
    authored: list[str] = []
    for unit in plan:
        key = unit["id"]
        metadata = BASE / "authoring/units" / (key + ".json")
        if not metadata.exists():
            if admit:
                raise ValueError(f"{key} is not complete; do not admit a partial route")
            continue
        meta = json.loads(metadata.read_text("utf-8"))
        prose = (BASE / "authoring/chapters" / (key + ".md")).read_text("utf-8").strip()
        suffix = ".py" if meta["language"] == "python" else ".md"
        program = (BASE / "authoring/programs" / (key + suffix)).read_text("utf-8")
        if len(prose.split()) < 500 or prose.count("## Worked case") != 2:
            raise ValueError(f"{key} requires developed prose and two worked cases")
        if "\u2014" in prose + program or len(program.encode("utf-8")) > 48_000:
            raise ValueError(f"{key} violates the text/source boundary")
        if meta["language"] == "python":
            ast.parse(program, filename=key + ".py")
        elif meta["language"] != "markdown" or meta["runtime"] != "reading":
            raise ValueError(f"{key} has an unsupported authoring surface")
        if len(meta["sources"]) < 2:
            raise ValueError(f"{key} needs relevant primary sources")
        # Sources live under authoring/chapters; generated guides are one level
        # shallower. Only this explicit course-project link prefix is relocated.
        prose = prose.replace("](../../projects/", "](../projects/")
        guide_path = f"courses/{BASE.name}/guides/{key}.md"
        source_path = f"courses/{BASE.name}/examples/{key}{suffix}"
        boundary = (
            "This is a complete editable worked program for the declared prepared runtime. "
            "It uses bounded local fixtures and does not install packages "
            "or start distributed services."
            if meta["language"] == "python"
            else "This is a project-only command notebook. Read and edit it in the classroom; "
            "run its explicitly labeled commands from the copied owned Docker workshop. "
            "The classroom does not execute these service commands."
        )
        refs = "\n".join(f"- [{label}]({url})" for label, url in meta["sources"])
        complete = f"```python\n{program.rstrip()}\n```" if suffix == ".py" else program.rstrip()
        result[ROOT / guide_path] = (
            f"# {key}: {unit['title']}\n\nTutorial mode. Stage: {meta['level']}. "
            + "Direct prerequisites: "
            + ", ".join(f"`{p}`" for p in meta["prerequisites"])
            + f".\n\n{prose}\n\n## Complete worked source\n\n{boundary}\n\n"
            + complete
            + "\n\n## Primary references\n\n"
            + refs
            + "\n"
        )
        result[ROOT / source_path] = program
        authored.append(key)
        rows.append(
            {
                "id": key,
                "title": unit["title"],
                "level": meta["level"],
                "minutes": meta["minutes"],
                "prerequisites": meta["prerequisites"],
                "runtime": meta["runtime"],
                "concepts": meta["concepts"],
                "outcome": unit["outcome"],
                "lab": (
                    "Compare the two complete worked cases and reproduce the stated observations."
                ),
                "verification": meta["evidence"],
            }
        )
        lessons.append(
            {
                "id": key,
                "status": "authored",
                "language": meta["language"],
                "runtime_profile": meta["runtime"],
                "guide_path": guide_path,
                "source_path": source_path,
                "solution_paths": [],
                "verification_id": None,
            }
        )
    if admit:
        result[BASE / "track.json"] = (
            json.dumps(
                {
                    "schema_version": 1,
                    "id": BASE.name,
                    "title": "Apache and open data platforms",
                    "summary": (
                        "Mechanisms and worked projects for columnar data, query engines, "
                        "orchestration, streaming, catalogs, analytical serving and open sharing."
                    ),
                    "learning_mode": "tutorial",
                    "lessons": rows,
                },
                indent=2,
            )
            + "\n"
        )
        result[BASE / "lessons.json"] = (
            json.dumps(
                {
                    "schema_version": 1,
                    "track_id": BASE.name,
                    "lessons": lessons,
                },
                indent=2,
            )
            + "\n"
        )
    result[BASE / "authoring/coverage.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "planned_units": len(plan),
                "authored_units": authored,
                "admitted": admit,
                "pending": [unit["id"] for unit in plan if unit["id"] not in authored],
            },
            indent=2,
        )
        + "\n"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--admit", action="store_true", help="Require and register all 88 completed units"
    )
    args = parser.parse_args()
    existing_admission = (BASE / "track.json").is_file() and (BASE / "lessons.json").is_file()
    generated = outputs(admit=args.admit or existing_admission)
    mismatches = []
    for path, value in generated.items():
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != value:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
    if mismatches:
        print("Generated subject drift:\n" + "\n".join(mismatches))
        return 1
    print(f"{len(generated)} subject outputs " + ("match" if args.check else "written"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
