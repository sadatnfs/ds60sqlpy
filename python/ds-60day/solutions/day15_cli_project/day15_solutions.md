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
