# Day 08 — Solutions: Files, JSON/CSV, and Context Managers

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **resource ownership, text encodings, and structured file boundaries**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **resource ownership, text encodings, and structured file boundaries** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Implement `safe_load_json(path)` that returns parsed data on success and `None` only for a missing file or malformed JSON, logging which expected failure occurred. **Constraints:** open with UTF-8, catch `FileNotFoundError` and `json.JSONDecodeError` explicitly, and let unrelated errors surface. **Verify:** test a valid file, a missing path, and an invalid JSON file inside a temporary directory.

**Reasoning:** Implement this exact contract as written: Implement `safe_load_json(path)` that returns parsed data on success and `None` only for a missing file or malformed JSON, logging which expected failure occurred. Constraints: open with UTF-8, catch `FileNotFoundError` and `json.JSONDecodeError` explicitly, and let unrelated errors surface. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test a valid file, a missing path, and an invalid JSON file inside a temporary directory. That connects the answer to resource ownership, text encodings, and structured file boundaries.

```python
import json
import logging
from pathlib import Path
import tempfile
from typing import Any

logger = logging.getLogger(__name__)


def safe_load_json(path: Path) -> Any | None:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        logger.warning("JSON file is missing: %s", path)
    except json.JSONDecodeError as error:
        logger.warning("Invalid JSON in %s at line %d", path, error.lineno)
    return None


with tempfile.TemporaryDirectory() as temporary:
    folder = Path(temporary)
    valid_path = folder / "valid.json"
    invalid_path = folder / "invalid.json"
    missing_path = folder / "missing.json"
    valid_path.write_text('{"course": "ds60"}', encoding="utf-8")
    invalid_path.write_text('{"course":', encoding="utf-8")

    assert safe_load_json(valid_path) == {"course": "ds60"}
    assert safe_load_json(invalid_path) is None
    assert safe_load_json(missing_path) is None
```

The two expected boundary failures are distinguished; unrelated
permission or programming failures remain visible.

**Verification evidence:** test a valid file, a missing path, and an invalid JSON file inside a temporary directory.

### Exercise 2 — worked answer

**Learner contract:** Implement `csv_to_records(path)` and `records_to_csv(records, path)` using `csv.DictReader` and `csv.DictWriter`. **Contract:** headers define keys, output field order is explicit, and numeric conversion policy is documented. **Constraints:** use UTF-8 and `newline=''`; do not hand-split comma-delimited text. **Verify:** round-trip two records including a non-ASCII name and compare the normalized records.

**Reasoning:** Implement this exact contract as written: Implement `csv_to_records(path)` and `records_to_csv(records, path)` using `csv.DictReader` and `csv.DictWriter`. Contract: headers define keys, output field order is explicit, and numeric conversion policy is documented. Constraints: use UTF-8 and `newline=''`; do not hand-split comma-delimited text. Keep the prompt's named data and constraints visible in the code, then establish this specific result: round-trip two records including a non-ASCII name and compare the normalized records. That connects the answer to resource ownership, text encodings, and structured file boundaries.

```python
import csv
from pathlib import Path
import tempfile

CSV_FIELDS = ("name", "score")


def csv_to_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def records_to_csv(
    records: list[dict[str, str]], path: Path
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)


records = [
    {"name": "Ada", "score": "10"},
    {"name": "José", "score": "8"},
]
with tempfile.TemporaryDirectory() as temporary:
    path = Path(temporary) / "scores.csv"
    records_to_csv(records, path)
    reloaded = csv_to_records(path)
    assert reloaded == records
    assert list(reloaded[0]) == list(CSV_FIELDS)
```

`DictReader` returns text, so this contract deliberately preserves
`"10"` and `"8"` as strings. A later domain-specific parsing stage may
convert them; the CSV transport layer does not guess numeric meaning.

**Verification evidence:** round-trip two records including a non-ASCII name and compare the normalized records.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor. **Progressive hint:** Reads advance the file object's current position. **Verify:** Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`.

**Reasoning:** Predict this named state change before running it: Prediction: After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor. Progressive hint: Reads advance the file object's current position. Then compare the prediction with this proof target: Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`. This makes resource ownership, text encodings, and structured file boundaries observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block. **Progressive hint:** Context-manager cleanup runs on both normal and exceptional exit. **Verify:** Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block. Progressive hint: Context-manager cleanup runs on both normal and exceptional exit. Record the named value, shape, label, or iterator position needed to establish: Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit. The trace exposes resource ownership, text encodings, and structured file boundaries directly.

**Evidence to locate in the grouped implementation:** Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination. **Progressive hint:** Use explicit UTF-8, `json.dump`, and `Path.replace`. **Verify:** Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact.

**Reasoning:** Implement this exact contract as written: Implementation: Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination. Progressive hint: Use explicit UTF-8, `json.dump`, and `Path.replace`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact. That connects the answer to resource ownership, text encodings, and structured file boundaries.

**Evidence to locate in the grouped implementation:** Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names. **Progressive hint:** Open with `newline=''` and `encoding='utf-8'`. **Verify:** Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names. Progressive hint: Open with `newline=''` and `encoding='utf-8'`. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters. The diagnosis depends on resource ownership, text encodings, and structured file boundaries.

**Evidence to locate in the grouped implementation:** Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs. **Progressive hint:** Validate each row at the boundary rather than failing much later. **Verify:** Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs. Progressive hint: Validate each row at the boundary rather than failing much later. Values below, at, and above the named boundary must produce the evidence Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule. Those cases show how resource ownership, text encodings, and structured file boundaries behaves at its edge.

**Evidence to locate in the grouped implementation:** Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule.

## Expanded mastery lab solutions

Treat files as fallible boundaries. Specify encoding, newline behavior, schema, and failure policy, and keep writes recoverable.

### Shared implementation for Exercises 3–4 — Cursor and context-manager behavior

The second read returns `"cd"` because the cursor is already after `"ab"`.
Leaving a `with` block closes the handle even when decoding raises.

### Shared implementation for Exercises 5–7 — Recoverable writes and explicit row validation

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
