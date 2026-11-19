// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace lower bound with duplicates: predict an edited check
// Copy Example A into a scratch `main.mjs` and change `assert.equal(lowerBound([1, 4, 4, 8],
// 4, trace), 1);` to `assert.equal(lowerBound([1, 4, 4, 8], 5, trace), 1);` inside its
// check. Before running it, predict whether the check still passes and explain why; then
// restore it.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(lowerBound([1, 4, 4, 8], 4, trace), 1)`. Restoring the original line brings
// back the worked observation: index 1; intervals shrink to the first duplicate.

// Exercise 2: Use a heap for repeated minimum extraction: debug a regression
// A regression changed one token in Example B, so one line now reads `for (const value of
// [6, 1, 3, 1]) heap.push(value);`. Run Example B with that line, use the failing check to
// locate the defect and repair it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.deepEqual([heap.pop(), heap.pop(), heap.pop(), heap.pop()], [1, 1, 3, 5])`; after
// it the line reads `for (const value of [5, 1, 3, 1]) heap.push(value);` again and pops
// 1,1,3,5, then undefined.

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
