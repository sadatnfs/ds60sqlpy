"""Lesson-specific Key terms for Kubernetes guides.

``key_terms.json`` maps a lesson ID to three to five ``{"term", "definition"}``
entries. Both generators call :func:`render` so the block lands at the end of
the guide's vocabulary section, and :func:`apply` updates an existing guide in
place without rebuilding the rest of it.
"""

from __future__ import annotations

import json
import re
import sys
from functools import cache
from pathlib import Path

SOURCE = Path(__file__).with_name("key_terms.json")
HEADING = "### Key terms"
VOCABULARY_HEADINGS = (
    "## Vocabulary and concepts",
    "## Purpose, vocabulary and mental model",
)
MIN_TERMS = 3
MAX_TERMS = 5
DASHES = re.compile("[\u2013\u2014]")


@cache
def load() -> dict[str, list[dict[str, str]]]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def validate(data: dict[str, list[dict[str, str]]] | None = None) -> list[str]:
    """Return problems with the Key terms source; an empty list means valid."""

    data = load() if data is None else data
    problems = []
    for key, entries in data.items():
        if not re.fullmatch(r"k8s-\d{3}", key):
            problems.append(f"{key}: lesson ID must look like k8s-NNN")
        if not MIN_TERMS <= len(entries) <= MAX_TERMS:
            problems.append(f"{key}: needs {MIN_TERMS} to {MAX_TERMS} terms, has {len(entries)}")
        terms = [entry.get("term", "") for entry in entries]
        if len({term.lower() for term in terms}) != len(terms):
            problems.append(f"{key}: duplicate term")
        for entry in entries:
            term, definition = entry.get("term", ""), entry.get("definition", "")
            if set(entry) != {"term", "definition"} or not term or not definition:
                problems.append(f"{key}: each entry needs only a term and a definition")
            if "*" in term or ":" in term or "\n" in term + definition:
                problems.append(f"{key}: {term!r} must be a single plain line")
            if not definition.endswith("."):
                problems.append(f"{key}: definition of {term!r} must end with a period")
            if DASHES.search(term + definition):
                problems.append(f"{key}: {term!r} uses an en or em dash")
    return problems


def render(key: str) -> str:
    """Return the Markdown Key terms block for ``key`` or an empty string."""

    entries = load().get(key, [])
    if not entries:
        return ""
    bullets = "\n".join(f"- **{e['term']}:** {e['definition']}" for e in entries)
    return f"{HEADING}\n\n{bullets}"


def apply(text: str, key: str) -> str:
    """Insert or replace the Key terms block at the end of the vocabulary section."""

    block = render(key)
    if not block:
        return text
    heading = next((h for h in VOCABULARY_HEADINGS if f"\n{h}\n" in text), None)
    if heading is None:
        raise ValueError(f"{key}: no vocabulary section to extend")
    start = text.index(f"\n{heading}\n") + len(heading) + 2
    end = text.find("\n## ", start)
    end = len(text) if end == -1 else end + 1
    section = text[start:end]
    existing = section.find(f"{HEADING}\n")
    if existing != -1:
        section = section[:existing]
    section = section.rstrip("\n") + f"\n\n{block}\n\n"
    if end == len(text):
        section = section.rstrip("\n") + "\n"
    return text[:start] + section + text[end:]


if __name__ == "__main__":
    issues = validate()
    print("\n".join(issues) or f"{len(load())} lessons valid")
    sys.exit(1 if issues else 0)
