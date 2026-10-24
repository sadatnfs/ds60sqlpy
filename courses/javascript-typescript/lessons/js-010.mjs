// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Observe a live binding
// Import a mutable counter and its increment function, then inspect the count before and
// after incrementing.
// Expected: count changes from 0 to 1 through the imported namespace.

// Exercise 2: Resolve a relative dependency
// Create a main module importing twice from ./math.mjs, then call its export.
// Expected: answer equals 8.

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
