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

1. Extract every email address from multiline text, then produce unique,
   lowercase results. **Hint:** first get all matches; normalize and de-duplicate
   as separate steps.
2. Rename files in a chosen directory to kebab-case with `pathlib`. **Hint:**
   calculate and print every source/destination pair before calling `rename`;
   preserve each suffix and handle name collisions.

### Additional mastery practice

Use ordinary string operations for fixed syntax, regular expressions for patterns, and `pathlib` for portable path semantics.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Compare `"\n"` with `r"\n"` and predict their lengths and printed representations.
   **Progressive hint:** A raw string preserves the backslash needed by many regex patterns.
4. **Tracing:** Trace named regex groups while parsing `order-2048.csv`; distinguish `group(0)` from the named capture.
   **Progressive hint:** The whole match and captured subparts are different values.
5. **Implementation:** Implement `parse_report_name(Path)` returning a date and region for names like `sales_2025-07-01_west.csv`, rejecting mismatches.
   **Progressive hint:** Use `fullmatch` so extra suffix text cannot pass silently.
6. **Debugging:** Repair a greedy `<.*>` pattern that consumes multiple tags in one line, then explain why a real HTML parser is safer for HTML.
   **Progressive hint:** Use a constrained or non-greedy pattern only for a bounded format.
7. **Edge case and explanation:** Build a rename plan to kebab-case that detects collisions before changing any files, including `A B.txt` and `a-b.txt`.
   **Progressive hint:** Separate planning/validation from filesystem mutation.

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
