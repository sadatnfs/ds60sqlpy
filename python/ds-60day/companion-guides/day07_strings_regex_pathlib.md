# Day 7 — Strings, Regular Expressions, and `pathlib`

**Level:** Beginner

Text and paths are boundary data. Normalize deliberately, validate narrowly,
and let `pathlib` handle operating-system path rules.

## Learning objectives

By the end of this lesson, you can:

- normalize and split strings without mutating the original value;
- use a raw-string regular expression with groups;
- distinguish regex search, matching, and substitution;
- construct, inspect, and rename paths with `pathlib.Path`.

## Prerequisites

Complete Day 6 (`python-06`): lists, sets, dictionaries, and iteration.

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day07_strings_regex_pathlib.md`, then open `python/ds-60day/notebooks/day07_strings_regex_pathlib.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 7 — strings, regular expressions, and `pathlib` to practice text normalization, bounded pattern matching, and portable paths
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **Unicode:** the character system Python strings represent.
- **normalization:** turning equivalent input forms into one chosen representation.
- **regular expression:** a pattern language for matching bounded text formats.
- **capture group:** a named or numbered subpart retained from a regex match.
- **path component:** one structured folder or filename element.
- **suffix:** a final filename extension such as `.csv`.

### Syntax anatomy

`pattern.fullmatch(text)` requires the entire input to match, while
`search` can find a match inside longer text. Raw string syntax such as
`r"\d{4}"` preserves backslashes for the regex engine. In
`folder / "report.csv"`, `/` is `Path` joining syntax, not division.

### Worked example 1 — Extract named fields from a bounded filename

Use `fullmatch` when extra text must be rejected. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import re

pattern = re.compile(
    r"sales_(?P<date>\d{4}-\d{2}-\d{2})_(?P<region>[a-z]+)\.csv"
)
match = pattern.fullmatch("sales_2025-07-01_west.csv")
match.groupdict() if match else None
```

**Expected observation**

```text
`{'date': '2025-07-01', 'region': 'west'}`. A filename with extra trailing text returns `None`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Build a path without platform-specific separators

Let `Path` own path joining and filename fields. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
from pathlib import Path

report = Path("artifacts") / "daily sales.csv"
(report.parent, report.stem, report.suffix, report.with_suffix(".json"))
```

**Expected observation**

```text
A tuple of `Path` values is displayed. On every supported operating system the components remain meaningful without hard-coded `/` or `\` separators.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Use `repr(text)` when whitespace, escapes, or invisible characters affect a match.
2. Choose `fullmatch`, `match`, or `search` deliberately and print `match.groupdict()` during diagnosis.
3. Use a raw string for regex patterns containing backslashes.
4. Calculate every destination and collision before calling `rename`.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Prefer `split`, `partition`, `startswith`, and `endswith` for fixed formats; use a parser rather than regex for languages such as HTML.

**Boundary to remember:** Mixed case, Unicode, multiple suffixes, existing destinations, and two source names that normalize to the same target need explicit policy.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Normalization:** convert equivalent text forms to one consistent form.
- **Regular expression:** a pattern language for matching text.
- **Capture group:** the portion of a match retained for later use.
- **Raw string:** `r"..."`, which prevents Python from consuming most
  backslashes before the regex engine sees them.
- **Path:** an object representing a filesystem location; it need not exist.
- **Stem/suffix:** a filename without its final extension / its final extension.

Use ordinary string methods for simple, fixed transformations. Reach for regex
when the text has a pattern with alternatives or variable-length parts.

## Worked example

```python
import re
from pathlib import Path

line = "run_id=DS-042 status=ok"
match = re.fullmatch(r"run_id=(?P<run_id>[A-Z]{2}-\d{3}) status=(?P<status>\w+)", line)
if match is not None:
    print(match.groupdict())

report = Path("reports") / "daily.csv"
print(report.parent, report.stem, report.suffix)
```

The regex describes the whole record. `Path` composes a portable location
without hard-coding `/` or `\`.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. From the supplied multiline text, extract email-shaped values, normalize them to lowercase, and return first-seen unique addresses. **Constraints:** use one bounded regex for extraction, then separate normalization and de-duplication steps; do not attempt full Internet-email validation.
   **Verify:** assert differently cased duplicates collapse to one lowercase address in first-seen order and a no-match string returns `[]`.

2. Write `plan_kebab_renames(folder: Path)` that returns source/destination pairs for regular files such as `Quarterly Report.CSV` without renaming them. **Rules:** normalize the stem to lowercase hyphen-separated words, preserve the suffix, skip unchanged names, and reject collisions including case-normalized collisions.
   **Verify:** use a temporary directory and inspect the complete plan before implementing a separate apply step.

### Additional mastery practice

Use ordinary string operations for fixed syntax, regular expressions for patterns, and `pathlib` for portable path semantics.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Compare `"\n"` with `r"\n"` and predict their lengths and printed representations.
   **Progressive hint:** A raw string preserves the backslash needed by many regex patterns.
   **Verify:** Record `len`, `repr`, and printed behavior for both strings; confirm the newline has length 1 and the raw backslash-n has length 2.
4. **Tracing:** Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture.
   **Progressive hint:** The whole match and captured subparts are different values.
   **Verify:** Assert `group(0)` is `'order-2048.csv'` while the named ID capture is `'2048'`; add a nonmatching filename returning no match.
5. **Implementation:** Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches.
   **Progressive hint:** Use `fullmatch` so extra suffix text cannot pass silently.
   **Verify:** Assert the valid filename returns the stated date/region and near misses with trailing text, bad date shape, or wrong suffix are rejected.
6. **Debugging:** Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML.
   **Progressive hint:** Use a constrained or non-greedy pattern only for a bounded format.
   **Verify:** Demonstrate the greedy overmatch, then assert the bounded repair returns separate intended tags; state why the fixture is not a general HTML parser.
7. **Edge case and explanation:** Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`.
   **Progressive hint:** Separate planning/validation from filesystem mutation.
   **Verify:** Generate a plan containing both colliding names and assert validation raises before any directory entry is renamed.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- When is `str.replace` clearer than `re.sub`?
- What is the difference between `re.search` and `re.fullmatch`?
- Why should a rename utility have a dry-run mode?
- Which part of `archive.tar.gz` is returned by `Path(...).suffix`?

Expected behavior: emails are normalized without duplicates, and the dry-run
rename plan does not modify files.

## Common pitfalls and diagnosis

- **Backslashes behave unexpectedly:** use a raw regex string and inspect
  `repr(pattern)`.
- **A pattern matches too much:** replace a greedy quantifier with a bounded
  class or non-greedy form, then add examples that must not match.
- **`match` is `None`:** check it before calling `.group()` and print the input
  with `repr`.
- **Windows paths break on another OS:** never split paths manually on `/` or
  `\`; use `Path` properties.
- **Renaming overwrites or collides:** compare normalized destination names
  before making any filesystem change.

## Continue

- [Open the learner notebook](../notebooks/day07_strings_regex_pathlib.ipynb)
- [Check the separate solution](../solutions/day07_strings_regex_pathlib/day07_solutions.md)
- [Next: Day 8 — Files, JSON, and CSV](day08_files_json_csv_context.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-07`
(Day 7 — Strings, Regular Expressions, and `pathlib`). Direct catalog prerequisites: `python-06`.
I have completed the direct prerequisites: `python-06`. Emphasize text normalization, bounded pattern matching, and portable paths.
Read `python/ds-60day/companion-guides/day07_strings_regex_pathlib.md` and use the learner notebook
`python/ds-60day/notebooks/day07_strings_regex_pathlib.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
