# julia-030: Threads, ownership and deterministic reductions

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-026`, `julia-029`.

Run independent chunks on the prepared two-thread runtime, combine results deterministically and protect shared state with an explicit lock.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Parallel work needs an ownership plan

Threads can execute tasks simultaneously and share memory. Shared memory avoids some copying but permits data races when concurrent accesses conflict without synchronization. An increment is conceptually a read, arithmetic operation and write; two tasks can read the same old value and lose an update. The reference does not execute an unsafe race to hope it fails. It tests a design that prevents the conflict.

The classroom launches Julia with two threads. That describes available scheduling capacity, not a guarantee that two tiny tasks overlap long enough to accelerate a program. Thread overhead can dominate small workloads. BLAS and other native libraries may also have thread pools, so nested parallelism can oversubscribe CPU resources.

## Independent chunks and controlled aggregation

Partition a vector into bounded disjoint ranges. Each task reads its range and computes a local partial sum without mutating the input or a shared accumulator. The parent fetches task results and combines them in a declared order. Task completion order may vary; fetch order can still be deterministic.

For integer inputs small enough to avoid overflow, addition is exact and regrouping preserves the result. Floating addition is not associative: \((a+b)+c\) can differ from \(a+(b+c)\). A parallel reduction changes grouping, so numerical tolerances and stability deserve analysis. Do not promise bitwise equality with every sequential floating implementation.

### Worked case A: partial sums with exclusive local state

The first program computes the sum of squares for integers 1 through 100. The hand-derived oracle is \(n(n+1)(2n+1)/6=338350\) for \(n=100\). No worker writes into another worker's accumulator. Repeated runs are checked for the same defined integer result.

```julia
using Test

function chunk_squares(values::Vector{Int})
    isempty(values) && return 0
    middle = cld(length(values), 2)
    ranges = [1:middle, (middle+1):length(values)]
    jobs = [
        Threads.@spawn(sum(value -> value * value, view(values, range); init = 0)) for
        range in ranges
    ]
    return sum(fetch(job) for job in jobs)
end

function locked_counter(workers::Int, increments::Int)
    workers >= 0 && increments >= 0 || throw(ArgumentError("Nonnegative work counts required"))
    guard = ReentrantLock()
    counter = Ref(0)
    @sync for _ = 1:workers
        Threads.@spawn begin
            for _ = 1:increments
                lock(guard) do
                    counter[] += 1
                end
            end
        end
    end
    return counter[]
end

function worked_a()
    values = collect(1:100)
    @test Threads.nthreads() == 2
    @test chunk_squares(values) == 338350
    @test chunk_squares(Int[]) == 0
    @test chunk_squares([3]) == 9
    @test all(chunk_squares(values) == 338350 for _ = 1:5)
    println("Two-thread chunk reduction: ", chunk_squares(values))
end

worked_a()
```

The function uses one or two chunks depending on input length. Empty input returns the additive identity without spawning pointless work. A larger system would choose chunk size based on workload and measurements, not automatically create one task per element.

### Worked case B: protect an intentionally shared counter

The second program uses a `ReentrantLock` around every shared increment. The lock establishes exclusive access to the read-modify-write operation. The final count equals the number of increments across joined tasks. This is a correctness demonstration, not an efficient way to sum integers.

```julia
using Test

function chunk_squares(values::Vector{Int})
    isempty(values) && return 0
    middle = cld(length(values), 2)
    ranges = [1:middle, (middle+1):length(values)]
    jobs = [
        Threads.@spawn(sum(value -> value * value, view(values, range); init = 0)) for
        range in ranges
    ]
    return sum(fetch(job) for job in jobs)
end

function locked_counter(workers::Int, increments::Int)
    workers >= 0 && increments >= 0 || throw(ArgumentError("Nonnegative work counts required"))
    guard = ReentrantLock()
    counter = Ref(0)
    @sync for _ = 1:workers
        Threads.@spawn begin
            for _ = 1:increments
                lock(guard) do
                    counter[] += 1
                end
            end
        end
    end
    return counter[]
end

function worked_b()
    @test locked_counter(4, 100) == 400
    @test locked_counter(0, 100) == 0
    @test locked_counter(2, 0) == 0
    @test_throws ArgumentError locked_counter(2, -1)
    println("Joined protected increments: ", locked_counter(4, 100))
end

worked_b()
```

## Task migration and scratch buffers

A task can yield and later resume on a different thread. Indexing scratch storage by `threadid()` is therefore not a general ownership strategy. Even work on one thread can interleave around yields. Prefer scratch state owned by a task or explicitly synchronized resource. Consult the runtime's documented scheduling semantics rather than depending on one observed schedule.

A lock protects only accesses that participate in the same synchronization protocol. Reading the counter outside the lock while writers run can still violate the intended contract. The example reads after all tasks have completed, making that final access safe under its lifecycle.

## Failure and performance reporting

A task failure must reach its caller through fetch or a synchronization boundary. Discarding task handles can lose both result and failure evidence. Do not leave work running after the function says it completed. Keep input ownership clear while tasks execute: the caller must not mutate a vector that workers are concurrently reading unless a stronger protocol exists.

Benchmark a warmed representative workload and compare the full parallel boundary, including scheduling and reduction, with a correct sequential implementation. Report thread counts, native library configuration and data size. Successful two-thread execution demonstrates the API and synchronization mechanism. It does not qualify multi-node distributed computation, GPU execution or universal speedup; those are separate environments and learning paths.


## Six investigations

### 1. Derive the reduction oracle

Compute the sum of squares through 100 from the closed-form formula.

**Expected:** The result is 338350.

**Hint:** Use n(n+1)(2n+1)/6.

### 2. Trace an empty chunk

Explain how the single-element input handles its second range.

**Expected:** The empty range contributes 0.

**Hint:** sum uses an explicit init.

### 3. Explain lost updates

Trace two unprotected increments that read the same value.

**Expected:** One update can overwrite the other.

**Hint:** An increment is not one abstract atomic step.

### 4. Review scratch ownership

Explain why threadid-indexed buffers can be unsafe.

**Expected:** Tasks may migrate or interleave.

**Hint:** A thread ID is not permanent task ownership.

### 5. Analyze floating reduction

Explain why changing grouping can change floating results.

**Expected:** Floating addition rounds intermediate values.

**Hint:** Associativity holds for real arithmetic, not all machine arithmetic.

### 6. Design a performance comparison

State the boundaries needed to claim a parallel speedup.

**Expected:** Include scheduling, work, reduction and thread configuration.

**Hint:** Small workloads can be slower.

## Primary references

- [Julia multithreading](https://docs.julialang.org/en/v1/manual/multi-threading/)
- [Task-local ownership guidance](https://julialang.org/blog/2023/07/PSA-dont-use-threadid/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
