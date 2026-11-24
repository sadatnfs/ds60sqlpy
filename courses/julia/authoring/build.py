#!/usr/bin/env python3
"""Publish complete Julia teaching artifacts without running Julia or learner code."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE = Path("courses/julia")
HERE = ROOT / BASE / "authoring"

# Literal values and calls belong in inline code; these shapes are what remains
# when a code span is stripped together with its leading space ("is[2,3]",
# "a2-by -3", "UTF -8").
GLUED_PROSE = re.compile(
    r"[A-Za-z]\[|UTF -\d|\ba\d-by|\d-by -\d"
    r"|\b(?:is|are|at|on|for|along|becomes|gives|plus|and|to)[\[(:]"
)


def prose_defects(text: str) -> list[str]:
    """Return glued code fragments outside fences, inline code and TeX math."""
    prose = re.sub(r"```.*?```", " ", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", " ", prose, flags=re.S)
    return [match.group(0) for match in GLUED_PROSE.finditer(prose)]


def unit_prose(row: dict[str, Any]) -> list[str]:
    fields = [row["title"], row["outcome"]]
    for term, definition in row["key_terms"]:
        fields += [term, definition]
    fields.append(row["approach"])
    if row.get("checks_note"):
        fields.append(row["checks_note"])
    for item in row["exercises"]:
        fields += [
            item[key]
            for key in ("title", "task", "expected", "hint", "answer", "why", "wrong", "verify")
        ]
    return fields


MIN_SOLUTION_WORDS = 700
REASONING_FIELDS = {"why": 12, "wrong": 12, "verify": 6}


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def check_reasoning(row: dict[str, Any]) -> None:
    """Require a unit approach plus why, wrong-approach and verify notes per exercise."""
    key = f"julia-{row['number']:03}"
    if words(row.get("approach", "")) < 35:
        raise ValueError(f"{key} needs an approach paragraph of at least 35 words")
    texts = [row["approach"]]
    for index, item in enumerate(row["exercises"], 1):
        for name, minimum in REASONING_FIELDS.items():
            if words(item.get(name, "")) < minimum:
                raise ValueError(f"{key} exercise {index} needs {name} of {minimum}+ words")
            texts.append(item[name])
    if "checks_note" in row:
        if words(row["checks_note"]) < 30:
            raise ValueError(f"{key} checks_note needs 30+ words when present")
        texts.append(row["checks_note"])
    wrong = [item["wrong"] for item in row["exercises"]]
    if len(set(wrong)) != len(wrong):
        raise ValueError(f"{key} wrong-approach notes must be distinct")
    if any(dash in text for text in texts for dash in ("\u2013", "\u2014")):
        raise ValueError(f"{key} solution reasoning contains an en or em dash")


def exercise_checks(source: str, key: str) -> str:
    """Return the reference's exercise_checks function for display in the solution."""
    match = re.search(r"^function exercise_checks\(\)\n.*?^end\n", source, re.S | re.M)
    if not match:
        raise ValueError(f"{key} reference needs a top-level exercise_checks function")
    return match.group(0)


def check_key_terms(row: dict[str, Any]) -> None:
    """Require three to five distinct, defined, lesson-specific vocabulary entries."""
    key = f"julia-{row['number']:03}"
    pairs = row.get("key_terms", [])
    names = [pair[0].lower() for pair in pairs]
    if not 3 <= len(names) <= 5 or len(set(names)) != len(names):
        raise ValueError(f"{key} needs three to five distinct key terms")
    for pair in pairs:
        if len(pair) != 2:
            raise ValueError(f"{key} key terms must be [term, definition] pairs")
        term, definition = pair
        if not term.strip() or any(mark in term for mark in ("*", ":", "\n")):
            raise ValueError(f"{key} has an invalid key term name {term!r}")
        if len(definition.split()) < 6 or not definition.endswith("."):
            raise ValueError(f"{key} key term {term!r} needs a one-sentence definition")
        if any(dash in term + definition for dash in ("\u2013", "\u2014")):
            raise ValueError(f"{key} key term {term!r} contains an en or em dash")


def units() -> list[dict[str, Any]]:
    rows = [json.loads(p.read_text("utf-8")) for p in sorted(HERE.glob("unit-*.json"))]
    if [r["number"] for r in rows] != list(range(1, 33)):
        raise ValueError("Publish only the complete 32-unit Julia route")
    for row in rows:
        if (
            row["level"] not in {"beginner", "intermediate", "advanced"}
            or len(row["exercises"]) != 6
        ):
            raise ValueError("Invalid teaching stage or practice contract")
        check_key_terms(row)
        check_reasoning(row)
        body = (HERE / "chapters" / f"julia-{row['number']:03}.md").read_text("utf-8")
        if len(re.findall(r"\b\w+\b", body)) < 450:
            raise ValueError("Chapter needs a substantive original explanation")
        for marker in ("{{WORKED_A}}", "{{WORKED_B}}"):
            if body.count(marker) != 1:
                raise ValueError("Two complete worked programs are required")
        defects = prose_defects(body) + [
            fragment for text in unit_prose(row) for fragment in prose_defects(text)
        ]
        if defects:
            raise ValueError(
                f"julia-{row['number']:03} has code glued into prose; use inline code: "
                + ", ".join(sorted(set(defects)))
            )
    return rows


def artifacts() -> dict[str, str]:
    output: dict[str, str] = {}
    plans = []
    manifest = []
    contracts = []
    figures = []
    readme = [
        "# Julia language and scientific computing\n",
        (
            "A complete 32-unit progression from first scripts to "
            "numerical work, data contracts, generic functions, "
            "concurrency and reproducible scientific analysis. The "
            "classroom uses the prepared Linux Julia profile, with no "
            "package downloads during a lesson.\n"
        ),
        (
            "Start with the [main classroom "
            "instructions](../../README.md). Julia source is staged as "
            "`main.jl` in a fresh process with two Julia threads, a fixed "
            "read-only package environment, no startup file and offline "
            "package settings. The classroom saves your code, notes and run "
            "output; scratch files disappear after the run. Optional projects "
            "and unfamiliar external ecosystems need their own preparation.\n"
        ),
        "| Unit | Stage | Topic |\n| --- | --- | --- |",
    ]
    for row in units():
        key = f"julia-{row['number']:03}"
        prefix = BASE.as_posix()
        code = {
            kind: (HERE / "programs" / f"{key}_{kind}.jl").read_text("utf-8")
            for kind in ("learner", "reference", "worked_a", "worked_b")
        }
        if any(len(text.encode()) > 48000 for text in code.values()):
            raise ValueError("Source exceeds the classroom admission limit")
        guide = (
            (HERE / "chapters" / f"{key}.md")
            .read_text("utf-8")
            .replace("](../../../", "](../../")
            .replace("{{WORKED_A}}", "```julia\n" + code["worked_a"] + "```")
            .replace("{{WORKED_B}}", "```julia\n" + code["worked_b"] + "```")
        )
        prereqs = (
            ", ".join("`" + p + "`" for p in row["prerequisites"]) or "No previous Julia experience"
        )
        body = (HERE / "chapters" / f"{key}.md").read_text("utf-8")
        cases = dict(re.findall(r"^#{2,3} Worked case ([AB]): (.+)$", body, re.M))
        if set(cases) != {"A", "B"}:
            raise ValueError(f"{key} needs titled worked cases A and B")
        figure_note = (
            " One program in this unit publishes a bounded Plotly figure with its "
            "description and exact table."
            if row.get("figure")
            else ""
        )
        intro = (
            f"# {key}: {row['title']}\n\n## Starting point and outcome\n\n"
            f"{row['level'].title()}; approximately {row['minutes']} minutes. "
            f"Direct prerequisites: {prereqs}.\n\n{row['outcome']}\n\n"
            f"## Classroom execution\n\nOpen `{key}` in `/classroom` with its prepared "
            f"`julia` runtime. Worked case A ({cases['A']}) and worked case B "
            f"({cases['B']}) are complete programs: save your current pad, paste one of "
            "them and press Run. The learner file contains the six investigations below; "
            f"the explained reference ends by printing `{key}: all reference checks passed`."
            f"{figure_note} The [course overview](../README.md) describes the shared "
            "runtime: a fresh offline `main.jl` process with two threads and a fixed "
            "package environment.\n\n"
        )
        intro += (
            "## Key terms\n\n"
            + "\n".join(f"- **{term}:** {definition}" for term, definition in row["key_terms"])
            + "\n\n"
        )
        guide = intro + guide + "\n\n## Six investigations\n\n"
        explanation = [
            f"# {key}: explained reference\n\n"
            f"The executable reference is `{key}_reference.jl`. "
            "Its checks cover the stated authored inputs; they are not a claim "
            "of general scientific validity or mastery.\n\n"
            f"## Approach\n\n{row['approach']}\n"
        ]
        for index, item in enumerate(row["exercises"], 1):
            guide += (
                f"### {index}. {item['title']}\n\n{item['task']}\n\n"
                f"**Expected:** {item['expected']}\n\n**Hint:** {item['hint']}\n\n"
            )
            explanation.append(
                f"## {index}. {item['title']}\n\n{item['answer']}\n\n"
                f"**Expected observation:** {item['expected']}\n\n"
                f"**Why it holds here:** {item['why']}\n\n"
                f"**Plausible wrong approach:** {item['wrong']}\n\n"
                f"**How to verify:** {item['verify']}\n"
            )
        concepts = row["concepts"]
        concept_phrase = (
            ", ".join(concepts[:-1]) + " or " + concepts[-1] if len(concepts) > 1 else concepts[0]
        )
        guide += (
            "## Primary references\n\n"
            + "\n".join(f"- [{title}]({url})" for title, url in row["sources"])
            + (
                "\n\n## Study companion\n\nA repository-aware assistant with the "
                f"learning-companion skill can review `{key}` with you. Give it your "
                "prediction for one investigation, your source and the actual output, "
                "and ask it to find the first incorrect assumption about "
                f"{concept_phrase}.\n"
            )
        )
        output[f"{prefix}/guides/{key}.md"] = guide
        output[f"{prefix}/lessons/{key}.jl"] = code["learner"]
        output[f"{prefix}/solutions/{key}_reference.jl"] = code["reference"]
        explanation.append(
            "## Reference checks\n\nThe reference's `exercise_checks` function runs these "
            f"assertions before `main` prints `{key}: all reference checks passed`:\n\n"
            + (f"{row['checks_note']}\n\n" if row.get("checks_note") else "")
            + "```julia\n"
            + exercise_checks(code["reference"], key)
            + "```\n"
        )
        solution = "\n".join(explanation)
        if words(solution) < MIN_SOLUTION_WORDS:
            raise ValueError(f"{key} explained reference has {words(solution)} words; needs 700")
        output[f"{prefix}/solutions/{key}_solutions.md"] = solution
        # Plain-text metadata: show concrete expected observations without Markdown.
        concrete = [
            item["expected"] for item in row["exercises"] if re.search(r"[0-9`]", item["expected"])
        ] or [row["exercises"][0]["expected"]]
        plans.append(
            {
                k: row[k]
                for k in ("title", "level", "minutes", "prerequisites", "concepts", "outcome")
            }
            | {
                "id": key,
                "runtime": "julia",
                "lab": row["exercises"][0]["task"].replace("`", ""),
                "verification": (
                    "Reproduce the stated observations, for example: "
                    + " ".join(concrete[:2]).replace("`", "")
                ),
            }
        )
        manifest.append(
            {
                "id": key,
                "status": "authored",
                "language": "julia",
                "runtime_profile": "julia",
                "guide_path": f"{prefix}/guides/{key}.md",
                "source_path": f"{prefix}/lessons/{key}.jl",
                "solution_paths": [
                    f"{prefix}/solutions/{key}_reference.jl",
                    f"{prefix}/solutions/{key}_solutions.md",
                ],
                "verification_id": None,
            }
        )
        contracts.append(
            {
                "id": key,
                "profile": "julia",
                "reference": f"{prefix}/solutions/{key}_reference.jl",
                "source_sha256": hashlib.sha256(code["reference"].encode()).hexdigest(),
                "expected_output": key + ": all reference checks passed",
            }
        )
        if row.get("figure"):
            figures.append(
                {
                    "id": key,
                    "kind": "plotly",
                    "count": row["figure"],
                    "description_required": True,
                    "table_required": True,
                }
            )
        readme.append(f"| [{key}](guides/{key}.md) | {row['level']} | {row['title']} |")
    output[str(BASE / "track.json")] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": "julia",
                "title": "Julia language and scientific computing",
                "summary": (
                    "Julia from first scripts and data types to multiple "
                    "dispatch, data workflows, numerical methods, optimization, "
                    "performance and concurrent scientific programs, with offline"
                    " executable examples."
                ),
                "lessons": plans,
            },
            indent=2,
        )
        + "\n"
    )
    output[str(BASE / "lessons.json")] = (
        json.dumps({"schema_version": 1, "track_id": "julia", "lessons": manifest}, indent=2) + "\n"
    )
    output[str(BASE / "fixtures/reference-contracts.json")] = (
        json.dumps({"schema_version": 1, "references": contracts}, indent=2) + "\n"
    )
    output[str(BASE / "figure-contracts.json")] = (
        json.dumps({"schema_version": 1, "units": figures}, indent=2) + "\n"
    )
    output[str(BASE / "README.md")] = "\n".join(readme) + (
        "\n\n## Prepared environment and boundaries\n\nThe Julia profile "
        "uses a locked project containing CSV, DataFrames, "
        "Distributions, ForwardDiff, Optim and JSON3. The "
        "classroom-specific `DS60Plots` helper writes bounded Plotly "
        "figures for browser display; it is not a standard Julia "
        "plotting package. Standard libraries support tests, dates, "
        "Unicode, arrays and linear algebra. GPU packages, "
        "distributed clusters and external services are separate "
        "optional projects. A successful source run does not "
        "establish numerical conditioning, statistical validity or "
        "universal performance; keep an observed run separate from a "
        "timing claim, an inferred mathematical result or an external "
        "deployment. Each guide ends with an optional study-companion "
        "prompt for a repository-aware assistant; the guides are complete "
        "without it. See [authoring](authoring/README.md) "
        "for maintained source and checks.\n"
    )
    for name, text in output.items():
        if "\u2014" in text:
            raise ValueError("Do not publish em dashes: " + name)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    different = []
    for name, text in artifacts().items():
        path = ROOT / name
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != text:
                different.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if different:
        print("\n".join(different))
        return 1
    print("Julia authoring checked" if args.check else "Julia course generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
