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
        body = (HERE / "chapters" / f"julia-{row['number']:03}.md").read_text("utf-8")
        if len(re.findall(r"\b\w+\b", body)) < 450:
            raise ValueError("Chapter needs a substantive original explanation")
        for marker in ("{{WORKED_A}}", "{{WORKED_B}}"):
            if body.count(marker) != 1:
                raise ValueError("Two complete worked programs are required")
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
            "`main.jl` in a fresh process. Code, notes and receipts are "
            "saved by the classroom; scratch files disappear after the "
            "run. Optional projects and unfamiliar external ecosystems "
            "need their own preparation.\n"
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
        intro = (
            f"# {key}: {row['title']}\n\n## Starting point and outcome\n\n"
            f"{row['level'].title()}; approximately {row['minutes']} minutes. "
            f"Direct prerequisites: {prereqs}.\n\n{row['outcome']}\n\n"
            "## Classroom execution\n\nChoose **Julia language and scientific computing** "
            "in `/classroom`, open this unit, and select its prepared `julia` runtime. "
            "The worker starts a fresh `main.jl` process with two Julia threads, "
            "a fixed package environment, no startup file and offline package settings. "
            "Both worked examples are complete under that environment. "
            "Save your current pad before replacing it. "
            "No package, model or dataset is fetched by a lesson.\n\n"
        )
        guide = intro + guide + "\n\n## Six investigations\n\n"
        explanation = [
            f"# {key}: explained reference\n\n"
            f"The executable reference is `{key}_reference.jl`. "
            "Its checks cover the stated authored inputs; they are not a claim "
            "of general scientific validity or mastery.\n"
        ]
        for index, item in enumerate(row["exercises"], 1):
            guide += (
                f"### {index}. {item['title']}\n\n{item['task']}\n\n"
                f"**Expected:** {item['expected']}\n\n**Hint:** {item['hint']}\n\n"
            )
            explanation.append(
                f"## {index}. {item['title']}\n\n{item['answer']}\n\n"
                f"**Expected observation:** {item['expected']}\n"
            )
        guide += (
            "## Primary references\n\n"
            + "\n".join(f"- [{title}]({url})" for title, url in row["sources"])
            + (
                "\n\n## Study companion\n\nUse the repository learning-companion "
                "skill with this lesson ID, your prediction and your actual "
                "source/output. Ask for a diagnosis of the first incorrect "
                "type, shape, state transition or assumption. Keep observed "
                "execution distinct from a timing claim, inferred "
                "mathematical result or external deployment.\n"
            )
        )
        output[f"{prefix}/guides/{key}.md"] = guide
        output[f"{prefix}/lessons/{key}.jl"] = code["learner"]
        output[f"{prefix}/solutions/{key}_reference.jl"] = code["reference"]
        output[f"{prefix}/solutions/{key}_solutions.md"] = "\n".join(explanation)
        plans.append(
            {
                k: row[k]
                for k in ("title", "level", "minutes", "prerequisites", "concepts", "outcome")
            }
            | {
                "id": key,
                "runtime": "julia",
                "lab": row["exercises"][0]["task"],
                "verification": (
                    f"The complete reference prints '{key}: all reference checks passed' "
                    "after its numerical and failure-case checks."
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
        "universal performance. See [authoring](authoring/README.md) "
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
