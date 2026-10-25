"""Rebuild the offline HTML, CSS and PHP curriculum without running learner code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
HERE = Path(__file__).resolve().parent


def specs() -> list[dict]:
    payload = json.loads((HERE / "chapters.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Unknown web authoring schema")
    result = payload["chapters"]
    if len(result) != 60 or [item["n"] for item in result] != list(range(1, 61)):
        raise ValueError("Web chapter identities changed unexpectedly")
    return result


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
                outcome=tasks[5][0],
                lab=tasks[2][0],
                verification=tasks[2][1],
            )
        )
        if language == "html":
            execution = """Choose **HTML browser preview** in the classroom. The pad is one complete HTML document with embedded CSS and, where taught, embedded JavaScript. Its preview is isolated from the classroom and recreated on each run. It does not contact a server, submit real forms, read cookies, fetch assets or load a CDN. All fixtures are inline and synthetic. The browser uses its native HTML parser, so classic-script ordering, shared lexical bindings, inline modules and real DOMContentLoaded/load events keep their browser semantics. External module imports remain blocked. Navigation metadata such as base and meta http-equiv is rejected explicitly. On any supported host, the browser renders the document while Docker serves the classroom. No host compiler is needed.

Run your own source after implementing the task. A reference's checks inspect only the named initial conditions. Its success message is not a full accessibility audit, proof of responsive behavior at every size, or evidence that you implemented the solution yourself. Inspect actual output after keyboard input, resizing and changes. Save your source before comparing with a reference. For visual experiments, explicitly turn on Live preview: the page refreshes after a short pause in typing, while Pause updates keeps the last rendered version and Stop preview cancels pending refreshes. Desktop, tablet and phone presets resize the same preview without rerunning it. Automatic previews do not create saved runs; choose Save observation or Run when you want to retain an exact source-and-output record. Changing lessons, opening history or reloading turns live execution off. The document and its CSS share one saved pad; HTML and CSS remain different languages within that artifact."""
        elif language == "php":
            execution = """Choose the **PHP CLI** worker in the classroom. The pad is staged as `main.php` and executes as a bounded Linux process, with prepared PHP and PDO SQLite. Write `<?php` at the beginning; a pure PHP file needs no closing tag. Output appears as text. PHP-generated HTML is escaped output here, not automatically injected into a browser. No host PHP installation is required for the Docker route.

The supplied requests, identities, sessions and database fixtures are synthetic local inputs. CLI runs are fresh processes, not persistent HTTP requests. A dictionary that represents a cookie or request is not a real browser cookie. SQLite examples use an in-memory database and do not connect to the classroom PostgreSQL service. Network servers, uploads, mail, Composer downloads and production credentials are outside this pad's contract. Later delivery lessons provide an explicitly separate loopback server lab. A successful function test does not qualify that server integration."""
        else:
            execution = """This is a reading and design worksheet with an optional external project lab. The classroom saves the worksheet but does not start an HTTP server, install packages or control Docker from its pad. Work from the supplied synthetic examples first. A command is a proposal until you deliberately execute it against your own disposable local project. The maintained optional fixture is `courses/web-development/fixtures/php-http-lab/`; read its README before preparing it. Do not expose that learning server to the internet or reuse real account data."""
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; allow about {minutes} minutes, with extra time for independent practice. Direct prerequisites: {prereq_text}

## Learning objectives

{tasks[2][0]} {tasks[5][0]} Explain the mechanism, a normal case and a failure case in your own words, then retain source and observations separately.

## Purpose, vocabulary and mental model

{spec["mental"]}

## Syntax anatomy and mechanism

{spec["anatomy"]}

## Classroom execution and offline inputs

{execution}

## Worked example / walkthrough
"""
        for i, example in enumerate(spec["examples"], 1):
            heading, intro, lang, code, expected = example
            text += f"\n### Worked example {i}: {heading}\n\n{intro}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += "\n## Six progressive exercises\n"
        hints = [
            "Trace the smallest example before editing. Name which values are source and which are observations.",
            "Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.",
            "Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.",
            "Keep the failing input. Identify the first layer where the observed result differs from the intended contract.",
            "Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.",
            "Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.",
        ]
        answers = f"# {key}: explanatory solutions\n\nCompare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.\n\n## Why the mechanism works\n\n{spec['mental']}\n\n{spec['anatomy']}\n"
        for i, (prompt, answer) in enumerate(tasks, 1):
            text += f"\n### Exercise {i}: {prompt}\n\n**Expected evidence:** {answer}\n\n**Progressive hint:** {hints[i - 1]}\n"
            answers += f"\n## Exercise {i}: {prompt}\n\n{answer}\n\n{hints[i - 1]}\n"
        text += (
            f"""
## Debugging and common mistakes

{spec["mistakes"]}

Keep the source that produced the failure, the relevant input or viewport, and the actual observation. Repair one cause and repeat the original case before adding a new one. A browser can recover malformed HTML, silently ignore a CSS declaration or display a plausible layout with the wrong reading order. PHP can produce correct-looking text while missing an invalid-input branch. A successful parse or an initial reference marker therefore answers a narrower question than the full lesson objective.

## Retrieval, transfer and next steps

Close the worked answers and explain {", ".join(spec["terms"][:3])} without using their names as definitions. Reconstruct the central example from a blank pad or worksheet. Use one new value, one empty or missing case and one adversarial or unusual boundary. State which result would disprove your explanation. When a behavior belongs to the browser, observe it in the browser; when it belongs to an HTTP server, keep that evidence separate from a CLI simulation.

Before moving on, keep a short learning record: your prediction, source revision, actual result, explanation and unresolved limitation. Revisit a direct prerequisite if you can reproduce output but cannot explain the mechanism. The path has milestones, not a fixed daily schedule, and a saved completion marker is a personal progress record rather than a professional certification.

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
        answers += "\n## Reference comparison and limits\n\nRead the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.\n"
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
                    for i, (prompt, _) in enumerate(tasks, 1)
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
