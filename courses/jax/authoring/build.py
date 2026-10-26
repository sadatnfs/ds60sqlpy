#!/usr/bin/env python3
"""Publish only the complete JAX course; never execute a learner program."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import indent

from model import HEADER, Case, Unit

ROOT = Path(__file__).resolve().parents[3]
BASE = "courses/jax"


def units() -> list[Unit]:
    from advanced import UNITS as advanced
    from composition import UNITS as composition
    from foundation import UNITS as foundations
    from scientific import UNITS as scientific

    result = [*foundations, *composition, *scientific, *advanced]
    numbers = [unit.number for unit in result]
    if numbers != list(range(1, len(result) + 1)):
        raise ValueError("JAX units must form one complete, unique ordered route")
    if {unit.level for unit in result} != {"beginner", "intermediate", "advanced"}:
        raise ValueError("Publish the complete route rather than placeholder stages")
    for unit in result:
        if len(unit.practice) != 6 or len({case.title for case in unit.practice}) != 6:
            raise ValueError(f"{unit.id} needs six distinct concrete tasks")
        if any(number >= unit.number for number in unit.prerequisites):
            raise ValueError(f"{unit.id} has a forward prerequisite")
    return result


def program(unit: Unit, cases: tuple[Case, ...]) -> str:
    setup_lines = unit.setup.strip().splitlines()
    extra_imports = [line for line in setup_lines if line.startswith(("import ", "from "))]
    setup = "\n".join(line for line in setup_lines if line not in extra_imports).strip()
    header = HEADER.replace(
        "# Choose precision", "\n".join(extra_imports) + "\n\n# Choose precision"
    )
    body = []
    for index, item in enumerate(cases, 1):
        body.append(f"# Case {index}: {item.title}\n{item.code}")
    body.append(f"print({unit.id!r} + ': {len(cases)} asserted cases passed')")
    return (
        header
        + setup
        + "\n\n\ndef main():\n"
        + indent("\n\n".join(body), "    ")
        + '\n\n\nif __name__ == "__main__":\n    main()\n'
    )


def render(unit: Unit) -> dict[str, str]:
    key = unit.id
    prefix = f"{BASE}/"
    prerequisites = (
        ", ".join(f"`jax-{n:03d}`" for n in unit.prerequisites) or "No prior JAX knowledge."
    )
    sections = [
        f"# {key}: {unit.title}\n\n## Starting point and outcome\n\n"
        f"{unit.level.title()}. Direct prerequisites: {prerequisites}\n\n{unit.outcome}\n",
        "## Mechanism and purpose\n\n" + unit.narrative.strip(),
        "## Derivation and shape contract\n\n" + unit.derivation.strip(),
    ]
    if unit.runtime == "reading":
        sections.append(
            "## Reading and evidence boundary\n\nThis unit uses written traces and a separate "
            "explanation. It does not start a device, process group, server or cluster. "
            "Any external execution needs the explicit preparation and evidence described below."
        )
    else:
        sections.append(
            "## Run this investigation\n\nUse the **JAX** subject in the shared `/classroom` "
            "interface and its prepared `jax-cpu` profile. A Run starts a fresh Python process; "
            "save source and notes before replacing an attempt. The examples below are each "
            "complete programs, including their setup. They use tiny offline fixtures and deliberately "
            "enable 64-bit arithmetic before constructing arrays. This is a course precision choice, "
            "not the usual JAX default. No packages, models or data are downloaded.\n\n"
            f"Learner source: `{prefix}lessons/{key}.py`. Guide: `{prefix}guides/{key}.md`. "
            "Predict the value and failure behavior before running. A passing assertion supports "
            "that particular contract; it does not establish statistical validity, mastery or "
            "accelerator performance."
        )
    sections.append("## Worked investigations")
    for number, item in enumerate(unit.worked, 1):
        sections.append(
            f"### Worked example {number}: {item.title}\n\n{item.task}\n\n"
            f"{item.explanation}\n\n**Expected:** {item.expected}\n\n"
            + (
                f"```python\n{program(unit, (item,))}```"
                if unit.runtime != "reading"
                else item.code
            )
        )
    sections.append("## Exercises")
    for number, item in enumerate(unit.practice, 1):
        sections.append(
            f"### Exercise {number}: {item.title}\n\n{item.task}\n\n"
            f"**Expected:** {item.expected}\n\n**Verify:** Retain the relevant inputs, intermediate "
            f"calculation and observation. {item.explanation}\n\n**Hint 1:** {item.hint}\n\n"
            "**Hint 2:** Revisit the worked case that changes the same assumption, then close "
            "the reference and reconstruct the result from the stated contract."
        )
    sections.extend(
        [
            "## Diagnosis and boundaries\n\n" + unit.diagnosis,
            "## Transfer and review\n\n" + unit.transfer,
            "## Primary references\n\n"
            + "\n".join(f"- [{title}]({url})" for title, url in unit.sources),
            "## Ask an AI tutor about this lesson\n\n"
            f"Use the checked-in $guide-ds60sqlpy-learning skill for `{key}`. Start with my own "
            "prediction and source. Ask me to explain one intermediate shape, derivative or state "
            "transition, then give a progressive hint for the first incorrect assumption. Distinguish "
            "authored examples, my actual receipt and any hardware or population claim requiring "
            "additional evidence.",
        ]
    )
    explanation = [f"# {key}: explained reference\n\n" + unit.derivation]
    for number, item in enumerate(unit.practice, 1):
        explanation.append(
            f"## Exercise {number}: {item.title}\n\n{item.explanation}\n\n"
            f"**Expected:** {item.expected}\n\n"
            + (f"```python\n{item.code}\n```" if unit.runtime != "reading" else item.code)
        )
    explanation.append("## Scope of this evidence\n\n" + unit.diagnosis + "\n\n" + unit.transfer)
    result = {
        f"{prefix}guides/{key}.md": "\n\n".join(sections) + "\n",
        f"{prefix}solutions/{key}_solutions.md": "\n\n".join(explanation) + "\n",
    }
    if unit.runtime == "reading":
        result[f"{prefix}lessons/{key}.md"] = (
            f"# {key}: reasoning worksheet\n\n"
            + "\n\n".join(
                f"## Exercise {i}: {item.title}\n\n{item.task}\n\nRecord your evidence and limits."
                for i, item in enumerate(unit.practice, 1)
            )
            + "\n"
        )
    else:
        result[f"{prefix}solutions/{key}_solution.py"] = program(unit, unit.worked + unit.practice)
        stubs = []
        for number, item in enumerate(unit.practice, 1):
            stubs.append(
                f"# Exercise {number}: {item.title}\n"
                f"# {item.task}\n"
                f"def exercise_{number}():\n"
                f"    raise NotImplementedError({item.title!r})\n"
            )
        result[f"{prefix}lessons/{key}.py"] = (
            HEADER
            + "\n\n".join(stubs)
            + '\n\nif __name__ == "__main__":\n'
            + "".join(f"    exercise_{number}()\n" for number in range(1, 7))
        )
    return result


def artifacts() -> dict[str, str]:
    result: dict[str, str] = {}
    plan, authored = [], []
    for unit in units():
        result.update(render(unit))
        plan.append(
            {
                "id": unit.id,
                "title": unit.title,
                "level": unit.level,
                "minutes": 100 if unit.level == "beginner" else 140,
                "prerequisites": [f"jax-{n:03d}" for n in unit.prerequisites],
                "runtime": unit.runtime,
                "concepts": list(unit.concepts),
                "outcome": unit.outcome,
                "lab": unit.worked[0].task,
                "verification": unit.worked[0].expected,
            }
        )
        reading = unit.runtime == "reading"
        authored.append(
            {
                "id": unit.id,
                "status": "authored",
                "language": "markdown" if reading else "python",
                "runtime_profile": unit.runtime,
                "guide_path": f"{BASE}/guides/{unit.id}.md",
                "source_path": f"{BASE}/lessons/{unit.id}.{'md' if reading else 'py'}",
                "solution_paths": ([] if reading else [f"{BASE}/solutions/{unit.id}_solution.py"])
                + [f"{BASE}/solutions/{unit.id}_solutions.md"],
                "verification_id": None,
            }
        )
    result[f"{BASE}/track.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": "jax",
                "title": "JAX: numerical functions to independent scientific work",
                "summary": "An offline CPU route through functional state, transformations, differentiation, training, scientific computing and measured systems tradeoffs, with explicit optional hardware boundaries.",
                "lessons": plan,
            },
            indent=2,
        )
        + "\n"
    )
    result[f"{BASE}/lessons.json"] = (
        json.dumps({"schema_version": 1, "track_id": "jax", "lessons": authored}, indent=2) + "\n"
    )
    # Match the repository's pinned Python formatter without importing any
    # learner program or requiring JAX in the authoring environment.
    with tempfile.TemporaryDirectory(prefix="jax-source-format-") as temporary:
        staging = Path(temporary)
        paths = []
        for relative, text in result.items():
            if relative.endswith(".py"):
                path = staging / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
                paths.append(str(path))
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--no-cache",
                "--config",
                str(ROOT / "pyproject.toml"),
                *paths,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        if completed.returncode:
            raise ValueError("JAX source formatting failed: " + completed.stdout + completed.stderr)
        for relative in result:
            if relative.endswith(".py"):
                result[relative] = (staging / relative).read_text(encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    different = []
    for relative, text in artifacts().items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                different.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if different:
        print("JAX artifacts differ:\n" + "\n".join(different))
        return 1
    print("JAX content checked" if args.check else "JAX content generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
