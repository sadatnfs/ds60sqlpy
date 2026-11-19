// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace lazy execution: change one input
// Copy Example A into a scratch `main.mjs` and change `trace.push('started');` to
// `trace.push('started!');`. Before running it, predict which check fails and which value it
// now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual(trace, ['started'])`. Restoring the original line brings back the worked
// observation: trace is empty before next; then started, with value 2.

// Exercise 2: Close on an early break: debug a regression
// A regression changed `yield 1;` to `yield 2;` in Example B. Run Example B with that
// change, use the failing check to explain the defect and repair it without changing the
// check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.deepEqual(trace, ['opened', 1, 'closed'])`; after it the line reads `yield 1;`
// again and trace records opened, value 1, closed.

// Exercise 3: Distinguish a cursor from a fresh iterable
// Consume one generator twice, then create a second generator.
// Expected: first pass is 0,1,2; second is empty; fresh pass repeats 0,1,2.

// Exercise 4: Inspect the final return value
// Read a generator yielding 1 and returning 9, then compare spread.
// Expected: next records value 1/done false then 9/done true; spread contains only 1.

// Exercise 5: Send a value into a suspended generator
// Suspend at a request, then send 4 to produce its double.
// Expected: request, then 8.

// Exercise 6: Bound the range and validate configuration
// Produce an empty range and reject negative or fractional lengths.
// Expected: empty array for 0; RangeError for -1 and 1.5.

console.log("Implement the six exercises in your saved copy.");
