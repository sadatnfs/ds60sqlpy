// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Measure only a checked computation: change one input
// In a scratch copy of Example A, change `const result = sumTo(10000);` to `const result =
// sumTo(10001);`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(result,
// 50005000)`. Restoring `const result = sumTo(10000);` brings back: correct sum 50005000;
// finite nonnegative elapsed time.

// Exercise 2: Preserve repeated samples and summarize them: debug a regression
// A regression made one Example B line read `const medianOf = values =>
// [...values].sort()[Math.floor(values.length / 2)];`. Locate and repair it without editing
// the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(medianOf([9, 10, 100, 2, 30]), 10)`. Restoring `const medianOf = values =>
// [...values].sort(byValue)[Math.floor(values.length / 2)];` brings back: five finite
// samples; median lies between minimum and maximum; the fixed control `[9, 10, 100, 2, 30]`
// has numeric median 10.

// Exercise 3: Release owned references without claiming immediate RSS change
// Populate and clear a Map while recording memory counters.
// Expected: entry count 100 then 0; valid counters, with no asserted memory drop.

// Exercise 4: Use and clear only owned performance entries
// Create named marks and one measure around a checked operation.
// Expected: one nonnegative duration; owned entries removed afterward.

// Exercise 5: Inspect event-loop utilization as a bounded observation
// Take a baseline, yield through a timer, then inspect the interval delta.
// Expected: finite utilization between 0 and 1; no speed or CPU-percentage claim.

// Exercise 6: Enable and disable a real delay monitor
// Collect a short delay-monitor interval and report whether samples exist.
// Expected: monitor disabled afterward; sample count reported honestly.

console.log("Implement the six exercises in your saved copy.");
