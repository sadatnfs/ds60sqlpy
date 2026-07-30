# Bridge Day 7 — Solution notes

Start with the [learner file](../lessons/day07_async_bounded_concurrency.py).
Then inspect [day07_solution.py](day07_solution.py).

## Structured, bounded work

`map_bounded()` creates one task per input inside a `TaskGroup`, but each task
must acquire a semaphore before calling the operation. Results are stored by
input index and reconstructed in order. Completion order therefore cannot
change the returned order.

`TaskGroup` gives failure ownership: one child failure cancels unfinished
siblings, waits for cleanup, and reports the failure to the parent scope.

`managed_async_connection()` mirrors Day 2 but awaits transaction and cleanup
methods. Cancellation is a failure path, so it rolls back and still closes.

## Async query

`fetch_customer_names()` validates IDs, avoids an empty round trip, and binds a
list as one parameter to PostgreSQL `ANY(%s)`. The tuple's trailing comma is
significant.

## Tradeoffs

- A semaphore bounds active operations but still creates one task per input.
  For millions of items, use a bounded queue and a fixed worker set.
- Preserving input order requires retaining indexed results. A streaming caller
  may prefer completion order to reduce latency and memory.
- One failed task cancels the group. Some bulk workloads instead collect
  per-item failures, but that must be an explicit result type—not suppressed
  exceptions.
- Async improves overlap for I/O waits; it does not speed CPU-heavy transforms.
- Connection-pool capacity should usually be the same as or lower than the
  database concurrency limit. More tasks do not create more database capacity.

Tests measure maximum active operations and resource events with
`asyncio.run()`, fakes, and `asyncio.sleep(0)`. They require neither a network
nor an async test plugin.

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day07_solution.py`; use it only after an honest attempt.

**Shared failure rule:** Blocking calls, shared unsafe cursors, swallowed cancellation, and unbounded task creation turn async code into a reliability hazard.

### Exercise 1 — Implementation

**Prompt:** Implement `managed_async_connection()` with awaited factory, one yield, commit on
success, rollback on failure, and close on every path.

**Approach:** Await acquisition, yield inside `try`, await commit after normal return, await
rollback on failure, re-raise, and await close in `finally`.

**Why this boundary matters:** Mirror the synchronous state machine with awaited lifecycle
calls.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 2 — Concurrency

**Prompt:** Implement `map_bounded()` with `asyncio.Semaphore` and `TaskGroup`, reject limits
below one, and preserve input order.

**Approach:** Preallocate indexed result slots, have each task acquire the semaphore before
calling the operation, store at its index, and rebuild the typed list after the `TaskGroup`
exits.

**Why this boundary matters:** Associate each task with its original index rather than
append-on-completion order.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 3 — Testing

**Prompt:** Measure active fake operations and assert maximum concurrency never exceeds the
configured limit.

**Approach:** Use an in-memory counter and `await asyncio.sleep(0)` only as a deterministic
scheduling yield. Assert the measured maximum is at most the limit and all counters return to
zero.

**Why this boundary matters:** Increment before an await point and decrement in `finally`.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 4 — Ordering

**Prompt:** Use different fake completion delays to prove output order follows input order
rather than completion order.

**Approach:** Return values after controlled events/delays, then assert the final list maps
one-for-one to the original sequence. Indexed storage makes scheduling irrelevant.

**Why this boundary matters:** Choose a completion schedule that visibly differs from the input.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 5 — Async SQL

**Prompt:** Define `AsyncReadCursor` and implement one query using `customer_id = ANY(%s)` with
the Python ID list as one bound parameter.

**Approach:** Await one static query with `(list(customer_ids),)`, await `fetchall`, convert
rows to an ID/name mapping, and never interpolate IDs into SQL.

**Why this boundary matters:** The parameter sequence is a one-element tuple containing the
list.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 6 — Validation

**Prompt:** Return early for empty customer IDs without touching the cursor and reject any
non-positive ID.

**Approach:** An empty sequence returns `{}` and leaves the recording cursor untouched. Scan all
IDs first and raise before execute if any value is non-positive.

**Why this boundary matters:** Validate the complete collection before the first database
effect.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 7 — Scale design

**Prompt:** Explain why a semaphore still creates one task per item and design a fixed-worker
queue for a million inputs.

**Approach:** Create a bounded `asyncio.Queue`, start exactly N workers, feed indexed items with
backpressure, collect indexed results, then send sentinels and join workers. This bounds both
active work and task creation.

**Why this boundary matters:** Separate active-operation bounds from task-count and memory
bounds.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 8 — Cancellation

**Prompt:** Cancel a task inside `managed_async_connection()` and verify rollback/close happen
before cancellation escapes.

**Approach:** Use events to pause inside the body, cancel it, and assert lifecycle ordering.
Cleanup completes (subject to shielding policy), then the original cancellation propagates.

**Why this boundary matters:** Never translate `CancelledError` into an empty or successful
result.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 9 — Failure analysis

**Prompt:** Trigger two concurrent task failures and inspect `ExceptionGroup` behavior from
`TaskGroup`.

**Approach:** Catch only in the test with `except*` to inspect expected types; production code
should not flatten multiple failures into one misleading success or discard cancellation
context.

**Why this boundary matters:** Structured concurrency cancels siblings and reports grouped
failures.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 10 — Empty work

**Prompt:** Test `map_bounded([], operation, limit=1)` and prove the operation is never called.

**Approach:** Return `[]` after validating the positive limit; a spy operation should have zero
calls and no event loop resources should leak.

**Why this boundary matters:** An empty collection is a successful no-op, not an invalid
concurrency request.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 11 — Duplicates

**Prompt:** Define whether duplicate customer IDs are preserved, deduplicated, or rejected and
test the chosen contract.

**Approach:** `map_bounded` preserves duplicate inputs and outputs. For `fetch_customer_names`,
validate/deduplicate IDs before the query if desired and document that the returned dictionary
naturally has one value per ID.

**Why this boundary matters:** Input-order promises and dictionary outputs have different
duplicate semantics.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 12 — Architecture

**Prompt:** Compare a semaphore-per-item design with the worker queue on fairness, memory,
cancellation, and complexity.

**Approach:** Semaphore tasks are concise for bounded small inputs; workers bound task count and
provide queue backpressure for large streams. Both require cancellation-safe cleanup and indexed
results for ordering.

**Why this boundary matters:** Choose based on workload scale rather than treating one pattern
as universally superior.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 13 — Database ownership

**Prompt:** Decide whether concurrent operations may share one connection/cursor or require a
pool-acquired resource per worker.

**Approach:** Do not share a cursor concurrently. Prefer a bounded pool resource per worker or
serialize statements on one connection when they belong to one transaction; keep pool size
aligned with the concurrency limit.

**Why this boundary matters:** Driver concurrency guarantees and transaction scope determine the
safe choice.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 14 — Deterministic testing

**Prompt:** Replace timing-based async assertions with events/barriers and explain why
wall-clock sleeps make tests flaky.

**Approach:** Use `asyncio.Event` objects to hold and release operations at known points,
inspect active counts while blocked, and avoid thresholds tied to machine speed.

**Why this boundary matters:** Coordinate state transitions directly instead of hoping a
scheduler runs in time.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.
