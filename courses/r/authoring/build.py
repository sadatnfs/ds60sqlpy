#!/usr/bin/env python3
"Assemble the R curriculum from its owned, original JSON teaching records."

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGES = [
    "Values, vectors and structured data",
    "Functions, files and reliable programs",
    "Object systems and maintainable analytical software",
    "Data transformation and reproducible workflows",
    "Statistical analysis and model validation",
    "Base graphics, ggplot2 and interactive Plotly",
]
RUNTIME = (
    "Use the classroom's R language pad and prepared "
    "r-statistics profile. Each run evaluates one main.R "
    "script in a fresh offline R process. Define every "
    "required input in the script; earlier runs do not "
    "leave live variables behind. Save source and notes "
    "separately from saved run output. No package installation "
    "or data download is needed for these examples."
)
PLOTS = (
    "Base plot calls are captured as PNG figures. "
    "Explicitly print ggplot2 and Plotly objects in "
    "scripts: print(chart). The classroom retains at most "
    "two figures per run; Plotly figures use the prepared "
    "interactive browser renderer. A temporary file created "
    "inside a run is not automatically a persistent "
    "download. Keep the supplied examples self-contained "
    "and use the saved source, notes and supported "
    "figure/result views for retained work."
)


VERSIONS = (
    "The prepared environment uses R 4.6.1, R6 2.6.1, S7 "
    "0.2.2, ggplot2 4.0.3 and Plotly 4.12.1. These original "
    "examples use the checked-in dependency contract; "
    "external package changes require a fresh compatibility "
    "check."
)
COMPARE = (
    "Compare your implementation with the reference only "
    "after retaining your own attempt. Different readable "
    "implementations can satisfy the same behavioral "
    "contract. Inspect type, shape, missingness and "
    "boundary behavior alongside printed numbers. A successful "
    "exit checks only the properties a program actually "
    "asserts; it does not establish general correctness or "
    "mastery."
)
# Base graphics draw immediately; ggplot2 and Plotly objects draw only when printed.
BASE_PLOT = re.compile(r"(?<![\w.:])(plot|hist|barplot|boxplot|image|pie|matplot|curve)\(")
FIGURE_CONSTRUCTOR = re.compile(
    r"\b(ggplot2::ggplot|ggplot|plotly::plot_ly|plot_ly|plotly::ggplotly|ggplotly)\("
)
ASSIGNMENT = re.compile(r"^\s*([A-Za-z.][\w.]*)\s*<-\s*(.*)$")


def units():
    return [json.loads(path.read_text()) for path in sorted((HERE / "units").glob("r-*.json"))]


def reasoning(key):
    "Per-lesson solution reasoning and extra guide sections, kept beside the unit schema."
    path = HERE / "reasoning" / f"{key}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def draws_figures(unit):
    for code in [unit["reference"], *[e["code"] for e in unit["worked_examples"]]]:
        if BASE_PLOT.search(code):
            return True
        figures = set()
        for line in code.splitlines():
            match = ASSIGNMENT.match(line)
            if not match or "ggplot_build(" in match[2] or "plotly_build(" in match[2]:
                continue
            if FIGURE_CONSTRUCTOR.search(match[2]) or any(
                re.search(rf"\b{re.escape(name)}\b", match[2]) for name in figures
            ):
                figures.add(match[1])
        if any(re.search(rf"\bprint\(\s*{re.escape(name)}\s*\)", code) for name in figures):
            return True
    return False


STUDY = "../STUDY-GUIDE.md"
NOTE_FIELDS = ("run_note", "checks_note")


def notes(key):
    "Lesson-specific run and check notes; shared routines live in STUDY-GUIDE.md."
    data = reasoning(key)
    for field in NOTE_FIELDS:
        value = data.get(field, "")
        if (
            not isinstance(value, str)
            or len(re.findall(r"[A-Za-z]+", value)) < 30
            or "\n" in value
            or re.search("[\u2013\u2014]", value)
            or not value.rstrip().endswith((".", "?"))
        ):
            raise ValueError(f"{key}: reasoning field {field} needs lesson-specific prose")
    return data


def run_section(unit):
    key = unit["id"]
    text = [
        notes(key)["run_note"],
        "",
        f"Work in the [starter](../lessons/{key}.R) under the [run rules]({STUDY}#run-a-chapter).",
        "",
        (
            f"The [complete reference](../solutions/{key}_reference.R) ends by printing "
            f"`{key} reference checks passed`."
        ),
    ]
    if draws_figures(unit):
        text += [
            "",
            (
                f"This chapter draws figures; read [figure capture]({STUDY}#figures) "
                "before printing them."
            ),
        ]
    return "\n".join(text)


def guide(unit, successors=()):
    key = unit["id"]
    prerequisites = ", ".join(f"`{x}`" for x in unit["prerequisites"]) or "None."
    text = [
        f"# {key}: {unit['title']}",
        "",
        f"**Level:** {unit['level']}. **Direct prerequisites:** {prerequisites}",
        "",
        "## Run and retain your work",
        "",
        run_section(unit),
        "",
        "## Outcome and mechanism",
        "",
        unit["outcome"],
        "",
        unit["mechanism"],
        "",
        "## Vocabulary",
        "",
        "| Term | Meaning |",
        "| --- | --- |",
    ]
    text += [f"| {item['term']} | {item['definition']} |" for item in unit["vocabulary"]]
    text += ["", "## Read the syntax", "", unit["anatomy"], "", "## Worked examples", ""]
    for number, example in enumerate(unit["worked_examples"], 1):
        text += [
            f"### Example {number}: {example['title']}",
            "",
            "```r",
            example["code"].rstrip(),
            "```",
            "",
            f"**Expected observation:** {example['expected']}",
            "",
            example["explanation"],
            "",
        ]
    for section in reasoning(key).get("guide_sections", []):
        text += [f"## {section['heading']}", "", section["body"].strip(), ""]
    text += ["## Practice with evidence", ""]
    labels = ["Predict", "Modify", "Construct", "Diagnose", "Check a boundary", "Transfer"]
    for number, task in enumerate(unit["exercises"], 1):
        text += [f"### Exercise {number}: {labels[number - 1]}", "", task["prompt"], ""]
    text += ["## Progressive hints", ""]
    text += [f"{i}. {task['hint']}" for i, task in enumerate(unit["exercises"], 1)]
    worked = {e["explanation"].strip() for e in unit["worked_examples"]}
    review = (
        "The reference reuses the worked examples' reasoning; "
        f"[explained answers](../solutions/{key}_solutions.md) cover each exercise."
        if set(unit["solution_explanation"].strip().split("\n\n")) <= worked
        else unit["solution_explanation"]
    )
    text += ["", "## Reference review", "", review, "", "## Primary references", ""]
    text += [f"- [{source['title']}]({source['url']})" for source in unit["sources"]]
    titles = {other["id"]: other["title"] for other in successors}
    followers = [other["id"] for other in successors if key in other["prerequisites"]]
    if followers:
        onward = "\n".join(
            ["| Next chapter | Title |", "| --- | --- |"]
            + [f"| [`{other}`]({other}.md) | {titles[other]} |" for other in followers]
        )
    else:
        onward = (
            f"No later chapter lists `{key}` as a direct prerequisite; see the "
            "[course map](../README.md)."
        )
    if 41 <= int(key.split("-")[1]) <= 50:
        onward += (
            "\n\nModeling assumptions behind these examples are in the "
            "[statistics tutorial](../../statistics-ml/README.md)."
        )
    text += [
        "",
        "## Continue",
        "",
        onward,
        "",
        "## Ask an AI tutor",
        "",
        "```text",
        f"Use $guide-ds60sqlpy-learning for {key} ({unit['title']}).",
        "Read the guide and my saved attempt. Explain the relevant R mechanism,",
        f"type and data-shape contract, focusing on: {', '.join(unit['concepts'])}.",
        "Give one progressive hint before revealing the complete reference unless",
        "I request it. Distinguish my observed output from an expected result and",
        "from unrun code. Do not claim mastery from a successful process exit or a",
        "matching source string.",
        "```",
        "",
    ]
    return "\n".join(text)


def solution(unit):
    key = unit["id"]
    steps = reasoning(key).get("exercises", [])
    text = [
        f"# {key}: reference reasoning",
        "",
        (
            f"Run the [complete reference]({key}_reference.R) under the "
            f"[run rules]({STUDY}#run-a-chapter)."
        ),
        "",
        "## Why the implementation has this shape",
        "",
        unit["solution_explanation"],
        "",
        "## Explained practice",
        "",
    ]
    for i, task in enumerate(unit["exercises"], 1):
        text += [
            f"### Exercise {i}",
            "",
            task["prompt"],
            "",
            task["answer"],
            "",
        ]
        if task["expected"].strip() != task["answer"].strip():
            text += [f"**Expected evidence:** {task['expected']}", ""]
        if i <= len(steps):
            step = steps[i - 1]
            text += [
                f"**Approach:** {step['approach']}",
                "",
                f"**Why it holds here:** {step['why']}",
                "",
                f"**Tempting mistake:** {step['wrong']}",
                "",
                f"**Verify:** {step['verify']}",
                "",
            ]
    text += [
        "## What the checks establish",
        "",
        notes(key)["checks_note"],
        "",
        (
            f"The reference makes {unit['reference'].count('stopifnot(')} `stopifnot()` checks; "
            f"see [what a passing run proves]({STUDY}#what-a-passing-run-proves)."
        ),
        "",
    ]
    return "\n".join(text)


def readme(records):
    text = [
        "# R: programming, statistical computing and visualization",
        "",
        (
            "This 60-lesson course starts with expressions and "
            "vectors, then develops functions, data contracts, "
            "object systems, analytical software, statistical "
            "modeling and visualization. It covers base R, S3, S4, "
            "R6, S7, base graphics, ggplot2 and Plotly using "
            "original small offline examples."
        ),
        "",
        "## Start in the Docker classroom",
        "",
        "From the repository root:",
        "",
        "```bash",
        "./classroom --profile r-statistics",
        "```",
        "",
        (
            "Choose **R** in the classroom directory. The launcher "
            "prepares missing local images and retains this project "
            "selection for later resumes. Keep the same custom "
            "project name if you use one. See the [front "
            "README](../../README.md) for Docker setup on "
            "macOS/Linux and Windows through WSL 2. You do not need "
            "a host R installation."
        ),
        "",
        RUNTIME,
        "",
        PLOTS,
        "",
        COMPARE,
        "",
        VERSIONS,
        "",
        (
            "The [study guide](STUDY-GUIDE.md) collects the run rules, figure capture "
            "and comparison routine that every chapter links to."
        ),
        "",
        (
            "Each guide ends with an optional prompt for a repository-aware AI tutor "
            "that names the chapter and its concepts; the guides are complete without it."
        ),
        "",
        "## Course map",
        "",
        (
            "Each chapter states its direct prerequisites and "
            "includes at least two independent worked programs, six varied "
            "tasks, hints, a complete reference and explained "
            "answers. A chapter number is a stable identifier, not "
            "a daily schedule."
        ),
        "",
    ]
    for stage, title in enumerate(STAGES):
        text += [f"### Part {stage + 1}: {title}", "", "| Lesson | Outcome |", "| --- | --- |"]
        for unit in records[stage * 10 : (stage + 1) * 10]:
            text += [
                (f"| [{unit['id']}: {unit['title']}](guides/{unit['id']}.md) | {unit['outcome']} |")
            ]
        text += [""]
    text += [
        "## Prepared packages and external projects",
        "",
        (
            "The ordinary worker is CPU-based and offline. Prepared "
            "packages include ggplot2, Plotly, R6, S7, jsonlite and "
            "R's statistical/recommended libraries. Lessons do not "
            "install packages, fetch remote data or require "
            "RStudio. The package-development chapters explain a "
            "real multi-file package workflow as an optional "
            "contributor project; the classroom pad remains a "
            "single-script execution surface. The worker keeps its "
            "C, C++ and Fortran compilers, so a script can write a "
            "small source package to a temporary directory and "
            "build it with `R CMD INSTALL` or compile Rcpp and cpp11 "
            "code offline."
        ),
        "",
        (
            "Learn modeling assumptions and scientific "
            "interpretation with the [statistics "
            "tutorial](../statistics-ml/README.md). Python and JAX "
            "provide complementary executable approaches. A "
            "successful R program is evidence about the stated "
            "computation, not evidence that an observational "
            "association is causal or a model will generalize."
        ),
        "",
        "## Maintain or extend the subject",
        "",
        (
            "Read [AGENTS.md](AGENTS.md) and the [authoring "
            "contract](authoring/README.md). The JSON units are the "
            "durable teaching sources; references and Markdown are "
            "generated from the same code fields to prevent drift."
        ),
        "",
    ]
    return "\n".join(text)


def artifacts():
    records = units()
    files, plan, admitted = {}, [], []
    for unit in records:
        key = unit["id"]
        source = f"courses/r/lessons/{key}.R"
        reference = f"courses/r/solutions/{key}_reference.R"
        files[source] = unit["starter"].rstrip() + "\n"
        files[reference] = (
            f"# {key}: complete reference for the declared synthetic inputs.\n"
            + unit["reference"].rstrip()
            + "\n"
        )
        files[f"courses/r/guides/{key}.md"] = guide(unit, records)
        files[f"courses/r/solutions/{key}_solutions.md"] = solution(unit)
        plan.append(
            {
                "id": key,
                "title": unit["title"],
                "level": unit["level"],
                "minutes": unit["minutes"],
                "prerequisites": unit["prerequisites"],
                "runtime": "r-statistics",
                "concepts": unit["concepts"],
                "outcome": unit["outcome"],
                "lab": unit["exercises"][2]["prompt"],
                "verification": "Reproduce the worked observations: "
                + " ".join(e["expected"].strip() for e in unit["worked_examples"][:2]).replace(
                    "`", ""
                ),
            }
        )
        admitted.append(
            {
                "id": key,
                "status": "authored",
                "language": "r",
                "runtime_profile": "r-statistics",
                "guide_path": f"courses/r/guides/{key}.md",
                "source_path": source,
                "solution_paths": [reference, f"courses/r/solutions/{key}_solutions.md"],
                "verification_id": None,
            }
        )
    for path, data in [
        (
            "courses/r/track.json",
            {
                "schema_version": 1,
                "id": "r",
                "title": "R: programming, statistical computing and visualization",
                "summary": (
                    "60 lessons covering R fundamentals, functions, data "
                    "workflows, S3/S4/R6/S7 objects, statistical models and "
                    "base, ggplot2 and Plotly visualization."
                ),
                "lessons": plan,
            },
        ),
        ("courses/r/lessons.json", {"schema_version": 1, "track_id": "r", "lessons": admitted}),
    ]:
        files[path] = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    files["courses/r/README.md"] = readme(records)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records = units()
    if [u["id"] for u in records] != [f"r-{n:03}" for n in range(1, 61)]:
        parser.error("All 60 ordered units are required before publishing R admission.")
    changed = []
    for relative, value in artifacts().items():
        path = ROOT / relative
        if not path.exists() or path.read_text() != value:
            changed.append(relative)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
    print(
        f"R authoring: {len(records)} units; {len(changed)} "
        + ("drifted files" if args.check else "files updated")
    )
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
