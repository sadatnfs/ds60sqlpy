# Measurement-first performance engineering

**Stable ID:** `python-perf-01`

**Level:** advanced

**Estimated time:** 210–270 minutes

## Level and prerequisites

- **Catalog prerequisites:** `python-23` and `python-pro-02`
- Python Days 1–15 and the data track through Day 23
- `python-pro-02` for process/concurrency trade-offs
- Optional NumPy from the normal data profile

The default lab uses only the standard library and local deterministic values.
Timings are observations, never pass/fail speed requirements.

## Learning objectives

You will be able to:

1. Define a representative workload and exact output semantics.
2. Separate warmup, repeated timing, and environmental noise.
3. Use `timeit`, `cProfile`, and `tracemalloc` for different questions.
4. Prefer algorithmic improvements before micro-optimization.
5. Compare loops, generators, and optional vectorization without universal
   speed claims.
6. Identify intermediate allocation and peak-memory pressure.
7. Estimate process serialization and transfer costs.
8. Evaluate cache reuse, memory, invalidation, and freshness trade-offs.
9. Bound native-extension/FFI work behind measured, batched interfaces.
10. Choose the next action from correctness and measured evidence.

## Vocabulary and concepts

- **Representative workload:** input shape, size, distribution, and environment
  that resemble the real decision.
- **Warmup:** preliminary execution that absorbs import, cache, and setup effects.
- **Noise:** timing variation from scheduling, background load, clocks, thermal
  state, allocation, and runtime behavior.
- **Microbenchmark:** focused measurement of a small operation.
- **Profiler:** tool attributing time or calls across functions.
- **Peak allocation:** largest traced live Python allocation total during work.
- **Complexity:** how resource use grows with input size.
- **Vectorization:** expressing bulk operations for an array/native engine.
- **Serialization:** encoding data to cross a storage or process boundary.
- **Transfer cost:** bytes, copies, and boundary calls needed to move data.
- **Cache hit rate:** fraction served from retained results.
- **Invalidation:** deciding when cached results are no longer valid.
- **FFI:** foreign-function interface between Python and native code.

## Worked example / walkthrough

Run the learner artifact. Its baseline returns the first value encountered for
a second time, but repeatedly scans prefixes.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_perf_01_measurement_optimization.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_perf_01_measurement_optimization.py
```

The reference path is:

```text
representative values
    -> prove baseline/candidate equivalence
    -> timeit repeated samples
    -> cProfile hotspot report
    -> tracemalloc peak evidence
    -> transfer/cache/native-boundary policy
    -> keep, measure, or optimize
```

Run the full local demonstration:

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\solutions\py_perf_01_measurement_optimization_solution.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/solutions/py_perf_01_measurement_optimization_solution.py
```

Numbers will differ by machine. Compare report structure and conclusions about
where work occurs, not exact seconds.

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_perf_01_measurement_optimization.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_perf_01_measurement_optimization.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

Performance engineering begins with a user-visible budget and a
reproducible workload. Wall-clock timing includes noise from warm-up,
caching, scheduling, CPU frequency, allocation, and I/O. Repeat
measurements, report a distribution, and keep correctness checks beside
the benchmark.

Profiling locates where time or memory is spent; algorithmic analysis
explains how cost grows. Optimize the measured bottleneck, then rerun
correctness and end-to-end evidence. Faster code that changes results,
ordering, errors, or resource bounds is a regression.

- **benchmark contract:** fixes data size/distribution, environment, warm-up, repetitions, statistic, and correctness invariant.
- **profile → hypothesis → one change:** connects an observed hotspot to a scoped optimization rather than guessing.
- **scale curve + budget:** measures several input sizes and checks latency/memory against an explicit threshold.

### Micro-example A — report repeat timing instead of one lucky run

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

**Why it matters:** The setup/workload matches the real bottleneck and `number=200` is included consistently in interpretation.

### Micro-example B — contrast quadratic and linear duplicate detection

```python
def has_duplicate_quadratic(values):
    return any(values[i] in values[:i] for i in range(len(values)))


def has_duplicate_linear(values):
    seen = set()
    for value in values:
        if value in seen:
            return True
        seen.add(value)
    return False


for size in (100, 1_000):
    data = list(range(size))
    assert has_duplicate_quadratic(data) == has_duplicate_linear(data) == False
print("both implementations agree on measured inputs")
```

**Expected observation:** Both functions preserve the Boolean contract, while the set-based design has expected linear rather than quadratic growth.

**Why it matters:** Values are hashable and set memory/order semantics are acceptable.

### Debugging and transfer

**Common mistake:** Optimizing a microbenchmark that excludes the actual I/O/serialization bottleneck or accepting a speedup that changes semantics.

**Diagnostic:** Reproduce the workload, record environment, profile CPU/memory/I/O, validate outputs, change one hotspot, and compare repeated end-to-end distributions.

**Transfer question:** Which evidence would distinguish Python-loop overhead from file I/O, database latency, or native NumPy work?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### 1. Define semantics before speed

For `[4, 1, 3, 2, 3, 4]`, the answer is `3`: the duplicate whose *second*
occurrence appears first. Complete `first_duplicate_linear` with a set and
prove equivalence for empty, unique, immediate, and competing duplicates.

**Verify:** Define semantics before speed — assert first_duplicate_linear([4,1,3,2,3,4]) == 3, [] and unique input return None, [2,2] returns 2, and competing duplicates follow earliest second occurrence; compare all cases with the baseline oracle.

### 2. Build a representative timing plan

Choose a workload size large enough to rise above timer noise but small enough
for quick study. Warm up separately, then collect at least five repeated
batches with `timeit`. Record Python version, platform, input size, and plan.

Do not assert “candidate < baseline” in the test suite. CI hosts, antivirus,
power state, and schedulers make that flaky.

**Verify:** Build a representative timing plan — choose a workload size large enough to rise above timer noise but small enough for quick study; record Python version, platform, input size, and plan; do not assert “candidate < baseline” in the test suite.

### 3. Ask cProfile a different question

Profile one complete representative call and sort by cumulative time. Locate
the call path, not just the leaf with the largest self time. Reduce the workload
if profiling overhead dominates, and do not compare profiled seconds directly
with unprofiled `timeit` seconds.

**Verify:** Ask cProfile a different question — profile one complete representative call and sort by cumulative time; locate the call path, not just the leaf with the largest self time; reduce the workload if profiling overhead dominates, and do not compare profiled seconds directly with unprofiled timeit seconds.

### 4. Measure allocation pressure

Compare materialized-list and generator sums with `tracemalloc`. Assert equal
results and report bounds (`peak >= current >= 0`). Explain why
`tracemalloc` may not see memory allocated inside every native library.

**Verify:** Measure allocation pressure — compare materialized-list and generator sums with tracemalloc; assert equal results and report bounds (peak >= current >= 0); explain why tracemalloc may not see memory allocated inside every native library.

### 5. Compare optional vectorization

With NumPy installed, compare a Python loop with `np.square(array).sum()`.
Include conversion from Python values when that conversion exists in the real
workflow. Small input can favor the loop; already-resident large arrays can
favor vectorized native work. Measure both representative cases.

**Verify:** Compare optional vectorization — with NumPy installed, compare a Python loop with np.square(array).sum(); include conversion from Python values when that conversion exists in the real workflow; measure both representative cases.

### 6. Model process transfer

Serialize a safe local JSON payload and measure its byte length. Complete
`estimated_transfer_bytes`. Four workers each receiving two copies move eight
payload equivalents before computation. Real process protocols may add framing,
copies, or shared-memory complexity.

**Verify:** Model process transfer — measure one JSON payload's encoded byte length and assert estimated_transfer_bytes(payload_bytes, workers=4, copies=2) equals 8 * payload_bytes; reject negative counts and state protocol overhead is excluded.

### 7. Evaluate caching

Use `cached_fibonacci.cache_info()` to observe hits. Then evaluate a real
candidate by:

- measured reuse,
- entry count and bytes,
- invalidation/freshness rules,
- key cardinality, and
- whether retained objects prevent memory release.

Caching a low-reuse, high-cardinality result can make performance worse.

**Verify:** Evaluate caching — use cached fibonacci.cache info() to observe hits; then evaluate a real candidate by: - measured reuse, - entry count and bytes, - invalidation/freshness rules, - key cardinality, and - whether retained objects prevent memory release; caching a low-reuse, high-cardinality result can make performance worse.

### 8. Bound native/FFI work

Use the policy to prefer an available algorithm improvement. If a measured
hotspot remains, batch native calls and cap transfer. Survey Cython, Rust/PyO3,
C/C++ extensions, and `ctypes`/`cffi`; record build wheels, ABI, ownership,
error, and safety obligations before choosing one.

**Verify:** Bound native/FFI work — use the policy to prefer an available algorithm improvement; if a measured hotspot remains, batch native calls and cap transfer; survey Cython, Rust/PyO3, C/C++ extensions, and ctypes/cffi; record build wheels, ABI, ownership, error, and safety obligations before choosing one.

### 9. Apply the evidence decision

Complete `choose_next_step` in priority order:

- fix unequal behavior,

- reduce peak memory beyond budget,

- reduce transfer consuming at least 30 percent,

- optimize a hotspot consuming at least 50 percent, or

- keep the current implementation.

Thresholds are a transparent lesson policy, not universal laws.

**Verify:** Apply the evidence decision — table-test choose_next_step so unequal outputs select correctness, over-budget memory selects memory, transfer >=30% selects transfer, hotspot >=50% selects optimization, and the below-threshold case selects keep.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 10 — compare timing distributions

Run interleaved repeated batches for baseline and candidate, report median, spread, paired ratios/differences, environment, and correctness. Avoid a binary CI speed assertion.

**Progressive hint:** Alternate order to reduce drift and choose repetitions from timer resolution/runtime. Keep raw measurements for review.

**Verify:** compare timing distributions — run interleaved repeated batches for baseline and candidate, report median, spread, paired ratios/differences, environment, and correctness; avoid a binary CI speed assertion.

### Exercise 11 — diagnose warmup, GC, and environment noise

Measure cold import/first call separately from steady state. Repeat with garbage collection controlled, background load noted, and process affinity/power assumptions documented rather than hidden.

**Progressive hint:** GC configuration can change real semantics/latency. Report it; do not simply disable GC to obtain a preferred number.

**Verify:** diagnose warmup, GC, and environment noise — measure cold import/first call separately from steady state; repeat with garbage collection controlled, background load noted, and process affinity/power assumptions documented rather than hidden.

### Exercise 12 — trade algorithm speed for memory

Compare set-based first-duplicate search with a sorted/indexed alternative under a strict memory budget. Preserve 'first second occurrence' semantics and report time/peak memory across unique-heavy and duplicate-early inputs.

**Progressive hint:** An algorithm with lower expected time can retain O(n) state. Alternative semantics or external sorting must be stated honestly.

**Verify:** trade algorithm speed for memory — compare set-based first-duplicate search with a sorted/indexed alternative under a strict memory budget; preserve 'first second occurrence' semantics and report time/peak memory across unique-heavy and duplicate-early inputs.

### Exercise 13 — test vectorized dtype boundaries

Compare Python integer sum-of-squares with NumPy int32, int64, float, and object arrays near overflow. Detect silent overflow and choose a validated dtype.

**Progressive hint:** Python integers grow; fixed-width NumPy integers wrap unless the operation/dtype is widened deliberately.

**Verify:** test vectorized dtype boundaries — compare Python integer sum-of-squares with NumPy int32, int64, float, and object arrays near overflow; detect silent overflow and choose a validated dtype.

### Exercise 14 — evaluate shared-memory process input

Compare normal process serialization with read-only shared memory for one large numeric payload. Include setup/copy, worker mapping, cleanup, spawn compatibility, and ownership failure cases.

**Progressive hint:** Pass only shared-memory name/shape/dtype to spawned workers. One owner closes/unlinks after every worker releases.

**Verify:** evaluate shared-memory process input — compare normal process serialization with read-only shared memory for one large numeric payload; include setup/copy, worker mapping, cleanup, spawn compatibility, and ownership failure cases.

### Exercise 15 — separate I/O concurrency from CPU optimization

Benchmark a local fake I/O wait and a pure-Python CPU loop under sequential, async/thread, and process designs. Explain why each model helps one workload and may hurt another.

**Progressive hint:** Use deterministic waits and fixed computations; include scheduling/startup and bounded active work.

**Verify:** separate I/O concurrency from CPU optimization — benchmark a local fake I/O wait and a pure-Python CPU loop under sequential, async/thread, and process designs; explain why each model helps one workload and may hurt another.

### Exercise 16 — prevent a cache stampede

Model many callers missing one expensive cache key. Add single-flight ownership, bounded wait, success publication, failure cleanup, and stale/retry policy with injected time.

**Progressive hint:** One caller computes; others await the same owned result. A failed owner must wake waiters and remove poisoned in-flight state.

**Verify:** prevent a cache stampede — model many callers missing one expensive cache key; add single-flight ownership, bounded wait, success publication, failure cleanup, and stale/retry policy with injected time.

### Exercise 17 — review an FFI ownership boundary

Specify one batched native function: accepted buffer dtype/layout, length, ownership/lifetime, mutability, error mapping, GIL behavior, panic/exception containment, and platform wheel matrix.

**Progressive hint:** Batch work across the boundary and validate before calling native code. Never let a borrowed buffer outlive its Python owner.

**Verify:** review an FFI ownership boundary — specify one batched native function: accepted buffer dtype/layout, length, ownership/lifetime, mutability, error mapping, GIL behavior, panic/exception containment, and platform wheel matrix.

### Exercise 18 — design a continuous performance gate

Define a stable local/CI benchmark artifact with workload version, correctness hash, environment, raw timings, peak memory, practical regression budget, comparison policy, and an investigation path instead of an immediate flaky fail.

**Progressive hint:** Separate noisy pull-request signal from controlled scheduled runs. Gate only after runner variance and minimum practical effect are characterized.

**Verify:** design a continuous performance gate — define a stable local/CI benchmark artifact with workload version, correctness hash, environment, raw timings, peak memory, practical regression budget, comparison policy, and an investigation path instead of an immediate flaky fail.

## Self-check

- Baseline and candidate return the same first duplicate for every test case.
- Timing reports contain the requested repeat count and ordered summary values.
- No correctness test asserts a wall-clock speed threshold.
- The profiler report contains a function-call table and target function.
- Memory reports satisfy `peak >= current >= 0` and results are equal.
- Transfer estimates validate counts and match measured serialized bytes.
- Cache policy considers reuse, memory, and freshness.
- Native-boundary policy prefers algorithm improvement and batching.
- Optional NumPy results equal the loop within floating tolerance.
- No benchmark, profiler, or Hypothesis cache remains in the repository.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_perf_01_measurement_optimization -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_perf_01_measurement_optimization -v
```

## Common pitfalls

- **A toy input drives the decision:** workload shape or size is not
  representative.
- **One timing is called a benchmark:** warmup and noise are invisible.
- **The fastest sample becomes a promise:** a machine observation is
  generalized universally.
- **A profiler is used as a stopwatch:** instrumentation overhead changes time.
- **A micro-optimization precedes complexity analysis:** the wrong algorithm is
  being polished.
- **Vectorization excludes conversion:** boundary cost is hidden.
- **Processes are assumed to share input for free:** serialization/copy costs
  are omitted.
- **A cache has no invalidation or budget:** stale data and retained memory grow.
- **Native code is called once per scalar:** FFI overhead dominates useful work.
- **`tracemalloc` equals process RSS:** native and operating-system memory are
  not fully represented.

## Next step

Apply the measurement record to one capstone hotspot and keep the before/after
correctness evidence. Combine with `python-pro-02` when processes or threads are
considered, and with `python-data-01` when columnar/vectorized execution changes
the data boundary.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-perf-01` — Measurement-first performance engineering.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize measurement design, complexity, profiling, and performance budgets. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_perf_01_measurement_optimization.md`
- learner artifact: `python/professional/lessons/py_perf_01_measurement_optimization.py`

Treat me as a beginner except for these direct catalog prerequisites:
`python-23`, `python-pro-02`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
