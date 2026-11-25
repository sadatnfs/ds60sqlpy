#!/usr/bin/env python3
"""Publish complete tutorial sources; never execute lesson programs."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import textwrap
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


INCLUDE = re.compile(
    r"^<!-- include: (?P<path>[\w./-]+)(?: #(?P<symbol>\w+))?"
    r"""(?: from=(?P<q1>["'])(?P<start>.+?)(?P=q1))?"""
    r"""(?: to=(?P<q2>["'])(?P<end>.+?)(?P=q2))?"""
    r"""(?: until=(?P<q3>["'])(?P<until>.+?)(?P=q3))? (?P<language>[\w+-]+)"""
    r"(?P<flags>(?: [\w=./-]+)*) -->$",
    re.M,
)
CASE = re.compile(r"^## Worked case(?: (\w+))?: (.+)$", re.M)


def excerpt(match: re.Match[str]) -> str:
    """Embed exact project source named by an include marker in a chapter."""
    relative = match["path"]
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE / "projects") or not path.is_file():
        raise ValueError(f"Include target {relative} is not a project file")
    text = path.read_text("utf-8")
    lines = text.splitlines()
    if match["symbol"]:
        node = next(
            n
            for n in ast.parse(text).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == match["symbol"]
        )
        first = min([d.lineno for d in node.decorator_list] + [node.lineno])
        lines = lines[first - 1 : node.end_lineno]
    if match["start"]:
        lines = lines[next(i for i, line in enumerate(lines) if match["start"] in line) :]
    if match["end"]:
        lines = lines[: next(i for i, line in enumerate(lines) if match["end"] in line) + 1]
    if match["until"]:
        lines = lines[: next(i for i, line in enumerate(lines) if match["until"] in line)]
    body = textwrap.dedent("\n".join(lines)).strip("\n")
    if "```" in body or not body:
        raise ValueError(f"Include {relative} cannot be fenced")
    if match["flags"] and not FENCE_FLAGS.fullmatch(match["flags"].strip()):
        raise ValueError(f"Include {relative} has unsupported fence flags")
    info = match["language"] + match["flags"]
    return f"From [`{relative}`](../{relative}):\n\n```{info}\n{body}\n```"


def lab(prose: str, reading: bool) -> str:
    cases = [title.strip() for _, title in CASE.findall(prose)]
    named = " and ".join(f'"{title}"' for title in cases)
    if reading:
        return (
            f"Read the worked cases {named}, run the linked project only through its own "
            "documented entrypoint, and compare its recorded observations with the chapter."
        )
    return (
        f"Run the complete program and check the worked cases {named} against the values "
        "and diagnostics the chapter states."
    )


def key_terms_block(unit: dict) -> str:
    """Render the unit's authored vocabulary as a Key terms section."""
    terms = unit.get("key_terms", [])
    names = [term for term, _ in terms]
    if not 3 <= len(terms) <= 5 or len(set(names)) != len(names):
        raise ValueError(unit["id"] + " needs three to five distinct key terms")
    for term, definition in terms:
        if not term.strip() or not definition.strip():
            raise ValueError(unit["id"] + " has an empty key term")
        if any(dash in term + definition for dash in ("\u2014", "\u2013")):
            raise ValueError(unit["id"] + " key terms must not use em or en dashes")
    return "## Key terms\n\n" + "\n".join(f"- **{t}:** {d}" for t, d in terms)


def with_key_terms(prose: str, block: str) -> str:
    """Place Key terms after the opening section, before the mechanism."""
    headings = [m.start() for m in re.finditer(r"^## ", prose, re.M)]
    if len(headings) < 2:
        raise ValueError("Chapter needs an opening section before its mechanism")
    second = headings[1]
    return prose[:second].rstrip() + "\n\n" + block + "\n\n" + prose[second:]


EXAMPLE_LANGUAGES = {"python", "scala", "sql", "bash", "yaml", "text"}
EXAMPLE_FIELDS = {"title", "language", "code", "output", "interpretation", "fence"}
OPTIONAL_FIELDS = {"output", "fence"}
FENCE_FLAGS = re.compile(
    r"(?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+)"
    r"(?: (?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+))*"
)
FENCE = re.compile(r"^```", re.M)


def worked_examples_block(unit: dict, titles: set[str], codes: set[str]) -> str:
    """Validate and render the unit's authored worked examples as guide sections.

    ``output`` is optional and must be text observed by running the block itself.
    """
    key = unit["id"]
    examples = unit.get("worked_examples", [])
    if not examples:
        raise ValueError(key + " needs at least one worked example")
    sections = []
    for example in examples:
        if set(example) - EXAMPLE_FIELDS or not set(example) >= EXAMPLE_FIELDS - OPTIONAL_FIELDS:
            raise ValueError(key + " worked examples need exactly the documented fields")
        title, code = example["title"].strip(), example["code"].strip("\n")
        language, note = example["language"], example["interpretation"].strip()
        output = example.get("output", "").strip("\n")
        fence = example.get("fence", "")
        if fence and not FENCE_FLAGS.fullmatch(fence):
            raise ValueError(key + " has an unsupported worked example fence: " + fence)
        info = language + (" " + fence if fence else "")
        if not title or not code.strip() or language not in EXAMPLE_LANGUAGES:
            raise ValueError(key + " has an empty or unsupported worked example")
        if title.lower() in titles or code in codes:
            raise ValueError(key + " repeats a worked example title or program: " + title)
        titles.add(title.lower())
        codes.add(code)
        if any(d in "".join(example.values()) for d in ("\u2014", "\u2013")):
            raise ValueError(key + " worked examples must not use em or en dashes")
        if "```" in code + output:
            raise ValueError(key + " worked example text cannot contain a fence")
        if "\n" in note or len(note.split()) < 40 or not note.endswith("."):
            raise ValueError(key + " interpretation must be one paragraph of 40+ words")
        if language == "python":
            ast.parse(code, filename=key + " worked example")
        observed = f"Output from running the block above:\n\n```text\n{output}\n```\n\n"
        sections.append(
            f"## Worked example: {title}\n\n```{info}\n{code}\n```\n\n"
            + (observed if output else "")
            + note
        )
    return "\n\n".join(sections)


def with_worked_examples(prose: str, block: str) -> str:
    """Place worked examples after the worked cases, before failure diagnosis."""
    marker = "\n## Failure diagnosis"
    if prose.count(marker) != 1:
        raise ValueError("Chapter needs one Failure diagnosis section")
    head, tail = prose.split(marker)
    return head.rstrip() + "\n\n" + block + "\n" + marker + tail


def outputs() -> dict[Path, str]:
    units = json.loads((BASE / "authoring/units.json").read_text("utf-8"))
    titles: set[str] = set()
    codes: set[str] = set()
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
        prose = INCLUDE.sub(excerpt, prose)
        if "<!-- include:" in prose:
            raise ValueError(key + " has a malformed include marker")
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
        prose = with_key_terms(prose, key_terms_block(unit))
        prose = with_worked_examples(prose, worked_examples_block(unit, titles, codes))
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
        if len(FENCE.findall(text)) < 4 or len(text.split()) < 1050:
            raise ValueError(key + " guide needs two fenced examples and 1050 words")
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
                "lab": lab(prose, reading),
                "verification": (
                    "Compare the project's recorded observations with the values and failure "
                    "cases each worked case states; a command reference or hand calculation "
                    "does not show that the project ran."
                    if reading
                    else f"Run `{key}{unit['suffix']}` on the `{unit['runtime']}` profile and "
                    "confirm the printed values and diagnostics that both worked cases state."
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
