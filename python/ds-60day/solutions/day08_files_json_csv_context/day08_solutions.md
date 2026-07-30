# Day 08 — Solutions: Files, JSON/CSV, and Context Managers

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Write `safe_load_json(path)` that returns `None` for expected read/decode failures and logs the cause. **Hint:** identify the narrow exception types raised by a missing file and malformed JSON; avoid catching every exception.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Convert CSV rows to JSON records and JSON records back to CSV. **Hint:** use `csv.DictReader`/`DictWriter`, decide which object supplies field names, and open CSV output with `newline=""`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor.

**Reasoning checkpoint:** Reads advance the file object's current position. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block.

**Reasoning checkpoint:** Context-manager cleanup runs on both normal and exceptional exit. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination.

**Reasoning checkpoint:** Use explicit UTF-8, `json.dump`, and `Path.replace`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names.

**Reasoning checkpoint:** Open with `newline=''` and `encoding='utf-8'`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs.

**Reasoning checkpoint:** Validate each row at the boundary rather than failing much later. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
