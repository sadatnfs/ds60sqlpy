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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day23_data_pipelines_generators.md`, then open `python/ds-60day/notebooks/day23_data_pipelines_generators.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 23 — streaming data pipelines and generators to practice lazy, composable data-pipeline stages with explicit resource and error policy
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **pipeline:** an ordered composition of input/output stages.
- **stage:** one transformation with a stated input and output contract.
- **streaming:** processing incrementally rather than loading everything.
- **backpressure:** a consumer limiting how quickly upstream work advances.
- **batch:** a bounded group processed or written together.
- **quarantine:** separate retention of invalid records and failure reasons.

### Syntax anatomy

`yield normalized` pauses a generator stage after producing one record.
`yield from iterable` delegates successive values to another iterable.
A consumer such as `for batch in batches(rows, 100):` drives the whole
upstream chain; without consumption, no generator body or file read
occurs.

### Worked example 1 — Compose lazy normalization and filtering

Each stage consumes and yields one record at a time. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
`[{'name': 'Ada', 'status': 'active'}]`. No stage needed all records at once.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Preserve a final partial batch

Batch boundaries are part of the contract. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
`[(0, 1), (2, 3), (4,)]`. The last partial batch is not silently lost.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Test each stage with a tiny list before composing the pipeline.
2. If no work occurs, confirm that a consumer actually iterates the generator.
3. Keep a file's `with` block inside the generator that performs iteration.
4. Count input, accepted, quarantined, and output records to reconcile every path.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Use eager lists for small data and simple debugging; use lazy stages when memory, streaming, or early stopping matters.

**Boundary to remember:** Partial consumption, consumer failure, invalid batch size, final partial batch, malformed first/last rows, and cleanup on exceptions need tests.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Build `stream_clean_csv(path)` that opens a UTF-8 CSV inside the generator, yields one normalized row dictionary at a time, and follows a written malformed-row policy. **Constraints:** use `csv.DictReader`, keep the file open during iteration, and do not return a list.
   **Verify:** partially consume two rows, consume the rest, test an empty file, and confirm the handle closes after completion/failure.

2. Compose separate generator stages to filter, map, and batch clean rows. **Contract:** every stage documents input/output shape; batch size must be positive; the final partial batch is yielded.
   **Verify:** on a five-row fixture with size two, assert exact batches, source order, and input = accepted + quarantined + deliberately filtered counts.

### Additional mastery practice

Build one-responsibility lazy stages with explicit resource ownership, error policy, and final-partial-batch behavior.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict when side effects inside a generator body occur: at function call, first iteration, or full materialization.
   **Progressive hint:** Calling a generator function creates an iterator; its body starts on iteration.
   **Verify:** Append an event inside the generator body and assert no event at construction, one at first `next`, and all remaining events only after full consumption.
4. **Tracing:** Consume two items from a five-item generator, then pass it onward. Trace which values the next stage can still see.
   **Progressive hint:** Consumption is stateful and does not rewind automatically.
   **Verify:** Assert the first consumer sees values 0 and 1 and the downstream stage sees exactly 2, 3, and 4—never a restarted sequence.
5. **Implementation:** Implement `batch_rows(rows, size)` yielding tuples and preserving the final partial batch.
   **Progressive hint:** Validate positive size and reset the accumulator after each yield.
   **Verify:** Assert five rows at size two produce `[(0, 1), (2, 3), (4,)]`, empty input produces none, and nonpositive size raises.
6. **Debugging:** Repair a function that returns a generator expression over a file after the surrounding `with` block has already closed the file.
   **Progressive hint:** Own the `with` block inside the generator that performs iteration.
   **Verify:** Partially consume the repaired file generator and then finish it; assert rows remain readable until exhaustion and the handle closes afterward.
7. **Edge case and explanation:** Add a quarantine side channel for malformed rows without making the clean stream eagerly load the entire file.
   **Progressive hint:** Pass a callback/list for bounded error records or yield tagged results.
   **Verify:** Feed valid/invalid/valid rows and assert the clean stream remains lazy, output order is preserved, and accepted plus quarantined counts equal input.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-23`
(Day 23 — Streaming Data Pipelines and Generators). Direct catalog prerequisites: `python-22`.
I have completed the direct prerequisites: `python-22`. Emphasize lazy, composable data-pipeline stages with explicit resource and error policy.
Read `python/ds-60day/companion-guides/day23_data_pipelines_generators.md` and use the learner notebook
`python/ds-60day/notebooks/day23_data_pipelines_generators.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
