# cpp-026: explanations and reference observations

The [executable reference](cpp-026_solution.cpp) adds the oracle cases `total({}) == 0` and `total({-1, 0, 1}) == 0`. The explanations cover measurement hypotheses and why timing is observed rather than asserted. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

A debugger pauses a process so its call stack and local values can be inspected. A profile measures where work was spent. A hypothesis predicts an observation that can be checked. Debugging starts with the smallest reproducible discrepancy, while performance measurement needs a correctness check and a fixed workload.

## Detailed reasoning

Start with a wrong value you can reproduce, then predict which variable or call should explain it. A debugger stack connects the current function to its caller, while local inspection checks the immediate hypothesis. Timing answers a different question. The reference prints elapsed nanoseconds but asserts only the exact checksum and count, since timing depends on compiler, optimizer and machine activity. A faster incorrect program fails before any performance conclusion.

<!-- depth:start -->
## Debugging a wrong value before timing it

Debugging begins with a reproducible mismatch between expected and observed behavior. A debugger lets you stop at a relevant point, inspect variables and follow the call stack. It is most useful when guided by a hypothesis, such as the accumulator being reset or a caller passing the wrong range. Stepping through every line without a question can produce activity without narrowing the cause.

The total function provides a small deterministic target. For [2, 4, 6], the expected sum is 12. A breakpoint before the return can inspect the input size and accumulated value. The call stack distinguishes a defect inside total from a caller supplying a different vector. Preserve the smallest failing fixture and the first point where actual state diverges from the predicted trace.

Timing asks a separate question. Repeating the computation 1000 times yields a checksum of 12000, which prevents the benchmark from being judged only by an elapsed number. A benchmark must still consider optimization, allocation, setup work, warm caches and whether the work resembles the real workload. The compiler may simplify work whose result is predictable, so an apparently tiny duration can reflect optimization rather than useful throughput.

Use a monotonic clock such as steady_clock for elapsed time. Wall-clock adjustments should not create negative benchmark durations. A single measurement is noisy because scheduling and other activity vary. Compare repeated samples and keep the correctness gate fixed. Never assert one exact nanosecond value as a portable expected result.

Debug builds improve some forms of observability, but their performance may differ substantially from optimized builds. A debug-time result should not be advertised as production speed. Record compiler, flags, architecture, input size and included setup costs. If an optimization changes the answer or skips a required validation step, the faster timing is not a valid improvement.

## Debugging the contract

When the wrong output appears only in optimized builds, investigate undefined behavior, uninitialized state and configuration differences before blaming the optimizer. When timing varies wildly, inspect fixture size, setup costs and competing work. When a benchmark is nearly zero, check whether the compiler eliminated or precomputed it. Retain a deterministic checksum and a real workload justification before drawing performance conclusions.
<!-- depth:end -->

## Worked example 1

```cpp
assert(total({2, 4, 6}) == 12);
```

Expected: Known input gives 12 before any measurement.

## Worked example 2

```cpp
for (int i = 0; i < 1000; ++i)
  checksum += total({2, 4, 6});
```

Expected: The checksum is 12000; elapsed nanoseconds vary by run.

## Exercise 1: Reproduce first

Write the expected sum of [2, 4, 6].

**Expected:** 12 from three values.

**Reasoning:** A debugger needs a precise discrepancy.

**Verify:** Write 12 down before running anything, then compare it with Worked example 1's assertion `total({2, 4, 6}) == 12`.

## Exercise 2: Inspect a stack

Use an already available debugger on a -g host build and break in total.

**Expected:** Call stack includes main and total; xs has three values.

**Reasoning:** The browser does not provide an interactive debugger.

**Verify:** At the breakpoint, print the backtrace and confirm `total` appears above `main`, then print `xs.size()` and check that it is 3.

## Exercise 3: Measure a bounded workload

Run 1000 totals and record steady_clock duration.

**Expected:** Checksum 12000 and nonnegative measured duration with units.

**Reasoning:** Output correctness prevents meaningless timing claims.

**Verify:** Assert `checksum == 12000`, as Worked example 2 does, and print the duration through `std::chrono::duration_cast<std::chrono::microseconds>` so the unit appears with the number.

## Exercise 4: Reject a false benchmark

Explain why one observed faster run proves little.

**Expected:** Build mode, workload, repetitions and variability listed.

**Reasoning:** Scheduler noise and optimizer behavior affect tiny measurements.

**Verify:** Check that your explanation names the build flags (`-O0` versus `-O2`), the fixed workload of 1000 totals, the number of repeated runs and the spread between them.

## Exercise 5: Test an empty case

Inspect total({}) with debugger or assertions.

**Expected:** 0 and no element access.

**Reasoning:** The accumulation identity handles emptiness.

**Verify:** Assert `total({}) == 0`, or step through it in the debugger and confirm `std::accumulate` returns its initial 0 without reading an element.

## Exercise 6: Transfer a hypothesis

Replace a linear scan with a map lookup and state a measurable hypothesis.

**Expected:** Same exact results, operation counts and bounded measurements compared.

**Reasoning:** Choose the evidence before declaring a winner.

**Verify:** First assert that both versions return the same answer for every query, then compare operation counts and repeated timings at the same input size and build flags.
