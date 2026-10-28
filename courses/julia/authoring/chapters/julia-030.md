## Parallel work needs an ownership plan

Threads can execute tasks simultaneously and share memory. Shared memory avoids some copying but permits data races when concurrent accesses conflict without synchronization. An increment is conceptually a read, arithmetic operation and write; two tasks can read the same old value and lose an update. The reference does not execute an unsafe race to hope it fails. It tests a design that prevents the conflict.

The classroom launches Julia with two threads. That describes available scheduling capacity, not a guarantee that two tiny tasks overlap long enough to accelerate a program. Thread overhead can dominate small workloads. BLAS and other native libraries may also have thread pools, so nested parallelism can oversubscribe CPU resources.

## Independent chunks and controlled aggregation

Partition a vector into bounded disjoint ranges. Each task reads its range and computes a local partial sum without mutating the input or a shared accumulator. The parent fetches task results and combines them in a declared order. Task completion order may vary; fetch order can still be deterministic.

For integer inputs small enough to avoid overflow, addition is exact and regrouping preserves the result. Floating addition is not associative: \((a+b)+c\) can differ from \(a+(b+c)\). A parallel reduction changes grouping, so numerical tolerances and stability deserve analysis. Do not promise bitwise equality with every sequential floating implementation.

### Worked case A: partial sums with exclusive local state

The first program computes the sum of squares for integers 1 through 100. The hand-derived oracle is \(n(n+1)(2n+1)/6=338350\) for \(n=100\). No worker writes into another worker's accumulator. Repeated runs are checked for the same defined integer result.

{{WORKED_A}}

The function uses one or two chunks depending on input length. Empty input returns the additive identity without spawning pointless work. A larger system would choose chunk size based on workload and measurements, not automatically create one task per element.

### Worked case B: protect an intentionally shared counter

The second program uses a `ReentrantLock` around every shared increment. The lock establishes exclusive access to the read-modify-write operation. The final count equals the number of increments across joined tasks. This is a correctness demonstration, not an efficient way to sum integers.

{{WORKED_B}}

## Task migration and scratch buffers

A task can yield and later resume on a different thread. Indexing scratch storage by `threadid()` is therefore not a general ownership strategy. Even work on one thread can interleave around yields. Prefer scratch state owned by a task or explicitly synchronized resource. Consult the runtime's documented scheduling semantics rather than depending on one observed schedule.

A lock protects only accesses that participate in the same synchronization protocol. Reading the counter outside the lock while writers run can still violate the intended contract. The example reads after all tasks have completed, making that final access safe under its lifecycle.

## Failure and performance reporting

A task failure must reach its caller through fetch or a synchronization boundary. Discarding task handles can lose both result and failure evidence. Do not leave work running after the function says it completed. Keep input ownership clear while tasks execute: the caller must not mutate a vector that workers are concurrently reading unless a stronger protocol exists.

Benchmark a warmed representative workload and compare the full parallel boundary, including scheduling and reduction, with a correct sequential implementation. Report thread counts, native library configuration and data size. Successful two-thread execution demonstrates the API and synchronization mechanism. It does not qualify multi-node distributed computation, GPU execution or universal speedup; those are separate environments and learning paths.
