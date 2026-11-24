# js-034: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Performance measurement begins with a correctness contract and a question. A faster implementation that computes a different answer is not an improvement. Wall-clock duration includes scheduling, warmup, JIT compilation, garbage collection and surrounding system load. A single tiny measurement cannot establish a robust speed ranking. Use repeated observations, representative inputs and clearly defined boundaries; retain raw samples instead of reporting only an attractive minimum.

performance.now provides a monotonic clock suitable for elapsed intervals. Date.now measures wall-clock time and can change when the system clock is adjusted. Named marks and measures help identify phases, but their entries also occupy a timeline until cleared. A library should clear only the marks it owns, not another component's measurements.

Memory counters describe different domains. heapUsed concerns managed JavaScript heap use, external and arrayBuffers describe other tracked allocations, and rss concerns resident process memory. Clearing a Map removes its references but does not guarantee immediate garbage collection or a visible drop in rss. A retained-reference count can prove an ownership change without pretending it measures reclaimed physical memory.

Event-loop utilization and delay measure related but distinct behavior. Utilization estimates active versus idle event-loop time under its API definition; delay measures how late scheduled monitoring callbacks run. Neither directly states CPU usage for every worker or the cause of a stall. This lesson records bounded real observations and asserts their shape and validity, not platform-specific performance thresholds. Profiling is a separate investigation after a reproducible workload identifies the problem.

**Measurement boundary:** The exact work included in a recorded interval.

**Monotonic clock:** A clock suited to elapsed time without wall-clock adjustments.

**Retention:** References that keep objects reachable.

**Event-loop delay:** Observed lateness in scheduled loop activity.

## Reading the implementation

Measure a known-correct function using start/end performance.now values. Summarize repeated samples with a declared statistic such as median while preserving all samples. process.memoryUsage returns byte counters that should not be subtracted indiscriminately as independent categories. performance.mark and measure use unique names and finally cleanup. monitorEventLoopDelay must be enabled and later disabled; a short or heavily delayed run may have too few samples, which is an evidence limit rather than a reason to invent a result.

## Exercise 1: Measure only a checked computation: change one input

Task: Copy Example A into a scratch `main.mjs` and change `const result = sumTo(10000);` to `const result = sumTo(10001);`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

Correctness is checked independently of the measured time. No assertion says the operation must be faster than a machine-dependent threshold.

The unchanged code is the exercise block of Example A:

```javascript
const start = performance.now();
const result = sumTo(10000);
const elapsed = performance.now() - start;
assert.equal(result, 50005000);
assert.ok(Number.isFinite(elapsed) && elapsed >= 0);
console.log(JSON.stringify({ operation: 'sumTo10000', elapsedMs: elapsed }));
```

**Expected:** The changed run fails with an `AssertionError` at `assert.equal(result, 50005000)`. Restoring `const result = sumTo(10000);` brings back: correct sum 50005000; finite nonnegative elapsed time.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(result, 50005000)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Preserve repeated samples and summarize them: debug a regression

Task: A regression changed one token in Example B, so one line now reads `const medianOf = values => [...values].sort()[Math.floor(values.length / 2)];`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

Five tiny trials illustrate record keeping, not a statistically robust benchmark. A real comparison needs workload control, enough repetitions and an analysis of variability.

The unchanged code is the exercise block of Example B:

```javascript
const samples = [];
for (let trial = 0; trial < 5; trial += 1) {
  const start = performance.now();
  assert.equal(sumTo(1000), 500500);
  samples.push(performance.now() - start);
}
const byValue = (a, b) => a - b;
const medianOf = (values) => [...values].sort(byValue)[Math.floor(values.length / 2)];
const median = medianOf(samples);
assert.equal(samples.length, 5);
assert.ok(samples.every((value) => Number.isFinite(value) && value >= 0));
assert.ok(median >= Math.min(...samples) && median <= Math.max(...samples));
assert.equal(medianOf([9, 10, 100, 2, 30]), 10);
console.log(JSON.stringify({ samplesMs: samples, medianMs: median }));
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(medianOf([9, 10, 100, 2, 30]), 10)`. Restoring `const medianOf = values => [...values].sort(byValue)[Math.floor(values.length / 2)];` brings back: five finite samples; median lies between minimum and maximum; the fixed control `[9, 10, 100, 2, 30]` has numeric median 10.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.equal(medianOf([9, 10, 100, 2, 30]), 10)` for this input.

## Exercise 3: Release owned references without claiming immediate RSS change

Task: Populate and clear a Map while recording memory counters.

The ownership claim is directly observed through the collection size. Physical memory reclamation depends on garbage collection and allocator behavior outside this deterministic check.

```javascript
const cache = new Map();
for (let index = 0; index < 100; index += 1) cache.set(index, { payload: 'x'.repeat(100) });
assert.equal(cache.size, 100);
const before = process.memoryUsage();
cache.clear();
assert.equal(cache.size, 0);
const after = process.memoryUsage();
assert.ok(before.heapUsed > 0 && after.rss > 0);
console.log(JSON.stringify({ before, after, retainedEntries: cache.size }));
```

**Expected:** entry count 100 then 0; valid counters, with no asserted memory drop.

**Verify:** Keep a check equivalent to `assert.equal(cache.size, 100)`. As a control, change `for (let index = 0; index < 100; index += 1) cache.set(index, { payload: 'x'.repeat(100) });` to `for (let index = 0; index <= 100; index += 1) cache.set(index, { payload: 'x'.repeat(100) });`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Use and clear only owned performance entries

Task: Create named marks and one measure around a checked operation.

Measurement infrastructure has state too. Scoped cleanup prevents this lesson from deleting unrelated entries or retaining its own indefinitely.

```javascript
const prefix = 'course-js034-owned';
try {
  performance.mark(prefix + '-start');
  assert.equal(sumTo(10), 55);
  performance.mark(prefix + '-end');
  performance.measure(prefix, prefix + '-start', prefix + '-end');
  const entries = performance.getEntriesByName(prefix, 'measure');
  assert.equal(entries.length, 1);
  assert.ok(entries[0].duration >= 0);
} finally {
  performance.clearMarks(prefix + '-start');
  performance.clearMarks(prefix + '-end');
  performance.clearMeasures(prefix);
}
assert.equal(performance.getEntriesByName(prefix).length, 0);
```

**Expected:** one nonnegative duration; owned entries removed afterward.

**Verify:** Keep a check equivalent to `assert.ok(entries[0].duration >= 0)`. As a control, change `performance.measure(prefix, prefix + '-start', prefix + '-end');` to `performance.measure(prefix, prefix + '-start', prefix - '-end');`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Inspect event-loop utilization as a bounded observation

Task: Take a baseline, yield through a timer, then inspect the interval delta.

The interval includes the explicit wait. A low value here says little about a production workload, other processes or worker-thread CPU consumption.

```javascript
const baseline = performance.eventLoopUtilization();
await delay(5);
const observed = performance.eventLoopUtilization(baseline);
assert.ok(Number.isFinite(observed.utilization));
assert.ok(observed.utilization >= 0 && observed.utilization <= 1);
console.log(JSON.stringify({ eventLoop: observed }));
```

**Expected:** finite utilization between 0 and 1; no speed or CPU-percentage claim.

**Verify:** Keep a check equivalent to `assert.ok(observed.utilization >= 0 && observed.utilization <= 1)`. As a control, change `assert.ok(observed.utilization >= 0 && observed.utilization <= 1);` to `assert.ok(observed.utilization >= 1 && observed.utilization <= 1);` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 6: Enable and disable a real delay monitor

Task: Collect a short delay-monitor interval and report whether samples exist.

The monitor reports nanoseconds, so the conversion to milliseconds is explicit. Zero samples remain an honest insufficient-observation result, not a fabricated zero delay.

```javascript
const histogram = monitorEventLoopDelay({ resolution: 10 });
histogram.enable();
try {
  await delay(35);
  const count = Number(histogram.count);
  assert.ok(Number.isInteger(count) && count >= 0);
  if (count > 0) assert.ok(Number.isFinite(histogram.mean));
  console.log(JSON.stringify({ samples: count, meanMs: count > 0 ? histogram.mean / 1e6 : null }));
} finally {
  histogram.disable();
}
```

**Expected:** monitor disabled afterward; sample count reported honestly.

**Verify:** Keep the guarded check `if (count > 0) assert.ok(Number.isFinite(histogram.mean))` and confirm that the reference still passes. Then name an input that satisfies the guard but makes the check fail, and explain which value changes.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
