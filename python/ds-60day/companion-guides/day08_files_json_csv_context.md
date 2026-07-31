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

2. Read `python/ds-60day/companion-guides/day08_files_json_csv_context.md`, then open `python/ds-60day/notebooks/day08_files_json_csv_context.ipynb` from the repository
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

**Lesson outcome:** use day 8 — files, json, csv, and context managers to practice resource ownership, text encodings, and structured file boundaries
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A file handle is a stateful resource with a current cursor and an open
or closed lifetime. A context manager (`with`) makes ownership visible:
acquire the resource, use it inside the block, and release it on both
success and failure. Text files also have an encoding and newline
policy; make both explicit at boundaries.

JSON and CSV are representations, not automatically trusted schemas.
JSON preserves nested object/list structure but has a small type system.
CSV is a table of text fields and requires column-name and conversion
policy. Parse and validate rows near the boundary, keep writes
recoverable, and report expected read/decode failures without hiding
programming errors.

### Vocabulary in plain language

- **file handle:** an open resource used to read or write a file.
- **cursor:** the current read/write position in a stream.
- **context manager:** an object that performs setup and guaranteed cleanup around a `with` block.
- **encoding:** the mapping between text characters and bytes.
- **serialization:** converting in-memory data to a storable representation.
- **schema:** the expected fields, types, and constraints of data.

### Syntax anatomy

`with path.open("r", encoding="utf-8") as handle:` creates a context,
binds the open handle, and guarantees `close` at block exit.
`json.load(handle)` reads JSON from a file object; `json.loads(text)`
parses an already-loaded string. For CSV output, `newline=""` lets the
`csv` module manage platform newline rules correctly.

### Worked example 1 — Round-trip JSON through an in-memory stream

Observe serialization without creating learner files. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import io
import json

record = {"name": "Ada", "skills": ["Python", "SQL"], "active": True}
stream = io.StringIO()
json.dump(record, stream, ensure_ascii=False)
encoded = stream.getvalue()
decoded = json.loads(encoded)
(encoded, decoded == record)
```

**Expected observation**

```text
The JSON text and `True` are displayed. Serialization creates text; parsing reconstructs equivalent Python data.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Read CSV rows as dictionaries

Column headers become keys while every field initially remains text. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import csv
import io

csv_text = "name,score\nAda,9\nLin,10\n"
rows = list(csv.DictReader(io.StringIO(csv_text)))
(rows, type(rows[0]["score"]).__name__)
```

**Expected observation**

```text
`([{'name': 'Ada', 'score': '9'}, {'name': 'Lin', 'score': '10'}], 'str')`. Numeric-looking CSV fields still require conversion.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Use `repr` on a short read and inspect the cursor with `handle.tell()` when content seems missing.
2. Catch `FileNotFoundError`, `PermissionError`, and `json.JSONDecodeError` separately when the recovery differs.
3. Open CSV with `newline=''` and text files with an explicit `encoding='utf-8'`.
4. Write to a temporary sibling and replace the destination only after a successful serialization.

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

**Useful alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Boundary to remember:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Implement `safe_load_json(path)` that returns parsed data on success and `None` only for a missing file or malformed JSON, logging which expected failure occurred. **Constraints:** open with UTF-8, catch `FileNotFoundError` and `json.JSONDecodeError` explicitly, and let unrelated errors surface.
   **Verify:** test a valid file, a missing path, and an invalid JSON file inside a temporary directory.

2. Implement `csv_to_records(path)` and `records_to_csv(records, path)` using `csv.DictReader` and `csv.DictWriter`. **Contract:** headers define keys, output field order is explicit, and numeric conversion policy is documented. **Constraints:** use UTF-8 and `newline=''`; do not hand-split comma-delimited text.
   **Verify:** round-trip two records including a non-ASCII name and compare the normalized records.

### Additional mastery practice

Treat files as fallible boundaries. Specify encoding, newline behavior, schema, and failure policy, and keep writes recoverable.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor.
   **Progressive hint:** Reads advance the file object's current position.
   **Verify:** Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`.
4. **Tracing:** Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block.
   **Progressive hint:** Context-manager cleanup runs on both normal and exceptional exit.
   **Verify:** Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit.
5. **Implementation:** Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination.
   **Progressive hint:** Use explicit UTF-8, `json.dump`, and `Path.replace`.
   **Verify:** Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact.
6. **Debugging:** Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names.
   **Progressive hint:** Open with `newline=''` and `encoding='utf-8'`.
   **Verify:** Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters.
7. **Edge case and explanation:** Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs.
   **Progressive hint:** Validate each row at the boundary rather than failing much later.
   **Verify:** Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-08`
(Day 8 — Files, JSON, CSV, and Context Managers). I am a complete beginner. Emphasize resource ownership, text encodings, and structured file boundaries.
Read `python/ds-60day/companion-guides/day08_files_json_csv_context.md` and use the learner notebook
`python/ds-60day/notebooks/day08_files_json_csv_context.ipynb`. Do not open or quote anything under `solutions/` unless
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
