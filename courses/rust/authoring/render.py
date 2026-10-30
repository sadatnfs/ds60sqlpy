# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Reproduce a subject's teaching artifacts from reviewed, original specifications."""

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
SUBJECT = BASE.name
LANGUAGE = "rust"
EXT = "rs"
PROFILE = "rust-stable"
FILENAME = "main.rs"
SPECS = []


def lesson(
    title, mental, anatomy, terms, a, b, tasks, pitfalls, *, helpers="", notes="", source=""
):
    """Each example is (title, code, observation, reasoning)."""
    assert len(tasks) == 6
    assert len(terms) >= 3
    SPECS.append(
        {
            "title": title,
            "mental": mental,
            "anatomy": anatomy,
            "terms": terms,
            "a": a,
            "b": b,
            "tasks": tasks,
            "pitfalls": pitfalls,
            "helpers": textwrap.dedent(helpers).strip(),
            "notes": notes,
            "source": source,
        }
    )


def program(spec, examples, identity):
    bodies = [textwrap.dedent(example[1]).strip() for example in examples]
    body = "\n\n".join("    {\n" + textwrap.indent(code, "        ") + "\n    }" for code in bodies)
    return (
        spec["helpers"]
        + "\n\nfn main() -> Result<(), Box<dyn std::error::Error>> {\n"
        + body
        + f'\n    println!("{identity}: passed");\n    Ok(())\n}}\n'
    )


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".md":
        value = canonical_markdown(value, root=ROOT, path=path.relative_to(ROOT).as_posix())
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def build():
    plan = []
    admitted = []
    for number, spec in enumerate(SPECS, 1):
        identity = f"{SUBJECT}-{number:03d}"
        level = "beginner" if number <= 16 else "intermediate" if number <= 32 else "advanced"
        prior = [] if number == 1 else [f"{SUBJECT}-{number - 1:03d}"]
        guide = f"courses/{SUBJECT}/guides/{identity}.md"
        starter = f"courses/{SUBJECT}/lessons/{identity}.{EXT}"
        reference = f"courses/{SUBJECT}/solutions/{identity}_solution.{EXT}"
        solution = f"courses/{SUBJECT}/solutions/{identity}_solutions.md"
        plan.append(
            {
                "id": identity,
                "title": spec["title"],
                "level": level,
                "minutes": 90 if level != "advanced" else 120,
                "prerequisites": prior,
                "runtime": PROFILE,
                "concepts": [term[0] for term in spec["terms"]],
                "outcome": spec["tasks"][-1],
                "lab": spec["tasks"][2],
                "verification": spec["a"][2] + " " + spec["b"][2],
            }
        )
        admitted.append(
            {
                "id": identity,
                "status": "authored",
                "language": LANGUAGE,
                "runtime_profile": PROFILE,
                "guide_path": guide,
                "source_path": starter,
                "solution_paths": [reference, solution],
                "verification_id": None,
            }
        )
        run = (
            "The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, "
            "edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active "
            "in normal builds. The fixed pad accepts one source file without arbitrary arguments, "
            "interactive input, Cargo manifests or package installation. The main function returns "
            "`Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; "
            "the final `Ok(())` means this fixture completed successfully. Standard library and Arrow "
            "examples remain offline after image preparation. Multi-file Cargo and external ecosystem "
            "projects have separate explicit preparation workflows."
        )
        terms = "\n\n".join(f"**{term}:** {definition}" for term, definition in spec["terms"])
        examples = "\n\n".join(
            f"### Example {label}: {example[0]}\n\n{example[3]}\n\n```{LANGUAGE}\n{program(spec, [example], identity).rstrip()}\n```\n\n**Observe:** {example[2]}"
            for label, example in zip("AB", (spec["a"], spec["b"]), strict=True)
        )
        exercises = "\n\n".join(
            f"{i}. **{name}.** {task}"
            for i, (name, task) in enumerate(
                zip(
                    (
                        "Predict and explain",
                        "Guided modification",
                        "Independent construction",
                        "Diagnose a defect",
                        "Boundary evidence",
                        "Transfer and justify",
                    ),
                    spec["tasks"],
                    strict=True,
                ),
                1,
            )
        )
        official = spec["source"] or "https://doc.rust-lang.org/book/"
        prompt = f"""Use $guide-ds60sqlpy-learning for {identity}: {spec["title"]}.
Read {guide} and {starter}. Prerequisites: {", ".join(prior) or "none"}.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep {reference} and
{solution} closed until I request comparison or show an attempt.
Use {PROFILE} for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker."""
        document = f"""# {identity}: {spec["title"]}

## Level and prerequisites

{level.capitalize()}, approximately {plan[-1]["minutes"]} minutes. Prerequisites: {", ".join(f"`{p}`" for p in prior) or "None. Begin with the source file and visible result."}

## Learning objectives

{spec["tasks"][2]} Then {spec["tasks"][-1][0].lower() + spec["tasks"][-1][1:]}

## Purpose and mental model

{spec["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{run}

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

{spec["notes"]}

## Syntax anatomy and execution trace

{spec["anatomy"]}

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

{examples}

## Exercises

{exercises}

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

{spec["pitfalls"]}

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain {", ".join(term[0] for term in spec["terms"])} without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation]({official}). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
        write(BASE / "guides" / f"{identity}.md", document)
        blank = (
            f"// {identity}: {spec['title']}\n"
            + "\n".join(f"// Task {i}: {task}" for i, task in enumerate(spec["tasks"], 1))
            + '\n\nfn main() {\n    todo!("Implement your own lesson attempt before running.");\n}\n'
        )
        write(BASE / "lessons" / f"{identity}.{EXT}", blank)
        write(
            BASE / "solutions" / f"{identity}_solution.{EXT}",
            program(spec, [spec["a"], spec["b"]], identity),
        )
        explanation = f"""# {identity}: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [{identity}_solution.{EXT}]({identity}_solution.{EXT}). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**{spec["a"][0]}:** {spec["a"][3]} {spec["a"][2]}

**{spec["b"][0]}:** {spec["b"][3]} {spec["b"][2]}

## Reason through the six tasks

{exercises}

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

{spec["mental"]}

{spec["anatomy"]}

{spec["pitfalls"]}

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
"""
        write(BASE / "solutions" / f"{identity}_solutions.md", explanation)
    title = "Rust: ownership, reliable systems and Arrow data engineering"
    summary = f"{len(SPECS)} detailed lessons from first programs through language mechanisms, reliable systems and independently designed projects."
    write(
        BASE / "track.json",
        json.dumps(
            {
                "schema_version": 1,
                "id": SUBJECT,
                "title": title,
                "summary": summary,
                "lessons": plan,
            },
            indent=2,
            ensure_ascii=False,
        ),
    )
    write(
        BASE / "lessons.json",
        json.dumps(
            {"schema_version": 1, "track_id": SUBJECT, "lessons": admitted},
            indent=2,
            ensure_ascii=False,
        ),
    )
