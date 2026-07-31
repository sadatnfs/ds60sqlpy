# Day 07 — Solutions: Strings, Regex, Pathlib

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**text normalization, bounded pattern matching, and portable paths**.

Strings are immutable sequences of Unicode characters. Ordinary string
methods are the clearest tool for fixed separators and normalization.
A regular expression describes a family of text shapes; it should be
used when the format truly varies according to a pattern, not as a
default replacement for simple string operations.

A filesystem path is structured data, not just a string with slashes.
`pathlib.Path` joins components and exposes names, stems, suffixes, and
parent folders using the host operating system's rules. Plan and
validate a rename before mutating files, preserve suffixes, and detect
collisions.

### Vocabulary used in the worked answers

- **Unicode:** the character system Python strings represent.
- **normalization:** turning equivalent input forms into one chosen representation.
- **regular expression:** a pattern language for matching bounded text formats.
- **capture group:** a named or numbered subpart retained from a regex match.
- **path component:** one structured folder or filename element.
- **suffix:** a final filename extension such as `.csv`.

### Reference pattern 1 — Extract named fields from a bounded filename

Use `fullmatch` when extra text must be rejected.

```python
import re

pattern = re.compile(
    r"sales_(?P<date>\d{4}-\d{2}-\d{2})_(?P<region>[a-z]+)\.csv"
)
match = pattern.fullmatch("sales_2025-07-01_west.csv")
match.groupdict() if match else None
```

**Expected observation:** `{'date': '2025-07-01', 'region': 'west'}`. A filename with extra trailing text returns `None`.

### Reference pattern 2 — Build a path without platform-specific separators

Let `Path` own path joining and filename fields.

```python
from pathlib import Path

report = Path("artifacts") / "daily sales.csv"
(report.parent, report.stem, report.suffix, report.with_suffix(".json"))
```

**Expected observation:** A tuple of `Path` values is displayed. On every supported operating system the components remain meaningful without hard-coded `/` or `\` separators.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** From the supplied multiline text, extract email-shaped values, normalize them to lowercase, and return first-seen unique addresses. **Constraints:** use one bounded regex for extraction, then separate normalization and de-duplication steps; do not attempt full Internet-email validation. **Verify:** include duplicate spellings with different case and text containing no match.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies text normalization, bounded pattern matching, and portable paths.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** include duplicate spellings with different case and text containing no match.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Write `plan_kebab_renames(folder: Path)` that returns source/destination pairs for regular files such as `Quarterly Report.CSV` without renaming them. **Rules:** normalize the stem to lowercase hyphen-separated words, preserve the suffix, skip unchanged names, and reject collisions including case-normalized collisions. **Verify:** use a temporary directory and inspect the complete plan before implementing a separate apply step.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies text normalization, bounded pattern matching, and portable paths.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** use a temporary directory and inspect the complete plan before implementing a separate apply step.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Compare `"\n"` with `r"\n"` and predict their lengths and printed representations. **Progressive hint:** A raw string preserves the backslash needed by many regex patterns. **Verify:** Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying text normalization, bounded pattern matching, and portable paths.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture. **Progressive hint:** The whole match and captured subparts are different values. **Verify:** Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the text normalization, bounded pattern matching, and portable paths model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches. **Progressive hint:** Use `fullmatch` so extra suffix text cannot pass silently. **Verify:** Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies text normalization, bounded pattern matching, and portable paths.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML. **Progressive hint:** Use a constrained or non-greedy pattern only for a bounded format. **Verify:** Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in text normalization, bounded pattern matching, and portable paths.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`. **Progressive hint:** Separate planning/validation from filesystem mutation. **Verify:** Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from text normalization, bounded pattern matching, and portable paths.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Edge case:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.

**Solution evidence to inspect:** Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed.
<!-- END BEGINNER SOLUTION REVIEW -->

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
