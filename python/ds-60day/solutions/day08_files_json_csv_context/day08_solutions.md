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
