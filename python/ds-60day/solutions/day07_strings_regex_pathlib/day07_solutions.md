# Day 7 Solutions: Strings, Regular Expressions, and pathlib

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** From the supplied multiline text, extract email-shaped values, normalize them to lowercase, and return first-seen unique addresses. **Constraints:** use one bounded regex for extraction, then separate normalization and de-duplication steps; do not attempt full Internet-email validation. **Verify:** assert differently cased duplicates collapse to one lowercase address in first-seen order and a no-match string returns `[]`.

**Reasoning:** Extraction, normalization, and de-duplication are separate steps, so each can be checked on its own. The lookarounds `(?<![\w.+-])` and `(?![\w.-])` stop the pattern from starting or ending inside a longer token, which keeps surrounding punctuation such as the `;` out of the match. `casefold()` makes `Ada@Example.com` and `ADA@example.com` identical, and `dict.fromkeys` removes repeats while keeping first-seen order (a `set` would lose the order). The pattern recognizes an email shape only; trying to validate every legal address with one regex produces an unreadable pattern that still accepts mailboxes that do not exist.

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


text = "Contact Ada@Example.com or lin@example.com; ADA@example.com replied."
addresses = extract_emails(text)
assert addresses == ["ada@example.com", "lin@example.com"]
assert extract_emails("There is no address in this sentence.") == []
```

The bounded pattern extracts a useful email *shape* only. Normalization
and first-seen de-duplication are separate steps, and no claim is made
that the domain or mailbox exists.

### Exercise 2: worked answer

**Learner contract:** Write `plan_kebab_renames(folder: Path)` that returns source/destination pairs for regular files such as `Quarterly Report.CSV` without renaming them. **Rules:** normalize the stem to lowercase hyphen-separated words, preserve the suffix, skip unchanged names, and reject collisions including case-normalized collisions. **Verify:** use a temporary directory and inspect the complete plan before implementing a separate apply step.

**Reasoning:** The function only plans and never renames, which makes it safe to run and easy to test. Each target keeps the original suffix (`.CSV` stays uppercase, as the assertion shows), and the stem becomes lowercase words joined by hyphens. Collisions are checked against both the other planned targets and the files already present, comparing `casefold()` names because many file systems treat `A-B.txt` and `a-b.txt` as the same file. Unchanged names are filtered out so that applying the plan cannot touch them. Renaming inside the loop would be the risky alternative: a collision found halfway leaves the folder half renamed.

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
    proposals = [(path, path.with_name(kebab_stem(path.stem) + path.suffix)) for path in files]
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
    return [(source, target) for source, target in proposals if source.name != target.name]


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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Compare `"\n"` with `r"\n"` and predict their lengths and printed representations. **Progressive hint:** A raw string preserves the backslash needed by many regex patterns. **Verify:** Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2.

**Reasoning:** In an ordinary string, `\n` is an escape sequence for one newline character, so `len("\n")` is 1 and printing it moves to the next line. A raw string keeps the backslash as a character, so `r"\n"` has two characters, a backslash and `n`, and prints exactly that. Regular expressions use backslashes for their own escapes such as `\d` and `\w`, which is why patterns are written as raw strings: without `r`, Python would turn some sequences, such as `\b`, into different characters before the regex engine sees them. The shared implementation for Exercises 3-4 prints both `repr` values and asserts the lengths.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture. **Progressive hint:** The whole match and captured subparts are different values. **Verify:** Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match.

**Reasoning:** `group(0)` is the whole text the pattern matched, here `order-2048.csv`; a named group such as `(?P<order_id>\d+)` returns only the part inside its parentheses, `2048`. Naming the group keeps the code readable where the value is used (`match.group("order_id")` rather than `match.group(1)`). `re.fullmatch` returns `None` for a name like `invoice-2048.csv`, so the code must check for `None` before calling `.group`, otherwise it fails with `AttributeError`. The shared implementation for Exercises 3-4 asserts the whole match, the capture, and the non-match.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches. **Progressive hint:** Use `fullmatch` so extra suffix text cannot pass silently. **Verify:** Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected.

**Reasoning:** `fullmatch` requires the entire filename to fit the pattern, so `sales_2025-07-01_west.csv.bak` is rejected; `search` would accept it because it only needs a matching substring. The pattern encodes the date shape and an escaped dot before `csv`, so `sales_2025-7-01_west.csv` and a `.txt` suffix also fail. A shape check does not prove the date exists: `2025-02-30` matches the pattern, so a stricter answer passes the captured text to `date.fromisoformat`, which raises for impossible dates. The shared implementation for Exercises 5-7 asserts the valid case and three near misses.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML. **Progressive hint:** Use a constrained or non-greedy pattern only for a bounded format. **Verify:** Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser.

**Reasoning:** `.*` is greedy: it takes as much text as possible and then backs off only enough for the final `>` to match, so `<.*>` swallows everything from the first `<` to the last `>` on the line. Excluding angle brackets from the middle, `<[^<>]*>`, makes each match stop at the first closing `>` and yields the four separate tags; the non-greedy `<.*?>` works here too. Both are acceptable only because the input is a tiny, known format: real HTML has comments, attributes that contain `>`, and nesting that regular expressions cannot handle, so use `html.parser` or a parsing library for HTML. The shared implementation for Exercises 5-7 shows the greedy overmatch and the bounded repair.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`. **Progressive hint:** Separate planning/validation from filesystem mutation. **Verify:** Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed.

**Reasoning:** Planning before mutating turns a dangerous operation into a value that can be checked: the plan is built in memory, validated, and only then applied. `A B.txt` and `a-b.txt` both become `a-b.txt`, so the destinations collide, and comparing `casefold()` names catches this even on case-insensitive file systems. Because `plan_renames` raises before any rename is attempted, no file can end up half renamed. Detecting the collision after renaming the first file would leave a folder that neither the old nor the new naming scheme describes.

## Expanded mastery lab solutions

Use ordinary string operations for fixed syntax, regular expressions for patterns, and `pathlib` for portable path semantics.

### Shared implementation for Exercises 3-4: Escapes and groups

An ordinary `"\n"` is one newline character. The raw `r"\n"` is two characters:
a backslash and `n`. `group(0)` is the full match; a named group returns only
its captured portion.

```python
import re

newline = "\n"
raw = r"\n"
print(len(newline), repr(newline))
print(len(raw), repr(raw))
assert (len(newline), len(raw)) == (1, 2)

ORDER_FILE = re.compile(r"order-(?P<order_id>\d+)\.csv")
match = ORDER_FILE.fullmatch("order-2048.csv")
assert match is not None
assert match.group(0) == "order-2048.csv"
assert match.group("order_id") == "2048"
assert ORDER_FILE.fullmatch("invoice-2048.csv") is None
```

### Shared implementation for Exercises 5-7: Parse and plan before mutating paths

```python
from __future__ import annotations

import re
from pathlib import Path

REPORT_PATTERN = re.compile(r"sales_(?P<date>\d{4}-\d{2}-\d{2})_(?P<region>[a-z]+)\.csv")


def parse_report_name(path: Path) -> tuple[str, str]:
    """Return (date, region) from one complete, valid report filename."""

    match = REPORT_PATTERN.fullmatch(path.name)
    if match is None:
        raise ValueError(f"unexpected report name: {path.name!r}")
    return match.group("date"), match.group("region")


assert parse_report_name(Path("sales_2025-07-01_west.csv")) == ("2025-07-01", "west")
for near_miss in (
    "sales_2025-07-01_west.csv.bak",
    "sales_2025-7-01_west.csv",
    "sales_2025-07-01_west.txt",
):
    try:
        parse_report_name(Path(near_miss))
    except ValueError:
        pass
    else:
        raise AssertionError(f"{near_miss} should be rejected")

greedy = re.findall(r"<.*>", "<b>one</b><i>two</i>")
assert greedy == ["<b>one</b><i>two</i>"]  # one overlong match
bounded_tags = re.findall(r"<[^<>]*>", "<b>one</b><i>two</i>")
assert bounded_tags == ["<b>", "</b>", "<i>", "</i>"]


def kebab_stem(stem: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", stem.casefold())
    return "-".join(words)


def plan_renames(paths: list[Path]) -> dict[Path, Path]:
    """Return a collision-free plan without touching the filesystem."""

    plan = {path: path.with_name(f"{kebab_stem(path.stem)}{path.suffix.lower()}") for path in paths}
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
