// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Measure only a checked computation
// Sum a fixed numeric range and record elapsed duration.
// Expected: correct sum 50005000; finite nonnegative elapsed time.

// Exercise 2: Preserve repeated samples and summarize them
// Measure five checked runs and compute their median.
// Expected: five finite samples; median lies between minimum and maximum.

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
