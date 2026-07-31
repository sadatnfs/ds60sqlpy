# Day 23 — Solutions: Data Pipelines and Generators

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **lazy, composable data-pipeline stages with explicit resource and error policy**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **lazy, composable data-pipeline stages with explicit resource and error policy** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Build `stream_clean_csv(path)` that opens a UTF-8 CSV inside the generator, yields one normalized row dictionary at a time, and follows a written malformed-row policy. **Constraints:** use `csv.DictReader`, keep the file open during iteration, and do not return a list. **Verify:** partially consume two rows, consume the rest, test an empty file, and confirm the handle closes after completion/failure.

**Reasoning:** Implement this exact contract as written: Build `stream_clean_csv(path)` that opens a UTF-8 CSV inside the generator, yields one normalized row dictionary at a time, and follows a written malformed-row policy. Constraints: use `csv.DictReader`, keep the file open during iteration, and do not return a list. Keep the prompt's named data and constraints visible in the code, then establish this specific result: partially consume two rows, consume the rest, test an empty file, and confirm the handle closes after completion/failure. That connects the answer to lazy, composable data-pipeline stages with explicit resource and error policy.

```python
import csv
from collections.abc import Iterator
from pathlib import Path
import tempfile


def stream_clean_csv(path: Path) -> Iterator[dict[str, str]]:
    '''Yield normalized valid rows; skip rows missing name or status.'''

    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not row.get("name") or not row.get("status"):
                continue
            yield {
                "name": row["name"].strip(),
                "status": row["status"].strip().lower(),
            }


with tempfile.TemporaryDirectory() as temporary:
    folder = Path(temporary)
    source = folder / "rows.csv"
    source.write_text(
        "name,status\n"
        "Ada,ACTIVE\n"
        "Lin,inactive\n"
        "Grace,active\n",
        encoding="utf-8",
    )
    stream = stream_clean_csv(source)
    first = next(stream)
    second = next(stream)
    rest = list(stream)
    assert first == {"name": "Ada", "status": "active"}
    assert second == {"name": "Lin", "status": "inactive"}
    assert rest == [{"name": "Grace", "status": "active"}]
    assert stream.gi_frame is None

    partial = stream_clean_csv(source)
    assert next(partial)["name"] == "Ada"
    partial.close()
    assert partial.gi_frame is None

    empty = folder / "empty.csv"
    empty.write_text("name,status\n", encoding="utf-8")
    assert list(stream_clean_csv(empty)) == []
```

Because the `with` block surrounds `yield`, the file remains open while
iteration is active and closes on exhaustion or generator close.

**Verification evidence:** partially consume two rows, consume the rest, test an empty file, and confirm the handle closes after completion/failure.

### Exercise 2 — worked answer

**Learner contract:** Compose separate generator stages to filter, map, and batch clean rows. **Contract:** every stage documents input/output shape; batch size must be positive; the final partial batch is yielded. **Verify:** on a five-row fixture with size two, assert exact batches, source order, and input = accepted + quarantined + deliberately filtered counts.

**Reasoning:** Implement this exact contract as written: Compose separate generator stages to filter, map, and batch clean rows. Contract: every stage documents input/output shape; batch size must be positive; the final partial batch is yielded. Keep the prompt's named data and constraints visible in the code, then establish this specific result: on a five-row fixture with size two, assert exact batches, source order, and input = accepted + quarantined + deliberately filtered counts. That connects the answer to lazy, composable data-pipeline stages with explicit resource and error policy.

```python
from collections.abc import Iterable, Iterator


def active(
    rows: Iterable[dict[str, str]],
    audit: dict[str, int],
) -> Iterator[dict[str, str]]:
    '''Map row dictionaries to accepted rows; audit other outcomes.'''

    for row in rows:
        if not row.get("name") or not row.get("status"):
            audit["quarantined"] += 1
        elif row["status"] != "active":
            audit["filtered"] += 1
        else:
            audit["accepted"] += 1
            yield row


def add_label(rows: Iterable[dict[str, str]]) -> Iterator[dict[str, str]]:
    '''Map one accepted row to one copied row with a display label.'''

    for row in rows:
        yield {**row, "label": row["name"].title()}


def batch(
    rows: Iterable[dict[str, str]], size: int
) -> Iterator[tuple[dict[str, str], ...]]:
    '''Map a row stream to ordered tuples of at most ``size`` rows.'''

    if size <= 0:
        raise ValueError("size must be positive")
    current = []
    for row in rows:
        current.append(row)
        if len(current) == size:
            yield tuple(current)
            current = []
    if current:
        yield tuple(current)


fixture = [
    {"name": "ada", "status": "active"},
    {"name": "lin", "status": "inactive"},
    {"name": "grace", "status": "active"},
    {"name": "", "status": "active"},
    {"name": "guido", "status": "active"},
]
audit = {"accepted": 0, "filtered": 0, "quarantined": 0}
result = list(batch(add_label(active(fixture, audit)), 2))
assert [[row["label"] for row in rows] for rows in result] == [
    ["Ada", "Grace"],
    ["Guido"],
]
assert audit == {"accepted": 3, "filtered": 1, "quarantined": 1}
assert len(fixture) == sum(audit.values())
assert [row["name"] for rows in result for row in rows] == [
    "ada", "grace", "guido"
]

try:
    list(batch([], 0))
except ValueError:
    pass
else:
    raise AssertionError("non-positive batch size should fail")
```

**Verification evidence:** on a five-row fixture with size two, assert exact batches, source order, and input = accepted + quarantined + deliberately filtered counts.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict when side effects inside a generator body occur: at function call, first iteration, or full materialization. **Progressive hint:** Calling a generator function creates an iterator; its body starts on iteration. **Verify:** Append an event inside the generator body and assert no event at construction, one at first `next`, and all remaining events only after full consumption.

**Reasoning:** Predict this named state change before running it: Prediction: Predict when side effects inside a generator body occur: at function call, first iteration, or full materialization. Progressive hint: Calling a generator function creates an iterator; its body starts on iteration. Then compare the prediction with this proof target: Append an event inside the generator body and assert no event at construction, one at first `next`, and all remaining events only after full consumption. This makes lazy, composable data-pipeline stages with explicit resource and error policy observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Append an event inside the generator body and assert no event at construction, one at first `next`, and all remaining events only after full consumption.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Consume two items from a five-item generator, then pass it onward. Trace which values the next stage can still see. **Progressive hint:** Consumption is stateful and does not rewind automatically. **Verify:** Assert the first consumer sees values 0 and 1 and the downstream stage sees exactly 2, 3, and 4—never a restarted sequence.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Consume two items from a five-item generator, then pass it onward. Trace which values the next stage can still see. Progressive hint: Consumption is stateful and does not rewind automatically. Record the named value, shape, label, or iterator position needed to establish: Assert the first consumer sees values 0 and 1 and the downstream stage sees exactly 2, 3, and 4—never a restarted sequence. The trace exposes lazy, composable data-pipeline stages with explicit resource and error policy directly.

**Evidence to locate in the grouped implementation:** Assert the first consumer sees values 0 and 1 and the downstream stage sees exactly 2, 3, and 4—never a restarted sequence.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement `batch_rows(rows, size)` yielding tuples and preserving the final partial batch. **Progressive hint:** Validate positive size and reset the accumulator after each yield. **Verify:** Assert five rows at size two produce `[(0, 1), (2, 3), (4,)]`, empty input produces none, and nonpositive size raises.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `batch_rows(rows, size)` yielding tuples and preserving the final partial batch. Progressive hint: Validate positive size and reset the accumulator after each yield. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert five rows at size two produce `[(0, 1), (2, 3), (4,)]`, empty input produces none, and nonpositive size raises. That connects the answer to lazy, composable data-pipeline stages with explicit resource and error policy.

**Evidence to locate in the grouped implementation:** Assert five rows at size two produce `[(0, 1), (2, 3), (4,)]`, empty input produces none, and nonpositive size raises.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a function that returns a generator expression over a file after the surrounding `with` block has already closed the file. **Progressive hint:** Own the `with` block inside the generator that performs iteration. **Verify:** Partially consume the repaired file generator and then finish it; assert rows remain readable until exhaustion and the handle closes afterward.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a function that returns a generator expression over a file after the surrounding `with` block has already closed the file. Progressive hint: Own the `with` block inside the generator that performs iteration. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Partially consume the repaired file generator and then finish it; assert rows remain readable until exhaustion and the handle closes afterward. The diagnosis depends on lazy, composable data-pipeline stages with explicit resource and error policy.

**Evidence to locate in the grouped implementation:** Partially consume the repaired file generator and then finish it; assert rows remain readable until exhaustion and the handle closes afterward.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Add a quarantine side channel for malformed rows without making the clean stream eagerly load the entire file. **Progressive hint:** Pass a callback/list for bounded error records or yield tagged results. **Verify:** Feed valid/invalid/valid rows and assert the clean stream remains lazy, output order is preserved, and accepted plus quarantined counts equal input.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Add a quarantine side channel for malformed rows without making the clean stream eagerly load the entire file. Progressive hint: Pass a callback/list for bounded error records or yield tagged results. Values below, at, and above the named boundary must produce the evidence Feed valid/invalid/valid rows and assert the clean stream remains lazy, output order is preserved, and accepted plus quarantined counts equal input. Those cases show how lazy, composable data-pipeline stages with explicit resource and error policy behaves at its edge.

**Evidence to locate in the grouped implementation:** Feed valid/invalid/valid rows and assert the clean stream remains lazy, output order is preserved, and accepted plus quarantined counts equal input.

## Expanded mastery lab solutions

Build one-responsibility lazy stages with explicit resource ownership, error policy, and final-partial-batch behavior.

### Shared implementation for Exercises 3–4 — Laziness is stateful

A generator body starts on the first `next`, not at function call. After two
items are consumed, downstream stages can see only the remaining three unless a
fresh iterator is constructed.

### Shared implementation for Exercises 5–7 — Batching and correct resource lifetime

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
