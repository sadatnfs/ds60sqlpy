#!/usr/bin/env python3
"""Build this subject's guides and sources, with explicit complete-route admission."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import Formatter, format_document, invoke  # noqa: E402

INCLUDE = re.compile(
    r"^<!-- include: (?P<path>[\w./-]+)(?: #(?P<symbol>\w+))?"
    r"""(?: from=(?P<q1>["'])(?P<start>.+?)(?P=q1))?"""
    r"""(?: to=(?P<q2>["'])(?P<end>.+?)(?P=q2))?"""
    r"""(?: until=(?P<q3>["'])(?P<until>.+?)(?P=q3))? (?P<language>[\w+-]+)"""
    r"(?P<flags>(?: [\w=./-]+)*) -->$",
    re.M,
)
CASE = re.compile(r"^## Worked case(?: (\w+))?: (.+)$", re.M)


def ruff_adapter(source: bytes, language: str, suffix: str, root: Path) -> bytes:
    """Run the locked Ruff with the configuration the fence formatting check uses."""
    config = str(root / "pyproject.toml")
    command = ["format", "--no-cache", "--config", config, "--stdin-filename", "snippet" + suffix]
    return invoke([sys.executable, "-m", "ruff", *command, "-"], source, root)


FORMATTER = Formatter(ROOT, adapter=ruff_adapter)


def statement_lines(tree: ast.AST) -> tuple[set[int], set[int]]:
    """First and last lines of every statement; decorators start their definition."""
    starts: set[int] = set()
    ends: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
            decorators = getattr(node, "decorator_list", [])
            starts.add(min([item.lineno for item in decorators] + [node.lineno]))
            ends.add(node.end_lineno or node.lineno)
    return starts, ends


def python_excerpt(relative: str, text: str, first: int, last: int, body: str) -> str:
    """Print a Python excerpt exactly as the repository's fence formatting check does.

    Dedenting can change where Ruff wraps a line, and lines such as list elements
    parse by accident as one-item tuples. An excerpt the check admits as a program
    must therefore begin and end on whole statements of the cited file.
    """
    document = f"```python\n{body}\n```\n"
    document, records = format_document(document, FORMATTER, {"python"}, path=relative)
    record = records[-1]
    if record["status"] == "preserved":
        # The check keeps fragments it cannot admit, such as a lone decorator.
        return body
    if record["status"] not in {"clean", "formatted"}:
        raise ValueError(f"Include {relative} could not be formatted: {record['reason']}")
    lines = text.splitlines()
    code = [
        number + 1
        for number in range(first, last)
        if lines[number].strip() and not lines[number].lstrip().startswith("#")
    ]
    starts, ends = statement_lines(ast.parse(text))
    if not code or code[0] not in starts or code[-1] not in ends:
        raise ValueError(
            f"Include {relative} must begin and end on whole Python statements; "
            "select them with #symbol, from=, to= or until="
        )
    return document.removeprefix("```python\n").removesuffix("\n```\n")


def excerpt(match: re.Match[str]) -> str:
    """Embed project source named by an include marker, with Python in canonical style."""
    relative = match["path"]
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE / "projects") or not path.is_file():
        raise ValueError(f"Include target {relative} is not a project file")
    text = path.read_text("utf-8")
    lines = text.splitlines()
    first, last = 0, len(lines)
    if match["symbol"]:
        node = next(
            n
            for n in ast.parse(text).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == match["symbol"]
        )
        first = min([d.lineno for d in node.decorator_list] + [node.lineno]) - 1
        last = node.end_lineno or last
    if match["start"]:
        first = next(i for i in range(first, last) if match["start"] in lines[i])
    if match["end"]:
        last = next(i for i in range(first, last) if match["end"] in lines[i]) + 1
    if match["until"]:
        last = next(i for i in range(first, last) if match["until"] in lines[i])
    body = textwrap.dedent("\n".join(lines[first:last])).strip("\n")
    if "```" in body or not body:
        raise ValueError(f"Include {relative} cannot be fenced")
    if match["language"] == "python":
        body = python_excerpt(relative, text, first, last, body)
    if match["flags"] and not FENCE_FLAGS.fullmatch(match["flags"].strip()):
        raise ValueError(f"Include {relative} has unsupported fence flags")
    info = match["language"] + match["flags"]
    return f"From [`{relative}`](../{relative}):\n\n```{info}\n{body}\n```"


def lab(prose: str, language: str) -> str:
    marker = " (design exercise)"
    cases = [(label, title.strip()) for label, title in CASE.findall(prose)]
    run = " and ".join(f'worked case {k} ("{t}")' for k, t in cases if marker not in t)
    design = " and ".join(
        f'worked case {k} ("{t.replace(marker, "")}")' for k, t in cases if marker in t
    )
    if language == "python":
        return f"Run the complete program and compare {run} with the values the chapter states."
    if not design:
        return (
            f"Read {run}, run their labeled commands only in the owned workshop, and compare "
            "the observations with the chapter."
        )
    if not run:
        return (
            f"Work through {design}, which are design exercises with written answers, and "
            "compare your reasoning with those answers."
        )
    return (
        f"Read {run} and run its labeled commands only in the owned workshop; {design} "
        "is a design exercise with a written answer to compare against your reasoning."
    )


def key_terms(key: str, entries: Any) -> str:
    """Validate a unit's structured key terms and render the guide's vocabulary section."""
    if not isinstance(entries, list) or not 3 <= len(entries) <= 5:
        raise ValueError(f"{key} needs 3 to 5 key_terms")
    seen: set[str] = set()
    bullets: list[str] = []
    for entry in entries:
        if not (
            isinstance(entry, list)
            and len(entry) == 2
            and all(isinstance(text, str) and text.strip() == text and text for text in entry)
        ):
            raise ValueError(f"{key} key_terms must be [term, definition] string pairs")
        term, definition = entry
        if re.search(r"[*:\n]", term) or term.casefold() in seen:
            raise ValueError(f"{key} has a malformed or duplicate key term: {term}")
        if not definition.endswith(".") or re.search("[\n\u2013\u2014]", term + definition):
            raise ValueError(f"{key} key term {term} needs a one-paragraph sentence definition")
        seen.add(term.casefold())
        bullets.append(f"- **{term}:** {definition}")
    return "## Key terms\n\n" + "\n".join(bullets)


EXAMPLE_FIELDS = {"title", "language", "code", "output", "interpretation", "fence"}
FENCE_FLAGS = re.compile(
    r"(?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+)"
    r"(?: (?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+))*"
)


def worked_examples(key: str, entries: Any) -> str:
    """Validate a unit's optional worked examples and render the guide section."""
    if entries is None:
        return ""
    if not isinstance(entries, list) or len(entries) < 2:
        raise ValueError(f"{key} needs at least two worked_examples when it declares them")
    titles: set[str] = set()
    codes: set[str] = set()
    blocks: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or not {"title", "language", "code", "interpretation"} <= (
            entry.keys()
        ):
            raise ValueError(f"{key} worked example needs title, language, code, interpretation")
        if set(entry) - EXAMPLE_FIELDS or not all(
            isinstance(value, str) and value.strip() == value and value for value in entry.values()
        ):
            raise ValueError(f"{key} worked example fields must be non-empty trimmed strings")
        title, language, code = entry["title"], entry["language"], entry["code"]
        interpretation = entry["interpretation"]
        fence = entry.get("fence", "")
        if fence and not FENCE_FLAGS.fullmatch(fence):
            raise ValueError(f"{key} worked example {title} has an unsupported fence: {fence}")
        info = language + (" " + fence if fence else "")
        if "\n" in title + interpretation or not interpretation.endswith("."):
            raise ValueError(f"{key} worked example {title} needs a one-paragraph interpretation")
        if not re.fullmatch(r"[a-z][a-z0-9+-]*", language) or "```" in code + entry.get(
            "output", ""
        ):
            raise ValueError(f"{key} worked example {title} has an invalid fence")
        if re.search("[\u2013\u2014]", "".join(entry.values())):
            raise ValueError(f"{key} worked example {title} contains an em or en dash")
        if title.casefold() in titles or code in codes:
            raise ValueError(f"{key} has a duplicate worked example: {title}")
        if language == "python":
            ast.parse(code, filename=f"{key}-example.py")
            document = f"```python\n{code}\n```\n"
            if format_document(document, FORMATTER, {"python"}, path=key)[0] != document:
                raise ValueError(f"{key} worked example {title} is not in canonical Ruff style")
        titles.add(title.casefold())
        codes.add(code)
        block = f"### {title}\n\n```{info}\n{code}\n```\n\n"
        if "output" in entry:
            block += f"```text\n{entry['output']}\n```\n\n"
        blocks.append(block + interpretation)
    return "## Worked examples\n\n" + "\n\n".join(blocks) + "\n\n"


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
        vocabulary = key_terms(key, meta.get("key_terms"))
        examples = worked_examples(key, meta.get("worked_examples"))
        # Sources live under authoring/chapters; generated guides are one level
        # shallower. Only this explicit course-project link prefix is relocated.
        prose = prose.replace("](../../projects/", "](../projects/")
        prose = INCLUDE.sub(excerpt, prose)
        if "<!-- include:" in prose:
            raise ValueError(f"{key} has a malformed include marker")
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
            + (", ".join(f"`{p}`" for p in meta["prerequisites"]) or "none")
            + f".\n\n{vocabulary}\n\n{prose}\n\n{examples}## Complete worked source\n\n"
            + f"{boundary}\n\n"
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
                "lab": lab(prose, meta["language"]),
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
