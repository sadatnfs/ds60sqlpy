// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Map a record into field flags
// Create a boolean flag type from id and count fields.
// Expected: id true and count false; a missing flag is a compile error.

// Exercise 2: Prove Omit does not remove runtime secrets
// Assign a wider record to an Omit type, then compare with an explicit public projection.
// Expected: typed view still has secret at runtime; explicit projection does not.

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
