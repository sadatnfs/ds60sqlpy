"""Generate the deployment tutorial from its maintained chapters and unit metadata."""

import argparse
import ast
import json
import re
import sys
import textwrap
from pathlib import Path

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
CASE = re.compile(r"^## Worked case (\w+): (.+)$", re.M)
EXAMPLE_LANGUAGES = {"python", "bash", "yaml", "ini", "dockerfile", "sql", "text"}
EXAMPLE_FIELDS = {"title", "language", "code", "output", "interpretation", "fence"}
OPTIONAL_FIELDS = {"output", "fence"}
FENCE_FLAGS = re.compile(
    r"(?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+)"
    r"(?: (?:fragment|external|expect-error|isolated|prelude=[\w./-]+|profile=[\w-]+))*"
)
GUIDE_WORDS = re.compile(r"\b[\w'-]+\b")


def ruff_adapter(source, language, suffix, root):
    """Run the locked Ruff with the configuration the fence formatting check uses."""
    config = str(root / "pyproject.toml")
    command = ["format", "--no-cache", "--config", config, "--stdin-filename", "snippet" + suffix]
    return invoke([sys.executable, "-m", "ruff", *command, "-"], source, root)


FORMATTER = Formatter(ROOT, adapter=ruff_adapter)


def statement_lines(tree):
    """First and last lines of every statement; decorators start their definition."""
    starts, ends = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
            decorators = getattr(node, "decorator_list", [])
            starts.add(min([item.lineno for item in decorators] + [node.lineno]))
            ends.add(node.end_lineno or node.lineno)
    return starts, ends


def python_excerpt(relative, text, first, last, body):
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


def excerpt(match):
    """Embed workshop source named by an include marker, with Python in canonical style."""
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


def key_terms_block(unit):
    """Render the unit's authored vocabulary as a Key terms section."""
    terms = unit.get("key_terms", [])
    names = [term for term, _ in terms]
    if not 3 <= len(terms) <= 5 or len(set(names)) != len(names):
        raise ValueError(f"{unit['id']} needs three to five distinct key terms")
    for term, definition in terms:
        if not term.strip() or not definition.strip():
            raise ValueError(f"{unit['id']} has an empty key term")
        if "\u2014" in term + definition or "\u2013" in term + definition:
            raise ValueError(f"{unit['id']} key terms must not use em or en dashes")
    return "## Key terms\n\n" + "\n".join(f"- **{t}:** {d}" for t, d in terms) + "\n\n"


def worked_examples_block(unit, titles, codes):
    """Validate and render the unit's worked examples as guide sections.

    ``output`` is optional and must be text observed by running the block itself.
    """
    key = unit["id"]
    examples = unit.get("worked_examples", [])
    if not examples:
        raise ValueError(f"{key} needs at least one worked example")
    sections = []
    for example in examples:
        if set(example) - EXAMPLE_FIELDS or not set(example) >= EXAMPLE_FIELDS - OPTIONAL_FIELDS:
            raise ValueError(f"{key} worked examples need exactly the documented fields")
        title, code = example["title"].strip(), example["code"].strip("\n")
        language, note = example["language"], example["interpretation"].strip()
        output = example.get("output", "").strip("\n")
        fence = example.get("fence", "")
        if fence and not FENCE_FLAGS.fullmatch(fence):
            raise ValueError(f"{key} has an unsupported worked example fence: {fence}")
        info = language + (" " + fence if fence else "")
        if not title or not code.strip() or language not in EXAMPLE_LANGUAGES:
            raise ValueError(f"{key} has an empty or unsupported worked example")
        if title.lower() in titles or code in codes:
            raise ValueError(f"{key} repeats a worked example title or program: {title}")
        titles.add(title.lower())
        codes.add(code)
        if any(d in "".join(example.values()) for d in ("\u2014", "\u2013")):
            raise ValueError(f"{key} worked examples must not use em or en dashes")
        if "```" in code + output:
            raise ValueError(f"{key} worked example text cannot contain a fence")
        if "\n" in note or len(note.split()) < 40 or not note.endswith("."):
            raise ValueError(f"{key} interpretation must be one paragraph of 40+ words")
        if language == "python":
            ast.parse(code, filename=f"{key} worked example")
        observed = f"Output from running the block above:\n\n```text\n{output}\n```\n\n"
        sections.append(
            f"## Worked example: {title}\n\n```{info}\n{code}\n```\n\n"
            + (observed if output else "")
            + note
        )
    return "\n\n".join(sections) + "\n\n"


def outputs():
    units = json.loads((BASE / "authoring/units.json").read_text())
    if [row["id"] for row in units] != [f"spark-deploy-{i:03d}" for i in range(1, 19)]:
        raise ValueError("Preserve the eighteen stable deployment lesson identities")
    result = {}
    titles, codes = set(), set()
    plan = []
    admitted = []
    for number, unit in enumerate(units, 1):
        body = (BASE / "authoring/chapters" / f"{number:02d}.md").read_text().strip()
        if len(body.split()) < 350 or body.count("## Worked case") != 2 or "\u2014" in body:
            raise ValueError(
                f"{unit['id']} requires substantial original prose and two worked cases"
            )
        header = (
            f"# {unit['id']}: {unit['title']}\n\n"
            f"Tutorial mode. Stage: {unit['level']}. Direct prerequisites: "
            + ", ".join(f"`{key}`" for key in unit["prerequisites"])
            + ".\n\n"
            + "Read this tutorial in the classroom. Its commands run only in the separately "
            "prepared [owned workshop](../projects/cluster-lab/README.md); "
            "there is no pad Run action. "
            "Examples describe expected observations. Check the workshop qualification ledger "
            "for actual execution evidence.\n\n"
        )
        body = INCLUDE.sub(excerpt, body)
        if "<!-- include:" in body:
            raise ValueError(f"{unit['id']} has a malformed include marker")
        cases = " and ".join(f'worked case {k} ("{t.strip()}")' for k, t in CASE.findall(body))
        first_case = body.index("## Worked case")
        body = body[:first_case] + key_terms_block(unit) + body[first_case:]
        marker = "## Diagnose and transfer"
        if body.count(marker) != 1:
            raise ValueError(f"{unit['id']} needs one Diagnose and transfer section")
        split = body.index(marker)
        body = body[:split] + worked_examples_block(unit, titles, codes) + body[split:]
        guide = header + body + "\n"
        fences = sum(line.startswith("```") for line in guide.splitlines())
        if fences < 4 or len(GUIDE_WORDS.findall(guide)) < 1050:
            raise ValueError(f"{unit['id']} guide needs two code blocks and 1050 words")
        result[BASE / "guides" / (unit["id"] + ".md")] = guide
        result[BASE / "lessons" / (unit["id"] + ".md")] = guide
        plan.append(
            {k: v for k, v in unit.items() if k not in {"key_terms", "worked_examples"}}
            | {
                "runtime": "reading",
                "lab": (
                    f"Follow {cases} in the owned cluster-lab workshop and compare each "
                    "observation with the chapter and the qualification ledger."
                ),
                "verification": (
                    "Keep the commands and observations from both worked cases that show this "
                    f"outcome: {unit['outcome']} A parsed configuration alone is not runtime "
                    "evidence."
                ),
            }
        )
        admitted.append(
            {
                "id": unit["id"],
                "status": "authored",
                "language": "markdown",
                "runtime_profile": "reading",
                "guide_path": f"courses/spark-deployment/guides/{unit['id']}.md",
                "source_path": f"courses/spark-deployment/lessons/{unit['id']}.md",
                "solution_paths": [],
                "verification_id": None,
            }
        )
    result[BASE / "track.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": "spark-deployment",
                "title": "Spark deployment: Compose, notebooks and Kubernetes",
                "summary": (
                    "An eighteen-unit tutorial connecting driver placement, isolated Compose, "
                    "Jupyter, images, networking, live/history UIs, storage, security, resource "
                    "budgets and portable Kubernetes submission."
                ),
                "learning_mode": "tutorial",
                "lessons": plan,
            },
            indent=2,
        )
        + "\n"
    )
    result[BASE / "lessons.json"] = (
        json.dumps(
            {"schema_version": 1, "track_id": "spark-deployment", "lessons": admitted}, indent=2
        )
        + "\n"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for path, expected in outputs().items():
        if not path.exists() or path.read_text() != expected:
            changed.append(str(path.relative_to(BASE)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected)
    if args.check and changed:
        raise SystemExit("Deployment source drift: " + ", ".join(changed))
    print(f"Checked {len(outputs())} deployment artifacts; drift={len(changed)}")


if __name__ == "__main__":
    main()
