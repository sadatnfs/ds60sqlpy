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

