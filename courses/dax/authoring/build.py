#!/usr/bin/env python3
"Build only the original DAX curriculum. Never execute a DAX engine or use network."

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import importlib.util
import io
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKAGE = "_ds60_dax_authoring"
if PACKAGE not in sys.modules:
    package_spec = importlib.util.spec_from_file_location(
        PACKAGE, HERE / "__init__.py", submodule_search_locations=[str(HERE)]
    )
    assert package_spec and package_spec.loader
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[PACKAGE] = package
    package_spec.loader.exec_module(package)
common = importlib.import_module(f"{PACKAGE}.common")
fixtures = importlib.import_module(f"{PACKAGE}.fixtures")
BASE, STAGES = common.BASE, common.STAGES
model_artifacts, dump = fixtures.artifacts, fixtures.dump

BOUNDARY = (
    "This is an offline DAX editing lesson. No DAX compiler, "
    "semantic-model engine, Power BI account or network "
    "connection is required. Worked tables describe the named "
    "reference and model, not execution of your draft. Save, "
    "compare and export source; do not interpret a comparison "
    "or completion marker as a passed program run."
)


def all_lessons():
    lessons = []
    for number in range(1, 11):
        path = HERE / f"part{number:02}.py"
        if path.exists():
            lessons.extend(importlib.import_module(f"{PACKAGE}.part{number:02}").LESSONS)
    return lessons


def reference_source(spec):
    declarations = spec["defines"]
    if declarations == BASE:
        queries = "\n".join(case["query"] for case in spec["cases"])
        lines = [
            line
            for line in BASE.splitlines()[1:]
            if any(
                f"[{name}]" in queries and f"Sales[{name}]" in line
                for name in ["NetRevenue", "QuantitySold", "GrossRevenue", "OrderCount"]
            )
        ]
        declarations = "DEFINE\n" + "\n".join(lines) + "\n" if lines else ""
    pieces = [
        f"// {spec['id']}: {spec['title']}",
        ("// Offline reference. These formulas have not been executed by this classroom."),
        f"// Model contract: courses/dax/models/{spec['model']}/model.json",
        "// Result cases and source/model hashes: courses/dax/reference-results.json",
        "",
    ]
    if declarations:
        pieces += [declarations.rstrip(), ""]
    for index, case in enumerate(spec["cases"], 1):
        pieces += [
            f"// {spec['id']}-{chr(96 + index)}: {case['title']}",
            "// Context: " + case["context"],
            case["query"],
            "",
        ]
    return "\n".join(pieces).rstrip() + "\n"


def table(case):
    def cell(value):
        if value is None:
            return "BLANK"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("Worked tables require finite numeric values")
            return f"{value:.10g}"
        return str(value).replace("|", "\\|")

    headers = [col["name"] for col in case["columns"]]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(cell(value) for value in row) + " |" for row in case["rows"]]
    if not case["rows"]:
        lines.append(
            "\nThe reference table has **zero rows**. This differs from "
            "one row whose value is BLANK."
        )
    return "\n".join(lines)


def starter_source(spec):
    body = spec.get("starter") or 'EVALUATE\nROW ( "Draft result", BLANK() )'
    return (
        f"// {spec['id']} learner draft: {spec['title']}\n"
        "// Offline editing only. No execution or automatic grading occurs here.\n"
        f"// Model: courses/dax/models/{spec['model']}/model.json\n"
        f"// Goal: {spec['outcome']}\n"
        "// Keep a prediction and row/filter-context trace beside your edits.\n"
        "// TODO: " + spec["practice"][2]["question"] + "\n\n" + body.strip() + "\n"
    )


def guide(spec):
    key = spec["id"]
    level = (
        "beginner" if spec["stage"] <= 2 else "intermediate" if spec["stage"] <= 6 else "advanced"
    )
    prereqs = (
        ", ".join(f"`{item}`" for item in spec["prerequisites"])
        or "None. Start from tables, sums and ratios."
    )
    content = [
        f"# {key}: {spec['title']}",
        "",
        (
            f"**Stage {spec['stage']}: {STAGES[spec['stage'] - 1]}.** Level: "
            f"{level}. Read the mechanisms, trace the worked cases and retain "
            f"your own draft."
        ),
        f"**Direct prerequisites:** {prereqs}",
        "",
        "## How to use this offline lesson",
        "",
        BOUNDARY,
        "",
        (
            f"Open the [starter](../lessons/{key}.dax). Compare the [named "
            f"reference](../solutions/{key}_reference.dax) and "
            f"[reasoning](../solutions/{key}_solutions.md) when ready. The "
            f"[model specification](../models/{spec['model']}/model.json) "
            f"identifies every fixture table, column type, key and relationship. "
            f"The [fixture handbook](../models/README.md) displays the original "
            f"data and explains each table grain."
        ),
        "",
        "## The question and the mechanism",
        "",
        spec["outcome"],
        "",
        spec["mechanism"],
        "",
        "## Vocabulary and expression anatomy",
        "",
        spec["anatomy"],
        "",
        "Concepts to explain in your own words: "
        + ", ".join(f"**{x}**" for x in spec["concepts"])
        + ".",
        "",
        "## Model and context contract",
        "",
        (
            "The ordinary star follows Product → Sales, Customer → "
            "Sales and Date → Sales through OrderDate. The ShipDate "
            "relationship is inactive unless a case explicitly "
            "activates it. Filters flow from the one side to the many "
            "side. Additional analytical tables have only the "
            "relationships declared in their named model; a similar "
            "column name does not create a relationship."
        ),
        "",
        (
            "```text\nProduct (one)  --> Sales (many) <-- Customer "
            "(one)\n                       ^\n                       | "
            "active OrderDate\n                    Date (one)\n          "
            "             | inactive ShipDate\n                       "
            "+------> Sales\n```"
        ),
        "",
        (
            "All amounts in ordinary Sales are USD after the line "
            "discount, before tax and returns. The Date fixture is "
            "complete for 2024 and 2025; a short result table is a "
            "selected slice, not the whole calendar. JSON `null` in "
            "the worked-results sidecar means DAX BLANK, not the text "
            '"null".'
        ),
        "",
        "## Worked cases",
        "",
    ]
    if spec.get("feature"):
        content += ["### Feature and version boundary", "", spec["feature"], ""]
    ref = reference_source(spec)
    declarations = ref.split("// " + key + "-a:", 1)[0]
    declarations = "\n".join(
        line for line in declarations.splitlines() if not line.startswith("//")
    ).strip()
    if declarations:
        content += [
            (
                "The following query-local declarations are shared by "
                "these cases. They do not create persisted measures in "
                "this classroom."
            ),
            "",
            "```dax",
            declarations,
            "```",
            "",
        ]
    for index, case in enumerate(spec["cases"], 1):
        content += [
            f"### Case {chr(64 + index)}: {case['title']}",
            "",
            f"**Starting context:** {case['context']}",
            "",
            "```dax",
            case["query"],
            "```",
            "",
            "**Context trace:**",
            "",
        ]
        content += [f"{n}. {step}" for n, step in enumerate(case["trace"], 1)]
        content += [
            "",
            "**Hand-derived worked-reference result:**",
            "",
            table(case),
            "",
            case["explanation"],
            "",
            case["note"],
            "",
        ]
    if spec["extra"]:
        content += ["## A deeper model or scope review", "", spec["extra"], ""]
    content += [
        "## Practice: prediction, construction and diagnosis",
        "",
        (
            "Retain your formula or written reasoning, the stated "
            "context, contributing rows or values, and a conclusion "
            "with its unit. This is a manual learning record, not an "
            "execution receipt."
        ),
        "",
    ]
    labels = [
        "Predict",
        "Change one condition",
        "Construct",
        "Diagnose",
        "Check a boundary",
        "Transfer",
    ]
    for index, practice in enumerate(spec["practice"], 1):
        content += [f"### Exercise {index}: {labels[index - 1]}", "", practice["question"], ""]
    content += ["## Progressive hints", ""]
    content += [f"{index}. {item['hint']}" for index, item in enumerate(spec["practice"], 1)]
    content += [
        "",
        "## Self-check and next step",
        "",
        (
            "Explain one changed result without quoting the formula "
            "alone. Identify which rows, filters, relationship or "
            "evaluation scope changed, then construct a counterexample "
            "to a plausible wrong interpretation. Keep your draft "
            "separate from the supplied reference. A small correct "
            "derivation does not certify performance, model security "
            "or broad expertise."
        ),
        "",
    ]
    if spec["number"] < 60:
        next_id = f"dax-{spec['number'] + 1:03d}"
        content += [
            (
                f"Continue to [{next_id}]({next_id}.md) when its prerequisites make "
                f"sense, or revisit this stage from the [course map](../README.md)."
            ),
            "",
        ]
    else:
        content += [
            (
                "Use the [course map](../README.md) to revisit a mechanism "
                "or extend one of the completed capstones."
            ),
            "",
        ]
    content += ["## Official references and evidence limits", ""]
    content += [
        f"- [Official documentation {i}]({url})" for i, url in enumerate(spec["sources"], 1)
    ]
    content += [
        "",
        (
            "Documentation was reviewed for this original course on "
            "2026-10-25. Version-sensitive features have explicit "
            "notes. Source/model checks and independent fixture "
            "arithmetic are not a DAX parser, compiler, semantic "
            "engine, real RLS test or performance measurement."
        ),
        "",
        "## Ask an AI tutor about this lesson",
        "",
        "```text",
        f"Use $guide-ds60sqlpy-learning for {key}. Read its guide and the named model.",
        ("Review my draft and prediction. Ask me to enumerate the relevant rows and context."),
        ("Give one progressive hint before reference comparison unless I request the answer."),
        ("This is offline DAX study: do not claim to execute or compile my draft, connect to"),
        ("Power BI, invent runtime results, or mark mastery from a matching source string."),
        ("Explain the difference between my edited source and the hand-derived reference table."),
        "```",
        "",
    ]
    return "\n".join(content)


def solution(spec):
    key = spec["id"]
    content = [
        f"# {key}: explained reference and practice reasoning",
        "",
        BOUNDARY,
        "",
        (
            f"The complete [reference source]({key}_reference.dax) and [named "
            f"model](../models/{spec['model']}/model.json) belong together. The "
            f"reference-results sidecar binds both exact files by SHA-256. Those "
            f"hashes identify bytes; they do not certify DAX execution."
        ),
        "",
        "## Worked-case reconciliation",
        "",
    ]
    for i, case in enumerate(spec["cases"], 1):
        content += [
            f"### Case {chr(64 + i)}: {case['title']}",
            "",
            case["context"],
            "",
            table(case),
            "",
            case["explanation"],
            "",
        ]
        content += [f"- {step}" for step in case["trace"]] + [""]
    content += ["## Explained practice answers", ""]
    for i, item in enumerate(spec["practice"], 1):
        content += [f"### Exercise {i}", "", item["question"], "", item["answer"], ""]
    content += [
        "## Review the boundary",
        "",
        (
            "A sound answer can use a different readable expression if "
            "its population, context and units agree. Compare "
            "counterexamples as well as ordinary rows. Where an "
            "engine, model role or newer feature is assumed, record "
            "that assumption separately from the offline calculation. "
            "Never reuse a supplied table as evidence that an edited "
            "formula ran."
        ),
        "",
    ]
    return "\n".join(content)


def artifacts():
    lessons = all_lessons()
    files = model_artifacts()
    plans = []
    admitted = []
    records = []
    for spec in lessons:
        key = spec["id"]
        reference = reference_source(spec)
        model_path = f"courses/dax/models/{spec['model']}/model.json"
        ref_path = f"courses/dax/solutions/{key}_reference.dax"
        files[ref_path] = reference
        files[f"courses/dax/lessons/{key}.dax"] = starter_source(spec)
        files[f"courses/dax/guides/{key}.md"] = guide(spec)
        files[f"courses/dax/solutions/{key}_solutions.md"] = solution(spec)
        plans.append(
            {
                "id": key,
                "title": spec["title"],
                "level": "beginner"
                if spec["stage"] <= 2
                else "intermediate"
                if spec["stage"] <= 6
                else "advanced",
                "minutes": 90 if spec["stage"] <= 2 else 120 if spec["stage"] <= 6 else 150,
                "prerequisites": spec["prerequisites"],
                "runtime": "dax-offline",
                "concepts": spec["concepts"],
                "outcome": spec["outcome"],
                "lab": spec["practice"][2]["question"],
                "verification": (
                    "Compare a written context trace with the named "
                    "hand-derived reference; no execution or automatic "
                    "correctness claim."
                ),
            }
        )
        admitted.append(
            {
                "id": key,
                "status": "authored",
                "language": "dax",
                "runtime_profile": "dax-offline",
                "guide_path": f"courses/dax/guides/{key}.md",
                "source_path": f"courses/dax/lessons/{key}.dax",
                "solution_paths": [ref_path, f"courses/dax/solutions/{key}_solutions.md"],
                "verification_id": None,
            }
        )
        record = {
            "lesson_id": key,
            "reference_path": ref_path,
            "source_sha256": hashlib.sha256(reference.encode()).hexdigest(),
            "model_path": model_path,
            "model_sha256": hashlib.sha256(files[model_path].encode()).hexdigest(),
            "evidence": "hand-derived",
            "cases": [],
        }
        for index, case in enumerate(spec["cases"], 1):
            record["cases"].append(
                {
                    "id": f"{key}-{chr(96 + index)}",
                    **{
                        name: case[name]
                        for name in ["title", "context", "trace", "columns", "rows", "note"]
                    },
                }
            )
        records.append(record)
    files["courses/dax/track.json"] = dump(
        {
            "schema_version": 1,
            "id": "dax",
            "title": "DAX: semantic models, context and analytical reasoning",
            "summary": (
                "60 offline coding lessons from table grain to context, "
                "analytical models, reusable logic, security and delivery. "
                "Edit and compare DAX with named hand-derived references; "
                "no engine, compiler or account is required."
            ),
            "lessons": plans,
        }
    )
    files["courses/dax/lessons.json"] = dump(
        {"schema_version": 1, "track_id": "dax", "lessons": admitted}
    )
    files["courses/dax/reference-results.json"] = dump(
        {"schema_version": 1, "track_id": "dax", "lessons": records}
    )
    files["courses/dax/README.md"] = course_readme(lessons)
    files["courses/dax/models/README.md"] = model_handbook(files)
    return files


def course_readme(lessons):
    text = [
        "# DAX: semantic models, context and analytical reasoning",
        "",
        (
            "This 60-lesson course teaches DAX through original small "
            "models, editable source, worked-result tables and "
            "explicit context traces. Start with table grain and basic "
            "arithmetic; the later stages examine time intelligence, "
            "cohorts, reusable expressions, model security and "
            "delivery."
        ),
        "",
        "## Open the classroom",
        "",
        "From the repository root, run:",
        "",
        "```bash",
        "./classroom",
        "```",
        "",
        (
            "Choose **DAX** in the classroom directory. Docker serves "
            "the reading and saved-work interface; this subject does "
            "not need a worker image, NVIDIA hardware, Power BI "
            "installation, account or connection. See the [main setup "
            "guide](../../README.md) for Docker and WSL 2 installation."
        ),
        "",
        "## Editing and evidence",
        "",
        BOUNDARY,
        "",
        (
            "Read the guide beside its editable `.dax` starter. Save a "
            "draft and notes, compare the supplied reference when "
            "useful, and export source for your own records. A "
            "worked-reference table stays tied to its named reference "
            "and model even after you edit your draft. It is not a Run "
            "result. Completion records study progress, not verified "
            "mastery."
        ),
        "",
        (
            "The [fixture handbook](models/README.md) exposes the tiny "
            "original CSVs. The [reference-results "
            "sidecar](reference-results.json) identifies every case "
            "and binds the exact reference and model bytes with "
            "SHA-256. No checked-in file is evidence that a DAX "
            "engine, model role or external service was executed."
        ),
        "",
        "## Course map",
        "",
        (
            "Prerequisites are direct concept dependencies, not a "
            "requirement to finish every earlier row. Revisit the "
            "named prerequisites when an expression's context is "
            "unclear."
        ),
        "",
    ]
    for stage, title in enumerate(STAGES, 1):
        text += [f"### Stage {stage}: {title}", "", "| Lesson | Outcome |", "| --- | --- |"]
        text += [
            f"| [{s['id']}: {s['title']}](guides/{s['id']}.md) | {s['outcome']} |"
            for s in lessons
            if s["stage"] == stage
        ]
        text += [""]
    text += [
        "## Platform and feature boundaries",
        "",
        (
            "Ordinary DAX syntax, model definitions, calculation-item "
            "definitions, user-defined functions and visual "
            "calculations are different artifacts. Guides state their "
            "scope instead of treating every expression as an "
            "interchangeable query. Version-sensitive features have "
            "dated notes and primary references. Calendar-based time "
            "intelligence and value-filter behavior are marked "
            "according to their reviewed documentation; the UDF "
            "lessons state their compatibility requirement."
        ),
        "",
        (
            "Security cases are expectations under specified synthetic "
            "role policies. Timing cases explicitly use supplied "
            "scenario numbers. Neither is a real security or "
            "performance test. Optional external model validation "
            "requires a compatible engine, a deliberately prepared "
            "model and its own observed evidence; it is not required "
            "to complete this offline route."
        ),
        "",
        (
            "For SQL table/query foundations, use the classroom's SQL "
            "subject. For data analysis, probability and model "
            "evaluation, use Python, R and the statistics tutorial. "
            "Their executable outputs do not turn an unrelated DAX "
            "draft into an executed program."
        ),
        "",
        "## Maintaining this course",
        "",
        (
            "Read [AGENTS.md](AGENTS.md) and the [authoring "
            "contract](authoring/README.md). The course generator owns "
            "its manifests, guides, references, starters and fixture "
            "handbook. Shared HTML readers are generated separately by "
            "the repository tools."
        ),
        "",
    ]
    return "\n".join(text)


def model_handbook(files):
    text = [
        "# Original DAX model fixtures",
        "",
        (
            "These small data sets are invented for this course. They "
            "describe a model contract for hand reasoning; opening a "
            "CSV or JSON file does not install a semantic model. Every "
            "named reference states which model and context it assumes."
        ),
        "",
        "## Retail grain and units",
        "",
        (
            "A Sales row is an order line, not an order or customer. "
            "NetAmount is quantity times unit price minus a line "
            "discount, in USD before tax and returns. Order 101 has "
            "two lines. Product and Customer keys are unique; Bag and "
            "Di intentionally have no sales. The Date table contains "
            "every day in 2024 and 2025, including leap day."
        ),
        "",
        (
            "Active one-to-many filters flow from Product, Customer "
            "and Date to Sales through OrderDate. The alternative "
            "Date-to-ShipDate relationship is inactive. Additional "
            "relationships below are explicit; matching names alone "
            "never create a join or filter path."
        ),
        "",
    ]
    seen = set()
    for model_id in ["retail", "unknown-member", "analytics"]:
        model = json.loads(files[f"courses/dax/models/{model_id}/model.json"])
        text += [
            f"## {model['title']}",
            "",
            f"[Typed specification]({model_id}/model.json)",
            "",
            model["description"],
            "",
        ]
        text += [f"- {item}" for item in model["assumptions"]] + [""]
        for tab in model["tables"]:
            if tab["path"] in seen:
                continue
            seen.add(tab["path"])
            rows = list(csv.reader(io.StringIO(files[tab["path"]])))
            head, body = rows[0], rows[1:]
            text += [
                f"### {tab['name']} ({model_id})",
                "",
                (
                    f"**Grain:** {tab['grain']}. **Key:** {', '.join(tab['key'])}. "
                    f"**Rows:** {tab['row_count']}."
                ),
                "",
                f"[Complete CSV]({Path(tab['path']).relative_to('courses/dax/models').as_posix()})",
                "",
                "Types: " + ", ".join(f"`{c['name']}` ({c['type']})" for c in tab["columns"]) + ".",
                "",
            ]
            if len(body) > 20:
                selected = {
                    "2024-01-01",
                    "2024-02-29",
                    "2024-12-31",
                    "2025-01-02",
                    "2025-02-01",
                    "2025-06-30",
                    "2025-07-01",
                    "2025-12-31",
                }
                body = [row for row in body if row[0] in selected]
                text += [
                    (
                        "The following is an explicitly selected calendar slice. "
                        "Use the complete CSV for all dates; absent rows in this "
                        "display are not missing model dates."
                    ),
                    "",
                ]
            text += ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
            text += ["| " + " | ".join(row) + " |" for row in body] + [""]
        text += [
            "### Declared relationship paths",
            "",
            "| One side | Many side | Active | Direction |",
            "| --- | --- | --- | --- |",
        ]
        text += [
            (
                f"| {r['from_table']}[{r['from_column']}] | "
                f"{r['to_table']}[{r['to_column']}] | {r['active']} | One to many |"
            )
            for r in model["relationships"]
        ] + [""]
    text += [
        "## Analytical conventions",
        "",
        (
            "Budget is monthly by category and disconnected, so "
            "formulas transfer matching month/category keys "
            "deliberately. Refunds are attributed to the original sale "
            "date, since this fixture does not provide return-event "
            "dates. Inventory is a balance at a snapshot, not an "
            "additive monthly flow. ForeignSales and ExchangeRate use "
            "a unique date/currency conversion key; mixed local "
            "currencies cannot be summed as if they shared one unit."
        ),
        "",
        (
            "Cohort membership and activity are separate, with "
            "observation ending on 2025-02-28. A future unobserved "
            "period is BLANK rather than an observed zero. "
            "Experimental assignments are the unit of analysis; "
            "repeated exposures are events, not additional independent "
            "units. Supplied Wilson intervals are marginal descriptive "
            "uncertainty summaries, not a treatment-effect interval or "
            "causal proof."
        ),
        "",
        (
            "The Access table contains synthetic `.test` principals. "
            "Its policy metadata states intended role behavior without "
            "installing or testing any security. Protecting the "
            "mapping itself is an additional real-model concern. The "
            "unknown-member model deliberately adds one unmatched "
            "ProductKey 999; the clean model does not contain that "
            "defect."
        ),
        "",
    ]
    return "\n".join(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    lessons = all_lessons()
    if len(lessons) != 60 or [x["number"] for x in lessons] != list(range(1, 61)):
        parser.error("The complete 60-lesson route is required before publishing manifests.")
    changed = []
    for name, text in artifacts().items():
        path = ROOT / name
        if not path.exists() or path.read_text("utf-8") != text:
            changed.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    print(
        f"DAX authoring: {len(lessons)} lessons; {len(changed)} "
        + ("drifted files" if args.check else "files updated")
    )
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
