# Day 07 — Solutions: Strings, Regex, Pathlib

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **text normalization, bounded pattern matching, and portable paths**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **text normalization, bounded pattern matching, and portable paths** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** From the supplied multiline text, extract email-shaped values, normalize them to lowercase, and return first-seen unique addresses. **Constraints:** use one bounded regex for extraction, then separate normalization and de-duplication steps; do not attempt full Internet-email validation. **Verify:** assert differently cased duplicates collapse to one lowercase address in first-seen order and a no-match string returns `[]`.

**Reasoning:** Implement this exact contract as written: From the supplied multiline text, extract email-shaped values, normalize them to lowercase, and return first-seen unique addresses. Constraints: use one bounded regex for extraction, then separate normalization and de-duplication steps; do not attempt full Internet-email validation. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert differently cased duplicates collapse to one lowercase address in first-seen order and a no-match string returns `[]`. That connects the answer to text normalization, bounded pattern matching, and portable paths.

```python
import re

EMAIL_SHAPE = re.compile(
    r"(?<![\w.+-])[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])"
)


def extract_emails(text: str) -> list[str]:
    matches = EMAIL_SHAPE.findall(text)
    normalized = [match.casefold() for match in matches]
    return list(dict.fromkeys(normalized))


text = (
    "Contact Ada@Example.com or lin@example.com; "
    "ADA@example.com replied."
)
addresses = extract_emails(text)
assert addresses == ["ada@example.com", "lin@example.com"]
assert extract_emails("There is no address in this sentence.") == []
```

The bounded pattern extracts a useful email *shape* only. Normalization
and first-seen de-duplication are separate steps, and no claim is made
that the domain or mailbox exists.

**Verification evidence:** assert differently cased duplicates collapse to one lowercase address in first-seen order and a no-match string returns `[]`.

### Exercise 2 — worked answer

**Learner contract:** Write `plan_kebab_renames(folder: Path)` that returns source/destination pairs for regular files such as `Quarterly Report.CSV` without renaming them. **Rules:** normalize the stem to lowercase hyphen-separated words, preserve the suffix, skip unchanged names, and reject collisions including case-normalized collisions. **Verify:** use a temporary directory and inspect the complete plan before implementing a separate apply step.

**Reasoning:** Implement this exact contract as written: Write `plan_kebab_renames(folder: Path)` that returns source/destination pairs for regular files such as `Quarterly Report.CSV` without renaming them. Rules: normalize the stem to lowercase hyphen-separated words, preserve the suffix, skip unchanged names, and reject collisions including case-normalized collisions. Keep the prompt's named data and constraints visible in the code, then establish this specific result: use a temporary directory and inspect the complete plan before implementing a separate apply step. That connects the answer to text normalization, bounded pattern matching, and portable paths.

```python
import re
from pathlib import Path
import tempfile


def kebab_stem(stem: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def plan_kebab_renames(folder: Path) -> list[tuple[Path, Path]]:
    files = sorted(
        (path for path in folder.iterdir() if path.is_file()),
        key=lambda path: path.name.casefold(),
    )
    proposals = [
        (path, path.with_name(kebab_stem(path.stem) + path.suffix))
        for path in files
    ]
    targets: dict[str, Path] = {}
    source_names = {path.name.casefold(): path for path in files}
    for source, target in proposals:
        key = target.name.casefold()
        prior = targets.get(key)
        occupied = source_names.get(key)
        if prior is not None and prior != source:
            raise ValueError(f"rename targets collide at {target.name!r}")
        if occupied is not None and occupied != source:
            raise ValueError(f"target already exists: {target.name!r}")
        targets[key] = source
    return [
        (source, target)
        for source, target in proposals
        if source.name != target.name
    ]


with tempfile.TemporaryDirectory() as temporary:
    folder = Path(temporary)
    source = folder / "Quarterly Report.CSV"
    unchanged = folder / "notes.txt"
    source.write_text("quarter,value\nQ1,10\n", encoding="utf-8")
    unchanged.write_text("keep", encoding="utf-8")
    planned = plan_kebab_renames(folder)
    assert planned == [(source, folder / "quarterly-report.CSV")]
    assert source.exists() and unchanged.exists()

    (folder / "A B.txt").write_text("one", encoding="utf-8")
    (folder / "a-b.TXT").write_text("two", encoding="utf-8")
    try:
        plan_kebab_renames(folder)
    except ValueError as error:
        assert "collide" in str(error) or "exists" in str(error)
    else:
        raise AssertionError("case-normalized collision should fail")
```

Applying `Path.rename` is a separate, deliberate mutation after this
complete plan passes collision checks.

**Verification evidence:** use a temporary directory and inspect the complete plan before implementing a separate apply step.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Compare `"\n"` with `r"\n"` and predict their lengths and printed representations. **Progressive hint:** A raw string preserves the backslash needed by many regex patterns. **Verify:** Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2.

**Reasoning:** Predict this named state change before running it: Prediction: Compare `"\n"` with `r"\n"` and predict their lengths and printed representations. Progressive hint: A raw string preserves the backslash needed by many regex patterns. Then compare the prediction with this proof target: Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2. This makes text normalization, bounded pattern matching, and portable paths observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture. **Progressive hint:** The whole match and captured subparts are different values. **Verify:** Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture. Progressive hint: The whole match and captured subparts are different values. Record the named value, shape, label, or iterator position needed to establish: Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match. The trace exposes text normalization, bounded pattern matching, and portable paths directly.

**Evidence to locate in the grouped implementation:** Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches. **Progressive hint:** Use `fullmatch` so extra suffix text cannot pass silently. **Verify:** Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches. Progressive hint: Use `fullmatch` so extra suffix text cannot pass silently. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected. That connects the answer to text normalization, bounded pattern matching, and portable paths.

**Evidence to locate in the grouped implementation:** Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML. **Progressive hint:** Use a constrained or non-greedy pattern only for a bounded format. **Verify:** Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML. Progressive hint: Use a constrained or non-greedy pattern only for a bounded format. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser. The diagnosis depends on text normalization, bounded pattern matching, and portable paths.

**Evidence to locate in the grouped implementation:** Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`. **Progressive hint:** Separate planning/validation from filesystem mutation. **Verify:** Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`. Progressive hint: Separate planning/validation from filesystem mutation. Values below, at, and above the named boundary must produce the evidence Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed. Those cases show how text normalization, bounded pattern matching, and portable paths behaves at its edge.

**Evidence to locate in the grouped implementation:** Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed.

## Expanded mastery lab solutions

Use ordinary string operations for fixed syntax, regular expressions for patterns, and `pathlib` for portable path semantics.

### Shared implementation for Exercises 3–4 — Escapes and groups

An ordinary `"\n"` is one newline character. The raw `r"\n"` is two characters:
a backslash and `n`. `group(0)` is the full match; a named group returns only
its captured portion.

### Shared implementation for Exercises 5–7 — Parse and plan before mutating paths

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
