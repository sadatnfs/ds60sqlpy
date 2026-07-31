# Day 11 — Debugging, Logging, and Profiling

**Level:** Beginner

Debugging explains incorrect behavior; logging records useful runtime events;
profiling locates where time is actually spent. Measure before optimizing.

## Learning objectives

By the end of this lesson, you can:

- reduce a failure to a small reproducible case and read its traceback;
- choose an appropriate log level and attach useful context;
- time a focused expression with `timeit`;
- profile a call tree with `cProfile`;
- distinguish an algorithmic improvement from a micro-optimization.

## Prerequisites

Complete Day 10 (`python-10`): tests, exceptions, importable utilities.





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

2. Read `python/ds-60day/companion-guides/day11_debug_logging_profiling.md`, then open `python/ds-60day/notebooks/day11_debug_logging_profiling.ipynb` from the repository
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

**Lesson outcome:** use day 11 — debugging, logging, and profiling to practice evidence-driven debugging, useful logs, and measurement before optimization
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

Debugging is the process of reducing uncertainty. Start from an
observable symptom, make the smallest reproducible case, form one
hypothesis, and collect evidence that could disprove it. Reading the
traceback from the final exception line upward usually identifies the
failure type before the stack frames identify how execution arrived
there.

Logging records meaningful runtime events for later inspection;
debugging explores a live failure; profiling measures where time or
memory is actually spent. A log entry should add context without
exposing credentials or personal data. Optimization begins after a
representative measurement, not after guessing which line “looks slow.”

### Vocabulary in plain language

- **symptom:** the observable incorrect output, failure, or slowdown.
- **traceback:** the exception report showing failure type and active call stack.
- **hypothesis:** a testable explanation for the observed symptom.
- **log level:** severity such as DEBUG, INFO, WARNING, or ERROR.
- **profiler:** a tool that measures resource use by code location.
- **benchmark:** a repeatable timing or resource comparison under stated conditions.

### Syntax anatomy

`logger.info("loaded rows=%d", row_count)` separates a stable message
template from its value; logging formats it only when the level is
enabled. In a traceback, the last line names the exception, while the
preceding frames show calls from outermost to innermost. With `timeit`,
setup and repeated statement execution are deliberately separated.

### Worked example 1 — Add context at the boundary

A small function logs an outcome without dumping the input records. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import logging

logger = logging.getLogger("day11")
logger.setLevel(logging.INFO)

def accepted_count(values: list[int]) -> int:
    count = sum(value >= 0 for value in values)
    logger.info("accepted=%d total=%d", count, len(values))
    return count

accepted_count([4, -1, 0])
```

**Expected observation**

```text
The function returns `2`; when the notebook has a visible logging handler, one INFO event reports counts rather than raw sensitive values.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Measure two equivalent membership strategies

Use repeated representative work instead of one noisy timestamp. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
from timeit import timeit

values = list(range(1_000))
value_set = set(values)
list_seconds = timeit("999 in values", number=5_000, globals=globals())
set_seconds = timeit("999 in value_set", number=5_000, globals=globals())
{"same_answer": (999 in values) == (999 in value_set),
 "set_faster_here": set_seconds < list_seconds}
```

**Expected observation**

```text
Both lookups agree and the set is normally faster in this repeated lookup scenario. Exact durations vary by computer and are not asserted.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Write the exact expected and actual behavior before changing code.
2. Reduce the input until the failure still reproduces, then inspect the final traceback line.
3. Add structured context such as IDs or counts, never passwords or entire private records.
4. Benchmark the original and candidate with the same setup and verify they return equivalent results.

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

**Useful alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Boundary to remember:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Traceback:** stack of calls leading to an uncaught exception; read the final
  exception first, then move upward into your code.
- **Log level:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`, indicating
  severity and intended audience.
- **Benchmark:** controlled measurement of a specific operation.
- **Profile:** distribution of runtime across functions/calls.
- **Hot spot:** code responsible for a meaningful share of runtime.

A stopwatch tells you *that* work is slow; a profiler helps locate *where*.

## Worked example

```python
import logging
import timeit

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def unique_count(values: list[int]) -> int:
    return len(set(values))


values = list(range(1_000))
logger.info("benchmarking unique_count count=%d", len(values))
elapsed = timeit.timeit(lambda: unique_count(values), number=10)
print(f"{elapsed=:.6f}s")
```

Configure logging once at an application entry point. Library code should emit
records through its module logger, not repeatedly call `basicConfig`.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Start from a supplied failing function and use `breakpoint()` or the VS Code debugger to pause immediately before the wrong value is produced. **Evidence:** record the call arguments, two relevant local variables, and the branch taken. **Constraint:** do not change logic until you can state one falsifiable hypothesis.
   **Verify:** after the fix, rerun the original failing input and one nearby passing input.

2. Add module-level logging with `logging.getLogger(__name__)` and emit useful DEBUG/INFO/WARNING events for a small processing function. **Constraints:** use lazy `%s`/`%d` formatting, do not call `basicConfig` inside reusable library logic, and log counts/identifiers rather than sensitive record contents.
   **Verify:** demonstrate that changing the configured level changes visibility without changing the returned value.

3. Profile a deliberately slow membership or aggregation function with `cProfile` or `timeit`, implement one behavior-preserving improvement, and compare under identical inputs.
   **Expected behavior:** outputs match exactly and the measurement identifies where time changed. **Constraint:** report repeated timings rather than claiming from a single run.
   **Verify:** Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change.

### Additional mastery practice

Observe before optimizing: reproduce a defect, add bounded context, profile representative work, and change the measured bottleneck.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted.
   **Progressive hint:** The threshold keeps records at that level or more severe.
   **Verify:** Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold.
5. **Tracing:** Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption.
   **Progressive hint:** Read a traceback from the final exception upward through your code.
   **Verify:** Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly.
6. **Implementation:** Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging.
   **Progressive hint:** Put elapsed-time logging in `finally` so failures are still timed.
   **Verify:** Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed.
7. **Debugging:** Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers.
   **Progressive hint:** Configuration is process state; inspect handlers before adding one.
   **Verify:** Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message.
8. **Edge case and explanation:** Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification.
   **Progressive hint:** A faster wrong answer is not an optimization.
   **Verify:** Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- What is the first traceback line you should interpret?
- Why is an f-string inside a disabled debug log less efficient than `%s`
  placeholders?
- Why can a single timing result be misleading?
- What evidence would justify an optimization?

Expected behavior: logs explain the operation without exposing data, profiling
identifies a measured bottleneck, and tests still pass after optimization.

## Common pitfalls and diagnosis

- **Duplicate log lines:** handlers were configured more than once, often in
  both a library and entry point.
- **Logs are silent:** inspect the configured level and logger hierarchy.
- **Timing includes setup/I/O:** move data construction outside the measured
  statement and repeat the measurement.
- **The "optimized" result changed:** run tests and compare representative
  outputs before comparing speed.
- **`print` statements scatter through library code:** use a module logger so
  callers control destination and verbosity.

## Continue

- [Open the learner notebook](../notebooks/day11_debug_logging_profiling.ipynb)
- [Check the separate solution](../solutions/day11_debug_logging_profiling/day11_solutions.md)
- [Next: Day 12 — OOP and dataclasses](day12_oop_dataclasses.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-11`
(Day 11 — Debugging, Logging, and Profiling). I am a complete beginner. Emphasize evidence-driven debugging, useful logs, and measurement before optimization.
Read `python/ds-60day/companion-guides/day11_debug_logging_profiling.md` and use the learner notebook
`python/ds-60day/notebooks/day11_debug_logging_profiling.ipynb`. Do not open or quote anything under `solutions/` unless
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
