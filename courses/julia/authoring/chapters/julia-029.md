## Concurrency describes progress, not a speed guarantee

A task is a schedulable unit of Julia work. Several tasks can make progress by yielding while waiting for data or another operation. Asynchronous execution is useful when a workflow has waiting points, but it does not automatically make a CPU loop parallel. The next unit uses thread scheduling explicitly. Keep the distinction visible when discussing throughput.

A channel communicates values between tasks. `Channel{Int}(2)` accepts integer values with a buffer capacity of two. `put!` can wait when the buffer is full; `take!` can wait when it is empty. This creates backpressure: a fast producer cannot enqueue an unlimited number of pending records. The capacity controls queued values, not the total size of all objects reachable from those values.

## Lifecycle is part of the algorithm

The consumer must know when no more values will arrive. Closing a channel permits iteration to finish after buffered values are consumed. A producer that forgets to close can leave its consumer waiting forever. A consumer that stops early can leave a producer blocked on a full buffer. Design ownership, termination and exception propagation together, not as cleanup after the data transformation.

The reference uses `@sync` to wait for enclosed asynchronous work and a `finally` block to close the channel even when the producer fails. It processes a fixed finite list. These bounds make the example appropriate for a classroom run. It does not start a background service or leave tasks alive after success.

### Worked case A: stream squares through a small buffer

The first example launches a producer and consumer, transports five integers through a capacity-two channel, and returns the squared sequence. The sum 55 is independently calculable. The order follows this single producer's ordered input, not a general promise that all concurrent pipelines preserve order.

{{WORKED_A}}

In a production pipeline, attach a stable record identifier if consumers can process items out of order. Reordering a completion stream into input order is a separate operation that requires memory and an explicit policy for failed records.

### Worked case B: make failure observable

The second example injects a declared producer error after sending one value. `@sync` reports task failure through a composite exception. Closure allows the consumer to finish instead of hanging. The program checks that the error reaches the caller; it does not quietly return a shortened successful dataset.

{{WORKED_B}}

## Error and cancellation boundaries

This toy pipeline accepts integer inputs, so the consumer's squaring operation is deliberately simple. If an arbitrary consumer callback could throw, the producer might need coordinated cancellation or channel closure to avoid blocking. Do not generalize this implementation into a fault-tolerant queue without designing that additional path. A timeout can limit waiting, but it does not by itself cancel all related work or establish which records completed.

Use `fetch` when a task's result is part of the API, and join tasks before returning from an operation that promises completion. Printing from a background task is not a durable result contract. Likewise, receiving a channel value does not prove that an external write succeeded unless that acknowledgment is explicitly modeled.

## Transfer to data engineering

A bounded pipeline can separate reading, transformation and writing, but each boundary needs an admission policy, stable identifiers and a completion record. At-least-once retries may duplicate effects; exact-once claims need stronger state coordination. These examples use only local values, so they establish scheduling and failure mechanics rather than a real broker guarantee.

Start with a synchronous reference that defines correct values. Introduce concurrency only after the state transitions and termination rule are clear. Compare outputs, explain allowed ordering, and measure realistic work before claiming throughput improvement. The threads unit keeps the same discipline for shared memory.
