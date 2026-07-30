# Bridge Day 7 — Async I/O and bounded concurrency

**Level:** Advanced  
**Prerequisite:** [Bridge Day 6](day06_bulk_etl_validation.md)

## Why this matters

`asyncio` can overlap waiting, but it does not make database capacity infinite.
Starting one task per input without a bound can exhaust a connection pool,
increase latency, and overwhelm PostgreSQL. Structured concurrency, explicit
limits, and async-aware resource cleanup make failure and cancellation
predictable.

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

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day07_async_bounded_concurrency.py
```

```bash
.venv/bin/python bridge/lessons/day07_async_bounded_concurrency.py
```

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
2. **Concurrency:** Implement `map_bounded()` with `asyncio.Semaphore` and `TaskGroup`, reject
   limits below one, and preserve input order.
   - **Progressive hint:** Associate each task with its original index rather than
     append-on-completion order.
3. **Testing:** Measure active fake operations and assert maximum concurrency never exceeds the
   configured limit.
   - **Progressive hint:** Increment before an await point and decrement in `finally`.
4. **Ordering:** Use different fake completion delays to prove output order follows input order
   rather than completion order.
   - **Progressive hint:** Choose a completion schedule that visibly differs from the input.
5. **Async SQL:** Define `AsyncReadCursor` and implement one query using `customer_id = ANY(%s)`
   with the Python ID list as one bound parameter.
   - **Progressive hint:** The parameter sequence is a one-element tuple containing the list.
6. **Validation:** Return early for empty customer IDs without touching the cursor and reject
   any non-positive ID.
   - **Progressive hint:** Validate the complete collection before the first database effect.
7. **Scale design:** Explain why a semaphore still creates one task per item and design a
   fixed-worker queue for a million inputs.
   - **Progressive hint:** Separate active-operation bounds from task-count and memory bounds.
8. **Cancellation:** Cancel a task inside `managed_async_connection()` and verify rollback/close
   happen before cancellation escapes.
   - **Progressive hint:** Never translate `CancelledError` into an empty or successful result.
9. **Failure analysis:** Trigger two concurrent task failures and inspect `ExceptionGroup`
   behavior from `TaskGroup`.
   - **Progressive hint:** Structured concurrency cancels siblings and reports grouped failures.
10. **Empty work:** Test `map_bounded([], operation, limit=1)` and prove the operation is never
   called.
   - **Progressive hint:** An empty collection is a successful no-op, not an invalid concurrency
     request.
11. **Duplicates:** Define whether duplicate customer IDs are preserved, deduplicated, or
   rejected and test the chosen contract.
   - **Progressive hint:** Input-order promises and dictionary outputs have different duplicate
     semantics.
12. **Architecture:** Compare a semaphore-per-item design with the worker queue on fairness,
   memory, cancellation, and complexity.
   - **Progressive hint:** Choose based on workload scale rather than treating one pattern as
     universally superior.
13. **Database ownership:** Decide whether concurrent operations may share one connection/cursor
   or require a pool-acquired resource per worker.
   - **Progressive hint:** Driver concurrency guarantees and transaction scope determine the
     safe choice.
14. **Deterministic testing:** Replace timing-based async assertions with events/barriers and
   explain why wall-clock sleeps make tests flaky.
   - **Progressive hint:** Coordinate state transitions directly instead of hoping a scheduler
     runs in time.

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

## Next step

[Day 8](day08_production_capstone.md) assembles configuration, adapters,
idempotency, tests, batches, and observability into a restartable job. See
[the Day 7 solution notes](../solutions/day07_solutions.md) after attempting the
exercises.
