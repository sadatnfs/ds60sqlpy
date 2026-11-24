// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Observe a live binding: change one input
// Copy Example A into a scratch `main.mjs` and change `1;` to `2;`. Before running it,
// predict which check fails and which value it now sees; then run it and restore the
// original line.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(module.count,
// 1)`. Restoring `1;` brings back: count changes from 0 to 1 through the imported namespace.

// Exercise 2: Resolve a relative dependency: debug a regression
// A regression changed one token in Example B, so one line now reads `3`. Run Example B with
// that line, use the failing check to locate the defect and repair it without changing the
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
