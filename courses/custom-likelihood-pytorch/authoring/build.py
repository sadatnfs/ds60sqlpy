#!/usr/bin/env python3
"""Publish complete tutorial sources; never execute lesson programs."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
FENCE_FLAGS = re.compile(
    r"(?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+)"
    r"(?: (?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+))*"
)


def key_terms(unit: dict) -> str:
    terms = unit["key_terms"]
    if not 3 <= len(terms) <= 5 or any(
        not term or not text or set(term) & set(":*") or set(term + text) & set("\u2013\u2014")
        for term, text in terms.items()
    ):
        raise ValueError(unit["id"] + " needs three to five plain key terms")
    return "## Key terms\n\n" + "\n".join(f"- **{t}:** {d}" for t, d in terms.items())


def worked_examples(unit: dict, prose: str, seen: set[str]) -> str:
    examples = unit["worked_examples"]
    fields = ("title", "language", "code", "interpretation")
    for item in examples:
        values = [item.get(name, "") for name in fields] + [item.get("output", "")]
        if not all(isinstance(v, str) for v in values) or not all(v.strip() for v in values[:4]):
            raise ValueError(unit["id"] + " worked examples need title, language, code and reading")
        if any(set(v) & set("\u2013\u2014") for v in values):
            raise ValueError(unit["id"] + " worked examples must not use em or en dashes")
        fence = item.get("fence", "")
        if fence and not (isinstance(fence, str) and FENCE_FLAGS.fullmatch(fence)):
            raise ValueError(unit["id"] + " has an unsupported worked example fence")
        for v in (item["title"], item["code"], item["interpretation"]):
            if v.casefold() in seen:
                raise ValueError(unit["id"] + " repeats worked example content")
            seen.add(v.casefold())
    if not examples or len(examples) + prose.count("## Worked case") < 2:
        raise ValueError(unit["id"] + " needs at least two worked treatments")
    parts = []
    for item in examples:
        info = item["language"] + (" " + item["fence"] if item.get("fence") else "")
        block = f"## Worked example: {item['title']}\n\n```{info}\n"
        block += item["code"].rstrip() + "\n```\n\n"
        if item.get("output", "").strip():
            block += "Observed output:\n\n```text\n" + item["output"].rstrip() + "\n```\n\n"
        parts.append(block + item["interpretation"].strip())
    return "\n\n".join(parts)


def outputs() -> dict[Path, str]:
    units = json.loads((BASE / "authoring/units.json").read_text("utf-8"))
    if [u["id"] for u in units] != [f"clp-{i:03}" for i in range(1, 21)]:
        raise ValueError("Publish the complete ordered twenty-chapter tutorial")
    if len({u["id"] for u in units}) != len(units):
        raise ValueError("Duplicate tutorial identity")
    result: dict[Path, str] = {}
    rows = []
    lessons = []
    seen: set[str] = set()
    for unit in units:
        key = unit["id"]
        prose = (BASE / "authoring/chapters" / (key + ".md")).read_text("utf-8").strip()
        program = (BASE / "authoring/programs" / (key + unit["suffix"])).read_text("utf-8")
        if unit["language"] == "python":
            ast.parse(program, filename=key + ".py")
        if len(program.encode("utf-8")) > 48_000:
            raise ValueError(key + " exceeds the published source limit")
        if len(prose.split()) < 600 or prose.count("## Worked case") < 2:
            raise ValueError(key + " needs developed, distinct worked treatments")
        prose = prose.replace("\n## Worked case", "\n" + key_terms(unit) + "\n\n## Worked case", 1)
        if "\u2014" in prose:
            raise ValueError("Use professional prose without em dashes")
        prefix = f"courses/{BASE.name}"
        guide = f"{prefix}/guides/{key}.md"
        source = f"{prefix}/examples/{key}{unit['suffix']}"
        setup = (
            "Run this complete source in the separately prepared `llm-torch-cpu` pad. "
            "It uses float64 CPU tensors and tiny original offline fixtures. "
            "Each execution starts fresh. Save edited source and notes with classroom controls. "
            "There is no exam or hidden solution, and execution is not scientific model acceptance."
        )
        header = (
            f"# {key}: {unit['title']}\n\nTutorial mode. Stage: {unit['level']}. "
            "Direct prerequisites: " + ", ".join(f"`{x}`" for x in unit["prerequisites"]) + ".\n\n"
        )
        refs = "\n".join(f"- [{label}]({url})" for label, url in unit["sources"])
        text = (
            header
            + prose
            + "\n\n"
            + worked_examples(unit, prose, seen)
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
            | {"lab": unit["lab"], "verification": unit["verification"]}
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
    generated = outputs()
    for path, text in generated.items():
        if not path.exists() or path.read_text("utf-8") != text:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    if args.check and changed:
        print("Stale tutorial outputs: " + ", ".join(changed))
        return 1
    print(BASE.name + ": " + str(len(generated)) + " maintained outputs verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
