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

