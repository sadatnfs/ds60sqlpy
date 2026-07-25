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

1. Implement `managed_async_connection()`. Await the factory, yield once, commit
   on success, roll back on failure, and always close.
2. Implement `map_bounded()` with `asyncio.Semaphore` and `TaskGroup`. Reject
   limits below one and preserve input order.
3. Build a fake operation that increments an active counter, awaits
   `asyncio.sleep(0)`, decrements it, and returns. Assert the measured maximum
   never exceeds the limit.
4. Test that results retain input order even when fake delays cause a different
   completion order.
5. Define an `AsyncReadCursor` Protocol and implement one query using
   `customer_id = ANY(%s)`. Bind the Python list as the single parameter.
6. Test empty input without calling the cursor and reject non-positive IDs.
7. Stretch: discuss why a semaphore bounds active operations but still creates
   one task per item. Design a worker-queue version for a million inputs.

### Progressive hints

1. An async context manager uses `@asynccontextmanager` and an async generator.
2. Store each result by original index, then rebuild the ordered list.
3. Use `async with asyncio.TaskGroup() as group`.
4. Pass `(list(customer_ids),)`—the trailing comma makes a one-element tuple.
5. Let cancellation propagate after cleanup; do not translate it to success.

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
