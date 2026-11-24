// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace plus versus numeric conversion: predict an edited check
// Copy Example A into a scratch `main.mjs` and change `assert.equal(Number('3') + 2, 5);` to
// `assert.equal(Number('3') + 3, 5);` inside its check. Before running it, predict whether
// the check still passes and explain why; then restore it.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(Number('3') + 3,
// 5);`. Restoring `assert.equal(Number('3') + 2, 5);` brings back: 5, string 23, and 5.

// Exercise 2: Inspect absence and NaN: diagnose an edited check
// A careless edit changed a check in Example B so that it reads
// `assert.equal(Number.isNaN('not a number'), true);`. Run Example B with that line, explain
// why the edited check now fails for the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(Number.isNaN('not a number'), true);`. Restoring
// `assert.equal(Number.isNaN('not a number'), false);` brings back: null reports object;
// undefined reports undefined; only numeric NaN passes isNaN.

// Exercise 3: Compare equality contracts
// Use NaN, +0 and -0 with strict equality and Object.is.
// Expected: NaN!==NaN; Object.is(NaN, NaN) is true; +0===-0; Object.is distinguishes zeros.

// Exercise 4: Expose floating-point approximation
// Add 0.1 and 0.2 and compare with 0.3 under an explicit tolerance.
// Expected: strict equality false; absolute error below 1e-15.

// Exercise 5: Protect integer identity
// Compare the two integers just beyond Number.MAX_SAFE_INTEGER and then use BigInt.
// Expected: Number collapses a difference; BigInt preserves it.

// Exercise 6: Reject ambiguous numeric input
// Validate finite nonblank numeric text and reject blank, Infinity and mixed BigInt
// arithmetic.
// Expected: valid 12 accepted; invalid cases throw.

console.log("Implement the six exercises in your saved copy.");
