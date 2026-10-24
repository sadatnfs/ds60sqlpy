// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Inspect the actual host
// Check that the prepared runtime is Node 24 and that process exists.
// Expected: major version 24; process.release.name is node.

// Exercise 2: Distinguish browser globals
// Inspect document and window using typeof inside Node.
// Expected: both undefined.

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
