# Concurrency and parallelism decision lab

**Stable ID:** `python-pro-02`

**Level:** advanced

**Estimated time:** 180–240 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-15`
- Python Days 1–15
- Functions, exceptions, context managers, and basic testing
- `async`/`await` vocabulary from Bridge Day 7 is helpful but not required

This lesson uses only the Python standard library and deterministic local work.

## Learning objectives

By the end, you can:

1. Distinguish concurrency from parallel execution.
2. Classify work as cooperative I/O, blocking I/O, or pure-Python CPU work.
3. Choose among asyncio, threads, and processes with explicit trade-offs.
4. Bound both active work and queued work.
5. Propagate failures, cancellation, and timeouts without orphaned tasks.
6. Explain a lost update and choose an ownership or synchronization strategy.
7. Write process-pool code that is safe under Windows `spawn`.

### Motivation

“Make it concurrent” is not a complete design. Unbounded tasks can move a
bottleneck into memory, threads do not make every CPU workload parallel, and a
cancelled caller must not leave work running in the background. The first
professional skill is choosing the model from the behavior of the work.

## Vocabulary and concepts

- **Concurrency:** multiple operations make progress during overlapping time.
- **Parallelism:** multiple operations execute at the same instant.
- **I/O-bound:** most elapsed time is spent waiting for files, sockets, or
  another service.
- **CPU-bound:** most elapsed time is spent executing computation.
- **Cooperative scheduling:** a task yields explicitly, normally at `await`.
- **Preemptive scheduling:** the runtime or operating system switches workers.
- **Event loop:** the scheduler that resumes ready asyncio tasks.
- **Thread:** a worker sharing process memory; useful around blocking I/O.
- **Process:** an isolated interpreter with serialization and startup cost.
- **Backpressure:** slowing producers when consumers cannot keep up.
- **Structured concurrency:** child tasks live inside a scope that waits for
  them and propagates their failures.
- **Cancellation:** a request to stop work at a safe suspension point.
- **Race condition:** correctness depends on an uncontrolled interleaving.
- **Lost update:** two workers read the same old value and one write overwrites
  the other's change.
- **Spawn:** a process start method that imports the main module in a new
  interpreter; it is the Windows default.

### Decision table

| Work behavior | First model to evaluate | Why | Main caution |
| --- | --- | --- | --- |
| Many awaitable local/network waits | asyncio | Low per-task overhead | Blocking the event loop |
| Blocking I/O library | bounded threads | Existing synchronous API can wait concurrently | Shared mutable state |
| Substantial pure-Python computation | bounded processes | Separate interpreters can execute in parallel | Startup and serialization |
| Tiny or sequential work | no concurrency | Simpler and often faster | Optimizing before measuring |

This is a starting hypothesis, not a guarantee. Measure representative work.

## Worked example / walkthrough

### Predict before running

Open
[`lessons/py_pro_02_concurrency_parallelism.py`](../lessons/py_pro_02_concurrency_parallelism.py).
The baseline awaits three 10 ms waits sequentially. Predict the lower bound on
elapsed time, then run it.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_pro_02_concurrency_parallelism.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pro_02_concurrency_parallelism.py
```

The exact measured time varies, so the check uses a broad behavioral boundary
rather than asserting a fragile benchmark.

### Two different bounds

A semaphore limits active operations, but a producer can still create a million
waiting task objects. A bounded queue controls pending work as well:

```text
producer -> queue(maxsize=2) -> three long-lived consumers
```

When the queue is full, `await queue.put(...)` pauses the producer. This is
backpressure. The consumer count bounds active worker calls.

## Exercises

### Exercise 1 — choose a model

Implement `choose_execution_model` in the learner artifact. For each case,
write one sentence explaining the choice:

- an async database driver,
- a synchronous file metadata API,
- image transforms written in pure Python,
- three tiny computations.

Reject labels that contradict each other. An async function that performs
computation without `await` is still CPU work and blocks the event loop.

### Exercise 2 — build a bounded async map

Implement `bounded_map` with:

1. `asyncio.Queue(maxsize=queue_capacity)`,
2. one producer,
3. a fixed number of consumers,
4. indexed items so results retain input order,
5. a unique sentinel per consumer, and
6. `asyncio.TaskGroup`.

Place `queue.task_done()` in `finally`. Let exceptions propagate. Do not catch
`CancelledError` unless cleanup requires it; if caught, re-raise it.

### Exercise 3 — add per-item timeouts

Wrap each worker call with `asyncio.timeout`. Test one worker slower than the
limit. Inspect the `ExceptionGroup` from `TaskGroup`, and verify a `finally`
block returns the active count to zero.

Prediction: what happens to sibling consumers when one item times out?

### Exercise 4 — adapt blocking I/O

Use `ThreadPoolExecutor(max_workers=N)` for deterministic `time.sleep` jobs.
Compare sequential and threaded elapsed time with generous bounds, then verify
ordered results rather than treating speed as the correctness assertion.

Explain why a thread pool requires a deliberate `max_workers`, even if the
remote service could theoretically accept more requests.

### Exercise 5 — isolate CPU work

Make the CPU function a top-level function with serializable arguments and
results. Use:

```python
multiprocessing.get_context("spawn")
```

and `ProcessPoolExecutor`. Run process creation only beneath:

```python
if __name__ == "__main__":
    ...
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\solutions\py_pro_02_concurrency_parallelism_solution.py --with-processes
```

macOS/Linux:

```bash
.venv/bin/python python/professional/solutions/py_pro_02_concurrency_parallelism_solution.py --with-processes
```

The workload is intentionally small for safety; process startup may make it
slower than sequential execution. That observation is part of the lesson.

### Exercise 6 — reason about shared state

Implement `deterministic_lost_update`. Force two workers to read the same
snapshot, then apply both writes. Compare with two serialized increments.

List three repairs:

- one owner task/process receives update messages,
- a lock protects the complete read/modify/write unit, or
- an external system performs an atomic update.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 7 — prove cancellation cleanup

Cancel `bounded_map` while workers are active. Instrument acquired resources and prove active count, queued acknowledgements, and child tasks return to zero before the parent finishes.

**Progressive hint:** Put cleanup in `finally`, do not suppress `CancelledError`, and use TaskGroup as the child ownership boundary.

### Exercise 8 — inspect structured failures

Run multiple workers that fail with different typed exceptions. Use `except*` to handle one expected category while preserving unexpected failures and their original tracebacks.

**Progressive hint:** ExceptionGroup is a tree. Match by exception type and re-raise what the current layer cannot translate.

### Exercise 9 — stream a backpressured producer

Adapt `bounded_map` from a finite Sequence to an async iterator whose length is unknown. Preserve output order without retaining every input or creating one task per item.

**Progressive hint:** Assign increasing indexes at production, use a bounded queue, and emit completed results through a second bounded channel.

### Exercise 10 — trace context across boundaries

Set a request ID in `contextvars`, then observe propagation through an async task, `asyncio.to_thread`, a raw thread-pool submission, and a spawned process. Make any explicit propagation visible.

**Progressive hint:** Async tasks and `to_thread` copy context by design; arbitrary executors and processes need deliberate value transfer.

### Exercise 11 — design graceful executor shutdown

Own a thread or process pool through a context manager. Stop accepting new work, wait with a bounded policy, cancel pending futures when allowed, and report unfinished work without hanging interpreter exit.

**Progressive hint:** Lifecycle ownership belongs to the component that created the executor. Differentiate pending work from already-running calls.

### Exercise 12 — make an evidence-based model decision

Benchmark sequential, bounded asyncio/threads, and spawned processes on representative I/O and CPU fixtures. Record correctness, startup, throughput, peak active work, transfer size, and cleanup—not just fastest elapsed time.

**Progressive hint:** Use generous repeated measurements and interpret each model only for the workload it matches. A tiny workload can legitimately stay sequential.

## Self-check

- Async results preserve input order even when completion order differs.
- Peak active calls never exceed `worker_count`.
- The bounded queue capacity is finite and positive.
- A worker exception reaches the caller as an exception-group leaf.
- A timeout cancels sibling work and cleanup returns active work to zero.
- Cancelling the parent does not hang.
- The process worker is top-level and pool creation is main-guarded.
- You can explain why a shorter benchmark is not proof of correctness.

Run the focused suite.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_pro_02_concurrency_parallelism -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_pro_02_concurrency_parallelism -v
```

## Common pitfalls

- **Async work runs sequentially:** each coroutine was awaited while it was
  created. Schedule child tasks within a structured scope.
- **The notebook freezes:** a blocking function ran on the event-loop thread,
  or `asyncio.run` was called inside an already-running notebook loop. In a
  notebook, await the coroutine directly.
- **Memory grows before work starts:** millions of tasks were created behind a
  semaphore. Feed fixed workers through a bounded queue.
- **A timeout appears ignored:** blocking code never reached an await point.
  Move compatible blocking I/O to a thread; use a process for cancellable
  isolation when appropriate.
- **Windows recursively launches children:** pool creation is at import time.
  Move it into a function and call that function only under the main guard.
- **A process cannot pickle a function:** lambdas, nested functions, open file
  handles, and many live objects cannot cross the boundary. Use top-level
  functions and plain data.
- **A counter occasionally loses changes:** a compound update was assumed
  atomic. Synchronize the whole invariant or use one owner.

## Next step

- Use Bridge Day 7 for database-specific bounded asyncio patterns.
- Continue to `python-svc-01` and apply retry/rate-limit policy without creating
  unbounded HTTP work.
- Investigate producer/consumer shutdown, signal handling, and process worker
  recycling in a project after mastering this deterministic core.
