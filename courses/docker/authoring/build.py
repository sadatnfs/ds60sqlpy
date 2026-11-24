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
    for name, table in (("BOUNDARY", BOUNDARY), ("RETRIEVAL", RETRIEVAL)):
        if set(table) != keys:
            raise ValueError(f"{name} needs exactly one entry per lesson")


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

The classroom displays this guide and saves your worksheet, `{source}`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough
"""
        for i, (heading, body, lang, code, expected) in enumerate(examples, 1):
            text += f"\n### Worked example {i}: {heading}\n\n{body}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += "\n## Six progressive exercises\n\nFor each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.\n"
        worksheet = f"# {key}: learner worksheet\n\nSave predictions before optional host execution. Keep exact project name, engine identity and timestamps with runtime observations. No exercise runs automatically.\n"
        answer = f"# {key}: explanatory solutions\n\nCompare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `{guide}`.\n"
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
            ""
            if answer_task(tasks[3][0])
            else f"Its expected observation is: {tasks[3][1]} Use it to avoid treating a successful command as proof of the wrong claim. "
        )
        text += (
            f"""
## Common mistakes and diagnosis

{MISTAKES[title]}

Exercise 4 is this chapter's boundary case: {tasks[3][0]} {boundary}{BOUNDARY[key]} Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. {RETRIEVAL[key]} Then reconstruct worked example 2 ({examples[1][0]}) with one different value, predict what changes, and name which of {series(concepts)} the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
        answer += "\n## Check your transfer\n\nA useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.\n"
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
