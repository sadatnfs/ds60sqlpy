"""Publish the three related data-engineering paths from maintained prose and programs."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from case_files import render_case  # noqa: E402


def format_python(source: str) -> str:
    # Extracted cases need only their own imports; keep generated pads lint-clean.
    organized = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--select",
            "I,F401",
            "--fix",
            "--config",
            str(ROOT / "pyproject.toml"),
            "--stdin-filename",
            "lesson.py",
            "-",
        ],
        input=source,
        capture_output=True,
        text=True,
        check=True,
    )
    source = organized.stdout
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--config",
            str(ROOT / "pyproject.toml"),
            "--stdin-filename",
            "lesson.py",
            "-",
        ],
        input=source,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract_case(
    source: str,
    functions: str | list[str],
    *,
    exclude: tuple[str, ...] = (),
    runnable: bool = True,
) -> str:
    names = [functions] if isinstance(functions, str) else list(functions)
    tree = ast.parse(source)
    definitions = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    required = set(names)
    while True:
        previous = set(required)
        for name in previous:
            required.update(
                n.id
                for n in ast.walk(definitions[name])
                if isinstance(n, ast.Name) and n.id in definitions and n.id not in exclude
            )
        if previous == required:
            break
    parts = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign)) or (
            isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in required
        ):
            parts.append(ast.get_source_segment(source, node) or "")
    trailer = ""
    if runnable:
        calls = "".join(f"    print({name}())\n" for name in names)
        trailer = f'\n\nif __name__ == "__main__":\n{calls}'
    return format_python("\n\n".join(parts) + trailer)


def helper_calls(source: str, function: str, helpers: tuple[str, ...]) -> list[str]:
    tree = ast.parse(source)
    definitions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    seen, pending, used = set(), [function], []
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        for node in ast.walk(definitions[name]):
            if isinstance(node, ast.Name) and node.id in definitions:
                if node.id in helpers:
                    if node.id not in used:
                        used.append(node.id)
                else:
                    pending.append(node.id)
    return [name for name in helpers if name in used]


def spoken_list(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def answer_block(task: dict) -> str:
    code = task.get("answer_code")
    if not code:
        return ""
    language, text = ("python", code) if isinstance(code, str) else (code["language"], code["code"])
    return f"\n\n```{language}\n{text.rstrip()}\n```"


def render(base: Path) -> dict[Path, str]:
    config = json.loads((base / "authoring/units.json").read_text("utf-8"))
    subject = config["id"]
    items = config["units"]
    assert {u["level"] for u in items} == {"beginner", "intermediate", "advanced"}
    result: dict[Path, str] = {}
    plan, admissions = [], []
    for unit in items:
        key = unit["id"]
        reference = base / "references" / f"{key}_reference.py"
        source = reference.read_text("utf-8")
        ast.parse(source)
        assert len(unit["worked"]) == 2 and len(unit["exercises"]) == 6
        assert len({x["title"] for x in unit["exercises"]}) == 6
        assert "\u2014" not in json.dumps(unit, ensure_ascii=False)
        prerequisites = ", ".join(f"`{v}`" for v in unit["prerequisites"])
        intro = (
            f"# {key}: {unit['title']}\n\n"
            f"## Level and prerequisites\n\n{unit['level'].title()}. Direct prerequisites: "
            f"{prerequisites or 'No prior knowledge of this tool.'}\n\n"
            f"**Outcome:** {unit['outcome']}\n\n"
            f"## Question and mechanism\n\n{unit['theory'].strip()}\n\n"
            f"## Syntax and data contract\n\n{unit['syntax'].strip()}\n\n"
        )
        if unit.get("math"):
            intro += "## Mathematical interpretation\n\n" + unit["math"].strip() + "\n\n"
        first_title, second_title = (case["title"] for case in unit["worked"])
        intro += (
            f"## Run the lesson\n\nOpen `{key}` in `/classroom`. Its starter `main.py` contains "
            f'both worked cases, "{first_title}" and "{second_title}", and prints the dictionary '
            "each case returns. The prepared `data-engineering` worker runs it in a fresh "
            "temporary directory. An `AssertionError` means that an observation differs from "
            f"the case's stated contract. {config['run_notice']} Save source and notes before "
            "switching lessons.\n\n"
        )
        if unit.get("sql_variant"):
            intro = intro.replace("## Run the lesson", "## Full-project Python workspace")
            intro += (
                "## SQL-first model workspace\n\n"
                "Choose **SQL model** in the language selector to write a model directly. "
                "The separate `dbt-duckdb` profile compiles and builds it "
                "in a prepared local project. "
                "It provides `ref('raw_orders')`, `ref('customers')` and "
                "`source('raw', 'orders')`. "
                "The five fixed orders have amounts 100, 50, 25, 80 and 120; statuses are paid, "
                "paid, refunded, pending and paid. The fixed status "
                "variable is paid, and report_date "
                "is 2024-01-06. Paid amount totals 270. Customers 10/20/30 "
                "are Ada/north, Ben/south "
                "and Cy/north. This fixture differs deliberately from the "
                "full-project examples below. "
                "Compare returned rows by their keys: a materialized "
                "relation has no guaranteed row "
                "order.\n\n"
                + unit["sql_variant"]["explanation"]
                + "\n\nThe SQL pad changes one model. Project configuration, "
                "custom macros, seeds, tests, "
                "snapshots and incremental state are taught through the "
                "complete Python/CLI projects; "
                "the model-only pad does not pretend to edit those files.\n\n"
            )
        sections = [intro]
        harness = config.get("case_harness")
        for index, case in enumerate(unit["worked"], 1):
            function = "example_one" if index == 1 else "example_two"
            body = f"## Worked case {index}: {case['title']}\n\n{case['explanation']}\n\n"
            note = ""
            if harness:
                first = key == harness["introduced_in"] and index == 1
                helpers = tuple(harness["helpers"])
                program = extract_case(
                    source, function, exclude=() if first else helpers, runnable=first
                )
                body += render_case(source, function, include_skeleton=first) + "\n\n"
                used = spoken_list(
                    [f"`{name}`" for name in helper_calls(source, function, helpers)]
                )
                template = harness["first_note"] if first else harness["note"]
                note = template.format(key=key, helpers=used) + "\n\n"
            else:
                program = extract_case(source, function)
            sections.append(
                body + f"**Expected evidence:** {case['expected']}\n\n{note}```python\n{program}```"
            )
        sections.append(
            "## Practice\n\nThe starter contains both worked cases, so a task can change either "
            "one. Make each change in a saved copy, run it, and compare the printed result with "
            "the task's check before opening the separate explained answers."
        )
        for index, task in enumerate(unit["exercises"], 1):
            sections.append(
                f"### {index}. {task['title']}\n\n{task['task']}\n\n"
                f"**Check:** {task['check']}\n\n**Hint:** {task['hint']}"
            )
        sections += [
            "## Diagnose errors and misleading results\n\n" + unit["diagnosis"],
            "## Transfer to independent work\n\n" + unit["transfer"],
            "## Primary references\n\n"
            + "\n".join(f"- [{label}]({url})" for label, url in unit["references"]),
            "## Tutor guidance\n\nUse the repository's `$guide-ds60sqlpy-learning` skill "
            f"(`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`) for `{key}`. Inspect the "
            "learner's own source and printed output first. Ask for an explanation of "
            f"{spoken_list(unit['concepts'])} in their own words, then give one focused hint at a "
            "time. Keep an assertion on this synthetic fixture separate from a claim about an "
            "external dataset or deployed service.",
        ]
        result[base / "guides" / f"{key}.md"] = (
            "\n\n".join(section.strip() for section in sections) + "\n"
        )
        starter = extract_case(source, ["example_one", "example_two"])
        tasks = "\n".join(
            textwrap.fill(
                task["task"], width=96, initial_indent=f"# TODO {i}: ", subsequent_indent="#    "
            )
            for i, task in enumerate(unit["exercises"], 1)
        )
        result[base / "lessons" / f"{key}.py"] = format_python(
            f'"""{key}: both worked cases; complete the guide\'s six changes."""\n\n'
            + starter
            + "\n"
            + tasks
            + "\n"
        )
        answers = [
            f"# {key}: explained reference\n\n{unit['outcome']}\n\n"
            "The executable reference contains the two complete worked cases with assertions. "
            "The changes below explain the independent practice and its limits.\n"
        ]
        for i, task in enumerate(unit["exercises"], 1):
            answers.append(
                f"## {i}. {task['title']}\n\n{task['answer']}{answer_block(task)}\n\n"
                f"**Expected:** {task['check']}"
            )
        answers += [
            "## Complete reference\n\n```python\n" + source + "```",
            "## Interpretation\n\n" + unit["transfer"],
        ]
        result[base / "solutions" / f"{key}_solutions.md"] = "\n\n".join(answers).rstrip() + "\n"
        prefix = f"courses/{subject}"
        plan.append(
            {
                "id": key,
                "title": unit["title"],
                "level": unit["level"],
                "minutes": unit.get("minutes", 90),
                "prerequisites": unit["prerequisites"],
                "runtime": "data-engineering",
                "concepts": unit["concepts"],
                "outcome": unit["outcome"],
                "lab": unit["lab"],
                "verification": (
                    "Run the starter and compare both printed results with the guide. "
                    f"Worked case 1: {unit['worked'][0]['expected']} "
                    f"Worked case 2: {unit['worked'][1]['expected']}"
                ),
            }
        )
        admissions.append(
            {
                "id": key,
                "status": "authored",
                "language": "python",
                "runtime_profile": "data-engineering",
                "guide_path": f"{prefix}/guides/{key}.md",
                "source_path": f"{prefix}/lessons/{key}.py",
                "solution_paths": [
                    f"{prefix}/references/{key}_reference.py",
                    f"{prefix}/solutions/{key}_solutions.md",
                ],
                "verification_id": None,
            }
        )
    by_id = {unit["id"]: unit for unit in items}
    for entry in admissions:
        unit = by_id[entry["id"]]
        if not unit.get("sql_variant"):
            continue
        key = unit["id"]
        prefix = f"courses/{subject}"
        explanatory = f"{prefix}/solutions/{key}_sql-model_solutions.md"
        entry["variants"] = [
            {
                "id": "sql-model",
                "title": "SQL model",
                "language": "sql",
                "runtime_profile": "dbt-duckdb",
                "source_path": f"{prefix}/variants/{key}_sql-model.sql",
                "solution_paths": [f"{prefix}/variants/{key}_sql-model_reference.sql", explanatory],
                "verification_id": None,
            }
        ]
        sql = (base / "variants" / f"{key}_sql-model_reference.sql").read_text("utf-8")
        result[ROOT / explanatory] = (
            f"# {key}: SQL-model reference\n\n"
            + unit["sql_variant"]["explanation"]
            + "\n\n```sql\n"
            + sql
            + "```\n\n"
            + "This is actual dbt compilation and DuckDB materialization "
            "in the prepared fixture project. "
            + "It does not execute the full project-editing exercises or deploy a cloud warehouse. "
            + "Model tables have no row-order guarantee; use keys when comparing records.\n"
        )
    result[base / "track.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": subject,
                "title": config["title"],
                "summary": config["summary"],
                "lessons": plan,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    result[base / "lessons.json"] = (
        json.dumps({"schema_version": 1, "track_id": subject, "lessons": admissions}, indent=2)
        + "\n"
    )
    result[base / "README.md"] = (
        "# " + config["title"] + "\n\n" + config["summary"] + "\n\n"
        "Start from the [main Docker "
        "instructions](../../README.md). Select this subject in "
        "the shared classroom. "
        "This path uses the prepared `data-engineering` worker and "
        "requires no host compiler or account. "
        "All examples use local synthetic inputs after image preparation.\n\n"
        "## Route\n\n| Lesson | Stage | Outcome |\n| --- | --- | --- |\n"
        + "\n".join(
            f"| [{u['id']}: {u['title']}](guides/{u['id']}.md) | {u['level']} | {u['outcome']} |"
            for u in items
        )
        + "\n\n## Authoring\n\nMaintained prose is in "
        "`authoring/units.json`; complete programs are in "
        "`references/`. "
        "Run `python authoring/build.py` from this directory, or use `--check` to detect drift. "
        "The three related data courses share `courses/ml-engineering/authoring/publish.py`. "
        "Keep the full repository when using the authoring tools. "
        "The shared readers are generated "
        "separately.\n"
    )
    if config.get("project_readme"):
        result[base / "README.md"] += (
            "\n## Complete local project\n\n"
            + config["project_summary"]
            + "\n\nFollow the [complete project instructions]("
            + config["project_readme"]
            + ").\n"
        )
    return result


def main(base: Path) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(base)
    drift = []
    for path, content in expected.items():
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, "utf-8")
    if drift:
        print("Generated course files need refresh:\n" + "\n".join(drift))
        return 1
    print(
        f"{base.name}: {len(expected)} generated artifacts {'checked' if args.check else 'written'}"
    )
    return 0
