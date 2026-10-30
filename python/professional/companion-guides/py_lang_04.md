# Structured Asyncio, Cancellation, and Context Ownership

**Stable ID:** `python-lang-04`. Plan about three hours for reading, tracing, and
independent implementation. Historical day 88 is a stable catalog
label, not a study deadline.

## How to run this lesson

Run `./classroom` from the repository root and open **Python** in the shared
`/classroom` directory. Select this lesson, read its Python capability notice,
and use the saved coding pad. Windows uses the same launcher in WSL 2.
Docker provides Python and all required standard-library modules. Paste the
complete [learner script](../lessons/py_lang_04.py) into the pad, save, and Run.
The output pane shows two worked-example observations and a completion message.
The six task functions intentionally raise `NotImplementedError` until you
implement them; the opening examples do not call those functions.

The browser saves source, notes, and results in its learning volume, while
every Run starts a fresh Python process. Include imports, fixtures, and checks
in the submitted source. In-memory closures, iterators, tasks, and event loops
do not survive the run. Save the source that reproduces your evidence. Running
the demonstrations proves only those cases, not completion of the six tasks.
Every input here is an original, bounded local fixture; no download, server,
database, credentials, or additional package is needed.

### Optional prepared contributor route

After the separate [contributor setup](../../../CONTRIBUTING.md), run
`uv run --no-sync python python/professional/lessons/py_lang_04.py` from the
repository root. This host interpreter and checkout do not read the browser's
Docker learning volume. See the [classroom guide](../../../docs/classroom-experience.md)
for source, result history, and navigation. This optional command is not a
second installation requirement for ordinary learners.

## Level and prerequisites

- **Level:** Advanced Python language practice, using Python 3.11-compatible syntax.
- **Direct prerequisite:** `python-lang-03`, [companion guide](py_lang_03.md).
- **Direct prerequisite:** `python-pro-02`, [companion guide](py_pro_02_concurrency_parallelism.md).
- **Artifacts:** [learner](../lessons/py_lang_04.py), [explained answers](../solutions/py_lang_04_solutions.md), [executable reference](../solutions/py_lang_04_solution.py).

You should already recognize async/await and TaskGroup from the concurrency lab and explain generator resource ownership. This unit deepens cancellation, deadlines, grouped failures, and context restoration. It does not require network services or thread/process workers.

## Learning objectives

Use a structured task lifetime to return ordered results and propagate sibling
failure. Distinguish a bound on active calls from a bound on all scheduled
tasks. Place a deadline around cooperative local work, await cancellation
cleanup, inspect individual leaves of grouped failures, and restore task-local
request context under all exit paths. Produce event and context evidence
without starting servers or relying on remote timing.

## Vocabulary and concepts

- **Coroutine:** An asynchronous computation produced by calling an `async def`
  function. Creating it does not run its body. Await it or schedule it exactly
  under a deliberate owner; abandoning it can produce a warning.
- **Task:** An event-loop-managed execution of a coroutine. Tasks overlap when
  they reach await points; they do not make ordinary Python CPU calculations
  parallel. Blocking synchronous work can prevent all tasks from progressing.
- **Structured concurrency:** A lifetime rule in which a lexical scope owns
  its children and waits for them before leaving. `asyncio.TaskGroup` provides
  that scope and cancels siblings when an ordinary child failure occurs.
- **Cancellation:** A request to interrupt a task at a cooperative point.
  `task.cancel()` requests it; awaiting the task observes the completed exit.
  `CancelledError` is a control signal derived from `BaseException`, so an
  ordinary `except Exception` does not catch it.
- **Deadline:** A limit on how long an operation may remain in its scope.
  `asyncio.timeout` uses cancellation internally and translates its own timeout
  into `TimeoutError` outside the scope. It cannot forcibly interrupt a blocked
  event loop or terminate an external side effect.
- **Exception group:** An exception containing multiple exceptions, possibly
  nested in further groups. Its summary text is not a list of leaf failures.
  `except*` can handle matching subgroups; this lesson also traces leaves to
  make the classification and original message order explicit.
- **Context variable:** A value associated with the current execution context.
  A new task inherits a copy of its creator's current context. A token returned
  by `ContextVar.set` identifies the earlier binding for exact restoration.

The `async with asyncio.TaskGroup() as group` statement creates an owning
scope. `group.create_task(operation(value))` schedules a child in that scope.
The list of task objects preserves input positions even if their results
complete in another order. Read `task.result()` after successful group exit;
reading it too early can raise `InvalidStateError`. If a child fails, there
is no complete result tuple, and group exit raises after sibling cleanup.

A semaphore controls entry into a protected region. Put the actual operation
inside `async with gate`, and place its finish observation in `finally` inside
that region. Waiting for a semaphore is not active operation work. Creating one
task per item still stores all those tasks; this lesson deliberately uses
small finite tuples. For unknown or very large inputs, revisit the bounded
queue design in the concurrency prerequisite rather than assuming a semaphore
alone provides producer backpressure.

## Worked example / walkthrough

### Task completion does not choose presentation order

The following program uses yielding local operations. `sleep(0)` offers a
cooperative scheduling opportunity without simulating a service or asserting
an exact elapsed time. The enclosing synchronous entrypoint calls `asyncio.run`
once to own a fresh loop. The final tuple follows the stored task list.

```python
import asyncio


async def ordered_demo():
    async def calculate(value):
        await asyncio.sleep(0)
        return value * 10

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(calculate(value)) for value in (3, 1)]
    result = tuple(task.result() for task in tasks)
    assert result == (30, 10)
    return result


print("Input-order results:", asyncio.run(ordered_demo()))
```

**Expected:** The tuple is `(30, 10)`. It is tied to input order `(3, 1)`, not
numerical sort order or a claim about which task finished first. An empty task
list would produce an empty tuple. A real failure needs separate evidence;
this successful demonstration alone says nothing about sibling cancellation.

### A cancellation request is followed by an awaited exit

The worker signals readiness after its acquisition event, before waiting on
an Event that this example never releases. The controller waits for that
signal, asks the task to cancel, then awaits the task. This order proves the
worker had entered its cleanup region. Guessing with a short sleep could race
with startup on a busy machine and make a missing cleanup look intermittent.

```python
import asyncio


async def cancellation_demo():
    ready = asyncio.Event()
    never = asyncio.Event()
    events = []

    async def worker():
        events.append("open")
        try:
            ready.set()
            await never.wait()
        finally:
            events.append("close")

    task = asyncio.create_task(worker())
    await ready.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("Cancellation was swallowed")
    assert task.cancelled()
    assert events == ["open", "close"]
    return events


print("Awaited cancellation:", asyncio.run(cancellation_demo()))
```

**Expected:** The task is cancelled and the log is `['open', 'close']` before
the controller returns. The controller catches the expected control signal
only at the ownership boundary. The worker's `finally` records cleanup and
allows cancellation to continue. Replacing the worker's cancellation with a
success value would change what the controller can observe.

If a timeout expires, inspect `TimeoutError` outside the timeout context.
Inside the operation, cleanup still runs through cancellation. If the caller
cancels before the deadline, preserve `CancelledError` instead of relabeling
it as a timeout. These are distinct causes, even though both can traverse a
`finally` block. Keep ordinary operation failures such as `ValueError` distinct
as well; a deadline wrapper should not hide malformed local data.

## Exercises

Use local Events and tiny arithmetic operations. Bound each independent test
with an outer timeout during debugging so a broken readiness protocol cannot
wait forever. The learner function's cancellation contract is still evaluated
by its exact exception and cleanup events, not by a guessed runtime duration.

### Exercise 1: Return ordered structured results

**Inputs:** A small finite tuple of integer values and an asynchronous operation for each value.

**Expected:** Create one child per value inside asyncio.TaskGroup, await group exit, and return results in input order regardless of completion order. Empty input returns (). A child Exception must propagate as an ExceptionGroup after sibling cleanup; do not return partial success or leave child tasks running.

**Verify:** Operations deliberately released in reverse order for (1, 2, 3) still return (10, 20, 30). An injected child failure cancels a waiting sibling and its finally block runs before the group exits.

### Exercise 2: Limit active work with cleanup

**Inputs:** A small finite tuple, an async operation, an exact positive integer limit, and an event list.

**Expected:** Use a TaskGroup plus a Semaphore so at most limit operation calls are active. Record ("start", value) after acquisition and ("finish", value) in finally before releasing the slot. Preserve input result order and propagate group failure/caller cancellation after cleanup. Reject invalid limits with ValueError even for empty input. This bounds active calls, not the number of scheduled tasks.

**Verify:** Six yielding operations with limit 2 return their six squares. Walk the event transcript to prove active work never exceeds 2 and ends at zero. Under failure every recorded start has a matching finish.

### Exercise 3: Put a deadline around owned work

**Inputs:** A factory for one awaitable and a finite strictly positive int or float deadline in seconds, excluding bool.

**Expected:** Validate the deadline before calling the factory. Use asyncio.timeout to return success or raise TimeoutError after timed-out work has finished its finally cleanup. A cancellation from the caller remains asyncio.CancelledError; an operation ValueError remains ValueError. Do not manufacture fallback values.

**Verify:** An immediately completing operation returns 7. A blocked local Event wait times out and records closed before TimeoutError is observed. Reject zero, negative, True, infinity, and NaN without calling the factory.

### Exercise 4: Make cancellation cleanup observable

**Inputs:** Two Events in the running loop and an observation list. The ready signal lets a controller know acquisition has happened.

**Expected:** Append acquired, set ready, then await release and return released. Append closed in finally on success or cancellation; allow CancelledError to propagate. The controller owns the created task and must await it after cancelling. Do not use sleeps to guess whether acquisition occurred.

**Verify:** Wait for ready, cancel the task, await it, and require CancelledError with events ["acquired", "closed"]. With release already set, the result is released and the same balanced event list appears.

### Exercise 5: Inspect every grouped failure

**Inputs:** An ExceptionGroup, possibly containing nested ExceptionGroups and ValueError subclasses alongside other ordinary Exceptions.

**Expected:** Return (value_error_messages, other_messages), traversing leaves depth first in their original order within each category. Classify using isinstance(error, ValueError); preserve each leaf message, including duplicates. Do not flatten by stringifying group summary text or classify BaseException control signals as ordinary failures.

**Verify:** A nested group containing ValueError("bad"), RuntimeError("disk"), and ValueError("bad") gives (("bad", "bad"), ("disk",)). An all-other group gives an empty first tuple.

### Exercise 6: Restore task-local request context

**Inputs:** A nonempty string request label and an async operation. Use the module ContextVar REQUEST_ID with default outside.

**Expected:** Set REQUEST_ID for the operation, return its result, and reset the exact token in finally on success, ordinary failure, or caller cancellation. Child tasks inherit a copy of the current context. Concurrent requests must not overwrite each other; invalid labels raise ValueError before invoking the operation.

**Verify:** Concurrent request labels north and south each remain visible across an await and in their own child task. The calling context is outside afterward. Repeat with an injected ValueError and cancellation and inspect restoration in the same task.

## Self-check

Explain why requesting cancellation is insufficient evidence of resource
closure. State which scope waits for sibling cleanup after a child fails and
why reading partial results would be a different contract. Distinguish two
active operations from two scheduled tasks. Describe why catching `Exception`
does not catch cancellation, and why swallowing cancellation can interfere
with structured task scopes.

**Verify:** Retain ordered output `(10, 20, 30)`, an event walk whose active
count remains between zero and two, a timeout whose cleanup marker is present,
and a cancelled task whose final events are `['acquired', 'closed']`. Preserve
the individual grouped failure messages, including duplicates. Show two
request labels across an await and in child tasks, then show `outside` restored
in the same calling context after success, failure, and cancellation.

## Common pitfalls

If a task result is unavailable, inspect whether group exit has completed.
If tasks keep running after a failure, look for an unowned `create_task` outside
the TaskGroup. If cancellation closes nothing, check that readiness was
signalled inside the acquired region and that the controller actually awaited
the cancelled task. A log immediately after `cancel()` can be too early.

If active work exceeds the limit, inspect whether the awaited operation is
inside the semaphore context. If a failure leaves the active count positive,
move the finish event into `finally`. If a deadline never triggers, look for
blocking code with no cooperative await point. This lesson cannot make such
code interruptible by merely changing its annotation to `async`.

If grouped failures appear as only `outer (3 sub-exceptions)`, the program is
printing a summary rather than visiting leaves. Preserve duplicate messages
because two failures can have the same text. If concurrent request labels
leak, inspect for a shared module string instead of a ContextVar. If the label
leaks only after an exception, token reset is probably outside `finally`.
Resetting to a hardcoded default also breaks nested scopes that had a
nondefault previous label.

## Next step

Return to [`python-pro-02`: Concurrency and parallelism decision lab](py_pro_02_concurrency_parallelism.md)
and compare this task-per-item fixture with its bounded producer/consumer queue.
Then use [measurement and optimization](py_perf_01_measurement_optimization.md)
to ask which model suits an observed workload. These local tests establish
Python lifetime semantics for small fixtures. They do not establish service
throughput, external cancellation, thread safety, or production reliability.
Before moving on, explain how the same request could time out, be cancelled,
or fail validation, and identify the different evidence each route requires.


## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-lang-04: Structured Asyncio, Cancellation, and Context Ownership.
Read python/professional/companion-guides/py_lang_04.md and python/professional/lessons/py_lang_04.py. Direct prerequisites: python-lang-03, python-pro-02.
Keep the advanced lesson self-contained for someone new to its specific mechanisms. Explain asyncio, taskgroup, cancellation, timeout, exceptiongroup, contextvars, ask me to predict a concrete result, then let me attempt it. Give one hint at a time and review my exact value, exception, event, and cleanup evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request comparison or have made an honest attempt.
Use only prepared local offline fixtures in the Docker Python classroom; preserve saved source and notes. No SQL or external service is involved. Done when all six contracts and boundary cases have inspected evidence, and I can explain the timing and ownership decision behind each result.
```
