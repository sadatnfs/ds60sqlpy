# julia-029: explained reference

The executable reference is `julia-029_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`squared_pipeline` connects one producer task and one consumer task through `Channel{Int}(2)` inside `@sync`. The producer closes the channel in `finally`, so the consumer's loop always ends, and `@sync` waits for both tasks and rethrows any failure as `CompositeException`. Tasks interleave on one thread here; they do not run simultaneously.

## 1. Trace the queue

The consumer drains a value, allowing the producer to continue without unbounded queue growth.

**Expected observation:** The next put! waits until space is available.

**Why it holds here:** With capacity 2, a third `put!` blocks until the consumer takes a value, so at most two values wait in the channel.

**Plausible wrong approach:** Using an unbounded channel removes the wait but lets a fast producer fill memory when the consumer is slow.

**How to verify:** Print a message before each `put!` and `take!` in an owned copy and observe that puts never run more than two ahead.

## 2. Preserve output meaning

Squares are emitted into the result in channel-consumption order; broader parallel pipelines need explicit ordering.

**Expected observation:** The result is `[4, 0, 9]`.

**Why it holds here:** A single producer puts -2, 0 and 3 in order and the single consumer appends their squares in the same order, giving `[4, 0, 9]`.

**Plausible wrong approach:** Assuming the same order holds with several consumers ignores that each can take values at different times.

**How to verify:** The reference asserts `squared_pipeline([-2, 0, 3]) == [4, 0, 9]` and `[2, 2]` gives `[4, 4]`.

## 3. Inject a failure

No shortened result is mislabeled success; joining propagates the producer failure.

**Expected observation:** A CompositeException reaches the caller.

**Why it holds here:** `fail_after = 0` makes the producer raise on index 1 before any `put!`; `finally` closes the channel and `@sync` reports `CompositeException`.

**Plausible wrong approach:** Wrapping the producer in `try` and swallowing the error returns an empty list that looks like a successful run.

**How to verify:** The reference asserts `@test_throws CompositeException squared_pipeline([1]; fail_after = 0)`.

## 4. Drain a closed channel

Buffered values can be drained before iteration terminates.

**Expected observation:** The buffered value is still returned.

**Why it holds here:** Closing a channel stops future `put!` calls, but the buffered 7 can still be read, so `collect` returns `[7]`.

**Plausible wrong approach:** Expecting `close` to discard buffered values loses the last items a producer sent before finishing.

**How to verify:** Example B asserts `collect(channel) == [7]`, `!isopen(channel)` and an `InvalidStateException` on a later `put!`.

## 5. Identify an unsupported generalization

The bounded example proves its stated simple consumer path; a generic pipeline needs both failure directions designed.

**Expected observation:** A producer can remain blocked without coordinated cancellation.

**Why it holds here:** If the consumer throws, nothing takes from the channel, so a producer blocked on a full buffer waits forever and `@sync` never returns.

**Plausible wrong approach:** Assuming the `finally` in the producer handles every failure ignores that it only runs when the producer itself finishes.

**How to verify:** Inject a consumer error in an owned copy with a timeout and design who closes the channel in that direction.

## 6. Transfer to file processing

Define ordering, retries and partial failure semantics before introducing concurrency.

**Expected observation:** Use stable file IDs and explicit per-file outcomes.

**Why it holds here:** For files, each result should carry a stable file id and an explicit success or failure outcome so retries and partial runs can be audited.

**Plausible wrong approach:** Treating a printed `done` line as completion loses the record if the process stops before output is flushed.

**How to verify:** Write one outcome row per file id and check that the count of rows equals the count of input files.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-029: all reference checks passed`:

`[2, 2]` and `[4]` add repeated and single-value cases. The `@async 6 * 7` lines show that `fetch` waits for the task and returns 42, after which `istaskdone(job)` is true, which is the same join that `@sync` performs for the pipeline.

```julia
function exercise_checks()
    @test squared_pipeline([-2, 0, 3]) == [4, 0, 9]
    @test squared_pipeline([2, 2]) == [4, 4]
    @test_throws CompositeException squared_pipeline([1]; fail_after = 0)
    job = @async 6 * 7
    @test fetch(job) == 42
    @test istaskdone(job)
    @test squared_pipeline([4]) == [16]
end
```
