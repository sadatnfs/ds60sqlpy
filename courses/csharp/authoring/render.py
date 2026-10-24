# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Reproduce a subject's teaching artifacts from reviewed, original specifications."""

import json
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SUBJECT = BASE.name
LANGUAGE = "csharp" if SUBJECT == "csharp" else "swift"
EXT = "cs" if SUBJECT == "csharp" else "swift"
PROFILE = "csharp-dotnet" if SUBJECT == "csharp" else "swift-linux"
FILENAME = "Program.cs" if SUBJECT == "csharp" else "main.swift"
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
    if SUBJECT == "csharp":
        imports = """using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;
"""
        body = "\n".join(
            "        {\n" + textwrap.indent(code, "            ") + "\n        }" for code in bodies
        )
        return (
            imports
            + "\ninternal static class Program\n{\n    private static void Check(bool condition, string reason)\n    {\n        if (!condition) throw new InvalidOperationException(reason);\n    }\n\n    private static async Task Main()\n    {\n"
            + body
            + f'\n        Console.WriteLine("{identity}: passed");\n        await Task.CompletedTask;\n    }}\n\n'
            + textwrap.indent(spec["helpers"], "    ")
            + "\n}\n"
        )
    body = "\n\n".join("do {\n" + textwrap.indent(code, "    ") + "\n}" for code in bodies)
    return (
        "import Foundation\n\n"
        + spec["helpers"]
        + "\n\n@main\nstruct LessonMain {\n    static func main() async throws {\n"
        + textwrap.indent(body, "        ")
        + f'\n        print("{identity}: passed")\n    }}\n}}\n'
    )


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
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
            "The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. "
            "C# 14 is the matching language generation. This route uses the prepared framework libraries; "
            "it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. "
            "The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws "
            "on a false condition in every build configuration, unlike conditional debugging assertions."
            if SUBJECT == "csharp"
            else "The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. "
            "An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated "
            "invariant fail the process. The fixed pad accepts one source file, without arbitrary command "
            "arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and "
            "application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad."
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
        official = spec["source"] or (
            "https://learn.microsoft.com/en-us/dotnet/csharp/"
            if SUBJECT == "csharp"
            else "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/"
        )
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
        if SUBJECT == "csharp":
            blank = (
                f"// {identity}: {spec['title']}\n// Implement the six tasks from the guide. Keep your prediction beside each check.\n"
                + "\n".join(f"// Task {i}: {task}" for i, task in enumerate(spec["tasks"], 1))
                + '\nusing System;\n\ninternal static class Program\n{\n    private static void Main()\n    {\n        throw new NotImplementedException("Implement your own lesson attempt before running.");\n    }\n}\n'
            )
        else:
            blank = (
                f"// {identity}: {spec['title']}\nimport Foundation\n\n"
                + "\n".join(f"// Task {i}: {task}" for i, task in enumerate(spec["tasks"], 1))
                + '\n\n@main\nstruct LessonMain {\n    static func main() async throws {\n        fatalError("Implement your own lesson attempt before running.")\n    }\n}\n'
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
    title = (
        "C#: from the first program to reliable .NET applications"
        if SUBJECT == "csharp"
        else "Swift: portable language foundations and Apple app architecture"
    )
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
