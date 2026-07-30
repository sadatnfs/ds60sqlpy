# Day 07 — Solutions: Strings, Regex, Pathlib

We provide robust, beginner-friendly solutions with careful file handling.

Contents
- Exercise 1: Extract all emails from a multiline string
- Exercise 2: Rename files in a directory to kebab-case using pathlib

---

Exercise 1 — Extract all emails (unique, lowercased)
```python
import re
from typing import Iterable, Set

EMAIL = re.compile(r"[\w.%-]+@[\w.-]+\.[A-Za-z]{2,}")

def extract_emails(lines: Iterable[str]) -> Set[str]:
    """Return a set of normalized (lowercased) emails found across lines.

    Uses a compiled regex. Lowercases to normalize case differences.
    """
    found: set[str] = set()
    for line in lines:
        for m in EMAIL.findall(line):    # 1) find all matches per line
            found.add(m.lower())         # 2) normalize
    return found

# Demo
text = """
Contact alice@example.com, Bob@Example.com.
Backup: team@sub.domain.org
"""
assert extract_emails(text.splitlines()) == {"alice@example.com","bob@example.com","team@sub.domain.org"}
```
Notes
- The pattern is intentionally simple; real-world email validation is more complex. For production, consider `email.utils` or well-tested libraries.

---

Exercise 2 — Rename files to kebab-case
Goal: Rename files like `Report (Jan).CSV` → `report-jan.csv` in a target directory.

```python
from pathlib import Path
import re

_slug_chars = re.compile(r"[^a-z0-9-]+")
_multi_dash = re.compile(r"-{2,}")


def to_kebab(stem: str) -> str:
    """Convert a filename stem to kebab-case (lowercase a-z0-9-)."""
    s = stem.lower()                               # 1) normalize case
    s = s.replace("_", "-").replace(" ", "-")    # 2) unify separators
    s = _slug_chars.sub("-", s)                    # 3) drop/replace unsafe chars
    s = _multi_dash.sub("-", s).strip("-")         # 4) collapse dashes, trim edges
    return s or "file"                              # 5) fallback if empty


def rename_dir_to_kebab(dirpath: Path, *, dry_run: bool = True) -> list[tuple[Path, Path]]:
    """Rename files in dirpath to kebab-case; return list of (old, new) paths.

    - Keeps file extension unchanged
    - Skips if the target name already exists
    - dry_run=True prints planned changes without renaming
    """
    changes: list[tuple[Path, Path]] = []
    for p in dirpath.iterdir():
        if not p.is_file():
            continue
        new_stem = to_kebab(p.stem)
        target = p.with_name(new_stem + p.suffix.lower())
        if target == p:
            continue                       # already kebab-case
        if target.exists():
            print(f"skip (exists): {target}")
            continue
        changes.append((p, target))
        if dry_run:
            print(f"DRY-RUN: {p.name} -> {target.name}")
        else:
            p.rename(target)
            print(f"renamed: {p.name} -> {target.name}")
    return changes

# Demo (dry run)
# rename_dir_to_kebab(Path('reports'), dry_run=True)
```
Safety checklist
- Use dry-run first to preview
- Preserve extensions case-insensitively
- Skip collisions to avoid overwriting existing files

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Extract every email address from multiline text, then produce unique, lowercase results. **Hint:** first get all matches; normalize and de-duplicate as separate steps.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Rename files in a chosen directory to kebab-case with `pathlib`. **Hint:** calculate and print every source/destination pair before calling `rename`; preserve each suffix and handle name collisions.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Compare `"\n"` with `r"\n"` and predict their lengths and printed representations.

**Reasoning checkpoint:** A raw string preserves the backslash needed by many regex patterns. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture.

**Reasoning checkpoint:** The whole match and captured subparts are different values. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches.

**Reasoning checkpoint:** Use `fullmatch` so extra suffix text cannot pass silently. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML.

**Reasoning checkpoint:** Use a constrained or non-greedy pattern only for a bounded format. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`.

**Reasoning checkpoint:** Separate planning/validation from filesystem mutation. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Use ordinary string operations for fixed syntax, regular expressions for patterns, and `pathlib` for portable path semantics.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Escapes and groups

An ordinary `"\n"` is one newline character. The raw `r"\n"` is two characters:
a backslash and `n`. `group(0)` is the full match; a named group returns only
its captured portion.

### Practices 3–5 — Parse and plan before mutating paths

```python
from __future__ import annotations

import re
from pathlib import Path

REPORT_PATTERN = re.compile(
    r"sales_(?P<date>\d{4}-\d{2}-\d{2})_(?P<region>[a-z]+)\.csv"
)


def parse_report_name(path: Path) -> tuple[str, str]:
    """Return (date, region) from one complete, valid report filename."""

    match = REPORT_PATTERN.fullmatch(path.name)
    if match is None:
        raise ValueError(f"unexpected report name: {path.name!r}")
    return match.group("date"), match.group("region")


assert parse_report_name(Path("sales_2025-07-01_west.csv")) == (
    "2025-07-01", "west"
)

bounded_tags = re.findall(r"<[^<>]*>", "<b>one</b><i>two</i>")
assert bounded_tags == ["<b>", "</b>", "<i>", "</i>"]


def kebab_stem(stem: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", stem.casefold())
    return "-".join(words)


def plan_renames(paths: list[Path]) -> dict[Path, Path]:
    """Return a collision-free plan without touching the filesystem."""

    plan = {path: path.with_name(f"{kebab_stem(path.stem)}{path.suffix.lower()}")
            for path in paths}
    destinations = list(plan.values())
    if len({destination.name.casefold() for destination in destinations}) != len(destinations):
        raise ValueError("rename destinations collide")
    return plan


try:
    plan_renames([Path("A B.txt"), Path("a-b.txt")])
except ValueError as error:
    assert "collide" in str(error)
else:
    raise AssertionError("the collision should be detected before renaming")
```

Regular expressions are appropriate for these deliberately small filename/tag
grammars; they are not a replacement for a standards-aware HTML parser.
