// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Import the public package entry
// Create a package with exports pointing at index.mjs and import its version value.
// Expected: actual child prints 1.

// Exercise 2: Use an explicitly exported subpath
// Import twice from course-fixture/math.
// Expected: actual child prints 6.

// Exercise 3: Reject an undeclared private path
// Attempt a package-name import of private.mjs even though the file exists.
// Expected: nonzero child status with ERR_PACKAGE_PATH_NOT_EXPORTED.

// Exercise 4: Observe that engines is metadata rather than a loader gate
// Read the fixture engine declaration requiring Node99, then import its entry with the
// actual runtime.
// Expected: metadata says >=99; ordinary import still succeeds.

// Exercise 5: Detect exact source tampering through a digest
// Hash the public source, change only that owned file, and compare hashes.
// Expected: digest changes after modification.

// Exercise 6: Preserve a versioned behavior contract
// Import the arithmetic subpath and assert both a normal and a boundary input in the child.
// Expected: child exits successfully for twice(0)=0 and twice(-2)=-4.

console.log("Implement the six exercises in your saved copy.");
