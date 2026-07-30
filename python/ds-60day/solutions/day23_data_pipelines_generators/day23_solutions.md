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

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Build a CSV streaming cleaner that yields normalized row dictionaries. **Hint:** let the generator open the file inside its own `with` block and use `csv.DictReader`; state whether malformed rows stop or are quarantined.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Compose generators to filter, map, and batch rows. **Hint:** give every stage one responsibility, preserve laziness, and make the final partial batch part of the contract.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict when side effects inside a generator body occur: at function call, first iteration, or full materialization.

**Reasoning checkpoint:** Calling a generator function creates an iterator; its body starts on iteration. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Consume two items from a five-item generator, then pass it onward. Trace which values the next stage can still see.

**Reasoning checkpoint:** Consumption is stateful and does not rewind automatically. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement `batch_rows(rows, size)` yielding tuples and preserving the final partial batch.

**Reasoning checkpoint:** Validate positive size and reset the accumulator after each yield. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a function that returns a generator expression over a file after the surrounding `with` block has already closed the file.

**Reasoning checkpoint:** Own the `with` block inside the generator that performs iteration. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Add a quarantine side channel for malformed rows without making the clean stream eagerly load the entire file.

**Reasoning checkpoint:** Pass a callback/list for bounded error records or yield tagged results. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Build one-responsibility lazy stages with explicit resource ownership, error policy, and final-partial-batch behavior.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Laziness is stateful

A generator body starts on the first `next`, not at function call. After two
items are consumed, downstream stages can see only the remaining three unless a
fresh iterator is constructed.

### Practices 3–5 — Batching and correct resource lifetime

```python
from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")


def batch_rows(rows: Iterable[T], size: int) -> Iterator[tuple[T, ...]]:
    """Yield tuples no larger than size, including a final partial tuple."""

    if size <= 0:
        raise ValueError("size must be positive")
    batch: list[T] = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield tuple(batch)
            batch.clear()
    if batch:
        yield tuple(batch)


def nonblank_lines(path: Path, rejected: list[tuple[int, str]]) -> Iterator[str]:
    """Yield normalized lines while recording bounded malformed-line evidence."""

    # The file remains open for exactly as long as iteration needs it.
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            normalized = raw.strip()
            if not normalized:
                if len(rejected) < 100:
                    rejected.append((line_number, "blank line"))
                continue
            yield normalized


assert list(batch_rows(range(5), 2)) == [(0, 1), (2, 3), (4,)]
```

The bounded quarantine prevents unbounded memory growth while leaving the
successful stream lazy. A production pipeline might yield a tagged result
object to route successes and errors to separate sinks.
