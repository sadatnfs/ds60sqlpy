# Day 8 — Files, JSON, CSV, and Context Managers

**Level:** Beginner

File I/O crosses a boundary where paths, encodings, permissions, and data shape
can all fail. Make those assumptions visible.

## Learning objectives

By the end of this lesson, you can:

- read and write text using an explicit UTF-8 encoding;
- explain how Python values map to JSON values;
- read and write row-oriented CSV with the standard library;
- use `with` so resources close on success or failure;
- report a recoverable file error without hiding programming defects.

## Prerequisites

Complete Day 7 (`python-07`): string normalization, exceptions, and `Path`.

## Vocabulary and mental model

- **Serialization:** encode in-memory values into a storable representation.
- **Deserialization:** decode stored bytes/text into values.
- **Encoding:** mapping between text characters and bytes; UTF-8 is the course
  default.
- **Context manager:** an object whose `with` block guarantees setup/cleanup.
- **CSV dialect:** delimiter, quoting, newline, and related format rules.
- **Schema:** the expected fields, types, and constraints of data.

Opening a file supplies a resource; `with` defines exactly how long that
resource is owned.

## Worked example

```python
import json
from pathlib import Path

path = Path("artifacts") / "day08-settings.json"
settings = {"theme": "light", "page_size": 25}
path.parent.mkdir(parents=True, exist_ok=True)

with path.open("w", encoding="utf-8") as stream:
    json.dump(settings, stream, indent=2)

with path.open(encoding="utf-8") as stream:
    loaded = json.load(stream)

assert loaded == settings
```

This deterministic round trip requires no network access. `artifacts/` is the
repository's ignored location for disposable generated data.

## Exercises and progressive hints

1. Write `safe_load_json(path)` that returns `None` for expected read/decode
   failures and logs the cause. **Hint:** identify the narrow exception types
   raised by a missing file and malformed JSON; avoid catching every exception.
2. Convert CSV rows to JSON records and JSON records back to CSV. **Hint:** use
   `csv.DictReader`/`DictWriter`, decide which object supplies field names, and
   open CSV output with `newline=""`.

### Additional mastery practice

Treat files as fallible boundaries. Specify encoding, newline behavior, schema, and failure policy, and keep writes recoverable.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor.
   **Progressive hint:** Reads advance the file object's current position.
4. **Tracing:** Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block.
   **Progressive hint:** Context-manager cleanup runs on both normal and exceptional exit.
5. **Implementation:** Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination.
   **Progressive hint:** Use explicit UTF-8, `json.dump`, and `Path.replace`.
6. **Debugging:** Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names.
   **Progressive hint:** Open with `newline=''` and `encoding='utf-8'`.
7. **Edge case and explanation:** Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs.
   **Progressive hint:** Validate each row at the boundary rather than failing much later.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- Why does JSON not preserve tuples as tuples?
- What guarantee does `with` provide if decoding raises an exception?
- Why should CSV output on Windows use `newline=""`?
- When should a loader raise instead of returning `None`?

Expected behavior: valid data round-trips, malformed JSON produces a useful log
entry, and CSV output has one header plus the expected row count.

## Common pitfalls and diagnosis

- **`UnicodeDecodeError`:** confirm the source encoding; do not silently discard
  characters with `errors="ignore"`.
- **Extra blank CSV rows on Windows:** pass `newline=""` when opening CSV files.
- **`JSONDecodeError`:** log the path and decoder message, then inspect the
  reported line and column.
- **A JSON top-level object has an unexpected shape:** validate that it is the
  list/dictionary your converter expects before iterating.
- **A write leaves a partial file:** production code should write a temporary
  file and replace the destination only after success.

## Continue

- [Open the learner notebook](../notebooks/day08_files_json_csv_context.ipynb)
- [Check the separate solution](../solutions/day08_files_json_csv_context/day08_solutions.md)
- [Next: Day 9 — Modules and packages](day09_modules_packages.md)
