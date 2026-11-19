# Day 11 Solutions: Debugging, Logging, and Profiling

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

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Start from a supplied failing function and use `breakpoint()` or the VS Code debugger to pause immediately before the wrong value is produced. **Evidence:** record the call arguments, two relevant local variables, and the branch taken. **Constraint:** do not change logic until you can state one falsifiable hypothesis. **Verify:** record the original failing test result before repair, then assert that exact input and one nearby passing input both produce their expected values after the fix.

**Reasoning:** The symptom is a wrong average, so the useful pause point is the line that produces it: the return statement. At that pause, `values`, `positives`, `sum(positives)`, and the denominator are all visible, and the hypothesis can be stated before any edit: the denominator counts every value, but the numerator counts only positives. Recording the failing result (`10.0` instead of `15.0`) before the fix gives you evidence to compare with afterwards. Editing first and checking later is the common mistake; it can make the symptom disappear without proving which assumption was wrong.

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

### Exercise 2: worked answer

**Learner contract:** Add module-level logging with `logging.getLogger(__name__)` and emit useful DEBUG/INFO/WARNING events for a small processing function. **Constraints:** use lazy `%s`/`%d` formatting, do not call `basicConfig` inside reusable library logic, and log counts/identifiers rather than sensitive record contents. **Verify:** demonstrate that changing the configured level changes visibility without changing the returned value.

**Reasoning:** `logging.getLogger(__name__)` gives each module its own named logger, so an application can turn one module's messages up or down without touching the rest. The `%s` and `%d` arguments are formatted only when a handler actually emits the record, which keeps disabled DEBUG calls cheap. Library code never calls `basicConfig`, because handler and level choices belong to the application that runs it. The messages record a file's basename and a line count, never the file contents, which keeps sensitive data out of logs.

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

### Exercise 3: worked answer

**Learner contract:** Profile a deliberately slow membership or aggregation function with `cProfile` or `timeit`, implement one behavior-preserving improvement, and compare under identical inputs. **Expected behavior:** outputs match exactly and the measurement identifies where time changed. **Constraint:** report repeated timings rather than claiming from a single run. **Verify:** Assert old and new functions return identical results, then report repeated measurements and the profiler line/call count supporting the change.

**Reasoning:** Profiling starts by fixing the inputs and proving that the old and new versions return the same answer; a faster wrong answer is not an improvement. The list version compares each query with up to 1,000 values, while the set version builds a hash table once and then answers each query in roughly constant time. Repeating each measurement five times shows the run-to-run spread, whereas asserting a specific duration would fail on a slower computer. `cProfile` adds call-level detail when you need to know which function the time is spent in.

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

list_trials = repeat(lambda: contains_with_list(values, queries), repeat=5, number=100)
set_trials = repeat(lambda: contains_with_set(values, queries), repeat=5, number=100)
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

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** With a logger set to `WARNING`, predict which of DEBUG, INFO, WARNING, and ERROR calls are emitted. **Progressive hint:** The threshold keeps records at that level or more severe. **Verify:** Capture emitted records and assert WARNING and ERROR appear while DEBUG and INFO do not at a WARNING threshold.

**Reasoning:** A logger's level is a threshold: records at that level or more severe pass, and less severe records are dropped before any handler sees them. At `WARNING`, the `debug` and `info` calls produce nothing, while `warning` and `error` are emitted. The shared implementation for Exercises 4-5 captures the emitted level names with a small handler and asserts `['WARNING', 'ERROR']`. Seeing no INFO output is therefore not a problem with the message; check the logger's level and its handlers' levels first.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace a nested call failure and identify the first frame you own, the input value, and the violated assumption. **Progressive hint:** Read a traceback from the final exception upward through your code. **Verify:** Annotate the traceback with failure type, first owned frame, input, and violated assumption; rerun the minimal fixture to reproduce it exactly.

**Reasoning:** Read a traceback from the bottom: the last line names the exception, and the frames above it lead back to the call that started the work. The first frame you own, counting from the bottom, is where to look for the violated assumption; library frames below it usually only report the symptom. In the shared implementation for Exercises 4-5, the deepest frame is `parse_ratio`, the input is `'3/0'`, and the violated assumption is a nonzero denominator. Keeping that one input as a fixture lets you reproduce the failure exactly after any change.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Implement a reusable `timed(label)` context manager using `time.perf_counter` and logging. **Progressive hint:** Put elapsed-time logging in `finally` so failures are still timed. **Verify:** Capture one success and one raised block; assert both log a non-negative elapsed duration and the original exception is not swallowed.

**Reasoning:** A context manager runs its setup before the `with` body and its `finally` block after the body, whatever happens. Putting the timing and logging in `finally` therefore records failing blocks too, and because `finally` neither returns nor catches, the original exception still reaches the caller. `perf_counter` is the right clock: it is monotonic and high resolution, while `time.time` can jump when the system clock changes. The shared implementation for Exercises 6-8 checks the success and the failure path with a capturing handler.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Explain why repeated `logging.basicConfig(...)` calls in notebooks may appear ineffective and configure a named logger without duplicate handlers. **Progressive hint:** Configuration is process state; inspect handlers before adding one. **Verify:** Run configuration twice and assert the named logger has exactly one intended handler and emits one copy of each message.

**Reasoning:** Logging configuration is process-wide state. In a notebook, the kernel or an earlier cell may already have attached a handler to the root logger, and `basicConfig` does nothing when the root logger already has handlers, so a second call appears ineffective. Calling `addHandler` again instead attaches a duplicate, and every message prints twice. The repair configures a named logger and adds a handler only when none is present, which the shared implementation for Exercises 6-8 checks by configuring twice and asserting one handler. `basicConfig(force=True)` is the explicit way to replace root handlers when that is truly intended.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Design a fair comparison between a loop and an alternative: include warm-up, equal inputs, repeated trials, and result verification. **Progressive hint:** A faster wrong answer is not an optimization. **Verify:** Assert both implementations return identical values across all benchmark inputs, then report warm-up and multiple comparable trial distributions.

**Reasoning:** A fair comparison gives both versions the same input, checks that they return the same value, runs each several times, and reports the distribution rather than one number. The first run of each version can also pay one-time costs, so repeated trials show whether a difference is stable. Logging and printing stay outside the timed region because they would dominate a microsecond measurement. In the shared implementation for Exercises 6-8, the equality assertion comes before the timing, and `repeat` produces five samples for each version.

## Expanded mastery lab solutions

Observe before optimizing: reproduce a defect, add bounded context, profile representative work, and change the measured bottleneck.

### Shared implementation for Exercises 4-5: Logging and traceback reading

At `WARNING`, warning and error records are emitted. Start traceback diagnosis
at the deepest frame in code you control, then inspect the input and assumption
there before editing callers.

```python
import logging
import traceback

emitted: list[str] = []


class LevelRecorder(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        emitted.append(record.levelname)


demo = logging.getLogger("ds60.day11.levels")
demo.setLevel(logging.WARNING)
demo.propagate = False
demo.handlers.clear()
demo.addHandler(LevelRecorder())
demo.debug("debug detail")
demo.info("progress")
demo.warning("suspicious input")
demo.error("failed record")
assert emitted == ["WARNING", "ERROR"]


def parse_ratio(text: str) -> float:
    numerator, denominator = text.split("/")
    return int(numerator) / int(denominator)


def summarize(texts: list[str]) -> list[float]:
    return [parse_ratio(text) for text in texts]


try:
    summarize(["1/2", "3/0"])
except ZeroDivisionError as error:
    deepest = traceback.extract_tb(error.__traceback__)[-1]
    print(type(error).__name__, error, "in", deepest.name)
    assert deepest.name == "parse_ratio"
```

### Shared implementation for Exercises 6-8: A timing tool and a fair benchmark

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


class Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


capture = Capture()
logger.addHandler(capture)
try:
    with timed("failing block"):
        raise RuntimeError("boom")
except RuntimeError:
    pass  # the original exception was not swallowed by timed()
logger.removeHandler(capture)
assert capture.messages[0].startswith("failing block completed in")


def configure(name: str) -> logging.Logger:
    configured = logging.getLogger(name)
    if not configured.handlers:
        configured.addHandler(logging.StreamHandler())
    return configured


configure("ds60.day11.app")
configure("ds60.day11.app")
assert len(logging.getLogger("ds60.day11.app").handlers) == 1

from timeit import repeat

loop_trials = repeat(lambda: loop_sum(values), repeat=5, number=200)
built_in_trials = repeat(lambda: sum(values), repeat=5, number=200)
print("loop best:", min(loop_trials), "built-in best:", min(built_in_trials))
```

For a real benchmark, reuse equivalent input, warm both paths, run multiple
trials, report a distribution, and keep logging/I/O outside the timed region.
