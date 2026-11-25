// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace lower bound with duplicates: predict an edited check
// In a scratch copy of Example A, change `assert.equal(lowerBound([1, 4, 4, 8], 4, trace),
// 1);` to `assert.equal(lowerBound([1, 4, 4, 8], 5, trace), 1);` inside its check. Does the
// check still pass?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(lowerBound([1, 4,
// 4, 8], 5, trace), 1);`. Restoring `assert.equal(lowerBound([1, 4, 4, 8], 4, trace), 1);`
// brings back: index 1; intervals shrink to the first duplicate.

// Exercise 2: Use a heap for repeated minimum extraction: debug a regression
// A regression made one Example B line read `for (const value of [6, 1, 3, 1])
// heap.push(value);`. Locate and repair it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.deepEqual([heap.pop(), heap.pop(), heap.pop(), heap.pop()], [1, 1, 3, 5])`.
// Restoring `for (const value of [5, 1, 3, 1]) heap.push(value);` brings back: pops 1,1,3,5,
// then undefined.

// Exercise 3: Cover empty and outside search boundaries
// Search empty input, then targets below and above a sorted input.
// Expected: positions 0,0,3.

// Exercise 4: Measure comparisons without a timing claim
// Search 1024 even integers for a missing value between two entries.
// Expected: insertion position 501 with no more than 11 comparisons.

// Exercise 5: Reject duplicate index keys
// Build a Map keyed by id and reject repeated ids rather than silently replacing a row.
// Expected: valid lookup returns 7; duplicate id throws.

// Exercise 6: Check the heap invariant after every update
// Push descending values and check each parent/child relation; reject NaN.
// Expected: all invariants hold; invalid value throws.

console.log("Implement the six exercises in your saved copy.");
