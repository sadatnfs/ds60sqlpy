// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Keep equal-looking object keys distinct: change one input
// Copy Example A into a scratch `main.mjs` and change `[second, 'b'],` to `[second, 'b!'],`.
// Before running it, predict which check fails and which value it now sees; then run it and
// restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(map.get(second), 'b')`. Restoring the original line brings back the worked
// observation: size 2 and separate values.

// Exercise 2: Inspect Set equality: diagnose an edited check
// A careless edit changed a check in Example B so that it reads
// `assert.equal(values.has(-1), true);`. Run Example B with that line, explain why the
// edited check now fails for the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(values.has(-0), true)`; after it the line reads
// `assert.equal(values.has(-0), true);` again and size 2: one NaN and one zero.

// Exercise 3: Count repeated events
// Build a frequency Map for red, blue, red.
// Expected: red 2, blue 1.

// Exercise 4: Distinguish a stored zero from absence
// Store key a with 0 and compare has/get for a and b.
// Expected: a present with 0; b absent with undefined.

// Exercise 5: Trace insertion order updates
// Insert a, b, update a, then delete and reinsert a.
// Expected: update order a, b; reinsertion order b, a.

// Exercise 6: Deduplicate while preserving first occurrence
// Use Set over b, a, b, c, a and compare the ordered unique values.
// Expected: b, a, c.

console.log("Implement the six exercises in your saved copy.");
