"""Publish this data-engineering path from its maintained sources.

The shared publisher renders every lesson. This wrapper then moves the routine that is
identical in all lessons (running, the case harness, the SQL pad, practice, answers and
tutoring) into ``STUDY-GUIDE.md`` and replaces it in each lesson with that lesson's own
``run_focus``, ``reference_focus`` and ``tutor_probe`` from ``units.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE.parents[1] / "courses/ml-engineering/authoring"))

from publish import ROOT, render, spoken_list  # noqa: E402

STUDY = "../STUDY-GUIDE.md"

SQL_FIXTURE = (
    "Choose **SQL model** in the language selector to write a model directly. "
    "The separate `dbt-duckdb` profile compiles and builds it in a prepared local project. "
    "It provides `ref('raw_orders')`, `ref('customers')` and `source('raw', 'orders')`. "
    "The five fixed orders have amounts 100, 50, 25, 80 and 120; statuses are paid, "
    "paid, refunded, pending and paid. The fixed status variable is paid, and report_date "
    "is 2024-01-06. Paid amount totals 270. Customers 10/20/30 are Ada/north, Ben/south "
    "and Cy/north. This fixture differs deliberately from the full-project examples below. "
    "Compare returned rows by their keys: a materialized relation has no guaranteed row "
    "order."
)
SQL_LIMITS = (
    "The SQL pad changes one model. Project configuration, custom macros, seeds, tests, "
    "snapshots and incremental state are taught through the complete Python/CLI projects; "
    "the model-only pad does not pretend to edit those files."
)
FILES_LABEL = (
    "**Project files.** The case writes these files before its first dbt command. "
    "YAML is shown in conventional key order; dbt reads the same mappings."
)
COMMANDS_LABEL = (
    "**Commands and changes, in order.** Each `dbt` line is one `invoke(...)` call; "
    "the harness adds `--project-dir` and `--profiles-dir` for the temporary project."
)
PRACTICE = (
    "The starter contains both worked cases, so a task can change either one. Make each "
    "change in a saved copy, run it, and compare the printed result with the task's check "
    "before opening the separate explained answers."
)
ANSWERS = (
    "The executable reference contains the two complete worked cases with assertions. "
    "The changes below explain the independent practice and its limits."
)


def run_paragraph(unit: dict, notice: str) -> str:
    first, second = (case["title"] for case in unit["worked"])
    return (
        f"Open `{unit['id']}` in `/classroom`. Its starter `main.py` contains "
        f'both worked cases, "{first}" and "{second}", and prints the dictionary '
        "each case returns. The prepared `data-engineering` worker runs it in a fresh "
        "temporary directory. An `AssertionError` means that an observation differs from "
        f"the case's stated contract. {notice} Save source and notes before "
        "switching lessons."
    )


def tutor_paragraph(unit: dict) -> str:
    return (
        "Use the repository's `$guide-ds60sqlpy-learning` skill "
        f"(`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`) for `{unit['id']}`. Inspect the "
        "learner's own source and printed output first. Ask for an explanation of "
        f"{spoken_list(unit['concepts'])} in their own words, then give one focused hint at a "
        "time. Keep an assertion on this synthetic fixture separate from a claim about an "
        "external dataset or deployed service."
    )


def swap(text: str, old: str, new: str, path: Path, count: int = 1) -> str:
    found = text.count(old)
    if found != count:
        raise SystemExit(
            f"{path.relative_to(ROOT)}: expected {count} copy of shared text, found {found}; "
            "the shared publisher changed, so update courses/dbt/authoring/build.py.\n" + old[:80]
        )
    return text.replace(old, new)


def study_guide(config: dict) -> str:
    total = len(config["units"])
    spoken = spoken_list([unit["id"] for unit in config["units"] if unit.get("sql_variant")])
    return f"""# dbt study guide

Every dbt lesson guide links here for the routine that is the same in all {total} lessons:
how a lesson runs, what the shared case harness does, how the SQL model pad works, how to
practice, how the explained answers are laid out and how a tutor should help. The lesson
guides keep only what is specific to their own projects and results.

## Run a lesson

Open the lesson in `/classroom`. Its starter `main.py` contains both worked cases and
prints the dictionary each case returns. The prepared `data-engineering` worker runs it
in a fresh temporary directory. {config["run_notice"]}

Each lesson's run section says which values should print and what they mean. An
`AssertionError` means that an observation differs from the case's stated contract. Read
its message, then compare the printed dictionary with the guide's **Expected evidence**
before you change code. Never delete or weaken an assertion to get a clean run: the
assertion is the evidence. Save source and notes before switching lessons.

In {spoken} the run section is titled "Full-project Python workspace", because those
lessons also offer the SQL model pad described below.

## Case harness

Every program uses the same small helpers. dbt-001 shows them in full in its first worked
case, and each starter repeats them at the top so that it runs on its own. Later guides
show only each case's own functions.

- `project(directory, models, seeds, schema, snapshots, macros)` creates `project/` with
  `models/`, `seeds/`, `snapshots/` and `macros/` folders. It writes `dbt_project.yml`
  with the profile `classroom` and `profiles.yml` with one `dev` output: DuckDB in
  `warehouse.duckdb`, schema `main`, one dbt thread and a 256MB memory limit. It then
  writes each model, seed CSV and macro, plus `models/schema.yml` and
  `snapshots/snapshots.yml` when they are given. Without models it writes the single
  model `answer`.
- `invoke(root, *arguments, succeeds=True)` runs dbt in the same process through
  `dbtRunner` with `--quiet`, `--no-use-colors` and `--no-send-anonymous-usage-stats`,
  then adds `--project-dir` and `--profiles-dir` (both the temporary project) and
  `--no-partial-parse`. It asserts success, or with `succeeds=False` asserts that dbt
  rejected a deliberately invalid fixture.
- `rows(root, sql)` queries the DuckDB file directly and returns a list of tuples.
- `artifact(root, name)` reads a JSON artifact such as `manifest.json` or
  `run_results.json` from `target/`.
- `relation(root, unique_id)` reads a node's `relation_name` from the manifest. Only
  dbt-010 uses it.

Lesson-specific helpers, such as `targets` in dbt-019 to dbt-021, appear in that
lesson's own program.

A worked case lists its **Project files** before its commands. YAML is shown in
conventional key order; the harness writes it with `yaml.safe_dump`, which sorts keys,
and dbt reads the same mappings either way. Under **Commands, in order**, each `dbt`
line is one `invoke(...)` call. The harness adds `--project-dir` and `--profiles-dir`
for the temporary project, so the listed commands omit them. Text between command
blocks names the file the program changes before its next command.

## SQL model pad

{SQL_FIXTURE}

{SQL_LIMITS}

## Practice routine

The six numbered tasks in each guide change one of its two worked cases, and the
starter contains both. Make each change in a saved copy, run it, and compare the
printed result with the task's **Check** before opening the explained answers. If a
check fails, use the task's **Hint** first, then the guide's section on diagnosing
errors and misleading results.

## Answers and references

Each lesson has an explained answer file in `solutions/` and a complete program in
`references/`. The answer file opens with the lesson outcome and a statement of what the
reference proves and what it does not. Each numbered answer explains the change; where
the guide asks for code or reasoning, it adds the code and the labels **Why it holds
here**, **Plausible wrong approach** and **How to verify**. It ends with the task's
**Expected** check. The file closes with the complete reference program, whose two
worked cases carry the assertions, and an interpretation for independent work.

## Tutor guidance

Tutors use the repository's `$guide-ds60sqlpy-learning` skill
(`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`). Inspect the learner's own source
and printed output first. Ask the learner to explain the lesson's concepts in their own
words, then give one focused hint at a time. Keep an assertion on a synthetic fixture
separate from a claim about an external dataset or deployed service. Each lesson's tutor
section adds the questions that matter for its own cases.
"""


def expected() -> dict[Path, str]:
    config = json.loads((BASE / "authoring/units.json").read_text("utf-8"))
    result = render(BASE)
    for unit in config["units"]:
        key = unit["id"]
        path = BASE / "guides" / f"{key}.md"
        text = result[path]
        text = swap(
            text,
            run_paragraph(unit, config["run_notice"]),
            f"{unit['run_focus']} See the [run routine]({STUDY}#run-a-lesson).",
            path,
        )
        if unit.get("sql_variant"):
            text = swap(
                text,
                SQL_FIXTURE,
                f"Choose **SQL model** in the language selector to use the "
                f"[SQL pad fixture]({STUDY}#sql-model-pad).",
                path,
            )
            text = swap(text, "\n\n" + SQL_LIMITS, "", path)
        text = swap(
            text,
            FILES_LABEL,
            "**Project files**, written before the first dbt command:",
            path,
            count=2,
        )
        text = swap(
            text,
            COMMANDS_LABEL,
            "**Commands, in order.** Each `dbt` line is one `invoke(...)` call.",
            path,
            count=2,
        )
        text = swap(
            text,
            PRACTICE,
            f"Use the [practice routine]({STUDY}#practice-routine).",
            path,
        )
        text = swap(
            text,
            tutor_paragraph(unit),
            f"{unit['tutor_probe']} See the [tutor routine]({STUDY}#tutor-guidance).",
            path,
        )
        result[path] = text
        path = BASE / "solutions" / f"{key}_solutions.md"
        result[path] = swap(
            result[path],
            ANSWERS,
            f"{unit['reference_focus']} See [how these answers are laid out]"
            f"({STUDY}#answers-and-references).",
            path,
        )
    readme = BASE / "README.md"
    result[readme] += (
        "\n## Study guide\n\nThe [study guide](STUDY-GUIDE.md) holds the routine shared by "
        "every lesson: running a case, the case harness, the SQL model pad, practice, "
        "explained answers and tutoring.\n"
    )
    result[BASE / "STUDY-GUIDE.md"] = study_guide(config)
    return result


def build() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = expected()
    drift = []
    for path, content in files.items():
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, "utf-8")
    if drift:
        print("Generated course files need refresh:\n" + "\n".join(drift))
        return 1
    print(f"{BASE.name}: {len(files)} generated artifacts {'checked' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
