// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Use structural compatibility: change one input
// In a scratch copy of Example A, change `const wider = { id: 'A', count: 2 };` to `const
// wider = { id: 'A', count: 3 };`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(wider.count, 2)`.
// Restoring `const wider = { id: 'A', count: 2 };` brings back: label A; original count
// remains 2.

// Exercise 2: Observe mutation through an alias: debug a regression
// A regression made one Example B line read `mutable.count = 5;`. Locate and repair it
// without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(view.count, 4)`. Restoring `mutable.count = 4;` brings back: readonly view
// observes count changing from 1 to 4.

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
