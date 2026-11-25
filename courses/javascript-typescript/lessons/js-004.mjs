// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Call a pure function: predict an edited check
// In a scratch copy of Example A, change `assert.equal(add(-1, 1), 0);` to
// `assert.equal(add(-2, 1), 0);` inside its check. Does the check still pass?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(add(-2, 1), 0);`.
// Restoring `assert.equal(add(-1, 1), 0);` brings back: 5 and 0.

// Exercise 2: Build independent closures: diagnose an edited check
// Example B's check was edited to read `assert.equal(second(), 2);`. Run it, explain the
// failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(second(), 2);`. Restoring `assert.equal(second(), 1);` brings back: first 1,
// 2; second 1.

// Exercise 3: Compare let and var loop capture
// Create three closures in a let loop and three in a var loop.
// Expected: let returns 0, 1, 2; var returns 3, 3, 3.

// Exercise 4: Distinguish undefined from null defaults
// Call a greeting function with no argument, undefined and null.
// Expected: default used for the first two; null preserved.

// Exercise 5: Observe an ordinary receiver
// Call a method through its object and then with an explicit alternate receiver.
// Expected: 4 and 9.

// Exercise 6: Reject an invalid factory configuration
// Create a step counter with nonpositive or noninteger step.
// Expected: TypeError for 0 and 1.5; step 2 yields 2, 4.

console.log("Implement the six exercises in your saved copy.");
