#!/usr/bin/env python3
"""Publish complete tutorial sources; never execute lesson programs."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    data: dict[str, object] = {}
    for name, value in pairs:
        if name in data:
            raise ValueError("Duplicate JSON key in units.json: " + name)
        data[name] = value
    return data


def key_terms_section(unit: dict) -> str:
    """Render the lesson's 3 to 5 authored key terms as a guide section."""
    key = unit["id"]
    terms = unit.get("key_terms")
    if not isinstance(terms, dict) or not 3 <= len(terms) <= 5:
        raise ValueError(key + " needs 3 to 5 lesson-specific key_terms")
    folded = [name.casefold() for name in terms]
    if len(set(folded)) != len(folded):
        raise ValueError(key + " repeats a key term")
    for name, definition in terms.items():
        if not isinstance(definition, str) or not name.strip() or not definition.strip():
            raise ValueError(key + " needs a nonempty term and definition")
        if name != name.strip() or definition != definition.strip() or ":" in name:
            raise ValueError(key + " key term " + repr(name) + " is not a clean label")
        if not definition.endswith("."):
            raise ValueError(key + " key term " + repr(name) + " needs a complete sentence")
        if "\u2014" in name + definition or "\u2013" in name + definition:
            raise ValueError("Use professional prose without em or en dashes")
    items = "\n".join(f"- **{name}:** {definition}" for name, definition in terms.items())
    return "## Key terms\n\n" + items


def with_key_terms(key: str, prose: str, section: str) -> str:
    """Place the key terms after the opening section, before the mechanism."""
    lines = prose.split("\n")
    fenced = False
    headings = []
    for index, line in enumerate(lines):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            headings.append(index)
    if len(headings) < 2:
        raise ValueError(key + " needs an opening section before its mechanism")
    split = headings[1]
    before = "\n".join(lines[:split]).rstrip()
    return before + "\n\n" + section + "\n\n" + "\n".join(lines[split:])


def worked_examples_section(unit: dict, seen_code: dict[str, str]) -> str:
    """Render the lesson's focused worked examples with their interpretation."""
    key = unit["id"]
    examples = unit.get("worked_examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError(key + " needs at least one worked example")
    titles = set()
    blocks = []
    for example in examples:
        if not isinstance(example, dict) or set(example) - {
            "title",
            "code",
            "output",
            "interpretation",
        }:
            raise ValueError(key + " has a malformed worked example")
        title = example.get("title", "")
        code = example.get("code", [])
        output = example.get("output", [])
        interpretation = example.get("interpretation", "")
        if not isinstance(title, str) or not title.strip() or title != title.strip():
            raise ValueError(key + " needs a clean worked example title")
        if title.casefold() in titles:
            raise ValueError(key + " repeats worked example title " + repr(title))
        titles.add(title.casefold())
        if not isinstance(code, list) or not code or not all(isinstance(x, str) for x in code):
            raise ValueError(key + " worked example " + repr(title) + " needs code lines")
        if not isinstance(output, list) or not all(isinstance(x, str) for x in output):
            raise ValueError(key + " worked example " + repr(title) + " has malformed output")
        if not isinstance(interpretation, str) or len(interpretation.split()) < 40:
            raise ValueError(key + " worked example " + repr(title) + " needs an interpretation")
        source = "\n".join(code)
        ast.parse(source, filename=key + " worked example")
        if source in seen_code:
            raise ValueError(key + " repeats the worked example code of " + seen_code[source])
        seen_code[source] = key
        text = "\n".join([title, source, *output, interpretation])
        if "\u2014" in text or "\u2013" in text or "```" in text:
            raise ValueError(key + " worked example " + repr(title) + " has a dash or fence")
        block = f"## Worked example: {title}\n\n```python\n{source}\n```\n\n"
        if output:
            block += "Expected output:\n\n```text\n" + "\n".join(output) + "\n```\n\n"
        blocks.append(block + interpretation.strip())
    return "\n\n".join(blocks)


def with_worked_examples(key: str, prose: str, section: str) -> str:
    """Place worked examples after the last worked case section."""
    lines = prose.split("\n")
    fenced = False
    headings = []
    for index, line in enumerate(lines):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            headings.append(index)
    cases = [i for i in headings if lines[i].startswith("## Worked case")]
    if not cases:
        raise ValueError(key + " needs a worked case before its worked examples")
    later = [i for i in headings if i > cases[-1]]
    if not later:
        return prose.rstrip() + "\n\n" + section
    split = later[0]
    before = "\n".join(lines[:split]).rstrip()
    return before + "\n\n" + section + "\n\n" + "\n".join(lines[split:])


def outputs() -> dict[Path, str]:
    units = json.loads(
        (BASE / "authoring/units.json").read_text("utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
    )
    if [u["id"] for u in units] != [f"pyweb-{i:03}" for i in range(1, 73)]:
        raise ValueError("Keep all 72 stable tutorial identities in order")
    if len({u["id"] for u in units}) != len(units):
        raise ValueError("Duplicate tutorial identity")
    result: dict[Path, str] = {}
    rows = []
    lessons = []
    term_sets: dict[frozenset[str], str] = {}
    seen_code: dict[str, str] = {}
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
        section = key_terms_section(unit)
        term_set = frozenset(name.casefold() for name in unit["key_terms"])
        if term_set in term_sets:
            raise ValueError(key + " repeats the key terms of " + term_sets[term_set])
        term_sets[term_set] = key
        prose = with_key_terms(key, prose, section)
        prose = with_worked_examples(key, prose, worked_examples_section(unit, seen_code))
        prefix = f"courses/{BASE.name}"
        guide = f"{prefix}/guides/{key}.md"
        source = f"{prefix}/examples/{key}{unit['suffix']}"
        reading = unit["runtime"] == "reading"
        if reading:
            # Authored references live two directories below this course;
            # generated guides/examples live one directory below it.
            program = program.replace("](../../projects/", "](../projects/")
        setup = (
            "This is a complete reading/project reference. It has no ordinary pad Run action. "
            "Prepare and execute any linked project through its own documented entrypoint. "
            "A command reference or hand calculation is not an execution receipt."
            if reading
            else "Run this complete finite program in the prepared Python web profile. "
            "It exercises real framework clients and bounded local fixtures, then exits. "
            "It does not open a browser or start an externally reachable HTTP server. "
            "Long-running applications use the separately documented owned projects."
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
                "lab": unit.get(
                    "lab",
                    (
                        "Follow the linked project's documented entrypoint and compare its "
                        "recorded evidence with the two worked cases."
                    )
                    if reading
                    else (
                        "Run the complete program, then change one input in each worked "
                        "case and predict the new result before rerunning."
                    ),
                ),
                "verification": unit.get(
                    "verification",
                    (
                        f"The project checks named in {key} pass under their documented "
                        "lifecycle; reading the unit records no pad run or mastery grade."
                    )
                    if reading
                    else (
                        f"Every assertion in the {key} program passes and its printed JSON "
                        "matches the worked cases; a passing run is not a mastery grade."
                    ),
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
    result[BASE / ("track.json" if config.get("admitted") is True else "track.draft.json")] = (
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
    result[BASE / ("lessons.json" if config.get("admitted") is True else "lessons.draft.json")] = (
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
        + "and [runtime research](RESEARCH.md).\n"
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
