"""Per-exercise solution reasoning for Kubernetes explanatory solutions.

``reasoning.json`` maps a lesson ID to six entries, one per exercise, each with
four non-empty parts: ``approach``, ``why``, ``pitfall`` and ``verify``. Both
generators call :func:`render` so each exercise section of
``solutions/<key>_solutions.md`` ends with a ``**Solution reasoning**`` list,
and :func:`apply` updates an existing solution in place without rebuilding the
rest of it.
"""

from __future__ import annotations

import json
import re
import sys
from functools import cache
from pathlib import Path

SOURCE = Path(__file__).with_name("reasoning.json")
HEADING = "**Solution reasoning**"
EXERCISES = 6
PARTS = (
    ("approach", "Approach"),
    ("why", "Why it is correct"),
    ("pitfall", "Plausible wrong approach"),
    ("verify", "How to verify"),
)
DASHES = re.compile("[\u2013\u2014]")


@cache
def load() -> dict[str, list[dict[str, str]]]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def validate(data: dict[str, list[dict[str, str]]] | None = None) -> list[str]:
    """Return problems with the reasoning source; an empty list means valid."""

    data = load() if data is None else data
    problems = []
    keys = {name for name, _ in PARTS}
    for key, entries in data.items():
        if not re.fullmatch(r"k8s-\d{3}", key):
            problems.append(f"{key}: lesson ID must look like k8s-NNN")
        if len(entries) != EXERCISES:
            problems.append(f"{key}: needs {EXERCISES} exercises, has {len(entries)}")
        for i, entry in enumerate(entries, 1):
            if set(entry) != keys:
                problems.append(f"{key} exercise {i}: needs exactly {sorted(keys)}")
                continue
            for name, value in entry.items():
                if not value.strip() or "\n" in value:
                    problems.append(f"{key} exercise {i}: {name} must be one non-empty line")
                elif not value.rstrip().endswith((".", ")", "`")):
                    problems.append(f"{key} exercise {i}: {name} must end a sentence")
                if DASHES.search(value):
                    problems.append(f"{key} exercise {i}: {name} uses an en or em dash")
    return problems


def render(key: str, exercise: int) -> str:
    """Return the Markdown reasoning block for one exercise or an empty string."""

    entries = load().get(key, [])
    if not 1 <= exercise <= len(entries):
        return ""
    entry = entries[exercise - 1]
    bullets = "\n".join(f"- **{label}:** {entry[name]}" for name, label in PARTS)
    return f"{HEADING}\n\n{bullets}"


def apply(text: str, key: str) -> str:
    """Insert or replace the reasoning block at the end of each exercise section."""

    for exercise in range(1, len(load().get(key, [])) + 1):
        block = render(key, exercise)
        heading = f"\n## Exercise {exercise}: "
        if heading not in text:
            raise ValueError(f"{key}: no Exercise {exercise} section in the solution")
        start = text.index(heading) + 1
        end = text.find("\n## ", start)
        end = len(text) if end == -1 else end + 1
        section = text[start:end]
        existing = section.find(f"\n{HEADING}\n")
        if existing != -1:
            section = section[: existing + 1]
        section = section.rstrip("\n") + f"\n\n{block}\n"
        section += "" if end == len(text) else "\n"
        text = text[:start] + section + text[end:]
    return text


if __name__ == "__main__":
    issues = validate()
    print("\n".join(issues) or f"{len(load())} lessons valid")
    sys.exit(1 if issues else 0)
