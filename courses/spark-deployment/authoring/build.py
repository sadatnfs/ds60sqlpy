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
    r"""(?: until=(?P<q3>["'])(?P<until>.+?)(?P=q3))? (?P<language>[\w+-]+) -->$""",
    re.M,
)
CASE = re.compile(r"^## Worked case (\w+): (.+)$", re.M)


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
    return f"From [`{relative}`](../{relative}):\n\n```{match['language']}\n{body}\n```"


def outputs():
    units = json.loads((BASE / "authoring/units.json").read_text())
    if [row["id"] for row in units] != [f"spark-deploy-{i:03d}" for i in range(1, 19)]:
        raise ValueError("Preserve the eighteen stable deployment lesson identities")
    result = {}
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
        guide = header + body + "\n"
        result[BASE / "guides" / (unit["id"] + ".md")] = guide
        result[BASE / "lessons" / (unit["id"] + ".md")] = guide
        plan.append(
            unit
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
