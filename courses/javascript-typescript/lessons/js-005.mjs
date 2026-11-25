// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Map and filter without changing input: change one input
// In a scratch copy of Example A, change `const original = [1, 2, 3, 4];` to `const original
// = [2, 2, 3, 4];`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.deepEqual(original, [1,
// 2, 3, 4])`. Restoring `const original = [1, 2, 3, 4];` brings back: 6, 8; original array
// unchanged.

// Exercise 2: Supply a reduction identity: diagnose an edited check
// Example B's check was edited to read `assert.equal([1, 2, 3].reduce((sum, value) => sum -
// value, 0), 6);`. Run it, explain the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at `assert.equal([1, 2,
// 3].reduce((sum, value) => sum - value, 0), 6);`. Restoring `assert.equal([1, 2,
// 3].reduce((sum, value) => sum + value, 0), 6);` brings back: 0 and 6.

// Exercise 3: Expose default sort coercion
// Sort 10, 2, 1 with default and numeric comparators.
// Expected: default 1, 10, 2; numeric 1, 2, 10.

// Exercise 4: Preserve an array while sorting
// Use toSorted on 3, 1, 2 and inspect both arrays.
// Expected: sorted 1, 2, 3; original 3, 1, 2.

// Exercise 5: Expose a shallow copy alias
// Spread an array containing one object and mutate that object through the copy.
// Expected: original nested value also changes.

// Exercise 6: Copy records for a specific edit
// Map records to new objects before changing one field.
// Expected: edited record changes; original record stays 1.

console.log("Implement the six exercises in your saved copy.");
