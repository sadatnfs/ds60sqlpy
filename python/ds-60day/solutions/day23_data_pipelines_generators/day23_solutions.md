# Day 23 — Solutions: Data Pipelines and Generators

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**lazy, composable data-pipeline stages with explicit resource and error policy**.

A pipeline is a sequence of stages that turn input into output. Give each
stage one responsibility—read, parse, validate, normalize, filter,
batch, or write—and define the shape it accepts and yields. Small stages
are easier to test and recombine than one function mixing files, rules,
logging, and output.

Generator stages keep memory bounded by yielding one item at a time.
Calling a generator function does not run its body; iteration starts
work and advances state. The stage that opens a resource should own its
`with` block for the entire iteration. Decide whether malformed records
stop the stream, are skipped with evidence, or go to quarantine.

### Vocabulary used in the worked answers

- **pipeline:** an ordered composition of input/output stages.
- **stage:** one transformation with a stated input and output contract.
- **streaming:** processing incrementally rather than loading everything.
- **backpressure:** a consumer limiting how quickly upstream work advances.
- **batch:** a bounded group processed or written together.
- **quarantine:** separate retention of invalid records and failure reasons.

### Reference pattern 1 — Compose lazy normalization and filtering

Each stage consumes and yields one record at a time.

```python
from collections.abc import Iterable, Iterator

def normalize(rows: Iterable[dict[str, str]]) -> Iterator[dict[str, str]]:
    for row in rows:
        yield {"name": row["name"].strip(), "status": row["status"].lower()}

def active_only(rows: Iterable[dict[str, str]]) -> Iterator[dict[str, str]]:
    for row in rows:
        if row["status"] == "active":
            yield row

source = [{"name": " Ada ", "status": "ACTIVE"}, {"name": "Lin", "status": "inactive"}]
list(active_only(normalize(source)))
```

**Expected observation:** `[{'name': 'Ada', 'status': 'active'}]`. No stage needed all records at once.

### Reference pattern 2 — Preserve a final partial batch

Batch boundaries are part of the contract.

```python
def batches(items: Iterable[int], size: int) -> Iterator[tuple[int, ...]]:
    if size <= 0:
        raise ValueError("size must be positive")
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield tuple(batch)
            batch = []
    if batch:
        yield tuple(batch)

list(batches(range(5), 2))
```

**Expected observation:** `[(0, 1), (2, 3), (4,)]`. The last partial batch is not silently lost.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Build `stream_clean_csv(path)` that opens a UTF-8 CSV inside the generator, yields one normalized row dictionary at a time, and follows a written malformed-row policy. **Constraints:** use `csv.DictReader`, keep the file open during iteration, and do not return a list. **Verify:** partially consume two rows, consume the rest, test an empty file, and confirm the handle closes after completion/failure.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies lazy, composable data-pipeline stages with explicit resource and error policy.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** partially consume two rows, consume the rest, test an empty file, and confirm the handle closes after completion/failure.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Compose separate generator stages to filter, map, and batch clean rows. **Contract:** every stage documents input/output shape; batch size must be positive; the final partial batch is yielded. **Verify:** on a five-row fixture with size two, assert exact batches, source order, and input = accepted + quarantined + deliberately filtered counts.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies lazy, composable data-pipeline stages with explicit resource and error policy.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** on a five-row fixture with size two, assert exact batches, source order, and input = accepted + quarantined + deliberately filtered counts.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict when side effects inside a generator body occur: at function call, first iteration, or full materialization. **Progressive hint:** Calling a generator function creates an iterator; its body starts on iteration. **Verify:** Append an event inside the generator body and assert no event at construction, one at first `next`, and all remaining events only after full consumption.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying lazy, composable data-pipeline stages with explicit resource and error policy.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** Append an event inside the generator body and assert no event at construction, one at first `next`, and all remaining events only after full consumption.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Consume two items from a five-item generator, then pass it onward. Trace which values the next stage can still see. **Progressive hint:** Consumption is stateful and does not rewind automatically. **Verify:** Assert the first consumer sees values 0 and 1 and the downstream stage sees exactly 2, 3, and 4—never a restarted sequence.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the lazy, composable data-pipeline stages with explicit resource and error policy model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** Assert the first consumer sees values 0 and 1 and the downstream stage sees exactly 2, 3, and 4—never a restarted sequence.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `batch_rows(rows, size)` yielding tuples and preserving the final partial batch. **Progressive hint:** Validate positive size and reset the accumulator after each yield. **Verify:** Assert five rows at size two produce `[(0, 1), (2, 3), (4,)]`, empty input produces none, and nonpositive size raises.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies lazy, composable data-pipeline stages with explicit resource and error policy.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** Assert five rows at size two produce `[(0, 1), (2, 3), (4,)]`, empty input produces none, and nonpositive size raises.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a function that returns a generator expression over a file after the surrounding `with` block has already closed the file. **Progressive hint:** Own the `with` block inside the generator that performs iteration. **Verify:** Partially consume the repaired file generator and then finish it; assert rows remain readable until exhaustion and the handle closes afterward.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in lazy, composable data-pipeline stages with explicit resource and error policy.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** Partially consume the repaired file generator and then finish it; assert rows remain readable until exhaustion and the handle closes afterward.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Add a quarantine side channel for malformed rows without making the clean stream eagerly load the entire file. **Progressive hint:** Pass a callback/list for bounded error records or yield tagged results. **Verify:** Feed valid/invalid/valid rows and assert the clean stream remains lazy, output order is preserved, and accepted plus quarantined counts equal input.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from lazy, composable data-pipeline stages with explicit resource and error policy.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Edge case:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.

**Solution evidence to inspect:** Feed valid/invalid/valid rows and assert the clean stream remains lazy, output order is preserved, and accepted plus quarantined counts equal input.
<!-- END BEGINNER SOLUTION REVIEW -->

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
