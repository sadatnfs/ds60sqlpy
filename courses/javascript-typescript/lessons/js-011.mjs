// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace lazy execution
// Create a generator, inspect its trace, then request one value.
// Expected: trace is empty before next; then started, with value 2.

// Exercise 2: Close on an early break
// Iterate one value from a generator protected by finally, then break.
// Expected: trace records opened, value 1, closed.

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
