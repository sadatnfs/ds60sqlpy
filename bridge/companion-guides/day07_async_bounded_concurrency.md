# Bridge Day 7 — Async I/O and bounded concurrency

**Level:** Advanced  
**Prerequisite:** [Bridge Day 6](day06_bulk_etl_validation.md)

## Why this matters

`asyncio` can overlap waiting, but it does not make database capacity infinite.
Starting one task per input without a bound can exhaust a connection pool,
increase latency, and overwhelm PostgreSQL. Structured concurrency, explicit
limits, and async-aware resource cleanup make failure and cancellation
predictable.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day07_async_bounded_concurrency.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day07_async_bounded_concurrency.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day07_async_bounded_concurrency.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Objectives

By the end, you can:

- distinguish I/O concurrency from CPU parallelism;
- manage async commit, rollback, and close paths;
- limit in-flight work with a semaphore;
- preserve result order independently of completion order;
- execute a parameterized Psycopg async query;
- test concurrency deterministically without network access.

## Vocabulary

| Term | Meaning |
|---|---|
| event loop | The scheduler that resumes coroutines when awaited work is ready |
| coroutine | A function execution that can suspend with `await` |
| task | A scheduled coroutine |
| bounded concurrency | A fixed maximum number of operations in flight |
| semaphore | A counter-based synchronization primitive that enforces a limit |
| structured concurrency | Child tasks are owned and awaited within a lexical scope |
| cancellation | A request for a running coroutine to stop and clean up |


## Worked example: concurrency needs a measurable limit

```python
semaphore = asyncio.Semaphore(limit)


async def guarded(item: str) -> Result:
    async with semaphore:
        return await operation(item)
```

The semaphore caps operations inside its context. `asyncio.TaskGroup` owns the
tasks: it waits for all on success and cancels siblings when one fails.

Do not put `time.sleep()`, synchronous HTTP, or a synchronous Psycopg call inside
an async function. Those block the event loop. Use an async API or deliberately
move blocking work to a thread when the library is thread-safe.


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: concurrency is owned, bounded waiting

Async code helps when tasks spend time waiting for I/O. It does not make CPU
work faster, create database capacity, or remove transaction ownership. The
parent scope must still know which tasks exist, how many may enter the scarce
operation, what happens on failure, and when cleanup is complete.

`TaskGroup` provides structured ownership: children cannot silently outlive the
group. A semaphore bounds the number currently inside an operation. These are
related but different controls. Creating one task per million inputs and
placing a semaphore inside each task still creates a million task objects; a
fixed worker queue is the bounded design at that scale.

You can test active concurrency without a wall-clock assertion:

```python
import asyncio


async def demo() -> int:
    semaphore = asyncio.Semaphore(2)
    active = 0
    peak = 0

    async def one() -> None:
        nonlocal active, peak
        async with semaphore:
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0)
            active -= 1

    async with asyncio.TaskGroup() as group:
        for _ in range(5):
            group.create_task(one())
    return peak


assert asyncio.run(demo()) == 2
```

Preserving input order is also an explicit policy. Store each result by input
index rather than appending in completion order. If low-latency streaming needs
completion order, return a different abstraction and document it.

Cancellation is a failure path. An async connection manager should await
rollback and close before cancellation crosses the ownership boundary. When
several children fail, Python may report an `ExceptionGroup`; do not catch a
broad exception merely to make the group disappear. Database concurrency must
respect pool and server limits, and concurrent operations should not share a
cursor or transaction unless the driver and application design explicitly
support that ownership.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

## Exercises

### Practice contract

- **Focus:** Own async connection cleanup, bound active work with structured concurrency, preserve input order, and keep PostgreSQL value binding safe.
- **Assumptions:** Cancellation must propagate after cleanup; `asyncio.Semaphore` bounds active operations but not the number of created tasks.
- **Primary failure mode:** Blocking calls, shared unsafe cursors, swallowed cancellation, and unbounded task creation turn async code into a reliability hazard.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Implementation:** Implement `managed_async_connection()` with awaited factory, one yield,
   commit on success, rollback on failure, and close on every path.
   - **Progressive hint:** Mirror the synchronous state machine with awaited lifecycle calls.
   - **Verify:** Assert async success events are `acquire, body, commit, close`; failure events are `acquire, body, rollback, close`; all lifecycle calls are awaited and the body error escapes.
2. **Concurrency:** Implement `map_bounded()` with `asyncio.Semaphore` and `TaskGroup`, reject
   limits below one, and preserve input order.
   - **Progressive hint:** Associate each task with its original index rather than
     append-on-completion order.
   - **Verify:** Assert limits below one raise `ValueError`; with limit two, peak active operations is at most two and returned results remain in input order.
3. **Testing:** Measure active fake operations and assert maximum concurrency never exceeds the
   configured limit.
   - **Progressive hint:** Increment before an await point and decrement in `finally`.
   - **Verify:** Use an active-counter fake guarded by `try/finally`; for limits one, two, and four, assert the recorded peak never exceeds the requested limit and returns to zero.
4. **Ordering:** Use different fake completion delays to prove output order follows input order
   rather than completion order.
   - **Progressive hint:** Choose a completion schedule that visibly differs from the input.
   - **Verify:** Give later inputs shorter completion waits; assert completion log differs from input order while the returned list still matches input order.
5. **Async SQL:** Define `AsyncReadCursor` and implement one query using `customer_id = ANY(%s)`
   with the Python ID list as one bound parameter.
   - **Progressive hint:** The parameter sequence is a one-element tuple containing the list.
   - **Verify:** Inspect one awaited cursor call: SQL contains `customer_id = ANY(%s)`, parameters equal `([id1, id2],)`, and fetched rows map to the expected ID-to-name dictionary.
6. **Validation:** Return early for empty customer IDs without touching the cursor and reject
   any non-positive ID.
   - **Progressive hint:** Validate the complete collection before the first database effect.
   - **Verify:** Assert an empty ID sequence returns `{}` with zero cursor calls and any zero/negative ID raises `ValueError` before execute.
7. **Scale design:** Explain why a semaphore still creates one task per item and design a
   fixed-worker queue for a million inputs.
   - **Progressive hint:** Separate active-operation bounds from task-count and memory bounds.
   - **Verify:** For one million inputs, calculate one-million-task semaphore memory versus a fixed worker count; diagram producer, bounded queue, workers, sentinel shutdown, and result policy.
8. **Cancellation:** Cancel a task inside `managed_async_connection()` and verify rollback/close
   happen before cancellation escapes.
   - **Progressive hint:** Never translate `CancelledError` into an empty or successful result.
   - **Verify:** Cancel inside the managed body; assert awaited rollback and close finish before `CancelledError` reaches the parent.
9. **Failure analysis:** Trigger two concurrent task failures and inspect `ExceptionGroup`
   behavior from `TaskGroup`.
   - **Progressive hint:** Structured concurrency cancels siblings and reports grouped failures.
   - **Verify:** Synchronize two child failures, catch the resulting `ExceptionGroup`, and assert both configured exception types are inspectable after sibling cancellation cleanup.
10. **Empty work:** Test `map_bounded([], operation, limit=1)` and prove the operation is never
   called.
   - **Progressive hint:** An empty collection is a successful no-op, not an invalid concurrency
     request.
   - **Verify:** Call `map_bounded([], operation, limit=1)`; assert result `[]` and operation call count zero.
11. **Duplicates:** Define whether duplicate customer IDs are preserved, deduplicated, or
   rejected and test the chosen contract.
   - **Progressive hint:** Input-order promises and dictionary outputs have different duplicate
     semantics.
   - **Verify:** Document one duplicate-ID policy and test `[2, 2, 3]` against it, including exact query parameters and returned keys/order.
12. **Architecture:** Compare a semaphore-per-item design with the worker queue on fairness,
   memory, cancellation, and complexity.
   - **Progressive hint:** Choose based on workload scale rather than treating one pattern as
     universally superior.
   - **Verify:** Provide a comparison table with task count, peak memory, fairness, cancellation path, ordering policy, and implementation complexity for semaphore and worker-queue designs.
13. **Database ownership:** Decide whether concurrent operations may share one connection/cursor
   or require a pool-acquired resource per worker.
   - **Progressive hint:** Driver concurrency guarantees and transaction scope determine the
     safe choice.
   - **Verify:** Record resource IDs under concurrent work; assert each worker owns a pool-acquired connection/cursor and no unsafe cursor is entered concurrently.
14. **Deterministic testing:** Replace timing-based async assertions with events/barriers and
   explain why wall-clock sleeps make tests flaky.
   - **Progressive hint:** Coordinate state transitions directly instead of hoping a scheduler
     runs in time.
   - **Verify:** Coordinate workers with `Event`/barrier objects, assert peak and order from recorded state, and remove pass/fail dependence on elapsed wall-clock sleep duration.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


## Optional live-DB step

Psycopg 3 provides `AsyncConnection.connect()`. Use one disposable connection
and a read-only cursor:

```python
connection = await psycopg.AsyncConnection.connect(database_url)
try:
    async with connection.cursor() as cursor:
        names = await fetch_customer_names(cursor, [1, 2, 3])
finally:
    await connection.rollback()
    await connection.close()
```

Set `DS60_DATABASE_URL` in the shell, but never print it:

```powershell
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
```

```bash
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
```

For concurrent queries, pool size and semaphore limit must agree. A concurrency
limit of 50 does not help if a pool of 5 causes 45 tasks to wait while still
holding other resources.

## Self-check

- Is the maximum active fake count never above the configured limit?
- Are results returned in input order?
- Does one child failure propagate and cancel unfinished siblings?
- Are rollback and close awaited on failure?
- Does empty ID input avoid a database round trip?

## Common pitfalls

- **Calling `asyncio.run()` inside a running event loop:** notebooks and async
  frameworks already own the loop; `await` the coroutine there.
- **Using blocking calls in coroutines:** one call stalls every task.
- **Unlimited `gather()`:** task creation itself can consume large memory.
- **Sharing one connection across concurrent transactions:** transaction state
  and cursor use can interfere.
- **Swallowing cancellation:** resources may remain open and shutdown hangs.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-06`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-07: Async Bounded Concurrency.
Direct catalog prerequisites: bridge-06. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day07_async_bounded_concurrency.md
Learner artifact: bridge/lessons/day07_async_bounded_concurrency.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

[Day 8](day08_production_capstone.md) assembles configuration, adapters,
idempotency, tests, batches, and observability into a restartable job. See
[the Day 7 solution notes](../solutions/day07_solutions.md) after attempting the
exercises.
