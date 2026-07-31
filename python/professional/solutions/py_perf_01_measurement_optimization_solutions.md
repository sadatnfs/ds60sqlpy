# Measurement-first optimization solution reasoning

Attempt `python-perf-01` before opening
[`py_perf_01_measurement_optimization_solution.py`](py_perf_01_measurement_optimization_solution.py).

The solution first fixes the workload and output semantics. The quadratic
duplicate search repeatedly scans prefixes; the set-based implementation keeps
the value whose second occurrence appears first while changing expected
complexity from O(n squared) to O(n). Correctness tests compare varied edge
cases before any timing is interpreted.

`timeit` performs warmups and repeated batches. Minimum, median, and maximum are
reported as evidence from one machine; none becomes a universal test
threshold. `cProfile` locates cumulative hotspots, while `tracemalloc` measures
Python allocations and peak pressure. Native-library buffers and operating
system memory may require additional tools.

The streamed sum avoids an intermediate list. NumPy is an optional vectorized
comparison, not a promised speedup: conversion cost and array size matter.
Likewise, process work may copy or serialize the payload per worker, so adding
processes can increase elapsed time and memory.

Caching trades recomputation for memory and staleness. The deterministic policy
refuses cache when freshness or budget disallows it, accepts high measured
reuse within budget, and otherwise requests more evidence.

Native extensions and foreign-function interfaces (FFIs) add packaging,
portability, safety, and boundary-transfer costs. Improve the algorithm first.
When native work owns a measured hotspot, batch calls and data transfer rather
than crossing the boundary in a tight Python loop.

Edge cases include benchmarks smaller than timer noise, cold imports, thermal
or background-load variation, changed semantics, hash/cache keys that retain
large objects, process copies hidden by copy-on-write assumptions, native
allocations invisible to `tracemalloc`, and microbenchmarks that do not
represent production data.

---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

The workflow preserves a correctness oracle and performance budget while using profiles and scaling evidence to justify each change.

1. **benchmark contract:** fixes data size/distribution, environment, warm-up, repetitions, statistic, and correctness invariant.
2. **profile → hypothesis → one change:** connects an observed hotspot to a scoped optimization rather than guessing.
3. **scale curve + budget:** measures several input sizes and checks latency/memory against an explicit threshold.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** Caching, batching, vectorization, database pushdown, native libraries, concurrency, or a better algorithm solve different bottlenecks.

**Trade-off:** Optimizations can increase memory, latency variance, startup cost, code complexity, and platform dependence even when median runtime improves.

**Failure boundary:** Warm/cold cache, tiny inputs, skew, GC, first-run imports, thread oversubscription, nonhashable values, and Windows process startup need separate evidence.

**Verification:** Assert output equivalence and failures, benchmark repeated realistic workloads/sizes, report distribution and resources, profile the hotspot, and enforce the stated budget.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

```python
import statistics
import timeit

samples = timeit.repeat(
    "sum(range(10_000))",
    repeat=7,
    number=200,
)
report = {
    "median_seconds": statistics.median(samples),
    "min_seconds": min(samples),
    "max_seconds": max(samples),
}
print(report)
assert report["min_seconds"] <= report["median_seconds"] <= report["max_seconds"]
```

**Expected observation:** Repeated timings vary; median and range reveal noise that one measurement hides.

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_perf_01_measurement_optimization_solution.py`](py_perf_01_measurement_optimization_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — Define semantics before speed

**Prompt recap:** For `[4, 1, 3, 2, 3, 4]`, the answer is `3`: the duplicate whose *second* occurrence appears first. Complete `first_duplicate_linear` with a set and prove equivalence for empty, unique, immediate, and competing duplicates.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Define semantics before speed — assert first_duplicate_linear([4,1,3,2,3,4]) == 3, [] and unique input return None, [2,2] returns 2, and competing duplicates follow earliest second occurrence; compare all cases with the baseline oracle.

### Exercise 2 — Build a representative timing plan

**Prompt recap:** Choose a workload size large enough to rise above timer noise but small enough for quick study. Warm up separately, then collect at least five repeated batches with `timeit`. Record Python version, platform, input size, and plan. Do not assert “candidate < baseline” in the test suite. CI hosts, antivirus, power state, and schedulers make that flaky.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Build a representative timing plan — choose a workload size large enough to rise above timer noise but small enough for quick study; record Python version, platform, input size, and plan; do not assert “candidate < baseline” in the test suite.

### Exercise 3 — Ask cProfile a different question

**Prompt recap:** Profile one complete representative call and sort by cumulative time. Locate the call path, not just the leaf with the largest self time. Reduce the workload if profiling overhead dominates, and do not compare profiled seconds directly with unprofiled `timeit` seconds.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Ask cProfile a different question — profile one complete representative call and sort by cumulative time; locate the call path, not just the leaf with the largest self time; reduce the workload if profiling overhead dominates, and do not compare profiled seconds directly with unprofiled timeit seconds.

### Exercise 4 — Measure allocation pressure

**Prompt recap:** Compare materialized-list and generator sums with `tracemalloc`. Assert equal results and report bounds (`peak >= current >= 0`). Explain why `tracemalloc` may not see memory allocated inside every native library.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Measure allocation pressure — compare materialized-list and generator sums with tracemalloc; assert equal results and report bounds (peak >= current >= 0); explain why tracemalloc may not see memory allocated inside every native library.

### Exercise 5 — Compare optional vectorization

**Prompt recap:** With NumPy installed, compare a Python loop with `np.square(array).sum()`. Include conversion from Python values when that conversion exists in the real workflow. Small input can favor the loop; already-resident large arrays can favor vectorized native work. Measure both representative cases.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Compare optional vectorization — with NumPy installed, compare a Python loop with np.square(array).sum(); include conversion from Python values when that conversion exists in the real workflow; measure both representative cases.

### Exercise 6 — Model process transfer

**Prompt recap:** Serialize a safe local JSON payload and measure its byte length. Complete `estimated_transfer_bytes`. Four workers each receiving two copies move eight payload equivalents before computation. Real process protocols may add framing, copies, or shared-memory complexity.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Model process transfer — measure one JSON payload's encoded byte length and assert estimated_transfer_bytes(payload_bytes, workers=4, copies=2) equals 8 * payload_bytes; reject negative counts and state protocol overhead is excluded.

### Exercise 7 — Evaluate caching

**Prompt recap:** Use `cached_fibonacci.cache_info()` to observe hits. Then evaluate a real candidate by: - measured reuse, - entry count and bytes, - invalidation/freshness rules, - key cardinality, and - whether retained objects prevent memory release. Caching a low-reuse, high-cardinality result can make performance worse.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Evaluate caching — use cached fibonacci.cache info() to observe hits; then evaluate a real candidate by: - measured reuse, - entry count and bytes, - invalidation/freshness rules, - key cardinality, and - whether retained objects prevent memory release; caching a low-reuse, high-cardinality result can make performance worse.

### Exercise 8 — Bound native/FFI work

**Prompt recap:** Use the policy to prefer an available algorithm improvement. If a measured hotspot remains, batch native calls and cap transfer. Survey Cython, Rust/PyO3, C/C++ extensions, and `ctypes`/`cffi`; record build wheels, ABI, ownership, error, and safety obligations before choosing one.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Bound native/FFI work — use the policy to prefer an available algorithm improvement; if a measured hotspot remains, batch native calls and cap transfer; survey Cython, Rust/PyO3, C/C++ extensions, and ctypes/cffi; record build wheels, ABI, ownership, error, and safety obligations before choosing one.

### Exercise 9 — Apply the evidence decision

**Prompt recap:** Complete `choose_next_step` in priority order: 1. fix unequal behavior, 2. reduce peak memory beyond budget, 3. reduce transfer consuming at least 30 percent, 4. optimize a hotspot consuming at least 50 percent, or 5. keep the current implementation. Thresholds are a transparent lesson policy, not universal laws.

**Reference reasoning:** Performance work begins with equivalent semantics and representative evidence, then addresses algorithm, memory, transfer, hotspot, cache, or native boundary in priority order. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Apply the evidence decision — table-test choose_next_step so unequal outputs select correctness, over-budget memory selects memory, transfer >=30% selects transfer, hotspot >=50% selects optimization, and the below-threshold case selects keep.

### Exercise 10 — compare timing distributions

**Prompt recap:** Run interleaved repeated batches for baseline and candidate, report median, spread, paired ratios/differences, environment, and correctness. Avoid a binary CI speed assertion.

**Reasoning path:** Alternate order to reduce drift and choose repetitions from timer resolution/runtime. Keep raw measurements for review.

Warm both implementations, verify output equality for every test workload,
then collect paired batches in alternating or randomized deterministic order.
Report sample count, min/median/quantiles, paired ratio distribution, Python/
platform, workload, and background caveats.

The evidence supports a local estimate, not a universal guarantee. A CI
performance gate needs a separately reviewed stable runner and practical
regression budget.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** compare timing distributions — run interleaved repeated batches for baseline and candidate, report median, spread, paired ratios/differences, environment, and correctness; avoid a binary CI speed assertion.

### Exercise 11 — diagnose warmup, GC, and environment noise

**Prompt recap:** Measure cold import/first call separately from steady state. Repeat with garbage collection controlled, background load noted, and process affinity/power assumptions documented rather than hidden.

**Reasoning path:** GC configuration can change real semantics/latency. Report it; do not simply disable GC to obtain a preferred number.

Define whether startup belongs to the user-facing workload. Record first-call
and subsequent distributions separately. Inspect GC counts/collections and
retain the production-like setting for the primary result; a controlled-GC run
is diagnostic evidence only.

Restart the interpreter when import/cache state matters. Do not discard
outliers automatically—identify scheduler, I/O, thermal, or allocation causes.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** diagnose warmup, GC, and environment noise — measure cold import/first call separately from steady state; repeat with garbage collection controlled, background load noted, and process affinity/power assumptions documented rather than hidden.

### Exercise 12 — trade algorithm speed for memory

**Prompt recap:** Compare set-based first-duplicate search with a sorted/indexed alternative under a strict memory budget. Preserve 'first second occurrence' semantics and report time/peak memory across unique-heavy and duplicate-early inputs.

**Reasoning path:** An algorithm with lower expected time can retain O(n) state. Alternative semantics or external sorting must be stated honestly.

The set solution is the correct linear baseline under available memory. If the
budget cannot hold all seen values, exact streaming detection may need disk/
partitioning or multiple passes. Sorting values alone loses encounter-order
semantics unless original indices are preserved.

Measure representative distributions and choose based on both time and peak
budget. Approximate probabilistic structures require an explicit false-positive
contract and cannot silently replace exact output.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** trade algorithm speed for memory — compare set-based first-duplicate search with a sorted/indexed alternative under a strict memory budget; preserve 'first second occurrence' semantics and report time/peak memory across unique-heavy and duplicate-early inputs.

### Exercise 13 — test vectorized dtype boundaries

**Prompt recap:** Compare Python integer sum-of-squares with NumPy int32, int64, float, and object arrays near overflow. Detect silent overflow and choose a validated dtype.

**Reasoning path:** Python integers grow; fixed-width NumPy integers wrap unless the operation/dtype is widened deliberately.

Construct values whose square/sum exceed int32 and then int64. Compute the
Python reference, inspect NumPy result dtype, and compare exactly. Choose a
wider or object dtype only after checking range and performance trade-offs;
for floats, define acceptable numeric tolerance and finite behavior.

Vectorization that returns a faster wrong number is a correctness failure and
must route `choose_next_step` to fix correctness first.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** test vectorized dtype boundaries — compare Python integer sum-of-squares with NumPy int32, int64, float, and object arrays near overflow; detect silent overflow and choose a validated dtype.

### Exercise 14 — evaluate shared-memory process input

**Prompt recap:** Compare normal process serialization with read-only shared memory for one large numeric payload. Include setup/copy, worker mapping, cleanup, spawn compatibility, and ownership failure cases.

**Reasoning path:** Pass only shared-memory name/shape/dtype to spawned workers. One owner closes/unlinks after every worker releases.

Verify identical results before timing. The parent creates/copies once into
shared memory, workers attach read-only by contract, and `finally` closes every
handle; the parent unlinks once after pool completion/failure. Include setup and
teardown in end-to-end evidence.

Shared memory reduces repeated transfer but adds lifecycle, synchronization,
and crash-cleanup complexity. It is justified only when measured payload cost
is material.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** evaluate shared-memory process input — compare normal process serialization with read-only shared memory for one large numeric payload; include setup/copy, worker mapping, cleanup, spawn compatibility, and ownership failure cases.

### Exercise 15 — separate I/O concurrency from CPU optimization

**Prompt recap:** Benchmark a local fake I/O wait and a pure-Python CPU loop under sequential, async/thread, and process designs. Explain why each model helps one workload and may hurt another.

**Reasoning path:** Use deterministic waits and fixed computations; include scheduling/startup and bounded active work.

Async/threads overlap cooperative/blocking waits but do not generally speed
substantial Python bytecode under the GIL. Processes can parallelize CPU work
but add spawn and serialization. Tiny tasks often remain fastest sequentially.

Report correctness, throughput, latency, peak concurrency, transfer, and
cleanup. Do not generalize from one task label such as “data processing.”

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** separate I/O concurrency from CPU optimization — benchmark a local fake I/O wait and a pure-Python CPU loop under sequential, async/thread, and process designs; explain why each model helps one workload and may hurt another.

### Exercise 16 — prevent a cache stampede

**Prompt recap:** Model many callers missing one expensive cache key. Add single-flight ownership, bounded wait, success publication, failure cleanup, and stale/retry policy with injected time.

**Reasoning path:** One caller computes; others await the same owned result. A failed owner must wake waiters and remove poisoned in-flight state.

Store a per-key future/condition separate from completed cache entries. The
first caller becomes owner, computes outside the global lock, then publishes
or propagates the failure and clears in-flight state in `finally`. Waiters have
a deadline/cancellation policy.

Single-flight prevents duplicate work but does not define freshness,
eviction, distributed coordination, or whether stale data is acceptable.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** prevent a cache stampede — model many callers missing one expensive cache key; add single-flight ownership, bounded wait, success publication, failure cleanup, and stale/retry policy with injected time.

### Exercise 17 — review an FFI ownership boundary

**Prompt recap:** Specify one batched native function: accepted buffer dtype/layout, length, ownership/lifetime, mutability, error mapping, GIL behavior, panic/exception containment, and platform wheel matrix.

**Reasoning path:** Batch work across the boundary and validate before calling native code. Never let a borrowed buffer outlive its Python owner.

The Python wrapper validates contiguous shape/dtype/range, pins/owns the buffer
for the complete call, and translates a bounded native error into a typed
Python exception. Native code must not unwind/panic across the ABI. State
whether it releases the GIL and how threads interact.

Test empty, maximum bounded size, invalid layout, native failure, and repeated
calls under sanitizers/native tooling where available. Packaging evidence is
required for every supported target.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** review an FFI ownership boundary — specify one batched native function: accepted buffer dtype/layout, length, ownership/lifetime, mutability, error mapping, GIL behavior, panic/exception containment, and platform wheel matrix.

### Exercise 18 — design a continuous performance gate

**Prompt recap:** Define a stable local/CI benchmark artifact with workload version, correctness hash, environment, raw timings, peak memory, practical regression budget, comparison policy, and an investigation path instead of an immediate flaky fail.

**Reasoning path:** Separate noisy pull-request signal from controlled scheduled runs. Gate only after runner variance and minimum practical effect are characterized.

Version fixtures and benchmark plan, save machine-readable raw observations,
and compare against a reviewed baseline from equivalent hardware/software.
Require correctness first. A regression exceeding both practical threshold and
uncertainty triggers repeat/investigation; a stable controlled pipeline may
then block.

Never optimize solely to the benchmark. Periodically reconcile it with
production/representative profiles and update through reviewed evidence.

**Common trap:** One fastest timing, a microbenchmark-only workload, invisible native memory, dtype overflow, process copies, or cache staleness can turn an optimization into a regression.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** design a continuous performance gate — define a stable local/CI benchmark artifact with workload version, correctness hash, environment, raw timings, peak memory, practical regression budget, comparison policy, and an investigation path instead of an immediate flaky fail.
