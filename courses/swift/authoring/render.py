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

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from answers import ANSWERS  # noqa: E402
from teaching import TEACHING  # noqa: E402
from outcomes import MINUTES, OUTCOMES  # noqa: E402
from reasoning import REASONING  # noqa: E402

TASK_NAMES = (
    "Predict and explain",
    "Guided modification",
    "Independent construction",
    "Diagnose a defect",
    "Boundary evidence",
    "Transfer and justify",
)

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


def program(spec, examples, identity, answers=()):
    bodies = [textwrap.dedent(example[1]).strip() for example in examples]
    bodies += [
        f"// Task {task}: {TASK_NAMES[task - 1]}\n" + textwrap.dedent(answer["code"]).strip()
        for task, answer in answers
    ]
    helpers = "\n".join(
        [spec["helpers"], *(answer["helpers"] for _, answer in answers if answer.get("helpers"))]
    ).strip()
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
            + textwrap.indent(helpers, "    ")
            + "\n}\n"
        )
    body = "\n\n".join("do {\n" + textwrap.indent(code, "    ") + "\n}" for code in bodies)
    return (
        "import Foundation\n\n"
        + helpers
        + "\n\n@main\nstruct LessonMain {\n    static func main() async throws {\n"
        + textwrap.indent(body, "        ")
        + f'\n        print("{identity}: passed")\n    }}\n}}\n'
    )


def code_answers(number):
    """Executable reference answers for one lesson, in task order."""
    return sorted(
        (task, answer) for task, answer in ANSWERS.get(number, {}).items() if answer.get("code")
    )


def answer_text(number, task, spec, identity):
    """The explanation for one task: its reference answer or an honest pointer."""
    answer = ANSWERS.get(number, {}).get(task)
    if answer and answer.get("code"):
        return (
            f"**Reference answer.** It runs as the `Task {task}` block of the reference program.\n\n"
            f"```{LANGUAGE}\n{answer['code'].strip()}\n```\n\n"
            f"**Observe:** {answer['observe']}\n\n{answer['explain']}"
        )
    if answer:
        return f"**Written answer.** {answer['explain']}"
    a, b = spec["a"], spec["b"]
    return {
        1: f"No separate reference answer has been written for this task. Example A is the evidence to compare with: {a[3]} {a[2]}",
        2: f"No separate reference answer has been written for this task. Start from Example B: {b[3]} {b[2]}",
        3: f"No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **{spec['terms'][0][0]}** and the lesson notes.",
        4: f"No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: {spec['pitfalls']}",
        5: f"No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A ({a[0]}) and Example B ({b[0]}).",
        6: "No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).",
    }[task]


REASONING_PARTS = (
    ("approach", "Approach"),
    ("correct", "Why it is correct"),
    ("wrong", "A plausible wrong approach"),
    ("verify", "How to verify"),
)


def reasoning_text(number, identity):
    """The four-part solution reasoning for one lesson, validated before rendering."""
    entry = REASONING.get(number)
    if entry is None or set(entry) != {key for key, _ in REASONING_PARTS}:
        raise ValueError(
            f"{identity} needs reasoning with exactly {[k for k, _ in REASONING_PARTS]}"
        )
    for key, _ in REASONING_PARTS:
        text = " ".join(entry[key].split())
        if len(text.split()) < 20:
            raise ValueError(f"{identity} reasoning '{key}' needs at least 20 words")
        if "\u2014" in text or "\u2013" in text:
            raise ValueError(f"{identity} reasoning '{key}' contains an em or en dash")
    return "\n\n".join(
        f"**{label}.** {' '.join(entry[key].split())}" for key, label in REASONING_PARTS
    )


TEACHING_FIELDS = {
    "run": 30,
    "trace_a": 50,
    "trace_b": 50,
    "regression": 40,
    "selfcheck": 40,
    "docs": 12,
}


def teaching_text(number, identity, openings):
    """Lesson-specific teaching prose, validated so no field becomes shared template text."""
    entry = TEACHING.get(number)
    if entry is None or set(entry) != set(TEACHING_FIELDS):
        raise ValueError(f"{identity} needs teaching prose with exactly {sorted(TEACHING_FIELDS)}")
    result = {}
    for key, minimum in TEACHING_FIELDS.items():
        text = " ".join(entry[key].split())
        if len(text.split()) < minimum:
            raise ValueError(f"{identity} teaching '{key}' needs at least {minimum} words")
        if "\u2014" in text or "\u2013" in text:
            raise ValueError(f"{identity} teaching '{key}' contains an em or en dash")
        opening = " ".join(text.lower().split()[:6])
        if opening in openings:
            raise ValueError(
                f"{identity} teaching '{key}' reuses the opening of {openings[opening]}"
            )
        openings[opening] = f"{identity} {key}"
        result[key] = text
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".md":
        value = canonical_markdown(value, root=ROOT, path=path.relative_to(ROOT).as_posix())
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def build():
    plan = []
    admitted = []
    openings = {}
    for number, spec in enumerate(SPECS, 1):
        identity = f"{SUBJECT}-{number:03d}"
        level = "beginner" if number <= 16 else "intermediate" if number <= 32 else "advanced"
        prior = [] if number == 1 else [f"{SUBJECT}-{number - 1:03d}"]
        guide = f"courses/{SUBJECT}/guides/{identity}.md"
        starter = f"courses/{SUBJECT}/lessons/{identity}.{EXT}"
        reference = f"courses/{SUBJECT}/solutions/{identity}_solution.{EXT}"
        solution = f"courses/{SUBJECT}/solutions/{identity}_solutions.md"
        outcome = OUTCOMES[number]
        if outcome == spec["tasks"][-1]:
            raise ValueError(identity + " needs a specific outcome")
        answered = code_answers(number)
        third = ANSWERS.get(number, {}).get(3, {})
        if third.get("code"):
            lab, verification = spec["tasks"][2], third["observe"]
        else:
            lab = f"Reproduce Example A ({spec['a'][0]}) and Example B ({spec['b'][0]}) and explain each check."
            verification = spec["a"][2] + " " + spec["b"][2]
        plan.append(
            {
                "id": identity,
                "title": spec["title"],
                "level": level,
                "minutes": MINUTES.get(number, 90 if level != "advanced" else 120),
                "prerequisites": prior,
                "runtime": PROFILE,
                "concepts": [term[0] for term in spec["terms"]],
                "outcome": outcome,
                "lab": lab,
                "verification": verification,
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
        teach = teaching_text(number, identity, openings)
        terms = "\n\n".join(f"**{term}:** {definition}" for term, definition in spec["terms"])
        examples = "\n\n".join(
            f"### Example {label}: {example[0]}\n\n{example[3]}\n\n```{LANGUAGE}\n{program(spec, [example], identity).rstrip()}\n```\n\n**Observe:** {example[2]}\n\n**Trace.** {trace}"
            for label, example, trace in zip(
                "AB", (spec["a"], spec["b"]), (teach["trace_a"], teach["trace_b"]), strict=True
            )
        )
        exercises = "\n\n".join(
            f"{i}. **{name}.** {task}"
            for i, (name, task) in enumerate(zip(TASK_NAMES, spec["tasks"], strict=True), 1)
        )
        hint3 = (
            f"Before opening the explanation, check your task 3 attempt ({spec['tasks'][2].rstrip('.')}) "
            "against each pitfall listed above, and add one input that would expose the tempting wrong rule."
        )
        task_answers = "\n\n".join(
            f"### Task {i}: {name}\n\n{task}\n\n{answer_text(number, i, spec, identity)}"
            for i, (name, task) in enumerate(zip(TASK_NAMES, spec["tasks"], strict=True), 1)
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

{outcome} The central exercise is task 3: {spec["tasks"][2]}

## Purpose and mental model

{spec["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{teach["run"]}

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

{spec["notes"]}

## Syntax anatomy and execution trace

{spec["anatomy"]}

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

{examples}

## Exercises

{exercises}

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

{spec["pitfalls"]}

{teach["regression"]}

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A ({spec["a"][0]}) before changing anything, and confirm its observation: {spec["a"][2]}
2. Compare Example B ({spec["b"][0]}) with Example A and name the first line whose behavior differs. Its observation is: {spec["b"][2]}
3. {hint3}

## Self-check and next step

{teach["selfcheck"]}

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation]({official}): {teach["docs"]}

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
            program(spec, [spec["a"], spec["b"]], identity, answered),
        )
        explanation = f"""# {identity}: explanation and comparison

Reference program: [{identity}_solution.{EXT}]({identity}_solution.{EXT}), covering both examples{" and the executed answers" if answered else ""}.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**{spec["a"][0]}:** {spec["a"][3]} {spec["a"][2]}

**{spec["b"][0]}:** {spec["b"][3]} {spec["b"][2]}

## Task answers

{task_answers}

## Solution reasoning

{reasoning_text(number, identity)}

## Mechanism and diagnostic reasoning

{spec["mental"]}

{spec["anatomy"]}

{spec["pitfalls"]}

## Review before continuing

Run the reference and confirm it prints `{identity}: passed`, then rerun the guide's counterexample.
"""
        write(BASE / "solutions" / f"{identity}_solutions.md", explanation)
    title = (
        "C#: from the first program to reliable .NET applications"
        if SUBJECT == "csharp"
        else "Swift: portable language foundations and Apple app architecture"
    )
    summary = f"{len(SPECS)} detailed lessons from first programs through language mechanisms, reliable systems and independently designed projects."
    code = sum(len(code_answers(number)) for number in range(1, len(SPECS) + 1))
    written = sum(
        1 for tasks in ANSWERS.values() for answer in tasks.values() if not answer.get("code")
    )
    print(
        f"{SUBJECT}: reference answers for {code} tasks (executed) and {written} written; "
        f"{6 * len(SPECS) - code - written} of {6 * len(SPECS)} tasks have none yet."
    )
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
