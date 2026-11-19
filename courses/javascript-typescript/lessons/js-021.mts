// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Use structural compatibility: change one input
// Copy Example A into a scratch `main.mts` and change `const wider = { id: 'A', count: 2 };`
// to `const wider = { id: 'A', count: 3 };`. Before running it, predict which check fails
// and which value it now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(wider.count, 2)`. Restoring the original line brings back the worked
// observation: label A; original count remains 2.

// Exercise 2: Observe mutation through an alias: debug a regression
// A regression changed one token in Example B, so one line now reads `mutable.count = 5;`.
// Run Example B with that line, use the failing check to locate the defect and repair it
// without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(view.count, 4)`; after it the line reads `mutable.count = 4;` again and
// readonly view observes count changing from 1 to 4.

// Exercise 3: Handle absent and zero-valued optional counts
// Use a nullish fallback on an optional count.
// Expected: absent becomes 10; explicit 0 remains 0.

// Exercise 4: Distinguish runtime presence from undefined
// Compare an absent property with an explicitly present undefined property.
// Expected: hasOwn is false versus true; JSON serializes both as empty objects.

// Exercise 5: Show shallow readonly and shallow freeze boundaries
// Freeze an outer record containing a nested mutable object and update the nested count.
// Expected: nested count becomes 3; outer object is frozen.

// Exercise 6: Transform a readonly array without mutation
// Accept readonly numbers, return a doubled array, and demonstrate push is rejected
// statically.
// Expected: new array 2,4; input remains 1,2.

console.log("Implement the six exercises in your saved copy.");
