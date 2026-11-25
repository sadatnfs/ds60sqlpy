// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Preserve identity type and object identity: change one input
// In a scratch copy of Example A, change `const value: number = identity(7);` to `const
// value: number = identity(8);`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(value, 7)`.
// Restoring `const value: number = identity(7);` brings back: number remains 7; object is
// the same reference.

// Exercise 2: Connect a key to its exact result type: debug a regression
// A regression made one Example B line read `const row = { id: 'A', count: 3 };`. Locate and
// repair it without editing the check.
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
