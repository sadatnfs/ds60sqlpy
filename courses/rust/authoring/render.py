# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Reproduce a subject's teaching artifacts from reviewed, original specifications."""

import json
import re
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
from outcomes import MINUTES, OUTCOMES  # noqa: E402
from practice import CHECK, READ, TRANSFER, WALK  # noqa: E402

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


def program(spec, examples, identity, answers=()):
    bodies = [textwrap.dedent(example[1]).strip() for example in examples]
    bodies += [
        f"// Task {task}: {TASK_NAMES[task - 1]}\n" + textwrap.dedent(answer["code"]).strip()
        for task, answer in answers
    ]
    body = "\n\n".join("    {\n" + textwrap.indent(code, "        ") + "\n    }" for code in bodies)
    return (
        spec["helpers"]
        + "\n\nfn main() -> Result<(), Box<dyn std::error::Error>> {\n"
        + body
        + f'\n    println!("{identity}: passed");\n    Ok(())\n}}\n'
    )


def code_answers(number):
    """Executable reference answers for one lesson, in task order."""
    return sorted(
        (task, answer) for task, answer in ANSWERS.get(number, {}).items() if answer.get("code")
    )


def first_sentence(text):
    return text.split(". ")[0].rstrip(".") + "."


def reasoning(answer):
    """The optional correctness, wrong-approach and verification paragraphs of one answer."""
    parts = []
    if answer.get("why"):
        parts.append(f"**Why it is correct.** {answer['why']}")
    if answer.get("wrong"):
        parts.append(f"**Plausible wrong approach.** {answer['wrong']}")
    if answer.get("verify"):
        parts.append(f"**How to verify.** {answer['verify']}")
    return "".join(f"\n\n{part}" for part in parts)


def answer_text(number, task, spec, identity):
    """The explanation for one task: its reference answer or an honest pointer."""
    answer = ANSWERS.get(number, {}).get(task)
    if answer and answer.get("code"):
        code = textwrap.dedent(answer["code"]).strip()
        used = [
            f"`{name}`"
            for kind, name in re.findall(
                r"(?m)^(?:pub )?(fn|struct|enum|trait|type) (\w+)", spec["helpers"]
            )
            if re.search(rf"(?<![\w:.]){name}\s*\(" if kind == "fn" else rf"\b{name}\b", code)
        ]
        uses = ""
        if used:
            names = ", ".join(used[:-1]) + " and " + used[-1] if len(used) > 1 else used[0]
            uses = f" Helpers used: {names}."
        wrapped = (
            "fn main() -> Result<(), Box<dyn std::error::Error>> {\n"
            + textwrap.indent(code, "    ")
            + "\n    Ok(())\n}"
        )
        return (
            f"**Reference answer**, wrapped in `main`; the reference runs it as its `Task {task}` block.{uses}\n\n"
            f"```{LANGUAGE}\n{wrapped}\n```\n\n"
            f"**Observe:** {answer['observe']}\n\n{answer['explain']}" + reasoning(answer)
        )
    if answer:
        return f"**Written answer.** {answer['explain']}" + reasoning(answer)
    a, b = spec["a"], spec["b"]
    return {
        1: f"No reference answer has been written for this task yet. Check your trace against whichever guided example exercises the same mechanism: Example A ({a[0]}) or Example B ({b[0]}).",
        2: f"No reference answer has been written for this task yet. Start from the guided example this task modifies, Example A ({a[0]}) or Example B ({b[0]}), and keep its original checks passing.",
        3: f"No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **{spec['terms'][0][0]}** and the lesson notes.",
        4: f"No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: {spec['pitfalls']}",
        5: f"No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A ({a[0]}) and Example B ({b[0]}).",
        6: f"**Judging criteria.** {TRANSFER[number]}",
    }[task]


def modules(spec):
    """The standard library and Arrow modules a lesson's programs name, as a sentence."""
    text = "\n".join((spec["helpers"], spec["a"][1], spec["b"][1]))
    found = sorted(set(re.findall(r"\b((?:std|arrow)::[a-z_]+)\b", text)))
    if not found:
        return "This lesson's programs need only the prelude and their own helpers."
    named = [f"`{name}`" for name in found]
    listed = ", ".join(named[:-1]) + " and " + named[-1] if len(named) > 1 else named[0]
    return f"Beyond the prelude, this lesson's programs use {listed}."


def tempting(number):
    """Wrong approaches recorded for the construction and evidence tasks, as hint bullets."""
    return "\n".join(
        f"- **Task {task}.** {answer['wrong']}"
        for task, answer in sorted(ANSWERS.get(number, {}).items())
        if task != 4 and answer.get("wrong")
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
        terms = "\n\n".join(f"**{term}:** {definition}" for term, definition in spec["terms"])
        examples = "\n\n".join(
            f"### Example {label}: {example[0]}\n\n{example[3]}\n\n```{LANGUAGE}\n{program(spec, [example], identity).rstrip()}\n```\n\n**Observe:** {example[2]}"
            for label, example in zip("AB", (spec["a"], spec["b"]), strict=True)
        )
        exercises = "\n\n".join(
            f"{i}. **{name}.** {task}"
            for i, (name, task) in enumerate(zip(TASK_NAMES, spec["tasks"], strict=True), 1)
        )
        task_answers = "\n\n".join(
            f"### Task {i}: {name}\n\n{task}\n\n{answer_text(number, i, spec, identity)}"
            for i, (name, task) in enumerate(zip(TASK_NAMES, spec["tasks"], strict=True), 1)
        )
        url, label, focus = READ[number]
        reading = f"Read [{label}]({url}) {focus}."
        if spec["source"] and spec["source"] != url:
            reading += f" The broader reference is [{spec['source']}]({spec['source']})."
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

{modules(spec)} A passing run prints `{identity}: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).

{spec["notes"]}

## Syntax anatomy and execution trace

{spec["anatomy"]}

**Reading Example A ({spec["a"][0]}, code below).** {WALK[number]}

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

{examples}

## Exercises

{exercises}

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

{spec["pitfalls"]}

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A ({spec["a"][0]}) before changing anything, and confirm its observation: {spec["a"][2]}
2. Compare Example B ({spec["b"][0]}) with Example A and name the first line whose behavior differs. Its observation is: {spec["b"][2]}
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: {first_sentence(spec["pitfalls"])}

Tempting approaches to rule out before you compare:

{tempting(number)}

## Self-check and next step

{CHECK[number]}

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

{reading}

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
            program(spec, [spec["a"], spec["b"]], identity, answered),
        )
        explanation = f"""# {identity}: explanation and comparison

Executable reference: [{identity}_solution.{EXT}]({identity}_solution.{EXT}), which runs both examples{" and the coded answers" if answered else ""}.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**{spec["a"][0]}:** {spec["a"][3]} {spec["a"][2]}

**{spec["b"][0]}:** {spec["b"][3]} {spec["b"][2]}

## Task answers

{task_answers}

## Mechanism and diagnostic reasoning

{spec["mental"]}

{spec["anatomy"]}

{spec["pitfalls"]}

## Review before continuing

Rebuild Example B ({spec["b"][0]}) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
"""
        write(BASE / "solutions" / f"{identity}_solutions.md", explanation)
    title = "Rust: ownership, reliable systems and Arrow data engineering"
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
