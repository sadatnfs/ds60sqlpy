"""Rebuild the offline HTML, CSS and PHP curriculum without running learner code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
HERE = Path(__file__).resolve().parent
# Exercises led by these verbs ask for an answer rather than an artifact, so the
# guide shows only the hint and the solutions file keeps the expected answer.
ANSWER_VERBS = {
    "Calculate",
    "Choose",
    "Classify",
    "Compare",
    "Compute",
    "Describe",
    "Diagnose",
    "Distinguish",
    "Draw",
    "Explain",
    "Identify",
    "List",
    "Map",
    "Name",
    "Predict",
    "Resolve",
    "Trace",
}
FAILURE_NOTES = {
    "html": "Keep the failing source, the viewport width and what you observed, then repair one cause at a time. A browser can recover malformed HTML, silently ignore a CSS declaration or display a plausible layout with the wrong reading order, so inspect the element and its computed styles in the browser's developer tools instead of trusting the rendering alone.",
    "php": "Keep the failing source, its input and the exact output, then repair one cause at a time. PHP can produce correct-looking text while missing an invalid-input branch, so rerun the empty, wrong-type and boundary cases after every fix.",
    "markdown": "A plausible plan or one successful request can hide an untested failure path. Record each request, response and stored state, and repeat the original failing case after every change.",
}


def answer_task(prompt: str) -> bool:
    return prompt.split(maxsplit=1)[0] in ANSWER_VERBS


def series(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def specs() -> list[dict]:
    payload = json.loads((HERE / "chapters.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Unknown web authoring schema")
    result = payload["chapters"]
    if len(result) != 60 or [item["n"] for item in result] != list(range(1, 61)):
        raise ValueError("Web chapter identities changed unexpectedly")
    for item in result:
        check_key_terms(item["n"], item.get("key_terms"))
        check_reasoning(item["n"], item.get("reasoning"))
        check_contrast(item["n"], item.get("contrast"))
    return result


REASONING_FIELDS = ("approach", "pitfall", "verify")
CONTRAST_FIELDS = ("heading", "setup", "lang", "code", "reading")


def plain_text(n: int, label: str, value: object, *, sentence: bool = True) -> None:
    """Require non-empty single-line prose without em or en dashes."""
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"web-{n:03d} {label} must be non-empty trimmed text")
    if "\u2014" in value or "\u2013" in value or "\n" in value:
        raise ValueError(f"web-{n:03d} {label} contains a dash character or line break")
    if sentence and not value.endswith((".", "?")):
        raise ValueError(f"web-{n:03d} {label} must be complete sentences")


def check_reasoning(n: int, items: object) -> None:
    """Require approach, plausible wrong approach and verification text for all six tasks."""
    if not isinstance(items, list) or len(items) != 6:
        raise ValueError(f"web-{n:03d} needs reasoning for all six exercises")
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict) or sorted(item) != sorted(REASONING_FIELDS):
            raise ValueError(f"web-{n:03d} exercise {i} reasoning needs {REASONING_FIELDS}")
        for field in REASONING_FIELDS:
            plain_text(n, f"exercise {i} {field}", item[field])
        if len(item["pitfall"].split()) < 10 or len(item["verify"].split()) < 8:
            raise ValueError(f"web-{n:03d} exercise {i} reasoning is too thin to teach")


def check_contrast(n: int, item: object) -> None:
    """Require one lesson-specific contrast case: a runnable snippet and its reading."""
    if not isinstance(item, dict) or sorted(item) != sorted(CONTRAST_FIELDS):
        raise ValueError(f"web-{n:03d} contrast needs {CONTRAST_FIELDS}")
    plain_text(n, "contrast heading", item["heading"], sentence=False)
    if ":" in item["heading"] or "*" in item["heading"]:
        raise ValueError(f"web-{n:03d} contrast heading cannot contain ':' or '*'")
    plain_text(n, "contrast setup", item["setup"])
    plain_text(n, "contrast reading", item["reading"])
    if item["lang"] not in {"html", "css", "js", "php", "text", "http", "sh", "sql", "yaml"}:
        raise ValueError(f"web-{n:03d} contrast lang is not a supported fence language")
    code = item["code"]
    if not isinstance(code, str) or not code.strip() or "```" in code:
        raise ValueError(f"web-{n:03d} contrast code must be a non-empty fenced snippet")
    if "\u2014" in code or "\u2013" in code:
        raise ValueError(f"web-{n:03d} contrast code contains a dash character")


def check_key_terms(n: int, pairs: object) -> None:
    """Require 3 to 5 lesson-specific term and definition pairs for the Key terms list."""
    if not isinstance(pairs, list) or not 3 <= len(pairs) <= 5:
        raise ValueError(f"web-{n:03d} needs 3 to 5 key_terms")
    seen: set[str] = set()
    for pair in pairs:
        if not (
            isinstance(pair, list)
            and len(pair) == 2
            and all(isinstance(value, str) and value.strip() for value in pair)
        ):
            raise ValueError(f"web-{n:03d} key_terms entries must be [term, definition]")
        term, definition = pair
        if ":" in term or "*" in term or len(term) > 80 or term.lower() in seen:
            raise ValueError(f"web-{n:03d} has an invalid or repeated key term: {term!r}")
        if not definition.endswith("."):
            raise ValueError(f"web-{n:03d} definition for {term!r} must be a sentence")
        seen.add(term.lower())


def artifacts() -> dict[Path, str]:
    files: dict[Path, str] = {}
    rows, records, inventory = [], [], []
    for spec in specs():
        n, title = spec["n"], spec["title"]
        key = f"web-{n:03d}"
        language = "html" if n <= 30 else "php" if n <= 56 else "markdown"
        runtime = {"html": "html-browser", "php": "php-cli", "markdown": "reading"}[language]
        extension = {"html": ".html", "php": ".php", "markdown": ".md"}[language]
        level = spec.get(
            "level",
            "beginner"
            if n <= 12 or 31 <= n <= 36
            else "intermediate"
            if n <= 24 or 37 <= n <= 44
            else "advanced",
        )
        prerequisites = spec.get("prerequisites", [] if n == 1 else [f"web-{n - 1:03d}"])
        prereq_text = (
            ", ".join(f"`{value}`" for value in prerequisites)
            or "None. This lesson explains the necessary vocabulary."
        )
        minutes = spec.get(
            "minutes", 90 if level == "beginner" else 110 if level == "intermediate" else 140
        )
        guide = f"courses/web-development/guides/{key}.md"
        source = f"courses/web-development/lessons/{key}{extension}"
        explanation = f"courses/web-development/solutions/{key}_solutions.md"
        reference = f"courses/web-development/solutions/{key}_solution{extension}"
        tasks = spec["tasks"]
        assert len(tasks) == 6 and len(spec["examples"]) == 2
        rows.append(
            dict(
                id=key,
                title=title,
                level=level,
                minutes=minutes,
                prerequisites=prerequisites,
                runtime=runtime,
                concepts=spec["terms"],
                outcome=f"{tasks[2][0]} {tasks[5][0]}",
                lab=tasks[2][0],
                verification=tasks[2][1],
            )
        )
        readme = "**How to run lessons** in the [subject README](../README.md)"
        if language == "html":
            execution = f"Choose **HTML browser preview** and work in `{source}`, one complete HTML document with embedded CSS and, where taught, inline JavaScript. The preview is offline: it cannot contact a server, submit real forms or load external assets, so every fixture is inline and synthetic. Save your attempt before comparing it with `{reference}`. {readme} explains Live preview, the viewport presets and what a reference check does not show."
        elif language == "php":
            execution = f"Choose the **PHP CLI** worker and work in `{source}`, which runs as `main.php` in a bounded Linux process with PDO SQLite. Every input is a small synthetic value, and CLI runs are fresh processes, not persistent HTTP requests. Save your attempt before comparing it with `{reference}`. {readme} lists what the pad does not provide."
        else:
            execution = f"This lesson is a design worksheet saved as `{source}`. The classroom does not start a server, install packages or control Docker, so a command here is a proposal until you deliberately run it in your own disposable project. The optional lab is `courses/web-development/fixtures/php-http-lab/`; read its README before preparing it and never expose it to the internet. {readme} describes this boundary."
        terms = series(spec["terms"][:3])
        key_terms = "\n".join(
            f"- **{term}:** {definition}" for term, definition in spec["key_terms"]
        )
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; allow about {minutes} minutes, with extra time for independent practice. Direct prerequisites: {prereq_text}

## Learning objectives

{tasks[2][0]} {tasks[5][0]} Use {terms} accurately when you explain a normal case and a failure case.

## Purpose, vocabulary and mental model

{spec["mental"]}

### Key terms

{key_terms}

## Syntax anatomy and mechanism

{spec["anatomy"]}

## Classroom execution and offline inputs

{execution}

## Worked example / walkthrough
"""
        for i, example in enumerate(spec["examples"], 1):
            heading, intro, lang, code, expected = example
            text += f"\n### Worked example {i}: {heading}\n\n{intro}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        contrast = spec["contrast"]
        text += (
            f"\n## Contrast case: {contrast['heading']}\n\n{contrast['setup']}\n\n"
            f"```{contrast['lang']}\n{contrast['code']}\n```\n\n{contrast['reading']}\n"
        )
        text += "\n## Six progressive exercises\n"
        if any(answer_task(prompt) for prompt, *_ in tasks):
            text += "\nExercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file. The others show the evidence to look for.\n"
        answers = f"# {key}: explanatory solutions\n\nOpen this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `{guide}`.\n"
        for i, ((prompt, answer, hint, why), reason) in enumerate(
            zip(tasks, spec["reasoning"], strict=True), 1
        ):
            text += f"\n### Exercise {i}: {prompt}\n\n"
            label = "Expected answer" if answer_task(prompt) else "Expected evidence"
            if label == "Expected evidence":
                text += f"**Expected evidence:** {answer}\n\n"
            text += f"**Progressive hint:** {hint}\n"
            answers += (
                f"\n## Exercise {i}: {prompt}\n\n**{label}:** {answer}\n\n"
                f"**Approach:** {reason['approach']}\n\n**Why:** {why}\n\n"
                f"**Plausible wrong approach:** {reason['pitfall']}\n\n"
                f"**How to verify:** {reason['verify']}\n"
            )
        text += (
            f"""
## Debugging and common mistakes

{spec["mistakes"]}

{FAILURE_NOTES[language]}

## Retrieval, transfer and next steps

Close the worked answers and explain {terms} without using the terms as their own definitions. Rebuild worked example 1 ({spec["examples"][0][0]}) from a blank {"worksheet" if language == "markdown" else "pad"}, then try one new value, one empty or missing case and one unusual boundary. State which result would disprove your explanation.

If you can reproduce the output but cannot explain why it happens, revisit {prereq_text if prerequisites else "the worked examples"}. A saved completion marker records your own progress; it is not a certification.

## Primary references

"""
            + "\n".join(f"- [{label}]({url})" for label, url in spec["refs"])
            + f"""

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {key}: {title}.
Read {guide} and {source}. Direct prerequisites: {prereq_text}
Ask what I predict, inspect my attempt and give one progressive hint.
Keep courses/web-development/solutions/ closed until I attempt or explicitly request comparison.
Distinguish browser observation, PHP CLI output and actual HTTP server evidence.
Do not install packages, start servers, transmit data or mark completion without my request.
Finish with a new boundary case and ask me to explain the mechanism in my own words.
```
"""
        )
        if language == "markdown":
            answers += "\n## Comparing your worksheet\n\nThis lesson has no executable reference. Compare your worksheet with the answers above. The optional lab in `courses/web-development/fixtures/php-http-lab/` gives real request evidence only when you deliberately run it.\n"
        else:
            limit = (
                "its success message is not an accessibility audit or proof of responsive behavior at every size"
                if language == "html"
                else "server lifecycle, persistence, concurrency and security need their own integration evidence"
            )
            answers += f"\n## Reference comparison\n\nOpen `{reference}` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; {limit}.\n"
        if language in {"html", "php"}:
            templates = HERE / "templates"
            files[ROOT / reference] = (templates / f"{key}_reference{extension}").read_text(
                encoding="utf-8"
            )
            starter = (templates / f"{key}_starter{extension}").read_text(encoding="utf-8")
        else:
            starter = (
                f"# {key}: learner worksheet\n\nReading and optional external lab only. Preserve your prediction before running anything.\n"
                + "".join(
                    f"\n## Exercise {i}: {prompt}\n\nPrediction:\n\nEvidence:\n\nExplanation and limitation:\n"
                    for i, (prompt, *_) in enumerate(tasks, 1)
                )
            )
        files[ROOT / guide] = text
        files[ROOT / source] = starter
        files[ROOT / explanation] = answers
        records.append(
            dict(
                id=key,
                status="authored",
                language=language,
                runtime_profile=runtime,
                guide_path=guide,
                source_path=source,
                solution_paths=([reference] if language != "markdown" else []) + [explanation],
                verification_id=None,
            )
        )
        inventory.append(
            dict(
                id=key,
                runtime_profile=runtime,
                reference_path=reference if language != "markdown" else None,
                marker=f"{key} reference checks passed" if language != "markdown" else None,
                expected_observation=spec.get("observation", tasks[2][1]),
                qualification="Requires actual runtime and manual observations; this inventory is not a receipt.",
            )
        )
    track = dict(
        schema_version=1,
        id="web-development",
        title="Web development: HTML, CSS and PHP",
        summary="60 lessons build accessible documents, responsive interfaces and tested PHP applications, from a first page to secure request handling and a deliberate deployment plan. HTML/CSS previews run offline; PHP examples use an isolated Linux CLI worker.",
        lessons=rows,
    )
    files[BASE / "track.json"] = json.dumps(track, indent=2)
    files[BASE / "lessons.json"] = json.dumps(
        dict(schema_version=1, track_id="web-development", lessons=records), indent=2
    )
    files[BASE / "fixtures/reference-inventory.json"] = json.dumps(
        dict(schema_version=1, lessons=inventory), indent=2
    )
    return {path: content.rstrip() + "\n" for path, content in files.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Report generated content drift without writing."
    )
    args = parser.parse_args()
    changed = []
    for path, content in artifacts().items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            changed.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and changed:
        raise SystemExit("Web curriculum generation drift:\n" + "\n".join(changed))
    print(
        f"Web curriculum: 60 complete bundles; {len(changed)} {'pending' if args.check else 'updated'} artifacts."
    )


if __name__ == "__main__":
    main()
