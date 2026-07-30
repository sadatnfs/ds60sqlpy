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

1. Add useful logging to the CSV/JSON utilities from Day 8. **Hint:** log path,
   operation, row count, and expected failures; never log secrets or entire
   sensitive records.
2. Profile a deliberately slow function, identify its hot spot, then improve
   it. **Hint:** first improve the algorithm or data structure. If the work is
   numeric array processing, compare the measured loop with NumPy vectorization
   from the course's installed data dependencies.

### Additional mastery practice

Observe before optimizing: reproduce a defect, add bounded context, profile representative work, and change the measured bottleneck.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted.
   **Progressive hint:** The threshold keeps records at that level or more severe.
4. **Tracing:** Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption.
   **Progressive hint:** Read a traceback from the final exception upward through your code.
5. **Implementation:** Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging.
   **Progressive hint:** Put elapsed-time logging in `finally` so failures are still timed.
6. **Debugging:** Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers.
   **Progressive hint:** Configuration is process state; inspect handlers before adding one.
7. **Edge case and explanation:** Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification.
   **Progressive hint:** A faster wrong answer is not an optimization.

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
