// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Compare false and truthy containers: predict an edited check
// Copy Example A into a scratch `main.mjs` and change `assert.deepEqual([Boolean(0),
// Boolean(''), Boolean([]), Boolean({})], [false, false, true, true]);` to
// `assert.deepEqual([Boolean(1), Boolean(''), Boolean([]), Boolean({})], [false, false,
// true, true]);` inside its check. Before running it, predict whether the check still passes
// and explain why; then restore it.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false,
// true, true])`. Restoring the original line brings back the worked observation: false,
// false, true, true.

// Exercise 2: Preserve a valid zero with nullish fallback: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `assert.equal(null ?? 11,
// 10);`. Run Example B with that line, explain why the edited check now fails for the same
// program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(null ?? 10, 10)`; after it the line reads `assert.equal(null ?? 10, 10);`
// again and 10, 0, 10.

// Exercise 3: Trace a prefix sum
// Sum 2, 4, 6 and record the accumulator after each iteration.
// Expected: prefixes 2, 6, 12.

// Exercise 4: Handle an empty collection
// Run the same accumulation pattern on an empty array.
// Expected: sum 0 and iterations 0.

// Exercise 5: Stop at the first match
// Find the first 8 in 3, 8, 8 using an indexed loop and break.
// Expected: index 1.

// Exercise 6: Make a wrong boundary observable
// Iterate with index<=length over a one-element array and record the values.
// Expected: extra undefined element exposes the off-by-one.

console.log("Implement the six exercises in your saved copy.");
