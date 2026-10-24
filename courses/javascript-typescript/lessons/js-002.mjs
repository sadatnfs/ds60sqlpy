// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace plus versus numeric conversion
// Compare 2+3, 2+string 3, and Number(string 3)+2.
// Expected: 5, string 23, and 5.

// Exercise 2: Inspect absence and NaN
// Compare typeof null, undefined and Number.isNaN results.
// Expected: null reports object; undefined reports undefined; only numeric NaN passes isNaN.

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
