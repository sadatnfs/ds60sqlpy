#!/usr/bin/env python3
"""Build the complete, offline LLM evaluation course from maintained source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import fill
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE = Path("courses/llm-evaluation")
HERE = ROOT / BASE / "authoring"


def specifications() -> list[dict[str, Any]]:
    rows = [json.loads(p.read_text("utf-8")) for p in sorted(HERE.glob("unit-*.json"))]
    if [r["number"] for r in rows] != list(range(1, 25)):
        raise ValueError("Publish only the complete 24-unit route.")
    for row in rows:
        if row["level"] not in {"beginner", "intermediate", "advanced"}:
            raise ValueError("Unknown stage")
        if row["runtime"] not in {"python-core", "llm-torch-cpu"}:
            raise ValueError("Unprepared execution profile")
        if len(row["exercises"]) != 6 or len({e["title"] for e in row["exercises"]}) != 6:
            raise ValueError("Six distinct practice tasks are required.")
        for task in row["exercises"]:
            if set(task) != {"title", "task", "expected", "hint", "answer"} or not all(
                task.values()
            ):
                raise ValueError("Practice needs task, expected observation, hint and explanation.")
        body = (HERE / "chapters" / f"eval-{row['number']:03}.md").read_text("utf-8")
        if body.count("{{WORKED_A}}") != 1 or body.count("{{WORKED_B}}") != 1:
            raise ValueError("Each chapter needs two complete worked programs.")
        if len(re.findall(r"\b\w+\b", body)) < 450:
            raise ValueError("A chapter needs a substantive original explanation.")
    return rows


def format_programs(programs: dict[str, str]) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="ds60-evaluation-format-") as temporary:
        staging = Path(temporary)
        for name, source in programs.items():
            compile(source, name, "exec")
            (staging / name).write_text(source, encoding="utf-8", newline="\n")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--no-cache",
                "--config",
                str(ROOT / "pyproject.toml"),
                str(staging),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=90,
        )
        if completed.returncode:
            raise ValueError(completed.stdout + completed.stderr)
        return {name: (staging / name).read_text("utf-8") for name in programs}


def artifacts() -> dict[str, str]:
    rows = specifications()
    programs: dict[str, str] = {}
    for row in rows:
        key = f"eval-{row['number']:03}"
        source = (HERE / "programs" / f"{key}.py").read_text("utf-8")
        parts = re.split(
            r"^# === (?:EXAMPLE A|EXAMPLE B|EXERCISES|MAIN) ===\s*$", source, flags=re.MULTILINE
        )
        if len(parts) != 5:
            raise ValueError(f"{key} program sections are incomplete")
        core, a, b, exercises, main = parts
        programs[key + "_reference.py"] = source
        plot_path = HERE / "programs" / f"{key}_plotly.py.in"
        if plot_path.is_file():
            programs[key + "_plotly_reference.py"] = source + "\n" + plot_path.read_text("utf-8")
            programs[key + "_plotly_learner.py"] = core + "\n" + plot_path.read_text("utf-8")
        programs[key + "_worked_a.py"] = core + a + "\nworked_a()\n"
        programs[key + "_worked_b.py"] = core + b + "\nworked_b()\n"
        tasks = "\n".join(
            fill(f"# Task {n}: {e['task']}", width=88, subsequent_indent="# ")
            for n, e in enumerate(row["exercises"], 1)
        )
        programs[key + "_learner.py"] = (
            core + a + "\nworked_a()\n\n" + tasks + "\n\n# Implement your six changes below.\n"
        )
    formatted = format_programs(programs)
    output: dict[str, str] = {}
    plan = []
    admitted = []
    checks = []
    readme = [
        "# LLM evaluation and alignment\n",
        (
            "A 24-unit course in scientific evaluation and bounded "
            "alignment mechanisms. The route uses authored synthetic "
            "research-support records, not outputs from a pretrained "
            "model. Python Core runs the statistical and finite-policy "
            "examples; two units perform actual small CPU PyTorch "
            "optimization. No model, dataset, account or service is "
            "fetched by opening or running a lesson.\n"
        ),
        (
            "Start with the [main classroom "
            "instructions](../../README.md). Existing [LLM "
            "mechanisms](../llm-theory/README.md), [applied "
            "systems](../llm-applied/README.md), [NLP](../nlp/README.md) "
            "and the [statistics book](../statistics-ml/README.md) "
            "provide the direct prerequisites.\n"
        ),
        "| Unit | Stage | Topic | Runtime |\n| --- | --- | --- | --- |",
    ]
    for row in rows:
        key = f"eval-{row['number']:03}"
        prefix = BASE.as_posix()
        source = formatted[key + "_reference.py"]
        guide = (HERE / "chapters" / f"{key}.md").read_text("utf-8")
        guide = guide.replace(
            "{{WORKED_A}}", "```python\n" + formatted[key + "_worked_a.py"] + "```"
        ).replace("{{WORKED_B}}", "```python\n" + formatted[key + "_worked_b.py"] + "```")
        intro = (
            f"# {key}: {row['title']}\n\n## Starting point and outcome\n\n"
            f"{row['level'].title()}; approximately {row['minutes']} minutes. "
            + "Direct prerequisites: "
            + ", ".join("`" + p + "`" for p in row["prerequisites"])
            + ".\n\n"
            + row["outcome"]
            + "\n\n## Classroom execution\n\n"
            + (
                f"Choose **LLM evaluation and alignment** in `/classroom`, open `{key}`, "
                f"and use its `{row['runtime']}` profile. "
            )
            + (
                "A Run starts a fresh Python process. Both worked programs "
                "below include their own setup and can be copied in full. "
                "Save your draft first. "
            )
            + (
                "The examples use small authored fixtures and explicit "
                "numerical checks. Process success establishes those checks, "
                "not population validity, safety certification or "
                "natural-language competence. "
            )
            + (
                "Code and notes persist; temporary program files do not. No "
                "network call or model download is needed.\n\n"
            )
        )
        guide = intro + guide + "\n\n## Six investigations\n\n"
        explanation = [
            f"# {key}: explained reference\n\n"
            f"The full reference is `{key}_reference.py`. "
            "Its assertions check the specific authored inputs. "
            "Read the assumptions and counterexamples before transferring a result.\n"
        ]
        for n, e in enumerate(row["exercises"], 1):
            guide += (
                f"### {n}. {e['title']}\n\n{e['task']}\n\n"
                f"**Expected:** {e['expected']}\n\n**Hint:** {e['hint']}\n\n"
            )
            explanation.append(
                f"## {n}. {e['title']}\n\n{e['answer']}\n\n"
                f"**Expected observation:** {e['expected']}\n"
            )
        guide += (
            "## Primary references\n\n"
            + "\n".join(f"- [{title}]({url})" for title, url in row["sources"])
            + "\n\n"
        )
        guide += (
            "## Study companion\n\nUse the repository learning-companion "
            "skill with this lesson ID and your own source/output. Ask "
            "for clarification of the estimand, probability distribution,"
            " data split or gradient before a hint. Keep claims about the"
            " authored fixture separate from claims requiring real "
            "population or model evidence.\n"
        )
        has_plot = key + "_plotly_reference.py" in formatted
        if has_plot:
            guide += (
                "\n## Interactive figure variant\n\nSelect **Interactive "
                "Plotly** in the lesson variant control. Its complete program"
                " uses the same authored inputs to draw the corresponding "
                "risk, calibration or policy curve. The captured figure "
                "retains a description and exact data table, and its JSON can"
                " be downloaded. Hovering a point does not create new "
                "statistical evidence. The default numerical reference "
                "remains separately saved.\n"
            )
        output[f"{prefix}/guides/{key}.md"] = guide
        output[f"{prefix}/lessons/{key}.py"] = formatted[key + "_learner.py"]
        output[f"{prefix}/solutions/{key}_reference.py"] = source
        output[f"{prefix}/solutions/{key}_solutions.md"] = "\n".join(explanation)
        plan.append(
            {
                k: row[k]
                for k in ("title", "level", "minutes", "prerequisites", "concepts", "outcome")
            }
            | {
                "id": key,
                "runtime": row["runtime"],
                "lab": row["exercises"][0]["task"],
                "verification": (
                    f"The complete reference prints '{key}: all reference checks passed' "
                    "after numerical and failure-case assertions."
                ),
            }
        )
        admitted.append(
            {
                "id": key,
                "status": "authored",
                "language": "python",
                "runtime_profile": row["runtime"],
                "guide_path": f"{prefix}/guides/{key}.md",
                "source_path": f"{prefix}/lessons/{key}.py",
                "solution_paths": [
                    f"{prefix}/solutions/{key}_reference.py",
                    f"{prefix}/solutions/{key}_solutions.md",
                ],
                "verification_id": None,
            }
        )
        if has_plot:
            output[f"{prefix}/lessons/{key}_plotly.py"] = formatted[key + "_plotly_learner.py"]
            output[f"{prefix}/solutions/{key}_plotly_reference.py"] = formatted[
                key + "_plotly_reference.py"
            ]
            admitted[-1]["variants"] = [
                {
                    "id": "plotly",
                    "title": "Interactive Plotly",
                    "language": "python",
                    "runtime_profile": "python-core",
                    "source_path": f"{prefix}/lessons/{key}_plotly.py",
                    "solution_paths": [
                        f"{prefix}/solutions/{key}_plotly_reference.py",
                        f"{prefix}/solutions/{key}_solutions.md",
                    ],
                    "verification_id": None,
                }
            ]
            checks.append(
                {
                    "id": key + "@plotly",
                    "profile": "python-core",
                    "reference": f"{prefix}/solutions/{key}_plotly_reference.py",
                    "source_sha256": hashlib.sha256(
                        formatted[key + "_plotly_reference.py"].encode()
                    ).hexdigest(),
                    "expected_output": key + " Plotly curve complete",
                    "artifacts": ["plotly"],
                    "evidence": (
                        "authored assertions and a bounded chart, not an independent "
                        "worker verifier"
                    ),
                }
            )
        checks.append(
            {
                "id": key,
                "profile": row["runtime"],
                "reference": f"{prefix}/solutions/{key}_reference.py",
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "expected_output": key + ": all reference checks passed",
                "evidence": "authored assertions, not an independent worker verifier",
            }
        )
        readme.append(
            f"| [{key}](guides/{key}.md) | {row['level']} | {row['title']} | `{row['runtime']}` |"
        )
    output[str(BASE / "track.json")] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": "llm-evaluation",
                "title": "LLM evaluation and alignment",
                "summary": (
                    "Scientific evaluation from task definitions and annotation "
                    "to uncertainty, deployment decisions and preference "
                    "optimization. Includes exact CPU mechanisms and small real "
                    "PyTorch training runs with explicit inference boundaries."
                ),
                "lessons": plan,
            },
            indent=2,
        )
        + "\n"
    )
    output[str(BASE / "lessons.json")] = (
        json.dumps(
            {"schema_version": 1, "track_id": "llm-evaluation", "lessons": admitted}, indent=2
        )
        + "\n"
    )
    output[str(BASE / "fixtures/reference-contracts.json")] = (
        json.dumps({"schema_version": 1, "references": checks}, indent=2) + "\n"
    )
    output[str(BASE / "README.md")] = "\n".join(readme) + (
        "\n\n## Evidence and boundaries\n\nThe corpus is synthetic. "
        "Enumerated finite policies and tiny learned reward/policy "
        "networks make mathematics inspectable; they are not "
        "pretrained assistants. Advanced guides explicitly separate "
        "an objective value, its sampled estimator, its derivative "
        "and the deployment claim. RAG support labels are authored "
        "judgments, not automated proofs of entailment. Statistical "
        "thresholds do not replace access-control or critical-error "
        "gates. See [fixture provenance](fixtures/README.md) and "
        "[authoring](authoring/README.md).\n"
    )
    for name, text in output.items():
        if "\u2014" in text:
            raise ValueError("Do not publish em dashes: " + name)
        if name.endswith(".py") and len(text.encode()) > 48000:
            raise ValueError("Pad exceeds admission bound")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatch = []
    for name, content in artifacts().items():
        path = ROOT / name
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != content:
                mismatch.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if mismatch:
        print("\n".join(mismatch))
        return 1
    print("LLM evaluation authoring checked" if args.check else "LLM evaluation course generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
