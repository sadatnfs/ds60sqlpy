"""Connected textbook openings and chapter bridges for llm-001 through llm-024."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from runpy import run_path
from typing import cast

BASE = Path(__file__).resolve().parent / "textbook_foundations"
START = "<!-- textbook-foundations-start -->"
END = "<!-- textbook-foundations-end -->"
RUN_START = "<!-- textbook-foundations-run-start -->"
RUN_END = "<!-- textbook-foundations-run-end -->"

REBASE_LINKS = cast(
    Callable[[str, Path, Path], str],
    run_path(str(Path(__file__).with_name("textbook_links.py")))["rebase_links"],
)


def fenced_blocks(document: str) -> list[str]:
    return re.findall(r"^```[^\n]*\n.*?^```[ \t]*$", document, re.M | re.S)


def enrich_guide(identity: str, document: str) -> str:
    match = re.fullmatch(r"llm-(\d{3})", identity)
    if match is None or not 1 <= int(match.group(1)) <= 24:
        return document
    path = BASE / f"{identity}.md"
    raw = path.read_text(encoding="utf-8")
    if raw.count("<!-- bridge -->") != 1 or "\u2014" in raw or "```" in raw:
        raise ValueError("Textbook source requires prose, one bridge and no code fences")
    raw = REBASE_LINKS(raw, path, BASE.parent.parent / "guides" / f"{identity}.md")
    opening, bridge = (part.strip() for part in raw.split("<!-- bridge -->"))
    if not opening.startswith("## "):
        raise ValueError("Textbook opening requires a topic-specific heading")
    opening = "#" + opening  # Keep the topic heading inside the existing purpose section.
    before = fenced_blocks(document)
    pattern = re.compile(r"^## Purpose and mental model\n(.*?)(?=^## |\Z)", re.M | re.S)
    found = pattern.search(document)
    if found is None:
        raise ValueError("Missing purpose section for " + identity)
    existing = found.group(1)
    marker = "<!-- reviewed-mechanism-start -->"
    retained = existing[existing.index(marker) :].strip() if marker in existing else ""
    replacement = (
        "## Purpose and mental model\n\n"
        + START
        + "\n\n"
        + opening
        + "\n\n"
        + END
        + "\n\n"
        + (retained + "\n\n" if retained else "")
    )
    document = document[: found.start()] + replacement + document[found.end() :]
    next_pattern = re.compile(r"^## Next step\n.*?(?=^## |\Z)", re.M | re.S)
    if not next_pattern.search(document):
        raise ValueError("Missing chapter bridge section for " + identity)
    document = next_pattern.sub(lambda _: "## Next step\n\n" + bridge + "\n\n", document, count=1)
    if 2 <= int(match.group(1)) <= 9:
        document = re.sub(
            re.escape(RUN_START) + r".*?" + re.escape(RUN_END) + r"\n*", "", document, flags=re.S
        )
        run_heading = re.search(r"^## How to run[^\n]*\n", document, re.M)
        if run_heading is None:
            raise ValueError("Missing pilot run instructions for " + identity)
        directions = (
            f"Open the [Docker classroom](../../../docs/docker-classroom.md), choose **Journeys** "
            f"and select `{identity}` with its `python-core` worker. Use the saved learner pad for "
            "your complete scratch program and keep the sequential A+B example contract below. "
            "The worker supplies Python and NumPy; no host installation is required. "
            "The native interpreter commands below are an optional alternative "
            "for an already prepared environment."
        )
        position = run_heading.end()
        document = (
            document[:position]
            + "\n"
            + RUN_START
            + "\n\n"
            + directions
            + "\n\n"
            + RUN_END
            + "\n"
            + document[position:]
        )
    # Repair an observed prose-only split without altering code or copy-ready prompts.
    chunks = re.split(r"(^```[^\n]*\n.*?^```[ \t]*$)", document, flags=re.M | re.S)
    for index in range(0, len(chunks), 2):
        chunks[index] = chunks[index].replace("index ing", "indexing")
    document = "".join(chunks)
    if fenced_blocks(document) != before:
        raise ValueError("Textbook prose changed a fenced program or prompt for " + identity)
    return document
