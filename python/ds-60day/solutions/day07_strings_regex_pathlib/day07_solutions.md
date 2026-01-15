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
