# Day 11 — Solutions: Debugging, Logging, and Profiling

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Add useful logging to the CSV/JSON utilities from Day 8. **Hint:** log path, operation, row count, and expected failures; never log secrets or entire sensitive records.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Profile a deliberately slow function, identify its hot spot, then improve it. **Hint:** first improve the algorithm or data structure. If the work is numeric array processing, compare the measured loop with NumPy vectorization from the course's installed data dependencies.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted.

**Reasoning checkpoint:** The threshold keeps records at that level or more severe. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption.

**Reasoning checkpoint:** Read a traceback from the final exception upward through your code. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging.

**Reasoning checkpoint:** Put elapsed-time logging in `finally` so failures are still timed. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers.

**Reasoning checkpoint:** Configuration is process state; inspect handlers before adding one. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification.

**Reasoning checkpoint:** A faster wrong answer is not an optimization. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
