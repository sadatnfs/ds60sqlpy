# julia-030: explained reference

The executable reference is `julia-030_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`chunk_squares` splits the input into two index ranges, spawns one task per range that sums squares with `init = 0`, then fetches and adds the two partial sums in a fixed order. `locked_counter` spawns workers that each increment a shared `Ref` inside `lock(guard)`, so every read and write of the counter is protected.

## 1. Derive the reduction oracle

The independent formula checks the reduction without copying its loop.

**Expected observation:** The result is 338350.

**Why it holds here:** The formula n(n+1)(2n+1)/6 with n = 100 gives 100 times 101 times 201 divided by 6, which is 338350.

**Plausible wrong approach:** Checking the threaded result against a serial loop written by the same author shares any indexing mistake with the parallel code.

**How to verify:** Example A asserts `chunk_squares(collect(1:100)) == 338350` five times in a row.

## 2. Trace an empty chunk

The additive identity makes the empty partial result well-defined.

**Expected observation:** The empty range contributes 0.

**Why it holds here:** For `[3]`, `middle = cld(1, 2) = 1`, so the second range is `2:1`, which is empty, and `sum` with `init = 0` returns 0.

**Plausible wrong approach:** Dropping `init = 0` makes `sum` over an empty view throw, so a one-element input fails.

**How to verify:** Example A asserts `chunk_squares([3]) == 9`, and the reference checks `chunk_squares([-2, 3]) == 13`.

## 3. Explain lost updates

Locking the full read-modify-write operation prevents this schedule under the stated protocol.

**Expected observation:** One update can overwrite the other.

**Why it holds here:** Two tasks can both read 5, both compute 6 and both write 6, so one increment is lost without a lock.

**Plausible wrong approach:** Assuming `counter[] += 1` is a single indivisible step predicts the full count even without the lock.

**How to verify:** Example B asserts `locked_counter(4, 100) == 400`; an unprotected owned copy may sometimes print less.

## 4. Review scratch ownership

Task-owned state or explicit synchronization is safer than undocumented schedule assumptions.

**Expected observation:** Tasks may migrate or interleave.

**Why it holds here:** Tasks can move between threads, so a buffer indexed by `Threads.threadid()` may be shared by two tasks that both start on one thread.

**Plausible wrong approach:** Allocating per-thread buffers by `threadid()` assumes a task keeps its thread for life, which the scheduler does not promise.

**How to verify:** Give each spawned task its own local buffer and confirm results do not depend on the thread count.

## 5. Analyze floating reduction

Use a justified tolerance or a numerically stable reduction when extending the integer example.

**Expected observation:** Floating addition rounds intermediate values.

**Why it holds here:** Floating addition rounds each partial result, so grouping the sum into two chunks can change the last bits compared with a serial sum.

**Plausible wrong approach:** Asserting exact equality between a threaded float reduction and a serial one fails or passes by luck depending on the data.

**How to verify:** Compare float sums with `isapprox` and a stated tolerance; the integer example can stay exact.

## 6. Design a performance comparison

Measure the full warmed operation with identical correct outputs and representative data.

**Expected observation:** Include scheduling, work, reduction and thread configuration.

**Why it holds here:** A speedup claim must compare warmed runs of the whole operation, with identical correct outputs, on the same thread configuration.

**Plausible wrong approach:** Timing 100 small integers once on two threads and calling it faster ignores the scheduling cost that dominates tiny workloads.

**How to verify:** Report the thread count from `Threads.nthreads()`, input size and repeated timings for one and two threads.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-030: all reference checks passed`:

`[0, 0]` gives 0 through the zero contributions, while `locked_counter(1, 7) == 7` is the serial baseline with no contention. The `before` copy confirms that splitting work into views reads the input without changing it, and the sum of squares of 1, 2 and 3 is 14.

```julia
function exercise_checks()
    @test chunk_squares([-2, 3]) == 13
    @test chunk_squares([0, 0]) == 0
    @test locked_counter(1, 7) == 7
    @test_throws ArgumentError locked_counter(-1, 2)
    values = [1, 2, 3]
    before = copy(values)
    @test chunk_squares(values) == 14
    @test values == before
end
```
