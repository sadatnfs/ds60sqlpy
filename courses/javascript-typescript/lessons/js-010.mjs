// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Observe a live binding: change one input
// In a scratch copy of Example A, change `1;` to `2;`. Which check fails, and what value
// does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(module.count,
// 1)`. Restoring `1;` brings back: count changes from 0 to 1 through the imported namespace.

// Exercise 2: Resolve a relative dependency: debug a regression
// A regression made one Example B line read `3`. Locate and repair it without editing the
// check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(module.answer, 8)`. Restoring `2` brings back: answer equals 8.

// Exercise 3: Prove cached module identity
// Import one URL twice and compare the namespace and exported object.
// Expected: both namespace and object identities are shared.

// Exercise 4: Inspect CommonJS interoperability
// Import a .cjs file exporting an object through its default binding.
// Expected: default.label equals legacy.

// Exercise 5: Reject a missing dependency
// Import a module with a nonexistent relative dependency and preserve the loader error code.
// Expected: ERR_MODULE_NOT_FOUND.

// Exercise 6: Respect namespace ownership
// Attempt to assign an exported binding from the importer.
// Expected: TypeError; exported value remains 3.

console.log("Implement the six exercises in your saved copy.");
