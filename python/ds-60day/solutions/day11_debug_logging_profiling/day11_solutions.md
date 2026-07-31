# Day 11 — Solutions: Debugging, Logging, and Profiling

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **evidence-driven debugging, useful logs, and measurement before optimization**. Predict each named
result before comparing your attempt with its matching assertions.

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

### Vocabulary used in the worked answers

- **symptom:** the observable incorrect output, failure, or slowdown.
- **traceback:** the exception report showing failure type and active call stack.
- **hypothesis:** a testable explanation for the observed symptom.
- **log level:** severity such as DEBUG, INFO, WARNING, or ERROR.
- **profiler:** a tool that measures resource use by code location.
- **benchmark:** a repeatable timing or resource comparison under stated conditions.

### How to compare an answer

For this lesson's **evidence-driven debugging, useful logs, and measurement before optimization** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Start from a supplied failing function and use `breakpoint()` or the VS Code debugger to pause immediately before the wrong value is produced. **Evidence:** record the call arguments, two relevant local variables, and the branch taken. **Constraint:** do not change logic until you can state one falsifiable hypothesis. **Verify:** record the original failing test result before repair, then assert that exact input and one nearby passing input both produce their expected values after the fix.

**Reasoning:** Reproduce the exact failure described here before changing code: Start from a supplied failing function and use `breakpoint()` or the VS Code debugger to pause immediately before the wrong value is produced. Evidence: record the call arguments, two relevant local variables, and the branch taken. Constraint: do not change logic until you can state one falsifiable hypothesis. Preserve that failing case, repair the violated rule, and rerun the evidence named here: record the original failing test result before repair, then assert that exact input and one nearby passing input both produce their expected values after the fix. The diagnosis depends on evidence-driven debugging, useful logs, and measurement before optimization.

```python
def average_positive(values: list[float]) -> float:
    positives = [value for value in values if value > 0]
    if not positives:
        raise ValueError("at least one positive value is required")

    # In VS Code, set a breakpoint on the return line. At the pause,
    # inspect values, positives, sum(positives), and len(positives).
    # Temporarily writing `breakpoint()` here gives the same view in a
    # terminal; remove it after the diagnosis.
    return sum(positives) / len(positives)


failing_input = [-100.0, 10.0, 20.0]
result = average_positive(failing_input)
assert result == 15.0
```

The original bug divided by `len(values)` and returned `10.0`.
Pausing immediately before that division reveals `sum(positives) == 30`
but a denominator of `3`; the violated contract says only positive
values belong to both numerator and denominator. After the one-line
repair, rerun the original case and the no-positive boundary.

**Verification evidence:** record the original failing test result before repair, then assert that exact input and one nearby passing input both produce their expected values after the fix.

### Exercise 2 — worked answer

**Learner contract:** Add module-level logging with `logging.getLogger(__name__)` and emit useful DEBUG/INFO/WARNING events for a small processing function. **Constraints:** use lazy `%s`/`%d` formatting, do not call `basicConfig` inside reusable library logic, and log counts/identifiers rather than sensitive record contents. **Verify:** demonstrate that changing the configured level changes visibility without changing the returned value.

**Reasoning:** Implement this exact contract as written: Add module-level logging with `logging.getLogger(__name__)` and emit useful DEBUG/INFO/WARNING events for a small processing function. Constraints: use lazy `%s`/`%d` formatting, do not call `basicConfig` inside reusable library logic, and log counts/identifiers rather than sensitive record contents. Keep the prompt's named data and constraints visible in the code, then establish this specific result: demonstrate that changing the configured level changes visibility without changing the returned value. That connects the answer to evidence-driven debugging, useful logs, and measurement before optimization.

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def report_file(path: Path) -> int:
    logger.debug("reading file=%s", path.name)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("missing file=%s", path.name)
        return 0
    line_count = len(text.splitlines())
    logger.info("read lines=%d file=%s", line_count, path.name)
    return line_count
```

Library code emits contextual records but leaves handler/level
configuration to the application. It logs a basename and counts, not
file contents or credentials.

**Verification evidence:** demonstrate that changing the configured level changes visibility without changing the returned value.

### Exercise 3 — worked answer

**Learner contract:** Profile a deliberately slow membership or aggregation function with `cProfile` or `timeit`, implement one behavior-preserving improvement, and compare under identical inputs. **Expected behavior:** outputs match exactly and the measurement identifies where time changed. **Constraint:** report repeated timings rather than claiming from a single run. **Verify:** Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change.

**Reasoning:** Implement this exact contract as written: Profile a deliberately slow membership or aggregation function with `cProfile` or `timeit`, implement one behavior-preserving improvement, and compare under identical inputs. Expected behavior: outputs match exactly and the measurement identifies where time changed. Constraint: report repeated timings rather than claiming from a single run. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change. That connects the answer to evidence-driven debugging, useful logs, and measurement before optimization.

```python
from timeit import repeat


def contains_with_list(values: list[int], queries: list[int]) -> list[bool]:
    return [query in values for query in queries]


def contains_with_set(values: list[int], queries: list[int]) -> list[bool]:
    lookup = set(values)
    return [query in lookup for query in queries]


values = list(range(1_000))
queries = list(range(900, 1_100))
expected = contains_with_list(values, queries)
assert contains_with_set(values, queries) == expected

list_trials = repeat(
    lambda: contains_with_list(values, queries), repeat=5, number=100
)
set_trials = repeat(
    lambda: contains_with_set(values, queries), repeat=5, number=100
)
assert len(list_trials) == len(set_trials) == 5
```

Compare distributions rather than asserting a duration that will be
brittle across computers. The equality assertion proves behavior before
timing; the five samples expose run-to-run variation. Save the fixture
and use cProfile when call-level evidence is needed:

```text
python -m cProfile -s cumulative your_profile_fixture.py
```

The list version repeatedly scans up to 1,000 values for every query.
The set version pays one construction cost and then uses expected
constant-time membership checks.

**Verification evidence:** Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted. **Progressive hint:** The threshold keeps records at that level or more severe. **Verify:** Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold.

**Reasoning:** Predict this named state change before running it: Prediction: With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted. Progressive hint: The threshold keeps records at that level or more severe. Then compare the prediction with this proof target: Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold. This makes evidence-driven debugging, useful logs, and measurement before optimization observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption. **Progressive hint:** Read a traceback from the final exception upward through your code. **Verify:** Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption. Progressive hint: Read a traceback from the final exception upward through your code. Record the named value, shape, label, or iterator position needed to establish: Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly. The trace exposes evidence-driven debugging, useful logs, and measurement before optimization directly.

**Evidence to locate in the grouped implementation:** Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging. **Progressive hint:** Put elapsed-time logging in `finally` so failures are still timed. **Verify:** Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed.

**Reasoning:** Implement this exact contract as written: Implementation: Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging. Progressive hint: Put elapsed-time logging in `finally` so failures are still timed. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed. That connects the answer to evidence-driven debugging, useful logs, and measurement before optimization.

**Evidence to locate in the grouped implementation:** Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers. **Progressive hint:** Configuration is process state; inspect handlers before adding one. **Verify:** Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers. Progressive hint: Configuration is process state; inspect handlers before adding one. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message. The diagnosis depends on evidence-driven debugging, useful logs, and measurement before optimization.

**Evidence to locate in the grouped implementation:** Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification. **Progressive hint:** A faster wrong answer is not an optimization. **Verify:** Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification. Progressive hint: A faster wrong answer is not an optimization. Values below, at, and above the named boundary must produce the evidence Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions. Those cases show how evidence-driven debugging, useful logs, and measurement before optimization behaves at its edge.

**Evidence to locate in the grouped implementation:** Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions.

## Expanded mastery lab solutions

Observe before optimizing: reproduce a defect, add bounded context, profile representative work, and change the measured bottleneck.

### Shared implementation for Exercises 4–5 — Logging and traceback reading

At `WARNING`, warning and error records are emitted. Start traceback diagnosis
at the deepest frame in code you control, then inspect the input and assumption
there before editing callers.

### Shared implementation for Exercises 6–8 — A timing tool and a fair benchmark

```python
from __future__ import annotations

import logging
from contextlib import contextmanager
from time import perf_counter
from collections.abc import Iterator

logger = logging.getLogger("ds60.day11")
logger.setLevel(logging.INFO)
if not logger.handlers:
    # Add exactly one local handler in an interactive process.
    logger.addHandler(logging.NullHandler())


@contextmanager
def timed(label: str) -> Iterator[None]:
    """Log elapsed time for a block, including blocks that raise."""

    started = perf_counter()
    try:
        yield
    finally:
        elapsed = perf_counter() - started
        logger.info("%s completed in %.6f seconds", label, elapsed)


def loop_sum(values: list[int]) -> int:
    total = 0
    for value in values:
        total += value
    return total


values = list(range(1_000))
with timed("loop_sum"):
    loop_result = loop_sum(values)
with timed("built_in_sum"):
    built_in_result = sum(values)

# Verify equivalent behavior before comparing repeated timings.
assert loop_result == built_in_result
```

For a real benchmark, reuse equivalent input, warm both paths, run multiple
trials, report a distribution, and keep logging/I/O outside the timed region.
