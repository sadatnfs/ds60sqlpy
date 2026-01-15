# Day 23 — Solutions: Data Pipelines and Generators

We build a streaming CSV cleaner and compose generators to filter/map/batch rows.

Contents
- Exercise 1: CSV streaming cleaner (yield rows)
- Exercise 2: Compose generators to filter, map, and batch

---

Exercise 1 — CSV streaming cleaner
```python
from __future__ import annotations
from typing import Iterable, Iterator
import csv
from pathlib import Path


def stream_csv(path: Path) -> Iterator[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def clean_rows(rows: Iterable[dict[str, str]]) -> Iterator[dict[str, str]]:
    for r in rows:
        # Example cleanup: trim spaces and uppercase a code field
        r = {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
        if 'code' in r and isinstance(r['code'], str):
            r['code'] = r['code'].upper()
        yield r

# Usage:
# for row in clean_rows(stream_csv(Path('data.csv'))):
#     process(row)
```
Line-by-line
- stream_csv yields one row at a time; no large list in memory
- clean_rows transforms without side effects outside the generator

---

Exercise 2 — Compose filter/map/batch
```python
from itertools import islice
from typing import Iterable, Iterator, Callable, TypeVar

T = TypeVar('T')


def only_if(rows: Iterable[T], pred: Callable[[T], bool]) -> Iterator[T]:
    for r in rows:
        if pred(r):
            yield r


def mapper(rows: Iterable[T], fn: Callable[[T], T]) -> Iterator[T]:
    for r in rows:
        yield fn(r)


def batched(rows: Iterable[T], size: int) -> Iterator[list[T]]:
    it = iter(rows)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        yield chunk

# Example: filter rows by predicate, map to typed dict, then batch
# pipeline = batched(
#     mapper(
#         only_if(clean_rows(stream_csv(Path('data.csv'))), lambda r: r.get('qty','0').isdigit()),
#         lambda r: {**r, 'qty': int(r['qty'])}
#     ),
#     size=500
#)
# for chunk in pipeline:
#     bulk_insert(chunk)
```
Notes
- Keep transforms pure; side effects (DB writes) occur at pipeline edges
- Use itertools and generator composition to stay memory-efficient
