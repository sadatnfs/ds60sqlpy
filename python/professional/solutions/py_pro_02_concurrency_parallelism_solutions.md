# Concurrency and parallelism solution reasoning

Attempt `python-pro-02` before reading this file. The executable reference is
[`py_pro_02_concurrency_parallelism_solution.py`](py_pro_02_concurrency_parallelism_solution.py).

## Choosing by behavior

The solution does not choose from task names such as “download” or “analysis.”
It asks whether the API yields cooperatively, blocks a thread, or executes
substantial Python bytecode. Asyncio is a concurrency model for awaitable work,
threads adapt blocking I/O, and processes isolate CPU work and the interpreter.

A three-item computation may remain sequential because startup, scheduling, and
serialization cost more than the saved time. Correctness and measurement come
before adding workers.

## Bounded queue design

The producer inserts `(index, item)` pairs into a queue with a real maximum
size. A fixed number of consumers performs work. This creates two independent
bounds:

- `queue_capacity` limits waiting inputs and applies backpressure.
- `worker_count` limits active calls.

Results are stored by index and assembled after the `TaskGroup`, so completion
order does not change output order. A unique object is used as the sentinel;
ordinary user data can never equal it accidentally.

`TaskGroup` is the ownership boundary. If one consumer raises, the group
cancels its siblings, waits for their cleanup, and raises an `ExceptionGroup`.
The implementation does not log and continue because that would silently
return partial data.

## Cancellation and timeouts

`asyncio.timeout` transforms an overdue operation into `TimeoutError`.
Cancellation reaches the worker at an await point. `ConcurrencyProbe.activity`
decrements its count in `finally`, which proves cleanup for normal return,
worker failure, timeout, and parent cancellation.

Cancellation is cooperative. A CPU loop or blocking library call on the event
loop cannot observe it promptly. Choosing the correct execution boundary is
therefore part of timeout correctness.

## Threads and processes

The thread example passes immutable job tuples and returns values. It avoids a
shared output list, making ordering the executor's responsibility. Threads
share memory, so real programs still need ownership or synchronization for
shared invariants.

The process function is top-level and accepts an integer. The pool explicitly
uses `spawn`, so tests exercise the same import behavior required by Windows.
Pool creation occurs only inside called functions, and the executable calls it
under a main guard. A child can import the module without recursively launching
more children.

## Lost-update edge case

Timing-sensitive race tests are unreliable. The solution models the dangerous
interleaving directly:

1. both workers read the same initial value,
2. both compute `initial + 1`,
3. the second write replaces the first.

The unsafe result grows by one; the serialized result grows by two. A lock must
cover the entire read/modify/write operation—not just the final assignment.

## Alternatives

- `asyncio.Semaphore` is adequate when the number of created tasks is already
  bounded. A queue is safer for a large or streaming producer.
- `asyncio.to_thread` is concise for occasional blocking calls. A named
  executor gives explicit lifecycle and capacity for a subsystem.
- Native-code libraries may release the Global Interpreter Lock and benefit
  from threads for CPU work. Measure the actual library rather than assuming.
- A job system may replace local process pools when work must survive process or
  machine failure. That introduces persistence and delivery semantics beyond
  this lesson.

## Expected behavior

The tests prove ordered results, peak active work at or below the limit,
timeout and failure propagation, cancellation cleanup, deterministic lost
updates, thread output, and a small spawned-process calculation. No test relies
on a narrow elapsed-time threshold, random scheduling, or external I/O.


---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

The solution treats primitive choice, admission control, lifecycle, and result accounting as separate contracts validated under forced interleavings.

1. **workload classification:** identifies CPU time, blocking/nonblocking I/O, data transfer, and external capacity before selecting a primitive.
2. **semaphore/worker queue:** bounds active and queued work rather than creating one task per input.
3. **structured result:** associates each input with success/failure/cancellation so no work disappears.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** Vectorized/native libraries often outperform Python processes; a simple sequential loop is best when overhead dominates.

**Trade-off:** Higher concurrency may reduce latency until external or local saturation, then worsens queuing, memory, and failure amplification.

**Failure boundary:** Cancellation during acquisition, task exception, process pickle failure, Windows spawn recursion, lost ordering, and executor shutdown need tests.

**Verification:** Benchmark against sequential, prove peak active/queued bounds, account for every input, inject failures/cancellation, and run process examples behind a main guard.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

```python
def choose_execution(*, waits_nonblocking=False, waits_blocking=False, cpu_python=False):
    if sum((waits_nonblocking, waits_blocking, cpu_python)) != 1:
        raise ValueError("classify one dominant workload")
    if waits_nonblocking:
        return "asyncio"
    if waits_blocking:
        return "threads"
    return "processes-or-native-vectorization"

assert choose_execution(waits_nonblocking=True) == "asyncio"
assert choose_execution(cpu_python=True) == "processes-or-native-vectorization"
```

**Expected observation:** The decision follows where time is spent, not a belief that one primitive is universally faster.

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_pro_02_concurrency_parallelism_solution.py`](py_pro_02_concurrency_parallelism_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — choose a model

**Prompt recap:** Implement `choose_execution_model` in the learner artifact. For each case, write one sentence explaining the choice: - an async database driver, - a synchronous file metadata API, - image transforms written in pure Python, - three tiny computations. Reject labels that contradict each other. An async function that performs computation without `await` is still CPU work and blocks the event loop.

**Reference reasoning:** Choose concurrency from workload behavior, then bound task ownership, queued work, active work, cancellation, and process/thread lifecycle explicitly. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `choose a model`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 2 — build a bounded async map

**Prompt recap:** Implement `bounded_map` with: 1. `asyncio.Queue(maxsize=queue_capacity)`, 2. one producer, 3. a fixed number of consumers, 4. indexed items so results retain input order, 5. a unique sentinel per consumer, and 6. `asyncio.TaskGroup`. Place `queue.task_done()` in `finally`. Let exceptions propagate. Do not catch `CancelledError` unless cleanup requires it; if caught, re-raise it.

**Reference reasoning:** Choose concurrency from workload behavior, then bound task ownership, queued work, active work, cancellation, and process/thread lifecycle explicitly. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `build a bounded async map`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 3 — add per-item timeouts

**Prompt recap:** Wrap each worker call with `asyncio.timeout`. Test one worker slower than the limit. Inspect the `ExceptionGroup` from `TaskGroup`, and verify a `finally` block returns the active count to zero. Prediction: what happens to sibling consumers when one item times out?

**Reference reasoning:** Choose concurrency from workload behavior, then bound task ownership, queued work, active work, cancellation, and process/thread lifecycle explicitly. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `add per-item timeouts`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 4 — adapt blocking I/O

**Prompt recap:** Use `ThreadPoolExecutor(max_workers=N)` for deterministic `time.sleep` jobs. Compare sequential and threaded elapsed time with generous bounds, then verify ordered results rather than treating speed as the correctness assertion. Explain why a thread pool requires a deliberate `max_workers`, even if the remote service could theoretically accept more requests.

**Reference reasoning:** Choose concurrency from workload behavior, then bound task ownership, queued work, active work, cancellation, and process/thread lifecycle explicitly. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `adapt blocking I/O`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 5 — isolate CPU work

**Prompt recap:** Make the CPU function top-level with serializable arguments and results. Use `multiprocessing.get_context("spawn")` with `ProcessPoolExecutor`, and create processes only beneath an `if __name__ == "__main__":` guard. Run the solution with `--with-processes`; explain why startup can make a small workload slower.

**Reference reasoning:** Choose concurrency from workload behavior, then bound task ownership, queued work, active work, cancellation, and process/thread lifecycle explicitly. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `isolate CPU work`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 6 — reason about shared state

**Prompt recap:** Implement `deterministic_lost_update`. Force two workers to read the same snapshot, then apply both writes. Compare with two serialized increments. List three repairs: - one owner task/process receives update messages, - a lock protects the complete read/modify/write unit, or - an external system performs an atomic update.

**Reference reasoning:** Choose concurrency from workload behavior, then bound task ownership, queued work, active work, cancellation, and process/thread lifecycle explicitly. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `reason about shared state`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 7 — prove cancellation cleanup

**Prompt recap:** Cancel `bounded_map` while workers are active. Instrument acquired resources and prove active count, queued acknowledgements, and child tasks return to zero before the parent finishes.

**Reasoning path:** Put cleanup in `finally`, do not suppress `CancelledError`, and use TaskGroup as the child ownership boundary.

Start the operation as one parent task, wait on a deterministic probe until at
least one worker is active, cancel the parent, and await it while expecting
`CancelledError`. Every worker releases its probe/resource in `finally`, and
the producer/consumers are owned by the TaskGroup so no orphan remains.

Queue accounting must still call `task_done` for an item already removed.
Cancellation is a normal control path; logging it as an application error or
continuing with partial results is incorrect.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `prove cancellation cleanup`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 8 — inspect structured failures

**Prompt recap:** Run multiple workers that fail with different typed exceptions. Use `except*` to handle one expected category while preserving unexpected failures and their original tracebacks.

**Reasoning path:** ExceptionGroup is a tree. Match by exception type and re-raise what the current layer cannot translate.

Allow TaskGroup to collect concurrent failures, then use `except* ExpectedError`
for the domain category this boundary owns. Record bounded item identities,
not full sensitive payloads. Any unmatched subgroup must propagate.

Do not flatten everything into one string or return only the first exception;
that destroys evidence. Cancellation caused by sibling failure is distinct
from an independent worker defect.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `inspect structured failures`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 9 — stream a backpressured producer

**Prompt recap:** Adapt `bounded_map` from a finite Sequence to an async iterator whose length is unknown. Preserve output order without retaining every input or creating one task per item.

**Reasoning path:** Assign increasing indexes at production, use a bounded queue, and emit completed results through a second bounded channel.

Separate input and output backpressure. A fixed consumer pool receives indexed
items; a coordinator buffers only the out-of-order window needed to emit the
next index. If the downstream consumer is slow, a bounded result queue stops
workers from accumulating unbounded completed objects.

Define cancellation and partial-output semantics before implementation.
Preserving all results in a final list is incompatible with truly unbounded
input, so expose an async result iterator instead.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `stream a backpressured producer`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 10 — trace context across boundaries

**Prompt recap:** Set a request ID in `contextvars`, then observe propagation through an async task, `asyncio.to_thread`, a raw thread-pool submission, and a spawned process. Make any explicit propagation visible.

**Reasoning path:** Async tasks and `to_thread` copy context by design; arbitrary executors and processes need deliberate value transfer.

Pass correlation data as an explicit argument whenever crossing a process
boundary. For a raw thread executor, submit `copy_context().run` only when
implicit context is truly part of the API. The worker returns the observed ID
so the test asserts behavior rather than inspecting logs by eye.

Context propagation must never become credential propagation. Keep security
tokens in a reviewed credential boundary, not a general diagnostic context.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `trace context across boundaries`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 11 — design graceful executor shutdown

**Prompt recap:** Own a thread or process pool through a context manager. Stop accepting new work, wait with a bounded policy, cancel pending futures when allowed, and report unfinished work without hanging interpreter exit.

**Reasoning path:** Lifecycle ownership belongs to the component that created the executor. Differentiate pending work from already-running calls.

Expose an explicit close/drain operation and make repeated close idempotent.
The shutdown path prevents submissions first, waits for the documented grace
period, and records still-running jobs. Threads cannot be safely killed;
blocking calls require their own timeout/cancellation contract.

Process pools also need import-safe top-level callables and a main guard.
Avoid relying only on garbage collection or interpreter teardown.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `design graceful executor shutdown`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 12 — make an evidence-based model decision

**Prompt recap:** Benchmark sequential, bounded asyncio/threads, and spawned processes on representative I/O and CPU fixtures. Record correctness, startup, throughput, peak active work, transfer size, and cleanup—not just fastest elapsed time.

**Reasoning path:** Use generous repeated measurements and interpret each model only for the workload it matches. A tiny workload can legitimately stay sequential.

First assert identical ordered results and failure behavior. Then run warmups
and repeated local measurements, reporting distributions rather than flaky
speed assertions. For processes, include serialization and startup; for async
and threads, include dependency capacity and caller deadline.

Choose the simplest model that satisfies the measured requirement and resource
budget. Preserve the benchmark plan so future workloads can invalidate the
decision honestly.

**Common trap:** Unbounded task creation, swallowed cancellation, shared mutation, or process startup outside a main guard can make correct-looking code leak work or fail on Windows.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `make an evidence-based model decision`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
