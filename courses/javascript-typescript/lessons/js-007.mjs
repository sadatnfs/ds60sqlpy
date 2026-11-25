// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Keep equal-looking object keys distinct: change one input
// In a scratch copy of Example A, change `[second, 'b'],` to `[second, 'b!'],`. Which check
// fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(map.get(second),
// 'b')`. Restoring `[second, 'b'],` brings back: size 2 and separate values.

// Exercise 2: Inspect Set equality: diagnose an edited check
// Example B's check was edited to read `assert.equal(values.has(-1), true);`. Run it,
// explain the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(values.has(-1), true);`. Restoring `assert.equal(values.has(-0), true);`
// brings back: size 2: one NaN and one zero.

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
