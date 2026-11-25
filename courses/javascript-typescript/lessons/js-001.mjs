// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Inspect the actual host: predict an edited check
// In a scratch copy of Example A, change
// `assert.equal(Number(process.versions.node.split('.')[0]), 24);` to
// `assert.equal(Number(process.versions.node.split('.')[1]), 24);` inside its check. Does
// the check still pass?
// Expected: The edited run fails with an `AssertionError` at
// `assert.equal(Number(process.versions.node.split('.')[1]), 24);`. Restoring
// `assert.equal(Number(process.versions.node.split('.')[0]), 24);` brings back: major
// version 24; process.release.name is node.

// Exercise 2: Distinguish browser globals: diagnose an edited check
// Example B's check was edited to read `assert.equal(typeof window, 'undefined!');`. Run it,
// explain the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at `assert.equal(typeof
// window, 'undefined!');`. Restoring `assert.equal(typeof window, 'undefined');` brings
// back: both undefined.

// Exercise 3: Use language arithmetic independently of host APIs
// Calculate 2+3 and compare the numeric result with a string.
// Expected: number 5; not strictly equal to string 5.

// Exercise 4: Inspect module identity
// Read import.meta.url and confirm it identifies the current module.
// Expected: a file URL ending in .mjs in the classroom.

// Exercise 5: Observe strict module function calls
// Call an ordinary function without a receiver and inspect this.
// Expected: this is undefined.

// Exercise 6: Await a real Promise result
// Resolve 7 through a Promise and await it before checking.
// Expected: observed value 7 after await.

console.log("Implement the six exercises in your saved copy.");
