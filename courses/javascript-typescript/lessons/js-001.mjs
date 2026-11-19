// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Inspect the actual host: predict an edited check
// Copy Example A into a scratch `main.mjs` and change
// `assert.equal(Number(process.versions.node.split('.')[0]), 24);` to
// `assert.equal(Number(process.versions.node.split('.')[1]), 24);` inside its check. Before
// running it, predict whether the check still passes and explain why; then restore it.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(Number(process.versions.node.split('.')[0]), 24)`. Restoring the original
// line brings back the worked observation: major version 24; process.release.name is node.

// Exercise 2: Distinguish browser globals: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `assert.equal(typeof window,
// 'undefined!');`. Run Example B with that line, explain why the edited check now fails for
// the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(typeof window, 'undefined')`; after it the line reads `assert.equal(typeof
// window, 'undefined');` again and both undefined.

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
