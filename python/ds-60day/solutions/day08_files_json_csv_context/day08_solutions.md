# Day 08 — Solutions: Files, JSON/CSV, and Context Managers

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**resource ownership, text encodings, and structured file boundaries**.

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

### Vocabulary used in the worked answers

- **file handle:** an open resource used to read or write a file.
- **cursor:** the current read/write position in a stream.
- **context manager:** an object that performs setup and guaranteed cleanup around a `with` block.
- **encoding:** the mapping between text characters and bytes.
- **serialization:** converting in-memory data to a storable representation.
- **schema:** the expected fields, types, and constraints of data.

### Reference pattern 1 — Round-trip JSON through an in-memory stream

Observe serialization without creating learner files.

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

**Expected observation:** The JSON text and `True` are displayed. Serialization creates text; parsing reconstructs equivalent Python data.

### Reference pattern 2 — Read CSV rows as dictionaries

Column headers become keys while every field initially remains text.

```python
import csv
import io

csv_text = "name,score\nAda,9\nLin,10\n"
rows = list(csv.DictReader(io.StringIO(csv_text)))
(rows, type(rows[0]["score"]).__name__)
```

**Expected observation:** `([{'name': 'Ada', 'score': '9'}, {'name': 'Lin', 'score': '10'}], 'str')`. Numeric-looking CSV fields still require conversion.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Implement `safe_load_json(path)` that returns parsed data on success and `None` only for a missing file or malformed JSON, logging which expected failure occurred. **Constraints:** open with UTF-8, catch `FileNotFoundError` and `json.JSONDecodeError` explicitly, and let unrelated errors surface. **Verify:** test a valid file, a missing path, and an invalid JSON file inside a temporary directory.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies resource ownership, text encodings, and structured file boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** test a valid file, a missing path, and an invalid JSON file inside a temporary directory.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Implement `csv_to_records(path)` and `records_to_csv(records, path)` using `csv.DictReader` and `csv.DictWriter`. **Contract:** headers define keys, output field order is explicit, and numeric conversion policy is documented. **Constraints:** use UTF-8 and `newline=''`; do not hand-split comma-delimited text. **Verify:** round-trip two records including a non-ASCII name and compare the normalized records.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies resource ownership, text encodings, and structured file boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** round-trip two records including a non-ASCII name and compare the normalized records.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor. **Progressive hint:** Reads advance the file object's current position. **Verify:** Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying resource ownership, text encodings, and structured file boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block. **Progressive hint:** Context-manager cleanup runs on both normal and exceptional exit. **Verify:** Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the resource ownership, text encodings, and structured file boundaries model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination. **Progressive hint:** Use explicit UTF-8, `json.dump`, and `Path.replace`. **Verify:** Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies resource ownership, text encodings, and structured file boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names. **Progressive hint:** Open with `newline=''` and `encoding='utf-8'`. **Verify:** Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in resource ownership, text encodings, and structured file boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs. **Progressive hint:** Validate each row at the boundary rather than failing much later. **Verify:** Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from resource ownership, text encodings, and structured file boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `json.loads`/`dumps` for in-memory text and `load`/`dump` for open file objects; use a database or columnar format when CSV cannot express the needed contract.

**Edge case:** Missing files, malformed records, absent or extra CSV columns, non-ASCII names, partial writes, and empty files need deliberate behavior.

**Solution evidence to inspect:** Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule.
<!-- END BEGINNER SOLUTION REVIEW -->

We build a safe JSON loader and converters between CSV and JSON with careful error handling.

Contents
- Exercise 1: `safe_load_json(path)` returns None on errors and logs them
- Exercise 2: Convert CSV → JSON and JSON → CSV

---

Exercise 1 — Safe JSON loader
```python
from pathlib import Path
from typing import Any
import json


def safe_load_json(path: str | Path, *, verbose: bool = True) -> Any | None:
    """Load JSON or return None on error; print concise diagnostics when verbose.

    - Opens with utf-8 encoding
    - Differentiates not found, permission, and decoding errors
    """
    p = Path(path)
    try:
        with p.open(encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        if verbose:
            print(f"safe_load_json: not found: {p}")
    except PermissionError:
        if verbose:
            print(f"safe_load_json: permission denied: {p}")
    except json.JSONDecodeError as e:
        if verbose:
            print(f"safe_load_json: invalid JSON in {p}: line {e.lineno}, col {e.colno}: {e.msg}")
    return None

# Demo
# data = safe_load_json('data/people.json')
```
Why return None?
- Signals failure without raising; the caller can decide a default or next step.

---

Exercise 2 — CSV ↔ JSON converters
CSV → JSON
```python
import csv
from pathlib import Path
from typing import Iterable


def csv_to_json(csv_path: Path, json_path: Path) -> None:
    """Read rows from csv_path and write a JSON array to json_path."""
    with csv_path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)                  # small to medium files; stream for huge files
    # Optional: type coercion (e.g., ints) could be added here
    with json_path.open('w', encoding='utf-8') as out:
        json.dump(rows, out, indent=2, ensure_ascii=False)

# csv_to_json(Path('data/people.csv'), Path('data/people.json'))
```

JSON → CSV
```python
from typing import Any


def json_to_csv(json_path: Path, csv_path: Path) -> None:
    """Write records in json_path (list of dict-like) to CSV with unioned fieldnames."""
    data: list[dict[str, Any]] = safe_load_json(json_path) or []
    if not data:
        # Write empty CSV with no header when no data
        csv_path.write_text('', encoding='utf-8')
        return

    # Determine all fieldnames across records to avoid missing columns
    fieldnames: list[str] = sorted({k for rec in data for k in rec.keys()})
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in data:
            w.writerow({k: rec.get(k, '') for k in fieldnames})

# json_to_csv(Path('data/people.json'), Path('data/people.csv'))
```
Notes
- Always specify encoding; use newline='' when writing CSVs (especially on Windows).
- For large files, stream row-by-row rather than building a list in memory.

---

## Expanded mastery lab solutions

Treat files as fallible boundaries. Specify encoding, newline behavior, schema, and failure policy, and keep writes recoverable.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Cursor and context-manager behavior

The second read returns `"cd"` because the cursor is already after `"ab"`.
Leaving a `with` block closes the handle even when decoding raises.

### Practices 3–5 — Recoverable writes and explicit row validation

```python
from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


def write_json_atomic(path: Path, value: Any) -> None:
    """Replace ``path`` only after a complete sibling file is written."""

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(path)


def partition_rows(
    rows: Iterable[Mapping[str, str]], required: set[str]
) -> tuple[list[dict[str, str]], list[tuple[dict[str, str], str]]]:
    """Separate valid rows from rows that violate the required-column contract."""

    accepted: list[dict[str, str]] = []
    rejected: list[tuple[dict[str, str], str]] = []
    for source_row in rows:
        row = dict(source_row)
        missing = sorted(name for name in required if not row.get(name, "").strip())
        if missing:
            rejected.append((row, f"missing values: {', '.join(missing)}"))
        else:
            accepted.append(row)
    return accepted, rejected


with TemporaryDirectory() as directory:
    destination = Path(directory) / "people.json"
    write_json_atomic(destination, [{"name": "Zoë"}])
    assert json.loads(destination.read_text(encoding="utf-8"))[0]["name"] == "Zoë"

    csv_path = Path(directory) / "people.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name"])
        writer.writeheader()
        writer.writerow({"name": "Zoë"})

accepted, rejected = partition_rows(
    [{"id": "1", "name": "Ada"}, {"id": "2", "name": ""}], {"id", "name"}
)
assert len(accepted) == 1 and rejected[0][1] == "missing values: name"
```
