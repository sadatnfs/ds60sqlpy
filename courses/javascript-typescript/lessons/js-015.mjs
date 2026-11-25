// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Run a passing pure-function test: change one input
// In a scratch copy of Example A, change `assert.equal(2` to `assert.equal(3`. Which check
// fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(result.status, 0,
// result.stderr + result.stdout)`. Restoring `assert.equal(2` brings back: child exit status
// 0; one passing test.

// Exercise 2: Prove a wrong result fails the runner: debug a regression
// A regression made one Example B line read `assert.equal(3`. Locate and repair it without
// editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.notEqual(result.status, 0)`. Restoring `assert.equal(2` brings back: nonzero child
// exit; one failing test.

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
