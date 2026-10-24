// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace lower bound with duplicates
// Find the first insertion position for 4 in 1,4,4,8 and inspect the visited intervals.
// Expected: index 1; intervals shrink to the first duplicate.

// Exercise 2: Use a heap for repeated minimum extraction
// Insert 5,1,3,1 and remove all values.
// Expected: pops 1,1,3,5, then undefined.

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
