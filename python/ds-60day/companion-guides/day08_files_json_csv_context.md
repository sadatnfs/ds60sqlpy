# Day 8 — Files, JSON/CSV, and Context Managers (Companion Guide)

## Learning objectives
- Read/write text, JSON, and CSV reliably
- Use `with` statements to guarantee resource cleanup
- Handle errors (missing files, bad JSON) gracefully

## Why this matters
I/O is where data enters or leaves your system. Good patterns prevent file descriptor leaks, half-written files, and cryptic errors for users.

## Mental models
- Context managers wrap setup/teardown around a block (`__enter__` / `__exit__`)
- CSV and JSON have edge cases: quoting, newlines, encodings; always be explicit

## Reading and writing JSON
```python
import json
from pathlib import Path
p = Path('data/people.json')
people = [{"name": "Ada", "age": 36}, {"name": "Alan", "age": 41}]
with p.open('w', encoding='utf-8') as f:
    json.dump(people, f, indent=2, ensure_ascii=False)

with p.open(encoding='utf-8') as f:
    loaded = json.load(f)
```
Use `ensure_ascii=False` to preserve Unicode; always specify `encoding`.

## CSV pitfalls and dialects
```python
import csv
p = Path('data/people.csv')
with p.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['name','age'])
    w.writeheader(); w.writerows(people)
```
Use `newline=''` on Windows to avoid double newlines. For reading, `csv.Sniffer` can guess dialects.

## Safe loaders
```python
from typing import Any

def safe_load_json(p: Path) -> Any | None:
    try:
        with p.open(encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"missing: {p}")
    except json.JSONDecodeError as e:
        print(f"bad json in {p}: {e}")
    return None
```

## Context managers beyond files
- Database connections, locks, temporary directory changes (`contextlib`)
- Write your own with `contextlib.contextmanager`

## Common pitfalls
- Forgetting `newline=''` on CSV writes (Windows)
- Blindly using `open('file')` without `encoding` (non‑portable)
- Swallowing exceptions without context (always include file path)

## Practice exercises
1) Write `read_csv_dicts(path) -> list[dict]` that returns rows as dicts with robust error handling
2) Build a converter between CSV and JSON with CLI flags for input/output paths
3) Implement a context manager that temporarily sets `os.environ` vars for a block

## Stretch goals
- Stream CSV in chunks; transform rows and write out a new CSV without loading everything into memory
- Write an `atomic_write(path)` context manager that writes to a temp file and moves it into place on success

## Further reading
- csv docs: https://docs.python.org/3/library/csv.html
- json docs: https://docs.python.org/3/library/json.html
- contextlib: https://docs.python.org/3/library/contextlib.html
