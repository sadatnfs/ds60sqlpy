## Starting point and result

Asynchronous Python can overlap operations that yield control while waiting. It does not turn CPU work into parallel execution or remove resource limits. This chapter uses explicit synchronization and cancellation observations to show what concurrent tasks actually do, without relying on a noisy speed benchmark.

## Mechanism: progress happens at suspension points

An async function returns a coroutine until it is awaited or scheduled. When that coroutine awaits an operation that suspends, the event loop may run another ready task. A blocking filesystem call, synchronous HTTP call or long numerical loop inside the coroutine can prevent that cooperative progress.

Concurrency and parallelism describe different properties. Two tasks may be in progress on one event-loop thread without executing Python instructions simultaneously. CPU parallelism usually needs separate processes, native code that releases the interpreter lock, or another explicitly chosen execution mechanism. The correct mechanism depends on the workload and its resource ownership.

Cancellation is also cooperative. A task receives a cancellation exception at an await boundary. Cleanup belongs in finally blocks or context managers, and callers must await cancelled tasks so cleanup has an opportunity to finish. Merely calling cancel and forgetting the task can leave uncertain resource state.

## Worked case: measure overlap as a state property

The complete program coordinates a small number of asynchronous operations and records the maximum number active at once. The sequential arrangement reaches one active operation; the deliberately concurrent arrangement reaches two. Assertions inspect those counts rather than requiring a particular elapsed duration on the learner's machine.

This matters in a Docker classroom with variable CPU allocation. A timing threshold can fail because the host is busy even when the concurrency logic is correct. An explicit synchronization fixture tests the intended relationship directly and produces a useful diagnostic when the structure is wrong.

The workload is intentionally waiting-oriented. Replacing its suspension with a CPU loop would change the scheduling behavior. That change should lead to a different design decision rather than an assumption that adding async keywords always improves throughput.

## Worked case: cancel and wait for cleanup

The second case starts an operation that records cleanup in a finally block. The caller requests cancellation, awaits the task and handles the cancellation exception. Only then does it assert that cleanup completed.

In a real request, cancellation may follow client disconnect, deadline expiry or application shutdown. The application should decide which work can stop and which durable job must continue independently. A request handler is usually the wrong owner for a long-running operation that must survive the loss of that request or process.

Cancellation does not reverse a completed external effect. If a database commit succeeded just before the caller timed out, retry logic must reconcile the outcome using an operation identity. The later idempotency and outbox chapters build that distinction explicitly.

## Failure diagnosis and discussion

**Why can an async endpoint freeze other requests?** It may contain blocking work between suspension points. Inspect the called libraries and execution path, not just the endpoint's declaration.

**Why avoid sleep-based correctness assertions?** Sleeps can arrange a demonstration, but elapsed-time assumptions are brittle. Events, barriers and observed state provide stronger evidence for lifecycle and ordering properties.

**Does cancelling a task stop a thread it launched?** Not necessarily. The thread's function needs its own cooperative stop mechanism or a bounded lifetime. The coroutine and the external work have separate ownership.

Continue with asynchronous database sessions. They combine cooperative waiting with transactions, connection pools and cleanup rules that must remain correct when a request fails.
