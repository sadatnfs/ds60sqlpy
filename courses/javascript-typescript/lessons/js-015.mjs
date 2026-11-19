// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Run a passing pure-function test: change one input
// Copy Example A into a scratch `main.mjs` and change `assert.equal(2` to `assert.equal(3`.
// Before running it, predict which check fails and which value it now sees; then run it and
// restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(result.status, 0, result.stderr + result.stdout)`. Restoring the original
// line brings back the worked observation: child exit status 0; one passing test.

// Exercise 2: Prove a wrong result fails the runner: debug a regression
// A regression changed one token in Example B, so one line now reads `assert.equal(3`. Run
// Example B with that line, use the failing check to locate the defect and repair it without
// changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.notEqual(result.status, 0)`; after it the line reads `assert.equal(2` again and
// nonzero child exit; one failing test.

// Exercise 3: Await an asynchronous test
// Declare an async test that awaits Promise resolution before checking the value.
// Expected: child exit status 0.

// Exercise 4: Check rejection with rejects
// Assert that an async operation rejects with a RangeError.
// Expected: child exit status 0.

// Exercise 5: Cover a table of boundary cases
// Use a table for sums of empty, singleton and signed arrays.
// Expected: three passing child tests.

// Exercise 6: Keep fixtures independent
// Create a fresh array inside each test and mutate it in only one test.
// Expected: two tests pass without shared mutable state.

console.log("Implement the six exercises in your saved copy.");
