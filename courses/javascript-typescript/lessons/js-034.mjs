// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Measure only a checked computation: change one input
// Copy Example A into a scratch `main.mjs` and change `const result = sumTo(10000);` to
// `const result = sumTo(10001);`. Before running it, predict which check fails and which
// value it now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(result, 50005000)`. Restoring the original line brings back the worked
// observation: correct sum 50005000; finite nonnegative elapsed time.

// Exercise 2: Preserve repeated samples and summarize them: debug a regression
// A regression changed one token in Example B, so one line now reads `const sorted =
// [...samples].sort((a, b) => a + b);`. Run Example B with that line, use the failing check
// to locate the defect and repair it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.ok(median >= sorted[0] && median <= sorted[4])`; after it the line reads `const
// sorted = [...samples].sort((a, b) => a - b);` again and five finite samples; median lies
// between minimum and maximum.

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
