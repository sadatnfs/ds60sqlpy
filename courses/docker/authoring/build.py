"""Durable Docker curriculum authoring. No engine access or downloads."""

from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown  # noqa: E402

AUTHORED = runpy.run_path(str(Path(__file__).with_name("chapters.py")))
SPECS = AUTHORED["CHAPTERS"]
CONCEPTS = AUTHORED["CONCEPTS"]
REFERENCE_LABELS = AUTHORED["REFERENCE_LABELS"]
MISTAKES = AUTHORED["MISTAKES"]
KEY_TERMS = AUTHORED["KEY_TERMS"]
BOUNDARY = AUTHORED["BOUNDARY"]
RETRIEVAL = AUTHORED["RETRIEVAL"]
REASONING = runpy.run_path(str(Path(__file__).with_name("reasoning.py")))["REASONING"]
# Per-lesson host lab, extra misconception and transfer case; shared rules live in STUDY-GUIDE.md.
LABS = runpy.run_path(str(Path(__file__).with_name("labs.py")))["LABS"]
LAB_FIELDS = ("lab", "trap", "ask", "answer")
REASONING_LABELS = (
    "Approach",
    "Why this is correct",
    "A plausible wrong approach",
    "How to verify",
)
# Exercises led by these verbs ask for an answer rather than an artifact, so the
# guide shows the prompt and the solutions file keeps the expected answer.
ANSWER_VERBS = {
    "Calculate",
    "Choose",
    "Classify",
    "Compare",
    "Describe",
    "Diagnose",
    "Distinguish",
    "Draw",
    "Explain",
    "Identify",
    "List",
    "Name",
    "Predict",
    "Trace",
}


def answer_task(prompt):
    return prompt.split(maxsplit=1)[0] in ANSWER_VERBS


def series(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def check_key_terms():
    titles = [spec[0] for spec in SPECS]
    if set(KEY_TERMS) != set(titles):
        missing = sorted(set(titles) - set(KEY_TERMS))
        extra = sorted(set(KEY_TERMS) - set(titles))
        raise ValueError(f"KEY_TERMS mismatch: missing {missing}, extra {extra}")
    for title in titles:
        pairs = KEY_TERMS[title]
        terms = [term for term, _ in pairs]
        if not 3 <= len(pairs) <= 5 or len(set(terms)) != len(terms):
            raise ValueError(f"{title}: key terms need 3 to 5 unique entries")
        for term, definition in pairs:
            if not term or len(term) > 80 or any(c in term for c in ":*\n"):
                raise ValueError(f"{title}: unusable key term {term!r}")
            if not definition.endswith("."):
                raise ValueError(f"{title}: definition of {term!r} must end with a period")


def check_reasoning():
    titles = [spec[0] for spec in SPECS]
    if set(REASONING) != set(titles):
        missing = sorted(set(titles) - set(REASONING))
        extra = sorted(set(REASONING) - set(titles))
        raise ValueError(f"REASONING mismatch: missing {missing}, extra {extra}")
    for spec in SPECS:
        title, tasks = spec[0], spec[4]
        entries = REASONING[title]
        if len(entries) != len(tasks):
            raise ValueError(f"{title}: reasoning needs one entry per exercise ({len(tasks)})")
        for i, parts in enumerate(entries, 1):
            if len(parts) != len(REASONING_LABELS):
                raise ValueError(f"{title} exercise {i}: reasoning needs four parts")
            for label, part in zip(REASONING_LABELS, parts, strict=True):
                if not part.strip() or not part.endswith((".", "?")):
                    raise ValueError(f"{title} exercise {i}: {label} must be a sentence")
                if "\u2014" in part or "\u2013" in part:
                    raise ValueError(f"{title} exercise {i}: {label} contains a dash")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".md":
        text = canonical_markdown(text, root=ROOT, path=path.relative_to(ROOT).as_posix())
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def check_lesson_prose():
    keys = {f"docker-{n:03d}" for n in range(1, len(SPECS) + 1)}
    for name, table in (("BOUNDARY", BOUNDARY), ("RETRIEVAL", RETRIEVAL), ("LABS", LABS)):
        if set(table) != keys:
            raise ValueError(f"{name} needs exactly one entry per lesson")
    for key, entry in LABS.items():
        if set(entry) != set(LAB_FIELDS):
            raise ValueError(f"{key}: LABS entry needs exactly {LAB_FIELDS}")
        for field, value in entry.items():
            if "\u2014" in value or "\u2013" in value:
                raise ValueError(f"{key}: LABS {field} contains a dash")


def build():
    check_lesson_prose()
    check_key_terms()
    check_reasoning()
    rows, records = [], []
    for n, spec in enumerate(SPECS, 1):
        key = f"docker-{n:03d}"
        level = "beginner" if n <= 14 else "intermediate" if n <= 28 else "advanced"
        prereq = [f"docker-{n - 1:03d}"] if n > 1 else []
        title, mental, anatomy, examples, tasks, refs = spec
        concepts = CONCEPTS[title]
        notes = LABS[key]
        key_terms = "\n".join(
            f"- **{term}:** {definition}" for term, definition in KEY_TERMS[title]
        )
        rows.append(
            dict(
                id=key,
                title=title,
                level=level,
                minutes=100 if n < 29 else 120,
                prerequisites=prereq,
                runtime="reading",
                concepts=concepts,
                outcome=f"{tasks[2][0]} {tasks[-1][0]}",
                lab=tasks[2][0],
                verification=tasks[2][1],
            )
        )
        guide = f"courses/docker/guides/{key}.md"
        source = f"courses/docker/lessons/{key}.md"
        solution = f"courses/docker/solutions/{key}_solutions.md"
        prerequisites = (
            ", ".join(f"`{p}`" for p in prereq)
            or "None; start with the terminal and process explanations here."
        )
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; about {rows[-1]["minutes"]} minutes, with additional time for the optional host experiment. Direct prerequisites: {prerequisites}

## Learning objectives

{tasks[2][0]} {tasks[-1][0]} Use {series(concepts[:3])} accurately when you explain what you observed.

## Purpose, vocabulary and mental model

{mental}

### Key terms

{key_terms}

## Anatomy and a trace you can follow

{anatomy}

## How to use this lesson

The classroom saves `{source}` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** {notes["lab"]}

## Worked example / walkthrough
"""
        for i, (heading, body, lang, code, expected) in enumerate(examples, 1):
            text += f"\n### Worked example {i}: {heading}\n\n{body}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += "\n## Six progressive exercises\n\nAnswer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).\n"
        worksheet = f"# {key}: learner worksheet\n\nSave predictions before optional host execution. Keep exact project name, engine identity and timestamps with runtime observations. No exercise runs automatically.\n"
        answer = f"# {key}: explanatory solutions\n\nThese answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/{key}.md).\n"
        for i, (prompt, expected, reason, *extra) in enumerate(tasks, 1):
            text += f"\n### Exercise {i}: {prompt}\n"
            label = "Expected answer" if answer_task(prompt) else "Expected evidence"
            if label == "Expected evidence":
                text += f"\n**Expected evidence:** {expected}\n"
            if extra:
                text += f"\n**Hint:** {extra[0]}\n"
            worksheet += f"\n## Exercise {i}: {prompt}\n\nMy prediction:\n\nMy evidence:\n\nMy explanation and remaining limitation:\n"
            answer += (
                f"\n## Exercise {i}: {prompt}\n\n**{label}:** {expected}\n\n**Why:** {reason}\n"
            )
            for part_label, part in zip(REASONING_LABELS, REASONING[title][i - 1], strict=True):
                answer += f"\n**{part_label}:** {part}\n"
        boundary = (
            "" if answer_task(tasks[3][0]) else f"Its expected observation is: {tasks[3][1]} "
        )
        text += (
            f"""
## Common mistakes and diagnosis

{MISTAKES[title]}

Exercise 4 is this chapter's boundary case: {tasks[3][0]} {boundary}{BOUNDARY[key]}

{notes["trap"]}

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** {RETRIEVAL[key]}

**Transfer case.** {notes["ask"]}

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

"""
            + "\n".join(f"- [{REFERENCE_LABELS[url]}]({url})" for url in refs)
            + f"""

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {key}: {title}.
Read {guide} and {source}. Direct prerequisites: {prerequisites}
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
"""
        )
        answer += f"\n## Check your transfer\n\n{notes['answer']}\n"
        write(ROOT / guide, text)
        write(ROOT / source, worksheet)
        write(ROOT / solution, answer)
        records.append(
            dict(
                id=key,
                status="authored",
                language="markdown",
                runtime_profile="reading",
                guide_path=guide,
                source_path=source,
                solution_paths=[solution],
                verification_id=None,
            )
        )
    write(
        BASE / "track.json",
        json.dumps(
            dict(
                schema_version=1,
                id="docker",
                title="Docker: images, applications and operating containers",
                summary=f"{len(rows)} detailed lessons from the first container to reproducible builds, Compose, networking, durable data, security, delivery and recovery. Study offline and use clearly scoped optional host labs.",
                lessons=rows,
            ),
            indent=2,
        ),
    )
    write(
        BASE / "lessons.json",
        json.dumps(dict(schema_version=1, track_id="docker", lessons=records), indent=2),
    )
    print(f"Authored {len(rows)} Docker lessons with explicit host-only execution boundaries.")


if __name__ == "__main__":
    build()
