# Day 11 — Solutions: Debugging, Logging, and Profiling

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**evidence-driven debugging, useful logs, and measurement before optimization**.

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

### Reference pattern 1 — Add context at the boundary

A small function logs an outcome without dumping the input records.

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

**Expected observation:** The function returns `2`; when the notebook has a visible logging handler, one INFO event reports counts rather than raw sensitive values.

### Reference pattern 2 — Measure two equivalent membership strategies

Use repeated representative work instead of one noisy timestamp.

```python
from timeit import timeit

values = list(range(1_000))
value_set = set(values)
list_seconds = timeit("999 in values", number=5_000, globals=globals())
set_seconds = timeit("999 in value_set", number=5_000, globals=globals())
{"same_answer": (999 in values) == (999 in value_set),
 "set_faster_here": set_seconds < list_seconds}
```

**Expected observation:** Both lookups agree and the set is normally faster in this repeated lookup scenario. Exact durations vary by computer and are not asserted.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Start from a supplied failing function and use `breakpoint()` or the VS Code debugger to pause immediately before the wrong value is produced. **Evidence:** record the call arguments, two relevant local variables, and the branch taken. **Constraint:** do not change logic until you can state one falsifiable hypothesis. **Verify:** after the fix, rerun the original failing input and one nearby passing input.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** after the fix, rerun the original failing input and one nearby passing input.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add module-level logging with `logging.getLogger(__name__)` and emit useful DEBUG/INFO/WARNING events for a small processing function. **Constraints:** use lazy `%s`/`%d` formatting, do not call `basicConfig` inside reusable library logic, and log counts/identifiers rather than sensitive record contents. **Verify:** demonstrate that changing the configured level changes visibility without changing the returned value.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** demonstrate that changing the configured level changes visibility without changing the returned value.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Profile a deliberately slow membership or aggregation function with `cProfile` or `timeit`, implement one behavior-preserving improvement, and compare under identical inputs. **Expected behavior:** outputs match exactly and the measurement identifies where time changed. **Constraint:** report repeated timings rather than claiming from a single run. **Verify:** Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted. **Progressive hint:** The threshold keeps records at that level or more severe. **Verify:** Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption. **Progressive hint:** Read a traceback from the final exception upward through your code. **Verify:** Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the evidence-driven debugging, useful logs, and measurement before optimization model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging. **Progressive hint:** Put elapsed-time logging in `finally` so failures are still timed. **Verify:** Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers. **Progressive hint:** Configuration is process state; inspect handlers before adding one. **Verify:** Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification. **Progressive hint:** A faster wrong answer is not an optimization. **Verify:** Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from evidence-driven debugging, useful logs, and measurement before optimization.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A debugger is best for stepping through changing state; temporary prints can help a tiny example; logging is better for repeatable or production execution.

**Edge case:** Nondeterminism, first-run cache warm-up, logging duplicate handlers, swallowed exceptions, and unrepresentative benchmark data can mislead diagnosis.

**Solution evidence to inspect:** Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions.
<!-- END BEGINNER SOLUTION REVIEW -->

Line-by-line solutions that add logging to utilities and profile a slow function.

Contents
- Exercise 1: Add logging to CSV/JSON utilities
- Exercise 2: Profile and optimize a slow function

---

Exercise 1 — Add logging to utilities
We’ll instrument `safe_load_json` and the CSV/JSON converters (from Day 08) with the standard library `logging`.

```python
import logging
from pathlib import Path
import json, csv
from typing import Any

log = logging.getLogger(__name__)                  # 1) get a module-level logger


def safe_load_json(path: str | Path) -> Any | None:
    p = Path(path)
    log.info("loading JSON: %s", p)               # 2) info-level start message
    try:
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
            log.debug("loaded keys: %s", list(data)[:5])
            return data
    except FileNotFoundError:
        log.error("not found: %s", p)
    except PermissionError:
        log.error("permission denied: %s", p)
    except json.JSONDecodeError as e:
        log.error("invalid JSON %s (line %d col %d): %s", p, e.lineno, e.colno, e.msg)
    return None


def csv_to_json(csv_path: Path, json_path: Path) -> None:
    log.info("csv→json: %s → %s", csv_path, json_path)
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        log.info("rows read: %d", len(rows))
    with json_path.open("w", encoding="utf-8") as out:
        json.dump(rows, out, indent=2)
        log.info("wrote json: %s", json_path)


def json_to_csv(json_path: Path, csv_path: Path) -> None:
    log.info("json→csv: %s → %s", json_path, csv_path)
    data = safe_load_json(json_path)
    if not data:
        log.warning("no data; writing empty CSV: %s", csv_path)
        csv_path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({k for rec in data for k in rec})
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in data:
            w.writerow({k: rec.get(k, "") for k in fieldnames})
    log.info("wrote csv: %s (cols=%d)", csv_path, len(fieldnames))

# Configure logging in your app entry point (once):
# logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
```
Line-by-line highlights
- Use a module-level logger (getLogger(__name__)) so libraries can be configured by applications.
- INFO for high-level progress; DEBUG for noisy details; ERROR for failures.
- Prefer structured messages (`"%s"` placeholders) over f-strings in logging for lazy formatting.

---

Exercise 2 — Profile and optimize
Start with a slow Python loop and compare with NumPy vectorization.

```python
import timeit, numpy as np

# Baseline: Python loop (intentionally slow)
def scale_loop(xs: list[float], k: float) -> list[float]:
    out = []                               # 1) new list to hold results
    for x in xs:                           # 2) Python-level loop
        out.append(x * k)                  # 3) multiply and append
    return out

# Vectorized: ndarray operations

def scale_vec(xs: np.ndarray, k: float) -> np.ndarray:
    return xs * k                          # elementwise multiply in C

# Timing
arr = np.arange(1_000_00, dtype=float)     # 100k elements
lst = arr.tolist()

loop_t = timeit.timeit(lambda: scale_loop(lst, 2.0), number=10)
vec_t  = timeit.timeit(lambda: scale_vec(arr, 2.0), number=10)
print({"loop_sec": loop_t, "vec_sec": vec_t})
```
Explanation
- timeit runs the callable multiple times; compare totals.
- Expect significant speedup from vectorization due to C-level loops and contiguous memory.

Extra: Using `cProfile`
```python
import cProfile, pstats

with cProfile.Profile() as pr:
    _ = scale_loop(lst, 2.0)

pstats.Stats(pr).strip_dirs().sort_stats("cumtime").print_stats(10)
```
- cumtime shows where total time is spent; optimize those hot paths first.

---

## Expanded mastery lab solutions

Observe before optimizing: reproduce a defect, add bounded context, profile representative work, and change the measured bottleneck.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Logging and traceback reading

At `WARNING`, warning and error records are emitted. Start traceback diagnosis
at the deepest frame in code you control, then inspect the input and assumption
there before editing callers.

### Practices 3–5 — A timing tool and a fair benchmark

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
