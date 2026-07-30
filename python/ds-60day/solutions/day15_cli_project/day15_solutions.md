# Day 15 — Solutions: CLI Data Tool Project

We scaffold a small CLI that loads a CSV, cleans it, and writes a summary and cleaned output, with tests.

Contents
- Project layout
- Core transforms with tests
- CLI wired with argparse

---

Project layout
```
project/
  pyproject.toml
  src/
    cli.py
    io_utils.py
    transforms.py
  tests/
    test_transforms.py
```

src/transforms.py
```python
from __future__ import annotations
from typing import Sequence
import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    # Example cleaning: drop NA rows in key cols and convert types
    d = d.rename(columns=str.lower)
    if "date" in d.columns:
        d["date"] = pd.to_datetime(d["date"], errors="coerce", utc=True)
    for c in ("price", "qty"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=[c for c in ("price","qty") if c in d.columns])
    return d


def summarize(d: pd.DataFrame) -> pd.DataFrame:
    # Example summary: total revenue by day (if present)
    if {"price","qty"}.issubset(d.columns):
        d = d.assign(revenue=d["price"] * d["qty"])
    if "date" in d.columns:
        return d.groupby(d["date"].dt.date).agg(revenue=("revenue","sum"))
    return d.agg(revenue=("revenue","sum")).to_frame().T
```

src/io_utils.py
```python
from pathlib import Path
import pandas as pd

def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
```

src/cli.py
```python
import argparse
from pathlib import Path
from .io_utils import read_csv, write_csv
from .transforms import clean, summarize

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=False)
    args = ap.parse_args(argv)

    df = read_csv(args.input)
    tidy = clean(df)
    write_csv(tidy, args.out)
    if args.summary:
        summ = summarize(tidy)
        write_csv(summ, args.summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

tests/test_transforms.py
```python
import pandas as pd
from src.transforms import clean, summarize

def test_clean_and_summary():
    df = pd.DataFrame({"date":["2025-01-01","bad"],"price":["10","x"],"qty":[2,3]})
    tidy = clean(df)
    assert list(tidy.columns) >= ["date","price","qty"]
    assert tidy["price"].dtype.kind in "fi"   # numeric
    summ = summarize(tidy)
    assert "revenue" in summ.columns
```

Run
```bash
pytest -q
python -m src.cli --input data.csv --out out.csv --summary summary.csv
```
Notes
- Keep transforms pure and I/O thin for testability.
- Extend as needed (schemas, logging, error handling).

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Read a CSV with pandas, drop or handle required missing values, and convert documented column types. **Hint:** make `clean(frame)` return a copy so a caller's input is not silently mutated.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Compute summary statistics and save a cleaned CSV. **Hint:** keep read/write functions separate from transforms and create parent directories deliberately.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Provide `--input` and `--out` with `argparse`; the intended invocation is `python tool.py --input data.csv --out out.csv`. **Hint:** use `type=Path` and `required=True`; do not introduce Click.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Original lesson practice

**Prompt:** Test core functions and one parser path. **Hint:** use tiny in-memory frames and pytest's `tmp_path`, not large external data.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 5 — Original lesson practice

**Prompt:** Run Ruff lint/format checks, mypy, and pytest. **Hint:** use the same commands as Day 14 and inspect the first failure before continuing. Store practice source in a tracked project directory. Put disposable generated files under ignored `artifacts/`; never commit `.venv`, caches, secrets, or a machine-specific `.env`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 6 — Prediction

**Prompt:** Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`.

**Reasoning checkpoint:** The parser performs declared conversions before `main` receives values. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Tracing

**Prompt:** Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work.

**Reasoning checkpoint:** A pure transform accepts and returns data without reading global state. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Implementation

**Prompt:** Add `--overwrite` and refuse to replace an existing output unless the flag is present.

**Reasoning checkpoint:** Check the destination before performing the write. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 9 — Debugging

**Prompt:** Repair a module that parses arguments and writes files during import.

**Reasoning checkpoint:** Move behavior into `main(argv)` and use the `__main__` guard. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 10 — Edge case and explanation

**Prompt:** Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log.

**Reasoning checkpoint:** Translate expected boundary failures once, without hiding tracebacks in tests. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Keep command parsing and file I/O at thin boundaries around pure, importable transformations. Make failures observable through exit codes.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Parsed types and boundaries

`type=Path` produces a `Path`; `type=int` produces an integer or lets argparse
report invalid text. Reading and writing are boundaries; deterministic cleaning
and summarization should be pure enough to test in memory.

### Practices 3–5 — Safe overwrite and importable entry point

```python
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean a course CSV")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def ensure_writable_output(path: Path, *, overwrite: bool) -> None:
    """Reject accidental replacement before any output is opened."""

    if path.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if not args.input.is_file():
            raise FileNotFoundError(f"input not found: {args.input}")
        ensure_writable_output(args.out, overwrite=args.overwrite)
        # read -> clean -> summarize -> write belongs here.
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"error: {error}")   # One user-facing boundary translation.
        return 2
    return 0


parsed = parse_args(["--input", "in.csv", "--out", "out.csv", "--limit", "10"])
assert isinstance(parsed.input, Path) and parsed.limit == 10

# Production module only:
# if __name__ == "__main__":
#     raise SystemExit(main())
```

Expected user/data errors can return `2`; unexpected programming failures
should propagate during tests and normally produce a controlled top-level log
with a distinct nonzero code in a production application.
