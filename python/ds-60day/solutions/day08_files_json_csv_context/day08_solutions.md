# Day 8 Solutions: Files, JSON, CSV, and Context Managers

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Implement `safe_load_json(path)` that returns parsed data on success and `None` only for a missing file or malformed JSON, logging which expected failure occurred. **Constraints:** open with UTF-8, catch `FileNotFoundError` and `json.JSONDecodeError` explicitly, and let unrelated errors surface. **Verify:** test a valid file, a missing path, and an invalid JSON file inside a temporary directory.

**Reasoning:** Only the two failures this function can interpret are caught: `FileNotFoundError` for a missing path and `json.JSONDecodeError` for malformed content. Each logs a different message and returns `None`, so the caller can tell "no data" from data. Everything else, such as a permission error or a typo in the code, still raises, because returning `None` for it would hide a real problem. One ambiguity remains: a file containing the JSON value `null` also loads as `None`; if `null` is legitimate content, return a dedicated sentinel or raise instead.

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

### Exercise 2: worked answer

**Learner contract:** Implement `csv_to_records(path)` and `records_to_csv(records, path)` using `csv.DictReader` and `csv.DictWriter`. **Contract:** headers define keys, output field order is explicit, and numeric conversion policy is documented. **Constraints:** use UTF-8 and `newline=''`; do not hand-split comma-delimited text. **Verify:** round-trip two records including a non-ASCII name and compare the normalized records.

**Reasoning:** `csv.DictReader` uses the header row as keys, and `csv.DictWriter` writes columns in the explicit `fieldnames` order, so the layout depends neither on dictionary order nor on hand-split commas, which break on quoted values such as `"Smith, Ada"`. Opening with `newline=""` lets the csv module control line endings, and `encoding="utf-8"` keeps `José` intact on every platform. The round trip returns strings: CSV has no types, so converting `"10"` to an integer is a separate, documented parsing step. Comparing `list(reloaded[0])` with the field tuple checks the column order as well as the values.

```python
import csv
from pathlib import Path
import tempfile

CSV_FIELDS = ("name", "score")


def csv_to_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def records_to_csv(records: list[dict[str, str]], path: Path) -> None:
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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** After `handle.read(2)` on a text file containing `abcd`, predict what a second `handle.read()` returns and explain the cursor. **Progressive hint:** Reads advance the file object's current position. **Verify:** Assert the first read is `'ab'`, the second is `'cd'`, and a third is empty; record cursor positions `2` and `4`.

**Reasoning:** A text file object keeps a current position. `read(2)` returns `"ab"` and leaves the position after the second character, so the next `read()` returns the rest, `"cd"`, and a further `read()` returns `""` because the position is at the end. `tell()` reports 2 and then 4 for this ASCII text; for other encodings it is an opaque marker, not a character count. Reading the file again requires `seek(0)` or opening it again. The shared implementation for Exercises 3-4 asserts the three reads and both positions.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace when a file is open and closed through a `with` block, including when JSON decoding raises inside the block. **Progressive hint:** Context-manager cleanup runs on both normal and exceptional exit. **Verify:** Record `handle.closed` inside and after both successful and failing `with` blocks; assert it is true after either exit.

**Reasoning:** A `with` block calls the file's `__exit__` method however the block ends, so `handle.closed` is `True` after a successful read and also after `json.load` raises `JSONDecodeError` inside the block. That guarantee is the reason to prefer `with` over calling `close()` yourself, which an exception would skip. The exception still propagates after the file closes, so the caller decides how to handle it; the shared implementation for Exercises 3-4 catches it outside the block and checks that the handle is closed in both cases.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement an atomic JSON writer that writes a sibling temporary file then replaces the destination. **Progressive hint:** Use explicit UTF-8, `json.dump`, and `Path.replace`. **Verify:** Read the replaced destination and assert it contains the complete new JSON; simulate serialization failure and assert the old destination is still intact.

**Reasoning:** Writing directly to the destination risks leaving a half-written file if serialization fails. Writing to a sibling temporary file and then calling `Path.replace` swaps in the complete file in one step (an atomic rename on the same file system), so readers see either the old or the new content. The temporary file sits next to the destination because a rename across file systems is not atomic. The shared implementation for Exercises 5-7 forces a failure with a value `json` cannot serialize, checks that the old destination is intact, and confirms that the leftover temporary file was removed.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair CSV writing that creates blank lines on Windows or corrupts non-ASCII names. **Progressive hint:** Open with `newline=''` and `encoding='utf-8'`. **Verify:** Round-trip two CSV rows including a non-ASCII name on the current platform; assert no blank records and exact decoded characters.

**Reasoning:** The csv module writes its own `\r\n` line endings. When the file is opened without `newline=""`, Windows text mode translates each `\n` again and produces `\r\r\n`, which readers show as a blank row between records. A platform default encoding such as cp1252 can also corrupt or reject names such as `Zoë`. Opening with `newline=""` and `encoding="utf-8"` for both writing and reading fixes both problems; the shared implementation for Exercises 5-7 checks the exact line endings in the bytes and the decoded rows.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Design a CSV reader policy for missing columns and extra columns; return accepted rows and quarantined row/error pairs. **Progressive hint:** Validate each row at the boundary rather than failing much later. **Verify:** Use one valid, one missing-column, and one extra-column row; assert accepted plus quarantined equals input and each quarantine reason names its violated rule.

**Reasoning:** Validating each row at the boundary keeps bad rows from failing much later in a calculation. Each row ends up in exactly one list: accepted, or quarantined with a reason naming the violated rule (`missing values: name` or `unexpected columns: email`). Because nothing is dropped silently, `len(accepted) + len(rejected)` must equal the number of input rows, which the shared implementation for Exercises 5-7 asserts for one valid, one missing-value, and one extra-column row. Quarantining extra columns is a policy choice: an unexpected column often signals that the source format changed.

## Expanded mastery lab solutions

Treat files as fallible boundaries. Specify encoding, newline behavior, schema, and failure policy, and keep writes recoverable.

### Shared implementation for Exercises 3-4: Cursor and context-manager behavior

The second read returns `"cd"` because the cursor is already after `"ab"`.
Leaving a `with` block closes the handle even when decoding raises.

```python
import json
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    letters = Path(folder) / "letters.txt"
    letters.write_text("abcd", encoding="utf-8")
    with letters.open(encoding="utf-8") as handle:
        first = handle.read(2)
        after_first = handle.tell()
        second = handle.read()
        after_second = handle.tell()
        third = handle.read()
    assert (first, second, third) == ("ab", "cd", "")
    assert (after_first, after_second) == (2, 4)
    assert handle.closed  # closed after a normal exit

    broken = Path(folder) / "broken.json"
    broken.write_text('{"course":', encoding="utf-8")
    try:
        with broken.open(encoding="utf-8") as handle:
            json.load(handle)
    except json.JSONDecodeError:
        pass
    assert handle.closed  # closed after the exception, too
```

### Shared implementation for Exercises 5-7: Recoverable writes and explicit row validation

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
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except BaseException:
        temporary.unlink(missing_ok=True)  # never leave a partial file behind
        raise
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
        extra = sorted(str(name) for name in row if name not in required)
        if missing:
            rejected.append((row, f"missing values: {', '.join(missing)}"))
        elif extra:
            rejected.append((row, f"unexpected columns: {', '.join(extra)}"))
        else:
            accepted.append(row)
    return accepted, rejected


with TemporaryDirectory() as directory:
    destination = Path(directory) / "people.json"
    write_json_atomic(destination, [{"name": "Zoë"}])
    assert json.loads(destination.read_text(encoding="utf-8"))[0]["name"] == "Zoë"
    try:
        write_json_atomic(destination, {"bad": object()})  # not JSON-serializable
    except TypeError:
        pass
    assert json.loads(destination.read_text(encoding="utf-8"))[0]["name"] == "Zoë"
    assert not destination.with_suffix(".json.tmp").exists()

    csv_path = Path(directory) / "people.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name"])
        writer.writeheader()
        writer.writerow({"name": "Zoë"})
    assert csv_path.read_bytes() == "name\r\nZoë\r\n".encode()  # no doubled line endings
    with csv_path.open(encoding="utf-8", newline="") as handle:
        assert list(csv.DictReader(handle)) == [{"name": "Zoë"}]

rows = [
    {"id": "1", "name": "Ada"},
    {"id": "2", "name": ""},
    {"id": "3", "name": "Lin", "email": "lin@example.invalid"},
]
accepted, rejected = partition_rows(rows, {"id", "name"})
assert len(accepted) + len(rejected) == len(rows)
assert [reason for _, reason in rejected] == ["missing values: name", "unexpected columns: email"]
```
