# Day 23 — Streaming Data Pipelines and Generators

**Level:** Intermediate

A streaming pipeline bounds memory by processing records incrementally. It also
requires explicit ownership of files, errors, and partial output.

## Learning objectives

By the end of this lesson, you can:

- distinguish streaming from loading an entire dataset;
- write a generator that owns its input resource for the full iteration;
- compose filter, map, and batch stages;
- process CSV records incrementally;
- report malformed rows with enough context to diagnose them.

## Prerequisites

Complete Day 22 (`python-22`), generators from Day 4 (`python-04`), and file I/O
from Day 8 (`python-08`).

## Vocabulary and mental model

- **Streaming:** process a bounded portion while the rest remains unread.
- **Lazy evaluation:** work occurs only as the consumer requests values.
- **Stage:** one transformation with a clear input/output contract.
- **Batch:** bounded collection handled as one unit.
- **Backpressure:** a slower consumer naturally limits how quickly values are
  requested upstream.
- **Partial failure:** some records/output may exist before a later error.

## Worked example

```python
from collections.abc import Iterable, Iterator


def parsed_integers(lines: Iterable[str]) -> Iterator[int]:
    for line_number, raw in enumerate(lines, start=1):
        text = raw.strip()
        if not text:
            continue
        try:
            yield int(text)
        except ValueError as exc:
            raise ValueError(f"line {line_number}: expected integer") from exc


result = list(parsed_integers(["10\n", "\n", "20\n"]))
```

The generator is deterministic and does not require a file. Including the line
number turns a malformed record into actionable evidence.

## Exercises and progressive hints

1. Build a CSV streaming cleaner that yields normalized row dictionaries.
   **Hint:** let the generator open the file inside its own `with` block and use
   `csv.DictReader`; state whether malformed rows stop or are quarantined.
2. Compose generators to filter, map, and batch rows. **Hint:** give every stage
   one responsibility, preserve laziness, and make the final partial batch part
   of the contract.

### Additional mastery practice

Build one-responsibility lazy stages with explicit resource ownership, error policy, and final-partial-batch behavior.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict when side effects inside a generator body occur: at function call, first iteration, or full materialization.
   **Progressive hint:** Calling a generator function creates an iterator; its body starts on iteration.
4. **Tracing:** Consume two items from a five-item generator, then pass it onward. Trace which values the next stage can still see.
   **Progressive hint:** Consumption is stateful and does not rewind automatically.
5. **Implementation:** Implement `batch_rows(rows, size)` yielding tuples and preserving the final partial batch.
   **Progressive hint:** Validate positive size and reset the accumulator after each yield.
6. **Debugging:** Repair a function that returns a generator expression over a file after the surrounding `with` block has already closed the file.
   **Progressive hint:** Own the `with` block inside the generator that performs iteration.
7. **Edge case and explanation:** Add a quarantine side channel for malformed rows without making the clean stream eagerly load the entire file.
   **Progressive hint:** Pass a callback/list for bounded error records or yield tagged results.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- When does a generator function begin executing?
- What happens to an open file if iteration stops early?
- Why is `list(generator)` dangerous for an unbounded stream?
- Where should row numbers and source paths be added to errors?

Expected behavior: rows are processed in order with bounded memory, empty input
produces no batches, and malformed input follows the documented policy.

## Common pitfalls and diagnosis

- **A returned generator reads a closed file:** keep `yield` inside the file's
  `with` block so its lifetime covers iteration.
- **Memory still grows with file size:** a downstream stage called `list`,
  retained all batches, or performed a global sort/group.
- **The final records disappear:** emit the remaining partial batch after the
  source is exhausted.
- **Errors lack record context:** wrap them with source path and line number
  while preserving the original cause.
- **A pipeline can only run once:** iterators are consumable; expose a function
  that constructs a fresh pipeline for each run.

## Continue

- [Open the learner notebook](../notebooks/day23_data_pipelines_generators.ipynb)
- [Check the separate solution](../solutions/day23_data_pipelines_generators/day23_solutions.md)
- [Next: Day 24 — Exploratory data analysis](day24_eda_best_practices.md)
