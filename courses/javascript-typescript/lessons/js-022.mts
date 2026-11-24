// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Preserve identity type and object identity: change one input
// Copy Example A into a scratch `main.mts` and change `const value: number = identity(7);`
// to `const value: number = identity(8);`. Before running it, predict which check fails and
// which value it now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(value, 7)`.
// Restoring `const value: number = identity(7);` brings back: number remains 7; object is
// the same reference.

// Exercise 2: Connect a key to its exact result type: debug a regression
// A regression changed one token in Example B, so one line now reads `const row = { id: 'A',
// count: 3 };`. Run Example B with that line, use the failing check to locate the defect and
// repair it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at `assert.equal(count,
// 2)`. Restoring `const row = { id: 'A', count: 2 };` brings back: id is string A; count is
// number 2.

// Exercise 3: Expose absence in a generic first function
// Read the first item from a nonempty and an empty readonly array.
// Expected: 4 and undefined.

// Exercise 4: Use only the constrained length property
// Apply a length operation to a string and an array; reject a number at compile time.
// Expected: lengths 3 and 2.

// Exercise 5: Transform while preserving output element type
// Map numbers to labels through a generic map function.
// Expected: string array `['item:2', 'item:4']`; input unchanged.

// Exercise 6: Avoid pretending a constraint is the exact caller type
// Show that a replacement object cannot be returned as arbitrary T even if it meets the
// constraint.
// Expected: expected compile error for returning a fabricated length-only object.

console.log("Implement the six exercises in your saved copy.");
