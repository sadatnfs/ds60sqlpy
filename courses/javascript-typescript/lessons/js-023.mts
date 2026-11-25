// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Map a record into field flags: change one input
// In a scratch copy of Example A, change `const flags: Flags<Row> = { id: true, count: false
// };` to `const flags: Flags<Row> = { id: false, count: false };`. Which check fails, and
// what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.deepEqual(flags, { id:
// true, count: false })`. Restoring `const flags: Flags<Row> = { id: true, count: false };`
// brings back: id true and count false; a missing flag is a compile error.

// Exercise 2: Prove Omit does not remove runtime secrets: debug a regression
// A regression made one Example B line read `const full: RecordWithSecret = { id: 'A!',
// secret: 'fixture-only' };`. Locate and repair it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(JSON.stringify(publicRecord), '{"id":"A"}')`. Restoring `const full:
// RecordWithSecret = { id: 'A', secret: 'fixture-only' };` brings back: typed view still has
// secret at runtime; explicit projection does not.

// Exercise 3: Compare distributed and whole-union array types
// Define both conditional utilities and demonstrate their different assignment behavior.
// Expected: whole-union array accepts mixed values; distributed array rejects them.

// Exercise 4: Infer an array element type
// Extract the element type of a readonly array and use it in a checked value.
// Expected: element type permits number 7 and rejects text.

// Exercise 5: Derive an asynchronous result type without executing it
// Use ReturnType and Awaited for a small async function, then actually call it separately.
// Expected: declared resolved shape and actual result both have count 3.

// Exercise 6: Check a configuration with satisfies
// Require exactly the literal success/failure keys on a label table.
// Expected: valid table remains usable; misspelled literal key is a compiler error.

console.log("Implement the six exercises in your saved copy.");
